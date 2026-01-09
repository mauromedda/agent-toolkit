#!/usr/bin/env node
// ABOUTME: Example script for capturing browser screenshots
// ABOUTME: Demonstrates viewport, full-page, and element-specific screenshots

/**
 * Screenshot Capture Example
 *
 * Captures various types of screenshots from a web page:
 * - Viewport (visible area)
 * - Full page (scrolled content)
 * - Element-specific (header, main, footer)
 * - Responsive (mobile, tablet, desktop)
 *
 * Usage: node screenshot_capture.js <url> [--output <dir>]
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function captureScreenshots(url, outputDir = '/tmp') {
  // Ensure output directory exists
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const savedFiles = [];

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  await page.goto(url);
  await page.waitForLoadState('networkidle');

  // Viewport screenshot (what's visible)
  const viewportPath = path.join(outputDir, 'viewport.png');
  await page.screenshot({ path: viewportPath });
  savedFiles.push(viewportPath);
  console.log(`Saved viewport screenshot: ${viewportPath}`);

  // Full page screenshot (scrolled content)
  const fullpagePath = path.join(outputDir, 'fullpage.png');
  await page.screenshot({ path: fullpagePath, fullPage: true });
  savedFiles.push(fullpagePath);
  console.log(`Saved full-page screenshot: ${fullpagePath}`);

  // Try to capture specific elements
  const elementSelectors = [
    ['header', "header, [role='banner'], nav"],
    ['main', "main, [role='main'], #content, .content"],
    ['footer', "footer, [role='contentinfo']"],
  ];

  for (const [name, selector] of elementSelectors) {
    try {
      const element = page.locator(selector).first();
      if (await element.isVisible()) {
        const elementPath = path.join(outputDir, `element_${name}.png`);
        await element.screenshot({ path: elementPath });
        savedFiles.push(elementPath);
        console.log(`Saved ${name} element screenshot: ${elementPath}`);
      }
    } catch (e) {
      console.log(`Could not capture ${name}: ${e.message}`);
    }
  }

  // Capture with different viewport sizes (responsive testing)
  const viewports = [
    ['mobile', 375, 667],
    ['tablet', 768, 1024],
    ['desktop', 1920, 1080],
  ];

  for (const [name, width, height] of viewports) {
    await page.setViewportSize({ width, height });
    await page.waitForLoadState('networkidle');

    const responsivePath = path.join(outputDir, `responsive_${name}.png`);
    await page.screenshot({ path: responsivePath });
    savedFiles.push(responsivePath);
    console.log(`Saved ${name} (${width}x${height}) screenshot: ${responsivePath}`);
  }

  await browser.close();
  return savedFiles;
}

async function main() {
  const args = process.argv.slice(2);

  if (args.includes('--help') || args.includes('-h') || args.length === 0) {
    console.log(`
Screenshot Capture - Capture screenshots from a web page

Usage: node screenshot_capture.js <url> [options]

Arguments:
  url    Target URL to screenshot (e.g., http://localhost:3000)

Options:
  --output, -o <dir>    Output directory for screenshots (default: /tmp)
  --help, -h            Show this help message

Example:
  node screenshot_capture.js http://localhost:3000
  node screenshot_capture.js http://localhost:3000 --output /tmp/shots
`);
    process.exit(0);
  }

  const url = args[0];
  let outputDir = '/tmp';

  const outputIdx = args.findIndex(a => a === '--output' || a === '-o');
  if (outputIdx !== -1 && args[outputIdx + 1]) {
    outputDir = args[outputIdx + 1];
  }

  console.log(`Capturing screenshots from: ${url}`);
  console.log(`Output directory: ${outputDir}`);

  try {
    const files = await captureScreenshots(url, outputDir);
    console.log(`\nTotal screenshots captured: ${files.length}`);
    console.log('Files:');
    for (const f of files) {
      console.log(`  - ${f}`);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

main();
