"""Owner-controlled server-side location collection, without history erasure."""
from datetime import datetime, timedelta, timezone
import sqlite3
import time

from test_api import auth, client, device
from goreecloud_location.store import initialize, connect


def status(client, account, device_id, paused):
    response = client.put(f"/api/devices/{device_id}/collection",
                          headers=account, json={"paused": paused})
    assert response.status_code == 200, response.text
    assert response.json()["tracking_paused"] is paused
    return response.json()


def location(client, owner, device_id, lat=35, stamp=None):
    body = {"device_id": device_id, "latitude": lat,
            "longitude": -83, "accuracy_m": 5}
    if stamp is not None:
        body["recorded_at"] = stamp
    return client.post("/api/locations", headers=owner, json=body)


def test_owner_pause_resume_is_isolated_idempotent_and_preserves_history(client):
    alice = auth(client)
    bob = auth(client, "bob")
    tracking = device(client, alice)
    other = device(client, bob)
    d = tracking["id"]
    assert client.get("/api/devices", headers=alice).json()[0]["tracking_paused"] == 0
    assert client.get("/api/devices", headers=bob).json()[0]["id"] == other["id"]
    old = "2026-10-01T10:00:00Z"
    assert location(client, alice, d, stamp=old).status_code == 201

    path = f"/api/devices/{d}/collection"
    assert client.put(path, json={"paused": True}).status_code == 401
    assert client.put(path, headers=bob, json={"paused": True}).status_code == 404
    assert client.put(path, headers={"Authorization": "Bearer "+tracking["ingest_token"]},
                      json={"paused": True}).status_code == 401
    for incorrect in ("true", 1, None):
        assert client.put(path, headers=alice, json={"paused": incorrect}).status_code == 422

    first = status(client, alice, d, True)
    assert first["tracking_resumed_at"] is None
    assert status(client, alice, d, True)["tracking_resumed_at"] is None
    assert client.get("/api/devices", headers=alice).json()[0]["tracking_paused"] == 1
    assert location(client, alice, d, lat=36).status_code == 409
    assert client.get("/api/summary", headers=alice).json()["points"] == 1
    assert client.get("/api/summary", headers=bob).json()["points"] == 0

    resumed = status(client, alice, d, False)
    assert resumed["tracking_resumed_at"]
    assert datetime.fromisoformat(resumed["tracking_resumed_at"]).tzinfo is not None
    assert status(client, alice, d, False)["tracking_resumed_at"] == resumed["tracking_resumed_at"]
    assert location(client, alice, d, lat=36, stamp=old).status_code == 409
    time.sleep(0.025)
    assert location(client, alice, d, lat=36).status_code == 201
    assert client.get("/api/summary", headers=alice).json()["points"] == 2
    assert client.get("/api/devices", headers=alice).json()[0]["tracking_paused"] == 0
    assert client.get("/api/summary", headers=bob).json()["devices"] == 1


def test_paused_device_rejects_owner_device_owntracks_and_all_history_imports(client):
    alice = auth(client)
    tracker = device(client, alice)
    d = tracker["id"]
    token = tracker["ingest_token"]
    assert status(client, alice, d, True)["tracking_paused"]

    headers = {"Authorization": "Bearer "+token}
    assert location(client, alice, d).status_code == 409
    assert client.post(f"/api/ingest/{d}", headers=headers,
                       json={"latitude": 35, "longitude": -83}).status_code == 409
    owntracks = client.post(f"/api/ingest/owntracks/{d}",
                            auth=("owntracks", token),
                            json={"_type": "location", "lat": 35, "lon": -83,
                                  "tst": int(datetime.now(timezone.utc).timestamp())})
    assert owntracks.status_code == 409

    csv_data = "latitude,longitude,recorded_at\n35,-83,2026-10-01T10:00:00Z\n"
    assert client.post(f"/api/devices/{d}/import/csv",
                       headers={**alice, "Content-Type": "text/csv"},
                       content=csv_data).status_code == 409

    gpx = ('<gpx xmlns="http://www.topografix.com/GPX/1/1" version="1.1">'
           '<trk><trkseg><trkpt lat="35" lon="-83">'
           '<time>2026-10-01T10:00:00Z</time></trkpt></trkseg></trk></gpx>')
    assert client.post(f"/api/devices/{d}/import/gpx",
                       headers={**alice, "Content-Type": "application/gpx+xml"},
                       content=gpx).status_code == 409
    geojson = {
        "type": "FeatureCollection", "features": [{
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-83, 35]},
            "properties": {"recorded_at": "2026-10-01T10:00:00Z"}
        }]
    }
    assert client.post(f"/api/devices/{d}/import/geojson",
                       headers=alice, json=geojson).status_code == 409
    assert client.get("/api/summary", headers=alice).json()["points"] == 0
    assert client.get("/api/events", headers=alice).json() == []


