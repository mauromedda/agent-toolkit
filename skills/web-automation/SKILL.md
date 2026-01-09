---
name: web-automation
description: >-
  Web automation, debugging, and E2E testing with Playwright. Handles interactive
  (login, forms, reproduce bugs) and passive modes (network/console capture).
  Triggers on "e2e test", "browser test", "playwright", "screenshot", "debug UI",
  "debug frontend", "reproduce bug", "network trace", "console output", "verify fix",
  "test that", "verify change", "test the flow", "http://localhost", "open browser",
  "click button", "fill form", "submit form", "check page", "web scraping",
  "automation script", "headless browser", "browser automation", "selenium alternative",
  "puppeteer alternative", "page object", "web testing", "UI testing", "frontend testing",
  "visual regression", "capture network", "intercept requests", "mock API responses".
  PROACTIVE: Invoke for security verification, UI fix verification, testing forms/dropdowns,
  or multi-step UI flows. ON SESSION RESUME - check for pending UI verifications.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# ABOUTME: Claude Code skill for web automation, debugging, and E2E testing using Playwright
# ABOUTME: Covers interactive automation, passive monitoring, screenshots, and security verification

# Web Automation with Playwright

Complete browser automation and debugging using Playwright in **Python** or **JavaScript/TypeScript**.

## 🚨 MUST USE HELPER SCRIPTS FIRST

```
┌─────────────────────────────────────────────────────────────┐
│  BEFORE WRITING ANY PLAYWRIGHT CODE, CHECK THESE HELPERS:   │
│                                                             │
│  Task                          │ Use This Helper            │
│  ─────────────────────────────────────────────────────────  │
│  Login / fill forms            │ examples/python/form_interaction.py │
│  Take screenshots              │ examples/python/screenshot_capture.py │
│  Handle cookie consent         │ scripts/cookie_consent.py  │
│  Discover page elements        │ examples/python/element_discovery.py │
│  Capture network traffic       │ scripts/network_inspector.py │
│  Debug console errors          │ scripts/console_debugger.py │
│  Full debug (network+console)  │ scripts/combined_debugger.py │
│                                                             │
│  ❌ DO NOT write inline Playwright code                     │
│  ✅ DO use: uv run ~/.claude/skills/web-automation/...      │
└─────────────────────────────────────────────────────────────┘
```

**Quick start pattern:**
```bash
# Step 1: Check what's on the page
uv run ~/.claude/skills/web-automation/examples/python/element_discovery.py http://localhost:3000

# Step 2: Fill forms (handles cookies automatically)
uv run ~/.claude/skills/web-automation/examples/python/form_interaction.py http://localhost:3000 --discover-only

# Step 3: Take screenshots for verification
uv run ~/.claude/skills/web-automation/examples/python/screenshot_capture.py http://localhost:3000 --output /tmp/shots
```

## Modes of Operation

| Mode | When to Use | Example |
|------|-------------|---------|
| **Interactive** | Need to click, type, navigate | Login flow, form submission, reproduce bugs |
| **Passive** | Observe only, no interaction | Network capture, console monitoring, security verify |
| **E2E Testing** | Automated test suites | Playwright Test framework |

## When to Invoke This Skill (Proactive)

**ALWAYS invoke this skill when:**

1. **Verifying UI fixes** - After changing frontend code, use this to confirm the fix works
2. **Testing form fields/dropdowns** - Verify correct values display in selects, inputs
3. **Confirming visual changes** - Take screenshots to verify UI updates
4. **Reproducing bugs** - Automate the steps to reproduce an issue
5. **Security verification** - After Gemini/static analysis finds issues, verify in browser

**Common patterns that should trigger this skill:**
- "Test that the dropdown shows..."
- "Verify the fix works"
- "Check that the form displays..."
- "Test the login flow"
- "Take a screenshot of..."

**DO NOT manually write Playwright scripts** - use the helper scripts in this skill first!

## 🔄 RESUMED SESSION CHECKPOINT

**When a session is resumed from context compaction, verify web automation state:**

```
┌─────────────────────────────────────────────────────────────┐
│  SESSION RESUMED - WEB AUTOMATION VERIFICATION              │
│                                                             │
│  Before continuing ANY work, answer:                        │
│                                                             │
│  1. Was I in the middle of browser automation?              │
│     → Check for running browser instances or servers        │
│     → Run: ps aux | grep -E "chromium|playwright|node"      │
│                                                             │
│  2. Were there UI verification tasks pending?               │
│     → Check summary for "verify", "test UI", "screenshot"   │
│                                                             │
│  3. Did previous automation capture any findings?           │
│     → Check /tmp/ for screenshots, debug outputs            │
│     → Read any captured console/network logs                │
│                                                             │
│  If automation was in progress:                             │
│  → Re-run the verification step before continuing           │
│  → Do NOT assume previous results are still valid           │
└─────────────────────────────────────────────────────────────┘
```

