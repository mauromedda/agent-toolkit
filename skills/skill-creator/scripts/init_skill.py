#!/usr/bin/env python3
# ABOUTME: Initialize a new Claude Code skill with proper structure
# ABOUTME: Creates SKILL.md with frontmatter, ABOUTME headers, and optional resource dirs
"""
Initialize a new Claude Code skill with proper structure.

Usage:
    uv run init_skill.py <skill-name> --path <directory>

Examples:
    uv run init_skill.py my-api-helper --path ~/.claude/skills
    uv run init_skill.py data-analyzer --path /path/to/skills
"""

import argparse
import re
import sys
from pathlib import Path


def to_title_case(name: str) -> str:
    """Convert hyphen-case to Title Case."""
    return " ".join(word.capitalize() for word in name.split("-"))


def validate_name(name: str) -> tuple[bool, str]:
    """Validate skill name follows conventions."""
    if not name:
        return False, "Name cannot be empty"
    if not re.match(r"^[a-z0-9-]+$", name):
        return False, "Name must be hyphen-case (lowercase, digits, hyphens only)"
    if name.startswith("-") or name.endswith("-"):
        return False, "Name cannot start or end with hyphen"
    if "--" in name:
        return False, "Name cannot contain consecutive hyphens"
    if len(name) > 64:
        return False, f"Name too long ({len(name)} chars, max 64)"
    return True, ""


def create_skill_md(name: str, title: str) -> str:
    """Generate SKILL.md content with proper structure."""
    return f'''---
name: {name}
description: >-
  [TODO: Describe what this skill does and WHEN to use it.
  Include trigger phrases: Triggers on "keyword1", "keyword2".]
allowed-tools: Read, Write, Edit, Bash
---

# ABOUTME: [TODO: Brief description of skill purpose]
# ABOUTME: [TODO: Key context or dependencies]

# {title}

[TODO: Write skill instructions here]

## Overview

[TODO: 1-2 sentences explaining what this skill enables]

## When to Use

[TODO: Describe specific scenarios that trigger this skill]

## Workflow

[TODO: Add workflow steps, decision trees, or instructions]

## Resources

[TODO: Document any scripts, references, or assets if added]
'''


def init_skill(name: str, path: str, with_resources: bool = False) -> bool:
    """Initialize a new skill directory with proper structure."""
    valid, error = validate_name(name)
    if not valid:
        print(f"Error: {error}")
        return False

    base_path = Path(path).expanduser().resolve()
    skill_dir = base_path / name

    if skill_dir.exists():
        print(f"Error: Directory already exists: {skill_dir}")
        return False

    try:
        skill_dir.mkdir(parents=True)
        print(f"Created: {skill_dir}")
    except OSError as e:
        print(f"Error creating directory: {e}")
        return False

    title = to_title_case(name)
    skill_md = skill_dir / "SKILL.md"

    try:
        skill_md.write_text(create_skill_md(name, title))
        print(f"Created: {skill_md.name}")
    except OSError as e:
        print(f"Error writing SKILL.md: {e}")
        return False

    if with_resources:
        for subdir in ["scripts", "references"]:
            resource_dir = skill_dir / subdir
            resource_dir.mkdir()
            print(f"Created: {subdir}/")

    print(f"\nSkill '{name}' initialized at {skill_dir}")
    print("\nNext steps:")
    print("1. Edit SKILL.md: update description with trigger phrases")
    print("2. Write ABOUTME headers describing the skill")
    print("3. Add workflow instructions")
    print("4. Validate: uv run validate_skill.py", skill_dir)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new Claude Code skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run init_skill.py my-api-helper --path ~/.claude/skills
  uv run init_skill.py data-analyzer --path ~/.claude/skills --with-resources
        """,
    )
    parser.add_argument("name", help="Skill name (hyphen-case: my-skill-name)")
    parser.add_argument(
        "--path",
        required=True,
        help="Directory where skill folder will be created",
    )
    parser.add_argument(
        "--with-resources",
        action="store_true",
        help="Create scripts/ and references/ subdirectories",
    )

    args = parser.parse_args()

    success = init_skill(args.name, args.path, args.with_resources)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
