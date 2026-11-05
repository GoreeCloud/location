"""Account-wide session revocation must not revoke other accounts or trackers."""
from test_api import auth, client, device


def test_logout_all_revokes_only_current_accounts_sessions(client):
    alice_first = auth(client)
    alice_second = auth(client)
    bob = auth(client, "bob")
    registered = device(client, alice_first)
    device_key = {"Authorization": "Bearer " + registered["ingest_token"]}

    assert client.post("/api/auth/logout-all").status_code == 401
    assert client.post("/api/auth/logout-all", headers=device_key).status_code == 401
    assert client.get("/api/me", headers=alice_first).status_code == 200
    assert client.get("/api/me", headers=alice_second).status_code == 200
    assert client.get("/api/me", headers=bob).status_code == 200

    revoked = client.post("/api/auth/logout-all", headers=alice_first)
    assert revoked.status_code == 204
    assert client.get("/api/me", headers=alice_first).status_code == 401
    assert client.get("/api/me", headers=alice_second).status_code == 401
    assert client.post("/api/auth/logout-all", headers=alice_second).status_code == 401
    assert client.get("/api/me", headers=bob).status_code == 200

    # Device upload keys are deliberately separate from user login sessions.
    point = client.post(
        f"/api/ingest/{registered['id']}", headers=device_key,
        json={"latitude": 35.0, "longitude": -83.0, "accuracy_m": 5},
    )
    assert point.status_code == 201

    fresh = auth(client)
    assert client.get("/api/summary", headers=fresh).json()["points"] == 1


def test_each_account_can_revoke_its_own_sessions_independently(client):
    alice = auth(client)
    bob_first = auth(client, "bob")
    bob_second = auth(client, "bob")
    assert client.post("/api/auth/logout-all", headers=bob_first).status_code == 204
    assert client.get("/api/me", headers=alice).status_code == 200
    assert client.get("/api/me", headers=bob_first).status_code == 401
    assert client.get("/api/me", headers=bob_second).status_code == 401
