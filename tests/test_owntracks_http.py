"""OwnTracks native HTTP tracking uses private device-scoped Basic auth."""
from datetime import datetime, timedelta, timezone
import json

import pytest

from test_api import auth, client, device


def epoch(minute=0):
    return int(datetime(2026, 10, 1, 12, minute, tzinfo=timezone.utc).timestamp())


def post_owntracks(client, registered, payload, *, username="owntracks", token=None):
    return client.post(
        f"/api/ingest/owntracks/{registered['id']}",
        auth=(username, registered["ingest_token"] if token is None else token),
        json=payload,
    )


def test_owntracks_http_maps_fields_and_preserves_private_owner_history(client):
    alice, bob = auth(client), auth(client, "bob")
    tracker = device(client, alice)
    place = client.post("/api/places", headers=alice, json={
        "name": "Synthetic home", "latitude": 35, "longitude": -83,
        "radius_m": 150,
    })
    assert place.status_code == 201

    base = {
        "_type": "location", "lat": 36.0, "lon": -83.0,
        "tst": epoch(), "acc": 5, "alt": 130,
        "vel": 36, "cog": 90, "batt": 82,
        "topic": "owntracks/local/phone", "tid": "p1",
        "conn": "w", "SSID": "synthetic-private-wifi",
        "BSSID": "00:00:00:00:00:00",
    }
    posted = post_owntracks(client, tracker, base)
    assert posted.status_code == 200, posted.text
    assert posted.json() == []
    points = client.get("/api/locations", headers=alice).json()
    assert len(points) == 1
    assert points[0]["latitude"] == 36.0
    assert points[0]["speed_mps"] == pytest.approx(10)
    assert points[0]["altitude_m"] == 130
    assert points[0]["heading_deg"] == 90
    assert points[0]["battery_percent"] == 82
    assert points[0]["recorded_at"].startswith("2026-10-01T12:00:00")
    # Arbitrary OwnTracks metadata must not be copied to the point schema.
    assert "SSID" not in points[0] and "topic" not in points[0]

    arrival = post_owntracks(client, tracker, {
        **base, "lat": 35.0, "tst": epoch(1),
    })
    assert arrival.status_code == 200 and arrival.json() == []
    events = client.get("/api/events", headers=alice).json()
    assert len(events) == 1 and events[0]["kind"] == "arrival"

    # Old backfill or a conflicting equal-time point may be stored but must
    # not fabricate a new transition.
    assert post_owntracks(client, tracker, {
        **base, "lat": 36.0, "tst": epoch(1),
    }).json() == []
    assert len(client.get("/api/events", headers=alice).json()) == 1
    assert len(client.get("/api/locations", headers=bob).json()) == 0
    assert len(client.get("/api/events", headers=bob).json()) == 0


def test_owntracks_basic_credentials_are_write_only_and_can_be_rotated(client):
    alice, bob = auth(client), auth(client, "bob")
    tracker = device(client, alice)
    other = device(client, bob)
    payload = {"_type": "location", "lat": 25.0, "lon": 10.0, "tst": epoch()}
    url = f"/api/ingest/owntracks/{tracker['id']}"

    assert client.post(url, json=payload).status_code == 401
    assert client.post(url, json=payload, headers=alice).status_code == 401
    assert post_owntracks(client, tracker, payload, token="wrong-key").status_code == 401
    assert post_owntracks(client, tracker, payload, username="alice").status_code == 401
    assert post_owntracks(client, tracker, payload,
                          token=other["ingest_token"]).status_code == 401
    assert client.get("/api/locations",
                      auth=("owntracks", tracker["ingest_token"])).status_code == 401

    assert post_owntracks(client, tracker, payload).status_code == 200
    rotated = client.post(
        f"/api/devices/{tracker['id']}/rotate-token", headers=alice
    )
    assert rotated.status_code == 200
    new_key = rotated.json()["ingest_token"]
    assert post_owntracks(client, tracker, payload).status_code == 401
    assert post_owntracks(client, tracker, payload, token=new_key).status_code == 200
    assert client.get("/api/summary", headers=alice).json()["points"] == 2
    assert client.get("/api/summary", headers=bob).json()["points"] == 0


def test_owntracks_http_housekeeping_is_acknowledged_without_writes(client):
    alice = auth(client)
    tracker = device(client, alice)
    url = f"/api/ingest/owntracks/{tracker['id']}"
    credentials = ("owntracks", tracker["ingest_token"])
    empty = client.post(url, content=b"", auth=credentials)
    assert empty.status_code == 200 and empty.json() == []

    for kind in ("lwt", "status", "transition", "waypoint", "card"):
        event = client.post(url, auth=credentials, json={
            "_type": kind, "lat": 33, "lon": -10, "tst": epoch(),
            "event": "enter", "desc": "untrusted place",
        })
        assert event.status_code == 200 and event.json() == []
    assert client.get("/api/summary", headers=alice).json()["points"] == 0
    assert client.get("/api/events", headers=alice).json() == []


@pytest.mark.parametrize("payload", [
    {"_type": "location", "lat": 91, "lon": 0, "tst": epoch()},
    {"_type": "location", "lat": 0, "lon": -181, "tst": epoch()},
    {"_type": "location", "lat": 0, "lon": 0, "tst": -1},
    {"_type": "location", "lat": 0, "lon": 0, "tst": "invalid"},
    {"_type": "location", "lat": 0, "lon": 0, "tst": 2.5},
    {"_type": "location", "lat": 0, "lon": 0, "tst": epoch(), "acc": -2},
    {"_type": "location", "lat": 0, "lon": 0, "tst": epoch(), "batt": 111},
    {"_type": "location", "lat": 0, "lon": 0, "tst": epoch(), "vel": 5000},
    {"_type": "location", "lat": 0, "lon": 0, "tst": epoch(), "cog": 400},
    {"_type": "location", "lat": 0, "lon": 0,
     "tst": int((datetime.now(timezone.utc) + timedelta(hours=2)).timestamp())},
    {"_type": "encrypted", "data": "opaque"},
    {"_type": [], "lat": 0, "lon": 0, "tst": epoch()},
    [],
])
def test_owntracks_rejects_invalid_or_unsupported_payload(client, payload):
    alice = auth(client)
    tracker = device(client, alice)
    result = post_owntracks(client, tracker, payload)
    assert result.status_code == 422, result.text
    assert client.get("/api/summary", headers=alice).json()["points"] == 0


def test_owntracks_rejects_non_json_huge_or_malformed_body(client):
    alice = auth(client)
    tracker = device(client, alice)
    url = f"/api/ingest/owntracks/{tracker['id']}"
    credentials = ("owntracks", tracker["ingest_token"])

    html = client.post(url, auth=credentials, content=b"<hello>",
                       headers={"Content-Type": "text/plain"})
    assert html.status_code == 415
    invalid = client.post(url, auth=credentials, content=b"{not JSON",
                          headers={"Content-Type": "application/json"})
    assert invalid.status_code == 422
    bad_float = client.post(url, auth=credentials, content=(
        '{"_type":"location","lat":NaN,"lon":0,"tst":1760000000}'
    ), headers={"Content-Type": "application/json"})
    assert bad_float.status_code == 422
    oversized = client.post(url, auth=credentials,
                            content=json.dumps({"_type":"location", "extra":"X"*17000}),
                            headers={"Content-Type": "application/json"})
    assert oversized.status_code == 413
    assert client.get("/api/summary", headers=alice).json()["points"] == 0
