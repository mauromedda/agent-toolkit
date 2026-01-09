# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
# ABOUTME: Example script for capturing browser console logs
# ABOUTME: Demonstrates log filtering, error detection, and network monitoring

"""
Console Logging Example

Captures and filters browser console messages and network activity.
Useful for debugging JavaScript issues and monitoring API calls.
"""

import argparse
from dataclasses import dataclass, field
from playwright.sync_api import sync_playwright, ConsoleMessage, Request, Response


@dataclass
class LogCapture:
    """Container for captured logs and network activity."""
    console_logs: list[dict] = field(default_factory=list)
    network_requests: list[dict] = field(default_factory=list)
    network_responses: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def capture_logs(
    url: str,
    errors_only: bool = False,
    capture_network: bool = False,
) -> LogCapture:
    """Navigate to URL and capture console logs and network activity."""
    capture = LogCapture()

    def handle_console(msg: ConsoleMessage) -> None:
        log_entry = {
            "type": msg.type,
            "text": msg.text,
            "location": msg.location,
        }

        if errors_only and msg.type not in ("error", "warning"):
            return

        capture.console_logs.append(log_entry)

        if msg.type == "error":
            capture.errors.append(msg.text)

    def handle_request(request: Request) -> None:
        capture.network_requests.append({
            "method": request.method,
            "url": request.url,
            "resource_type": request.resource_type,
        })

    def handle_response(response: Response) -> None:
        capture.network_responses.append({
            "status": response.status,
            "url": response.url,
            "ok": response.ok,
        })

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Attach console listener
        page.on("console", handle_console)

        # Attach network listeners if requested
        if capture_network:
            page.on("request", handle_request)
            page.on("response", handle_response)

        # Capture page errors (uncaught exceptions)
        page.on("pageerror", lambda err: capture.errors.append(str(err)))

        page.goto(url)
        page.wait_for_load_state("networkidle")

        # Give a moment for any delayed console messages
        page.wait_for_timeout(1000)

        browser.close()

    return capture


def print_capture(capture: LogCapture, show_network: bool = False) -> None:
    """Print captured logs in a readable format."""
    type_colors = {
        "log": "",
        "info": "[INFO]",
        "warning": "[WARN]",
        "error": "[ERROR]",
        "debug": "[DEBUG]",
    }

    print("\n=== CONSOLE LOGS ===")
    if not capture.console_logs:
        print("  (no logs captured)")
    for log in capture.console_logs:
        prefix = type_colors.get(log["type"], f"[{log['type'].upper()}]")
        print(f"  {prefix} {log['text']}")

    if capture.errors:
        print("\n=== ERRORS ===")
        for err in capture.errors:
            print(f"  [!] {err}")

    if show_network:
        print("\n=== NETWORK REQUESTS ===")
        for req in capture.network_requests:
            print(f"  --> {req['method']} {req['url']} ({req['resource_type']})")

        print("\n=== NETWORK RESPONSES ===")
        failed = [r for r in capture.network_responses if not r["ok"]]
        if failed:
            print("  Failed responses:")
            for res in failed:
                print(f"    <-- {res['status']} {res['url']}")
        else:
            print(f"  All {len(capture.network_responses)} responses OK")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Capture browser console logs and optionally network activity.",
        epilog="Example: uv run console_logging.py http://localhost:3000 --errors-only --network",
    )
    parser.add_argument(
        "url",
        help="Target URL to monitor (e.g., http://localhost:3000)",
    )
    parser.add_argument(
        "--errors-only", "-e",
        action="store_true",
        help="Only capture errors and warnings, ignore info/debug/log messages",
    )
    parser.add_argument(
        "--network", "-n",
        action="store_true",
        help="Also capture network requests and responses",
    )

    args = parser.parse_args()

    print(f"Capturing console logs from: {args.url}")
    if args.errors_only:
        print("  (filtering to errors and warnings only)")
    if args.network:
        print("  (including network activity)")

    captured = capture_logs(
        args.url,
        errors_only=args.errors_only,
        capture_network=args.network,
    )

    print_capture(captured, show_network=args.network)

    print(f"\nSummary:")
    print(f"  Console messages: {len(captured.console_logs)}")
    print(f"  Errors: {len(captured.errors)}")
    if args.network:
        print(f"  Network requests: {len(captured.network_requests)}")


if __name__ == "__main__":
    main()
