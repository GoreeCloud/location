"""SQLite persistence and password utilities.

Location data is sensitive: all access must be scoped by the authenticated account.
No account is created automatically on service startup.
"""
from __future__ import annotations

from contextlib import contextmanager, closing
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import secrets
import sqlite3
import stat
from typing import Iterator
from urllib.parse import quote

USERNAME = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def default_db_path() -> Path:
    data_home = os.environ.get("XDG_DATA_HOME")
    parent = Path(data_home) if data_home else Path.home() / ".local" / "share"
    return Path(os.environ.get("GC_LOCATION_DB", str(parent / "goreecloud-location" / "location.db"))).expanduser()


def initialize(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.is_symlink():
        raise ValueError("Refusing a symlinked database path.")
    # SQLite's default creation mode inherits the process umask, which may be
    # 022. Force the sensitive database file to owner-only access.
    flags = os.O_CREAT | os.O_EXCL | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags, 0o600)
    except FileExistsError:
        if path.is_symlink():
            raise ValueError("Refusing a symlinked database path.")
    else:
        os.close(fd)
    if not path.is_file():
        raise ValueError("Database path is not a regular file.")
    file_mode = stat.S_IMODE(path.stat().st_mode)
    if file_mode & 0o077:
        path.chmod(file_mode & ~0o077)
    with connect(path) as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'owner',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY,
                account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                expires_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_sessions_account ON sessions(account_id);
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY,
                account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                kind TEXT NOT NULL,
                ingest_token_hash TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_devices_account ON devices(account_id);
            CREATE TABLE IF NOT EXISTS points (
                id INTEGER PRIMARY KEY,
                device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
                latitude REAL NOT NULL CHECK(latitude BETWEEN -90 AND 90),
                longitude REAL NOT NULL CHECK(longitude BETWEEN -180 AND 180),
                accuracy_m REAL,
                altitude_m REAL,
                speed_mps REAL,
                heading_deg REAL,
                battery_percent INTEGER,
                recorded_at TEXT NOT NULL,
                received_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_points_device_time
                ON points(device_id, recorded_at DESC, id DESC);
            CREATE TABLE IF NOT EXISTS places (
                id INTEGER PRIMARY KEY,
                account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                radius_m REAL NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_places_account ON places(account_id);
            CREATE TABLE IF NOT EXISTS geofence_state (
                device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
                place_id INTEGER NOT NULL REFERENCES places(id) ON DELETE CASCADE,
                inside INTEGER NOT NULL,
                PRIMARY KEY(device_id, place_id)
            );
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
                place_id INTEGER NOT NULL REFERENCES places(id) ON DELETE CASCADE,
                kind TEXT NOT NULL CHECK(kind IN ('arrival','departure')),
                recorded_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_events_device_time
                ON events(device_id, recorded_at DESC, id DESC);
        """)
        db.execute("""CREATE TABLE IF NOT EXISTS collection_activity (
            id INTEGER PRIMARY KEY,
            device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
            action TEXT NOT NULL CHECK(action IN ('paused','resumed')),
            changed_at TEXT NOT NULL
        )""")
        db.execute("""CREATE INDEX IF NOT EXISTS idx_collection_activity_device
            ON collection_activity(device_id, id DESC)""")
        # Preserve existing self-hosted databases while adding a reversible
        # owner collection switch. No GPS history or tracker credentials change.
        # Serialize migrations across concurrent service starts.
        db.execute("BEGIN IMMEDIATE")
        columns = {row["name"] for row in db.execute("PRAGMA table_info(devices)")}
        if "tracking_paused" not in columns:
            db.execute(
                "ALTER TABLE devices ADD COLUMN tracking_paused INTEGER NOT NULL DEFAULT 0 CHECK (tracking_paused IN (0,1))"
            )
        if "tracking_resumed_at" not in columns:
            db.execute("ALTER TABLE devices ADD COLUMN tracking_resumed_at TEXT")


@contextmanager
def connect(path: Path) -> Iterator[sqlite3.Connection]:
    db = sqlite3.connect(path, timeout=15)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA busy_timeout=15000")
    db.execute("PRAGMA journal_mode=WAL")
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def hash_password(password: str) -> str:
    if not 14 <= len(password) <= 1024:
        raise ValueError("Password must be 14–1024 characters.")
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt:16384:8:1:{salt.hex()}:{digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        label, n, r, p, salt, expected = stored.split(":")
        if label != "scrypt" or (int(n), int(r), int(p)) != (2**14, 8, 1):
            return False
        digest = hashlib.scrypt(password.encode("utf-8"), salt=bytes.fromhex(salt),
                                n=int(n), r=int(r), p=int(p))
        return secrets.compare_digest(digest, bytes.fromhex(expected))
    except (ValueError, TypeError, OverflowError):
        return False


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_account(path: Path, username: str, password: str) -> int:
    if not USERNAME.fullmatch(username):
        raise ValueError("Username must be 3–32 letters, digits, dots, dashes, or underscores.")
    hashed = hash_password(password)
    with connect(path) as db:
        cur = db.execute(
            "INSERT INTO accounts (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, hashed, utc_now()),
        )
        return int(cur.lastrowid)

def backup_database(path: Path, destination: Path) -> None:
    """Take a consistent SQLite snapshot without overwriting other files.

    SQLite's online backup API includes committed data in WAL mode; an
    exclusive destination prevents inadvertent destruction of prior backups.
    The caller should separately protect backup transfer and storage.
    """
    path, destination = Path(path), Path(destination)
    if not path.is_file() or path.is_symlink():
        raise ValueError("Source database must be a regular non-symlink file.")
    if destination.is_symlink():
        raise ValueError("Refusing a symlinked backup destination.")
    if not destination.parent.is_dir():
        raise ValueError("Backup destination directory does not exist.")
    flags = os.O_CREAT | os.O_EXCL | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(destination, flags, 0o600)
    os.close(fd)
    try:
        with sqlite3.connect(path) as source, sqlite3.connect(destination) as snapshot:
            source.backup(snapshot)
        destination.chmod(0o600)
    except Exception:
        destination.unlink(missing_ok=True)
        raise



# A consistent backup is useful only if it can be opened and restored.
# Verify expected relations without returning private account/device information.
RECOVERY_TABLES = frozenset({
    "accounts", "sessions", "devices", "points", "places",
    "geofence_state", "events",
})


def verify_database(path: Path) -> None:
    """Read-only integrity and schema checks on a candidate recovery snapshot.

    Never initializes or writes to the candidate. The caller controls its
    source and should treat the file as untrusted until verification succeeds.
    """
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("Database candidate must be a regular non-symlink file.")
    try:
        with path.open("rb") as header:
            if header.read(16) != b"SQLite format 3\x00":
                raise ValueError("File is not a SQLite database.")
        source_uri = "file:" + quote(str(path.absolute()), safe="/") + "?mode=ro"
        with closing(sqlite3.connect(source_uri, uri=True, timeout=10)) as db:
            db.execute("PRAGMA trusted_schema=OFF")
            db.execute("PRAGMA query_only=ON")
            integrity = db.execute("PRAGMA integrity_check").fetchone()
            if not integrity or integrity[0] != "ok":
                raise ValueError("SQLite integrity check failed.")
            if db.execute("PRAGMA foreign_key_check").fetchone():
                raise ValueError("SQLite foreign key integrity check failed.")
            tables = {
                name for (name,) in db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            if not RECOVERY_TABLES.issubset(tables):
                raise ValueError("Not a compatible GoreeCloud Location database.")
    except sqlite3.DatabaseError as exc:
        raise ValueError("Database verification failed.") from exc


def restore_database(source: Path, destination: Path) -> None:
    """Restore a verified snapshot to a NEW database, never overwrite a live one.

    User sessions are invalidated in the restored copy to prevent replay of
    sessions that might have been revoked since the snapshot was captured.
    Registered device ingestion keys remain intact so trackers can reconnect.
    The operator must deliberately switch the service to the new database.
    """
    source, destination = Path(source), Path(destination)
    verify_database(source)
    backup_completed = False
    try:
        backup_database(source, destination)
        backup_completed = True
        with closing(sqlite3.connect(destination, timeout=10)) as db:
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("DELETE FROM sessions")
            db.commit()
        verify_database(destination)
    except Exception:
        if backup_completed:
            destination.unlink(missing_ok=True)
        raise
