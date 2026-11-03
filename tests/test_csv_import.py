"""CSV import validation, deduplication and access boundaries."""
from test_api import auth, client, device


def upload(client, headers, device_id, content):
    return client.post(
        f"/api/devices/{device_id}/import/csv",
        data=content.encode("utf-8"),
        headers={**headers, "Content-Type": "text/csv"},
    )


def test_csv_import_idempotent_and_owner_restricted(client):
    alice = auth(client)
    bob = auth(client, "bob")
    registered = device(client, alice)
    data = (
        "latitude,longitude,recorded_at,accuracy_m\n"
        "35.2,-83.1,2026-11-01T10:00:00+00:00,4\n"
        "35.3,-83.2,2026-11-01T11:00:00+00:00,7\n"
        "35.2,-83.1,2026-11-01T10:00:00+00:00,4\n"
    )
    assert upload(client, bob, registered["id"], data).status_code == 404
    assert upload(client, {}, registered["id"], data).status_code == 401
    first = upload(client, alice, registered["id"], data)
    assert first.status_code == 201, first.text
    assert first.json()["imported"] == 2
    assert first.json()["skipped_duplicates"] == 1
    second = upload(client, alice, registered["id"], data)
    assert second.status_code == 201
    assert second.json()["imported"] == 0
    assert second.json()["skipped_duplicates"] == 3
    assert client.get("/api/summary", headers=alice).json()["points"] == 2
    assert client.get("/api/summary", headers=bob).json()["points"] == 0


def test_csv_import_is_atomic_on_bad_coordinates(client):
    alice = auth(client)
    registered = device(client, alice)
    invalid = (
        "latitude,longitude,recorded_at\n"
        "10,11,2026-11-01T00:00:00Z\n"
        "999,12,2026-11-01T00:00:01Z\n"
    )
    result = upload(client, alice, registered["id"], invalid)
    assert result.status_code == 422
    assert client.get("/api/summary", headers=alice).json()["points"] == 0
    missing_timezone = (
        "latitude,longitude,recorded_at\n"
        "10,11,2026-11-01T00:00:00\n"
    )
    assert upload(client, alice, registered["id"], missing_timezone).status_code == 422
    assert client.get("/api/summary", headers=alice).json()["points"] == 0
