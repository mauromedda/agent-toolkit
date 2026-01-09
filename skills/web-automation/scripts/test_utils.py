# ABOUTME: Helper utilities for detecting test frameworks and running tests
# ABOUTME: Supports Jest, Playwright, Vitest, pytest, and other common test runners

# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Test Utilities

Detects test frameworks in a project and runs tests with optional server startup.

Usage:
    python test_utils.py <repo_path> [options]

Examples:
    python test_utils.py . --detect-only
    python test_utils.py . --run
    python test_utils.py . --run --with-server
    python test_utils.py . --run --filter "e2e"
"""

import json
import subprocess
import sys
import time
import signal
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import socket


@dataclass
class TestFramework:
    """Information about a detected test framework."""
    name: str
    runner: str
    command: list[str]
    config_file: Optional[str] = None
    test_dir: Optional[str] = None


@dataclass
class TestConfig:
    """Complete test configuration for a project."""
    project_type: str
    frameworks: list[TestFramework] = field(default_factory=list)
    has_e2e: bool = False
    has_unit: bool = False
    working_dir: Optional[str] = None
    server_required: bool = False
    server_command: Optional[list[str]] = None
    server_port: Optional[int] = None


def is_port_in_use(port: int) -> bool:
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def detect_js_test_frameworks(repo_path: Path, package_json: dict) -> list[TestFramework]:
    """Detect JavaScript/TypeScript test frameworks."""
    frameworks = []
    deps = {
        **package_json.get("dependencies", {}),
        **package_json.get("devDependencies", {}),
    }
    scripts = package_json.get("scripts", {})

    # Playwright
    if "@playwright/test" in deps or "playwright" in deps:
        config_file = None
        for cfg in ["playwright.config.ts", "playwright.config.js"]:
            if (repo_path / cfg).exists():
                config_file = cfg
                break

        cmd = ["npx", "playwright", "test"]
        frameworks.append(TestFramework(
            name="playwright",
            runner="npx",
            command=cmd,
            config_file=config_file,
            test_dir="tests/e2e" if (repo_path / "tests/e2e").exists() else "tests",
        ))

    # Jest
    if "jest" in deps or (repo_path / "jest.config.js").exists() or (repo_path / "jest.config.ts").exists():
        config_file = None
        for cfg in ["jest.config.js", "jest.config.ts", "jest.config.mjs"]:
            if (repo_path / cfg).exists():
                config_file = cfg
                break

        cmd = ["npx", "jest"]
        frameworks.append(TestFramework(
            name="jest",
            runner="npx",
            command=cmd,
            config_file=config_file,
        ))

    # Vitest
    if "vitest" in deps:
        cmd = ["npx", "vitest", "run"]
        frameworks.append(TestFramework(
            name="vitest",
            runner="npx",
            command=cmd,
            config_file="vitest.config.ts" if (repo_path / "vitest.config.ts").exists() else None,
        ))

    # Mocha
    if "mocha" in deps:
        cmd = ["npx", "mocha"]
        frameworks.append(TestFramework(
            name="mocha",
            runner="npx",
            command=cmd,
        ))

    # Cypress
    if "cypress" in deps:
        cmd = ["npx", "cypress", "run"]
        frameworks.append(TestFramework(
            name="cypress",
            runner="npx",
            command=cmd,
            config_file="cypress.config.js" if (repo_path / "cypress.config.js").exists() else None,
        ))

    # Check npm scripts for test commands
    if not frameworks:
        if "test" in scripts:
            cmd = ["npm", "test"]
            frameworks.append(TestFramework(
                name="npm-test",
                runner="npm",
                command=cmd,
            ))
        if "test:unit" in scripts:
            cmd = ["npm", "run", "test:unit"]
            frameworks.append(TestFramework(
                name="npm-test-unit",
                runner="npm",
                command=cmd,
            ))
        if "test:e2e" in scripts:
            cmd = ["npm", "run", "test:e2e"]
            frameworks.append(TestFramework(
                name="npm-test-e2e",
                runner="npm",
                command=cmd,
            ))

    return frameworks


def detect_python_test_frameworks(repo_path: Path) -> list[TestFramework]:
    """Detect Python test frameworks."""
    frameworks = []

    # Check for pytest
    has_pytest = False
    pyproject = repo_path / "pyproject.toml"
    requirements = repo_path / "requirements.txt"
    setup_py = repo_path / "setup.py"

    content = ""
    if pyproject.exists():
        content += pyproject.read_text()
    if requirements.exists():
        content += requirements.read_text()
    if setup_py.exists():
        content += setup_py.read_text()

    if "pytest" in content.lower() or (repo_path / "pytest.ini").exists() or (repo_path / "conftest.py").exists():
        has_pytest = True

    # Check for test directories
    test_dirs = []
    for d in ["tests", "test", "tests/unit", "tests/e2e", "tests/integration"]:
        if (repo_path / d).exists():
            test_dirs.append(d)

    if has_pytest or test_dirs:
        cmd = ["pytest", "-v"]
        if (repo_path / "pytest.ini").exists():
            config_file = "pytest.ini"
        elif (repo_path / "pyproject.toml").exists():
            config_file = "pyproject.toml"
        else:
            config_file = None

        frameworks.append(TestFramework(
            name="pytest",
            runner="pytest",
            command=cmd,
            config_file=config_file,
            test_dir="tests" if (repo_path / "tests").exists() else None,
        ))

    # Check for unittest
    if not frameworks and test_dirs:
        cmd = ["python", "-m", "unittest", "discover"]
        frameworks.append(TestFramework(
            name="unittest",
            runner="python",
            command=cmd,
            test_dir=test_dirs[0] if test_dirs else None,
        ))

    return frameworks


def detect_test_config(repo_path: str) -> TestConfig:
    """Detect all test frameworks and configuration for a project."""
    path = Path(repo_path).resolve()
    frameworks = []
    project_type = "unknown"
    server_required = False
    server_command = None
    server_port = None

    # Node.js project
    package_json_path = path / "package.json"
    if package_json_path.exists():
        with open(package_json_path) as f:
            package_json = json.load(f)

        project_type = "nodejs"
        frameworks.extend(detect_js_test_frameworks(path, package_json))

        # Check if server is needed for e2e tests
        scripts = package_json.get("scripts", {})
        if any(f.name in ["playwright", "cypress", "npm-test-e2e"] for f in frameworks):
            server_required = True
            if "dev" in scripts:
                server_command = ["npm", "run", "dev"]
            elif "serve" in scripts:
                server_command = ["npm", "run", "serve"]
            elif "start" in scripts:
                server_command = ["npm", "start"]

    # Hugo project (check for hugo.toml or config.toml with content/)
    hugo_configs = ["hugo.toml", "hugo.yaml", "hugo.json", "config.toml", "config.yaml"]
    has_hugo = any((path / cfg).exists() for cfg in hugo_configs) and (
        (path / "content").exists() or (path / "layouts").exists()
    )

    if has_hugo:
        project_type = "hugo"
        server_required = True
        server_command = ["hugo", "server", "-D"]
        server_port = 1313

        # Hugo projects often have package.json for test tooling
        # Only detect JS frameworks if not already detected above
        if package_json_path.exists() and not frameworks:
            with open(package_json_path) as f:
                package_json = json.load(f)
            frameworks.extend(detect_js_test_frameworks(path, package_json))

    # Python project
    has_python = any([
        (path / "pyproject.toml").exists(),
        (path / "requirements.txt").exists(),
        (path / "setup.py").exists(),
    ])

    if has_python and project_type == "unknown":
        project_type = "python"
        frameworks.extend(detect_python_test_frameworks(path))

        # Check for web frameworks that need server
        content = ""
        if (path / "pyproject.toml").exists():
            content += (path / "pyproject.toml").read_text()
        if (path / "requirements.txt").exists():
            content += (path / "requirements.txt").read_text()

        content_lower = content.lower()
        if any(fw in content_lower for fw in ["fastapi", "flask", "django", "uvicorn"]):
            server_required = True
            if "fastapi" in content_lower or "uvicorn" in content_lower:
                server_command = ["uvicorn", "main:app", "--reload"]
                server_port = 8000
            elif "flask" in content_lower:
                server_command = ["flask", "run"]
                server_port = 5000
            elif "django" in content_lower:
                server_command = ["python", "manage.py", "runserver"]
                server_port = 8000

    # Determine test types
    has_e2e = any(f.name in ["playwright", "cypress", "npm-test-e2e"] for f in frameworks)
    has_unit = any(f.name in ["jest", "vitest", "pytest", "unittest", "mocha", "npm-test-unit"] for f in frameworks)

    return TestConfig(
        project_type=project_type,
        frameworks=frameworks,
        has_e2e=has_e2e,
        has_unit=has_unit,
        working_dir=str(path),
        server_required=server_required,
        server_command=server_command,
        server_port=server_port,
    )


def wait_for_server(port: int, timeout: int = 60) -> bool:
    """Wait for server to be ready on the given port."""
    start = time.time()
    while time.time() - start < timeout:
        if is_port_in_use(port):
            return True
        time.sleep(0.5)
    return False


def run_tests(
    config: TestConfig,
    framework_filter: Optional[str] = None,
    test_filter: Optional[str] = None,
    with_server: bool = False,
    verbose: bool = True,
) -> dict:
    """Run tests with optional server startup."""
    results = {
        "success": True,
        "frameworks_run": [],
        "server_started": False,
        "errors": [],
    }

    server_proc = None

    try:
        # Start server if needed
        if with_server and config.server_required and config.server_command:
            port = config.server_port or 3000

            if is_port_in_use(port):
                if verbose:
                    print(f"Server already running on port {port}")
            else:
                if verbose:
                    print(f"Starting server: {' '.join(config.server_command)}")

                server_proc = subprocess.Popen(
                    config.server_command,
                    cwd=config.working_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    preexec_fn=os.setsid if os.name != 'nt' else None,
                )

                if verbose:
                    print(f"Waiting for server on port {port}...")

                if wait_for_server(port, timeout=30):
                    if verbose:
                        print(f"Server ready on port {port}")
                    results["server_started"] = True
                else:
                    results["errors"].append(f"Server failed to start on port {port}")
                    results["success"] = False
                    return results

        # Filter frameworks if specified
        frameworks_to_run = config.frameworks
        if framework_filter:
            frameworks_to_run = [f for f in frameworks_to_run if framework_filter.lower() in f.name.lower()]

        if not frameworks_to_run:
            if verbose:
                print("No test frameworks found to run")
            results["errors"].append("No test frameworks detected")
            return results

        # Run each framework
        for framework in frameworks_to_run:
            if verbose:
                print(f"\n{'='*60}")
                print(f"Running {framework.name} tests...")
                print(f"Command: {' '.join(framework.command)}")
                print('='*60)

            cmd = framework.command.copy()

            # Add test filter if provided
            if test_filter:
                if framework.name == "playwright":
                    cmd.extend(["--grep", test_filter])
                elif framework.name == "jest":
                    cmd.extend(["--testNamePattern", test_filter])
                elif framework.name == "pytest":
                    cmd.extend(["-k", test_filter])
                elif framework.name == "vitest":
                    cmd.extend(["--testNamePattern", test_filter])

            try:
                result = subprocess.run(
                    cmd,
                    cwd=config.working_dir,
                    capture_output=not verbose,
                    text=True,
                )

                framework_result = {
                    "name": framework.name,
                    "success": result.returncode == 0,
                    "returncode": result.returncode,
                }

                if not verbose:
                    framework_result["stdout"] = result.stdout
                    framework_result["stderr"] = result.stderr

                results["frameworks_run"].append(framework_result)

                if result.returncode != 0:
                    results["success"] = False

            except Exception as e:
                results["errors"].append(f"{framework.name}: {str(e)}")
                results["success"] = False

    finally:
        # Cleanup server
        if server_proc:
            if verbose:
                print("\nStopping server...")
            try:
                if os.name != 'nt':
                    os.killpg(os.getpgid(server_proc.pid), signal.SIGTERM)
                else:
                    server_proc.terminate()
                server_proc.wait(timeout=5)
            except Exception:
                server_proc.kill()

    return results


def print_test_config(config: TestConfig) -> None:
    """Print detected test configuration."""
    print(f"\n=== TEST CONFIGURATION ===")
    print(f"  Project type: {config.project_type}")
    print(f"  Working directory: {config.working_dir}")
    print(f"  Has unit tests: {config.has_unit}")
    print(f"  Has E2E tests: {config.has_e2e}")
    print(f"  Server required: {config.server_required}")

    if config.server_command:
        print(f"  Server command: {' '.join(config.server_command)}")
    if config.server_port:
        print(f"  Server port: {config.server_port}")

    print(f"\n  Detected frameworks ({len(config.frameworks)}):")
    for fw in config.frameworks:
        print(f"    - {fw.name}")
        print(f"      Command: {' '.join(fw.command)}")
        if fw.config_file:
            print(f"      Config: {fw.config_file}")
        if fw.test_dir:
            print(f"      Test dir: {fw.test_dir}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Detect test frameworks and run tests.",
        epilog="""
