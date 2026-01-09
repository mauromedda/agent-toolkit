# ABOUTME: Detailed JavaScript/TypeScript Playwright patterns and examples
# ABOUTME: Extended from SKILL.md core patterns for in-depth reference

# JavaScript Playwright Patterns

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

## Cookie Consent Handling

```javascript
async function dismissCookieConsent(page, timeout = 3000) {
  const cookieSelectors = [
    '[id*="onetrust"] button[id*="accept"]',
    '#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll',
    'button:has-text("Accept all")',
    'button:has-text("Accept All")',
    'button:has-text("Accetta tutti")',
    'button:has-text("Allow all")',
    'button:has-text("I agree")',
    'button:has-text("OK")',
    '[class*="cookie"] button[class*="accept"]',
    '[class*="consent"] button[class*="accept"]',
  ];

  for (const selector of cookieSelectors) {
    try {
      const btn = page.locator(selector).first();
      if (await btn.isVisible({ timeout })) {
        await btn.click();
        await page.waitForTimeout(500);
        return true;
      }
    } catch {
      continue;
    }
  }
  return false;
}
```

## Nuclear Option: Force Remove Overlay

```javascript
async function forceRemoveOverlay(page) {
  const result = await page.evaluate(() => {
    let removed = 0;
    const patterns = ['cookie', 'consent', 'gdpr', 'modal', 'overlay', 'popup', 'backdrop'];

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
    document.documentElement.style.overflow = 'auto';
    return removed;
  });
  return result;
}
```

## Common Operations

### Screenshots
```javascript
await page.screenshot({ path: '/tmp/screenshot.png' });
await page.screenshot({ path: '/tmp/full.png', fullPage: true });
await page.locator('#element').screenshot({ path: '/tmp/element.png' });
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
await page.waitForLoadState('networkidle');
await page.waitForSelector('.result');
await page.waitForTimeout(1000);  // Avoid if possible
await page.locator('.btn').waitFor({ state: 'visible' });
```

### Full Debugging Pattern
```javascript
const errors = [];
const requests = [];
const responses = [];

page.on('console', msg => console.log(`[CONSOLE ${msg.type()}] ${msg.text()}`));
page.on('pageerror', err => errors.push(err.message));
page.on('request', req => requests.push(`${req.method()} ${req.url()}`));
page.on('response', res => responses.push(`${res.status()} ${res.url()}`));

await page.goto('http://localhost:3000');
await page.fill('#email', 'user@example.com');
await page.click('button[type="submit"]');
await page.waitForLoadState('networkidle');

console.log('Errors:', errors);
console.log('Failed:', responses.filter(r => r.startsWith('4') || r.startsWith('5')));
```

### Assertions
```javascript
await expect(page.locator('.element')).toBeVisible();
await expect(page.locator('.element')).toHaveText('Expected Text');
await expect(page.locator('.element')).toContainText('partial');
await expect(page.locator('.element')).toHaveCount(3);
await expect(page.locator('input')).toHaveValue('expected value');
await expect(page).toHaveURL('/expected-path');
await expect(page).toHaveTitle('Expected Title');
```

## Test Suite Patterns

### Project Structure
```
project/
├── tests/e2e/
│   ├── homepage.spec.js
│   └── forms.spec.js
├── playwright.config.js
└── package.json
```

### Playwright Config
```javascript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: true,
  },
});
```

### Page Object Pattern
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
}

// Usage
test('help command works', async ({ page }) => {
  const terminal = new TerminalPage(page);
  await terminal.goto();
  await terminal.runCommand('help');
  await expect(terminal.output).toContainText('Navigation:');
});
```

### Data-Driven Tests
```javascript
const commands = [
  { cmd: 'help', expected: 'Navigation:' },
  { cmd: 'pwd', expected: '/home/guest' },
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

## File URLs for Local HTML

```javascript
import path from 'path';
const htmlPath = path.resolve('/path/to/file.html');
await page.goto(`file://${htmlPath}`);
```

## Running Tests

```bash
npx playwright test                              # Run all
npx playwright test tests/e2e/terminal.spec.js  # Specific file
npx playwright test --ui                         # UI mode
npx playwright test --headed                     # See browser
npx playwright show-report                       # View report
```
