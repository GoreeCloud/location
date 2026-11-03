"""Authentication hardening and bounded online-guessing regression tests."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from goreecloud_location.security import LoginAttemptLimiter
from test_api import auth, client


def test_username_peer_and_global_limits_are_independent():
    clock = [100.0]
    limiter = LoginAttemptLimiter(
        window_seconds=300, username_limit=3, peer_limit=4,
        global_limit=7, clock=lambda: clock[0],
    )
    for i in range(3):
        assert limiter.allow("ALICE", f"peer-{i}")
    assert not limiter.allow("alice", "other-peer")
    assert limiter.allow("bob", "peer-0")
    assert limiter.allow("charlie", "peer-0")
    assert limiter.allow("david", "peer-0")
    assert not limiter.allow("erin", "peer-0")  # peer budget full
    assert limiter.allow("eve", "peer-5")
    assert not limiter.allow("frank", "peer-6")  # global budget full
    clock[0] += 301
    assert limiter.allow("alice", "other-peer")  # expired attempts pruned


def test_limiter_is_memory_bounded_and_reservation_is_atomic():
    limiter = LoginAttemptLimiter(
        max_buckets=16, username_limit=200, peer_limit=200,
        global_limit=1000,
    )
    for i in range(200):
        assert limiter.allow(f"account-{i}", f"peer-{i}")
    assert len(limiter._buckets) <= 16

    clock = [0.0]
    atomic = LoginAttemptLimiter(
        username_limit=5, peer_limit=40, global_limit=100,
        clock=lambda: clock[0],
    )
    with ThreadPoolExecutor(max_workers=16) as executor:
        admitted = list(executor.map(lambda _: atomic.allow("same-account", "one-peer"),
                                     range(60)))
    assert sum(admitted) == 5


def test_clear_user_does_not_reset_peer_abuse_budget():
    limiter = LoginAttemptLimiter(username_limit=2, peer_limit=3, global_limit=20)
    assert limiter.allow("alice", "peer-a")
    assert limiter.allow("alice", "peer-a")
    assert not limiter.allow("alice", "peer-a")
    limiter.clear_user("alice")
    assert limiter.allow("alice", "peer-a")
    assert not limiter.allow("bob", "peer-a")


def test_unknown_username_uses_expensive_password_verifier(client, monkeypatch):
    import importlib
    mod = importlib.import_module("goreecloud_location.main")
    called = []
    def observe(password, hashed):
        called.append((password, hashed))
        return False
    monkeypatch.setattr(mod, "verify_password", observe)
    unknown = client.post("/api/auth/login", json={
        "username": "no-such-account", "password": "wrong"
    })
    known = client.post("/api/auth/login", json={
        "username": "alice", "password": "wrong"
    })
    assert unknown.status_code == known.status_code == 401
    assert len(called) == 2
    assert all(hash_value.startswith("scrypt:") for _, hash_value in called)
    assert called[0][1] != called[1][1]


def test_username_throttle_does_not_block_other_users(client):
    for _ in range(5):
        assert client.post("/api/auth/login", json={
            "username": "alice", "password": "wrong"
        }).status_code == 401
    assert client.post("/api/auth/login", json={
        "username": "alice", "password": "wrong"
    }).status_code == 429
    other_user = auth(client, "bob")
    assert client.get("/api/me", headers=other_user).status_code == 200


def test_login_session_limit_revokes_oldest_token(client):
    old = auth(client)
    latest = None
    for _ in range(23):
        latest = auth(client)
    assert latest is not None
    assert client.get("/api/me", headers=latest).status_code == 200
    assert client.get("/api/me", headers=old).status_code == 401
    assert client.get("/api/me", headers=auth(client, "bob")).status_code == 200
