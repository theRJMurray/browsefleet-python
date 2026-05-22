# Operator mode (Python SDK)

Profile + operator-mode session + human-to-agent handoff via `sessions.control()`.

## Run

```bash
pip install -r requirements.txt
python main.py
```

## What it does

1. Creates a persistent profile.
2. Starts an operator-mode session attached to the profile (begins in `human` control).
3. Prints the live viewer URL.
4. Waits for you to type `done` in the terminal.
5. Switches control to `agent` via `sessions.control(...)`.
6. Issues a small action batch as proof the gate is open.
7. Releases the session.
