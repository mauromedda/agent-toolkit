# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
# ABOUTME: Console log and JavaScript error capture using Chrome DevTools Protocol
# ABOUTME: Captures console.log/warn/error, exceptions, and unhandled promise rejections

"""
Console Debugger

Capture console logs and JavaScript errors via Chrome DevTools Protocol.
Includes stack traces and exception details.

Usage:
    uv run console_debugger.py http://localhost:3000
    uv run console_debugger.py http://localhost:3000 --errors-only
    uv run console_debugger.py http://localhost:3000 --with-stack-traces
    uv run console_debugger.py http://localhost:3000 --output /tmp/console.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from typing import Any

from playwright.async_api import async_playwright


class ConsoleDebugger:
    """Captures console messages and exceptions via CDP Runtime domain."""

    def __init__(
        self,
        errors_only: bool = False,
        with_stack_traces: bool = True,
        include_timestamps: bool = True,
    ):
        self.errors_only = errors_only
        self.with_stack_traces = with_stack_traces
        self.include_timestamps = include_timestamps

        self.messages: list[dict[str, Any]] = []
        self.exceptions: list[dict[str, Any]] = []

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

    def _format_stack_trace(self, stack_trace: dict) -> list[dict]:
        """Format a CDP StackTrace for output."""
        frames = []
        for frame in stack_trace.get("callFrames", []):
            frames.append(
                {
                    "function": frame.get("functionName", "(anonymous)"),
                    "file": frame.get("url", ""),
                    "line": frame.get("lineNumber", 0) + 1,
                    "column": frame.get("columnNumber", 0) + 1,
                }
            )
        return frames

    def _on_console_api_called(self, params: dict) -> None:
        """Handle Runtime.consoleAPICalled event."""
        msg_type = params.get("type", "log")

        if self.errors_only and msg_type not in ("error", "warning", "assert"):
            return

        args = params.get("args", [])
        formatted_args = [self._format_remote_object(arg) for arg in args]

        message = {
            "type": msg_type,
            "level": self._type_to_level(msg_type),
            "text": " ".join(str(arg) for arg in formatted_args),
            "args": formatted_args,
        }

        if self.include_timestamps:
            message["timestamp"] = params.get("timestamp", datetime.now(timezone.utc).timestamp())

        if self.with_stack_traces and "stackTrace" in params:
            message["stack"] = self._format_stack_trace(params["stackTrace"])

        self.messages.append(message)

    def _on_exception_thrown(self, params: dict) -> None:
        """Handle Runtime.exceptionThrown event."""
        exception_details = params.get("exceptionDetails", {})
        exception_obj = exception_details.get("exception", {})

        exception = {
            "type": "exception",
            "level": "error",
            "exception_id": exception_details.get("exceptionId"),
            "text": exception_details.get("text", ""),
            "description": exception_obj.get("description", ""),
            "line": exception_details.get("lineNumber", 0) + 1,
            "column": exception_details.get("columnNumber", 0) + 1,
            "url": exception_details.get("url", ""),
        }

        if self.include_timestamps:
            exception["timestamp"] = params.get("timestamp", datetime.now(timezone.utc).timestamp())

        if self.with_stack_traces:
            stack_trace = exception_details.get("stackTrace")
            if stack_trace:
                exception["stack"] = self._format_stack_trace(stack_trace)

        self.exceptions.append(exception)

    def _type_to_level(self, msg_type: str) -> str:
        """Map console type to severity level."""
        mapping = {
            "log": "info",
            "info": "info",
            "debug": "debug",
            "warning": "warning",
            "warn": "warning",
            "error": "error",
            "assert": "error",
            "trace": "debug",
            "dir": "info",
            "dirxml": "info",
            "table": "info",
            "count": "info",
            "timeEnd": "info",
            "group": "info",
            "groupCollapsed": "info",
            "groupEnd": "info",
            "clear": "info",
        }
        return mapping.get(msg_type, "info")

    async def capture(
        self,
        url: str,
        duration: float = 30.0,
        wait_for_idle: bool = True,
    ) -> dict:
        """
        Capture console messages and exceptions for a URL.

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

            client = await context.new_cdp_session(page)

            await client.send("Runtime.enable")
            await client.send("Log.enable")

            client.on("Runtime.consoleAPICalled", self._on_console_api_called)
            client.on("Runtime.exceptionThrown", self._on_exception_thrown)

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)

                if wait_for_idle:
                    try:
                        await page.wait_for_load_state("networkidle", timeout=10000)
                    except Exception:
                        pass

                await asyncio.sleep(duration)

            except Exception as e:
                self.exceptions.append(
                    {
                        "type": "navigation_error",
                        "level": "error",
                        "text": f"Navigation failed: {e}",
                        "description": str(e),
                    }
                )

            finally:
                await browser.close()

        all_entries = self.messages + self.exceptions
        all_entries.sort(key=lambda x: x.get("timestamp", 0))

        error_count = sum(1 for e in all_entries if e.get("level") == "error")
        warning_count = sum(1 for e in all_entries if e.get("level") == "warning")

        return {
            "metadata": {
                "url": url,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "duration_seconds": duration,
                "browser": "Chromium",
                "options": {
                    "errors_only": self.errors_only,
                    "with_stack_traces": self.with_stack_traces,
                },
            },
            "data": all_entries,
            "summary": {
                "total": len(all_entries),
                "messages": len(self.messages),
                "exceptions": len(self.exceptions),
                "by_level": self._count_by_level(all_entries),
                "errors": error_count,
                "warnings": warning_count,
            },
        }

    def _count_by_level(self, entries: list[dict]) -> dict[str, int]:
        """Count entries by severity level."""
        counts: dict[str, int] = {}
        for entry in entries:
            level = entry.get("level", "info")
            counts[level] = counts.get(level, 0) + 1
        return counts


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Capture console logs and JavaScript errors via Chrome DevTools Protocol",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    uv run console_debugger.py http://localhost:3000
    uv run console_debugger.py http://localhost:3000 --errors-only
    uv run console_debugger.py http://localhost:3000 --with-stack-traces
    uv run console_debugger.py http://localhost:3000 --duration 60 --output /tmp/console.json

Captured message types:
    - Console API calls (log, warn, error, debug, info, assert, trace)
    - Unhandled exceptions
    - Unhandled promise rejections
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
        "--errors-only",
        "-e",
        action="store_true",
        help="Only capture errors and warnings (skip log/info/debug)",
    )
    parser.add_argument(
        "--with-stack-traces",
        "-s",
        action="store_true",
        default=True,
        help="Include stack traces (default: True)",
    )
    parser.add_argument(
        "--no-stack-traces",
        action="store_true",
        help="Exclude stack traces from output",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: stdout)",
    )

    args = parser.parse_args()

    with_stack_traces = args.with_stack_traces and not args.no_stack_traces

    debugger = ConsoleDebugger(
        errors_only=args.errors_only,
        with_stack_traces=with_stack_traces,
    )

    results = await debugger.capture(args.url, duration=args.duration)

    json_str = json.dumps(results, indent=2, default=str)
    if args.output:
        with open(args.output, "w") as f:
            f.write(json_str)
        print(f"Output written to: {args.output}", file=sys.stderr)
    else:
        print(json_str)


if __name__ == "__main__":
    asyncio.run(main())