def test_resume_rebaselines_fences_and_explicit_old_import_has_no_new_alerts(client):
    alice = auth(client)
    tracker = device(client, alice)
    d = tracker["id"]
    place = client.post("/api/places", headers=alice, json={
        "name": "Synthetic Home", "latitude": 35, "longitude": -83,
        "radius_m": 120
    })
    assert place.status_code == 201
    assert location(client, alice, d, lat=36, stamp="2026-10-01T10:00:00Z").json()["events"] == []
    assert location(client, alice, d, lat=35, stamp="2026-10-01T10:01:00Z").json()["events"] == [
        {"kind": "arrival", "place": "Synthetic Home"}
    ]
    status(client, alice, d, True)
    assert location(client, alice, d, lat=36).status_code == 409
    status(client, alice, d, False)
    # Explicit owner archive import is permitted AFTER resuming collection,
    # but old fixes must not masquerade as new geofence events.
    historic = "latitude,longitude,recorded_at,accuracy_m\n36,-83,2026-10-01T10:02:00Z,5\n"
    imported = client.post(
        f"/api/devices/{d}/import/csv",
        headers={**alice, "Content-Type": "text/csv"}, content=historic)
    assert imported.status_code == 201, imported.text
    assert imported.json()["imported"] == 1
    assert imported.json()["geofence_events"] == 0
    time.sleep(0.025)
    first = location(client, alice, d, lat=36)
    assert first.status_code == 201, first.text
    assert first.json()["events"] == []
    time.sleep(0.025)
    second = location(client, alice, d, lat=35)
    assert second.status_code == 201
    assert second.json()["events"] == [{"kind": "arrival", "place": "Synthetic Home"}]
    assert [x["kind"] for x in client.get("/api/events", headers=alice).json()] == [
        "arrival", "arrival"
    ]


def test_legacy_sqlite_device_table_migrates_in_place(tmp_path):
    path = tmp_path / "private" / "legacy.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    old_conn = sqlite3.connect(path)
    old_conn.execute(
        """CREATE TABLE devices (
            id INTEGER PRIMARY KEY, account_id INTEGER NOT NULL,
            name TEXT NOT NULL, kind TEXT NOT NULL,
            ingest_token_hash TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL
        )"""
    )
    old_conn.execute(
        """INSERT INTO devices(id,account_id,name,kind,ingest_token_hash,created_at)
           VALUES(12,1,'Existing Tracker','person','example_digest','2026-10-01T00:00:00Z')"""
    )
    old_conn.commit()
    old_conn.close()
    initialize(path)
    initialize(path)
    with connect(path) as db:
        d = db.execute("SELECT * FROM devices WHERE id=12").fetchone()
        assert d["name"] == "Existing Tracker"
        assert d["ingest_token_hash"] == "example_digest"
        assert d["tracking_paused"] == 0
        assert d["tracking_resumed_at"] is None
        assert db.execute("SELECT COUNT(*) FROM devices").fetchone()[0] == 1
