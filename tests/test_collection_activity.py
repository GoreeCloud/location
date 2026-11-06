"""Collection-setting activity is private, bounded and intentionally metadata-minimal."""
from datetime import datetime
from test_api import auth, client, device
from goreecloud_location.store import initialize, connect


def change(client, owner, device_id, paused):
    result = client.put(f"/api/devices/{device_id}/collection",
                        headers=owner, json={"paused": paused})
    assert result.status_code == 200, result.text
    return result.json()


def activity(client, owner, *, device_id=None, limit=None):
    params = {}
    if device_id is not None:
        params["device_id"] = device_id
    if limit is not None:
        params["limit"] = limit
    return client.get("/api/privacy/collection-activity",
                      headers=owner, params=params)


def test_collection_activity_records_real_changes_only_without_gps_fields(client):
    alice = auth(client)
    tracker = device(client, alice)
    did = tracker["id"]
    assert activity(client, alice).json() == []

    change(client, alice, did, True)
    change(client, alice, did, True)
    change(client, alice, did, False)
    change(client, alice, did, False)
    entries = activity(client, alice).json()
    assert len(entries) == 2
    assert [x["action"] for x in entries] == ["resumed", "paused"]
    for x in entries:
        assert set(x) == {"id", "device_id", "device_name", "action", "changed_at"}
        assert x["device_id"] == did
        assert x["device_name"] == tracker["name"]
        assert datetime.fromisoformat(x["changed_at"]).tzinfo is not None
        assert "latitude" not in x and "longitude" not in x
        assert "ingest_token" not in x and "ip" not in x
    assert entries[0]["id"] > entries[1]["id"]
    assert activity(client, alice, device_id=did, limit=1).json() == entries[:1]


def test_collection_activity_owner_isolation_and_device_key_denial(client):
    alice = auth(client)
    bob = auth(client, "bob")
    owned = device(client, alice)
    other = device(client, bob)
    change(client, alice, owned["id"], True)
    change(client, bob, other["id"], True)

    assert activity(client, alice).json()[0]["device_id"] == owned["id"]
    assert activity(client, bob).json()[0]["device_id"] == other["id"]
    assert activity(client, alice, device_id=other["id"]).status_code == 404
    assert activity(client, bob, device_id=owned["id"]).status_code == 404
    assert client.get("/api/privacy/collection-activity").status_code == 401
    assert client.get("/api/privacy/collection-activity", headers={
        "Authorization": "Bearer " + owned["ingest_token"]
    }).status_code == 401
    for bad in ("0", "101", "-1"):
        assert activity(client, alice, limit=bad).status_code == 422


def test_collection_activity_lifecycle_on_history_erasure_and_device_removal(client):
    alice = auth(client)
    tracker = device(client, alice)
    did = tracker["id"]
    change(client, alice, did, True)
    assert client.delete(f"/api/devices/{did}/history",
                         headers=alice).status_code == 204
    assert len(activity(client, alice).json()) == 1
    assert client.delete(f"/api/devices/{did}", headers=alice).status_code == 204
    assert activity(client, alice).json() == []
    assert activity(client, alice, device_id=did).status_code == 404


def test_collection_activity_keeps_only_last_hundred_events_per_device(client):
    alice = auth(client)
    first = device(client, alice)
    second = device(client, alice)
    did = first["id"]
    change(client, alice, second["id"], True)
    for i in range(106):
        change(client, alice, did, paused=(i % 2 == 0))
    rows = activity(client, alice, device_id=did, limit=100).json()
    assert len(rows) == 100
    assert rows[0]["action"] == "resumed"
    assert rows[-1]["action"] == "paused"
    assert all(x["device_id"] == did for x in rows)
    assert len(activity(client, alice).json()) == 50
    assert len(activity(client, alice, device_id=second["id"]).json()) == 1


def test_collection_activity_schema_is_additive_and_reentrant(tmp_path):
    db_path = tmp_path / "private-location" / "location.db"
    initialize(db_path)
    initialize(db_path)
    with connect(db_path) as db:
        rows = db.execute("PRAGMA table_info(collection_activity)").fetchall()
        assert {row["name"] for row in rows} == {
            "id", "device_id", "action", "changed_at"
        }
        assert db.execute("SELECT COUNT(*) FROM collection_activity").fetchone()[0] == 0
