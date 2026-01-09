# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
# ABOUTME: Combined network + console debugging in a single browser instance
# ABOUTME: Captures requests, responses, console logs, errors with automatic timestamp correlation

"""
Combined Debugger

Capture network requests, console logs, and JavaScript errors in a single browser instance.
All events are correlated by timestamp for easy analysis.

Usage:
    uv run combined_debugger.py http://localhost:3000
    uv run combined_debugger.py http://localhost:3000 --duration 30
    uv run combined_debugger.py http://localhost:3000 --errors-only
    uv run combined_debugger.py http://localhost:3000 --output /tmp/debug.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from datetime import datetime, timezone
from typing import Any

from playwright.async_api import async_playwright


class CombinedDebugger:
    """Captures network requests, console messages, and exceptions in correlation."""

    def __init__(
        self,
        filter_types: list[str] | None = None,
        url_pattern: str | None = None,
        errors_only: bool = False,
        capture_bodies: bool = False,
        max_body_size: int = 10240,
    ):
        self.filter_types = filter_types
        self.url_pattern = re.compile(url_pattern) if url_pattern else None
        self.errors_only = errors_only
        self.capture_bodies = capture_bodies
        self.max_body_size = max_body_size

        self.requests: dict[str, dict[str, Any]] = {}
        self.events: list[dict[str, Any]] = []
        self.start_time: float = 0

    def _get_timestamp_offset(self, ms: float | None) -> float:
        """Get milliseconds since start of session."""
        if ms is None:
            return 0
        return ms - self.start_time

    def _should_capture_request(self, url: str, resource_type: str) -> bool:
        """Check if request matches filters."""
        if self.filter_types:
            if resource_type.lower() not in [t.lower() for t in self.filter_types]:
                return False

        if self.url_pattern:
            if not self.url_pattern.search(url):
                return False

        return True

    def _format_remote_object(self, obj: dict) -> Any:
        """Format a CDP RemoteObject for output."""
        obj_type = obj.get("type", "undefined")

        if obj_type == "undefined":
            return "undefined"
        elif obj_type == "object":
            if obj.get("subtype") == "null":
                return None
            if obj.get("subtype") == "error":
                return obj.get("description", str(obj.get("value")))
            if "value" in obj:
                return obj["value"]
            return obj.get("description", f"[{obj.get('className', 'Object')}]")
        elif obj_type in ("string", "number", "boolean"):
            return obj.get("value")
        else:
            return obj.get("description", str(obj.get("value")))

    async def capture(self, url: str, duration: int = 30) -> dict[str, Any]:
        """Capture network and console events in a single browser."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            # Set start time
            self.start_time = datetime.now(timezone.utc).timestamp() * 1000

            # Setup network event handlers
            page.on("request", self._on_request)
            page.on("response", self._on_response)
            page.on("requestfailed", self._on_request_failed)

            # Setup console event handlers
            page.on("console", self._on_console)
            page.on("pageerror", self._on_page_error)

            # Navigate and wait
            try:
                await page.goto(url, wait_until="networkidle")
            except Exception as e:
                self.events.append({
                    "type": "navigation_error",
                    "timestamp_ms": self._get_timestamp_offset(
                        datetime.now(timezone.utc).timestamp() * 1000
                    ),
                    "error": str(e),
                })

            # Wait for additional events
            await asyncio.sleep(duration)

            await context.close()
            await browser.close()

        return self._build_output()

    def _on_request(self, request) -> None:
        """Handle request event."""
        url = request.url
        resource_type = request.resource_type
        request_id = id(request)

        if not self._should_capture_request(url, resource_type):
            return

        self.requests[request_id] = {
            "id": str(request_id),
            "url": url,
            "method": request.method,
            "type": resource_type,
            "headers": dict(request.headers),
            "timestamp_ms": self._get_timestamp_offset(
                datetime.now(timezone.utc).timestamp() * 1000
            ),
        }

        self.events.append({
            "type": "request",
            "timestamp_ms": self.requests[request_id]["timestamp_ms"],
            "url": url,
            "method": request.method,
            "resource_type": resource_type,
        })

    def _on_response(self, response) -> None:
        """Handle response event."""
        request_id = id(response.request)

        if request_id not in self.requests:
            return

        timestamp_ms = self._get_timestamp_offset(
            datetime.now(timezone.utc).timestamp() * 1000
        )

        status = response.status
        headers = dict(response.headers)
        url = response.url

        req_data = self.requests[request_id]
        req_data["status"] = status
        req_data["response_headers"] = headers
        req_data["timestamp_response_ms"] = timestamp_ms

        # Determine if error
        is_error = status >= 400

        self.events.append({
            "type": "response",
            "timestamp_ms": timestamp_ms,
            "url": url,
            "status": status,
            "is_error": is_error,
        })

    def _on_request_failed(self, request) -> None:
        """Handle request failure."""
        request_id = id(request)

        if request_id not in self.requests:
            return

        timestamp_ms = self._get_timestamp_offset(
            datetime.now(timezone.utc).timestamp() * 1000
        )

        self.events.append({
            "type": "request_failed",
            "timestamp_ms": timestamp_ms,
            "url": request.url,
            "method": request.method,
        })

    def _on_console(self, msg) -> None:
        """Handle console message."""
        if self.errors_only and msg.type not in ("error", "warning"):
            return

        timestamp_ms = self._get_timestamp_offset(
            datetime.now(timezone.utc).timestamp() * 1000
        )

        self.events.append({
            "type": "console",
            "timestamp_ms": timestamp_ms,
            "level": msg.type,
            "text": msg.text,
        })

    def _on_page_error(self, error) -> None:
        """Handle page error."""
        timestamp_ms = self._get_timestamp_offset(
            datetime.now(timezone.utc).timestamp() * 1000
        )

        self.events.append({
            "type": "page_error",
            "timestamp_ms": timestamp_ms,
            "error": str(error),
        })

    def _build_output(self) -> dict[str, Any]:
        """Build final output with correlation."""
        # Sort events by timestamp
        sorted_events = sorted(self.events, key=lambda e: e["timestamp_ms"])

        # Correlate errors with surrounding events
        correlated_events = []
        for i, event in enumerate(sorted_events):
            correlated = event.copy()

            # Find related events (within 100ms)
            if event["type"] in ("page_error", "request_failed"):
                nearby = [
                    e for e in sorted_events
                    if abs(e["timestamp_ms"] - event["timestamp_ms"]) <= 100
                    and e != event
                ]
                if nearby:
                    correlated["related_events"] = nearby

            correlated_events.append(correlated)

        return {
            "metadata": {
                "url": "",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "browser": "Chromium",
                "combined_capture": True,
            },
            "events": correlated_events,
            "summary": {
                "total_events": len(correlated_events),
                "requests": len([e for e in correlated_events if e["type"] == "request"]),
                "responses": len([e for e in correlated_events if e["type"] == "response"]),
                "errors": len([e for e in correlated_events if e["type"] in ("page_error", "request_failed")]),
                "console_messages": len([e for e in correlated_events if e["type"] == "console"]),
            },
        }


