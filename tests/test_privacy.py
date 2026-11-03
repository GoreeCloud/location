"""Owner-only history erasure and geofence privacy consistency."""
from __future__ import annotations

from test_api import auth, client, device


def upload(client, headers, device_id, lat, lon, timestamp):
    result = client.post("/api/locations", headers=headers, json={
        "device_id": device_id, "latitude": lat, "longitude": lon,
        "accuracy_m": 3, "recorded_at": timestamp,
    })
    assert result.status_code == 201, result.text
    return result.json()


def test_erase_device_history_keeps_credentials_but_resets_events(client):
    alice = auth(client)
    bob = auth(client, "bob")
    d1 = device(client, alice)
    d2 = device(client, alice)
    place = client.post("/api/places", headers=alice, json={
        "name": "Private home", "latitude": 10, "longitude": 10, "radius_m": 200,
    })
    assert place.status_code == 201
    upload(client, alice, d1["id"], 12, 12, "2026-11-01T12:00:00+00:00")
    inside = upload(client, alice, d1["id"], 10, 10, "2026-11-01T12:01:00+00:00")
    assert inside["events"] == [{"kind": "arrival", "place": "Private home"}]
    upload(client, alice, d2["id"], 20, 20, "2026-11-01T12:02:00+00:00")
    assert len(client.get("/api/events", headers=alice).json()) == 1
    endpoint = f"/api/devices/{d1['id']}/history"
    assert client.delete(endpoint, headers=bob).status_code == 404
    assert client.delete(endpoint).status_code == 401
    assert client.delete(endpoint, headers=alice).status_code == 204
    assert client.get("/api/events", headers=alice).json() == []
    assert client.get("/api/locations", headers=alice,
                      params={"device_id": d1["id"]}).json() == []
    assert client.get("/api/summary", headers=alice).json()["points"] == 1
    registered = client.get("/api/devices", headers=alice).json()
    assert {d["id"] for d in registered} == {d1["id"], d2["id"]}

    # Upload key is still valid and the first new point initializes state,
    # rather than spuriously generating arrival from erased prior position.
    key = {"Authorization": "Bearer " + d1["ingest_token"]}
    reply = client.post(f"/api/ingest/{d1['id']}", headers=key, json={
        "latitude": 10, "longitude": 10, "accuracy_m": 3,
        "recorded_at": "2026-11-01T12:03:00+00:00"
    })
    assert reply.status_code == 201
    assert reply.json()["events"] == []


def test_single_point_deletion_cleans_related_event_and_resets_fence(client):
    alice, bob = auth(client), auth(client, "bob")
    d = device(client, alice)
    place = client.post("/api/places", headers=alice, json={
        "name": "Test region", "latitude": 40, "longitude": -76, "radius_m": 100
    })
    assert place.status_code == 201
    outside = upload(client, alice, d["id"], 41, -76, "2026-11-01T15:00:00+00:00")
    arrival = upload(client, alice, d["id"], 40, -76, "2026-11-01T15:01:00+00:00")
    assert arrival["events"] == [{"kind": "arrival", "place": "Test region"}]
    endpoint = f"/api/locations/{arrival['id']}"
    assert client.delete(endpoint, headers=bob).status_code == 404
    assert client.delete(endpoint, headers=alice).status_code == 204
    assert client.get("/api/events", headers=alice).json() == []
    remaining = client.get("/api/locations", headers=alice).json()
    assert [p["id"] for p in remaining] == [outside["id"]]
    assert client.delete(endpoint, headers=alice).status_code == 404
    # Reset fence state so next position initializes rather than emitting a
    # transition based on a point that no longer exists.
    new_position = upload(client, alice, d["id"], 40, -76, "2026-11-01T15:02:00+00:00")
    assert new_position["events"] == []
    assert client.get("/api/events", headers=bob).json() == []
