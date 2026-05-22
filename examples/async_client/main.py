"""BrowseFleet async client example."""

from __future__ import annotations

import asyncio

from browsefleet import AsyncBrowseFleet


async def main() -> int:
    async with AsyncBrowseFleet() as bf:
        print("Step 1: Health check")
        health = await bf.health()
        print(f"  {health}")

        print("\nStep 2: Scrape https://example.com (async)")
        page = await bf.scrape("https://example.com")
        print(f"  Title: {page.title}")
        print(f"  Markdown (first 120 chars): {page.markdown[:120]}...")

        print("\nStep 3: Screenshot to example.png")
        png = await bf.screenshot("https://example.com", format="png", full_page=True)
        with open("example.png", "wb") as fh:
            fh.write(png)
        print(f"  Wrote example.png ({len(png)} bytes)")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
