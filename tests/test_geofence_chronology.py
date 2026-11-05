"""A GPS timestamp must advance before a live geofence transition is accepted.

Exact-time conflicting coordinates may be retained in owner history, but must
not fabricate arrival or departure events. Older backfill is also historical.
"""
from test_api import auth, client, device


def report(client, headers, device_id, lat, timestamp, *, hardware=False):
    url = (f"/api/ingest/{device_id}" if hardware else "/api/locations")
    point = {
        "latitude": lat, "longitude": -83.0, "accuracy_m": 5,
        "recorded_at": timestamp,
    }
    if not hardware:
        point["device_id"] = device_id
    response = client.post(url, headers=headers, json=point)
    assert response.status_code == 201, response.text
    return response.json()


def add_home(client, headers):
    result = client.post("/api/places", headers=headers, json={
        "name": "Synthetic Home", "latitude": 35.0, "longitude": -83.0,
        "radius_m": 120,
    })
    assert result.status_code == 201, result.text


def test_equal_and_older_timestamps_cannot_generate_false_transitions(client):
    alice, bob = auth(client), auth(client, "bob")
    d = device(client, alice)
    add_home(client, alice)

    t0 = "2026-10-01T10:00:00+00:00"
    t1 = "2026-10-01T10:01:00+00:00"
    t2 = "2026-10-01T10:02:00+00:00"
    t3 = "2026-10-01T10:03:00+00:00"

    assert report(client, alice, d["id"], 36.0, t0)["events"] == []
    assert report(client, alice, d["id"], 35.0, t1)["events"] == [
        {"kind": "arrival", "place": "Synthetic Home"}
    ]
    # Conflicting coordinates at the same recorded instant are ambiguous.
    assert report(client, alice, d["id"], 36.0, t1)["events"] == []
    # Older backfill cannot rewrite the live state either.
    assert report(client, alice, d["id"], 36.0, "2026-09-30T09:00:00Z")["events"] == []
    assert report(client, alice, d["id"], 35.0, t2)["events"] == []
    assert report(client, alice, d["id"], 36.0, t3)["events"] == [
        {"kind": "departure", "place": "Synthetic Home"}
    ]

    events = client.get("/api/events", headers=alice)
    assert events.status_code == 200
    assert [x["kind"] for x in events.json()] == ["departure", "arrival"]
    assert client.get("/api/summary", headers=alice).json()["points"] == 6
    assert client.get("/api/locations", headers=bob).json() == []
    assert client.get("/api/events", headers=bob).json() == []


def test_device_token_ingest_uses_the_same_monotonic_guard(client):
    alice = auth(client)
    d = device(client, alice)
    add_home(client, alice)
    hardware = {"Authorization": "Bearer " + d["ingest_token"]}

    assert report(client, hardware, d["id"], 36.0,
                  "2026-10-02T10:00:00Z", hardware=True)["events"] == []
    assert report(client, hardware, d["id"], 35.0,
                  "2026-10-02T10:01:00Z", hardware=True)["events"][0]["kind"] == "arrival"
    assert report(client, hardware, d["id"], 36.0,
                  "2026-10-02T10:01:00Z", hardware=True)["events"] == []
    assert report(client, hardware, d["id"], 35.0,
                  "2026-10-02T10:02:00Z", hardware=True)["events"] == []
    assert report(client, hardware, d["id"], 36.0,
                  "2026-10-02T10:03:00Z", hardware=True)["events"][0]["kind"] == "departure"
    assert len(client.get("/api/events", headers=alice).json()) == 2
    assert client.get("/api/events", headers=hardware).status_code == 401


def test_csv_equal_time_backfill_is_historical_not_a_live_transition(client):
    alice = auth(client)
    d = device(client, alice)
    add_home(client, alice)
    raw = (
        "latitude,longitude,recorded_at,accuracy_m\n"
        "36,-83,2026-10-01T10:00:00Z,5\n"
        "35,-83,2026-10-01T10:01:00Z,5\n"
        "36,-83,2026-10-01T10:01:00Z,5\n"
    )
    result = client.post(
        f"/api/devices/{d['id']}/import/csv", headers={
            **alice, "Content-Type": "text/csv"
        }, content=raw.encode("utf-8")
    )
    assert result.status_code == 201, result.text
    assert result.json()["imported"] == 3
    assert result.json()["geofence_events"] == 1
    assert [x["kind"] for x in client.get("/api/events", headers=alice).json()] == ["arrival"]
    assert report(client, alice, d["id"], 35.0,
                  "2026-10-01T10:02:00Z")["events"] == []
    assert report(client, alice, d["id"], 36.0,
                  "2026-10-01T10:03:00Z")["events"][0]["kind"] == "departure"