## CRITICAL: Handling Overlays (Cookie Consent, Modals, Popups)

**Overlays WILL block your automation.** All helper scripts now auto-dismiss overlays, but if writing custom scripts:

```python
# ALWAYS call this after page.goto() and wait_for_load_state()
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
        // Click close buttons
        for (const sel of ['[aria-label="Close"]', '.btn-close', '[data-dismiss="modal"]']) {
            const btn = document.querySelector(sel);
            if (btn && btn.offsetParent !== null) { btn.click(); break; }
        }
        // Remove overlay backdrops
        document.querySelectorAll('.modal-backdrop, [class*="overlay"]').forEach(el => {
            if (getComputedStyle(el).position === 'fixed') el.remove();
        });
    }''')

# Usage pattern - EVERY script should follow this:
page.goto('https://example.com')
page.wait_for_load_state('networkidle')
dismiss_all_overlays(page)  # <-- CRITICAL: Always call this!
# Now safe to interact...
```

**If overlays still block:** Use the NUCLEAR OPTION to forcefully remove them:
```python
from scripts.cookie_consent import force_remove_overlay

# NUCLEAR OPTION: Remove all blocking overlays via JavaScript
removed = force_remove_overlay(page, verbose=True)
print(f"Removed {removed} blocking elements")
```

Or inline if not importing:
```python
# Forcefully remove blocking overlays
page.evaluate('''() => {
    const patterns = ['cookie', 'consent', 'modal', 'overlay', 'popup', 'backdrop', 'gdpr'];
    for (const pattern of patterns) {
        document.querySelectorAll(`[class*="${pattern}"], [id*="${pattern}"]`).forEach(el => {
            const style = getComputedStyle(el);
            if (style.position === 'fixed' || style.position === 'absolute') {
                el.remove();
            }
        });
    }
    document.body.style.overflow = 'auto';
}''')
```

**Last resort: interact via JavaScript** (bypasses all overlays):
```python
# Fill form via JavaScript if clicks are still blocked
page.evaluate('''(value) => {
    document.querySelector('input[name="email"]').value = value;
    document.querySelector('input[name="email"]').dispatchEvent(new Event('input', {bubbles: true}));
}''', 'test@example.com')
```

## Quick Decision Flow

```
Task:
    |
    +-- Need to interact? (click, type, submit)
    |       |
    |       +-- YES → Interactive mode (full debugging pattern)
    |
    +-- Just observe/capture?
    |       |
    |       +-- YES → Passive mode (scripts/combined_debugger.py)
    |
    +-- Security verification after Gemini/static analysis?
            |
            +-- YES → Passive mode + grep for sensitive patterns
```

## Quick Verification Workflow (After Code Changes)

**Use this when verifying a fix works or testing UI changes.**

### Verify Form/Dropdown Displays Correctly

```bash
# 1. Discover form elements
uv run ~/.claude/skills/web-automation/examples/python/form_interaction.py \
    http://localhost:3000/edit-page \
    --discover-only

# 2. Or take a screenshot for visual verification
uv run ~/.claude/skills/web-automation/examples/python/screenshot_capture.py \
    http://localhost:3000/edit-page \
    --output /tmp/verify
```

### Login + Verify Pattern

For pages requiring authentication:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
from playwright.sync_api import sync_playwright

# Import the cookie consent handler from skill docs
def dismiss_cookie_consent(page, timeout=3000):
    """ALWAYS call after page.goto() - see full implementation in skill docs."""
    selectors = [
        'button:has-text("Accept All")',
        'button:has-text("Accept all")',
        '[class*="cookie"] button[class*="accept"]',
    ]
    for sel in selectors:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=timeout):
                btn.click()
                page.wait_for_timeout(500)
                return True
        except:
            continue
    return False

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

### Common Verification Checklist

| What to Verify | Approach |
|----------------|----------|
| Dropdown shows correct value | `page.locator('select').input_value()` |
| Input has expected text | `page.locator('input').input_value()` |
| Element is visible | `page.locator('.element').is_visible()` |
| Text content correct | `page.locator('.element').text_content()` |
| Page redirected correctly | `page.url` after action |

