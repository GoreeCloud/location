"""Verify that private snapshots can be recovered without touching a live database."""

import os
from pathlib import Path
import sqlite3
import stat
import subprocess
import sys

import pytest
from fastapi.testclient import TestClient

from goreecloud_location.main import create_app
from goreecloud_location.store import (
    backup_database,
    connect,
    create_account,
    initialize,
    restore_database,
    verify_database,
)


def build_test_history(db_path):
    app = create_app(db_path)
    create_account(db_path, "recoveryuser", "a unique test-only password phrase")
    with TestClient(app) as client:
        login = client.post("/api/auth/login", json={
            "username": "recoveryuser", "password": "a unique test-only password phrase"
        })
        assert login.status_code == 200
        token = login.json()["access_token"]
        headers = {"Authorization": "Bearer " + token}
        dev = client.post("/api/devices", headers=headers, json={
            "name": "Test GPS", "kind": "vehicle"
        }).json()
        point = client.post("/api/locations", headers=headers, json={
            "device_id": dev["id"], "latitude": 35.12345, "longitude": -83.12345,
            "accuracy_m": 12, "recorded_at": "2026-11-01T10:00:00+00:00"
        })
        assert point.status_code == 201
        return token, dev


def test_round_trip_backup_restore_and_invalidated_sessions(tmp_path):
    original = tmp_path / "live" / "locations.sqlite"
    original_token, device = build_test_history(original)
    snapshot = tmp_path / "backup.sqlite"
    backup_database(original, snapshot)
    verify_database(snapshot)
    restored = tmp_path / "restored.sqlite"
    restore_database(snapshot, restored)
    verify_database(restored)
    assert stat.S_IMODE(restored.stat().st_mode) == 0o600
    with connect(original) as db:
        assert db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0] == 1
    with connect(restored) as db:
        assert db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0] == 0
        assert db.execute("SELECT COUNT(*) FROM points").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM devices").fetchone()[0] == 1

    with TestClient(create_app(restored)) as client:
        assert client.get("/api/me", headers={
            "Authorization": "Bearer " + original_token
        }).status_code == 401
        login = client.post("/api/auth/login", json={
            "username": "recoveryuser",
            "password": "a unique test-only password phrase",
        })
        assert login.status_code == 200
        new_header = {"Authorization": "Bearer " + login.json()["access_token"]}
        points = client.get("/api/locations", headers=new_header).json()
        assert len(points) == 1
        assert points[0]["latitude"] == 35.12345
        # Dedicated write-only tokens survive a restore, unless intentionally rotated.
        upload = client.post(f"/api/ingest/{device['id']}", headers={
            "Authorization": "Bearer " + device["ingest_token"]
        }, json={"latitude": 35.5, "longitude": -83.5, "accuracy_m": 8})
        assert upload.status_code == 201
    with connect(original) as db:
        assert db.execute("SELECT COUNT(*) FROM points").fetchone()[0] == 1


def test_refuses_existing_destination_without_modifying_it(tmp_path):
    source = tmp_path / "source.sqlite"
    initialize(source)
    snapshot = tmp_path / "snapshot.sqlite"
    backup_database(source, snapshot)
    target = tmp_path / "already-exists.sqlite"
    target.write_bytes(b"protected content")
    with pytest.raises(FileExistsError):
        restore_database(snapshot, target)
    assert target.read_bytes() == b"protected content"
    assert snapshot.exists()


def test_corruption_wrong_schema_and_symlink_rejected(tmp_path):
    bad = tmp_path / "corrupt.sqlite"
    bad.write_bytes(b"this is not a sqlite snapshot")
    destination = tmp_path / "no-restore.sqlite"
    with pytest.raises(ValueError):
        restore_database(bad, destination)
    assert not destination.exists()
    other = tmp_path / "foreign-schema.sqlite"
    with sqlite3.connect(other) as db:
        db.execute("CREATE TABLE unrelated(test INTEGER)")
    with pytest.raises(ValueError, match="compatible"):
        verify_database(other)
    link = tmp_path / "link.sqlite"
    link.symlink_to(other)
    with pytest.raises(ValueError, match="symlink"):
        verify_database(link)


def test_foreign_key_integrity_failure_is_detected(tmp_path):
    source = tmp_path / "source.sqlite"
    initialize(source)
    with sqlite3.connect(source) as db:
        db.execute("PRAGMA foreign_keys=OFF")
        db.execute("INSERT INTO devices (id,account_id,name,kind,ingest_token_hash,created_at) "
                   "VALUES (1,999,'orphan','other','dummyhash','2026-11-01')")
    with pytest.raises(ValueError, match="foreign key"):
        verify_database(source)


def test_admin_verify_and_restore_cli(tmp_path):
    source = tmp_path / "source.sqlite"
    initialize(source)
    backup = tmp_path / "snapshot.sqlite"
    backup_database(source, backup)
    dest = tmp_path / "new-location.sqlite"
    assert subprocess.run(
        [sys.executable, "-m", "goreecloud_location.cli", "verify-backup",
         "--source", str(backup)], capture_output=True, text=True
    ).returncode == 0
    result = subprocess.run(
        [sys.executable, "-m", "goreecloud_location.cli", "restore",
         "--source", str(backup), "--destination", str(dest)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    assert dest.is_file()
    result2 = subprocess.run(
        [sys.executable, "-m", "goreecloud_location.cli", "restore",
         "--source", str(backup), "--destination", str(dest)],
        capture_output=True, text=True
    )
    assert result2.returncode != 0
    verify_database(dest)
