# browsefleet (Python SDK)

Official Python SDK for [BrowseFleet](https://browsefleet.com), the open-source cloud browser API for AI agents.

[![PyPI](https://img.shields.io/pypi/v/browsefleet.svg)](https://pypi.org/project/browsefleet/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-3776ab.svg)](./.python-version)
[![Issues](https://img.shields.io/github/issues/theRJMurray/browsefleet-python)](https://github.com/theRJMurray/browsefleet-python/issues)

One runtime dependency (`httpx`). Sync + async clients in one import. Full type hints with `py.typed`. Tested on Python 3.10, 3.11, 3.12, 3.13.

> **Working in this repo with an AI agent?** Read [`skill.md`](./skill.md) first. It teaches Claude Code, Cursor, Aider, or any coding agent how to set up, run, test, and contribute to this repo with no further instruction.

## Install

```bash
pip install browsefleet
```

The SDK needs a running BrowseFleet server. Follow the [server repo's Quick start](https://github.com/theRJMurray/browsefleet#quick-start) to spin one up via Docker or local Node dev.

## Quick start

```python
from browsefleet import BrowseFleet

bf = BrowseFleet(
    base_url="http://localhost:3000",  # or BROWSEFLEET_URL env var
    api_key="optional-when-server-requires-it",  # or BROWSEFLEET_API_KEY env var
)

# Scrape a page
page = bf.scrape("https://example.com")
print(page.title, page.markdown[:200])

# Take a screenshot
png = bf.screenshot("https://example.com", full_page=True)
with open("example.png", "wb") as f:
    f.write(png)

# Generate a PDF
pdf = bf.pdf("https://example.com", format="A4", print_background=True)

# Spin up a persistent session
session = bf.sessions.create(stealth="full")
bf.sessions.actions(session.id, [
    {"type": "navigate", "url": "https://example.com"},
    {"type": "screenshot"},
])
bf.sessions.release(session.id)

# Vision-based agent task
result = bf.agent.run(
    task="Extract the most expensive product price from this page",
    url="https://example.com/products",
    provider="anthropic",
    max_iterations=10,
)
print(result.success, result.result)
```

## Async client

```python
import asyncio
from browsefleet import AsyncBrowseFleet

async def main():
    async with AsyncBrowseFleet(base_url="http://localhost:3000") as bf:
        page = await bf.scrape("https://example.com")
        print(page.title)

asyncio.run(main())
```

Both clients share the same public surface. Same methods, same return types, same typed errors.

## Features

- **Sessions, scrape, screenshot, PDF, agent, profiles, files, CAPTCHA.** Full coverage of the BrowseFleet REST surface.
- **Operator mode.** Sessions can start in `human` control, hand off to `agent` via `sessions.control()`.
- **Typed errors.** `AuthError`, `NotFoundError`, `RateLimitError`, `ValidationError`, `ServerError`, all extending `BrowseFleetError`.
- **Auto-retry.** Exponential backoff on `429` / `5xx`, honors `Retry-After`. Configurable per client via `max_retries`.
- **Env-var fallback.** `BROWSEFLEET_URL` and `BROWSEFLEET_API_KEY` are read when not passed explicitly.
- **Sync + async.** `BrowseFleet` and `AsyncBrowseFleet`. Both implement context-manager protocol.
- **Typed.** `py.typed` marker, dataclass return types, `TypedDict` request params. Strict mypy across the source.

## Configuration

```python
BrowseFleet(
    base_url="http://localhost:3000",  # or BROWSEFLEET_URL env (default: http://localhost:3000)
    api_key="optional",                # or BROWSEFLEET_API_KEY env (omit if server is authless)
    timeout=60.0,                      # seconds, default 60
    max_retries=2,                     # retries on 429 / 5xx, default 2
)
```

## Examples

See [`examples/`](./examples/) for runnable mini-projects:

- [`examples/quickstart/`](./examples/quickstart/), scrape + screenshot + release
- [`examples/agent_task/`](./examples/agent_task/), vision-based agent task
- [`examples/operator_mode/`](./examples/operator_mode/), human-to-agent handoff via profile + control state machine
- [`examples/async_client/`](./examples/async_client/), the same flows on `AsyncBrowseFleet`

## Contributing

PRs welcome. Read [`CONTRIBUTING.md`](./CONTRIBUTING.md) and [`skill.md`](./skill.md). Conventional Commits, squash-merge, base branch is `master`.

## Security

Do not file security issues publicly. See [`SECURITY.md`](./SECURITY.md).

## License

MIT. See [`LICENSE`](./LICENSE).

## See also

- [BrowseFleet server](https://github.com/theRJMurray/browsefleet)
- [Node SDK](https://github.com/theRJMurray/browsefleet-node)
- [Marketing site](https://browsefleet.com)
