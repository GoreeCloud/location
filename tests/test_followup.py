"""Regression coverage for follow-up security, export, and storage guarantees."""
from __future__ import annotations

import os
from pathlib import Path
import sqlite3
import stat

from goreecloud_location.store import backup_database, connect, create_account, initialize, utc_now

from test_api import auth, device


def test_device_rotation_revokes_old_token_without_deleting_history(client):
    alice, bob = auth(client, "alice"), auth(client, "bob")
    registered = device(client, alice)
    device_id = registered["id"]
    old_header = {"Authorization": "Bearer " + registered["ingest_token"]}
    point = {"latitude": 40.1, "longitude": -75.5, "accuracy_m": 3}
    endpoint = f"/api/ingest/{device_id}"
    assert client.post(endpoint, json=point, headers=old_header).status_code == 201

    # A second account cannot rotate or otherwise see this device.
    assert client.post(f"/api/devices/{device_id}/rotate-token", headers=bob).status_code == 404
    rotated = client.post(f"/api/devices/{device_id}/rotate-token", headers=alice)
    assert rotated.status_code == 200
    new_token = rotated.json()["ingest_token"]
    assert new_token != registered["ingest_token"]
    assert client.post(endpoint, json=point, headers=old_header).status_code == 401
    new_header = {"Authorization": "Bearer " + new_token}
    assert client.post(endpoint, json=point, headers=new_header).status_code == 201
    assert client.get("/api/summary", headers=alice).json()["points"] == 2
    assert client.get("/api/summary", headers=bob).json()["points"] == 0
    assert "ingest_token" not in str(client.get("/api/devices", headers=alice).json())
    assert client.get("/api/locations", headers=new_header).status_code == 401


def test_stable_cursor_page_and_owner_isolation(client):
    alice, bob = auth(client, "alice"), auth(client, "bob")
    first = device(client, alice)
    second = device(client, bob)
    for n in range(7):
        point = {"device_id": first["id"], "latitude": 30 + n, "longitude": -81,
                 "recorded_at": "2026-11-01T14:00:00+00:00"}
        assert client.post("/api/locations", headers=alice, json=point).status_code == 201
    assert client.post("/api/locations", headers=bob, json={
        "device_id": second["id"], "latitude": -33, "longitude": -70
    }).status_code == 201

    cursor = None
    collected = []
    while True:
        params = {"device_id": first["id"], "limit": 3}
        if cursor is not None:
            params["cursor"] = cursor
        result = client.get("/api/locations/page", headers=alice, params=params)
        assert result.status_code == 200
        page = result.json()
        collected.extend(x["id"] for x in page["items"])
        if not page["has_more"]:
            assert page["next_cursor"] is None
            break
        assert page["next_cursor"] and page["items"]
        cursor = page["next_cursor"]
    assert len(collected) == 7
    assert len(set(collected)) == 7
    assert collected == sorted(collected, reverse=True)
    assert client.get("/api/locations/page", headers=bob,
                      params={"device_id": first["id"]}).status_code == 404
    assert len(client.get("/api/locations/page", headers=bob).json()["items"]) == 1
    assert client.get("/api/locations/page", headers=alice,
                      params={"cursor": "corrupt"}).status_code == 422
    assert client.get("/api/locations/page", headers=alice,
                      params={"limit": 1000}).status_code == 422
    assert client.get("/api/locations/page").status_code == 401


def test_large_export_has_no_silent_cap(tmp_path):
    db_path = tmp_path / "private" / "location.db"
    # Verify completeness using one storage-backed seed with a dedicated test app.
    from fastapi.testclient import TestClient
    from goreecloud_location.main import create_app
    path = db_path
    app = create_app(path)
    create_account(path, "exportuser", "a sufficiently long private passphrase")
    create_account(path, "other", "another sufficiently long password")
    with TestClient(app) as local:
        session = auth(local, "exportuser", "a sufficiently long private passphrase")
        dd = device(local, session)
        with connect(path) as db:
            db.executemany(
                """INSERT INTO points (device_id,latitude,longitude,recorded_at,received_at)
                   VALUES (?,?,?,?,?)""",
                ((dd["id"], 35.0, -83.0, "2026-11-01T10:00:00+00:00", utc_now())
                 for _ in range(10_012)),
            )
        geo = local.get("/api/export/geojson", headers=session, params={"device_id": dd["id"]})
        assert geo.status_code == 200
        document = geo.json()
        assert document["type"] == "FeatureCollection"
        assert len(document["features"]) == 10_012
        assert "truncated" not in document
        gpx = local.get("/api/export/gpx", headers=session, params={"device_id": dd["id"]})
        assert gpx.status_code == 200
        assert gpx.content.count(b"<trkpt ") == 10_012
        assert gpx.headers.get("X-GoreeCloud-Export-Truncated") is None
        other = auth(local, "other", "another sufficiently long password")
        assert local.get("/api/export/gpx", headers=other,
                         params={"device_id": dd["id"]}).status_code == 404


def test_private_sqlite_modes_and_consistent_backup(tmp_path: Path):
    path = tmp_path / "owner-data" / "location.db"
    previous_mask = os.umask(0o022)
    try:
        initialize(path)
    finally:
        os.umask(previous_mask)
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    create_account(path, "first", "a long and unique admin passphrase")
    with connect(path) as db:
        db.execute("INSERT INTO accounts(username,password_hash,created_at) VALUES(?,?,?)",
                   ("second", "not-an-actual-login-password-hash", utc_now()))
    snapshot = tmp_path / "snapshot.sqlite"
    backup_database(path, snapshot)
    assert stat.S_IMODE(snapshot.stat().st_mode) == 0o600
    with sqlite3.connect(snapshot) as db:
        assert db.execute("SELECT COUNT(*) FROM accounts").fetchone()[0] == 2
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    try:
        backup_database(path, snapshot)
    except FileExistsError:
        pass
    else:
        raise AssertionError("Backup must not overwrite existing destination")
    assert snapshot.exists()
    symlink = tmp_path / "location-link.db"
    symlink.symlink_to(path)
    try:
        initialize(symlink)
    except ValueError:
        pass
    else:
        raise AssertionError("Symlinked SQLite database path must be refused")
