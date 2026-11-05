"""GPX track import must be private, atomic and resistant to hostile XML."""
from datetime import datetime, timedelta, timezone

from test_api import auth, client, device


def gpx(*entries, version="1.1"):
    ns = "http://www.topografix.com/GPX/1/1" if version == "1.1" else "http://www.topografix.com/GPX/1/0"
    points = "".join(
        f'<trkpt lat="{lat}" lon="{lon}"><ele>125</ele><time>{time}</time></trkpt>'
        for lat, lon, time in entries
    )
    return (f'<gpx xmlns="{ns}" version="{version}" creator="Synthetic Test">'
            f'<trk><trkseg>{points}</trkseg></trk></gpx>')


def upload(client, headers, device_id, text, content_type="application/gpx+xml"):
    return client.post(
        f"/api/devices/{device_id}/import/gpx",
        headers={**headers, "Content-Type": content_type},
        content=text.encode("utf-8"),
    )


def test_gpx_import_is_sorted_idempotent_and_owner_scoped(client):
    alice, bob = auth(client), auth(client, "bob")
    d = device(client, alice)
    data = gpx(
        (35.0, -83.0, "2026-10-01T10:01:00Z"),
        (36.0, -83.0, "2026-10-01T10:00:00Z"),
        (35.0, -83.0, "2026-10-01T10:01:00Z"),
    )
    place = client.post("/api/places", headers=alice, json={
        "name": "Synthetic", "latitude": 35, "longitude": -83, "radius_m": 150,
    })
    assert place.status_code == 201

    assert upload(client, {}, d["id"], data).status_code == 401
    assert upload(client, bob, d["id"], data).status_code == 404
    first = upload(client, alice, d["id"], data)
    assert first.status_code == 201, first.text
    assert first.json() == {
        "device_id": d["id"], "imported": 2,
        "skipped_duplicates": 1, "geofence_events": 0,
    }
    assert client.get("/api/summary", headers=alice).json()["points"] == 2
    assert client.get("/api/summary", headers=bob).json()["points"] == 0
    # GPX track points contain no accuracy value; absent accuracy must not
    # invent a geofence arrival notification during historical import.
    assert client.get("/api/events", headers=alice).json() == []
    assert client.get("/api/events", headers=bob).json() == []

    repeated = upload(client, alice, d["id"], data)
    assert repeated.status_code == 201
    assert repeated.json()["imported"] == 0
    assert repeated.json()["skipped_duplicates"] == 3
    assert repeated.json()["geofence_events"] == 0
    assert client.get("/api/summary", headers=alice).json()["points"] == 2


def test_gpx_export_can_be_imported_into_second_owned_device(client):
    alice = auth(client)
    first = device(client, alice)
    second = device(client, alice)
    for time, lat in [("2026-10-01T10:00:00Z", 36), ("2026-10-01T10:01:00Z", 35)]:
        recorded = client.post("/api/locations", headers=alice, json={
            "device_id": first["id"], "latitude": lat, "longitude": -83,
            "altitude_m": 125, "recorded_at": time,
        })
        assert recorded.status_code == 201
    exported = client.get(
        "/api/export/gpx", headers=alice, params={"device_id": first["id"]}
    )
    assert exported.status_code == 200
    result = upload(client, alice, second["id"], exported.content.decode("utf-8"))
    assert result.status_code == 201, result.text
    assert result.json()["imported"] == 2
    assert len(client.get("/api/locations", headers=alice,
                          params={"device_id": second["id"]}).json()) == 2


def test_gpx_v10_supported_with_strict_timestamp(client):
    alice = auth(client)
    d = device(client, alice)
    valid = gpx((35, -83, "2026-10-01T10:00:00+00:00"), version="1.0")
    assert upload(client, alice, d["id"], valid).status_code == 201
    assert client.get("/api/summary", headers=alice).json()["points"] == 1


def test_gpx_import_rejects_bad_points_without_partial_writes(client):
    alice = auth(client)
    d = device(client, alice)
    valid_point = '<trkpt lat="35" lon="-83"><time>2026-10-01T10:00:00Z</time></trkpt>'
    missing_time = '<trkpt lat="36" lon="-83"></trkpt>'
    bad_lat = '<trkpt lat="999" lon="-83"><time>2026-10-01T10:01:00Z</time></trkpt>'
    naive_time = '<trkpt lat="36" lon="-83"><time>2026-10-01T10:01:00</time></trkpt>'
    future = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
    invalid_point_sets = [
        valid_point + missing_time, valid_point + bad_lat,
        valid_point + naive_time, valid_point
        + f'<trkpt lat="36" lon="-83"><time>{future}</time></trkpt>',
    ]
    for points in invalid_point_sets:
        text = (
            '<gpx xmlns="http://www.topografix.com/GPX/1/1" version="1.1">'
            f"<trk><trkseg>{points}</trkseg></trk></gpx>"
        )
        result = upload(client, alice, d["id"], text)
        assert result.status_code == 422, result.text
        assert client.get("/api/summary", headers=alice).json()["points"] == 0


def test_gpx_rejects_dtd_entities_malformed_xml_and_wrong_documents(client):
    alice = auth(client)
    d = device(client, alice)
    bad = [
        '<!DOCTYPE gpx [<!ENTITY x SYSTEM "file:///etc/passwd">]>'
        '<gpx xmlns="http://www.topografix.com/GPX/1/1">'
        '<trk><trkseg><trkpt lat="35" lon="-83"><time>&x;</time></trkpt>'
        '</trkseg></trk></gpx>',
        '<!DOCTYPE gpx [<!ENTITY x "expanded">]>'
        '<gpx xmlns="http://www.topografix.com/GPX/1/1"></gpx>',
        '<gpx><trk><trkseg><trkpt lat="35" lon="-83" /></trkseg></trk></gpx>',
        '<gpx xmlns="http://www.topografix.com/GPX/1/1"><trk>',
        '<gpx xmlns="http://www.topografix.com/GPX/1/1">'
        '<wpt lat="35" lon="-83" /></gpx>',
    ]
    for data in bad:
        result = upload(client, alice, d["id"], data)
        assert result.status_code == 422, result.text
    assert client.get("/api/summary", headers=alice).json()["points"] == 0


def test_gpx_body_and_record_caps(client):
    alice = auth(client)
    d = device(client, alice)
    small = gpx((35, -83, "2026-10-01T10:00:00Z"))
    assert upload(client, alice, d["id"], small, "text/plain").status_code == 415
    huge = ("<gpx>" + "x" * 2_100_000 + "</gpx>")
    assert upload(client, alice, d["id"], huge).status_code == 413
    many = gpx(*[(35, -83, "2026-10-01T10:00:00Z") for _ in range(5001)])
    assert upload(client, alice, d["id"], many).status_code == 413
    assert client.get("/api/summary", headers=alice).json()["points"] == 0
