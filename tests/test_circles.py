"""Circles require two affirmative acts and never grant GPS access."""
from datetime import datetime, timedelta, timezone

from test_api import auth, client, device
from goreecloud_location.store import connect, initialize


def circle(client, owner, name="Private family"):
    res = client.post("/api/circles", headers=owner, json={"name": name})
    assert res.status_code == 201, res.text
    return res.json()


def code(client, account):
    res = client.post("/api/circle-invite-code", headers=account)
    assert res.status_code == 201, res.text
    return res.json()["invite_code"]


def invite(client, owner, cid, token):
    return client.post(f"/api/circles/{cid}/invite", headers=owner,
                       json={"invite_code": token})


def test_circle_membership_requires_recipient_code_and_acceptance(client):
    alice, bob = auth(client), auth(client, "bob")
    owned = circle(client, alice)
    assert owned["role"] == "owner"
    assert owned["sharing_enabled"] is False
    assert client.get("/api/circles", headers=bob).json() == []
    assert client.get("/api/circle-invitations", headers=bob).json() == []
    assert client.get(f"/api/circles/{owned['id']}/members",
                      headers=bob).status_code == 404

    invitee_code = code(client, bob)
    sent = invite(client, alice, owned["id"], invitee_code)
    assert sent.status_code == 201, sent.text
    assert sent.json()["status"] == "pending"
    assert sent.json()["sharing_enabled"] is False
    assert client.get("/api/circles", headers=bob).json() == []

    pending = client.get("/api/circle-invitations", headers=bob).json()
    assert len(pending) == 1
    assert pending[0]["circle_name"] == "Private family"
    assert pending[0]["inviter_username"] == "alice"
    assert "invite_code" not in str(pending)
    assert client.get("/api/circle-invitations", headers=alice).json() == []
    rid = pending[0]["id"]
    assert client.post(f"/api/circle-invitations/{rid}/respond",
                       headers=alice, json={"accept": True}).status_code == 404
    joined = client.post(f"/api/circle-invitations/{rid}/respond",
                         headers=bob, json={"accept": True})
    assert joined.status_code == 200, joined.text
    assert joined.json() == {"id": rid, "status": "accepted",
                             "sharing_enabled": False}
    assert client.get("/api/circle-invitations", headers=bob).json() == []
    assert [c["role"] for c in client.get("/api/circles", headers=bob).json()] == ["member"]
    assert [c["role"] for c in client.get("/api/circles", headers=alice).json()] == ["owner"]

    members = client.get(f"/api/circles/{owned['id']}/members", headers=bob).json()
    assert [(m["username"], m["role"], m["status"]) for m in members] == [
        ("alice", "owner", "accepted"), ("bob", "member", "accepted")
    ]
    # Even an accepted member receives absolutely no new position access.
    d = device(client, alice)
    assert client.post("/api/locations", headers=alice, json={
        "device_id": d["id"], "latitude": 35, "longitude": -83,
    }).status_code == 201
    assert client.get("/api/locations", headers=bob).json() == []
    assert client.get("/api/locations/page", headers=bob).json()["items"] == []
    assert client.get("/api/devices", headers=bob).json() == []
    assert client.get("/api/places", headers=bob).json() == []
    assert client.get("/api/events", headers=bob).json() == []
    assert client.get(f"/api/export/geojson?device_id={d['id']}",
                      headers=bob).status_code == 404
    assert client.get(f"/api/export/gpx?device_id={d['id']}",
                      headers=bob).status_code == 404
    assert client.post("/api/locations", headers=bob, json={
        "device_id": d["id"], "latitude": 42, "longitude": -74,
    }).status_code == 404


def test_code_is_one_time_rotatable_and_never_account_enumerable(client):
    alice, bob = auth(client), auth(client, "bob")
    first = circle(client, alice)
    second = circle(client, alice, "Second circle")
    old = code(client, bob)
    fresh = code(client, bob)
    assert old != fresh
    assert invite(client, alice, first["id"], old).status_code == 422
    assert invite(client, alice, first["id"], fresh).status_code == 201
    assert invite(client, alice, second["id"], fresh).status_code == 422
    assert invite(client, alice, first["id"], "not-a-valid-code").status_code == 422
    assert client.post(f"/api/circles/{first['id']}/invite", headers=bob,
                       json={"invite_code": fresh}).status_code == 404
    assert client.post(f"/api/circles/{first['id']}/invite", headers=alice,
                       json={"invite_code": "a" * 100}).status_code == 422
    assert client.post("/api/circle-invite-code", headers={
        "Authorization": "Bearer not-a-session"
    }).status_code == 401


