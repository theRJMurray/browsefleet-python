# Changelog

All notable changes to the BrowseFleet Python SDK are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the SDK adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.0.0 (2026-05-22)

First public OSS release. MIT licensed. Coordinated v1.0.0 launch alongside the BrowseFleet server and Node SDK.

### Features

* agent/billing/live endpoints, async client, full API coverage ([e7233ab](https://github.com/theRJMurray/browsefleet-python/commit/e7233ab2071ae2a3f7345bf89b6aea2bf49c8273))
* auto-retry, default base_url, env fallback, typed errors, py.typed ([343a3a5](https://github.com/theRJMurray/browsefleet-python/commit/343a3a5f845bcb0634373303164c09d9461f34cf))
* oss phase 5 foundation, sync + async, tests, CI ([#1](https://github.com/theRJMurray/browsefleet-python/issues/1)) ([78d7667](https://github.com/theRJMurray/browsefleet-python/commit/78d76677418ebf53b8bd37e4b76d1060f88e9e78))


### Bug Fixes

* async live() yields properly, SSE handles [DONE] sentinel ([bc78a43](https://github.com/theRJMurray/browsefleet-python/commit/bc78a4372e010a00028f2ab4c20e854823d99323))

## [Unreleased]

### Added

- LICENSE (MIT), CODE_OF_CONDUCT.md (Contributor Covenant 2.1), SECURITY.md, CONTRIBUTING.md.
- `skill.md` at the repo root for AI coding agents.
- `.github/` issue and PR templates, CODEOWNERS, FUNDING placeholder, dependabot.
- `.editorconfig`, `.python-version`, `.gitattributes`.
- ruff + mypy + pytest configuration in `pyproject.toml`. Strict mypy across `src/`.
- pytest-asyncio + respx for async tests + httpx mocking. Test suite under `tests/`.
- GitHub Actions: `ci.yml` (matrix Python 3.10/3.11/3.12/3.13), `release.yml` (release-please + PyPI publish via Trusted Publishing), `skill-smoke.yml`, `pr-title.yml`.
- `sessions.control()` method on both sync and async clients, plus operator-mode fields on `Session` and `CreateSessionParams` (`operator_mode`, `sensitive_mode`, `control_mode`, `events_url`). `SessionControlMode` and `ControlSessionParams` types.
- `__version__` now read from installed package metadata via `importlib.metadata`.

### Changed

- `base_url` defaults to `http://localhost:3000` (was `https://api.browsefleet.com`, which does not exist). Reads `BROWSEFLEET_URL` env var as a fallback.
- `api_key` is now optional. The SDK omits the `x-api-key` header when no key is configured, matching the server's authless-by-default behavior.
- `User-Agent` header now reports the installed SDK version dynamically.
- `Authorization: Bearer` header replaced with `x-api-key` to match the BrowseFleet server's auth scheme.

### Removed

- `_BillingResource` and `_AsyncBillingResource` namespaces (`create_checkout`, `create_portal`, `get_usage`). The server's billing routes were removed during the OSS conversion (see the server repo's ADR-0001).

## [0.1.0] - 2026-04-02

Initial private release. Not published to PyPI.
