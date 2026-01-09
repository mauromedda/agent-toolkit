# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
# ABOUTME: Extract Claude Code session transcripts to markdown format
# ABOUTME: Supports listing sessions, extracting by ID, or getting the latest session

"""
Extract Claude Code session transcripts to markdown.

Usage:
    uv run extract_session.py --help
    uv run extract_session.py --list
    uv run extract_session.py --latest
    uv run extract_session.py --session-id <id>
    uv run extract_session.py --session-id <id> --output /tmp/session.md
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_claude_projects_dir() -> Path:
    """Get the Claude Code projects directory."""
    return Path.home() / ".claude" / "projects"


def encode_cwd_to_project_dir(cwd: str) -> str:
    """Encode a working directory path to Claude's project directory format."""
    # Claude uses path with slashes replaced by dashes and leading dash
    return "-" + cwd.replace("/", "-")


def find_project_dir(cwd: Optional[str] = None) -> Optional[Path]:
    """Find the project directory for the given working directory."""
    projects_dir = get_claude_projects_dir()

    if not projects_dir.exists():
        return None

    if cwd:
        encoded = encode_cwd_to_project_dir(cwd)
        project_dir = projects_dir / encoded
        if project_dir.exists():
            return project_dir
        return None

    # Return None if no cwd specified - caller should list all
    return None


def list_sessions(cwd: Optional[str] = None, limit: int = 20) -> list[dict]:
    """List recent sessions, optionally filtered by working directory."""
    projects_dir = get_claude_projects_dir()

    if not projects_dir.exists():
        return []

    sessions = []

    # Determine which project directories to search
    if cwd:
        project_dir = find_project_dir(cwd)
        if project_dir:
            project_dirs = [project_dir]
        else:
            return []
    else:
        project_dirs = [d for d in projects_dir.iterdir() if d.is_dir()]

    for project_dir in project_dirs:
        for session_file in project_dir.glob("*.jsonl"):
            # Skip agent files (they have agent- prefix)
            if session_file.name.startswith("agent-"):
                continue

            try:
                stat = session_file.stat()
                # Try to get session metadata from first few lines
                session_id = session_file.stem
                session_cwd = "unknown"
                with open(session_file, "r") as f:
                    for _ in range(5):  # Check first 5 lines
                        line = f.readline().strip()
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            if data.get("sessionId"):
                                session_id = data["sessionId"]
                            if data.get("cwd") and data.get("cwd") != "unknown":
                                session_cwd = data["cwd"]
                                break
                        except json.JSONDecodeError:
                            continue

                sessions.append({
                    "id": session_id,
                    "file": session_file,
                    "cwd": session_cwd,
                    "modified": datetime.fromtimestamp(stat.st_mtime),
                    "size": stat.st_size,
                })
            except (json.JSONDecodeError, OSError):
                continue

    # Sort by modification time, most recent first
    sessions.sort(key=lambda s: s["modified"], reverse=True)

    return sessions[:limit]


def find_session_file(session_id: str, cwd: Optional[str] = None) -> Optional[Path]:
    """Find a session file by ID."""
    projects_dir = get_claude_projects_dir()

    if not projects_dir.exists():
        return None

    # Determine which project directories to search
    if cwd:
        project_dir = find_project_dir(cwd)
        if project_dir:
            project_dirs = [project_dir]
        else:
            project_dirs = []
    else:
        project_dirs = [d for d in projects_dir.iterdir() if d.is_dir()]

    for project_dir in project_dirs:
        session_file = project_dir / f"{session_id}.jsonl"
        if session_file.exists():
            return session_file

    return None


def extract_content_text(content: list | str | dict) -> str:
    """Extract text from message content."""
    if isinstance(content, str):
        return content

    if isinstance(content, dict):
        # Handle single content block
        if content.get("type") == "text":
            return content.get("text", "")
        elif content.get("type") == "tool_use":
            tool_name = content.get("name", "unknown")
            tool_input = json.dumps(content.get("input", {}), indent=2)
            # Truncate long inputs
            if len(tool_input) > 1000:
                tool_input = tool_input[:1000] + "\n... [truncated]"
            return f"**Tool: {tool_name}**\n```json\n{tool_input}\n```"
        elif content.get("type") == "tool_result":
            result = content.get("content", "")
            if isinstance(result, str) and len(result) > 500:
                result = result[:500] + "\n... [truncated]"
            return f"**Tool Result:**\n```\n{result}\n```"
        elif content.get("type") == "thinking":
            thinking = content.get("thinking", "")
            if len(thinking) > 500:
                thinking = thinking[:500] + "\n... [truncated]"
            return f"*[Thinking: {thinking}]*"
        return ""

    if isinstance(content, list):
        parts = []
        for item in content:
            text = extract_content_text(item)
            if text:
                parts.append(text)
        return "\n\n".join(parts)

    return ""


