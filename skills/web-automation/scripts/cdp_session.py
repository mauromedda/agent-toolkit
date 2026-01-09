# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
# ABOUTME: Core CDP session management for Chrome DevTools debugging
# ABOUTME: Provides reusable utilities for browser launch and CDP domain management

"""
CDP Session Manager

Core utilities for Chrome DevTools Protocol interactions via Playwright.
This module is imported by other debugging scripts.

Usage as library:
    from cdp_session import create_browser_and_page, enable_domains

Usage standalone (test connection):
    uv run cdp_session.py http://localhost:3000 --domains Network,Runtime
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from playwright.async_api import async_playwright

if TYPE_CHECKING:
    from playwright.async_api import Browser, CDPSession, Page


async def create_browser_and_page(
    headless: bool = True,
) -> tuple["Browser", "Page"]:
    """
    Launch Chromium and create a new page.

    Args:
        headless: Run browser in headless mode (default: True)

    Returns:
        Tuple of (browser, page)
    """
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=headless)
    context = await browser.new_context()
    page = await context.new_page()
    return browser, page


async def create_cdp_session(page: "Page") -> "CDPSession":
    """
    Create a CDP session from a Playwright page.

    Args:
        page: Playwright page object

    Returns:
        CDPSession for direct CDP commands
    """
    return await page.context.new_cdp_session(page)


async def enable_domains(client: "CDPSession", domains: list[str]) -> None:
    """
    Enable multiple CDP domains.

    Args:
        client: CDP session
        domains: List of domain names (e.g., ["Network", "Runtime"])
    """
    for domain in domains:
        await client.send(f"{domain}.enable")


async def disable_domains(client: "CDPSession", domains: list[str]) -> None:
    """
    Disable multiple CDP domains.

    Args:
        client: CDP session
        domains: List of domain names
    """
    for domain in domains:
        try:
            await client.send(f"{domain}.disable")
        except Exception:
            pass  # Some domains may not support disable


def create_metadata(url: str, duration: float) -> dict:
    """
    Create standard metadata block for output.

    Args:
        url: Target URL
        duration: Capture duration in seconds

    Returns:
        Metadata dictionary
    """
    return {
        "url": url,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": duration,
        "browser": "Chromium",
    }


def output_json(data: dict, output_file: str | None = None) -> None:
    """
    Output JSON to file or stdout.

    Args:
        data: Dictionary to serialize
        output_file: Optional file path; if None, prints to stdout
    """
    json_str = json.dumps(data, indent=2, default=str)
    if output_file:
        with open(output_file, "w") as f:
            f.write(json_str)
        print(f"Output written to: {output_file}", file=sys.stderr)
    else:
        print(json_str)


async def test_connection(url: str, domains: list[str]) -> dict:
    """
    Test CDP connection and domain availability.

    Args:
        url: URL to navigate to
        domains: Domains to test

    Returns:
        Test results dictionary
    """
    results = {"url": url, "domains": {}, "success": True}

    browser, page = await create_browser_and_page()
    try:
        client = await create_cdp_session(page)

        for domain in domains:
            try:
                await client.send(f"{domain}.enable")
                results["domains"][domain] = "enabled"
            except Exception as e:
                results["domains"][domain] = f"error: {e}"
                results["success"] = False

        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        results["navigation"] = "success"

    except Exception as e:
        results["navigation"] = f"error: {e}"
        results["success"] = False
    finally:
        await browser.close()

    return results


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Test CDP connection and domain availability",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    uv run cdp_session.py http://localhost:3000
    uv run cdp_session.py http://localhost:3000 --domains Network,Runtime,Log
        """,
    )
    parser.add_argument("url", help="URL to test connection against")
    parser.add_argument(
        "--domains",
        default="Network,Runtime",
        help="Comma-separated CDP domains to test (default: Network,Runtime)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: stdout)",
    )

    args = parser.parse_args()
    domains = [d.strip() for d in args.domains.split(",")]

    results = await test_connection(args.url, domains)
    output_json(results, args.output)

    sys.exit(0 if results["success"] else 1)


if __name__ == "__main__":
    asyncio.run(main())
