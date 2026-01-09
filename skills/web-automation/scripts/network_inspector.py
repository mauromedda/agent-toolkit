# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
# ABOUTME: Network request/response inspector using Chrome DevTools Protocol
# ABOUTME: Captures XHR, fetch, WebSocket with timing, headers, and optional bodies

"""
Network Inspector

Capture and analyze network requests via Chrome DevTools Protocol.
Supports XHR, fetch, script, stylesheet, and WebSocket inspection.

Usage:
    uv run network_inspector.py http://localhost:3000
    uv run network_inspector.py http://localhost:3000 --errors-only
    uv run network_inspector.py http://localhost:3000 --filter xhr,fetch --capture-bodies
    uv run network_inspector.py http://localhost:3000 --url-pattern "api/" --output /tmp/network.json
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


class NetworkInspector:
    """Captures network requests via CDP Network domain."""

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
        self.completed: list[dict[str, Any]] = []
        self.client = None

    def _should_capture(self, url: str, resource_type: str) -> bool:
        """Check if request matches filters."""
        if self.filter_types:
            if resource_type.lower() not in [t.lower() for t in self.filter_types]:
                return False

        if self.url_pattern:
            if not self.url_pattern.search(url):
                return False

        return True

    def _on_request_will_be_sent(self, params: dict) -> None:
        """Handle Network.requestWillBeSent event."""
        request_id = params["requestId"]
        request = params["request"]
        resource_type = params.get("type", "Other")

        if not self._should_capture(request["url"], resource_type):
            return

        self.requests[request_id] = {
            "id": request_id,
            "url": request["url"],
            "method": request["method"],
            "type": resource_type,
            "request": {
                "headers": request.get("headers", {}),
                "post_data": request.get("postData"),
            },
            "timestamp": params.get("wallTime", datetime.now(timezone.utc).timestamp()),
            "timing": {},
            "response": None,
            "error": None,
        }

    def _on_response_received(self, params: dict) -> None:
        """Handle Network.responseReceived event."""
        request_id = params["requestId"]
        if request_id not in self.requests:
            return

        response = params["response"]
        self.requests[request_id]["response"] = {
            "status": response["status"],
            "status_text": response.get("statusText", ""),
            "headers": response.get("headers", {}),
            "mime_type": response.get("mimeType", ""),
            "remote_address": response.get("remoteIPAddress"),
        }

        timing = response.get("timing")
        if timing:
            self.requests[request_id]["timing"] = {
                "dns_ms": timing.get("dnsEnd", 0) - timing.get("dnsStart", 0),
                "connect_ms": timing.get("connectEnd", 0) - timing.get("connectStart", 0),
                "ssl_ms": timing.get("sslEnd", 0) - timing.get("sslStart", 0),
                "ttfb_ms": timing.get("receiveHeadersEnd", 0),
            }

    async def _on_loading_finished(self, params: dict) -> None:
        """Handle Network.loadingFinished event."""
        request_id = params["requestId"]
        if request_id not in self.requests:
            return

        req = self.requests[request_id]
        req["completed"] = True
        req["encoded_data_length"] = params.get("encodedDataLength", 0)

        if self.capture_bodies and self.client:
            try:
                body_response = await self.client.send(
                    "Network.getResponseBody",
                    {"requestId": request_id},
                )
                body = body_response.get("body", "")
                if len(body) > self.max_body_size:
                    body = body[: self.max_body_size] + f"... (truncated, total {len(body)} bytes)"
                req["response_body"] = body
                req["body_base64"] = body_response.get("base64Encoded", False)
            except Exception:
                req["response_body"] = None

        if not self.errors_only or req.get("error") or (req.get("response", {}).get("status", 0) >= 400):
            self.completed.append(req)

        del self.requests[request_id]

    def _on_loading_failed(self, params: dict) -> None:
        """Handle Network.loadingFailed event."""
        request_id = params["requestId"]
        if request_id not in self.requests:
            return

        req = self.requests[request_id]
        req["error"] = {
            "type": params.get("type", "Unknown"),
            "error_text": params.get("errorText", ""),
            "canceled": params.get("canceled", False),
            "blocked_reason": params.get("blockedReason"),
            "cors_error": params.get("corsErrorStatus"),
        }
        req["completed"] = False

        self.completed.append(req)
        del self.requests[request_id]

    async def capture(
        self,
        url: str,
        duration: float = 30.0,
        wait_for_idle: bool = True,
    ) -> dict:
        """
        Capture network requests for a URL.

        Args:
            url: URL to navigate to
            duration: Maximum capture duration in seconds
            wait_for_idle: Wait for network idle before starting timer

        Returns:
            Capture results dictionary
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            self.client = await context.new_cdp_session(page)

            await self.client.send("Network.enable")

            self.client.on("Network.requestWillBeSent", self._on_request_will_be_sent)
            self.client.on("Network.responseReceived", self._on_response_received)
            self.client.on(
                "Network.loadingFinished",
                lambda p: asyncio.create_task(self._on_loading_finished(p)),
            )
            self.client.on("Network.loadingFailed", self._on_loading_failed)

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)

                if wait_for_idle:
                    try:
                        await page.wait_for_load_state("networkidle", timeout=10000)
                    except Exception:
                        pass

                await asyncio.sleep(duration)

            except Exception as e:
                self.completed.append(
                    {
                        "id": "navigation_error",
                        "url": url,
                        "error": {"type": "NavigationError", "error_text": str(e)},
                    }
                )

            finally:
                await browser.close()

        error_count = sum(1 for r in self.completed if r.get("error") or (r.get("response", {}).get("status", 0) >= 400))

        return {
            "metadata": {
                "url": url,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "duration_seconds": duration,
                "browser": "Chromium",
                "filters": {
                    "types": self.filter_types,
                    "url_pattern": self.url_pattern.pattern if self.url_pattern else None,
                    "errors_only": self.errors_only,
                },
            },
            "data": self.completed,
            "summary": {
                "total": len(self.completed),
                "errors": error_count,
                "by_type": self._count_by_type(),
                "by_status": self._count_by_status(),
            },
        }

    def _count_by_type(self) -> dict[str, int]:
        """Count requests by resource type."""
        counts: dict[str, int] = {}
        for req in self.completed:
            req_type = req.get("type", "Other")
            counts[req_type] = counts.get(req_type, 0) + 1
        return counts

    def _count_by_status(self) -> dict[str, int]:
        """Count requests by status code range."""
        counts = {"2xx": 0, "3xx": 0, "4xx": 0, "5xx": 0, "failed": 0}
        for req in self.completed:
            if req.get("error"):
                counts["failed"] += 1
            elif req.get("response"):
                status = req["response"].get("status", 0)
                if 200 <= status < 300:
                    counts["2xx"] += 1
                elif 300 <= status < 400:
                    counts["3xx"] += 1
                elif 400 <= status < 500:
                    counts["4xx"] += 1
                elif status >= 500:
                    counts["5xx"] += 1
        return counts


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Capture and analyze network requests via Chrome DevTools Protocol",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    uv run network_inspector.py http://localhost:3000
    uv run network_inspector.py http://localhost:3000 --errors-only
    uv run network_inspector.py http://localhost:3000 --filter xhr,fetch
    uv run network_inspector.py http://localhost:3000 --url-pattern "api/" --capture-bodies
    uv run network_inspector.py http://localhost:3000 --output /tmp/network.json

