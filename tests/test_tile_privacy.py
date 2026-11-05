"""Optional map tiles must never enable browser requests to external hosts."""
import pytest

from test_api import client


@pytest.mark.parametrize("unsafe", [
    "https://tiles.example.net/{z}/{x}/{y}.png",
    "//tiles.example.net/{z}/{x}/{y}.png",
    "/\\tiles.example.net/{z}/{x}/{y}.png",
    "\\tiles.example.net/{z}/{x}/{y}.png",
    "/\t/tiles/{z}/{x}/{y}.png",
    "/\n/tiles/{z}/{x}/{y}.png",
    "tiles/{z}/{x}/{y}.png",
])
def test_unsafe_tile_template_is_never_exposed(client, monkeypatch, unsafe):
    monkeypatch.setenv("GC_TILE_TEMPLATE", unsafe)
    response = client.get("/api/config")
    assert response.status_code == 200
    assert response.json()["tile_template"] == ""


@pytest.mark.parametrize("safe", [
    "/tiles/{z}/{x}/{y}.png",
    "/private-tiles/{z}/{x}/{y}.webp?style=light",
])
def test_same_origin_tile_template_remains_available(client, monkeypatch, safe):
    monkeypatch.setenv("GC_TILE_TEMPLATE", safe)
    response = client.get("/api/config")
    assert response.status_code == 200
    assert response.json()["tile_template"] == safe


def test_image_content_policy_blocks_external_https_tiles(client):
    result = client.get("/")
    assert result.status_code == 200
    csp = result.headers["content-security-policy"]
    assert "img-src 'self' data:;" in csp
    assert "img-src 'self' data: https:;" not in csp
    assert "connect-src 'self'" in csp
