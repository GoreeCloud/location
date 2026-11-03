"""Manual account-scoped retention previews, confirmation and safeguards."""
from __future__ import annotations

from test_api import auth, client, device


def point(client, headers, device_id, lat, lon, timestamp):
    result = client.post("/api/locations", headers=headers, json={
        "device_id": device_id, "latitude": lat, "longitude": lon,
        "accuracy_m": 5, "recorded_at": timestamp,
    })
    assert result.status_code == 201, result.text
    return result.json()


def test_retention_preview_purge_and_account_isolation(client):
    alice, bob = auth(client), auth(client, "bob")
    a = device(client, alice)
    b = device(client, bob)
    created = client.post("/api/places", headers=alice, json={
        "name": "Sample place", "latitude": 40, "longitude": -80,
        "radius_m": 150,
    })
    assert created.status_code == 201
    point(client, alice, a["id"], 41, -80, "2026-01-01T10:00:00+00:00")
    arrival = point(client, alice, a["id"], 40, -80, "2026-01-02T10:00:00+00:00")
    assert arrival["events"] == [{"kind": "arrival", "place": "Sample place"}]
    point(client, alice, a["id"], 40, -80, "2026-11-02T10:00:00+00:00")
    point(client, bob, b["id"], 20, 30, "2026-01-01T10:00:00+00:00")

    preview = client.get("/api/retention/preview", headers=alice,
                         params={"older_than_days": 30})
    assert preview.status_code == 200
    candidate = preview.json()
    assert candidate["eligible_points"] == 2
    assert candidate["eligible_events"] == 1
    assert candidate["affected_devices"] == 1
    assert client.get("/api/retention/preview", headers=bob,
                      params={"older_than_days": 30}).json()["eligible_points"] == 1
    assert client.get("/api/summary", headers=alice).json()["points"] == 3

    valid = {
        "older_than_days": 30, "expected_points": 2,
        "expected_events": 1, "confirmation": "DELETE_OLD_HISTORY"
    }
    assert client.post("/api/retention/purge", headers=bob,
                       json={"older_than_days": 30, "expected_points": 2,
                             "expected_events": 1,
                             "confirmation": "DELETE_OLD_HISTORY"}).status_code == 409
    assert client.post("/api/retention/purge", headers=alice,
                       json={**valid, "confirmation": "no"}).status_code == 422
    assert client.get("/api/summary", headers=alice).json()["points"] == 3

    erased = client.post("/api/retention/purge", headers=alice, json=valid)
    assert erased.status_code == 200
    assert erased.json()["deleted_points"] == 2
    assert erased.json()["deleted_events"] == 1
    assert erased.json()["reset_devices"] == 1
    assert client.get("/api/summary", headers=alice).json()["points"] == 1
    assert client.get("/api/summary", headers=bob).json()["points"] == 1
    assert client.get("/api/events", headers=alice).json() == []
    assert len(client.get("/api/devices", headers=alice).json()) == 1
    assert client.get("/api/locations", headers=alice).json()[0]["recorded_at"].startswith("2026-11-02")

    # A fresh GPS fix initializes state; no spurious arrival using deleted history.
    new = point(client, alice, a["id"], 40, -80, "2026-11-03T03:00:00+00:00")
    assert new["events"] == []


def test_retention_rejects_stale_previews_and_invalid_inputs(client):
    alice = auth(client)
    d = device(client, alice)
    assert client.get("/api/retention/preview",
                      params={"older_than_days": 30}).status_code == 401
    assert client.get("/api/retention/preview", headers=alice,
                      params={"older_than_days": 0}).status_code == 422
    assert client.get("/api/retention/preview", headers=alice).status_code == 422
    assert client.post("/api/retention/purge", json={
        "older_than_days": 30, "expected_points": 0,
        "expected_events": 0, "confirmation": "DELETE_OLD_HISTORY"
    }).status_code == 401

    point(client, alice, d["id"], 10, 20, "2026-01-01T10:00:00+00:00")
    old = client.get("/api/retention/preview", headers=alice,
                     params={"older_than_days": 30}).json()
    assert old["eligible_points"] == 1
    point(client, alice, d["id"], 11, 20, "2026-01-02T10:00:00+00:00")
    outdated = client.post("/api/retention/purge", headers=alice, json={
        "older_than_days": 30, "expected_points": 1,
        "expected_events": 0, "confirmation": "DELETE_OLD_HISTORY"
    })
    assert outdated.status_code == 409
    assert len(client.get("/api/locations", headers=alice).json()) == 2

    fresh = client.get("/api/retention/preview", headers=alice,
                       params={"older_than_days": 30}).json()
    result = client.post("/api/retention/purge", headers=alice, json={
        "older_than_days": 30, "expected_points": fresh["eligible_points"],
        "expected_events": fresh["eligible_events"],
        "confirmation": "DELETE_OLD_HISTORY"
    })
    assert result.status_code == 200
    assert result.json()["deleted_points"] == 2
    assert client.get("/api/retention/preview", headers=alice,
                      params={"older_than_days": 30}).json()["eligible_points"] == 0