## Passive Mode & Security Verification

### Passive Debugging Scripts

Use these scripts when you need to observe without interacting:

| Script | Purpose | Location |
|--------|---------|----------|
| `combined_debugger.py` | Network + Console + Errors together | `scripts/combined_debugger.py` |
| `network_inspector.py` | Network requests only | `scripts/network_inspector.py` |
| `console_debugger.py` | Console/errors only | `scripts/console_debugger.py` |

**Quick start (passive capture):**
```bash
uv run ~/.claude/skills/web-automation/scripts/combined_debugger.py \
    http://localhost:3000 \
    --duration 30 \
    --output /tmp/debug.json
```

### Security Verification Workflow

**PROACTIVE**: When Gemini or static analysis identifies security issues, verify in live browser:

```bash
# After Gemini found: "Sensitive data logging in api.service.ts:186"
uv run ~/.claude/skills/web-automation/scripts/console_debugger.py \
    http://localhost:3000 \
    --duration 60 \
    --output /tmp/security_console.json

# Search for sensitive patterns
grep -i "password\|token\|secret\|bearer" /tmp/security_console.json
```

**Why this matters:**
- Static analysis shows **potential** issues
- Browser verification provides **concrete evidence**
- Helps prioritize: is the vulnerable code actually executed?

### Common Passive Debugging Scenarios

| Scenario | Script | Flags |
|----------|--------|-------|
| API failures | `network_inspector.py` | `--errors-only` |
| CORS issues | `network_inspector.py` | `--filter xhr,fetch` |
| JavaScript exceptions | `console_debugger.py` | `--errors-only --with-stack-traces` |
| Full picture (unknown issue) | `combined_debugger.py` | default |
| Security verification | `console_debugger.py` | `--duration 60` |

## Language Selection

| Use Case | Recommended | Reason |
|----------|-------------|--------|
| Existing JS/TS project | JavaScript | Consistent tooling |
| Existing Python project | Python | Consistent tooling |
| Quick scripts | Python | Simpler setup with `uv run` |
| Test suites | JavaScript | Better `@playwright/test` framework |
| CI/CD integration | Either | Both work well |

## CRITICAL: Using Helper Scripts

**ALWAYS run scripts with `--help` first** to see usage. DO NOT read the script source code to guess parameters.

```bash
# Python examples (use uv run)
uv run ~/.claude/skills/web-automation/scripts/server_utils.py --help
uv run ~/.claude/skills/web-automation/examples/python/element_discovery.py --help

# JavaScript examples (use node or npx)
node ~/.claude/skills/web-automation/examples/js/element_discovery.js --help
```

These scripts are designed as black-box tools. See "Help Output Examples" section below for what to expect.

## Prerequisites

### Python
All example scripts include **inline dependencies** (PEP 723), so `uv run` auto-installs them:

```bash
# Dependencies installed automatically when running
uv run ~/.claude/skills/web-automation/examples/python/element_discovery.py --help
```

### JavaScript/TypeScript
For new projects, initialize with:

```bash
npm init -y
npm install -D @playwright/test
npx playwright install chromium
```

**One-time setup**: Playwright requires browser binaries:
```bash
# Install Chromium browser (required once per machine)
npx playwright install chromium
# Or install all browsers
npx playwright install
```

## Decision Tree: Choosing Your Approach

```
User task --> Is it static HTML?
    |
    +-- Yes --> Read HTML file directly to identify selectors
    |           |
    |           +-- Success --> Write Playwright script using selectors
    |           +-- Fails/Incomplete --> Treat as dynamic (below)
    |
    +-- No (dynamic webapp) --> Is the server already running?
        |
        +-- No --> Detect project type --> Start appropriate server
        |
        +-- Yes --> Reconnaissance-then-action:
            1. Navigate and wait for networkidle
            2. Take screenshot or inspect DOM
            3. Identify selectors from rendered state
            4. Execute actions with discovered selectors
```

## Server Detection and Startup

Before running Playwright scripts, detect the project type and start the appropriate dev server.

### Detection Strategy

Check for these files in the repository root to determine project type:

| File | Project Type | Common Dev Servers |
|------|--------------|-------------------|
| `hugo.toml` / `config.toml` | Hugo | hugo server |
| `package.json` | Node.js | npm/yarn/pnpm |
| `pyproject.toml` | Python (modern) | uvicorn, flask, django |
| `requirements.txt` | Python (legacy) | same as above |
| `Cargo.toml` | Rust | cargo run |
| `go.mod` | Go | go run |
| `Gemfile` | Ruby | rails server, puma |
| `composer.json` | PHP | php artisan serve |

