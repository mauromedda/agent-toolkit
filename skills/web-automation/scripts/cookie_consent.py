# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
# ABOUTME: Reusable cookie consent dismissal for Playwright automation
# ABOUTME: Import dismiss_cookie_consent() in any script to handle cookie banners

"""
Cookie Consent Handler for Playwright

Usage:
    from cookie_consent import dismiss_cookie_consent

    page.goto('https://example.com')
    page.wait_for_load_state('networkidle')
    dismiss_cookie_consent(page)  # ALWAYS call after navigation
"""

from playwright.sync_api import Page


# Comprehensive list of cookie consent selectors, ordered by specificity
COOKIE_SELECTORS = [
    # Specific consent management platforms (most reliable)
    '[id*="onetrust"] button[id*="accept"]',
    '[class*="onetrust"] button[id*="accept"]',
    '#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll',
    '[data-testid="cookie-policy-dialog-accept-button"]',
    '[data-cookiebanner] button[data-action="accept"]',
    '#gdpr-cookie-accept',
    '.cc-accept-all',
    '.cc-allow',
    '[data-consent="accept"]',
    '#cookie-accept',
    '#accept-cookies',
    '.accept-cookies',
    '#acceptAllCookies',
    '.acceptAllCookies',

    # Generic patterns (text-based) - English
    'button:has-text("Accept all")',
    'button:has-text("Accept All")',
    'button:has-text("Accept cookies")',
    'button:has-text("Accept Cookies")',
    'button:has-text("Allow all")',
    'button:has-text("Allow All")',
    'button:has-text("Allow cookies")',
    'button:has-text("I agree")',
    'button:has-text("I Accept")',
    'button:has-text("Agree")',
    'button:has-text("Got it")',
    'button:has-text("OK")',
    'button:has-text("Continue")',

    # Generic patterns (text-based) - Italian
    'button:has-text("Accetta tutti")',
    'button:has-text("Accetta tutto")',
    'button:has-text("Accetta")',
    'button:has-text("Accetto")',
    'button:has-text("Consenti")',
    'button:has-text("Consenti tutti")',

    # Generic patterns (text-based) - German
    'button:has-text("Alle akzeptieren")',
    'button:has-text("Akzeptieren")',
    'button:has-text("Zustimmen")',

    # Generic patterns (text-based) - French
    'button:has-text("Accepter tout")',
    'button:has-text("Accepter")',
    'button:has-text("J\'accepte")',

    # Generic patterns (text-based) - Spanish
    'button:has-text("Aceptar todo")',
    'button:has-text("Aceptar")',

    # Generic patterns (attribute-based)
    '[class*="cookie"] button[class*="accept"]',
    '[class*="cookie"] button[class*="agree"]',
    '[class*="cookie"] button[class*="allow"]',
    '[class*="consent"] button[class*="accept"]',
    '[class*="consent"] button[class*="agree"]',
    '[class*="consent"] button[class*="allow"]',
    '[id*="cookie"] button[class*="accept"]',
    '[id*="consent"] button[class*="accept"]',
    '[aria-label*="cookie" i] button',
    '[aria-label*="consent" i] button',
    '[role="dialog"] button[class*="accept"]',
    '[role="dialog"] button[class*="agree"]',

    # Fallback: any prominent button in cookie-related containers
    '[class*="cookie-banner"] button:first-of-type',
    '[class*="cookie-notice"] button:first-of-type',
    '[class*="cookie-popup"] button:first-of-type',
    '[class*="gdpr"] button:first-of-type',
]


def dismiss_cookie_consent(page: Page, timeout: int = 3000, verbose: bool = False) -> bool:
    """
    Dismiss cookie consent banner if present. Non-blocking.

    Args:
        page: Playwright Page object
        timeout: How long to wait for each selector (ms)
        verbose: Print debug info

    Returns:
        True if a cookie banner was dismissed, False otherwise

    Usage:
        page.goto('https://example.com')
        page.wait_for_load_state('networkidle')
        dismiss_cookie_consent(page)  # ALWAYS call after navigation
    """
    for selector in COOKIE_SELECTORS:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=timeout):
                if verbose:
                    print(f"[COOKIE] Found and clicking: {selector}")
                btn.click()
                page.wait_for_timeout(500)  # Brief pause for banner to close
                return True
        except Exception:
            continue

    if verbose:
        print("[COOKIE] No cookie consent banner found")
    return False


