"""Concurrent device and owner ingestion must serialize geofence decisions.

Each request uses a distinct SQLite connection. The writer lock must be taken
before inspecting the newest recorded location, rather than after that read.
"""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from test_api import auth, client, device


def test_simultaneous_owner_and_device_uploads_emit_one_transition(client):
    owner = auth(client)
    registered = device(client, owner)
    created = client.post("/api/places", headers=owner, json={
        "name": "Synthetic home", "latitude": 35.0, "longitude": -83.0,
        "radius_m": 120,
    })
    assert created.status_code == 201

    def submit(lat, stamp, *, hardware=False):
        endpoint = (f"/api/ingest/{registered['id']}"
                    if hardware else "/api/locations")
        headers = ({"Authorization": "Bearer " + registered["ingest_token"]}
                   if hardware else owner)
        payload = {"latitude": lat, "longitude": -83.0,
                   "accuracy_m": 5, "recorded_at": stamp}
        if not hardware:
            payload["device_id"] = registered["id"]
        return client.post(endpoint, headers=headers, json=payload)

    first = submit(36.0, "2026-10-01T10:00:00Z")
    assert first.status_code == 201
    assert first.json()["events"] == []

    def batch(lat, stamp, workers=12):
        barrier = Barrier(workers)

        def work(index):
            barrier.wait(timeout=10)
            return submit(lat, stamp, hardware=bool(index % 2))

        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(work, range(workers)))
        assert all(r.status_code == 201 for r in results), [
            (r.status_code, r.text[:120]) for r in results if r.status_code != 201
        ]
        return results

    arrivals = batch(35.0, "2026-10-01T10:01:00Z")
    assert sum(len(r.json()["events"]) for r in arrivals) == 1
    assert [x["kind"] for x in client.get("/api/events", headers=owner).json()] == [
        "arrival"
    ]

    departures = batch(36.0, "2026-10-01T10:02:00Z")
    assert sum(len(r.json()["events"]) for r in departures) == 1
    assert [x["kind"] for x in client.get("/api/events", headers=owner).json()] == [
        "departure", "arrival"
    ]
    assert client.get("/api/summary", headers=owner).json()["points"] == 25
    assert client.get("/api/events").status_code == 401
