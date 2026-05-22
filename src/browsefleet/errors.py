"""BrowseFleet SDK exceptions."""

from __future__ import annotations


class BrowseFleetError(Exception):
    """Base exception for all BrowseFleet API errors."""

    def __init__(
        self, message: str, status_code: int | None = None, body: dict | None = None
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body or {}


class AuthError(BrowseFleetError):
    """Raised on 401/403 responses (invalid or missing API key)."""


class NotFoundError(BrowseFleetError):
    """Raised on 404 responses (session/profile not found)."""


class RateLimitError(BrowseFleetError):
    """Raised on 429 responses (too many sessions or requests)."""


class ValidationError(BrowseFleetError):
    """Raised on 400 responses (invalid request body)."""


class ServerError(BrowseFleetError):
    """Raised on 5xx responses."""


class TimeoutError(BrowseFleetError):
    """Raised when a request times out."""
