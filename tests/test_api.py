from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree

from fastapi.testclient import TestClient
import pytest

from goreecloud_location.main import create_app
from goreecloud_location.store import create_account


@pytest.fixture()
def client(tmp_path: Path):
    path = tmp_path / "private" / "location.db"
    app = create_app(path)
    create_account(path, "alice", "this is a very strong first password")
    create_account(path, "bob", "this is a separate strong password")
    with TestClient(app) as c:
        yield c


def auth(client, username="alice", password=None):
    password = password or ("this is a very strong first password" if username == "alice"
                            else "this is a separate strong password")
    result = client.post("/api/auth/login", json={"username": username, "password": password})
    assert result.status_code == 200
    return {"Authorization": f"Bearer {result.json()['access_token']}"}


def device(client, headers):
    result = client.post("/api/devices", json={"name": "Phone", "kind": "person"}, headers=headers)
    assert result.status_code == 201
    return result.json()


def test_private_by_default(client):
    for url in ("/api/me", "/api/devices", "/api/locations", "/api/places",
                "/api/events", "/api/summary", "/api/export/geojson?device_id=1"):
        assert client.get(url).status_code == 401
    assert client.post("/api/locations", json={"device_id": 1, "latitude": 0,
                                                "longitude": 0}).status_code == 401
    assert client.get("/api/health").json()["status"] == "ok"
    assert client.get("/api/config").json()["tile_template"] == ""


def test_location_creation_and_export(client):
    alice = auth(client)
    d = device(client, alice)
    assert "ingest_token" in d
    assert "ingest_token" not in str(client.get("/api/devices", headers=alice).json())
    point = {"latitude": 35.95, "longitude": -83.92, "accuracy_m": 7.5,
             "battery_percent": 87, "device_id": d["id"]}
    response = client.post("/api/locations", headers=alice, json=point)
    assert response.status_code == 201
    assert client.get("/api/summary", headers=alice).json()["points"] == 1
    result = client.get("/api/locations", headers=alice).json()
    assert result[0]["device_name"] == "Phone"
    export = client.get(f"/api/export/geojson?device_id={d['id']}", headers=alice)
    assert export.status_code == 200
    assert export.json()["features"][0]["geometry"]["coordinates"] == [-83.92, 35.95]
    gpx = client.get(f"/api/export/gpx?device_id={d['id']}", headers=alice)
    assert gpx.status_code == 200
    assert ElementTree.fromstring(gpx.content).tag.endswith("gpx")
    assert gpx.headers["cache-control"] == "no-store"


def test_cross_account_isolation(client):
    alice, bob = auth(client, "alice"), auth(client, "bob")
    d = device(client, alice)
    other = client.get("/api/devices", headers=bob)
    assert other.json() == []
    assert client.post("/api/locations", headers=bob, json={"device_id": d["id"],
            "latitude": 1, "longitude": 1}).status_code == 404
    assert client.get(f"/api/export/geojson?device_id={d['id']}", headers=bob).status_code == 404
    assert client.delete(f"/api/devices/{d['id']}", headers=bob).status_code == 404
    assert client.post(f"/api/ingest/{d['id']}", json={"latitude": 1,"longitude": 1},
                       headers=bob).status_code == 401


def test_dedicated_device_token(client):
    alice = auth(client)
    d = device(client, alice)
    headers = {"Authorization": f"Bearer {d['ingest_token']}"}
    assert client.post(f"/api/ingest/{d['id']}",
                       json={"latitude": 40, "longitude": -78, "accuracy_m": 3},
                       headers=headers).status_code == 201
    assert client.get("/api/locations", headers=headers).status_code == 401
    assert len(client.get("/api/locations", headers=alice).json()) == 1


def test_validation_and_geofence_events(client):
    alice = auth(client)
    d = device(client, alice)
    place = client.post("/api/places", headers=alice,
                        json={"name": "Home", "latitude": 35.0,
                              "longitude": -83.0, "radius_m": 100}).json()
    def report(lat, lon):
        return client.post("/api/locations", headers=alice,
                           json={"device_id": d["id"], "latitude": lat,
                                 "longitude": lon, "accuracy_m": 5})
    assert report(36, -83).json()["events"] == []
    events = report(35, -83).json()["events"]
    assert events == [{"kind": "arrival", "place": "Home"}]
    assert report(35, -83).json()["events"] == []
    assert report(36, -83).json()["events"] == [{"kind": "departure", "place": "Home"}]
    assert len(client.get("/api/events", headers=alice).json()) == 2
    assert client.post("/api/locations", headers=alice,
                       json={"device_id": d["id"], "latitude": 200,
                             "longitude": 0}).status_code == 422
    assert client.post("/api/locations", headers=alice,
                       json={"device_id": d["id"], "latitude": 0,
                             "longitude": 0, "unexpected": 1}).status_code == 422
    assert client.delete(f"/api/places/{place['id']}", headers=alice).status_code == 204
    assert client.get("/api/events", headers=alice).json() == []


def test_logout_revokes_session(client):
    alice = auth(client)
    assert client.post("/api/auth/logout", headers=alice).status_code == 204
    assert client.get("/api/me", headers=alice).status_code == 401


def test_login_rate_limiting(client):
    for i in range(5):
        assert client.post("/api/auth/login",
                           json={"username": "alice", "password": "incorrect"}).status_code == 401
    assert client.post("/api/auth/login",
                       json={"username": "alice", "password": "incorrect"}).status_code == 429


def test_static_security_headers(client):
    result = client.get("/")
    assert result.status_code == 200
    assert result.headers["x-frame-options"] == "DENY"
    assert result.headers["content-security-policy"].startswith("default-src 'self'")
