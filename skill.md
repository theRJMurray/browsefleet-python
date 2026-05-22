# Working in browsefleet-python with a coding agent

This file is read by AI coding agents that land in this repo (Claude Code, Cursor, Aider, etc.). It contains the exact setup, run, test, and contribution steps. Read it once; refer back on errors.

## TL;DR for the impatient agent

```bash
git clone https://github.com/theRJMurray/browsefleet-python.git
cd browsefleet-python
python -m venv .venv
.venv/bin/activate          # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
pytest
```

All five commands should succeed. If `pytest` shows 36 passed, the SDK is good. Failures: jump to "Known failure modes" below.

## Required tools and versions

| Tool | Minimum | Why |
|------|---------|-----|
| Python | 3.10 (3.12 recommended) | Modern type hints, `match`, `httpx 0.27+`. Pinned in `.python-version`. |
| pip | 23+ | PEP 660 editable installs. |

The SDK has one runtime dependency: `httpx>=0.27`. Dev extras add `pytest`, `pytest-asyncio`, `pytest-cov`, `respx`, `ruff`, `mypy`.

## First-time setup

```bash
git clone https://github.com/theRJMurray/browsefleet-python.git
cd browsefleet-python
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Expected: 5 to 30 seconds. No native bindings.

## Running the project

This package is a library. The development loop:

```bash
pytest                    # run the test suite
pytest --cov              # with coverage
ruff check src tests      # lint
ruff format src tests     # autoformat
mypy src                  # strict typecheck
python -m build           # build wheel + sdist
```

To exercise the SDK against a real BrowseFleet server, see [`examples/`](./examples/).

## Verifying it works (smoke test)

```bash
python -c "import browsefleet; print(browsefleet.__version__)"
# expected: a semver string

python -c "
from browsefleet import BrowseFleet
bf = BrowseFleet(base_url='http://localhost:3000')
print(bf.health())
"
# expected: {'status': 'ok', ...} when a BrowseFleet server is running locally
```

The server is in a separate repo: https://github.com/theRJMurray/browsefleet. Run `docker run -p 3000:3000 --shm-size=2g ghcr.io/therjmurray/browsefleet:latest` to spin one up.

## Project layout

```
browsefleet-python/
├── src/
│   └── browsefleet/
│       ├── __init__.py     # public surface
│       ├── client.py       # BrowseFleet (sync) + AsyncBrowseFleet
│       ├── types.py        # dataclasses + TypedDicts (mirror server types)
│       ├── errors.py       # typed error classes
│       └── py.typed        # PEP 561 marker
├── tests/                  # pytest + respx suite
├── examples/               # runnable mini-projects
├── pyproject.toml          # PEP 621 metadata + ruff/mypy/pytest config
├── README.md
├── skill.md                # this file
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── CHANGELOG.md
├── LICENSE                 # MIT
└── .github/                # issue templates, PR template, workflows, dependabot
```

## Common tasks

### Mirror a new server endpoint

1. Add the dataclass / TypedDict to `src/browsefleet/types.py`. Mirror the server's TypeScript type exactly. Server fields are camelCase; Python fields are snake_case (the `_snake_to_camel` helper handles request conversion, and `from_dict` classmethods handle response conversion).
2. Add the method to the appropriate resource class in `src/browsefleet/client.py`. Add the same method to the async resource (mirror the sync one). Both clients live in the same file.
3. Add a test in `tests/test_<area>.py` using `@respx.mock` to intercept httpx.
4. Update `CHANGELOG.md` and `skill.md` if the public surface changed.

### Add a new typed error

1. Subclass `BrowseFleetError` in `src/browsefleet/errors.py`.
2. Re-export from `src/browsefleet/__init__.py`.
3. Map the status code in the `_throw_for_status` paths inside `client.py` (both sync and async).
4. Add a test in `tests/test_errors.py`.

### Add an async client method (sync already exists)

1. Find the sync method in `client.py`.
2. Locate the corresponding `_Async<X>Resource` class.
3. Add an `async def` mirror that awaits `self._client._request(...)`.

## Testing

```bash
pytest                       # one shot
pytest -x                    # stop on first failure
pytest --cov=browsefleet     # coverage
pytest tests/test_client.py  # one file
pytest -k "control"          # filter by name
```

The suite is fully offline. `respx` intercepts httpx requests. No live server required.

Async tests use `pytest-asyncio` in auto mode, so you don't decorate them; they run automatically.

## Linting, formatting, type checking

```bash
ruff check src tests        # lint
ruff check src tests --fix  # autofix
ruff format src tests       # format
mypy src                    # strict typecheck (src only; tests are non-strict)
```

ruff and mypy run on every PR via `.github/workflows/ci.yml`.

## Branching, commits, PRs

- Base branch: `master`. Branch off, target master.
- Branch names: `feat/<short-desc>`, `fix/<short-desc>`.
- Commits: Conventional Commits. Enforced by `.github/workflows/pr-title.yml`.
- PRs squash-merge.
- CI: matrix on Python 3.10, 3.11, 3.12, 3.13.

## Releases

Releases are automated by `release-please`. Merging `feat:` / `fix:` to `master` causes the bot to open a release PR. Merging that PR cuts a tag and the workflow publishes to PyPI via Trusted Publishing (OIDC, no API token).

Do not manually edit `pyproject.toml` `version`. The bot owns it.

## Known failure modes

### `pip install -e ".[dev]"` fails with "no matching distribution found for httpx"

You are likely on Python 3.9 or earlier. The SDK requires Python 3.10+. Check with `python --version`.

### `pytest` collects 0 tests

You forgot to install dev extras. `pip install -e ".[dev]"` includes `pytest`, `respx`, etc.

### `mypy src` fails with "Cannot find implementation or library stub for module named 'browsefleet'"

The package is not installed in the current environment. Activate the venv and `pip install -e ".[dev]"`.

### Async tests hang or fail with "RuntimeError: asyncio.run() cannot be called from a running event loop"

The `[tool.pytest.ini_options]` block in `pyproject.toml` sets `asyncio_mode = "auto"`. If the file is missing or that setting changed, `pytest-asyncio` falls back to strict mode and you need `@pytest.mark.asyncio` on every async test. Restore the auto setting.

### `respx` does not intercept

Confirm you imported it at the top of the test and decorated the test with `@respx.mock`. `respx` patches `httpx` at the transport layer; if your code reaches for `requests` or `urllib`, `respx` does nothing.

## Don't do

- Don't add `requests` or `urllib3` to dependencies. The SDK uses `httpx` everywhere.
- Don't bypass `_request` / `_request_raw` / `_stream_sse`. They own retry, timeout, and error mapping. Adding a method that calls `httpx` directly will silently miss those behaviors.
- Don't pin `httpx` to an exact version. Use `>=0.27`. We respect breaking-change semver from upstream.
- Don't reintroduce the deleted `_BillingResource` / `_AsyncBillingResource`. The server's billing routes were removed in the OSS conversion.

## Where to ask

- Bugs: open an Issue using the bug template.
- Features: feature request template (note: needs to map to a real server endpoint).
- Discussion: GitHub Discussions.
- Security: see `SECURITY.md`. Do not file security issues publicly.

---

_Last updated as part of OSS Phase 5 (2026-05-21). Linked from the README's AI Agent banner._
