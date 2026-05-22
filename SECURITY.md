# Security Policy

## Supported versions

The Python SDK supports the latest published minor release. Security fixes for older releases are best-effort.

| Version | Supported |
|---------|-----------|
| latest 0.x | yes |
| older | no |

## Reporting a vulnerability

Please do **not** open a public GitHub Issue for security findings. Email:

> `therjmurray+browsefleet-sec@gmail.com`

Include a clear description, a reproduction, the SDK version (`pip show browsefleet`), the Python version (`python --version`), and whether you have disclosed elsewhere.

## What to expect

| Stage | Target response |
|-------|-----------------|
| Acknowledgement | within one business day |
| Initial triage | within five business days |
| Public disclosure | coordinated; default 90 days from report or at fix release, whichever is sooner |

## Out of scope

- Bugs in `httpx` or other dependencies that have not been demonstrated to affect this SDK's behavior. File those upstream.
- Misconfigurations on the operator side (running an unauthenticated BrowseFleet server, leaking API keys via client-side code, etc.). The SDK does not validate operator hygiene.
- Reports from automated scanners without manual validation.
