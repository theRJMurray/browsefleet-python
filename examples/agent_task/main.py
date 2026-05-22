"""BrowseFleet agent task example."""

from __future__ import annotations

from browsefleet import BrowseFleet


def main() -> int:
    with BrowseFleet() as bf:
        print("Sending agent task to BrowseFleet...")
        result = bf.agent.run(
            task=(
                "Read the H1 heading on this page and report its text. "
                "When done, return the H1 text as the final result."
            ),
            url="https://example.com",
            provider="anthropic",
            max_iterations=5,
        )

        print("\nDone.")
        print(f"  Success: {result.success}")
        print(f"  Iterations: {result.total_iterations}")
        print(f"  Result: {result.result or '(no result)'}")
        if result.error:
            print(f"  Error: {result.error}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