async def main():
    parser = argparse.ArgumentParser(
        description="Capture network requests and console output simultaneously",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Quick capture for 30 seconds
    uv run combined_debugger.py http://localhost:3000

    # Only errors and failures
    uv run combined_debugger.py http://localhost:3000 --errors-only

    # Save to file
    uv run combined_debugger.py http://localhost:3000 --output /tmp/debug.json

    # Longer capture
    uv run combined_debugger.py http://localhost:3000 --duration 60
        """,
    )

    parser.add_argument("url", help="URL to debug (e.g., http://localhost:3000)")
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=30,
        help="Capture duration in seconds (default: 30)",
    )
    parser.add_argument(
        "--errors-only", "-e",
        action="store_true",
        help="Only capture errors and failures (skip normal logs)",
    )
    parser.add_argument(
        "--filter", "-f",
        type=str,
        help="Filter by resource types (comma-separated: xhr,fetch,script,etc.)",
    )
    parser.add_argument(
        "--url-pattern", "-p",
        type=str,
        help="Filter requests by URL pattern (regex)",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path (default: stdout)",
    )

    args = parser.parse_args()

    filter_types = None
    if args.filter:
        filter_types = [t.strip() for t in args.filter.split(",")]

    debugger = CombinedDebugger(
        filter_types=filter_types,
        url_pattern=args.url_pattern,
        errors_only=args.errors_only,
    )

    print(f"Starting combined debug capture for {args.url}...")
    print(f"Duration: {args.duration} seconds", file=sys.stderr)

    try:
        result = await debugger.capture(args.url, args.duration)

        # Output result
        if args.output:
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2)
            print(f"\nDebug output saved to: {args.output}", file=sys.stderr)
        else:
            print(json.dumps(result, indent=2))

    except KeyboardInterrupt:
        print("\nCapture cancelled", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\nError during capture: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
