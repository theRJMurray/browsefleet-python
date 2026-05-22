"""Tests for the asynchronous AsyncBrowseFleet client."""

from __future__ import annotations

import httpx
import pytest
import respx

from browsefleet import AsyncBrowseFleet


async def test_async_construct_with_no_args_does_not_raise() -> None:
    bf = AsyncBrowseFleet()
    assert bf is not None
    await bf.close()


@respx.mock
async def test_async_health() -> None:
    respx.get("http://localhost:3000/health").mock(
        return_value=httpx.Response(200, json={"status": "ok"}),
    )
    async with AsyncBrowseFleet() as bf:
        assert await bf.health() == {"status": "ok"}


@respx.mock
async def test_async_scrape() -> None:
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
    async with AsyncBrowseFleet() as bf:
        result = await bf.scrape("https://example.com")
        assert result.markdown == "# Example"


@respx.mock
async def test_async_sessions_control() -> None:
    response = {
        "id": "sess-1",
        "status": "active",
        "websocketUrl": "ws://localhost:3000/cdp/sess-1",
        "viewerUrl": "http://localhost:3000/v1/sessions/sess-1/live",
        "eventsUrl": "http://localhost:3000/v1/sessions/sess-1/events",
        "createdAt": "2026-05-21T20:00:00.000Z",
        "expiresAt": "2026-05-21T20:30:00.000Z",
        "timeout": 1800000,
        "stealth": "full",
        "viewport": {"width": 1920, "height": 1080},
        "operatorMode": True,
        "controlMode": "agent",
        "sensitiveMode": False,
    }
    route = respx.post("http://localhost:3000/v1/sessions/sess-1/control").mock(
        return_value=httpx.Response(200, json=response),
    )
    async with AsyncBrowseFleet() as bf:
        updated = await bf.sessions.control("sess-1", control_mode="agent")
        assert updated.control_mode == "agent"
    assert route.called


async def test_async_billing_namespace_does_not_exist() -> None:
    async with AsyncBrowseFleet() as bf:
        assert not hasattr(bf, "billing")


@pytest.mark.parametrize("status", [400, 401, 404, 429, 500])
@respx.mock
async def test_async_status_mappings_raise(status: int) -> None:
    from browsefleet import BrowseFleetError

    respx.get("http://localhost:3000/v1/usage").mock(
        return_value=httpx.Response(status, json={"error": "x"}, headers={"retry-after": "0"}),
    )
    async with AsyncBrowseFleet(max_retries=0) as bf:
        with pytest.raises(BrowseFleetError):
            await bf.usage()