def extract_session(session_file: Path, max_messages: int = 100) -> str:
    """Extract a session transcript to markdown format."""
    messages = []
    session_id = session_file.stem
    session_cwd = "unknown"

    with open(session_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Get session metadata from entries with cwd
            if entry.get("sessionId"):
                session_id = entry["sessionId"]
            if entry.get("cwd") and session_cwd == "unknown":
                session_cwd = entry["cwd"]

            # Skip non-message entries
            if entry.get("type") == "summary":
                continue

            # Extract message
            message = entry.get("message", {})
            role = message.get("role")
            content = message.get("content")

            if not role or not content:
                # Check for user type entries
                if entry.get("type") == "user" and entry.get("message"):
                    message = entry["message"]
                    role = message.get("role", "user")
                    content = message.get("content")
                elif entry.get("type") == "assistant":
                    message = entry["message"]
                    role = "assistant"
                    content = message.get("content")
                else:
                    continue

            if not content:
                continue

            text = extract_content_text(content)
            if text:
                timestamp = entry.get("timestamp", "")
                messages.append({
                    "role": role,
                    "content": text,
                    "timestamp": timestamp,
                })

    # Take last N messages
    messages = messages[-max_messages:]

    # Build markdown output
    lines = [
        "# Session Transcript",
        "",
        f"**Session ID:** `{session_id}`",
        f"**Working Directory:** `{session_cwd}`",
        f"**File:** `{session_file}`",
        f"**Total Messages:** {len(messages)}",
        "",
        "---",
        "",
    ]

    for msg in messages:
        role_label = "**User:**" if msg["role"] == "user" else "**Assistant:**"
        timestamp = msg.get("timestamp", "")
        if timestamp:
            lines.append(f"### {role_label} ({timestamp})")
        else:
            lines.append(f"### {role_label}")
        lines.append("")
        lines.append(msg["content"])
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Extract Claude Code session transcripts to markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # List recent sessions
    uv run extract_session.py --list

    # Extract the most recent session
    uv run extract_session.py --latest

    # Extract a specific session
    uv run extract_session.py --session-id abc123

    # Extract session for a specific project
    uv run extract_session.py --latest --cwd /path/to/project

    # Save to file
    uv run extract_session.py --latest --output /tmp/session.md
        """
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List recent sessions"
    )
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Extract the most recent session"
    )
    parser.add_argument(
        "--session-id",
        type=str,
        help="Session ID to extract"
    )
    parser.add_argument(
        "--cwd",
        type=str,
        help="Filter sessions by working directory"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--max-messages",
        type=int,
        default=100,
        help="Maximum number of messages to include (default: 100)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Number of sessions to list (default: 20)"
    )

    args = parser.parse_args()

    if args.list:
        sessions = list_sessions(cwd=args.cwd, limit=args.limit)
        if not sessions:
            print("No sessions found.", file=sys.stderr)
            sys.exit(1)

        print(f"{'ID':<40} {'Modified':<20} {'Size':<10} {'CWD'}")
        print("-" * 100)
        for s in sessions:
            modified = s["modified"].strftime("%Y-%m-%d %H:%M")
            size = f"{s['size'] / 1024:.1f}KB"
            cwd = s["cwd"]
            if len(cwd) > 40:
                cwd = "..." + cwd[-37:]
            print(f"{s['id']:<40} {modified:<20} {size:<10} {cwd}")
        sys.exit(0)

    # Determine which session to extract
    session_file = None

    if args.session_id:
        session_file = find_session_file(args.session_id, cwd=args.cwd)
        if not session_file:
            print(f"Session not found: {args.session_id}", file=sys.stderr)
            sys.exit(1)
    elif args.latest:
        sessions = list_sessions(cwd=args.cwd, limit=1)
        if not sessions:
            print("No sessions found.", file=sys.stderr)
            sys.exit(1)
        session_file = sessions[0]["file"]
    else:
        parser.print_help()
        sys.exit(1)

    # Extract the session
    transcript = extract_session(session_file, max_messages=args.max_messages)

    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(transcript)
        print(f"Transcript saved to: {output_path}", file=sys.stderr)
    else:
        print(transcript)


if __name__ == "__main__":
    main()
