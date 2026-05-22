"""Tests for the SessionsResource request shapes."""

from __future__ import annotations

import httpx
import respx

from browsefleet import BrowseFleet


def _session_response(extra: dict | None = None) -> dict:
    base = {
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
        "operatorMode": False,
        "controlMode": "agent",
        "sensitiveMode": False,
    }
    if extra:
        base.update(extra)
    return base


@respx.mock
def test_sessions_create_posts_body_with_snake_to_camel_conversion() -> None:
    route = respx.post("http://localhost:3000/v1/sessions").mock(
        return_value=httpx.Response(200, json=_session_response()),
    )
    bf = BrowseFleet()
    session = bf.sessions.create(stealth="full", operator_mode=True, sensitive_mode=False)

    assert route.called
    sent = route.calls.last.request
    body = sent.read().decode()
    assert '"stealth":"full"' in body
    assert '"operatorMode":true' in body
    assert '"sensitiveMode":false' in body
    assert session.id == "sess-1"
    assert session.operator_mode is False  # the response, not the request


@respx.mock
def test_sessions_get_url_encodes_id() -> None:
    route = respx.get("http://localhost:3000/v1/sessions/with%20space").mock(
        return_value=httpx.Response(200, json=_session_response({"id": "with space"})),
    )
    bf = BrowseFleet()
    bf.sessions.get("with space")
    assert route.called


@respx.mock
def test_sessions_release_returns_bool() -> None:
    respx.post("http://localhost:3000/v1/sessions/sess-1/release").mock(
        return_value=httpx.Response(200, json={"released": True}),
    )
    bf = BrowseFleet()
    assert bf.sessions.release("sess-1") is True


@respx.mock
def test_sessions_control_posts_to_control_endpoint() -> None:
    route = respx.post("http://localhost:3000/v1/sessions/sess-1/control").mock(
        return_value=httpx.Response(200, json=_session_response({"controlMode": "agent"})),
    )
    bf = BrowseFleet()
    updated = bf.sessions.control(
        "sess-1",
        control_mode="agent",
        sensitive_mode=False,
        reason="operator finished",
    )

    assert route.called
    sent = route.calls.last.request
    body = sent.read().decode()
    assert '"controlMode":"agent"' in body
    assert '"sensitiveMode":false' in body
    assert '"reason":"operator finished"' in body
    assert updated.control_mode == "agent"


@respx.mock
def test_session_dataclass_parses_operator_mode_fields() -> None:
    respx.get("http://localhost:3000/v1/sessions/abc").mock(
        return_value=httpx.Response(
            200,
            json=_session_response(
                {
                    "id": "abc",
                    "operatorMode": True,
                    "controlMode": "human",
                    "sensitiveMode": True,
                    "currentUrl": "https://example.com",
                    "title": "Example",
                },
            ),
        ),
    )
    bf = BrowseFleet()
    session = bf.sessions.get("abc")
    assert session.operator_mode is True
    assert session.control_mode == "human"
    assert session.sensitive_mode is True
    assert session.current_url == "https://example.com"
    assert session.title == "Example"
