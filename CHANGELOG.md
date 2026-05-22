# Changelog

All notable changes to the BrowseFleet Python SDK are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the SDK adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
