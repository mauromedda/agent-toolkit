# ABOUTME: Wrapper around shared server detection library
# ABOUTME: Provides CLI interface for server detection and startup

"""
Server Utilities

Detects project type from repository structure and manages dev server lifecycle.
Uses shared server_detection library from ~/.claude/lib/

Usage:
    python server_utils.py <repo_path> [--start] [--detect-only]

Example:
    python server_utils.py /path/to/project --detect-only
    python server_utils.py . --start
"""

import sys
from pathlib import Path

# Import from shared library
sys.path.insert(0, str(Path.home() / ".claude" / "lib"))
from server_detection import (
    detect_project,
    start_server,
    print_project_info,
    is_port_in_use,
    ProjectInfo,
)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Detect project type and manage dev server lifecycle.",
        epilog="Example: uv run server_utils.py /path/to/project --detect-only",
    )
    parser.add_argument(
        "repo_path",
        help="Path to the repository to analyze (e.g., . or /path/to/project)",
    )
    parser.add_argument(
        "--detect-only", "-d",
        action="store_true",
        help="Only detect project type, do not start server",
    )
    parser.add_argument(
        "--start", "-s",
        action="store_true",
        help="Start the detected dev server and stream output",
    )

    args = parser.parse_args()

    print(f"Analyzing repository: {args.repo_path}")
    project = detect_project(args.repo_path)
    print_project_info(project)

    if args.detect_only:
        sys.exit(0)

    if args.start:
        print(f"\nStarting server...")
        try:
            proc = start_server(project)
            print(f"Server process started (PID: {proc.pid})")
            print(f"Waiting for server at {project.url}...")

            if wait_for_server(project.url):
                print(f"Server is ready at {project.url}")
                print("Press Ctrl+C to stop")

                # Stream output
                try:
                    while True:
                        line = proc.stdout.readline()
                        if line:
                            print(f"  {line.rstrip()}")
                        elif proc.poll() is not None:
                            break
                except KeyboardInterrupt:
                    print("\nStopping server...")
                    proc.terminate()
                    proc.wait()
                    print("Server stopped")
            else:
                print(f"Server failed to start within timeout")
                proc.terminate()
                sys.exit(1)

        except RuntimeError as e:
            print(f"Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
