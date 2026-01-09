# ABOUTME: Test framework detection and unified test runner documentation
# ABOUTME: Covers server auto-start, framework detection, and test execution

# Test Framework Integration

## Unified Test Runner

Use `test_utils.py` to detect frameworks and run tests in any project:

```bash
# Detect test frameworks only
uv run ~/.claude/skills/web-automation/scripts/test_utils.py /path/to/repo --detect-only

# Run all detected tests
uv run ~/.claude/skills/web-automation/scripts/test_utils.py /path/to/repo --run

# Run tests with server auto-start (for E2E)
uv run ~/.claude/skills/web-automation/scripts/test_utils.py /path/to/repo --run --with-server

# Run specific framework only
uv run ~/.claude/skills/web-automation/scripts/test_utils.py /path/to/repo --run --framework playwright

# Filter tests by name pattern
uv run ~/.claude/skills/web-automation/scripts/test_utils.py /path/to/repo --run --filter "login"
```

## Supported Test Frameworks

| Framework | Language | Detection |
|-----------|----------|-----------|
| Playwright | JS/TS | `@playwright/test` in package.json, playwright.config.js |
| Jest | JS/TS | `jest` in package.json, jest.config.js |
| Vitest | JS/TS | `vitest` in package.json |
| Mocha | JS/TS | `mocha` in package.json |
| Cypress | JS/TS | `cypress` in package.json |
| pytest | Python | `pytest` in requirements.txt/pyproject.toml, conftest.py |
| unittest | Python | test/ or tests/ directory |

## Server Detection Strategy

Check for these files in the repository root:

| File | Project Type | Dev Server |
|------|--------------|------------|
| `hugo.toml` / `config.toml` | Hugo | `hugo server` |
| `package.json` | Node.js | npm/yarn/pnpm |
| `pyproject.toml` | Python (modern) | uvicorn, flask, django |
| `requirements.txt` | Python (legacy) | same as above |
| `Cargo.toml` | Rust | `cargo run` |
| `go.mod` | Go | `go run` |
| `Gemfile` | Ruby | `rails server` |

**Note**: Hugo is detected first since Hugo projects often include `package.json` for asset pipelines.

## Server Auto-Start

When using `--with-server`, the script:

1. Detects the project type (Hugo, Node.js, Python)
2. Starts the appropriate dev server in background
3. Waits for server to be ready
4. Runs tests
5. Stops the server automatically

| Project Type | Server Command | Port |
|--------------|----------------|------|
| Hugo | `hugo server -D` | 1313 |
| Node.js (Next) | `npm run dev` | 3000 |
| Node.js (Vite) | `npm run dev` | 5173 |
| Python (FastAPI) | `uvicorn main:app` | 8000 |
| Python (Flask) | `flask run` | 5000 |
| Python (Django) | `python manage.py runserver` | 8000 |

## Server Utils

Use `scripts/server_utils.py` to detect and manage servers:

```bash
# Detect project type only
uv run ~/.claude/skills/web-automation/scripts/server_utils.py /path/to/repo --detect-only

# Detect and start server
uv run ~/.claude/skills/web-automation/scripts/server_utils.py /path/to/repo --start
```

Output:
```
=== PROJECT DETECTION ===
  Type: nodejs
  Framework: next
  Start command: npm run dev
  Port: 3000
  URL: http://localhost:3000
```

## Typical Workflow

```bash
# 1. Detect what's available
uv run ~/.claude/skills/web-automation/scripts/test_utils.py . --detect-only

# 2. Run E2E tests with server
uv run ~/.claude/skills/web-automation/scripts/test_utils.py . --run --with-server --framework playwright

# 3. Run unit tests (no server needed)
uv run ~/.claude/skills/web-automation/scripts/test_utils.py . --run --framework jest
```
