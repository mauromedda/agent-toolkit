# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
# ABOUTME: Visual comparison tool for comparing two websites side by side
# ABOUTME: Takes screenshots and extracts CSS properties for analysis

"""
Visual Compare - Website Comparison Tool

Captures screenshots of two URLs and extracts key CSS properties
for visual comparison analysis. Useful for matching designs.

Usage:
    uv run visual_compare.py URL1 URL2 --output /tmp/compare
"""

import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright


def extract_css_properties(page) -> dict:
    """Extract key CSS properties from the page."""
    return page.evaluate("""
        () => {
            const body = document.body;
            const computedStyle = window.getComputedStyle(body);

            // Get first heading if exists
            const h1 = document.querySelector('h1');
            const h1Style = h1 ? window.getComputedStyle(h1) : null;

            // Get links
            const link = document.querySelector('a');
            const linkStyle = link ? window.getComputedStyle(link) : null;

            // Get main content container
            const main = document.querySelector('main, .main, #main, [role="main"]');
            const mainStyle = main ? window.getComputedStyle(main) : null;

            return {
                body: {
                    fontFamily: computedStyle.fontFamily,
                    fontSize: computedStyle.fontSize,
                    lineHeight: computedStyle.lineHeight,
                    color: computedStyle.color,
                    backgroundColor: computedStyle.backgroundColor,
                    letterSpacing: computedStyle.letterSpacing,
                },
                h1: h1Style ? {
                    fontFamily: h1Style.fontFamily,
                    fontSize: h1Style.fontSize,
                    fontWeight: h1Style.fontWeight,
                    color: h1Style.color,
                } : null,
                links: linkStyle ? {
                    color: linkStyle.color,
                    textDecoration: linkStyle.textDecoration,
                } : null,
                container: mainStyle ? {
                    maxWidth: mainStyle.maxWidth,
                    padding: mainStyle.padding,
                    margin: mainStyle.margin,
                } : null,
                viewport: {
                    width: window.innerWidth,
                    height: window.innerHeight,
                }
            };
        }
    """)


def compare_sites(url1: str, url2: str, output_dir: str = "/tmp/compare") -> dict:
    """Compare two websites visually and extract CSS properties."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results = {"url1": url1, "url2": url2, "sites": {}}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for i, url in enumerate([url1, url2], 1):
            site_key = f"site{i}"
            page = browser.new_page()
            page.set_viewport_size({"width": 1920, "height": 1080})

            try:
                page.goto(url, timeout=30000)
                page.wait_for_load_state("networkidle")
            except Exception as e:
                print(f"Warning: {url} - {e}")
                page.wait_for_timeout(2000)

            # Take screenshots
            screenshot_path = output_path / f"site{i}_desktop.png"
            page.screenshot(path=str(screenshot_path))
            print(f"Saved: {screenshot_path}")

            # Full page
            fullpage_path = output_path / f"site{i}_fullpage.png"
            page.screenshot(path=str(fullpage_path), full_page=True)
            print(f"Saved: {fullpage_path}")

            # Extract CSS
            css_props = extract_css_properties(page)
            results["sites"][site_key] = {
                "url": url,
                "css": css_props,
                "screenshots": {
                    "desktop": str(screenshot_path),
                    "fullpage": str(fullpage_path),
                }
            }

            page.close()

        browser.close()

    # Save comparison results
    results_path = output_path / "comparison.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nComparison data saved: {results_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("CSS COMPARISON SUMMARY")
    print("=" * 60)

    site1 = results["sites"]["site1"]["css"]
    site2 = results["sites"]["site2"]["css"]

    print(f"\n{'Property':<25} {'Site 1':<30} {'Site 2':<30}")
    print("-" * 85)

    for category in ["body", "h1", "links"]:
        if site1.get(category) and site2.get(category):
            print(f"\n[{category.upper()}]")
            for prop in site1[category]:
                val1 = site1[category].get(prop, "N/A")
                val2 = site2[category].get(prop, "N/A") if site2.get(category) else "N/A"
                # Truncate long values
                val1_str = str(val1)[:28] if val1 else "N/A"
                val2_str = str(val2)[:28] if val2 else "N/A"
                match = "✓" if val1 == val2 else "✗"
                print(f"  {prop:<23} {val1_str:<30} {val2_str:<30} {match}")

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare two websites visually and extract CSS properties.",
        epilog="Example: uv run visual_compare.py https://example.com http://localhost:3000",
    )
    parser.add_argument("url1", help="First URL to compare (reference)")
    parser.add_argument("url2", help="Second URL to compare (target)")
    parser.add_argument(
        "--output", "-o",
        default="/tmp/compare",
        help="Output directory for screenshots and data (default: /tmp/compare)",
    )

    args = parser.parse_args()

    print(f"Comparing:")
    print(f"  Reference: {args.url1}")
    print(f"  Target:    {args.url2}")
    print(f"  Output:    {args.output}")
    print()

    compare_sites(args.url1, args.url2, args.output)


if __name__ == "__main__":
    main()
