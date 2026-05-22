# Examples

Runnable example projects for the `browsefleet` Python SDK.

| Example | Demonstrates |
|---------|--------------|
| [`quickstart/`](./quickstart/) | Scrape, screenshot, release. The 5-line snippet expanded to a real script. |
| [`agent_task/`](./agent_task/) | Vision-based agent task end-to-end. Requires `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` on the server. |
| [`operator_mode/`](./operator_mode/) | Profile + operator-mode session + human-to-agent handoff via `sessions.control()`. |
| [`async_client/`](./async_client/) | The same flows on `AsyncBrowseFleet`. |

## Running an example

Every example assumes a BrowseFleet server is running at `http://localhost:3000`. Start one from the [server repo](https://github.com/theRJMurray/browsefleet):

```bash
docker run -p 3000:3000 --shm-size=2g ghcr.io/therjmurray/browsefleet:latest
```

Then:

```bash
cd examples/<name>
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```

Each example takes the same env vars: `BROWSEFLEET_URL` (default `http://localhost:3000`) and `BROWSEFLEET_API_KEY` (optional).

Examples consume the local SDK via `-e ../..` until first PyPI publish; after publish you can switch them to `browsefleet>=0.2`.
