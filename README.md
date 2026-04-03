# BrowseFleet Python SDK

Python client for the [BrowseFleet](https://browsefleet.com) cloud browser API. Manage headless browser sessions, scrape pages, take screenshots, generate PDFs, and control browsers programmatically.

## Installation

```bash
pip install browsefleet
```

## Quick Start

```python
from browsefleet import BrowseFleet

bf = BrowseFleet(api_key="bf_xxx", base_url="https://api.browsefleet.com")

# Scrape a page
result = bf.scrape("https://example.com")
print(result.markdown)

# Take a screenshot
image = bf.screenshot("https://example.com", full_page=True)
with open("screenshot.png", "wb") as f:
    f.write(image)

# Generate a PDF
pdf = bf.pdf("https://example.com", format="A4", print_background=True)
with open("page.pdf", "wb") as f:
    f.write(pdf)
```

## Sessions

Create browser sessions to connect via Playwright, Puppeteer, or any CDP client.

```python
# Create a session
session = bf.sessions.create(
    stealth="full",
    viewport={"width": 1920, "height": 1080},
    block_ads=True,
    timezone="America/New_York",
)
print(session.id)
print(session.websocket_url)  # Connect Playwright here

# List active sessions
sessions = bf.sessions.list()
for s in sessions:
    print(f"{s.id} — {s.status}")

# Get session details
session = bf.sessions.get("session-id")

# Release a session
bf.sessions.release("session-id")

# Release all sessions
bf.sessions.release_all()

# Release specific sessions
bf.sessions.release_batch(["id-1", "id-2"])
```

### Session Options

| Parameter | Type | Description |
|-----------|------|-------------|
| `stealth` | `"none" \| "basic" \| "full"` | Anti-detection level |
| `viewport` | `dict` | `{"width": 1920, "height": 1080}` |
| `proxy_url` | `str` | Route traffic through a proxy |
| `user_agent` | `str` | Custom user agent |
| `timeout` | `int` | Session timeout in milliseconds |
| `profile_id` | `str` | Persistent browser profile |
| `block_ads` | `bool` | Block ads |
| `cookies` | `list` | Inject cookies |
| `timezone` | `str` | Timezone override |
| `locale` | `str` | Locale override |
| `headers` | `dict` | Custom headers |

## Quick Actions

### Scrape

```python
result = bf.scrape(
    "https://example.com",
    wait_for="article",  # CSS selector or milliseconds
    stealth="full",
)
print(result.url)
print(result.title)
print(result.markdown)       # Cleaned markdown content
print(result.readability)    # Reader-mode text
print(result.links)          # [{"href": "...", "text": "..."}]
print(result.metadata)       # description, og_image, canonical
```

### Screenshot

```python
image_bytes = bf.screenshot(
    "https://example.com",
    full_page=True,
    format="png",           # "png", "jpeg", "webp"
    quality=90,             # JPEG/WebP quality
    viewport={"width": 1440, "height": 900},
)
```

### PDF

```python
pdf_bytes = bf.pdf(
    "https://example.com",
    format="A4",            # "A4", "Letter", "Legal"
    landscape=False,
    print_background=True,
    margin={"top": "1cm", "bottom": "1cm"},
)
```

## Computer API

Execute browser actions on a session — click, type, scroll, navigate, take screenshots.

```python
session = bf.sessions.create(stealth="full")

response = bf.sessions.actions(session.id, [
    {"type": "navigate", "url": "https://example.com"},
    {"type": "wait", "duration": 1000},
    {"type": "click", "x": 100, "y": 200},
    {"type": "type", "text": "hello world"},
    {"type": "press_key", "key": "Enter"},
    {"type": "screenshot"},
])

for result in response.results:
    print(f"{result.type}: success={result.success}")
    if result.screenshot:
        print(f"  screenshot (base64): {result.screenshot[:50]}...")

bf.sessions.release(session.id)
```

### Action Types

| Action | Fields | Description |
|--------|--------|-------------|
| `navigate` | `url` | Navigate to URL |
| `click` | `x`, `y`, `button?`, `click_count?` | Click at coordinates |
| `type` | `text` | Type text |
| `press_key` | `key` | Press a keyboard key |
| `scroll` | `x?`, `y?`, `delta_x?`, `delta_y?` | Scroll |
| `move_mouse` | `x`, `y` | Move mouse cursor |
| `wait` | `duration` | Wait in milliseconds |
| `screenshot` | — | Take a screenshot |

## CAPTCHA Solving

Solve CAPTCHAs on the current page (requires 2captcha API key on the server).

```python
result = bf.sessions.solve_captcha(session.id, type="auto")
print(result.success)
print(result.type)      # "recaptcha", "hcaptcha", "turnstile"
print(result.duration)  # Milliseconds
```

## Browser Profiles

Persistent browser profiles that preserve cookies and local storage across sessions.

```python
# Create a profile
profile = bf.profiles.create("My Profile")
print(profile.id)

# Use it in a session
session = bf.sessions.create(profile_id=profile.id)

# List profiles
profiles = bf.profiles.list()

# Delete a profile
bf.profiles.delete(profile.id)
```

## File Management

Upload and download files within a session.

```python
# Upload a file
bf.sessions.upload_file(session.id, "input.csv", csv_bytes)

# List files
files = bf.sessions.list_files(session.id)

# Download a file
data = bf.sessions.download_file(session.id, "output.csv")
```

## Usage Statistics

```python
stats = bf.usage()
print(f"Active sessions: {stats.active_sessions}")
print(f"Total browser hours: {stats.total_browser_hours}")
print(f"API calls today: {stats.today_api_calls}")
```

## Health Check

```python
health = bf.health()
print(health)
```

## Error Handling

The SDK raises typed exceptions for all error responses.

```python
from browsefleet import (
    BrowseFleetError,
    AuthError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    ServerError,
)

try:
    session = bf.sessions.get("nonexistent")
except NotFoundError:
    print("Session not found")
except AuthError:
    print("Invalid API key")
except RateLimitError:
    print("Too many concurrent sessions")
except BrowseFleetError as e:
    print(f"API error {e.status_code}: {e}")
```

All exceptions inherit from `BrowseFleetError` and include:
- `status_code` — HTTP status code
- `body` — Raw error response dict

## Context Manager

The client can be used as a context manager to ensure cleanup:

```python
with BrowseFleet(api_key="bf_xxx", base_url="https://api.browsefleet.com") as bf:
    result = bf.scrape("https://example.com")
    print(result.markdown)
```

## Requirements

- Python 3.10+
- httpx >= 0.24.0

## License

MIT
