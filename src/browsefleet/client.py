"""BrowseFleet Python SDK client."""

from __future__ import annotations

from typing import Any, Sequence

import httpx

from .errors import (
    AuthError,
    BrowseFleetError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .types import (
    ActionResponse,
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
        data = self._client._request("GET", f"/v1/sessions/{session_id}")
        return Session.from_dict(data)

    def release(self, session_id: str) -> bool:
        """Release (close) a single session.

        Args:
            session_id: The session ID to release.

        Returns:
            True if released successfully.
        """
        data = self._client._request("POST", f"/v1/sessions/{session_id}/release")
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
        data = self._client._request("POST", f"/v1/sessions/{session_id}/actions", json=body)
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
            f"/v1/sessions/{session_id}/captcha/solve",
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
            f"/v1/sessions/{session_id}/files",
            files=files,
        )

    def list_files(self, session_id: str) -> list[str]:
        """List files associated with a session.

        Args:
            session_id: The session ID.

        Returns:
            List of file paths.
        """
        data = self._client._request("GET", f"/v1/sessions/{session_id}/files")
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
            f"/v1/sessions/{session_id}/files/{file_name}",
        )


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
        data = self._client._request("GET", f"/v1/profiles/{profile_id}")
        return Profile.from_dict(data)

    def delete(self, profile_id: str) -> bool:
        """Delete a browser profile.

        Args:
            profile_id: The profile ID to delete.

        Returns:
            True if deleted successfully.
        """
        data = self._client._request("DELETE", f"/v1/profiles/{profile_id}")
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
        api_key: str,
        base_url: str,
        timeout: float = 60.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )
        self.sessions = _SessionsResource(self)
        self.profiles = _ProfilesResource(self)

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

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        """Make a JSON API request and return the parsed response."""
        # For file uploads, remove Content-Type so httpx sets multipart boundary
        if "files" in kwargs:
            headers = {k: v for k, v in self._client.headers.items() if k.lower() != "content-type"}
            kwargs["headers"] = headers

        response = self._client.request(method, path, **kwargs)
        self._raise_for_status(response)
        return response.json()

    def _request_raw(self, method: str, path: str, **kwargs: Any) -> bytes:
        """Make an API request and return raw bytes (for screenshots, PDFs, files)."""
        response = self._client.request(method, path, **kwargs)
        self._raise_for_status(response)
        return response.content

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
