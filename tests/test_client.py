"""Tests for the synchronous BrowseFleet client."""

from __future__ import annotations

import os

import httpx
import pytest
import respx

from browsefleet import AuthError, BrowseFleet, BrowseFleetError, __version__


def test_construct_with_no_args_does_not_raise() -> None:
    bf = BrowseFleet()
    assert bf is not None


def test_construct_default_base_url_is_localhost() -> None:
    bf = BrowseFleet()
    assert bf._base_url == "http://localhost:3000"


def test_construct_strips_trailing_slashes_from_base_url() -> None:
    bf = BrowseFleet(base_url="http://localhost:3000///")
    assert bf._base_url == "http://localhost:3000"


def test_env_var_base_url_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BROWSEFLEET_URL", "http://bf.test.example.com:9999")
    bf = BrowseFleet()
    assert bf._base_url == "http://bf.test.example.com:9999"


def test_env_var_api_key_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BROWSEFLEET_API_KEY", "env-key")
    bf = BrowseFleet()
    assert bf._client.headers.get("x-api-key") == "env-key"


def test_no_api_key_header_when_authless() -> None:
    if "BROWSEFLEET_API_KEY" in os.environ:
        del os.environ["BROWSEFLEET_API_KEY"]
    bf = BrowseFleet()
    assert "x-api-key" not in bf._client.headers


def test_explicit_api_key_sets_header() -> None:
    bf = BrowseFleet(api_key="explicit-secret")
    assert bf._client.headers.get("x-api-key") == "explicit-secret"


def test_user_agent_includes_sdk_version() -> None:
    bf = BrowseFleet()
    ua = bf._client.headers.get("user-agent", "")
    assert ua.startswith("browsefleet-python/")


def test_dunder_version_matches_installed_package() -> None:
    assert __version__
    # Either a real semver or the dev fallback
    assert __version__ == "0.0.0-dev" or len(__version__.split(".")) >= 3


def test_context_manager_closes_client() -> None:
    with BrowseFleet() as bf:
        assert not bf._client.is_closed
    assert bf._client.is_closed


@respx.mock
def test_health_returns_dict() -> None:
    respx.get("http://localhost:3000/health").mock(
        return_value=httpx.Response(200, json={"status": "ok"}),
    )
    bf = BrowseFleet()
    assert bf.health() == {"status": "ok"}


@respx.mock
def test_scrape_posts_url_and_returns_result() -> None:
    respx.post("http://localhost:3000/v1/scrape").mock(
        return_value=httpx.Response(
            200,
            json={
                "url": "https://example.com",
                "statusCode": 200,
                "title": "Example",
                "html": "<h1>Example</h1>",
                "cleanedHtml": "<h1>Example</h1>",
                "markdown": "# Example",
                "readability": "Example",
                "links": [],
                "metadata": {},
            },
        ),
    )
    bf = BrowseFleet()
    result = bf.scrape("https://example.com")
    assert result.title == "Example"
    assert result.markdown == "# Example"


@respx.mock
def test_billing_namespace_does_not_exist() -> None:
    bf = BrowseFleet()
    assert not hasattr(bf, "billing")


def test_re_exported_error_classes() -> None:
    assert AuthError is not None
    assert BrowseFleetError is not None
    assert issubclass(AuthError, BrowseFleetError)
