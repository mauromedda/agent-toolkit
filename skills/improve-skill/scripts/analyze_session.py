# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
# ABOUTME: Analyze Claude Code session transcripts to generate skill improvement prompts
# ABOUTME: Produces structured analysis and recommendations for skill enhancement

"""
Analyze Claude Code session transcripts to improve or create skills.

Usage:
    uv run analyze_session.py --help
    uv run analyze_session.py --transcript /tmp/session.md --skill ~/.claude/skills/foo/SKILL.md
    uv run analyze_session.py --transcript /tmp/session.md --create-skill
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional


def extract_struggles(transcript: str) -> list[str]:
    """Extract specific struggle patterns from transcript."""
    struggles = []

    struggle_patterns = [
        (r"(?i)(couldn't find|can't find|not found|doesn't exist)", "Missing files or resources"),
        (r"(?i)(permission denied|access denied|forbidden)", "Permission/access issues"),
        (r"(?i)(import error|module not found|no such module)", "Dependency or import issues"),
        (r"(?i)(timeout|took too long|slow)", "Performance or timeout issues"),
        (r"(?i)(wrong format|invalid|malformed)", "Data format or syntax issues"),
        (r"(?i)(unexpected|doesn't match|behavior)", "Unexpected behavior"),
        (r"(?i)(conflicting|conflicts|incompatible)", "Conflicts or incompatibility"),
    ]

    for pattern, label in struggle_patterns:
        if re.search(pattern, transcript):
            struggles.append(label)

    return list(set(struggles))  # Deduplicate


def extract_missing_info(transcript: str) -> list[str]:
    """Extract what information was missing from documentation."""
    missing = []

    missing_patterns = [
        (r"(?i)(had to|needed to|should have|didn't know)", "Implicit knowledge"),
        (r"(?i)(example|wasn't shown|no example)", "Missing examples"),
        (r"(?i)(parameter|option|flag|argument)", "Missing parameter documentation"),
        (r"(?i)(edge case|special case|exception)", "Unhandled edge cases"),
        (r"(?i)(workaround|hack|temporary fix)", "Lack of proper solution"),
    ]

    for pattern, label in missing_patterns:
        if re.search(pattern, transcript):
            missing.append(label)

    return list(set(missing))


def extract_success_patterns(transcript: str) -> list[str]:
    """Extract what approaches led to success."""
    successes = []

    success_patterns = [
        (r"(?i)(first try|right away|immediately)", "Direct approach worked"),
        (r"(?i)(simple|straightforward|easy)", "Simplicity effective"),
        (r"(?i)(then\s+\w+\s+(worked|succeeded|completed))", "Sequential approach effective"),
        (r"(?i)(combined|together|both)", "Combining approaches worked"),
        (r"(?i)(documented well|clear|explicit)", "Good documentation helped"),
    ]

    for pattern, label in success_patterns:
        if re.search(pattern, transcript):
            successes.append(label)

    return list(set(successes))


def count_patterns(transcript: str) -> dict:
    """Count patterns in the transcript that might indicate issues or successes."""
    patterns = {
        "tool_uses": len(re.findall(r"\*\*Tool:", transcript)),
        "tool_results": len(re.findall(r"\*\*Tool Result:", transcript)),
        "errors": len(re.findall(r"(?i)(error|failed|exception|traceback)", transcript)),
        "retries": len(re.findall(r"(?i)(try again|retry|let me try|another approach)", transcript)),
        "user_corrections": len(re.findall(r"(?i)(no,|not that|wrong|instead|actually)", transcript)),
        "confusion": len(re.findall(r"(?i)(confused|unclear|not sure|don't understand)", transcript)),
        "skill_invocations": len(re.findall(r"(?i)(skill:|/\w+)", transcript)),
        "thinking_blocks": len(re.findall(r"\*\[Thinking:", transcript)),
        "success_markers": len(re.findall(r"(?i)(successfully|completed|done|worked|fixed)", transcript)),
        "struggles": extract_struggles(transcript),
        "missing_info": extract_missing_info(transcript),
        "success_patterns": extract_success_patterns(transcript),
    }
    return patterns


def generate_improvement_prompt(
    transcript_path: Path,
    skill_path: Optional[Path] = None,
) -> str:
    """Generate a prompt for improving an existing skill based on session analysis."""
    transcript = transcript_path.read_text()
    patterns = count_patterns(transcript)

    # Read skill if provided
    skill_content = ""
    if skill_path and skill_path.exists():
        skill_content = skill_path.read_text()

    prompt_lines = [
        "# Skill Improvement Analysis",
        "",
        "## Task",
        "",
        "Analyze the session transcript below to identify improvements for the skill.",
        "Focus on gaps, confusion, and what could be better documented.",
        "",
        "## Session Statistics",
        "",
        f"- Tool invocations: {patterns['tool_uses']}",
        f"- Errors encountered: {patterns['errors']}",
        f"- Retries/corrections: {patterns['retries']}",
        f"- User corrections: {patterns['user_corrections']}",
        f"- Confusion indicators: {patterns['confusion']}",
        f"- Success markers: {patterns['success_markers']}",
        "",
        "## Automatically Detected Issues",
        "",
    ]

    # Add detected struggles
    if patterns["struggles"]:
        prompt_lines.append("**Struggles Identified:**")
        for s in patterns["struggles"]:
            prompt_lines.append(f"- {s}")
        prompt_lines.append("")

    # Add missing info
    if patterns["missing_info"]:
        prompt_lines.append("**Missing Information:**")
        for m in patterns["missing_info"]:
            prompt_lines.append(f"- {m}")
        prompt_lines.append("")

    # Add success patterns
    if patterns["success_patterns"]:
        prompt_lines.append("**What Worked:**")
        for s in patterns["success_patterns"]:
            prompt_lines.append(f"- {s}")
        prompt_lines.append("")

    prompt_lines.extend([
        "## Analysis Framework",
        "",
        "Review the transcript and identify:",
        "",
        "### 1. Where I Struggled",
        "- What was unclear or missing from the skill documentation?",
        "- Where did I make wrong assumptions?",
        "- What tools or approaches did I try that didn't work?",
        "",
        "### 2. What Information Was Missing",
        "- What did I have to discover through trial and error?",
        "- What context would have helped me succeed faster?",
        "- What edge cases or variations weren't documented?",
        "",
        "### 3. What Worked Well",
        "- Which approaches led to success?",
        "- What patterns should be preserved or emphasized?",
        "",
        "### 4. Recommended Changes",
        "- Specific additions to the skill documentation",
        "- Examples that should be added",
        "- Trigger words that should be updated",
        "- Decision trees or workflows to clarify",
        "",
    ])

    if skill_content:
        prompt_lines.extend([
            "## Current Skill",
            "",
            "```markdown",
            skill_content,
            "```",
            "",
        ])

    prompt_lines.extend([
        "## Session Transcript",
        "",
        "```markdown",
        transcript,
        "```",
        "",
        "---",
        "",
        "## Your Analysis",
        "",
        "Provide a structured analysis with specific, actionable recommendations.",
        "Focus on what would have helped in THIS session.",
    ])

    return "\n".join(prompt_lines)


def generate_creation_prompt(transcript_path: Path) -> str:
    """Generate a prompt for creating a new skill from a session."""
    transcript = transcript_path.read_text()
    patterns = count_patterns(transcript)

    prompt_lines = [
        "# New Skill Creation",
        "",
        "## Task",
        "",
        "Analyze the session transcript below to create a new skill that captures",
        "the workflow demonstrated. Extract patterns, document key steps, and",
        "create reusable skill documentation.",
        "",
        "## Session Statistics",
        "",
        f"- Tool invocations: {patterns['tool_uses']}",
        f"- Errors encountered: {patterns['errors']}",
        f"- Retries/corrections: {patterns['retries']}",
        f"- Success markers: {patterns['success_markers']}",
        "",
        "## Analysis Framework",
        "",
        "### 1. Core Workflow",
        "- What was the main task being accomplished?",
        "- What were the key steps?",
        "- What tools were used?",
        "",
        "### 2. Key Patterns",
        "- What approaches worked well?",
        "- What decision points existed?",
        "- What was the successful sequence?",
        "",
        "### 3. Pitfalls to Document",
        "- What didn't work initially?",
        "- What workarounds were needed?",
        "- What edge cases were encountered?",
        "",
        "### 4. Skill Structure",
        "",
        "Create a skill with:",
        "",
        "```markdown",
        "---",
        "name: <skill-name>",
        "description: <clear description with trigger words>",
        "allowed-tools: <relevant tools>",
        "---",
        "",
        "# ABOUTME: <one-line purpose>",
        "# ABOUTME: <key context>",
        "",
        "# <Skill Title>",
        "",
        "## Quick Reference",
        "| Command | Purpose |",
        "|---------|---------|",
        "",
        "## Workflow",
        "<step-by-step guide>",
        "",
        "## Common Pitfalls",
        "<what to avoid>",
        "",
        "## Examples",
        "<practical examples>",
        "```",
        "",
        "## Session Transcript",
        "",
        "```markdown",
        transcript,
        "```",
        "",
        "---",
        "",
        "## Create the Skill",
        "",
        "Based on this session, create complete skill documentation.",
        "Include trigger words, decision trees, and practical examples.",
    ]

    return "\n".join(prompt_lines)


def generate_quick_analysis(transcript_path: Path) -> str:
    """Generate a quick analysis summary without a full prompt."""
    transcript = transcript_path.read_text()
    patterns = count_patterns(transcript)

    # Extract some context
    lines = transcript.split("\n")
    first_user_msg = ""
    for i, line in enumerate(lines):
        if "**User:**" in line:
            # Get the content after this line
            for j in range(i + 1, min(i + 10, len(lines))):
                if lines[j].strip() and not lines[j].startswith("#"):
                    first_user_msg = lines[j].strip()[:200]
                    break
            break

    output_lines = [
        "# Quick Session Analysis",
        "",
        "## Overview",
        "",
        f"**First User Request:** {first_user_msg}..." if first_user_msg else "",
        "",
        "## Metrics",
        "",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Tool invocations | {patterns['tool_uses']} |",
        f"| Tool results | {patterns['tool_results']} |",
        f"| Errors | {patterns['errors']} |",
        f"| Retries | {patterns['retries']} |",
        f"| User corrections | {patterns['user_corrections']} |",
        f"| Confusion indicators | {patterns['confusion']} |",
        f"| Success markers | {patterns['success_markers']} |",
        "",
    ]

    # Add identified patterns
    if patterns["struggles"]:
        output_lines.extend([
            "## Struggles Identified",
            "",
            *[f"- {s}" for s in patterns["struggles"]],
            "",
        ])

    if patterns["missing_info"]:
        output_lines.extend([
            "## Missing Information",
            "",
            *[f"- {m}" for m in patterns["missing_info"]],
            "",
        ])

    if patterns["success_patterns"]:
        output_lines.extend([
            "## Success Patterns",
            "",
            *[f"- {s}" for s in patterns["success_patterns"]],
            "",
        ])

    output_lines.extend([
        "## Assessment",
        "",
    ])

    # Generate simple assessment
    if patterns["errors"] > 3 or patterns["retries"] > 2:
        output_lines.append("- **High friction session** - multiple errors or retries detected")
    if patterns["user_corrections"] > 1:
        output_lines.append("- **Misalignment detected** - user had to correct the agent")
    if patterns["confusion"] > 0:
        output_lines.append("- **Confusion present** - agent expressed uncertainty")
    if patterns["success_markers"] > patterns["errors"]:
        output_lines.append("- **Overall successful** - more successes than errors")
    else:
        output_lines.append("- **Challenging session** - consider reviewing for improvements")

    output_lines.extend([
        "",
        "## Recommended Actions",
        "",
        "1. Review the full transcript for specific pain points",
        "2. Identify which skill was used (or should have been used)",
        "3. Run full analysis with `--skill` flag to generate improvement prompt",
    ])

    return "\n".join(output_lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Claude Code session transcripts for skill improvement",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Quick analysis of a session
    uv run analyze_session.py --transcript /tmp/session.md

    # Generate improvement prompt for existing skill
    uv run analyze_session.py --transcript /tmp/session.md \\
        --skill ~/.claude/skills/web-automation/SKILL.md

    # Generate prompt to create a new skill
    uv run analyze_session.py --transcript /tmp/session.md --create-skill

    # Save analysis to file
    uv run analyze_session.py --transcript /tmp/session.md --output /tmp/analysis.md
        """
    )

    parser.add_argument(
        "--transcript", "-t",
        type=str,
        required=True,
        help="Path to the session transcript markdown file"
    )
    parser.add_argument(
        "--skill", "-s",
        type=str,
        help="Path to existing skill SKILL.md to improve"
    )
    parser.add_argument(
        "--create-skill",
        action="store_true",
        help="Generate prompt for creating a new skill"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick analysis summary only (no full prompt)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path (default: stdout)"
    )

    args = parser.parse_args()

    transcript_path = Path(args.transcript)
    if not transcript_path.exists():
        print(f"Transcript not found: {transcript_path}", file=sys.stderr)
        sys.exit(1)

    # Generate appropriate output
    if args.quick:
        output = generate_quick_analysis(transcript_path)
    elif args.create_skill:
        output = generate_creation_prompt(transcript_path)
    elif args.skill:
        skill_path = Path(args.skill)
        if not skill_path.exists():
            print(f"Skill file not found: {skill_path}", file=sys.stderr)
            sys.exit(1)
        output = generate_improvement_prompt(transcript_path, skill_path)
    else:
        # Default to quick analysis
        output = generate_quick_analysis(transcript_path)

    # Write output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output)
        print(f"Analysis saved to: {output_path}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
