"""BrowseFleet Python SDK — cloud browser API for AI agents and automation."""

from .client import BrowseFleet
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
    ActionResult,
    CaptchaResult,
    Profile,
    ScrapeResult,
    Session,
    UsageStats,
)

__all__ = [
    "BrowseFleet",
    "BrowseFleetError",
    "AuthError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "TimeoutError",
    "ValidationError",
    "ActionResponse",
    "ActionResult",
    "CaptchaResult",
    "Profile",
    "ScrapeResult",
    "Session",
    "UsageStats",
]

__version__ = "0.1.0"
