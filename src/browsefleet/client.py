"""BrowseFleet Python SDK client."""

from __future__ import annotations

import json as _json
import os
import random
import time
from typing import Any, AsyncIterator, Iterator, Sequence
from urllib.parse import quote

import httpx

from .errors import (
    AuthError,
    BrowseFleetError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError,
)
from .types import (
    ActionResponse,
    AgentResult,
    AgentStep,
    BrowserAction,
    CaptchaResult,
    CreateSessionParams,
    PdfParams,
    Profile,
    ScrapeParams,
    ScrapeResult,
    ScreenshotParams,
    Session,
    UsageStats,
    Viewport,
)


def _snake_to_camel(key: str) -> str:
    parts = key.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def _convert_keys(obj: Any) -> Any:
    """Convert snake_case dict keys to camelCase for the API."""
    if isinstance(obj, dict):
        return {_snake_to_camel(k): _convert_keys(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_keys(item) for item in obj]
    return obj


class _SessionsResource:
    """Namespace for session-related API calls."""

    def __init__(self, client: BrowseFleet) -> None:
        self._client = client

    def create(self, **kwargs: Any) -> Session:
        """Create a new browser session.

        Args:
            session_id: Optional custom session ID.
            proxy_url: Proxy URL to route traffic through.
            stealth: Anti-detection level ("none", "basic", "full").
            user_agent: Custom user agent string.
            viewport: Dict with width and height.
            timeout: Session timeout in milliseconds.
            profile_id: Browser profile ID for persistent state.
            block_ads: Whether to block ads.
            cookies: List of cookies to inject.
            timezone: Browser timezone override.
            locale: Browser locale override.
            headers: Custom headers to set on all requests.

        Returns:
            Session object with id, websocket_url, etc.
        """
        body = _convert_keys(kwargs)
        data = self._client._request("POST", "/v1/sessions", json=body)
        return Session.from_dict(data)

    def list(self) -> list[Session]:
        """List all active browser sessions.

        Returns:
            List of Session objects.
        """
        data = self._client._request("GET", "/v1/sessions")
        return [Session.from_dict(s) for s in data.get("sessions", [])]

    def get(self, session_id: str) -> Session:
        """Get details of a specific session.

        Args:
            session_id: The session ID.

        Returns:
            Session object.
        """
        data = self._client._request("GET", f"/v1/sessions/{quote(session_id, safe='')}")
        return Session.from_dict(data)

    def release(self, session_id: str) -> bool:
        """Release (close) a single session.

        Args:
            session_id: The session ID to release.

        Returns:
            True if released successfully.
        """
        data = self._client._request("POST", f"/v1/sessions/{quote(session_id, safe='')}/release")
        return data.get("released", False)

    def release_all(self) -> int:
        """Release all active sessions.

        Returns:
            Number of sessions released.
        """
        data = self._client._request("POST", "/v1/sessions/release", json={})
        return data.get("released", 0)

    def release_batch(self, ids: list[str]) -> int:
        """Release multiple sessions by ID.

        Args:
            ids: List of session IDs to release.

        Returns:
            Number of sessions released.
        """
        data = self._client._request("POST", "/v1/sessions/release", json={"ids": ids})
        return data.get("released", 0)

    def actions(self, session_id: str, actions: Sequence[BrowserAction]) -> ActionResponse:
        """Execute browser actions on a session (Computer API).

        Args:
            session_id: The session ID.
            actions: List of action dicts (navigate, click, type, screenshot, etc.).

        Returns:
            ActionResponse with results for each action.
        """
        body = {"actions": _convert_keys(list(actions))}
        data = self._client._request("POST", f"/v1/sessions/{quote(session_id, safe='')}/actions", json=body)
        return ActionResponse.from_dict(data)

    def solve_captcha(
        self,
        session_id: str,
        type: str = "auto",
    ) -> CaptchaResult:
        """Solve a CAPTCHA on the current page.

        Args:
            session_id: The session ID.
            type: CAPTCHA type ("auto", "recaptcha", "hcaptcha", "turnstile").

        Returns:
            CaptchaResult with success status and timing.
        """
        data = self._client._request(
            "POST",
            f"/v1/sessions/{quote(session_id, safe='')}/captcha/solve",
            json={"type": type},
        )
        return CaptchaResult.from_dict(data)

    def upload_file(self, session_id: str, file_name: str, file_data: bytes) -> dict[str, Any]:
        """Upload a file to a session.

        Args:
            session_id: The session ID.
            file_name: Name for the uploaded file.
            file_data: File contents as bytes.

        Returns:
            Dict with uploaded file name and size.
        """
        files = {"file": (file_name, file_data)}
        return self._client._request(
            "POST",
            f"/v1/sessions/{quote(session_id, safe='')}/files",
            files=files,
        )

    def list_files(self, session_id: str) -> list[str]:
        """List files associated with a session.

        Args:
            session_id: The session ID.

        Returns:
            List of file paths.
        """
        data = self._client._request("GET", f"/v1/sessions/{quote(session_id, safe='')}/files")
        return data.get("files", [])

    def download_file(self, session_id: str, file_name: str) -> bytes:
        """Download a file from a session.

        Args:
            session_id: The session ID.
            file_name: Name of the file to download.

        Returns:
            File contents as bytes.
        """
        return self._client._request_raw(
            "GET",
            f"/v1/sessions/{quote(session_id, safe='')}/files/{quote(file_name, safe='')}",
        )

    def live(self, session_id: str) -> Iterator[dict[str, Any]]:
        """Stream live session events via SSE.

        Args:
            session_id: The session ID.

        Yields:
            Parsed JSON dicts from each SSE data line.
        """
        return self._client._stream_sse(
            "GET",
            f"/v1/sessions/{quote(session_id, safe='')}/live",
        )


class _AgentResource:
    """Namespace for agent-related API calls."""

    def __init__(self, client: BrowseFleet) -> None:
        self._client = client

    def run(
        self,
        task: str,
        url: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        max_iterations: int | None = None,
        api_key: str | None = None,
    ) -> AgentResult:
        """Run an autonomous agent that creates its own session.

        Args:
            task: Natural-language description of the task.
            url: Optional starting URL.
            provider: LLM provider ("anthropic" or "openai").
            model: LLM model name.
            max_iterations: Maximum agent iterations (capped at 30 server-side).
            api_key: LLM API key (uses server default if omitted).

        Returns:
            AgentResult with steps and outcome.
        """
        body: dict[str, Any] = {"task": task}
        if url is not None:
            body["url"] = url
        if provider is not None:
            body["provider"] = provider
        if model is not None:
            body["model"] = model
        if max_iterations is not None:
            body["maxIterations"] = max_iterations
        if api_key is not None:
            body["apiKey"] = api_key
        data = self._client._request("POST", "/v1/agent", json=body)
        return AgentResult.from_dict(data)

    def run_on_session(
        self,
        session_id: str,
        task: str,
        url: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        max_iterations: int | None = None,
        api_key: str | None = None,
    ) -> AgentResult:
        """Run an agent on an existing session.

        Args:
            session_id: The session ID to run on.
            task: Natural-language description of the task.
            url: Optional starting URL.
            provider: LLM provider ("anthropic" or "openai").
            model: LLM model name.
            max_iterations: Maximum agent iterations.
            api_key: LLM API key.

        Returns:
            AgentResult with steps and outcome.
        """
        body: dict[str, Any] = {"task": task}
        if url is not None:
            body["url"] = url
        if provider is not None:
            body["provider"] = provider
        if model is not None:
            body["model"] = model
        if max_iterations is not None:
            body["maxIterations"] = max_iterations
        if api_key is not None:
            body["apiKey"] = api_key
        data = self._client._request(
            "POST",
            f"/v1/sessions/{quote(session_id, safe='')}/agent",
            json=body,
        )
        return AgentResult.from_dict(data)

    def stream(
        self,
        task: str,
        url: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        max_iterations: int | None = None,
        api_key: str | None = None,
    ) -> Iterator[AgentStep]:
        """Stream agent steps via SSE.

        Args:
            task: Natural-language description of the task.
            url: Optional starting URL.
            provider: LLM provider ("anthropic" or "openai").
            model: LLM model name.
            max_iterations: Maximum agent iterations.
            api_key: LLM API key.

        Yields:
            AgentStep objects for each step event.
        """
        body: dict[str, Any] = {"task": task}
        if url is not None:
            body["url"] = url
        if provider is not None:
            body["provider"] = provider
        if model is not None:
            body["model"] = model
        if max_iterations is not None:
            body["maxIterations"] = max_iterations
        if api_key is not None:
            body["apiKey"] = api_key
        for event in self._client._stream_sse("POST", "/v1/agent/stream", json=body):
            event_type = event.get("type")
            if event_type == "step":
                yield AgentStep.from_dict(event)
            elif event_type == "screenshot":
                yield AgentStep(
                    iteration=event.get("iteration", 0),
                    reasoning="",
                    actions=[],
                    screenshot=event.get("screenshot"),
                )


class _BillingResource:
    """Namespace for billing-related API calls."""

    def __init__(self, client: BrowseFleet) -> None:
        self._client = client

    def create_checkout(self, price_id: str, success_url: str, cancel_url: str) -> dict[str, Any]:
        """Create a Stripe checkout session.

        Args:
            price_id: Stripe price ID.
            success_url: URL to redirect to on success.
            cancel_url: URL to redirect to on cancel.

        Returns:
            Dict with checkout URL and session ID.
        """
        return self._client._request(
            "POST",
            "/v1/billing/checkout",
            json={"priceId": price_id, "successUrl": success_url, "cancelUrl": cancel_url},
        )

    def create_portal(self, return_url: str) -> dict[str, Any]:
        """Create a Stripe billing portal session.

        Args:
            return_url: URL to return to after portal.

        Returns:
            Dict with portal URL.
        """
        return self._client._request(
            "POST",
            "/v1/billing/portal",
            json={"returnUrl": return_url},
        )

    def get_usage(self) -> dict[str, Any]:
        """Get billing usage information.

        Returns:
            Dict with usage data.
        """
        return self._client._request("GET", "/v1/billing/usage")


class _ProfilesResource:
    """Namespace for profile-related API calls."""

    def __init__(self, client: BrowseFleet) -> None:
        self._client = client

    def create(self, name: str) -> Profile:
        """Create a new browser profile.

        Args:
            name: Human-readable name for the profile.

        Returns:
            Profile object.
        """
        data = self._client._request("POST", "/v1/profiles", json={"name": name})
        return Profile.from_dict(data)

    def list(self) -> list[Profile]:
        """List all browser profiles.

        Returns:
            List of Profile objects.
        """
        data = self._client._request("GET", "/v1/profiles")
        return [Profile.from_dict(p) for p in data.get("profiles", [])]

    def get(self, profile_id: str) -> Profile:
        """Get a specific profile.

        Args:
            profile_id: The profile ID.

        Returns:
            Profile object.
        """
        data = self._client._request("GET", f"/v1/profiles/{quote(profile_id, safe='')}")
        return Profile.from_dict(data)

    def delete(self, profile_id: str) -> bool:
        """Delete a browser profile.

        Args:
            profile_id: The profile ID to delete.

        Returns:
            True if deleted successfully.
        """
        data = self._client._request("DELETE", f"/v1/profiles/{quote(profile_id, safe='')}")
        return data.get("deleted", False)


class BrowseFleet:
    """BrowseFleet API client.

    Args:
        api_key: Your BrowseFleet API key.
        base_url: Base URL of the BrowseFleet API server.
        timeout: Request timeout in seconds (default: 60).

    Example::

        from browsefleet import BrowseFleet

        bf = BrowseFleet(api_key="bf_xxx", base_url="https://api.browsefleet.com")
        session = bf.sessions.create(stealth="full")
        print(session.websocket_url)
        bf.sessions.release(session.id)
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.browsefleet.com",
        timeout: float = 60.0,
        max_retries: int = 2,
    ) -> None:
        resolved_key = api_key or os.environ.get("BROWSEFLEET_API_KEY")
        if not resolved_key:
            raise AuthError("api_key is required — pass it directly or set BROWSEFLEET_API_KEY")
        self._base_url = base_url.rstrip("/")
        self._max_retries = max_retries
        self._client = httpx.Client(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {resolved_key}",
                "Content-Type": "application/json",
                "User-Agent": "browsefleet-python/0.1.0",
            },
            timeout=timeout,
        )
        self.sessions = _SessionsResource(self)
        self.profiles = _ProfilesResource(self)
        self.agent = _AgentResource(self)
        self.billing = _BillingResource(self)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> BrowseFleet:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # ─── Quick Actions ──────────────────────────────────────────────────────

    def scrape(self, url: str, **kwargs: Any) -> ScrapeResult:
        """Scrape a URL and extract content.

        Args:
            url: The URL to scrape.
            wait_for: CSS selector or milliseconds to wait before extraction.
            headers: Custom request headers.
            cookies: Cookies to inject.
            proxy_url: Proxy URL to use.
            stealth: Anti-detection level.
            timeout: Request timeout in milliseconds.

        Returns:
            ScrapeResult with html, markdown, readability, links, metadata.
        """
        body = _convert_keys({"url": url, **kwargs})
        data = self._request("POST", "/v1/scrape", json=body)
        return ScrapeResult.from_dict(data)

    def screenshot(self, url: str, **kwargs: Any) -> bytes:
        """Take a screenshot of a URL.

        Args:
            url: The URL to screenshot.
            full_page: Capture the full scrollable page (default: False).
            viewport: Dict with width and height.
            quality: JPEG/WebP quality (1-100).
            format: Image format ("png", "jpeg", "webp").
            wait_for: CSS selector or milliseconds to wait.
            proxy_url: Proxy URL to use.
            stealth: Anti-detection level.
            timeout: Request timeout in milliseconds.

        Returns:
            Screenshot image bytes.
        """
        body = _convert_keys({"url": url, **kwargs})
        return self._request_raw("POST", "/v1/screenshot", json=body)

    def pdf(self, url: str, **kwargs: Any) -> bytes:
        """Generate a PDF from a URL.

        Args:
            url: The URL to render as PDF.
            format: Paper format ("A4", "Letter", "Legal").
            landscape: Landscape orientation (default: False).
            print_background: Include background graphics (default: True).
            margin: Dict with top, right, bottom, left margins.
            wait_for: CSS selector or milliseconds to wait.
            proxy_url: Proxy URL to use.
            stealth: Anti-detection level.
            timeout: Request timeout in milliseconds.

        Returns:
            PDF file bytes.
        """
        body = _convert_keys({"url": url, **kwargs})
        return self._request_raw("POST", "/v1/pdf", json=body)

    # ─── Usage ──────────────────────────────────────────────────────────────

    def usage(self) -> UsageStats:
        """Get API usage statistics.

        Returns:
            UsageStats with session counts, browser hours, and daily breakdown.
        """
        data = self._request("GET", "/v1/usage")
        return UsageStats.from_dict(data)

    def health(self) -> dict[str, Any]:
        """Check API health.

        Returns:
            Health status dict.
        """
        return self._request("GET", "/health")

    # ─── Internal ───────────────────────────────────────────────────────────

    @staticmethod
    def _is_retryable(status: int) -> bool:
        return status == 429 or status >= 500

    @staticmethod
    def _retry_delay(attempt: int, retry_after: str | None = None) -> float:
        if retry_after:
            try:
                seconds = float(retry_after)
                if seconds > 0:
                    return seconds
            except ValueError:
                pass
        base = min(1.0 * (2 ** attempt), 30.0)
        jitter = random.uniform(0, 0.2)
        return base + jitter

    def _do_request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Execute a request with retry logic and exception wrapping."""
        # For file uploads, remove Content-Type so httpx sets multipart boundary
        if "files" in kwargs:
            headers = {k: v for k, v in self._client.headers.items() if k.lower() != "content-type"}
            kwargs["headers"] = headers

        last_response: httpx.Response | None = None
        for attempt in range(self._max_retries + 1):
            try:
                response = self._client.request(method, path, **kwargs)
            except httpx.TimeoutException as exc:
                raise TimeoutError(f"Request timed out: {exc}") from exc

            if response.is_success:
                return response

            last_response = response

            if self._is_retryable(response.status_code) and attempt < self._max_retries:
                delay = self._retry_delay(attempt, response.headers.get("retry-after"))
                time.sleep(delay)
                continue

            self._raise_for_status(response)

        # Should not reach here, but satisfy type checker
        assert last_response is not None
        self._raise_for_status(last_response)
        raise BrowseFleetError("Request failed after retries")  # unreachable

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        """Make a JSON API request and return the parsed response."""
        response = self._do_request(method, path, **kwargs)
        return response.json()

    def _request_raw(self, method: str, path: str, **kwargs: Any) -> bytes:
        """Make an API request and return raw bytes (for screenshots, PDFs, files)."""
        response = self._do_request(method, path, **kwargs)
        return response.content

    def _stream_sse(self, method: str, path: str, **kwargs: Any) -> Iterator[dict[str, Any]]:
        """Make a streaming SSE request and yield parsed JSON events."""
        # For file uploads, remove Content-Type so httpx sets multipart boundary
        if "files" in kwargs:
            headers = {k: v for k, v in self._client.headers.items() if k.lower() != "content-type"}
            kwargs["headers"] = headers

        with self._client.stream(method, path, **kwargs) as response:
            if not response.is_success:
                # Read the full body so we can raise a proper error
                response.read()
                self._raise_for_status(response)

            for line in response.iter_lines():
                if line.startswith("data: "):
                    payload = line[6:]
                    if payload.strip():
                        try:
                            yield _json.loads(payload)
                        except _json.JSONDecodeError:
                            continue

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        """Raise typed exceptions for error responses."""
        if response.is_success:
            return

        try:
            body = response.json()
        except Exception:
            body = {"error": response.text}

        message = body.get("error", f"HTTP {response.status_code}")
        status = response.status_code

        if status == 400:
            raise ValidationError(message, status, body)
        if status in (401, 403):
            raise AuthError(message, status, body)
        if status == 404:
            raise NotFoundError(message, status, body)
        if status == 429:
            raise RateLimitError(message, status, body)
        if status >= 500:
            raise ServerError(message, status, body)

        raise BrowseFleetError(message, status, body)


# ─── Async Client ──────────────────────────────────────────────────────────


class _AsyncSessionsResource:
    """Async namespace for session-related API calls."""

    def __init__(self, client: AsyncBrowseFleet) -> None:
        self._client = client

    async def create(self, **kwargs: Any) -> Session:
        body = _convert_keys(kwargs)
        data = await self._client._request("POST", "/v1/sessions", json=body)
        return Session.from_dict(data)

    async def list(self) -> list[Session]:
        data = await self._client._request("GET", "/v1/sessions")
        return [Session.from_dict(s) for s in data.get("sessions", [])]

    async def get(self, session_id: str) -> Session:
        data = await self._client._request("GET", f"/v1/sessions/{quote(session_id, safe='')}")
        return Session.from_dict(data)

    async def release(self, session_id: str) -> bool:
        data = await self._client._request("POST", f"/v1/sessions/{quote(session_id, safe='')}/release")
        return data.get("released", False)

    async def release_all(self) -> int:
        data = await self._client._request("POST", "/v1/sessions/release", json={})
        return data.get("released", 0)

    async def release_batch(self, ids: list[str]) -> int:
        data = await self._client._request("POST", "/v1/sessions/release", json={"ids": ids})
        return data.get("released", 0)

    async def actions(self, session_id: str, actions: Sequence[BrowserAction]) -> ActionResponse:
        body = {"actions": _convert_keys(list(actions))}
        data = await self._client._request("POST", f"/v1/sessions/{quote(session_id, safe='')}/actions", json=body)
        return ActionResponse.from_dict(data)

    async def solve_captcha(self, session_id: str, type: str = "auto") -> CaptchaResult:
        data = await self._client._request(
            "POST",
            f"/v1/sessions/{quote(session_id, safe='')}/captcha/solve",
            json={"type": type},
        )
        return CaptchaResult.from_dict(data)

    async def upload_file(self, session_id: str, file_name: str, file_data: bytes) -> dict[str, Any]:
        files = {"file": (file_name, file_data)}
        return await self._client._request(
            "POST",
            f"/v1/sessions/{quote(session_id, safe='')}/files",
            files=files,
        )

    async def list_files(self, session_id: str) -> list[str]:
        data = await self._client._request("GET", f"/v1/sessions/{quote(session_id, safe='')}/files")
        return data.get("files", [])

    async def download_file(self, session_id: str, file_name: str) -> bytes:
        return await self._client._request_raw(
            "GET",
            f"/v1/sessions/{quote(session_id, safe='')}/files/{quote(file_name, safe='')}",
        )

    async def live(self, session_id: str) -> AsyncIterator[dict[str, Any]]:
        return self._client._stream_sse(
            "GET",
            f"/v1/sessions/{quote(session_id, safe='')}/live",
        )


class _AsyncProfilesResource:
    """Async namespace for profile-related API calls."""

    def __init__(self, client: AsyncBrowseFleet) -> None:
        self._client = client

    async def create(self, name: str) -> Profile:
        data = await self._client._request("POST", "/v1/profiles", json={"name": name})
        return Profile.from_dict(data)

    async def list(self) -> list[Profile]:
        data = await self._client._request("GET", "/v1/profiles")
        return [Profile.from_dict(p) for p in data.get("profiles", [])]

    async def get(self, profile_id: str) -> Profile:
        data = await self._client._request("GET", f"/v1/profiles/{quote(profile_id, safe='')}")
        return Profile.from_dict(data)

    async def delete(self, profile_id: str) -> bool:
        data = await self._client._request("DELETE", f"/v1/profiles/{quote(profile_id, safe='')}")
        return data.get("deleted", False)


class _AsyncAgentResource:
    """Async namespace for agent-related API calls."""

    def __init__(self, client: AsyncBrowseFleet) -> None:
        self._client = client

    async def run(
        self,
        task: str,
        url: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        max_iterations: int | None = None,
        api_key: str | None = None,
    ) -> AgentResult:
        body: dict[str, Any] = {"task": task}
        if url is not None:
            body["url"] = url
        if provider is not None:
            body["provider"] = provider
        if model is not None:
            body["model"] = model
        if max_iterations is not None:
            body["maxIterations"] = max_iterations
        if api_key is not None:
            body["apiKey"] = api_key
        data = await self._client._request("POST", "/v1/agent", json=body)
        return AgentResult.from_dict(data)

    async def run_on_session(
        self,
        session_id: str,
        task: str,
        url: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        max_iterations: int | None = None,
        api_key: str | None = None,
    ) -> AgentResult:
        body: dict[str, Any] = {"task": task}
        if url is not None:
            body["url"] = url
        if provider is not None:
            body["provider"] = provider
        if model is not None:
            body["model"] = model
        if max_iterations is not None:
            body["maxIterations"] = max_iterations
        if api_key is not None:
            body["apiKey"] = api_key
        data = await self._client._request(
            "POST",
            f"/v1/sessions/{quote(session_id, safe='')}/agent",
            json=body,
        )
        return AgentResult.from_dict(data)

    async def stream(
        self,
        task: str,
        url: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        max_iterations: int | None = None,
        api_key: str | None = None,
    ) -> AsyncIterator[AgentStep]:
        body: dict[str, Any] = {"task": task}
        if url is not None:
            body["url"] = url
        if provider is not None:
            body["provider"] = provider
        if model is not None:
            body["model"] = model
        if max_iterations is not None:
            body["maxIterations"] = max_iterations
        if api_key is not None:
            body["apiKey"] = api_key
        async for event in self._client._stream_sse("POST", "/v1/agent/stream", json=body):
            event_type = event.get("type")
            if event_type == "step":
                yield AgentStep.from_dict(event)
            elif event_type == "screenshot":
                yield AgentStep(
                    iteration=event.get("iteration", 0),
                    reasoning="",
                    actions=[],
                    screenshot=event.get("screenshot"),
                )


class _AsyncBillingResource:
    """Async namespace for billing-related API calls."""

    def __init__(self, client: AsyncBrowseFleet) -> None:
        self._client = client

    async def create_checkout(self, price_id: str, success_url: str, cancel_url: str) -> dict[str, Any]:
        return await self._client._request(
            "POST",
            "/v1/billing/checkout",
            json={"priceId": price_id, "successUrl": success_url, "cancelUrl": cancel_url},
        )

    async def create_portal(self, return_url: str) -> dict[str, Any]:
        return await self._client._request(
            "POST",
            "/v1/billing/portal",
            json={"returnUrl": return_url},
        )

    async def get_usage(self) -> dict[str, Any]:
        return await self._client._request("GET", "/v1/billing/usage")


class AsyncBrowseFleet:
    """Async BrowseFleet API client.

    Args:
        api_key: Your BrowseFleet API key.
        base_url: Base URL of the BrowseFleet API server.
        timeout: Request timeout in seconds (default: 60).

    Example::

        import asyncio
        from browsefleet import AsyncBrowseFleet

        async def main():
            async with AsyncBrowseFleet(api_key="bf_xxx") as bf:
                session = await bf.sessions.create(stealth="full")
                print(session.websocket_url)
                await bf.sessions.release(session.id)

        asyncio.run(main())
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.browsefleet.com",
        timeout: float = 60.0,
        max_retries: int = 2,
    ) -> None:
        resolved_key = api_key or os.environ.get("BROWSEFLEET_API_KEY")
        if not resolved_key:
            raise AuthError("api_key is required — pass it directly or set BROWSEFLEET_API_KEY")
        self._base_url = base_url.rstrip("/")
        self._max_retries = max_retries
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {resolved_key}",
                "Content-Type": "application/json",
                "User-Agent": "browsefleet-python/0.1.0",
            },
            timeout=timeout,
        )
        self.sessions = _AsyncSessionsResource(self)
        self.profiles = _AsyncProfilesResource(self)
        self.agent = _AsyncAgentResource(self)
        self.billing = _AsyncBillingResource(self)

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> AsyncBrowseFleet:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    # ─── Quick Actions ──────────────────────────────────────────────────────

    async def scrape(self, url: str, **kwargs: Any) -> ScrapeResult:
        body = _convert_keys({"url": url, **kwargs})
        data = await self._request("POST", "/v1/scrape", json=body)
        return ScrapeResult.from_dict(data)

    async def screenshot(self, url: str, **kwargs: Any) -> bytes:
        body = _convert_keys({"url": url, **kwargs})
        return await self._request_raw("POST", "/v1/screenshot", json=body)

    async def pdf(self, url: str, **kwargs: Any) -> bytes:
        body = _convert_keys({"url": url, **kwargs})
        return await self._request_raw("POST", "/v1/pdf", json=body)

    # ─── Usage ──────────────────────────────────────────────────────────────

    async def usage(self) -> UsageStats:
        data = await self._request("GET", "/v1/usage")
        return UsageStats.from_dict(data)

    async def health(self) -> dict[str, Any]:
        return await self._request("GET", "/health")

    # ─── Internal ───────────────────────────────────────────────────────────

    @staticmethod
    def _is_retryable(status: int) -> bool:
        return status == 429 or status >= 500

    @staticmethod
    def _retry_delay(attempt: int, retry_after: str | None = None) -> float:
        if retry_after:
            try:
                seconds = float(retry_after)
                if seconds > 0:
                    return seconds
            except ValueError:
                pass
        base = min(1.0 * (2 ** attempt), 30.0)
        jitter = random.uniform(0, 0.2)
        return base + jitter

    async def _do_request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Execute an async request with retry logic and exception wrapping."""
        if "files" in kwargs:
            headers = {k: v for k, v in self._client.headers.items() if k.lower() != "content-type"}
            kwargs["headers"] = headers

        last_response: httpx.Response | None = None
        for attempt in range(self._max_retries + 1):
            try:
                response = await self._client.request(method, path, **kwargs)
            except httpx.TimeoutException as exc:
                raise TimeoutError(f"Request timed out: {exc}") from exc

            if response.is_success:
                return response

            last_response = response

            if self._is_retryable(response.status_code) and attempt < self._max_retries:
                delay = self._retry_delay(attempt, response.headers.get("retry-after"))
                import asyncio
                await asyncio.sleep(delay)
                continue

            self._raise_for_status(response)

        assert last_response is not None
        self._raise_for_status(last_response)
        raise BrowseFleetError("Request failed after retries")

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        response = await self._do_request(method, path, **kwargs)
        return response.json()

    async def _request_raw(self, method: str, path: str, **kwargs: Any) -> bytes:
        response = await self._do_request(method, path, **kwargs)
        return response.content

    async def _stream_sse(self, method: str, path: str, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        if "files" in kwargs:
            headers = {k: v for k, v in self._client.headers.items() if k.lower() != "content-type"}
            kwargs["headers"] = headers

        async with self._client.stream(method, path, **kwargs) as response:
            if not response.is_success:
                await response.aread()
                self._raise_for_status(response)

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    payload = line[6:]
                    if payload.strip():
                        try:
                            yield _json.loads(payload)
                        except _json.JSONDecodeError:
                            continue

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        if response.is_success:
            return

        try:
            body = response.json()
        except Exception:
            body = {"error": response.text}

        message = body.get("error", f"HTTP {response.status_code}")
        status = response.status_code

        if status == 400:
            raise ValidationError(message, status, body)
        if status in (401, 403):
            raise AuthError(message, status, body)
        if status == 404:
            raise NotFoundError(message, status, body)
        if status == 429:
            raise RateLimitError(message, status, body)
        if status >= 500:
            raise ServerError(message, status, body)

        raise BrowseFleetError(message, status, body)