**Note**: Hugo is detected first since Hugo projects often include `package.json` for asset pipelines.

### Server Startup Pattern

Use the helper script `scripts/server_utils.py` to detect and manage servers:

```bash
# First, check available options
uv run ~/.claude/skills/web-automation/scripts/server_utils.py --help

# Detect project type only
uv run ~/.claude/skills/web-automation/scripts/server_utils.py /path/to/repo --detect-only

# Detect and start server
uv run ~/.claude/skills/web-automation/scripts/server_utils.py /path/to/repo --start
```

---

# Python Patterns

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

## Cookie Consent Handling (Python)

**CRITICAL**: Many sites display cookie banners that block interaction. Handle them immediately after page load.

```python
def dismiss_cookie_consent(page, timeout=3000):
    """Dismiss cookie consent banner if present. Non-blocking."""
    # Common cookie consent selectors (ordered by specificity)
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
        'button:has-text("Accept Cookies")',
        'button:has-text("Accetta tutti")',
        'button:has-text("Accetta")',
        'button:has-text("Allow all")',
        'button:has-text("Allow All")',
        'button:has-text("I agree")',
        'button:has-text("Agree")',
        'button:has-text("Got it")',
        'button:has-text("OK")',

        # Generic patterns (attribute-based)
        '[class*="cookie"] button[class*="accept"]',
        '[class*="cookie"] button[class*="agree"]',
        '[class*="consent"] button[class*="accept"]',
        '[class*="consent"] button[class*="agree"]',
        '[id*="cookie"] button[class*="accept"]',
        '[aria-label*="cookie" i] button',
        '[aria-label*="consent" i] button',
    ]

    for selector in cookie_selectors:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=timeout):
                btn.click()
                page.wait_for_timeout(500)  # Brief pause for banner to close
                return True
        except:
            continue
    return False

# Usage in your automation
page.goto('https://example.com')
page.wait_for_load_state('networkidle')
dismiss_cookie_consent(page)  # Always call after navigation
# ... continue with your automation
```

### Integration Pattern

```python
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto('https://example.com')
    page.wait_for_load_state('networkidle')

    # ALWAYS handle cookies after initial load
    dismiss_cookie_consent(page)

    # Now safe to interact with the page
    page.click('button.main-action')
```

## Reconnaissance-Then-Action Pattern (Python)

**Step 1: Inspect the rendered DOM**
```python
page.screenshot(path='/tmp/inspect.png', full_page=True)
content = page.content()
buttons = page.locator('button').all()
```

**Step 2: Identify selectors from inspection results**

**Step 3: Execute actions using discovered selectors**

## Common Operations (Python)

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
# Capture everything while interacting with the app
errors = []
requests = []
responses = []

page.on('console', lambda msg: print(f'[CONSOLE {msg.type}] {msg.text}'))
page.on('pageerror', lambda err: errors.append(str(err)))
page.on('request', lambda req: requests.append(f'{req.method} {req.url}'))
page.on('response', lambda res: responses.append(f'{res.status} {res.url}'))

# Now interact - all events are captured in the SAME browser
page.goto('http://localhost:3000')
page.fill('#email', 'user@example.com')
page.fill('#password', 'secret')
page.click('button[type="submit"]')
page.wait_for_load_state('networkidle')

