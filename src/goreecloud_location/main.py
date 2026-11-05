"""GoreeCloud Location API.

An authenticated, owner-scoped development foundation. It does not offer public
sharing, covert tracking, professional emergency response, or mobile background
tracking. The default server binds to 127.0.0.1.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import base64
import binascii
import csv
import io
import json
import math
import os
from pathlib import Path
from typing import Literal
import secrets
from xml.etree import ElementTree
from defusedxml.ElementTree import fromstring as safe_xml_fromstring
from defusedxml.common import DefusedXmlException

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, Response
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .security import LoginAttemptLimiter
from .store import connect, default_db_path, hash_password, initialize, token_digest, utc_now, verify_password


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class LoginIn(StrictModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=1, max_length=1024)


class DeviceIn(StrictModel):
    name: str = Field(min_length=1, max_length=80)
    kind: str = Field(default="person", pattern=r"^(person|vehicle|pet|item|asset|other)$")


class PlaceIn(StrictModel):
    name: str = Field(min_length=1, max_length=80)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    radius_m: float = Field(ge=10, le=50000)


class PointIn(StrictModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    accuracy_m: float | None = Field(default=None, ge=0, le=10000)
    altitude_m: float | None = Field(default=None, ge=-11000, le=100000)
    speed_mps: float | None = Field(default=None, ge=0, le=300)
    heading_deg: float | None = Field(default=None, ge=0, le=360)
    battery_percent: int | None = Field(default=None, ge=0, le=100)
    recorded_at: datetime | None = None


class UserPointIn(PointIn):
    device_id: int = Field(ge=1)


class OwnTracksLocation(BaseModel):
    """Subset of OwnTracks' native HTTP JSON used for position ingestion.

    Ignore non-position metadata (Wi-Fi identifiers, contacts, etc.) rather
    than storing sensitive fields that GoreeCloud Location does not need.
    """
    model_config = ConfigDict(extra="ignore", allow_inf_nan=False)

    kind: Literal["location"] = Field(alias="_type")
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    tst: int = Field(ge=0, le=253402300799, strict=True)
    acc: float | None = Field(default=None, ge=0, le=10000)
    alt: float | None = Field(default=None, ge=-11000, le=100000)
    vel: float | None = Field(default=None, ge=0, le=1080)  # km/h
    cog: float | None = Field(default=None, ge=0, le=360)
    batt: int | None = Field(default=None, ge=0, le=100, strict=True)


class RetentionPurgeIn(StrictModel):
    older_than_days: int = Field(ge=1, le=36500)
    expected_points: int = Field(ge=0)
    expected_events: int = Field(ge=0)
    confirmation: Literal["DELETE_OLD_HISTORY"]


def api_error(status: int, detail: str) -> None:
    raise HTTPException(status_code=status, detail=detail)


def haversine_m(a_lat: float, a_lon: float, b_lat: float, b_lon: float) -> float:
    a1, a2 = math.radians(a_lat), math.radians(b_lat)
    da, db = a2 - a1, math.radians(b_lon - a_lon)
    h = math.sin(da / 2) ** 2 + math.cos(a1) * math.cos(a2) * math.sin(db / 2) ** 2
    return 12742000 * math.asin(min(1.0, math.sqrt(h)))


def timestamp_for(value: datetime | None) -> str:
    if value is None:
        value = datetime.now(timezone.utc)
    if value.tzinfo is None or value.utcoffset() is None:
        api_error(422, "recorded_at must include a timezone offset")
    value = value.astimezone(timezone.utc)
    if value > datetime.now(timezone.utc) + timedelta(minutes=5):
        api_error(422, "Future location timestamps are not accepted")
    return value.isoformat(timespec="milliseconds")


def rowdict(row):
    return dict(row) if row is not None else None


def clean_name(name: str) -> str:
    value = name.strip()
    if not value:
        api_error(422, "Name cannot be blank")
    return value


def create_app(db_path: Path | None = None) -> FastAPI:
    path = Path(db_path) if db_path is not None else default_db_path()
    initialize(path)
    app = FastAPI(title="GoreeCloud Location", version="0.1.0",
                  docs_url=None, redoc_url=None, openapi_url=None)
    bearer = HTTPBearer(auto_error=False)
    basic = HTTPBasic(auto_error=False)
    login_limiter = LoginAttemptLimiter()
    # Always run scrypt for an unknown username to reduce account enumeration
    # via response timing. No account uses this random dummy password hash.
    dummy_password_hash = hash_password(secrets.token_urlsafe(32))

    def account(creds: HTTPAuthorizationCredentials | None = Depends(bearer)):
        if not creds or creds.scheme.lower() != "bearer" or len(creds.credentials) > 256:
            api_error(401, "Authentication required")
        with connect(path) as db:
            record = db.execute(
                """SELECT a.id, a.username, a.role FROM sessions s
                   JOIN accounts a ON a.id=s.account_id
                   WHERE s.token_hash=? AND s.expires_at>?""",
                (token_digest(creds.credentials), utc_now()),
            ).fetchone()
        if not record:
            api_error(401, "Session expired or invalid")
        return rowdict(record)

    def owned_device(db, account_id: int, device_id: int):
        row = db.execute(
            "SELECT * FROM devices WHERE id=? AND account_id=?", (device_id, account_id)
        ).fetchone()
        if not row:
            api_error(404, "Device not found")
        return row

    def ingest(db, device, point: PointIn):
        stamp = timestamp_for(point.recorded_at)
        last = db.execute(
            """SELECT recorded_at FROM points WHERE device_id=?
               ORDER BY recorded_at DESC, id DESC LIMIT 1""",
            (device["id"],),
        ).fetchone()
        cur = db.execute(
            """INSERT INTO points
               (device_id, latitude, longitude, accuracy_m, altitude_m, speed_mps,
                heading_deg, battery_percent, recorded_at, received_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (device["id"], point.latitude, point.longitude, point.accuracy_m,
             point.altitude_m, point.speed_mps, point.heading_deg,
             point.battery_percent, stamp, utc_now()),
        )
        alerts = []
        # Only strictly newer observations can update current geofence state.
        # A conflicting position at the exact same recorded millisecond is
        # historical/ambiguous; allowing it to flip state can invent a false
        # arrival/departure alert. Preserve the point for review and export.
        if last and stamp <= last["recorded_at"]:
            return {"id": cur.lastrowid, "recorded_at": stamp, "events": alerts}
        for place in db.execute(
            "SELECT * FROM places WHERE account_id=?", (device["account_id"],)
        ).fetchall():
            if point.accuracy_m is None or point.accuracy_m > min(100, place["radius_m"] / 2):
                continue
            is_inside = haversine_m(point.latitude, point.longitude,
                                    place["latitude"], place["longitude"]) <= place["radius_m"]
            prev = db.execute(
                "SELECT inside FROM geofence_state WHERE device_id=? AND place_id=?",
                (device["id"], place["id"]),
            ).fetchone()
            if prev is None:
                db.execute(
                    "INSERT INTO geofence_state(device_id,place_id,inside) VALUES(?,?,?)",
                    (device["id"], place["id"], int(is_inside)),
                )
            elif bool(prev["inside"]) != is_inside:
                db.execute(
                    "UPDATE geofence_state SET inside=? WHERE device_id=? AND place_id=?",
                    (int(is_inside), device["id"], place["id"]),
                )
                kind = "arrival" if is_inside else "departure"
                db.execute(
                    "INSERT INTO events(device_id,place_id,kind,recorded_at) VALUES(?,?,?,?)",
                    (device["id"], place["id"], kind, stamp),
                )
                alerts.append({"kind": kind, "place": place["name"]})
        return {"id": cur.lastrowid, "recorded_at": stamp, "events": alerts}

    def import_validated_batch(owner_id: int, device_id: int,
                               pending: list[tuple[str, PointIn]]):
        """Commit a previously validated history batch with shared deduplication.

        CSV and GPX imports use identical owner checks, chronology and
        transactional geofence semantics; any database error rolls back all.
        """
        pending.sort(key=lambda item: item[0])
        imported = duplicates = generated_events = 0
        with connect(path) as db:
            db.execute("BEGIN IMMEDIATE")
            device = owned_device(db, owner_id, device_id)
            for stamp, point in pending:
                seen = db.execute(
                    """SELECT 1 FROM points WHERE device_id=? AND recorded_at=?
                       AND latitude=? AND longitude=? LIMIT 1""",
                    (device_id, stamp, point.latitude, point.longitude),
                ).fetchone()
                if seen:
                    duplicates += 1
                    continue
                result = ingest(db, device, point)
                imported += 1
                generated_events += len(result["events"])
        return {"device_id": device_id, "imported": imported,
                "skipped_duplicates": duplicates, "geofence_events": generated_events}

    @app.middleware("http")
    async def safety_headers(request: Request, call_next):
        result: Response = await call_next(request)
        result.headers["X-Content-Type-Options"] = "nosniff"
        result.headers["Referrer-Policy"] = "no-referrer"
        result.headers["X-Frame-Options"] = "DENY"
        result.headers["Permissions-Policy"] = "geolocation=(self), microphone=(), camera=()"
        result.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; "
            "base-uri 'none'; object-src 'none'; frame-ancestors 'none'; form-action 'self'"
        )
        if request.url.path.startswith("/api/"):
            result.headers["Cache-Control"] = "no-store"
        return result

    @app.get("/api/health")
    def health():
        return {"status": "ok", "service": "GoreeCloud Location", "version": "0.1.0"}

    @app.get("/api/config")
    def public_config():
        tile = os.environ.get("GC_TILE_TEMPLATE", "")
        if tile and (
            not tile.startswith("/") or tile.startswith("//")
            or "\\" in tile or any(ord(char) < 32 or ord(char) == 127 for char in tile)
        ):
            # A leading / followed by a backslash is normalized by browsers
            # into //external-host. Reject that and other URL controls.
            tile = ""
        return {"tile_template": tile, "self_hosted": True}

    @app.post("/api/auth/login")
    def login(body: LoginIn, request: Request):
        # The bounded global/username/peer budget is reserved before running
        # the expensive scrypt verifier, even for unknown usernames.
        peer = request.client.host if request.client else "unknown"
        if not login_limiter.allow(body.username, peer):
            api_error(429, "Too many attempts; try again later")
        with connect(path) as db:
            record = db.execute(
                "SELECT id, username, role, password_hash FROM accounts WHERE username=?",
                (body.username,),
            ).fetchone()
            match = verify_password(
                body.password, record["password_hash"] if record else dummy_password_hash
            )
            if not record or not match:
                api_error(401, "Invalid username or password")
            token = secrets.token_urlsafe(32)
            expires = (datetime.now(timezone.utc) + timedelta(hours=8)).isoformat()
            db.execute("DELETE FROM sessions WHERE expires_at<=?", (utc_now(),))
            db.execute(
                "INSERT INTO sessions(token_hash,account_id,expires_at) VALUES(?,?,?)",
                (token_digest(token), record["id"], expires),
            )
            # Bound live sessions per account without a schema migration.
            db.execute(
                """DELETE FROM sessions WHERE token_hash IN (
                       SELECT token_hash FROM sessions WHERE account_id=?
                       ORDER BY expires_at DESC, token_hash DESC
                       LIMIT -1 OFFSET 20
                   )""",
                (record["id"],),
            )
        login_limiter.clear_user(body.username)
        return {"access_token": token, "token_type": "bearer",
                "expires_at": expires,
                "user": {"id": record["id"], "username": record["username"], "role": record["role"]}}

    @app.post("/api/auth/logout", status_code=204)
    def logout(creds: HTTPAuthorizationCredentials | None = Depends(bearer),
               user=Depends(account)):
        with connect(path) as db:
            db.execute("DELETE FROM sessions WHERE token_hash=?", (token_digest(creds.credentials),))
        return Response(status_code=204)

    @app.post("/api/auth/logout-all", status_code=204)
    def logout_all(user=Depends(account)):
        """Revoke every login session owned by this account, including this one.

        Device ingestion keys are separate credentials and are not revoked.
        """
        with connect(path) as db:
            db.execute("DELETE FROM sessions WHERE account_id=?", (user["id"],))
        return Response(status_code=204)

    @app.get("/api/me")
    def me(user=Depends(account)):
        return user

    def retention_cutoff(older_than_days: int) -> str:
        return (datetime.now(timezone.utc) - timedelta(days=older_than_days)).isoformat(
            timespec="milliseconds"
        )

    def retention_counts(db, owner_id: int, cutoff: str) -> tuple[int, int, int]:
        points = db.execute(
            """SELECT COUNT(*) FROM points p JOIN devices d ON d.id=p.device_id
               WHERE d.account_id=? AND p.recorded_at<?""",
            (owner_id, cutoff),
        ).fetchone()[0]
        events = db.execute(
            """SELECT COUNT(*) FROM events e JOIN devices d ON d.id=e.device_id
               WHERE d.account_id=? AND e.recorded_at<?""",
            (owner_id, cutoff),
        ).fetchone()[0]
        devices = db.execute(
            """SELECT COUNT(*) FROM devices d WHERE d.account_id=? AND (
                    EXISTS (SELECT 1 FROM points p WHERE p.device_id=d.id AND p.recorded_at<?)
                 OR EXISTS (SELECT 1 FROM events e WHERE e.device_id=d.id AND e.recorded_at<?)
               )""",
            (owner_id, cutoff, cutoff),
        ).fetchone()[0]
        return int(points), int(events), int(devices)

    @app.get("/api/retention/preview")
    def retention_preview(older_than_days: int = Query(ge=1, le=36500),
                          user=Depends(account)):
        """Only return counts; never mutate stored GPS positions."""
        cutoff = retention_cutoff(older_than_days)
        with connect(path) as db:
            points, events, devices = retention_counts(db, user["id"], cutoff)
        return {"older_than_days": older_than_days, "cutoff_utc": cutoff,
                "eligible_points": points, "eligible_events": events,
                "affected_devices": devices,
                "warning": "Preview only. Backups and exported copies are not included."}

    @app.post("/api/retention/purge")
    def retention_purge(body: RetentionPurgeIn, user=Depends(account)):
        """Manually purge only an owner's old GPS points and associated events.

        The explicit confirmation and a transaction/lock prevent partial writes.
        Device registrations, newer history and token credentials remain.
        This is logical live-database deletion, not forensic erasure of backups.
        """
        cutoff = retention_cutoff(body.older_than_days)
        with connect(path) as db:
            db.execute("BEGIN IMMEDIATE")
            current_points, current_events, _ = retention_counts(
                db, user["id"], cutoff
            )
            if (current_points != body.expected_points
                    or current_events != body.expected_events):
                api_error(409, "Eligible records changed; preview again before deleting")
            affected = [
                row[0] for row in db.execute(
                    """SELECT d.id FROM devices d WHERE d.account_id=? AND (
                           EXISTS (SELECT 1 FROM points p
                                   WHERE p.device_id=d.id AND p.recorded_at<?)
                        OR EXISTS (SELECT 1 FROM events e
                                   WHERE e.device_id=d.id AND e.recorded_at<?)
                       )""",
                    (user["id"], cutoff, cutoff),
                )
            ]
            points = db.execute(
                """DELETE FROM points WHERE id IN (
                      SELECT p.id FROM points p JOIN devices d ON d.id=p.device_id
                      WHERE d.account_id=? AND p.recorded_at<?
                    )""",
                (user["id"], cutoff),
            ).rowcount
            events = db.execute(
                """DELETE FROM events WHERE id IN (
                      SELECT e.id FROM events e JOIN devices d ON d.id=e.device_id
                      WHERE d.account_id=? AND e.recorded_at<?
                    )""",
                (user["id"], cutoff),
            ).rowcount
            for device_id in affected:
                db.execute("DELETE FROM geofence_state WHERE device_id=?", (device_id,))
        return {"cutoff_utc": cutoff, "deleted_points": points,
                "deleted_events": events, "reset_devices": len(affected),
                "warning": "Live records deleted. Backups, exports and offline caches remain."}

    @app.get("/api/summary")
    def summary(user=Depends(account)):
        with connect(path) as db:
            devices = db.execute("SELECT COUNT(*) FROM devices WHERE account_id=?", (user["id"],)).fetchone()[0]
            points = db.execute(
                "SELECT COUNT(*) FROM points p JOIN devices d ON d.id=p.device_id WHERE d.account_id=?",
                (user["id"],),
            ).fetchone()[0]
            places = db.execute("SELECT COUNT(*) FROM places WHERE account_id=?", (user["id"],)).fetchone()[0]
            alerts = db.execute(
                """SELECT COUNT(*) FROM events e JOIN devices d ON d.id=e.device_id
                   WHERE d.account_id=?""", (user["id"],)
            ).fetchone()[0]
        return {"devices": devices, "points": points, "places": places, "events": alerts}

    @app.post("/api/devices", status_code=201)
    def create_device(body: DeviceIn, user=Depends(account)):
        secret = secrets.token_urlsafe(32)
        with connect(path) as db:
            cur = db.execute(
                """INSERT INTO devices(account_id,name,kind,ingest_token_hash,created_at)
                   VALUES(?,?,?,?,?)""",
                (user["id"], clean_name(body.name), body.kind, token_digest(secret), utc_now()),
            )
        return {"id": cur.lastrowid, "name": body.name.strip(), "kind": body.kind,
                "ingest_token": secret, "warning": "Save this token now. It is not shown again."}

    @app.get("/api/devices")
    def devices(user=Depends(account)):
        with connect(path) as db:
            rows = db.execute(
                """SELECT d.id,d.name,d.kind,d.created_at,
                          p.latitude,p.longitude,p.recorded_at,p.accuracy_m,p.battery_percent
                   FROM devices d LEFT JOIN points p ON p.id = (
                       SELECT id FROM points WHERE device_id=d.id
                       ORDER BY recorded_at DESC,id DESC LIMIT 1)
                   WHERE d.account_id=? ORDER BY d.id DESC""",
                (user["id"],),
            ).fetchall()
        return [rowdict(row) for row in rows]

    @app.post("/api/devices/{device_id}/rotate-token")
    def rotate_device_token(device_id: int, user=Depends(account)):
        """Issue a replacement write-only token without deleting the device's history.

        The previous token ceases to work immediately when the database commit
        completes; no history or device identity is lost.
        """
        new_token = secrets.token_urlsafe(32)
        with connect(path) as db:
            owned_device(db, user["id"], device_id)
            db.execute(
                "UPDATE devices SET ingest_token_hash=? WHERE id=? AND account_id=?",
                (token_digest(new_token), device_id, user["id"]),
            )
        return {"id": device_id, "ingest_token": new_token,
                "warning": "The old token is now revoked. Save the new token once and reconfigure your device."}

    @app.delete("/api/devices/{device_id}", status_code=204)
    def delete_device(device_id: int, user=Depends(account)):
        with connect(path) as db:
            owned_device(db, user["id"], device_id)
            db.execute("DELETE FROM devices WHERE id=?", (device_id,))
        return Response(status_code=204)

    @app.delete("/api/devices/{device_id}/history", status_code=204)
    def clear_device_history(device_id: int, user=Depends(account)):
        """Permanently erase one owned device's points, events and fence state.

        The registered device and its credential remain intact.
        """
        with connect(path) as db:
            owned_device(db, user["id"], device_id)
            db.execute("DELETE FROM events WHERE device_id=?", (device_id,))
            db.execute("DELETE FROM geofence_state WHERE device_id=?", (device_id,))
            db.execute("DELETE FROM points WHERE device_id=?", (device_id,))
        return Response(status_code=204)

    @app.post("/api/devices/{device_id}/import/csv", status_code=201)
    async def import_csv(device_id: int, request: Request, user=Depends(account)):
        """Import a bounded UTF-8 CSV into one owned device, atomically.

        The entire file is validated before any write. Files larger than 2 MiB
        or containing more than 5,000 records are rejected. Historical records
        are sorted before ingestion for deterministic transition processing.
        """
        if not request.headers.get("content-type", "").lower().startswith("text/csv"):
            api_error(415, "Send raw UTF-8 CSV with Content-Type: text/csv")
        with connect(path) as db:
            device = owned_device(db, user["id"], device_id)

        payload = bytearray()
        async for chunk in request.stream():
            if len(payload) + len(chunk) > 2_097_152:
                api_error(413, "CSV is limited to 2 MiB")
            payload.extend(chunk)
        try:
            content = bytes(payload).decode("utf-8-sig")
        except UnicodeDecodeError:
            api_error(422, "CSV must be UTF-8")
        reader = csv.DictReader(io.StringIO(content, newline=""), strict=True)
        allowed = {"latitude", "longitude", "recorded_at", "accuracy_m",
                   "altitude_m", "speed_mps", "heading_deg", "battery_percent"}
        required = {"latitude", "longitude", "recorded_at"}
        try:
            columns = reader.fieldnames
            if (not columns or len(columns) != len(set(columns)) or
                    not required.issubset(columns) or not set(columns).issubset(allowed)):
                api_error(422, "CSV headers require latitude,longitude,recorded_at; optional GPS metadata only")

            pending: list[tuple[str, PointIn]] = []
            for row_number, row in enumerate(reader, start=2):
                if row_number > 5001:
                    api_error(413, "CSV is limited to 5,000 data rows")
                if None in row:
                    api_error(422, f"Row {row_number}: too many columns")
                values = {key: val.strip() for key, val in row.items()
                          if val is not None and val.strip() != ""}
                if not required.issubset(values):
                    api_error(422, f"Row {row_number}: missing coordinates or recorded_at")
                try:
                    point = PointIn.model_validate(values)
                    stamp = timestamp_for(point.recorded_at)
                except ValidationError:
                    api_error(422, f"Row {row_number}: invalid GPS value")
                pending.append((stamp, point))
        except csv.Error:
            api_error(422, "Malformed CSV document")
        if not pending:
            api_error(422, "CSV contains no location records")
        return import_validated_batch(user["id"], device_id, pending)

    @app.post("/api/devices/{device_id}/import/gpx", status_code=201)
    async def import_gpx(device_id: int, request: Request, user=Depends(account)):
        """Owner-controlled, atomic import of timestamped GPX track points.

        DefusedXML rejects DTD, entity and external resource use. This path
        imports trk/trkseg/trkpt only, never waypoints or user-supplied alerts.
        """
        content_type = request.headers.get("content-type", "").split(";", 1)[0].lower().strip()
        if content_type not in {"application/gpx+xml", "application/xml", "text/xml"}:
            api_error(415, "GPX must use application/gpx+xml or XML content type")
        with connect(path) as db:
            owned_device(db, user["id"], device_id)

        payload = bytearray()
        async for chunk in request.stream():
            if len(payload) + len(chunk) > 2_097_152:
                api_error(413, "GPX is limited to 2 MiB")
            payload.extend(chunk)
        if not payload:
            api_error(422, "GPX file is empty")
        try:
            root = safe_xml_fromstring(
                bytes(payload), forbid_dtd=True,
                forbid_entities=True, forbid_external=True,
            )
        except (ElementTree.ParseError, DefusedXmlException, ValueError, RecursionError):
            api_error(422, "Malformed or unsafe GPX document")

        namespaces = {
            "http://www.topografix.com/GPX/1/0",
            "http://www.topografix.com/GPX/1/1",
        }
        if not any(root.tag == f"{{{ns}}}gpx" for ns in namespaces):
            api_error(422, "Expected GPX 1.0 or 1.1 document")
        ns = root.tag.rsplit("}", 1)[0][1:]
        tag = lambda name: f"{{{ns}}}{name}"
        trackpoints = root.findall(
            f"{tag('trk')}/{tag('trkseg')}/{tag('trkpt')}"
        )
        if len(trackpoints) > 5000:
            api_error(413, "GPX is limited to 5,000 track points")
        if not trackpoints:
            api_error(422, "GPX contains no track points")

        pending: list[tuple[str, PointIn]] = []
        for number, element in enumerate(trackpoints, start=1):
            try:
                gpx_time = element.findtext(tag("time"))
                if not gpx_time or "T" not in gpx_time:
                    api_error(422, f"GPX track point {number} needs an ISO 8601 time")
                values = {
                    "latitude": element.attrib["lat"],
                    "longitude": element.attrib["lon"],
                    "recorded_at": gpx_time,
                }
                elevation = element.findtext(tag("ele"))
                if elevation is not None:
                    values["altitude_m"] = elevation
                point = PointIn.model_validate(values)
                stamp = timestamp_for(point.recorded_at)
            except (KeyError, ValidationError, ValueError, TypeError):
                api_error(422, f"GPX track point {number} is invalid")
            pending.append((stamp, point))
        return import_validated_batch(user["id"], device_id, pending)

    @app.post("/api/locations", status_code=201)
    def create_point(body: UserPointIn, user=Depends(account)):
        with connect(path) as db:
            db.execute("BEGIN IMMEDIATE")
            device = owned_device(db, user["id"], body.device_id)
            return ingest(db, device, body)

    @app.post("/api/ingest/{device_id}", status_code=201)
    def ingest_device(device_id: int, body: PointIn,
                      creds: HTTPAuthorizationCredentials | None = Depends(bearer)):
        if not creds or creds.scheme.lower() != "bearer" or len(creds.credentials) > 256:
            api_error(401, "Device token required")
        with connect(path) as db:
            db.execute("BEGIN IMMEDIATE")
            device = db.execute(
                "SELECT * FROM devices WHERE id=? AND ingest_token_hash=?",
                (device_id, token_digest(creds.credentials)),
            ).fetchone()
            if not device:
                api_error(401, "Invalid device token")
            return ingest(db, device, body)

    @app.post("/api/ingest/owntracks/{device_id}")
    async def ingest_owntracks(device_id: int, request: Request,
                               creds: HTTPBasicCredentials | None = Depends(basic)):
        """Accept the OwnTracks HTTP location subset via write-only device key.

        Basic username is 'owntracks', Basic password is the existing one-time
        device ingestion token. Never use account login passwords for tracking.
        A valid empty or recognized non-location message is acknowledged
        without modifying positions, places or geofence state.
        """
        if (creds is None or creds.username != "owntracks"
                or not creds.password or len(creds.password) > 256):
            raise HTTPException(401, "Device token required",
                                headers={"WWW-Authenticate": "Basic"})
        digest = token_digest(creds.password)
        with connect(path) as db:
            registered = db.execute(
                "SELECT id FROM devices WHERE id=? AND ingest_token_hash=?",
                (device_id, digest),
            ).fetchone()
        if registered is None:
            raise HTTPException(401, "Invalid device token",
                                headers={"WWW-Authenticate": "Basic"})

        # Bound request size regardless of HTTP content length or streaming
        # transfer encoding; do not log the incoming private GPS payload.
        payload = bytearray()
        async for chunk in request.stream():
            if len(payload) + len(chunk) > 16384:
                api_error(413, "OwnTracks payload exceeds 16 KiB")
            payload.extend(chunk)
        if not payload:
            return []  # OwnTracks sends empty messages for some housekeeping.
        content_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            api_error(415, "OwnTracks requires application/json")
        try:
            data = json.loads(
                bytes(payload).decode("utf-8"),
                parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Non-finite JSON")),
            )
        except (UnicodeDecodeError, ValueError, RecursionError):
            api_error(422, "Invalid OwnTracks JSON")
        if not isinstance(data, dict):
            api_error(422, "OwnTracks JSON must be an object")

        kind = data.get("_type")
        if not isinstance(kind, str):
            api_error(422, "Unsupported OwnTracks message type")
        # OwnTracks sends transition, waypoint and status messages as well.
        # Device-reported transitions are not trusted as server geofences.
        if kind in {"lwt", "status", "transition", "waypoint", "beacon",
                    "steps", "card", "cmd", "configuration", "request"}:
            return []
        if kind != "location":
            api_error(422, "Unsupported OwnTracks message type")

        try:
            location = OwnTracksLocation.model_validate(data)
            recorded_at = datetime.fromtimestamp(location.tst, tz=timezone.utc)
            point = PointIn(
                latitude=location.lat, longitude=location.lon,
                recorded_at=recorded_at, accuracy_m=location.acc,
                altitude_m=location.alt,
                speed_mps=(location.vel / 3.6 if location.vel is not None else None),
                heading_deg=location.cog, battery_percent=location.batt,
            )
        except (ValidationError, ValueError, OSError, OverflowError):
            api_error(422, "Invalid OwnTracks location fields")

        with connect(path) as db:
            # Serialize with all other GPS ingestion and re-check token after
            # acquiring the writer lock, so key rotation cannot race the write.
            db.execute("BEGIN IMMEDIATE")
            registered = db.execute(
                "SELECT * FROM devices WHERE id=? AND ingest_token_hash=?",
                (device_id, digest),
            ).fetchone()
            if registered is None:
                raise HTTPException(401, "Invalid device token",
                                    headers={"WWW-Authenticate": "Basic"})
            ingest(db, registered, point)
        return []  # Native OwnTracks HTTP response format.

    @app.get("/api/locations")
    def locations(device_id: int | None = None,
                  limit: int = Query(default=300, ge=1, le=1000),
                  user=Depends(account)):
        with connect(path) as db:
            if device_id is not None:
                owned_device(db, user["id"], device_id)
                rows = db.execute(
                    """SELECT p.*,d.name AS device_name,d.kind AS device_kind
                       FROM points p JOIN devices d ON d.id=p.device_id
                       WHERE d.account_id=? AND d.id=?
                       ORDER BY p.recorded_at DESC,p.id DESC LIMIT ?""",
                    (user["id"], device_id, limit),
                ).fetchall()
            else:
                rows = db.execute(
                    """SELECT p.*,d.name AS device_name,d.kind AS device_kind
                       FROM points p JOIN devices d ON d.id=p.device_id
                       WHERE d.account_id=? ORDER BY p.recorded_at DESC,p.id DESC LIMIT ?""",
                    (user["id"], limit),
                ).fetchall()
        return [rowdict(row) for row in rows]

    def encode_cursor(recorded_at: str, point_id: int) -> str:
        value = json.dumps([recorded_at, point_id], separators=(",", ":")).encode()
        return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")

    def decode_cursor(cursor: str | None) -> tuple[str, int] | None:
        if cursor is None:
            return None
        if not 1 <= len(cursor) <= 256 or not all(c.isalnum() or c in "-_" for c in cursor):
            api_error(422, "Invalid location cursor")
        try:
            data = base64.b64decode(cursor + "=" * (-len(cursor) % 4), altchars=b"-_", validate=True)
            pair = json.loads(data)
            if not (isinstance(pair, list) and len(pair) == 2
                    and isinstance(pair[0], str) and len(pair[0]) <= 40
                    and type(pair[1]) is int and pair[1] > 0
                    and datetime.fromisoformat(pair[0]).tzinfo is not None):
                raise ValueError("Malformed cursor")
            return pair[0], pair[1]
        except (ValueError, TypeError, UnicodeDecodeError, binascii.Error):
            api_error(422, "Invalid location cursor")

    @app.get("/api/locations/page")
    def location_page(device_id: int | None = None,
                      limit: int = Query(default=100, ge=1, le=500),
                      cursor: str | None = Query(default=None, max_length=256),
                      user=Depends(account)):
        """Keyset pagination, ordered by timestamp and stable ID.

        Cursor never authorizes data: every page is scoped to the user.
        """
        before = decode_cursor(cursor)
        clauses = ["d.account_id=?"]
        args: list[object] = [user["id"]]
        with connect(path) as db:
            if device_id is not None:
                owned_device(db, user["id"], device_id)
                clauses.append("d.id=?")
                args.append(device_id)
            if before is not None:
                clauses.append("(p.recorded_at < ? OR (p.recorded_at = ? AND p.id < ?))")
                args.extend([before[0], before[0], before[1]])
            query = ("""SELECT p.*, d.name AS device_name, d.kind AS device_kind
                        FROM points p JOIN devices d ON d.id=p.device_id
                        WHERE """ + " AND ".join(clauses) +
                     " ORDER BY p.recorded_at DESC, p.id DESC LIMIT ?")
            args.append(limit + 1)
            rows = db.execute(query, args).fetchall()
        more = len(rows) > limit
        items = [rowdict(r) for r in rows[:limit]]
        next_cursor = (encode_cursor(items[-1]["recorded_at"], items[-1]["id"])
                       if more and items else None)
        return {"items": items, "next_cursor": next_cursor, "has_more": more}

    @app.delete("/api/locations/{point_id}", status_code=204)
    def delete_point(point_id: int, user=Depends(account)):
        with connect(path) as db:
            point = db.execute(
                """SELECT p.device_id, p.recorded_at FROM points p
                   JOIN devices d ON d.id=p.device_id
                   WHERE p.id=? AND d.account_id=?""",
                (point_id, user["id"]),
            ).fetchone()
            if point is None:
                api_error(404, "Location not found")
            db.execute("DELETE FROM points WHERE id=?", (point_id,))
            # Events reveal an inferred place visit; remove those attached to
            # the deleted timestamp and reset state to avoid stale transitions.
            db.execute(
                "DELETE FROM events WHERE device_id=? AND recorded_at=?",
                (point["device_id"], point["recorded_at"]),
            )
            db.execute("DELETE FROM geofence_state WHERE device_id=?", (point["device_id"],))
        return Response(status_code=204)

    @app.get("/api/places")
    def places(user=Depends(account)):
        with connect(path) as db:
            rows = db.execute(
                "SELECT * FROM places WHERE account_id=? ORDER BY id DESC", (user["id"],)
            ).fetchall()
        return [rowdict(row) for row in rows]

    @app.post("/api/places", status_code=201)
    def create_place(body: PlaceIn, user=Depends(account)):
        with connect(path) as db:
            cur = db.execute(
                """INSERT INTO places(account_id,name,latitude,longitude,radius_m,created_at)
                   VALUES(?,?,?,?,?,?)""",
                (user["id"], clean_name(body.name), body.latitude, body.longitude,
                 body.radius_m, utc_now()),
            )
        return {"id": cur.lastrowid, **body.model_dump()}

    @app.delete("/api/places/{place_id}", status_code=204)
    def delete_place(place_id: int, user=Depends(account)):
        with connect(path) as db:
            cur = db.execute(
                "DELETE FROM places WHERE id=? AND account_id=?", (place_id, user["id"])
            )
            if not cur.rowcount:
                api_error(404, "Place not found")
        return Response(status_code=204)

    @app.get("/api/events")
    def events(limit: int = Query(default=40, ge=1, le=200), user=Depends(account)):
        with connect(path) as db:
            rows = db.execute(
                """SELECT e.id,e.kind,e.recorded_at,d.name AS device_name,
                          pl.name AS place_name
                   FROM events e JOIN devices d ON d.id=e.device_id
                   JOIN places pl ON pl.id=e.place_id
                   WHERE d.account_id=?
                   ORDER BY e.recorded_at DESC,e.id DESC LIMIT ?""",
                (user["id"], limit),
            ).fetchall()
        return [rowdict(row) for row in rows]

    def iter_export_rows(owner_id: int, device_id: int):
        """Stream every historical position in ascending timestamp order.

        A new connection and an owner-constrained query remain active during the
        response; no unbounded fetchall or silent fixed-record cap.
        """
        with connect(path) as db:
            rows = db.execute(
                """SELECT p.latitude,p.longitude,p.altitude_m,p.recorded_at,
                          p.accuracy_m,p.speed_mps
                   FROM points p JOIN devices d ON d.id=p.device_id
                   WHERE d.account_id=? AND d.id=?
                   ORDER BY p.recorded_at ASC,p.id ASC""",
                (owner_id, device_id),
            )
            yield from rows

    @app.get("/api/export/geojson")
    def export_geojson(device_id: int, user=Depends(account)):
        with connect(path) as db:
            owned_device(db, user["id"], device_id)
        owner_id = user["id"]

        def generate():
            yield '{"type":"FeatureCollection","features":['
            first = True
            for r in iter_export_rows(owner_id, device_id):
                feature = {
                    "type": "Feature",
                    "geometry": {"type": "Point",
                                 "coordinates": [r["longitude"], r["latitude"]]},
                    "properties": {
                        "recorded_at": r["recorded_at"], "altitude_m": r["altitude_m"],
                        "accuracy_m": r["accuracy_m"], "speed_mps": r["speed_mps"]
                    },
                }
                if not first:
                    yield ","
                yield json.dumps(feature, separators=(",", ":"), allow_nan=False)
                first = False
            yield ']}'

        return StreamingResponse(generate(), media_type="application/geo+json",
                                 headers={"Content-Disposition": 'attachment; filename="locations.geojson"'})

    @app.get("/api/export/gpx")
    def export_gpx(device_id: int, user=Depends(account)):
        with connect(path) as db:
            owned_device(db, user["id"], device_id)
        owner_id = user["id"]

        def generate():
            yield (b'<?xml version="1.0" encoding="utf-8"?>'
                   b'<gpx xmlns="http://www.topografix.com/GPX/1/1" '
                   b'version="1.1" creator="GoreeCloud Location"><trk><trkseg>')
            for r in iter_export_rows(owner_id, device_id):
                pt = ElementTree.Element("trkpt", attrib={
                    "lat": str(r["latitude"]), "lon": str(r["longitude"])
                })
                if r["altitude_m"] is not None:
                    ElementTree.SubElement(pt, "ele").text = str(r["altitude_m"])
                ElementTree.SubElement(pt, "time").text = r["recorded_at"]
                yield ElementTree.tostring(pt, encoding="utf-8")
            yield b"</trkseg></trk></gpx>"

        return StreamingResponse(generate(), media_type="application/gpx+xml",
                                 headers={"Content-Disposition": 'attachment; filename="locations.gpx"'})

    static_dir = Path(__file__).parent / "static"
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
    return app


app = create_app()