Resource types: Document, Stylesheet, Image, Media, Font, Script, TextTrack,
                XHR, Fetch, Prefetch, EventSource, WebSocket, Manifest, Other
        """,
    )
    parser.add_argument("url", help="URL to inspect")
    parser.add_argument(
        "--duration",
        "-d",
        type=float,
        default=10.0,
        help="Capture duration in seconds (default: 10)",
    )
    parser.add_argument(
        "--filter",
        "-f",
        help="Comma-separated resource types to capture (e.g., xhr,fetch,script)",
    )
    parser.add_argument(
        "--url-pattern",
        "-p",
        help="Regex pattern to filter URLs (e.g., 'api/')",
    )
    parser.add_argument(
        "--errors-only",
        "-e",
        action="store_true",
        help="Only show failed requests and 4xx/5xx responses",
    )
    parser.add_argument(
        "--capture-bodies",
        "-b",
        action="store_true",
        help="Capture response bodies (increases memory usage)",
    )
    parser.add_argument(
        "--max-body-size",
        type=int,
        default=10240,
        help="Maximum response body size to capture in bytes (default: 10240)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: stdout)",
    )

    args = parser.parse_args()

    filter_types = None
    if args.filter:
        filter_types = [t.strip() for t in args.filter.split(",")]

    inspector = NetworkInspector(
        filter_types=filter_types,
        url_pattern=args.url_pattern,
        errors_only=args.errors_only,
        capture_bodies=args.capture_bodies,
        max_body_size=args.max_body_size,
    )

    results = await inspector.capture(args.url, duration=args.duration)

    json_str = json.dumps(results, indent=2, default=str)
    if args.output:
        with open(args.output, "w") as f:
            f.write(json_str)
        print(f"Output written to: {args.output}", file=sys.stderr)
    else:
        print(json_str)


if __name__ == "__main__":
    asyncio.run(main())