# Analyze what happened
print(f"Errors: {errors}")
print(f"Failed requests: {[r for r in responses if '4' in r or '5' in r]}")
```

---

# JavaScript/TypeScript Patterns

## Core Pattern: @playwright/test Framework

```javascript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should do something', async ({ page }) => {
    await expect(page.locator('.element')).toBeVisible();
    await page.click('button');
    await expect(page.locator('.result')).toContainText('Success');
  });
});
```

## Cookie Consent Handling (JavaScript)

**CRITICAL**: Many sites display cookie banners that block interaction. Handle them immediately after page load.

```javascript
async function dismissCookieConsent(page, timeout = 3000) {
  /** Dismiss cookie consent banner if present. Non-blocking. */
  const cookieSelectors = [
    // Specific consent management platforms
    '[id*="onetrust"] button[id*="accept"]',
    '[class*="onetrust"] button[id*="accept"]',
    '#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll',
    '[data-testid="cookie-policy-dialog-accept-button"]',
    '[data-cookiebanner] button[data-action="accept"]',

    // Generic patterns (text-based)
    'button:has-text("Accept all")',
    'button:has-text("Accept All")',
    'button:has-text("Accept cookies")',
    'button:has-text("Accept Cookies")',
    'button:has-text("Accetta tutti")',
    'button:has-text("Accetta")',
    'button:has-text("Allow all")',
    'button:has-text("Allow All")',
    'button:has-text("I agree")',
    'button:has-text("Agree")',
    'button:has-text("Got it")',
    'button:has-text("OK")',

    // Generic patterns (attribute-based)
    '[class*="cookie"] button[class*="accept"]',
    '[class*="cookie"] button[class*="agree"]',
    '[class*="consent"] button[class*="accept"]',
    '[class*="consent"] button[class*="agree"]',
    '[id*="cookie"] button[class*="accept"]',
    '[aria-label*="cookie" i] button',
    '[aria-label*="consent" i] button',
  ];

  for (const selector of cookieSelectors) {
    try {
      const btn = page.locator(selector).first();
      if (await btn.isVisible({ timeout })) {
        await btn.click();
        await page.waitForTimeout(500); // Brief pause for banner to close
        return true;
      }
    } catch {
      continue;
    }
  }
  return false;
}

// Usage in your automation
await page.goto('https://example.com');
await page.waitForLoadState('networkidle');
await dismissCookieConsent(page); // Always call after navigation
// ... continue with your automation
```

### NUCLEAR OPTION: Force Remove Overlay (JavaScript)

When `dismissCookieConsent()` doesn't work and overlays still block clicks:

```javascript
async function forceRemoveOverlay(page) {
  /** NUCLEAR OPTION: Forcefully remove all blocking overlays via JavaScript. */
  const result = await page.evaluate(() => {
    let removed = 0;
    const patterns = ['cookie', 'consent', 'gdpr', 'privacy', 'modal', 'overlay', 'popup', 'backdrop', 'banner'];

    for (const pattern of patterns) {
      document.querySelectorAll(`[class*="${pattern}"], [id*="${pattern}"]`).forEach(el => {
        const style = getComputedStyle(el);
        if (style.position === 'fixed' || style.position === 'absolute') {
          el.remove();
          removed++;
        }
      });
    }

    // Reset body overflow (often locked when modals are open)
    document.body.style.overflow = 'auto';
    document.documentElement.style.overflow = 'auto';

    return removed;
  });
  return result;
}

// Usage
await page.goto('https://example.com');
await page.waitForLoadState('networkidle');
await dismissCookieConsent(page);  // Try gentle approach first
const removed = await forceRemoveOverlay(page);  // Nuclear option if still blocked
console.log(`Removed ${removed} blocking elements`);
```

### Integration with Playwright Test

```javascript
import { test, expect } from '@playwright/test';

// Define as a test fixture or helper
async function dismissCookieConsent(page) {
  // ... same implementation as above
}

test.describe('Feature with Cookie Handling', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await dismissCookieConsent(page); // Handle cookies in beforeEach
  });

  test('should interact without cookie banner blocking', async ({ page }) => {
    await page.click('button.main-action'); // Safe to interact
  });
});
```

## Reconnaissance-Then-Action Pattern (JavaScript)

**Step 1: Inspect the rendered DOM**
```javascript
await page.screenshot({ path: '/tmp/inspect.png', fullPage: true });
const content = await page.content();
const buttons = await page.locator('button').all();
```

**Step 2: Identify selectors from inspection results**

**Step 3: Execute actions using discovered selectors**

## Common Operations (JavaScript)

### Screenshots
```javascript
await page.screenshot({ path: '/tmp/screenshot.png' });                    // Viewport only
await page.screenshot({ path: '/tmp/full.png', fullPage: true });          // Full page
await page.locator('#element').screenshot({ path: '/tmp/element.png' });   // Single element
```

### Form Interactions
```javascript
await page.fill('input[name="email"]', 'test@example.com');
await page.selectOption('select#country', 'IT');
await page.check('input[type="checkbox"]');
await page.click('button[type="submit"]');
```

### Waiting Strategies
```javascript
await page.waitForLoadState('networkidle');           // Wait for network quiet
await page.waitForSelector('.result');                 // Wait for element
await page.waitForTimeout(1000);                       // Fixed wait (avoid if possible)
await page.locator('.btn').waitFor({ state: 'visible' }); // Wait for visibility
```

### Console Log Capture
```javascript
page.on('console', msg => console.log(`[${msg.type()}] ${msg.text()}`));
await page.goto('http://localhost:3000');
```

### Full Debugging Pattern (Console + Network + Errors)
```javascript
// Capture everything while interacting with the app
const errors = [];
const requests = [];
const responses = [];

