"""BrowseFleet Python SDK quickstart."""

from __future__ import annotations

from browsefleet import BrowseFleet


def main() -> int:
    with BrowseFleet() as bf:
        print("Step 1: Health check")
        health = bf.health()
        print(f"  {health}")

        print("\nStep 2: Scrape https://example.com")
        page = bf.scrape("https://example.com")
        print(f"  Title: {page.title}")
        print(f"  Status: {page.status_code}")
        print(f"  Markdown (first 200 chars): {page.markdown[:200]}...")

        print("\nStep 3: Screenshot to example.png")
        png = bf.screenshot("https://example.com", format="png", full_page=True)
        with open("example.png", "wb") as fh:
            fh.write(png)
        print(f"  Wrote example.png ({len(png)} bytes)")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
