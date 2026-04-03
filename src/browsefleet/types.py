"""BrowseFleet SDK type definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, TypedDict


# ─── Session Types ─────────────────────────────────────────────────────────


class Viewport(TypedDict, total=False):
    width: int
    height: int


class CookieParam(TypedDict, total=False):
    name: str
    value: str
    domain: str
    path: str


class CreateSessionParams(TypedDict, total=False):
    session_id: str
    proxy_url: str
    stealth: Literal["none", "basic", "full"]
    user_agent: str
    viewport: Viewport
    timeout: int
    profile_id: str
    block_ads: bool
    cookies: list[CookieParam]
    timezone: str
    locale: str
    headers: dict[str, str]


@dataclass
class Session:
    id: str
    status: str
    websocket_url: str
    viewer_url: str
    created_at: str
    expires_at: str
    timeout: int
    stealth: str
    viewport: Viewport
    proxy_url: str | None = None
    profile_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Session:
        return cls(
            id=data["id"],
            status=data["status"],
            websocket_url=data["websocketUrl"],
            viewer_url=data["viewerUrl"],
            created_at=data["createdAt"],
            expires_at=data["expiresAt"],
            timeout=data["timeout"],
            stealth=data["stealth"],
            viewport=data.get("viewport", {"width": 1920, "height": 1080}),
            proxy_url=data.get("proxyUrl"),
            profile_id=data.get("profileId"),
        )


# ─── Quick Action Types ────────────────────────────────────────────────────


class ScrapeParams(TypedDict, total=False):
    wait_for: str | int
    headers: dict[str, str]
    cookies: list[CookieParam]
    proxy_url: str
    stealth: Literal["none", "basic", "full"]
    timeout: int


class LinkItem(TypedDict):
    href: str
    text: str


class ScrapeMetadata(TypedDict, total=False):
    description: str
    og_image: str
    canonical: str


@dataclass
class ScrapeResult:
    url: str
    status_code: int
    title: str
    html: str
    cleaned_html: str
    markdown: str
    readability: str
    links: list[LinkItem]
    metadata: ScrapeMetadata

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScrapeResult:
        meta = data.get("metadata", {})
        metadata: ScrapeMetadata = {}
        if "description" in meta:
            metadata["description"] = meta["description"]
        if "ogImage" in meta:
            metadata["og_image"] = meta["ogImage"]
        if "canonical" in meta:
            metadata["canonical"] = meta["canonical"]

        return cls(
            url=data["url"],
            status_code=data["statusCode"],
            title=data["title"],
            html=data["html"],
            cleaned_html=data["cleanedHtml"],
            markdown=data["markdown"],
            readability=data["readability"],
            links=data.get("links", []),
            metadata=metadata,
        )


class ScreenshotParams(TypedDict, total=False):
    full_page: bool
    viewport: Viewport
    quality: int
    format: Literal["png", "jpeg", "webp"]
    wait_for: str | int
    proxy_url: str
    stealth: Literal["none", "basic", "full"]
    timeout: int


class PdfParams(TypedDict, total=False):
    format: Literal["A4", "Letter", "Legal"]
    landscape: bool
    print_background: bool
    margin: dict[str, str]
    wait_for: str | int
    proxy_url: str
    stealth: Literal["none", "basic", "full"]
    timeout: int


# ─── Computer API Types ────────────────────────────────────────────────────


class ScreenshotAction(TypedDict):
    type: Literal["screenshot"]


class ClickAction(TypedDict, total=False):
    type: Literal["click"]
    x: int
    y: int
    button: Literal["left", "right", "middle"]
    click_count: int


class TypeAction(TypedDict):
    type: Literal["type"]
    text: str


class PressKeyAction(TypedDict):
    type: Literal["press_key"]
    key: str


class ScrollAction(TypedDict, total=False):
    type: Literal["scroll"]
    x: int
    y: int
    delta_x: int
    delta_y: int


class MoveMouseAction(TypedDict):
    type: Literal["move_mouse"]
    x: int
    y: int


class WaitAction(TypedDict):
    type: Literal["wait"]
    duration: int


class NavigateAction(TypedDict):
    type: Literal["navigate"]
    url: str


BrowserAction = (
    ScreenshotAction
    | ClickAction
    | TypeAction
    | PressKeyAction
    | ScrollAction
    | MoveMouseAction
    | WaitAction
    | NavigateAction
)


@dataclass
class ActionResult:
    type: str
    success: bool
    screenshot: str | None = None
    error: str | None = None


@dataclass
class ActionResponse:
    results: list[ActionResult]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ActionResponse:
        return cls(
            results=[
                ActionResult(
                    type=r["type"],
                    success=r["success"],
                    screenshot=r.get("screenshot"),
                    error=r.get("error"),
                )
                for r in data.get("results", [])
            ]
        )


# ─── CAPTCHA Types ─────────────────────────────────────────────────────────


@dataclass
class CaptchaResult:
    success: bool
    type: str
    duration: int
    error: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CaptchaResult:
        return cls(
            success=data["success"],
            type=data["type"],
            duration=data["duration"],
            error=data.get("error"),
        )


# ─── Profile Types ─────────────────────────────────────────────────────────


@dataclass
class Profile:
    id: str
    name: str
    created_at: str
    updated_at: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Profile:
        return cls(
            id=data["id"],
            name=data["name"],
            created_at=data["createdAt"],
            updated_at=data["updatedAt"],
        )


# ─── Usage Types ───────────────────────────────────────────────────────────


class DailyUsage(TypedDict):
    date: str
    sessions: int
    browser_hours: float
    api_calls: int


@dataclass
class UsageStats:
    total_sessions: int
    active_sessions: int
    total_browser_hours: float
    today_browser_hours: float
    today_api_calls: int
    daily: list[DailyUsage]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UsageStats:
        return cls(
            total_sessions=data["totalSessions"],
            active_sessions=data["activeSessions"],
            total_browser_hours=data["totalBrowserHours"],
            today_browser_hours=data["todayBrowserHours"],
            today_api_calls=data["todayApiCalls"],
            daily=[
                DailyUsage(
                    date=d["date"],
                    sessions=d["sessions"],
                    browser_hours=d["browserHours"],
                    api_calls=d["apiCalls"],
                )
                for d in data.get("daily", [])
            ],
        )