page.on('console', msg => console.log(`[CONSOLE ${msg.type()}] ${msg.text()}`));
page.on('pageerror', err => errors.push(err.message));
page.on('request', req => requests.push(`${req.method()} ${req.url()}`));
page.on('response', res => responses.push(`${res.status()} ${res.url()}`));

// Now interact - all events are captured in the SAME browser
await page.goto('http://localhost:3000');
await page.fill('#email', 'user@example.com');
await page.fill('#password', 'secret');
await page.click('button[type="submit"]');
await page.waitForLoadState('networkidle');

// Analyze what happened
console.log('Errors:', errors);
console.log('Failed requests:', responses.filter(r => r.startsWith('4') || r.startsWith('5')));
```

### Assertions (Playwright Test)
```javascript
await expect(page.locator('.element')).toBeVisible();
await expect(page.locator('.element')).toHaveText('Expected Text');
await expect(page.locator('.element')).toContainText('partial');
await expect(page.locator('.element')).toHaveCount(3);
await expect(page.locator('input')).toHaveValue('expected value');
await expect(page.locator('input')).toBeFocused();
await expect(page).toHaveURL('/expected-path');
await expect(page).toHaveTitle('Expected Title');
```

---

# Selector Strategies (Both Languages)

Order of preference:

1. **Role-based** (most resilient):
   - Python: `page.get_by_role('button', name='Submit')`
   - JS: `page.getByRole('button', { name: 'Submit' })`

2. **Text-based**:
   - Python: `page.get_by_text('Click me')`
   - JS: `page.getByText('Click me')`

3. **Test IDs**:
   - Python: `page.get_by_test_id('submit-btn')`
   - JS: `page.getByTestId('submit-btn')`

4. **CSS selectors**:
   - Both: `page.locator('.btn-primary')`

5. **XPath** (last resort):
   - Both: `page.locator('//button[@type="submit"]')`

---

# Test Suite Patterns (JavaScript)

## Project Structure

```
project/
├── tests/
│   └── e2e/
│       ├── homepage.spec.js
│       ├── navigation.spec.js
│       └── forms.spec.js
├── playwright.config.js
└── package.json
```

## Playwright Config (playwright.config.js)

```javascript
// ABOUTME: Playwright configuration for E2E tests
// ABOUTME: Configures browsers, base URL, and web server

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'npm run dev',  // Adjust for your project
    url: 'http://localhost:3000',
    reuseExistingServer: true,
  },
});
```

## Test Patterns

### Page Object Pattern (Recommended for complex UIs)

```javascript
// tests/e2e/pages/TerminalPage.js
export class TerminalPage {
  constructor(page) {
    this.page = page;
    this.input = page.locator('#input');
    this.output = page.locator('.output');
  }

  async goto() {
    await this.page.goto('/');
    await this.page.waitForLoadState('networkidle');
  }

  async runCommand(cmd) {
    await this.input.fill(cmd);
    await this.input.press('Enter');
  }

  async expectOutput(text) {
    await expect(this.output).toContainText(text);
  }
}

// tests/e2e/terminal.spec.js
import { TerminalPage } from './pages/TerminalPage.js';

test('help command shows sections', async ({ page }) => {
  const terminal = new TerminalPage(page);
  await terminal.goto();
  await terminal.runCommand('help');
  await terminal.expectOutput('Navigation:');
});
```

### Data-Driven Tests

```javascript
const commands = [
  { cmd: 'help', expected: 'Navigation:' },
  { cmd: 'pwd', expected: '/home/guest' },
  { cmd: 'date', expected: new Date().getFullYear().toString() },
];

