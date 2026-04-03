"""BrowseFleet Python SDK — cloud browser API for AI agents and automation."""

from .client import AsyncBrowseFleet, BrowseFleet
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
    AgentResult,
    AgentStep,
    CaptchaResult,
    Profile,
    ScrapeResult,
    Session,
    UsageStats,
)

__all__ = [
    "AsyncBrowseFleet",
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
    "AgentResult",
    "AgentStep",
    "CaptchaResult",
    "Profile",
    "ScrapeResult",
    "Session",
    "UsageStats",
]

__version__ = "0.1.0"
