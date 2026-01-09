# ABOUTME: Detailed Python Playwright patterns and examples
# ABOUTME: Extended from SKILL.md core patterns for in-depth reference

# Python Playwright Patterns

## Core Pattern: Synchronous Playwright

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)  # ALWAYS use headless=True
    page = browser.new_page()

    page.goto('http://localhost:3000')
    page.wait_for_load_state('networkidle')  # CRITICAL: Wait for JS to execute

    # ... your automation logic

    browser.close()
```

## Cookie Consent Handling

**CRITICAL**: Many sites display cookie banners that block interaction.

```python
def dismiss_cookie_consent(page, timeout=3000):
    """Dismiss cookie consent banner if present. Non-blocking."""
    cookie_selectors = [
        # Specific consent management platforms
        '[id*="onetrust"] button[id*="accept"]',
        '[class*="onetrust"] button[id*="accept"]',
        '#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll',
        '[data-testid="cookie-policy-dialog-accept-button"]',
        '[data-cookiebanner] button[data-action="accept"]',

        # Generic patterns (text-based)
        'button:has-text("Accept all")',
        'button:has-text("Accept All")',
        'button:has-text("Accept cookies")',
        'button:has-text("Accetta tutti")',
        'button:has-text("Allow all")',
        'button:has-text("I agree")',
        'button:has-text("OK")',

        # Generic patterns (attribute-based)
        '[class*="cookie"] button[class*="accept"]',
        '[class*="consent"] button[class*="accept"]',
        '[id*="cookie"] button[class*="accept"]',
    ]

    for selector in cookie_selectors:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=timeout):
                btn.click()
                page.wait_for_timeout(500)
                return True
        except:
            continue
    return False
```

## Dismiss All Overlays (Nuclear Option)

When cookie consent handling doesn't work:

```python
def dismiss_all_overlays(page):
    """Dismiss cookies AND modals/popups that block interaction."""
    # Cookie consent selectors
    cookie_selectors = [
        'button:has-text("Accept all")', 'button:has-text("Accept All")',
        'button:has-text("Accept cookies")', 'button:has-text("Allow all")',
        'button:has-text("I agree")', 'button:has-text("OK")',
        'button:has-text("Accetta tutti")', 'button:has-text("Accetta")',
        '[class*="cookie"] button[class*="accept"]',
    ]
    for sel in cookie_selectors:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=2000):
                btn.click()
                page.wait_for_timeout(500)
                break
        except:
            continue

    # Remove blocking overlays via JS
    page.evaluate('''() => {
        for (const sel of ['[aria-label="Close"]', '.btn-close', '[data-dismiss="modal"]']) {
            const btn = document.querySelector(sel);
            if (btn && btn.offsetParent !== null) { btn.click(); break; }
        }
        document.querySelectorAll('.modal-backdrop, [class*="overlay"]').forEach(el => {
            if (getComputedStyle(el).position === 'fixed') el.remove();
        });
    }''')


def force_remove_overlay(page, verbose=False):
    """NUCLEAR OPTION: Forcefully remove all blocking overlays."""
    result = page.evaluate('''() => {
        let removed = 0;
        const patterns = ['cookie', 'consent', 'modal', 'overlay', 'popup', 'backdrop', 'gdpr'];
        for (const pattern of patterns) {
            document.querySelectorAll(`[class*="${pattern}"], [id*="${pattern}"]`).forEach(el => {
                const style = getComputedStyle(el);
                if (style.position === 'fixed' || style.position === 'absolute') {
                    el.remove();
                    removed++;
                }
            });
        }
        document.body.style.overflow = 'auto';
        return removed;
    }''')
    if verbose:
        print(f"Removed {result} blocking elements")
    return result
```

## Common Operations

### Screenshots
```python
page.screenshot(path='/tmp/screenshot.png')                    # Viewport only
page.screenshot(path='/tmp/full.png', full_page=True)          # Full page
page.locator('#element').screenshot(path='/tmp/element.png')   # Single element
```

### Form Interactions
```python
page.fill('input[name="email"]', 'test@example.com')
page.select_option('select#country', 'IT')
page.check('input[type="checkbox"]')
page.click('button[type="submit"]')
```

### Waiting Strategies
```python
page.wait_for_load_state('networkidle')           # Wait for network quiet
page.wait_for_selector('.result')                  # Wait for element
page.wait_for_timeout(1000)                        # Fixed wait (avoid if possible)
page.locator('.btn').wait_for(state='visible')     # Wait for visibility
```

### Console Log Capture
```python
page.on('console', lambda msg: print(f'[{msg.type}] {msg.text}'))
page.goto('http://localhost:3000')
```

### Full Debugging Pattern (Console + Network + Errors)
```python
errors = []
requests = []
responses = []

page.on('console', lambda msg: print(f'[CONSOLE {msg.type}] {msg.text}'))
page.on('pageerror', lambda err: errors.append(str(err)))
page.on('request', lambda req: requests.append(f'{req.method} {req.url}'))
page.on('response', lambda res: responses.append(f'{res.status} {res.url}'))

page.goto('http://localhost:3000')
page.fill('#email', 'user@example.com')
page.fill('#password', 'secret')
page.click('button[type="submit"]')
page.wait_for_load_state('networkidle')

print(f"Errors: {errors}")
print(f"Failed requests: {[r for r in responses if '4' in r or '5' in r]}")
```

## Login + Verify Pattern

```python
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Login
    page.goto('http://localhost:3000/login')
    page.wait_for_load_state('networkidle')
    dismiss_cookie_consent(page)  # CRITICAL: Handle cookies first!

    page.fill('input[type="email"]', 'user@example.com')
    page.fill('input[type="password"]', 'password')
    page.click('button[type="submit"]')
    page.wait_for_load_state('networkidle')

    # Navigate and verify
    page.goto('http://localhost:3000/target-page')
    page.wait_for_load_state('networkidle')
    page.screenshot(path='/tmp/verification.png')

    # Check specific element
    dropdown = page.locator('select#my-dropdown')
    print(f"Dropdown value: {dropdown.input_value()}")

    browser.close()
```

## File URLs for Local HTML

```python
import pathlib
html_path = pathlib.Path('/path/to/file.html').resolve()
page.goto(f'file://{html_path}')
```
