# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
# ABOUTME: Example script for capturing browser screenshots
# ABOUTME: Demonstrates viewport, full-page, and element-specific screenshots

"""
Screenshot Capture Example

Captures various types of screenshots from a web page:
- Viewport (visible area)
- Full page (scrolled content)
- Element-specific (header, main, footer)
- Responsive (mobile, tablet, desktop)
"""

import argparse
from pathlib import Path
from playwright.sync_api import Page, sync_playwright


# Cookie consent selectors - comprehensive list
COOKIE_SELECTORS = [
    '[id*="onetrust"] button[id*="accept"]',
    '#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll',
    '[data-testid="cookie-policy-dialog-accept-button"]',
    'button:has-text("Accept all")',
    'button:has-text("Accept All")',
    'button:has-text("Accept cookies")',
    'button:has-text("Allow all")',
    'button:has-text("I agree")',
    'button:has-text("Agree")',
    'button:has-text("Got it")',
    'button:has-text("OK")',
    'button:has-text("Accetta tutti")',
    'button:has-text("Accetta")',
    '[class*="cookie"] button[class*="accept"]',
    '[class*="consent"] button[class*="accept"]',
]


def dismiss_cookie_consent(page: Page, timeout: int = 2000) -> bool:
    """Dismiss cookie consent banner if present."""
    for selector in COOKIE_SELECTORS:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=timeout):
                print(f"  [COOKIE] Dismissing cookie consent...")
                btn.click()
                page.wait_for_timeout(500)
                return True
        except Exception:
            continue
    return False


def dismiss_all_overlays(page: Page) -> None:
    """Dismiss cookie consent AND other blocking overlays (modals, popups)."""
    dismiss_cookie_consent(page)

    # Dismiss other common overlays via JavaScript
    page.evaluate('''() => {
        const closeSelectors = [
            '[aria-label="Close"]', '[aria-label="close"]',
            'button[class*="close"]', 'button[class*="dismiss"]',
            '.modal-close', '.popup-close', '.overlay-close',
            '[data-dismiss="modal"]', '.btn-close',
        ];
        for (const sel of closeSelectors) {
            const btn = document.querySelector(sel);
            if (btn && btn.offsetParent !== null) { btn.click(); break; }
        }
        // Remove blocking overlays
        document.querySelectorAll('.modal-backdrop, [class*="overlay"]').forEach(el => {
            if (el.style.position === 'fixed' || el.style.position === 'absolute') el.remove();
        });
    }''')
    page.wait_for_timeout(300)


def capture_screenshots(url: str, output_dir: str = "/tmp", handle_cookies: bool = True) -> list[str]:
    """Capture multiple types of screenshots and return file paths."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    saved_files = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url)
        page.wait_for_load_state("networkidle")

        # Handle cookie consent and other overlays
        if handle_cookies:
            dismiss_all_overlays(page)

        # Viewport screenshot (what's visible)
        viewport_path = output_path / "viewport.png"
        page.screenshot(path=str(viewport_path))
        saved_files.append(str(viewport_path))
        print(f"Saved viewport screenshot: {viewport_path}")

        # Full page screenshot (scrolled content)
        fullpage_path = output_path / "fullpage.png"
        page.screenshot(path=str(fullpage_path), full_page=True)
        saved_files.append(str(fullpage_path))
        print(f"Saved full-page screenshot: {fullpage_path}")

        # Try to capture specific elements
        element_selectors = [
            ("header", "header, [role='banner'], nav"),
            ("main", "main, [role='main'], #content, .content"),
            ("footer", "footer, [role='contentinfo']"),
        ]

        for name, selector in element_selectors:
            try:
                element = page.locator(selector).first
                if element.is_visible():
                    element_path = output_path / f"element_{name}.png"
                    element.screenshot(path=str(element_path))
                    saved_files.append(str(element_path))
                    print(f"Saved {name} element screenshot: {element_path}")
            except Exception as e:
                print(f"Could not capture {name}: {e}")

        # Capture with different viewport sizes (responsive testing)
        viewports = [
            ("mobile", 375, 667),
            ("tablet", 768, 1024),
            ("desktop", 1920, 1080),
        ]

        for name, width, height in viewports:
            page.set_viewport_size({"width": width, "height": height})
            page.wait_for_load_state("networkidle")

            responsive_path = output_path / f"responsive_{name}.png"
            page.screenshot(path=str(responsive_path))
            saved_files.append(str(responsive_path))
            print(f"Saved {name} ({width}x{height}) screenshot: {responsive_path}")

        browser.close()

    return saved_files


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Capture screenshots from a web page (viewport, full-page, responsive).",
        epilog="Example: uv run screenshot_capture.py http://localhost:3000 --output /tmp/shots",
    )
    parser.add_argument(
        "url",
        help="Target URL to screenshot (e.g., http://localhost:3000)",
    )
    parser.add_argument(
        "--output", "-o",
        default="/tmp",
        help="Output directory for screenshots (default: /tmp)",
    )
    parser.add_argument(
        "--no-cookies",
        action="store_true",
        help="Skip cookie consent and overlay dismissal",
    )

    args = parser.parse_args()

    print(f"Capturing screenshots from: {args.url}")
    print(f"Output directory: {args.output}")

    files = capture_screenshots(args.url, args.output, handle_cookies=not args.no_cookies)

    print(f"\nTotal screenshots captured: {len(files)}")
    print("Files:")
    for f in files:
        print(f"  - {f}")


if __name__ == "__main__":
    main()