def dismiss_cookie_consent_js(page: Page, verbose: bool = False) -> bool:
    """
    Alternative: Dismiss cookie consent using JavaScript injection.
    Use this if the CSS selector approach fails.

    This approach clicks buttons containing accept-related text.
    """
    result = page.evaluate('''() => {
        const acceptTexts = [
            'accept all', 'accept cookies', 'allow all', 'allow cookies',
            'i agree', 'agree', 'got it', 'ok', 'continue',
            'accetta', 'accetto', 'consenti',
            'akzeptieren', 'zustimmen',
            'accepter', "j'accepte",
            'aceptar'
        ];

        const buttons = document.querySelectorAll('button, [role="button"], a.button');
        for (const btn of buttons) {
            const text = btn.textContent?.toLowerCase().trim() || '';
            for (const acceptText of acceptTexts) {
                if (text.includes(acceptText)) {
                    btn.click();
                    return { found: true, text: btn.textContent };
                }
            }
        }
        return { found: false };
    }''')

    if verbose:
        if result.get('found'):
            print(f"[COOKIE-JS] Clicked button with text: {result.get('text')}")
        else:
            print("[COOKIE-JS] No cookie consent button found")

    return result.get('found', False)


def dismiss_all_overlays(page: Page, verbose: bool = False) -> None:
    """
    Dismiss cookie consent AND other blocking overlays (modals, popups, dialogs).

    Call this after page load to ensure no overlays block interaction.

    Args:
        page: Playwright Page object
        verbose: Print debug info

    Usage:
        page.goto('https://example.com')
        page.wait_for_load_state('networkidle')
        dismiss_all_overlays(page)  # Clears cookies AND other overlays
    """
    # First: cookie consent
    dismiss_cookie_consent(page, verbose=verbose)

    # Second: dismiss other common overlays via JavaScript
    page.evaluate('''() => {
        // Close any modal/dialog overlays by clicking close buttons
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
            '[data-testid="close-button"]',
            '[data-testid="modal-close"]',
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
            '[class*="backdrop"]',
        ];

        for (const sel of overlaySelectors) {
            const overlays = document.querySelectorAll(sel);
            overlays.forEach(el => {
                const style = window.getComputedStyle(el);
                if (style.position === 'fixed' || style.position === 'absolute') {
                    el.remove();
                }
            });
        }
    }''')
    page.wait_for_timeout(300)

    if verbose:
        print("[OVERLAY] Dismissed all overlays")