for (const { cmd, expected } of commands) {
  test(`${cmd} command works`, async ({ page }) => {
    await page.goto('/');
    await page.fill('#input', cmd);
    await page.press('#input', 'Enter');
    await expect(page.locator('.output')).toContainText(expected);
  });
}
```

### Async Sequences (for animations/delays)

```javascript
test('boot sequence completes', async ({ page }) => {
  await page.goto('/');

  // Wait for sequence steps
  await expect(page.locator('.output')).toContainText('initializing terminal...');
  await expect(page.locator('.ascii')).toBeVisible({ timeout: 5000 });
  await expect(page.locator('.tagline')).toContainText('builder. founder. dad.');
});
```

---

# Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| **Overlay blocking clicks** | **CRITICAL**: Call `dismiss_all_overlays(page)` after EVERY page load |
| Cookie banner blocking clicks | Helper scripts auto-handle this; for custom scripts use `dismiss_all_overlays()` |
| **Overlay STILL blocking** | **NUCLEAR OPTION**: Use `force_remove_overlay(page)` to remove overlay DOM elements |
| Modal/popup blocking form | Use JavaScript fallback: `page.evaluate()` to set values directly |
| DOM inspection before JS loads | Always `wait_for_load_state('networkidle')` first |
| Headful browser in CI/server | Always use `headless: true` |
| Forgetting to close browser | Use context managers (Python) or Playwright Test (JS) |
| Flaky selectors | Prefer role/text selectors over CSS classes |
| Race conditions | Use explicit waits, not `wait_for_timeout` |
| Hardcoded waits | Use `toBeVisible({ timeout: X })` assertions |

## File URLs for Local HTML

### Python
```python
import pathlib
html_path = pathlib.Path('/path/to/file.html').resolve()
page.goto(f'file://{html_path}')
```

### JavaScript
```javascript
import path from 'path';
const htmlPath = path.resolve('/path/to/file.html');
await page.goto(`file://${htmlPath}`);
```

---

# Helper Scripts

## scripts/ (Server & Test Management)

| Script | Purpose |
|--------|---------|
| `server_utils.py` | Auto-detect project type and manage dev server lifecycle |
| `test_utils.py` | Detect test frameworks, run tests with optional server startup |

## examples/python/ (Python Playwright)

| Script | Purpose |
|--------|---------|
| `element_discovery.py` | Discover buttons, links, inputs, forms on a page |
| `screenshot_capture.py` | Capture viewport, full-page, and responsive screenshots |
| `console_logging.py` | Capture console logs and monitor network activity |
| `form_interaction.py` | Discover and fill form fields |
| `visual_compare.py` | Compare two websites visually and extract CSS differences |

## examples/js/ (JavaScript Playwright)

| Script | Purpose |
|--------|---------|
| `element_discovery.js` | Discover buttons, links, inputs, forms on a page |
| `screenshot_capture.js` | Capture viewport, full-page, and responsive screenshots |
| `console_logging.js` | Capture console logs and monitor network activity |

**Usage Pattern** (always run `--help` first):

### Python
```bash
uv run ~/.claude/skills/web-automation/examples/python/element_discovery.py http://localhost:3000
uv run ~/.claude/skills/web-automation/examples/python/screenshot_capture.py http://localhost:3000 --output /tmp/shots
```

### JavaScript
```bash
node ~/.claude/skills/web-automation/examples/js/element_discovery.js http://localhost:3000
node ~/.claude/skills/web-automation/examples/js/screenshot_capture.js http://localhost:3000 --output /tmp/shots
```

---

# Visual Comparison Pattern

**CRITICAL**: When asked to compare websites visually or match designs, NEVER say "I cannot visually browse". Instead:

1. **Take screenshots** using `screenshot_capture` scripts or `visual_compare.py`
2. **Read the screenshots** using the Read tool (Claude can see images)
3. **Extract CSS properties** programmatically for precise comparison
4. **Provide specific recommendations** based on actual visual differences

```bash
# Compare two sites and get CSS diff (Python)
uv run ~/.claude/skills/web-automation/examples/python/visual_compare.py \
    https://reference-site.com \
    http://localhost:3000 \
    --output /tmp/compare

# Then read the screenshots to visually analyze
# Read /tmp/compare/site1_desktop.png
# Read /tmp/compare/site2_desktop.png
```

---

# Output Locations

Screenshots and artifacts should be saved to `/tmp/` by default for easy cleanup.

---

# Test Workflow

## Unified Test Runner

Use `test_utils.py` to detect frameworks and run tests in any project:

```bash
# First, check available options
uv run ~/.claude/skills/web-automation/scripts/test_utils.py --help

# Detect test frameworks only
uv run ~/.claude/skills/web-automation/scripts/test_utils.py /path/to/repo --detect-only

# Run all detected tests
uv run ~/.claude/skills/web-automation/scripts/test_utils.py /path/to/repo --run

# Run tests with server auto-start (for E2E)
uv run ~/.claude/skills/web-automation/scripts/test_utils.py /path/to/repo --run --with-server

