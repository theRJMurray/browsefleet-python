# Contributing to the BrowseFleet Python SDK

Thanks for the PR. Read [`skill.md`](./skill.md) for the exact setup, run, test, and contribution commands.

## TL;DR

1. Read `skill.md`.
2. Fork, branch off `master`, run `ruff check . && mypy src && pytest`, commit with [Conventional Commits](https://www.conventionalcommits.org/), open a PR.
3. CI runs the same checks on Python 3.10, 3.11, 3.12, and 3.13.

## What makes a good PR

- One logical change. If you touch the public surface, update `skill.md` and `CHANGELOG.md` in the same PR.
- New behavior gets a pytest test. Bug fixes get a regression test. Mocks for outbound HTTP use `respx` (httpx mocker).
- The SDK is a thin REST wrapper. We do not add features that the BrowseFleet server does not already expose. Server first, SDK second.
- No new runtime dependencies without discussion. The SDK ships with one runtime dep: `httpx`.

## What we will not accept

- Reintroducing the billing / hosted-SaaS code paths removed during the OSS conversion.
- Telemetry or phone-home behavior. The SDK is silent.
- Breaking changes without a `BREAKING CHANGE:` Conventional Commit footer and a CHANGELOG entry explaining the migration path.

## Releases

Releases are automated via `release-please`. Merge `feat:` / `fix:` commits to `master`; the bot opens a release PR. Merging that PR cuts a tag and the workflow publishes to PyPI via Trusted Publishing (OIDC).

## License

By submitting a contribution, you agree it is licensed under the [MIT License](./LICENSE). No CLA.