def force_remove_overlay(page: Page, verbose: bool = False) -> int:
    """
    NUCLEAR OPTION: Forcefully remove all blocking overlays via JavaScript.

    Use this when dismiss_all_overlays() doesn't work and clicks are still blocked.
    This directly removes DOM elements that cover the page.

    Args:
        page: Playwright Page object
        verbose: Print debug info

    Returns:
        Number of elements removed

    Usage:
        page.goto('https://example.com')
        page.wait_for_load_state('networkidle')
        dismiss_all_overlays(page)  # Try gentle approach first
        # If still blocked:
        removed = force_remove_overlay(page)
        print(f"Removed {removed} blocking elements")
    """
    result = page.evaluate('''() => {
        let removed = 0;
        const removedElements = [];

        // 1. Remove elements by common overlay/modal class patterns
        const classPatterns = [
            'cookie', 'consent', 'gdpr', 'privacy', 'notice', 'banner',
            'modal', 'overlay', 'popup', 'dialog', 'backdrop', 'mask',
            'notification', 'alert-overlay', 'blocker'
        ];

        for (const pattern of classPatterns) {
            // Match class names containing the pattern
            const elements = document.querySelectorAll(`[class*="${pattern}"]`);
            for (const el of elements) {
                const style = window.getComputedStyle(el);
                // Only remove fixed/absolute positioned elements that cover significant area
                if (style.position === 'fixed' || style.position === 'absolute') {
                    const rect = el.getBoundingClientRect();
                    // Check if element covers significant viewport area or is near top/bottom
                    const coversViewport = rect.width > window.innerWidth * 0.3 ||
                                          rect.height > window.innerHeight * 0.2;
                    const isEdgeBanner = rect.top <= 100 || rect.bottom >= window.innerHeight - 100;

                    if (coversViewport || isEdgeBanner) {
                        removedElements.push({
                            tag: el.tagName,
                            class: el.className,
                            id: el.id
                        });
                        el.remove();
                        removed++;
                    }
                }
            }
        }

        // 2. Remove elements by ID patterns
        const idPatterns = [
            'cookie', 'consent', 'gdpr', 'privacy', 'modal', 'overlay', 'popup'
        ];

        for (const pattern of idPatterns) {
            const elements = document.querySelectorAll(`[id*="${pattern}"]`);
            for (const el of elements) {
                const style = window.getComputedStyle(el);
                if (style.position === 'fixed' || style.position === 'absolute') {
                    if (!removedElements.some(r => r.id === el.id)) {
                        removedElements.push({
                            tag: el.tagName,
                            class: el.className,
                            id: el.id
                        });
                        el.remove();
                        removed++;
                    }
                }
            }
        }

        // 3. Remove any remaining full-screen fixed elements with high z-index
        const fixedElements = document.querySelectorAll('*');
        for (const el of fixedElements) {
            const style = window.getComputedStyle(el);
            if (style.position === 'fixed') {
                const zIndex = parseInt(style.zIndex) || 0;
                const rect = el.getBoundingClientRect();
                // High z-index AND covers most of viewport
                if (zIndex > 100 &&
                    rect.width > window.innerWidth * 0.5 &&
                    rect.height > window.innerHeight * 0.5) {
                    removedElements.push({
                        tag: el.tagName,
                        class: el.className,
                        id: el.id,
                        zIndex: zIndex
                    });
                    el.remove();
                    removed++;
                }
            }
        }

        // 4. Reset body overflow (often set to 'hidden' when modals are open)
        document.body.style.overflow = 'auto';
        document.documentElement.style.overflow = 'auto';

        return { removed, elements: removedElements };
    }''')

    if verbose:
        print(f"[FORCE-REMOVE] Removed {result['removed']} blocking elements:")
        for el in result.get('elements', []):
            print(f"  - <{el['tag']}> class='{el.get('class', '')}' id='{el.get('id', '')}'")

    return result['removed']


def set_cookie_consent_storage(page: Page, verbose: bool = False) -> None:
    """
    Set common localStorage/cookie values that indicate consent was given.
    Call BEFORE navigating to the page to prevent banner from appearing.

    Usage:
        page.goto('https://example.com')  # Initial load to set context
        set_cookie_consent_storage(page)
        page.reload()  # Reload with consent set
    """
    page.evaluate('''() => {
        // Common localStorage keys
        const consentKeys = [
            'cookie-consent', 'cookieConsent', 'cookies-accepted',
            'gdpr-consent', 'gdprConsent', 'privacy-consent',
            'CookieConsent', 'cookie_consent', 'cookies_accepted'
        ];

        for (const key of consentKeys) {
            localStorage.setItem(key, 'accepted');
            localStorage.setItem(key, 'true');
            localStorage.setItem(key, '1');
        }

        // Set cookies too
        document.cookie = 'cookie-consent=accepted; path=/; max-age=31536000';
        document.cookie = 'gdpr-consent=accepted; path=/; max-age=31536000';
    }''')

    if verbose:
        print("[COOKIE] Set consent in localStorage and cookies")


if __name__ == "__main__":
    # Demo/test
    from playwright.sync_api import sync_playwright

    print("Cookie Consent Handler - Demo")
    print("=" * 40)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Test with a site that has cookie consent
        test_url = "https://www.google.com"
        print(f"\nTesting with: {test_url}")

        page.goto(test_url)
        page.wait_for_load_state('networkidle')

        dismissed = dismiss_cookie_consent(page, verbose=True)
        print(f"Cookie banner dismissed: {dismissed}")

        browser.close()

    print("\nDone!")
