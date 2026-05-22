"""BrowseFleet Python SDK, the open-source cloud browser API for AI agents."""

from importlib.metadata import PackageNotFoundError, version

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
    ControlSessionParams,
    Profile,
    ScrapeResult,
    Session,
    SessionControlMode,
    UsageStats,
)

try:
    __version__ = version("browsefleet")
except PackageNotFoundError:
    __version__ = "1.0.0"

__all__ = [
    "ActionResponse",
    "ActionResult",
    "AgentResult",
    "AgentStep",
    "AsyncBrowseFleet",
    "AuthError",
    "BrowseFleet",
    "BrowseFleetError",
    "CaptchaResult",
    "ControlSessionParams",
    "NotFoundError",
    "Profile",
    "RateLimitError",
    "ScrapeResult",
    "ServerError",
    "Session",
    "SessionControlMode",
    "TimeoutError",
    "UsageStats",
    "ValidationError",
    "__version__",
]
