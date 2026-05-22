"""Tests for the typed error class mapping."""

from __future__ import annotations

import httpx
import pytest
import respx

from browsefleet import (
    AuthError,
    BrowseFleet,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)


@respx.mock
def test_400_raises_validation_error() -> None:
    respx.get("http://localhost:3000/v1/usage").mock(
        return_value=httpx.Response(400, json={"error": "bad request"}),
    )
    bf = BrowseFleet(max_retries=0)
    with pytest.raises(ValidationError):
        bf.usage()


@respx.mock
def test_401_raises_auth_error() -> None:
    respx.get("http://localhost:3000/v1/usage").mock(
        return_value=httpx.Response(401, json={"error": "no key"}),
    )
    bf = BrowseFleet(max_retries=0)
    with pytest.raises(AuthError):
        bf.usage()


@respx.mock
def test_404_raises_not_found_error() -> None:
    respx.get("http://localhost:3000/v1/sessions/missing").mock(
        return_value=httpx.Response(404, json={"error": "not found"}),
    )
    bf = BrowseFleet(max_retries=0)
    with pytest.raises(NotFoundError):
        bf.sessions.get("missing")


@respx.mock
def test_429_raises_rate_limit_error() -> None:
    respx.get("http://localhost:3000/v1/usage").mock(
        return_value=httpx.Response(429, headers={"retry-after": "5"}, json={"error": "slow"}),
    )
    bf = BrowseFleet(max_retries=0)
    with pytest.raises(RateLimitError):
        bf.usage()


@respx.mock
def test_500_raises_server_error() -> None:
    respx.get("http://localhost:3000/v1/usage").mock(
        return_value=httpx.Response(500, json={"error": "broken"}),
    )
    bf = BrowseFleet(max_retries=0)
    with pytest.raises(ServerError):
        bf.usage()


@respx.mock
def test_retry_on_429_succeeds_on_third_attempt() -> None:
    respx.get("http://localhost:3000/v1/usage").mock(
        side_effect=[
            httpx.Response(429, headers={"retry-after": "0"}, json={"error": "slow"}),
            httpx.Response(429, headers={"retry-after": "0"}, json={"error": "slow"}),
            httpx.Response(
                200,
                json={
                    "totalSessions": 0,
                    "activeSessions": 0,
                    "totalBrowserHours": 0,
                    "todayBrowserHours": 0,
                    "todayApiCalls": 0,
                    "daily": [],
                },
            ),
        ],
    )
    bf = BrowseFleet(max_retries=3)
    result = bf.usage()
    assert result.total_sessions == 0


@respx.mock
def test_no_retry_on_non_429_4xx() -> None:
    route = respx.get("http://localhost:3000/v1/usage").mock(
        return_value=httpx.Response(400, json={"error": "bad"}),
    )
    bf = BrowseFleet(max_retries=3)
    with pytest.raises(ValidationError):
        bf.usage()
    assert route.call_count == 1