def test_circles_are_revocable_and_decline_never_joins(client):
    alice, bob = auth(client), auth(client, "bob")
    first = circle(client, alice)
    rid = invite(client, alice, first["id"], code(client, bob)).json()["id"]
    assert client.get(f"/api/circles/{first['id']}/members",
                      headers=bob).status_code == 404
    assert [m["status"] for m in client.get(
        f"/api/circles/{first['id']}/members", headers=alice).json()] == [
            "accepted", "pending"
        ]
    declined = client.post(f"/api/circle-invitations/{rid}/respond",
                           headers=bob, json={"accept": False})
    assert declined.status_code == 200
    assert declined.json()["status"] == "declined"
    assert client.get("/api/circles", headers=bob).json() == []
    assert client.post(f"/api/circle-invitations/{rid}/respond",
                       headers=bob, json={"accept": True}).status_code == 409
    # Fresh recipient token supports a newly chosen invitation.
    newer = invite(client, alice, first["id"], code(client, bob))
    assert newer.status_code == 201
    new_id = newer.json()["id"]
    assert new_id != rid
    assert client.post(f"/api/circle-invitations/{rid}/respond",
                       headers=bob, json={"accept": True}).status_code == 404
    assert client.post(f"/api/circle-invitations/{new_id}/respond",
                       headers=bob, json={"accept": True}).status_code == 200

    assert client.delete(f"/api/circles/{first['id']}/members/2",
                         headers=bob).status_code == 404
    assert client.delete(f"/api/circles/{first['id']}/membership",
                         headers=alice).status_code == 409
    assert client.delete(f"/api/circles/{first['id']}/membership",
                         headers=bob).status_code == 204
    assert client.get("/api/circles", headers=bob).json() == []
    new_invite = invite(client, alice, first["id"], code(client, bob))
    assert new_invite.status_code == 201
    assert client.delete(f"/api/circles/{first['id']}/members/2",
                         headers=alice).status_code == 204
    assert client.get("/api/circle-invitations", headers=bob).json() == []
    assert client.delete(f"/api/circles/{first['id']}", headers=bob).status_code == 404
    assert client.delete(f"/api/circles/{first['id']}", headers=alice).status_code == 204
    assert client.get("/api/circles", headers=alice).json() == []


def test_expiry_is_checked_on_both_invite_and_acceptance(client, tmp_path):
    alice, bob = auth(client), auth(client, "bob")
    owned = circle(client, alice)
    token = code(client, bob)
    with connect(tmp_path / "private" / "location.db") as db:
        db.execute("UPDATE circle_invite_codes SET expires_at='2000-01-01T00:00:00Z'")
    assert invite(client, alice, owned["id"], token).status_code == 422
    rid = invite(client, alice, owned["id"], code(client, bob)).json()["id"]
    with connect(tmp_path / "private" / "location.db") as db:
        db.execute("UPDATE circle_memberships SET expires_at='2000-01-01T00:00:00Z' WHERE id=?", (rid,))
    assert client.get("/api/circle-invitations", headers=bob).json() == []
    assert client.post(f"/api/circle-invitations/{rid}/respond",
                       headers=bob, json={"accept": True}).status_code == 410
    assert client.get("/api/circles", headers=bob).json() == []
    renewed = invite(client, alice, owned["id"], code(client, bob))
    assert renewed.status_code == 201
    assert renewed.json()["id"] != rid


def test_privacy_default_auth_and_input_validation(client):
    alice, bob = auth(client), auth(client, "bob")
    tracker = device(client, alice)
    key = {"Authorization": "Bearer " + tracker["ingest_token"]}
    for url in ("/api/circles", "/api/circle-invitations"):
        assert client.get(url).status_code == 401
        assert client.get(url, headers=key).status_code == 401
    assert client.post("/api/circles", json={"name": "test"}).status_code == 401
    assert client.post("/api/circles", headers=key,
                       json={"name": "test"}).status_code == 401
    assert client.post("/api/circles", headers=alice,
                       json={"name": "   "}).status_code == 422
    assert client.post("/api/circles", headers=alice,
                       json={"name": "a" * 81}).status_code == 422
    assert client.post("/api/circles", headers=alice,
                       json={"name": "okay", "unknown": True}).status_code == 422
    assert client.post("/api/circle-invite-code", headers=key).status_code == 401

    created = circle(client, alice)
    rid = invite(client, alice, created["id"], code(client, bob)).json()["id"]
    assert client.post(f"/api/circle-invitations/{rid}/respond",
                       headers=bob, json={"accept": "true"}).status_code == 422
    assert client.post(f"/api/circle-invitations/{rid}/respond",
                       headers=bob, json={"accept": 1}).status_code == 422
    assert client.get(f"/api/circles/{created['id']}/members", headers=key).status_code == 401
    assert client.get(f"/api/circles/999999/members", headers=alice).status_code == 404
    assert client.get("/api/circle-invitations", headers=alice).json() == []


def test_owned_circles_are_bounded_and_reinitialize_safely(client, tmp_path):
    alice = auth(client)
    for n in range(20):
        circle(client, alice, f"Private {n}")
    overflow = client.post("/api/circles", headers=alice, json={"name": "21"})
    assert overflow.status_code == 409
    database = tmp_path / "private" / "location.db"
    initialize(database)
    initialize(database)
    with connect(database) as db:
        assert db.execute("SELECT COUNT(*) FROM circles").fetchone()[0] == 20
        cols = {x["name"] for x in db.execute("PRAGMA table_info(circle_memberships)")}
        assert {"circle_id", "account_id", "status", "expires_at"}.issubset(cols)