Examples:
    uv run test_utils.py . --detect-only
    uv run test_utils.py . --run
    uv run test_utils.py . --run --with-server
    uv run test_utils.py . --run --framework playwright
    uv run test_utils.py . --run --filter "login"
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "repo_path",
        help="Path to the repository to analyze",
    )
    parser.add_argument(
        "--detect-only", "-d",
        action="store_true",
        help="Only detect test frameworks, do not run tests",
    )
    parser.add_argument(
        "--run", "-r",
        action="store_true",
        help="Run detected tests",
    )
    parser.add_argument(
        "--with-server", "-s",
        action="store_true",
        help="Start server before running tests (for E2E)",
    )
    parser.add_argument(
        "--framework", "-f",
        help="Only run tests for specific framework (e.g., playwright, jest)",
    )
    parser.add_argument(
        "--filter", "-k",
        help="Filter tests by name pattern",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress output, only show summary",
    )

    args = parser.parse_args()

    print(f"Analyzing repository: {args.repo_path}")
    config = detect_test_config(args.repo_path)
    print_test_config(config)

    if args.detect_only:
        sys.exit(0)

    if args.run:
        print("\n" + "="*60)
        print("RUNNING TESTS")
        print("="*60)

        results = run_tests(
            config,
            framework_filter=args.framework,
            test_filter=args.filter,
            with_server=args.with_server,
            verbose=not args.quiet,
        )

        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        print(f"  Overall success: {results['success']}")
        print(f"  Server started: {results['server_started']}")

        for fw_result in results["frameworks_run"]:
            status = "PASS" if fw_result["success"] else "FAIL"
            print(f"  {fw_result['name']}: {status} (exit code: {fw_result['returncode']})")

        if results["errors"]:
            print(f"\n  Errors:")
            for err in results["errors"]:
                print(f"    - {err}")

        sys.exit(0 if results["success"] else 1)


if __name__ == "__main__":
    main()
