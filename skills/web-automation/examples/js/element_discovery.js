#!/usr/bin/env node
// ABOUTME: Example script for discovering interactive elements on a web page
// ABOUTME: Demonstrates locator patterns for buttons, links, inputs, and forms

/**
 * Element Discovery Example
 *
 * Discovers and lists interactive elements on a web page.
 * Useful for reconnaissance before writing automation scripts.
 *
 * Usage: node element_discovery.js <url>
 * Example: node element_discovery.js http://localhost:3000
 */

const { chromium } = require('playwright');

async function discoverElements(url) {
  const results = {
    buttons: [],
    links: [],
    inputs: [],
    forms: [],
  };

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  await page.goto(url);
  await page.waitForLoadState('networkidle');

  // Discover buttons
  const buttons = await page.locator('button').all();
  for (const btn of buttons) {
    const text = (await btn.textContent()) || '';
    const btnType = (await btn.getAttribute('type')) || 'button';
    const btnId = (await btn.getAttribute('id')) || '';
    results.buttons.push({
      text: text.trim(),
      type: btnType,
      id: btnId,
    });
  }

  // Discover links
  const links = await page.locator('a').all();
  for (const link of links) {
    const text = (await link.textContent()) || '';
    const href = (await link.getAttribute('href')) || '';
    results.links.push({
      text: text.trim(),
      href: href,
    });
  }

  // Discover inputs
  const inputs = await page.locator('input, textarea, select').all();
  for (const inp of inputs) {
    const inpType = (await inp.getAttribute('type')) || 'text';
    const inpName = (await inp.getAttribute('name')) || '';
    const inpId = (await inp.getAttribute('id')) || '';
    const inpPlaceholder = (await inp.getAttribute('placeholder')) || '';
    results.inputs.push({
      type: inpType,
      name: inpName,
      id: inpId,
      placeholder: inpPlaceholder,
    });
  }

  // Discover forms
  const forms = await page.locator('form').all();
  for (const form of forms) {
    const formId = (await form.getAttribute('id')) || '';
    const formAction = (await form.getAttribute('action')) || '';
    const formMethod = (await form.getAttribute('method')) || 'get';
    results.forms.push({
      id: formId,
      action: formAction,
      method: formMethod,
    });
  }

  await browser.close();
  return results;
}

function printResults(results) {
  console.log('\n=== BUTTONS ===');
  for (const btn of results.buttons) {
    console.log(`  [${btn.type}] "${btn.text}" (id="${btn.id}")`);
  }

  console.log('\n=== LINKS ===');
  for (const link of results.links) {
    console.log(`  "${link.text}" -> ${link.href}`);
  }

  console.log('\n=== INPUTS ===');
  for (const inp of results.inputs) {
    const selector = inp.name ? `name="${inp.name}"` : `id="${inp.id}"`;
    console.log(`  [${inp.type}] ${selector} placeholder="${inp.placeholder}"`);
  }

  console.log('\n=== FORMS ===');
  for (const form of results.forms) {
    console.log(`  ${form.method.toUpperCase()} -> ${form.action} (id="${form.id}")`);
  }
}

async function main() {
  const args = process.argv.slice(2);

  if (args.includes('--help') || args.includes('-h') || args.length === 0) {
    console.log(`
Element Discovery - Discover interactive elements on a web page

Usage: node element_discovery.js <url>

Arguments:
  url    Target URL to analyze (e.g., http://localhost:3000)

Options:
  --help, -h    Show this help message

Example:
  node element_discovery.js http://localhost:3000
  node element_discovery.js file:///path/to/file.html
`);
    process.exit(0);
  }

  const url = args[0];
  console.log(`Discovering elements on: ${url}`);

  try {
    const discovered = await discoverElements(url);
    printResults(discovered);

    const total = Object.values(discovered).reduce((sum, arr) => sum + arr.length, 0);
    console.log(`\nTotal elements discovered: ${total}`);
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

main();
