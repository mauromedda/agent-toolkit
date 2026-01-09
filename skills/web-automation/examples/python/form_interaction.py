# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
# ABOUTME: Example script for interacting with web forms
# ABOUTME: Demonstrates filling inputs, selecting options, and handling submissions

"""
Form Interaction Example

Demonstrates common form interactions: text input, selects, checkboxes, and submission.
Can run in dry-run mode to only discover fields without filling them.
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


def discover_form_fields(page: Page) -> dict:
    """Discover form fields on the page."""
    fields = {
        "text_inputs": [],
        "selects": [],
        "checkboxes": [],
        "radios": [],
        "textareas": [],
        "submit_buttons": [],
    }

    # Text inputs (including email, password, etc.)
    text_types = ["text", "email", "password", "tel", "number", "url", "search"]
    for input_type in text_types:
        inputs = page.locator(f'input[type="{input_type}"]').all()
        for inp in inputs:
            fields["text_inputs"].append({
                "type": input_type,
                "name": inp.get_attribute("name") or "",
                "id": inp.get_attribute("id") or "",
                "placeholder": inp.get_attribute("placeholder") or "",
                "required": inp.get_attribute("required") is not None,
            })

    # Select dropdowns
    selects = page.locator("select").all()
    for sel in selects:
        options = sel.locator("option").all()
        option_values = [opt.get_attribute("value") for opt in options]
        fields["selects"].append({
            "name": sel.get_attribute("name") or "",
            "id": sel.get_attribute("id") or "",
            "options": option_values,
        })

    # Checkboxes
    checkboxes = page.locator('input[type="checkbox"]').all()
    for cb in checkboxes:
        fields["checkboxes"].append({
            "name": cb.get_attribute("name") or "",
            "id": cb.get_attribute("id") or "",
            "value": cb.get_attribute("value") or "",
            "checked": cb.is_checked(),
        })

    # Radio buttons
    radios = page.locator('input[type="radio"]').all()
    for radio in radios:
        fields["radios"].append({
            "name": radio.get_attribute("name") or "",
            "id": radio.get_attribute("id") or "",
            "value": radio.get_attribute("value") or "",
            "checked": radio.is_checked(),
        })

    # Textareas
    textareas = page.locator("textarea").all()
    for ta in textareas:
        fields["textareas"].append({
            "name": ta.get_attribute("name") or "",
            "id": ta.get_attribute("id") or "",
            "placeholder": ta.get_attribute("placeholder") or "",
        })

    # Submit buttons
    submits = page.locator('button[type="submit"], input[type="submit"]').all()
    for btn in submits:
        text = btn.text_content() or btn.get_attribute("value") or "Submit"
        fields["submit_buttons"].append({
            "text": text.strip(),
            "id": btn.get_attribute("id") or "",
        })

    return fields


def fill_form_example(url: str, dry_run: bool = False, handle_cookies: bool = True) -> None:
    """Demonstrate form filling with discovered fields."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url)
        page.wait_for_load_state("networkidle")

        # Handle cookie consent and other overlays BEFORE interacting
        if handle_cookies:
            dismiss_all_overlays(page)

        print("Discovering form fields...")
        fields = discover_form_fields(page)

        print("\n=== DISCOVERED FIELDS ===")
        for field_type, items in fields.items():
            if items:
                print(f"\n{field_type.upper()}:")
                for item in items:
                    print(f"  - {item}")

        if dry_run:
            print("\n[DRY RUN] Skipping form interaction")
            browser.close()
            return

        # Example: Fill text inputs with sample data
        sample_data = {
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "name": "Test User",
            "username": "testuser",
            "phone": "+1234567890",
            "tel": "+1234567890",
            "message": "This is a test message.",
            "comment": "This is a test comment.",
        }

        print("\n=== FILLING FORM ===")
        for field in fields["text_inputs"]:
            field_name = field["name"].lower() or field["id"].lower()
            for key, value in sample_data.items():
                if key in field_name or field["type"] == key:
                    selector = f'[name="{field["name"]}"]' if field["name"] else f'#{field["id"]}'
                    try:
                        page.fill(selector, value)
                        print(f"  Filled {selector} with {value!r}")
                    except Exception as e:
                        print(f"  Failed to fill {selector}: {e}")
                    break

        # Fill textareas
        for field in fields["textareas"]:
            field_name = field["name"].lower() or field["id"].lower()
            selector = f'[name="{field["name"]}"]' if field["name"] else f'#{field["id"]}'
            for key, value in sample_data.items():
                if key in field_name:
                    try:
                        page.fill(selector, value)
                        print(f"  Filled textarea {selector}")
                    except Exception as e:
                        print(f"  Failed to fill textarea: {e}")
                    break

        # Select first option in dropdowns (if any)
        for field in fields["selects"]:
            if field["options"] and len(field["options"]) > 1:
                selector = f'[name="{field["name"]}"]' if field["name"] else f'#{field["id"]}'
                value = field["options"][1]  # Skip empty first option
                try:
                    page.select_option(selector, value)
                    print(f"  Selected {value!r} in {selector}")
                except Exception as e:
                    print(f"  Failed to select option: {e}")

        # Check unchecked checkboxes (demo)
        for field in fields["checkboxes"]:
            if not field["checked"]:
                selector = f'[name="{field["name"]}"]' if field["name"] else f'#{field["id"]}'
                try:
                    page.check(selector)
                    print(f"  Checked {selector}")
                except Exception as e:
                    print(f"  Failed to check: {e}")

        # Take screenshot of filled form
        page.screenshot(path="/tmp/form_filled.png")
        print("\n  Screenshot saved to /tmp/form_filled.png")

        # Note: Not submitting to avoid side effects
        print("\n[INFO] Form filled but NOT submitted (add page.click() to submit)")

        browser.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Discover and interact with form fields on a web page.",
        epilog="Example: uv run form_interaction.py http://localhost:3000/contact --dry-run",
    )
    parser.add_argument(
        "url",
        help="Target URL with a form (e.g., http://localhost:3000/signup)",
    )
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Only discover fields, do not fill or interact with them",
    )
    parser.add_argument(
        "--discover-only",
        action="store_true",
        help="Alias for --dry-run: only discover fields, do not fill",
    )
    parser.add_argument(
        "--no-cookies",
        action="store_true",
        help="Skip cookie consent and overlay dismissal",
    )

    args = parser.parse_args()

    print(f"Interacting with forms on: {args.url}")
    dry_run = args.dry_run or args.discover_only
    if dry_run:
        print("  (dry-run mode: will only discover, not fill)")

    fill_form_example(args.url, dry_run=dry_run, handle_cookies=not args.no_cookies)


if __name__ == "__main__":
    main()
