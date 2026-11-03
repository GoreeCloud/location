"""End-to-end loopback-only service smoke tests.

These launch an actual Uvicorn child process using a synthetic temporary DB.
No service is bound to a public interface and no real location data is read.
"""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import time

import httpx

from goreecloud_location.store import create_account, initialize


def test_loopback_server_login_location_and_dashboard_assets(tmp_path):
    database = tmp_path / "private" / "location.db"
    initialize(database)
    create_account(database, "smoke-user", "synthetic-only-strong-password")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    environment = os.environ.copy()
    environment["GC_LOCATION_DB"] = str(database)
    command = [
        sys.executable, "-m", "goreecloud_location.cli", "serve",
        "--host", "127.0.0.1", "--port", str(port)
    ]
    process = subprocess.Popen(
        command, env=environment, stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE, text=True
    )
    try:
        with httpx.Client(
            base_url=f"http://127.0.0.1:{port}", timeout=1.0, trust_env=False
        ) as client:
            deadline = time.monotonic() + 8
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise AssertionError(f"Server exited before readiness: {process.returncode}")
                try:
                    health = client.get("/api/health")
                    if health.status_code == 200:
                        break
                except httpx.RequestError:
                    time.sleep(0.1)
            else:
                raise AssertionError("Loopback-only server did not become ready")
            assert health.json()["status"] == "ok"
            assert client.get("/openapi.json").status_code == 404
            assert client.get("/api/devices").status_code == 401

            dashboard = client.get("/")
            assert dashboard.status_code == 200
            assert "GoreeCloud Location" in dashboard.text
            assert 'id="login-form"' in dashboard.text
            assert dashboard.headers["x-frame-options"] == "DENY"
            assert "default-src 'self'" in dashboard.headers["content-security-policy"]

            for asset, content_type in [
                ("/app.js", "javascript"),
                ("/styles.css", "css"),
            ]:
                response = client.get(asset)
                assert response.status_code == 200
                assert content_type in response.headers["content-type"]
                assert len(response.content) > 100

            login = client.post("/api/auth/login", json={
                "username": "smoke-user",
                "password": "synthetic-only-strong-password",
            })
            assert login.status_code == 200, login.text
            headers = {"Authorization": "Bearer " + login.json()["access_token"]}
            registered = client.post("/api/devices", headers=headers, json={
                "name": "Synthetic test tracker", "kind": "asset"
            })
            assert registered.status_code == 201
            device_id = registered.json()["id"]
            point = client.post("/api/locations", headers=headers, json={
                "device_id": device_id,
                "latitude": 35.25,
                "longitude": -83.25,
                "accuracy_m": 9,
            })
            assert point.status_code == 201
            history = client.get("/api/locations/page", headers=headers,
                                 params={"device_id": device_id})
            assert history.status_code == 200
            assert len(history.json()["items"]) == 1
            assert client.post("/api/auth/logout", headers=headers).status_code == 204
            assert client.get("/api/me", headers=headers).status_code == 401
    finally:
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        if process.stderr:
            process.stderr.close()


def test_cli_refuses_public_binding_without_explicit_opt_in():
    result = subprocess.run(
        [sys.executable, "-m", "goreecloud_location.cli", "serve",
         "--host", "0.0.0.0", "--port", "8123"],
        capture_output=True, text=True, timeout=5
    )
    assert result.returncode != 0
    assert "requires --i-understand-network-exposure" in result.stderr
