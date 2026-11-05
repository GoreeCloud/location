"""GeoJSON FeatureCollection imports are bounded, private and atomic."""
from datetime import datetime, timedelta, timezone
import json

from test_api import auth, client, device


def feature(lon, lat, stamp="2026-10-01T10:00:00Z", **properties):
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": {"recorded_at": stamp, **properties},
    }


def collection(*items):
    return json.dumps({"type": "FeatureCollection", "features": list(items)})


def upload(client, headers, did, content, content_type="application/geo+json"):
    return client.post(
        f"/api/devices/{did}/import/geojson",
        headers={**headers, "Content-Type": content_type},
        content=content,
    )


def test_geojson_import_is_private_sorted_and_idempotent(client):
    alice, bob = auth(client), auth(client, "bob")
    d = device(client, alice)
    assert client.post("/api/places", headers=alice, json={
        "name": "Synthetic Place", "latitude": 35, "longitude": -83,
        "radius_m": 120,
    }).status_code == 201
    data = collection(
        feature(-83, 35, "2026-10-01T10:01:00Z", accuracy_m=5),
        feature(-83, 36, "2026-10-01T10:00:00Z", accuracy_m=5),
        feature(-83, 35, "2026-10-01T10:01:00Z", accuracy_m=5),
    )
    assert upload(client, {}, d["id"], data).status_code == 401
    assert upload(client, bob, d["id"], data).status_code == 404
    result = upload(client, alice, d["id"], data)
    assert result.status_code == 201, result.text
    assert result.json() == {
        "device_id": d["id"], "imported": 2,
        "skipped_duplicates": 1, "geofence_events": 1,
    }
    assert [x["kind"] for x in client.get("/api/events", headers=alice).json()] == ["arrival"]
    assert client.get("/api/locations", headers=bob).json() == []
    assert client.get("/api/events", headers=bob).json() == []
    again = upload(client, alice, d["id"], data)
    assert again.status_code == 201 and again.json()["imported"] == 0
    assert again.json()["skipped_duplicates"] == 3
    assert client.get("/api/summary", headers=alice).json()["points"] == 2


def test_geojson_export_import_roundtrip_preserves_known_fields(client):
    alice = auth(client)
    source, target = device(client, alice), device(client, alice)
    for i in range(2):
        r = client.post("/api/locations", headers=alice, json={
            "device_id": source["id"], "latitude": 35 + i, "longitude": -83,
            "accuracy_m": 7.5, "altitude_m": 125, "speed_mps": 8,
            "recorded_at": f"2026-10-01T10:0{i}:00Z",
        })
        assert r.status_code == 201
    exported = client.get("/api/export/geojson", headers=alice,
                          params={"device_id": source["id"]})
    assert exported.status_code == 200
    imported = upload(client, alice, target["id"], exported.content)
    assert imported.status_code == 201, imported.text
    assert imported.json()["imported"] == 2
    points = client.get("/api/locations", headers=alice,
                        params={"device_id": target["id"]}).json()
    assert len(points) == 2
    assert {p["altitude_m"] for p in points} == {125}
    assert {p["accuracy_m"] for p in points} == {7.5}
    assert {p["speed_mps"] for p in points} == {8.0}


def test_geojson_point_third_coordinate_is_altitude(client):
    alice = auth(client)
    d = device(client, alice)
    f = feature(-83, 35)
    f["geometry"]["coordinates"] = [-83, 35, 222]
    result = upload(client, alice, d["id"], collection(f))
    assert result.status_code == 201
    assert client.get("/api/locations", headers=alice).json()[0]["altitude_m"] == 222


def test_geojson_rejects_malformed_points_before_any_write(client):
    alice = auth(client)
    d = device(client, alice)
    valid = feature(-83, 35)
    variants = []
    invalid_point = feature(-83, 36, "2026-10-01T10:01:00Z")
    invalid_point["geometry"]["type"] = "Polygon"
    variants.append(invalid_point)
    invalid_point = feature(-83, 36, "2026-10-01T10:01:00Z")
    invalid_point["geometry"]["coordinates"] = [-83, 200]
    variants.append(invalid_point)
    invalid_point = feature(-83, 36, "2026-10-01T10:01:00Z")
    del invalid_point["properties"]["recorded_at"]
    variants.append(invalid_point)
    variants.append(feature(-83, 36, "2026-10-01T10:01:00"))
    variants.append(feature(-83, 36,
                            (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()))
    invalid_point = feature(-83, 36, "2026-10-01T10:01:00Z")
    invalid_point["geometry"]["coordinates"] = [True, 36]
    variants.append(invalid_point)
    for bad in variants:
        result = upload(client, alice, d["id"], collection(valid, bad))
        assert result.status_code == 422, result.text
        assert client.get("/api/summary", headers=alice).json()["points"] == 0


def test_geojson_bad_content_type_structure_and_nonfinite_numbers(client):
    alice = auth(client)
    d = device(client, alice)
    good = collection(feature(-83, 35))
    assert upload(client, alice, d["id"], good, "text/plain").status_code == 415
    for bad in ("{not JSON", "[]", '{"type":"FeatureCollection","features":{}}',
                '{"type":"FeatureCollection","features":[]}',
                '{"type":"FeatureCollection","features":[{"type":"Feature",'
                '"geometry":{"type":"Point","coordinates":[NaN,35]},'
                '"properties":{"recorded_at":"2026-10-01T10:00:00Z"}}]}'):
        result = upload(client, alice, d["id"], bad)
        assert result.status_code == 422, result.text
    assert client.get("/api/summary", headers=alice).json()["points"] == 0


def test_geojson_limit_and_duplicate_privacy_semantics(client):
    alice = auth(client)
    d = device(client, alice)
    oversized = collection(feature(-83, 35, note="x" * 2_100_000))
    assert upload(client, alice, d["id"], oversized).status_code == 413
    too_many = collection(*[feature(-83, 35) for _ in range(5001)])
    assert upload(client, alice, d["id"], too_many).status_code == 413
    # Arbitrary identity/URL-like properties are never stored as point fields.
    private = collection(feature(-83, 35,
                                 name="Synthetic private display name",
                                 link="https://untrusted.invalid",
                                 SSID="private-wifi"))
    assert upload(client, alice, d["id"], private).status_code == 201
    point = client.get("/api/locations", headers=alice).json()[0]
    assert "name" not in point and "link" not in point and "SSID" not in point