# Run specific framework only
uv run ~/.claude/skills/web-automation/scripts/test_utils.py /path/to/repo --run --framework playwright
uv run ~/.claude/skills/web-automation/scripts/test_utils.py /path/to/repo --run --framework jest

# Filter tests by name pattern
uv run ~/.claude/skills/web-automation/scripts/test_utils.py /path/to/repo --run --filter "login"
```

## Supported Test Frameworks

| Framework | Language | Detection |
|-----------|----------|-----------|
| Playwright | JS/TS | `@playwright/test` in package.json, playwright.config.js |
| Jest | JS/TS | `jest` in package.json, jest.config.js |
| Vitest | JS/TS | `vitest` in package.json |
| Mocha | JS/TS | `mocha` in package.json |
| Cypress | JS/TS | `cypress` in package.json |
| pytest | Python | `pytest` in requirements.txt/pyproject.toml, conftest.py |
| unittest | Python | test/ or tests/ directory |

## Server Auto-Start

When using `--with-server`, the script:

1. Detects the project type (Hugo, Node.js, Python)
2. Starts the appropriate dev server in background
3. Waits for server to be ready
4. Runs tests
5. Stops the server automatically

| Project Type | Server Command | Port |
|--------------|----------------|------|
| Hugo | `hugo server -D` | 1313 |
| Node.js (Next) | `npm run dev` | 3000 |
| Node.js (Vite) | `npm run dev` | 5173 |
| Python (FastAPI) | `uvicorn main:app` | 8000 |
| Python (Flask) | `flask run` | 5000 |
| Python (Django) | `python manage.py runserver` | 8000 |

## Typical Workflow

```bash
# 1. Detect what's available
uv run ~/.claude/skills/web-automation/scripts/test_utils.py . --detect-only

# 2. Run E2E tests with server
uv run ~/.claude/skills/web-automation/scripts/test_utils.py . --run --with-server --framework playwright

# 3. Run unit tests (no server needed)
uv run ~/.claude/skills/web-automation/scripts/test_utils.py . --run --framework jest
```

---

## Help Output Examples

### server_utils.py

```
usage: server_utils.py [-h] [--detect-only] [--start] repo_path

Detect project type and manage dev server lifecycle

positional arguments:
  repo_path             Path to the repository to analyze (e.g., . or /path/to/project)

options:
  -h, --help            show this help message and exit
  --detect-only, -d     Only detect project type, do not start server
  --start, -s           Start the detected dev server and stream output

Examples:
  uv run server_utils.py /path/to/project --detect-only
  uv run server_utils.py . --start
```

Output shows:
```
=== PROJECT DETECTION ===
  Type: nodejs
  Framework: next
  Start command: npm run dev
  Port: 3000
  URL: http://localhost:3000
  Package manager: npm
  Working directory: /path/to/project
```

### element_discovery.py (Python)

```
usage: element_discovery.py [-h] [--headless] [--output OUTPUT] url

Discover buttons, links, inputs, forms on a page

positional arguments:
  url                   URL to inspect (e.g., http://localhost:3000)

options:
  -h, --help            show this help message and exit
  --headless            Run in headless mode (default: True)
  --output OUTPUT, -o OUTPUT
                        Save output to JSON file

Examples:
  uv run element_discovery.py http://localhost:3000
  uv run element_discovery.py http://localhost:3000 --output /tmp/elements.json
```

### test_utils.py

```
usage: test_utils.py [-h] [--detect-only] [--run] [--with-server]
                     [--framework FRAMEWORK] [--filter FILTER]
                     repo_path

Detect and run tests in any project

positional arguments:
  repo_path             Path to the repository

options:
  -h, --help            show this help message and exit
  --detect-only         Only detect test frameworks
  --run                 Run all detected tests
  --with-server         Start dev server before running tests
  --framework FRAMEWORK Only run specific framework (playwright, jest, pytest, etc.)
  --filter FILTER       Filter tests by name pattern

Examples:
  uv run test_utils.py . --detect-only
  uv run test_utils.py . --run --with-server --framework playwright
  uv run test_utils.py . --run --filter "login"
```

---

# Running E2E Tests

### JavaScript (Playwright Test)
```bash
# Run all tests
npx playwright test

# Run specific file
npx playwright test tests/e2e/terminal.spec.js

# Run with UI mode (debugging)
npx playwright test --ui

# Run headed (see browser)
npx playwright test --headed

# Generate report
npx playwright show-report
```

### Python (pytest-playwright)
```bash
# Install
pip install pytest-playwright

# Run tests
pytest tests/
```
