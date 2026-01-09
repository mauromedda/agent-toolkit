# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
# ABOUTME: Example script for discovering interactive elements on a web page
# ABOUTME: Demonstrates locator patterns for buttons, links, inputs, and forms

"""
Element Discovery Example

Discovers and lists interactive elements on a web page.
Useful for reconnaissance before writing automation scripts.
"""

import argparse
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
    # First: cookie consent
    dismiss_cookie_consent(page)

    # Second: dismiss other common overlays via JavaScript
    page.evaluate('''() => {
        // Close any modal/dialog overlays
        const closeSelectors = [
            '[aria-label="Close"]',
            '[aria-label="close"]',
            'button[class*="close"]',
            'button[class*="dismiss"]',
            '.modal-close',
            '.popup-close',
            '.overlay-close',
            '[data-dismiss="modal"]',
            '.btn-close',
            'button svg[class*="close"]',
        ];

        for (const sel of closeSelectors) {
            const btn = document.querySelector(sel);
            if (btn && btn.offsetParent !== null) {
                btn.click();
                break;
            }
        }

        // Remove overlay elements that block interaction
        const overlaySelectors = [
            '.modal-backdrop',
            '.overlay',
            '[class*="overlay"]',
            '[class*="modal-overlay"]',
            '[class*="popup-overlay"]',
        ];

        for (const sel of overlaySelectors) {
            const overlays = document.querySelectorAll(sel);
            overlays.forEach(el => {
                if (el.style.position === 'fixed' || el.style.position === 'absolute') {
                    el.remove();
                }
            });
        }
    }''')
    page.wait_for_timeout(300)


def discover_elements(url: str, handle_cookies: bool = True) -> dict:
    """Discover interactive elements on a page and return their details."""
    results = {
        "buttons": [],
        "links": [],
        "inputs": [],
        "forms": [],
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url)
        page.wait_for_load_state("networkidle")

        # Handle cookie consent and other overlays
        if handle_cookies:
            dismiss_all_overlays(page)

        # Discover buttons
        buttons = page.locator("button").all()
        for btn in buttons:
            text = btn.text_content() or ""
            btn_type = btn.get_attribute("type") or "button"
            btn_id = btn.get_attribute("id") or ""
            results["buttons"].append({
                "text": text.strip(),
                "type": btn_type,
                "id": btn_id,
            })

        # Discover links
        links = page.locator("a").all()
        for link in links:
            text = link.text_content() or ""
            href = link.get_attribute("href") or ""
            results["links"].append({
                "text": text.strip(),
                "href": href,
            })

        # Discover inputs
        inputs = page.locator("input, textarea, select").all()
        for inp in inputs:
            inp_type = inp.get_attribute("type") or "text"
            inp_name = inp.get_attribute("name") or ""
            inp_id = inp.get_attribute("id") or ""
            inp_placeholder = inp.get_attribute("placeholder") or ""
            results["inputs"].append({
                "type": inp_type,
                "name": inp_name,
                "id": inp_id,
                "placeholder": inp_placeholder,
            })

        # Discover forms
        forms = page.locator("form").all()
        for form in forms:
            form_id = form.get_attribute("id") or ""
            form_action = form.get_attribute("action") or ""
            form_method = form.get_attribute("method") or "get"
            results["forms"].append({
                "id": form_id,
                "action": form_action,
                "method": form_method,
            })

        browser.close()

    return results


def print_results(results: dict) -> None:
    """Print discovered elements in a readable format."""
    print("\n=== BUTTONS ===")
    for btn in results["buttons"]:
        print(f"  [{btn['type']}] {btn['text']!r} (id={btn['id']!r})")

    print("\n=== LINKS ===")
    for link in results["links"]:
        print(f"  {link['text']!r} -> {link['href']}")

    print("\n=== INPUTS ===")
    for inp in results["inputs"]:
        selector = f"name={inp['name']!r}" if inp["name"] else f"id={inp['id']!r}"
        print(f"  [{inp['type']}] {selector} placeholder={inp['placeholder']!r}")

    print("\n=== FORMS ===")
    for form in results["forms"]:
        print(f"  {form['method'].upper()} -> {form['action']} (id={form['id']!r})")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Discover interactive elements (buttons, links, inputs, forms) on a web page.",
        epilog="Example: uv run element_discovery.py http://localhost:3000",
    )
    parser.add_argument(
        "url",
        help="Target URL to analyze (e.g., http://localhost:3000 or file:///path/to/file.html)",
    )
    parser.add_argument(
        "--no-cookies",
        action="store_true",
        help="Skip cookie consent and overlay dismissal",
    )

    args = parser.parse_args()

    print(f"Discovering elements on: {args.url}")

    discovered = discover_elements(args.url, handle_cookies=not args.no_cookies)
    print_results(discovered)

    total = sum(len(v) for v in discovered.values())
    print(f"\nTotal elements discovered: {total}")


if __name__ == "__main__":
    main()
