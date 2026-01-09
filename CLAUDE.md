# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Agent Toolkit is a collection of production-quality skills for Claude Code. Skills are domain-specific knowledge modules that Claude loads on-demand to provide specialized guidance for languages, workflows, and tooling.

## Repository Structure

```
agent-toolkit/
├── skills/                   # Claude Code skills (main content)
│   ├── <skill-name>/
│   │   ├── SKILL.md          # Skill definition (required)
│   │   ├── scripts/          # Executable helpers (optional)
│   │   ├── references/       # Additional docs (optional)
│   │   └── resources/        # Templates/assets (optional)
├── CLAUDE.md-example         # User-facing CLAUDE.md template
└── README.md                 # Public documentation
```

## Skill Categories

| Category | Skills |
|----------|--------|
| **Language** | `bash`, `golang`, `python`, `make`, `terraform` |
| **Workflow** | `scm`, `trivy`, `gemini-review`, `web-automation` |
| **Architecture** | `design-patterns`, `ast-grep` |
| **Meta** | `skill-creator`, `improve-skill` |

## Development Commands

### Validate a Skill

```bash
uv run skills/skill-creator/scripts/validate_skill.py skills/<skill-name>
uv run skills/skill-creator/scripts/validate_skill.py skills/<skill-name> --verbose
```

### Initialize a New Skill

```bash
uv run skills/skill-creator/scripts/init_skill.py <skill-name> --path skills
uv run skills/skill-creator/scripts/init_skill.py <skill-name> --path skills --with-resources
```

### Python Skill Tests

```bash
cd skills/python
uv sync
uv run pytest                      # Run all tests
uv run pytest tests/test_models.py # Single test file
uv run ruff check src/             # Lint
uv run mypy src/                   # Type check
```

## Skill File Conventions

### SKILL.md Structure

SKILL.md files must follow this exact structure:

```markdown
---
name: skill-name
description: >-
  What the skill does. Triggers on "keyword1", "keyword2".
allowed-tools: Read, Write, Edit, Bash
---

# ABOUTME: Brief description of skill purpose
# ABOUTME: Key context or dependencies

# Skill Title

[Content...]
```

**Critical rules:**
- YAML frontmatter `---` MUST be on line 1 (no blank lines before)
- ABOUTME headers go AFTER the closing `---`
- `name` must match the directory name exactly
- `name` must be hyphen-case (lowercase, digits, hyphens only)
- `description` must include trigger phrases: `Triggers on "x", "y"`
- `description` cannot contain `<` or HTML/XML-like tags

### Allowed Frontmatter Keys

Only these keys are valid: `name`, `description`, `allowed-tools`, `license`, `metadata`

### ABOUTME Headers

All new files (not just SKILL.md) must start with 2-line ABOUTME comment:

```python
# ABOUTME: Brief description of file purpose
# ABOUTME: Key context or dependencies
```

Adjust syntax for the language (`//`, `#`, `/**/`).

## Architecture Patterns

### Progressive Disclosure

Skills use a progressive disclosure pattern:
1. **SKILL.md**: Core instructions, quick reference, essential patterns
2. **references/**: Deep-dive documentation, workflows, edge cases
3. **scripts/**: Executable automation helpers
4. **resources/**: Templates, configs, assets

### Session Resume Checkpoints

Skills include "SESSION RESUMED" checkpoint boxes that remind Claude to verify state after context compaction. These appear in Go, Python, Bash, and Gemini-review skills.

### Integrated Workflows

Skills are designed to work together:
- `scm` → `trivy` → `gemini-review` (secure commit workflow)
- Language skills → `gemini-review` (code review integration)
- `skill-creator` → `improve-skill` (skill lifecycle)

## Validation Rules

When creating or modifying skills, ensure:

1. **Name validation**: hyphen-case, no leading/trailing hyphens, max 64 chars
2. **Description validation**: must contain "trigger", max 1024 chars, no `<` character
3. **ABOUTME presence**: recommended within first 10 lines after frontmatter
4. **No TODO placeholders**: `[TODO:]` patterns should be completed

## Common Patterns Across Language Skills

All language skills enforce:
- **ABOUTME headers** on new files
- **Quality gates** (linters, formatters, type checkers)
- **Session resume checkpoints** for context recovery
- **Quick reference tables** for common patterns
- **Anti-pattern detection** with fixes

| Language | Quality Gate |
|----------|-------------|
| Python | `ruff check`, `mypy` |
| Go | `golangci-lint`, `go build` |
| Bash | `shellcheck` |
| Make | Structure validation |
