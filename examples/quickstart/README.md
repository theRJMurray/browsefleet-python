# Quickstart (Python SDK)

Scrape + screenshot + release.

## Prerequisites

- Python 3.10+
- A BrowseFleet server at `http://localhost:3000` (or set `BROWSEFLEET_URL`)

## Run

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```

## What it does

1. Health check.
2. Scrape `https://example.com`.
3. Take a full-page PNG screenshot, write to `example.png`.
