#!/usr/bin/env node
// ABOUTME: Example script for capturing browser console logs
// ABOUTME: Demonstrates log filtering, error detection, and network monitoring

/**
 * Console Logging Example
 *
 * Captures and filters browser console messages and network activity.
 * Useful for debugging JavaScript issues and monitoring API calls.
 *
 * Usage: node console_logging.js <url> [--errors-only] [--network]
 */

const { chromium } = require('playwright');

async function captureLogs(url, options = {}) {
  const { errorsOnly = false, captureNetwork = false } = options;

  const capture = {
    consoleLogs: [],
    networkRequests: [],
    networkResponses: [],
    errors: [],
  };

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  // Attach console listener
  page.on('console', msg => {
    const logEntry = {
      type: msg.type(),
      text: msg.text(),
      location: msg.location(),
    };

    if (errorsOnly && !['error', 'warning'].includes(msg.type())) {
      return;
    }

    capture.consoleLogs.push(logEntry);

    if (msg.type() === 'error') {
      capture.errors.push(msg.text());
    }
  });

  // Capture page errors (uncaught exceptions)
  page.on('pageerror', err => {
    capture.errors.push(err.toString());
  });

  // Attach network listeners if requested
  if (captureNetwork) {
    page.on('request', request => {
      capture.networkRequests.push({
        method: request.method(),
        url: request.url(),
        resourceType: request.resourceType(),
      });
    });

    page.on('response', response => {
      capture.networkResponses.push({
        status: response.status(),
        url: response.url(),
        ok: response.ok(),
      });
    });
  }

  await page.goto(url);
  await page.waitForLoadState('networkidle');

  // Give a moment for any delayed console messages
  await page.waitForTimeout(1000);

  await browser.close();
  return capture;
}

function printCapture(capture, showNetwork = false) {
  const typeLabels = {
    log: '',
    info: '[INFO]',
    warning: '[WARN]',
    error: '[ERROR]',
    debug: '[DEBUG]',
  };

  console.log('\n=== CONSOLE LOGS ===');
  if (capture.consoleLogs.length === 0) {
    console.log('  (no logs captured)');
  }
  for (const log of capture.consoleLogs) {
    const prefix = typeLabels[log.type] || `[${log.type.toUpperCase()}]`;
    console.log(`  ${prefix} ${log.text}`);
  }

  if (capture.errors.length > 0) {
    console.log('\n=== ERRORS ===');
    for (const err of capture.errors) {
      console.log(`  [!] ${err}`);
    }
  }

  if (showNetwork) {
    console.log('\n=== NETWORK REQUESTS ===');
    for (const req of capture.networkRequests) {
      console.log(`  --> ${req.method} ${req.url} (${req.resourceType})`);
    }

    console.log('\n=== NETWORK RESPONSES ===');
    const failed = capture.networkResponses.filter(r => !r.ok);
    if (failed.length > 0) {
      console.log('  Failed responses:');
      for (const res of failed) {
        console.log(`    <-- ${res.status} ${res.url}`);
      }
    } else {
      console.log(`  All ${capture.networkResponses.length} responses OK`);
    }
  }
}

async function main() {
  const args = process.argv.slice(2);

  if (args.includes('--help') || args.includes('-h') || args.length === 0) {
    console.log(`
Console Logging - Capture browser console logs and network activity

Usage: node console_logging.js <url> [options]

Arguments:
  url    Target URL to monitor (e.g., http://localhost:3000)

Options:
  --errors-only, -e    Only capture errors and warnings
  --network, -n        Also capture network requests and responses
  --help, -h           Show this help message

Example:
  node console_logging.js http://localhost:3000
  node console_logging.js http://localhost:3000 --errors-only --network
`);
    process.exit(0);
  }

  const url = args.find(a => !a.startsWith('-'));
  const errorsOnly = args.includes('--errors-only') || args.includes('-e');
  const captureNetwork = args.includes('--network') || args.includes('-n');

  console.log(`Capturing console logs from: ${url}`);
  if (errorsOnly) {
    console.log('  (filtering to errors and warnings only)');
  }
  if (captureNetwork) {
    console.log('  (including network activity)');
  }

  try {
    const captured = await captureLogs(url, { errorsOnly, captureNetwork });
    printCapture(captured, captureNetwork);

    console.log('\nSummary:');
    console.log(`  Console messages: ${captured.consoleLogs.length}`);
    console.log(`  Errors: ${captured.errors.length}`);
    if (captureNetwork) {
      console.log(`  Network requests: ${captured.networkRequests.length}`);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

main();
