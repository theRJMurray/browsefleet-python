"""Operator-mode + human-to-agent handoff using the Python SDK."""

from __future__ import annotations

from browsefleet import BrowseFleet


def main() -> int:
    with BrowseFleet() as bf:
        print("Step 1: Create a persistent profile")
        profile = bf.profiles.create(name="operator-mode-py-example")
        print(f"  Profile id: {profile.id}")

        print("\nStep 2: Start an operator-mode session attached to the profile")
        session = bf.sessions.create(
            profile_id=profile.id,
            operator_mode=True,
            stealth="full",
        )
        print(f"  Session id: {session.id}")
        print(f"  Control mode: {session.control_mode}")
        print(f"  Live viewer: {session.viewer_url}")
        print(f"  Event stream: {session.events_url}")

        print(
            "\nStep 3: Drive the browser as a human through the live viewer.\n"
            '       Type "done" here to hand off to the agent.\n'
        )
        while True:
            line = input("> ").strip().lower()
            if line == "done":
                break
            print('  (type "done" to continue)')

        print("\nStep 4: Hand off to the agent")
        updated = bf.sessions.control(
            session.id,
            control_mode="agent",
            reason="operator finished",
        )
        print(f"  Control mode is now: {updated.control_mode}")

        print("\nStep 5: Run a small action batch as proof the gate is open")
        result = bf.sessions.actions(
            session.id,
            [
                {"type": "navigate", "url": "https://example.com"},
                {"type": "screenshot"},
            ],
        )
        print(f"  Actions executed: {len(result.results)}")

        print("\nStep 6: Release the session (profile persists)")
        bf.sessions.release(session.id)
        print("  Released.")
        print(
            f"\nNext time, create a session with profile_id={profile.id!r} "
            "and skip the human step."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
