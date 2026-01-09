#!/usr/bin/env python3
# ABOUTME: Validate Claude Code skill structure and conventions
# ABOUTME: Checks frontmatter, ABOUTME headers, name format, and description
"""
Validate a Claude Code skill for proper structure and conventions.

Usage:
    uv run validate_skill.py <skill-directory>

Examples:
    uv run validate_skill.py ~/.claude/skills/my-skill
    uv run validate_skill.py . --verbose
"""
# /// script
# dependencies = ["pyyaml"]
# ///

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple

import yaml


class ValidationResult(NamedTuple):
    valid: bool
    errors: list[str]
    warnings: list[str]


ALLOWED_FRONTMATTER_KEYS = {"name", "description", "allowed-tools", "license", "metadata"}


def extract_frontmatter(content: str) -> tuple[dict | None, str, str]:
    """Extract YAML frontmatter and return (frontmatter, body, error)."""
    if not content.startswith("---"):
        return None, "", "SKILL.md must start with --- (YAML frontmatter)"

    match = re.match(r"^---\n(.*?)\n---\n?(.*)$", content, re.DOTALL)
    if not match:
        return None, "", "Invalid frontmatter format (missing closing ---)"

    frontmatter_text = match.group(1)
    body = match.group(2)

    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return None, "", "Frontmatter must be a YAML dictionary"
        return frontmatter, body, ""
    except yaml.YAMLError as e:
        return None, "", f"Invalid YAML in frontmatter: {e}"


def validate_name(name: str, directory_name: str) -> list[str]:
    """Validate skill name conventions."""
    errors = []

    if not isinstance(name, str):
        errors.append(f"name must be a string, got {type(name).__name__}")
        return errors

    name = name.strip()
    if not name:
        errors.append("name cannot be empty")
        return errors

    if not re.match(r"^[a-z0-9-]+$", name):
        errors.append(f"name '{name}' must be hyphen-case (lowercase, digits, hyphens only)")

    if name.startswith("-") or name.endswith("-"):
        errors.append(f"name '{name}' cannot start/end with hyphen")

    if "--" in name:
        errors.append(f"name '{name}' cannot contain consecutive hyphens")

    if len(name) > 64:
        errors.append(f"name too long ({len(name)} chars, max 64)")

    if name != directory_name:
        errors.append(f"name '{name}' does not match directory name '{directory_name}'")

    return errors


def validate_description(description: str) -> tuple[list[str], list[str]]:
    """Validate description conventions."""
    errors = []
    warnings = []

    if not isinstance(description, str):
        errors.append(f"description must be a string, got {type(description).__name__}")
        return errors, warnings

    description = description.strip()
    if not description:
        errors.append("description cannot be empty")
        return errors, warnings

    # Check for HTML/XML-like tags (e.g., <tag> or </tag>)
    # Allow standalone > for comparisons like ">100 lines"
    if re.search(r"<[^>]+>", description) or "<" in description:
        errors.append("description cannot contain HTML/XML-like tags or < character")

    if len(description) > 1024:
        errors.append(f"description too long ({len(description)} chars, max 1024)")

    if "trigger" not in description.lower():
        warnings.append("description should include trigger phrases (e.g., 'Triggers on \"x\", \"y\"')")

    return errors, warnings


def validate_aboutme(body: str) -> tuple[list[str], list[str]]:
    """Validate ABOUTME headers are present after frontmatter."""
    errors = []
    warnings = []

    lines = body.strip().split("\n") if body.strip() else []
    aboutme_found = False

    for i, line in enumerate(lines[:10]):  # Check first 10 lines
        if line.strip().startswith("# ABOUTME:"):
            aboutme_found = True
            break
        elif line.strip().startswith("#") and not line.strip().startswith("# ABOUTME"):
            # Found a heading before ABOUTME
            if not aboutme_found:
                warnings.append(
                    "ABOUTME headers should appear before the first heading "
                    "(immediately after closing ---)"
                )
            break

    if not aboutme_found:
        warnings.append("Missing ABOUTME headers after frontmatter (recommended: 2 lines)")

    return errors, warnings


def validate_skill(skill_path: Path, verbose: bool = False) -> ValidationResult:
    """Validate a skill directory."""
    errors = []
    warnings = []

    # Check directory exists
    if not skill_path.exists():
        return ValidationResult(False, [f"Directory not found: {skill_path}"], [])

    if not skill_path.is_dir():
        return ValidationResult(False, [f"Not a directory: {skill_path}"], [])

    # Check SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return ValidationResult(False, ["SKILL.md not found"], [])

    # Read and parse
    content = skill_md.read_text()
    frontmatter, body, fm_error = extract_frontmatter(content)

    if fm_error:
        return ValidationResult(False, [fm_error], [])

    # Validate frontmatter keys
    unexpected_keys = set(frontmatter.keys()) - ALLOWED_FRONTMATTER_KEYS
    if unexpected_keys:
        errors.append(
            f"Unexpected frontmatter keys: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed: {', '.join(sorted(ALLOWED_FRONTMATTER_KEYS))}"
        )

    # Validate required fields
    if "name" not in frontmatter:
        errors.append("Missing required field: name")
    else:
        errors.extend(validate_name(frontmatter["name"], skill_path.name))

    if "description" not in frontmatter:
        errors.append("Missing required field: description")
    else:
        desc_errors, desc_warnings = validate_description(frontmatter["description"])
        errors.extend(desc_errors)
        warnings.extend(desc_warnings)

    # Validate ABOUTME headers
    aboutme_errors, aboutme_warnings = validate_aboutme(body)
    errors.extend(aboutme_errors)
    warnings.extend(aboutme_warnings)

    # Check for TODO placeholders
    if "[TODO:" in content:
        warnings.append("SKILL.md contains [TODO:] placeholders that need completion")

    return ValidationResult(len(errors) == 0, errors, warnings)


def main():
    parser = argparse.ArgumentParser(
        description="Validate a Claude Code skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run validate_skill.py ~/.claude/skills/my-skill
  uv run validate_skill.py . --verbose
        """,
    )
    parser.add_argument("path", help="Path to skill directory")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show warnings")

    args = parser.parse_args()
    skill_path = Path(args.path).expanduser().resolve()

    result = validate_skill(skill_path, args.verbose)

    if result.errors:
        print(f"INVALID: {skill_path.name}")
        for error in result.errors:
            print(f"  - {error}")

    if args.verbose and result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"  - {warning}")

    if result.valid:
        print(f"VALID: {skill_path.name}")
        if result.warnings and not args.verbose:
            print(f"  ({len(result.warnings)} warnings, use --verbose to see)")

    sys.exit(0 if result.valid else 1)


if __name__ == "__main__":
    main()
