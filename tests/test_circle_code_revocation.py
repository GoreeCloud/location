"""A prospective circle member can immediately revoke an unused invite code.

Code revocation only invalidates the code; it must never silently revoke
already-sent invitations, accepted memberships, or GPS/device credentials.
"""
from test_api import auth, client, device
from test_circles import circle, code, invite


def test_invitee_can_revoke_unconsumed_code_and_reissue(client):
    alice = auth(client)
    bob = auth(client, "bob")
    group = circle(client, alice)

    old = code(client, bob)
    deleted = client.delete("/api/circle-invite-code", headers=bob)
    assert deleted.status_code == 204 and deleted.content == b""
    assert invite(client, alice, group["id"], old).status_code == 422

    # Repeated revocation reveals nothing about the existence of a code.
    assert client.delete("/api/circle-invite-code", headers=bob).status_code == 204
    fresh = code(client, bob)
    assert fresh != old
    assert invite(client, alice, group["id"], fresh).status_code == 201
    assert invite(client, alice, group["id"], fresh).status_code == 422


def test_revoke_code_is_account_scoped_and_requires_login(client):
    alice = auth(client)
    bob = auth(client, "bob")
    group = circle(client, alice)
    bob_code = code(client, bob)
    alice_code = code(client, alice)
    tracker = device(client, bob)

    assert client.delete("/api/circle-invite-code").status_code == 401
    assert client.delete("/api/circle-invite-code", headers={
        "Authorization": "Bearer " + tracker["ingest_token"]
    }).status_code == 401

    # Removing Alice's own unused code cannot revoke Bob's separate code.
    assert client.delete("/api/circle-invite-code", headers=alice).status_code == 204
    assert invite(client, alice, group["id"], alice_code).status_code == 422
    invite_result = invite(client, alice, group["id"], bob_code)
    assert invite_result.status_code == 201
    assert invite_result.json()["sharing_enabled"] is False


def test_revoking_another_unused_code_preserves_pending_and_accepted_memberships(client):
    alice = auth(client)
    bob = auth(client, "bob")
    carol = auth(client, "carol")
    group = circle(client, alice)

    invitation = invite(client, alice, group["id"], code(client, bob))
    assert invitation.status_code == 201
    invite_id = invitation.json()["id"]

    # The code used for an invitation has already been consumed, and an
    # unrelated freshly generated code can be revoked independently.
    spare = code(client, bob)
    assert client.delete("/api/circle-invite-code", headers=bob).status_code == 204
    assert invite(client, alice, group["id"], spare).status_code == 422
    pending = client.get("/api/circle-invitations", headers=bob)
    assert pending.status_code == 200
    assert [row["id"] for row in pending.json()] == [invite_id]

    accepted = client.post(
        f"/api/circle-invitations/{invite_id}/respond",
        headers=bob,
        json={"accept": True},
    )
    assert accepted.status_code == 200
    assert accepted.json()["sharing_enabled"] is False
    assert client.get("/api/circles", headers=bob).json()[0]["role"] == "member"
    assert client.delete("/api/circle-invite-code", headers=bob).status_code == 204
    assert client.get("/api/circles", headers=bob).json()[0]["role"] == "member"

    # Other account codes, membership lists, and private GPS remain separate.
    carol_code = code(client, carol)
    assert client.delete("/api/circle-invite-code", headers=bob).status_code == 204
    assert invite(client, alice, group["id"], carol_code).status_code == 201
    assert client.get("/api/locations", headers=bob).json() == []
    assert client.get("/api/locations", headers=carol).json() == []
