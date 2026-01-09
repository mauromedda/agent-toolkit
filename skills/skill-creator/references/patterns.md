# ABOUTME: Reference patterns for skill design
# ABOUTME: Sequential workflows, conditionals, templates, and organization

# Skill Design Patterns

Reference patterns for creating effective skills.

## Sequential Workflows

For multi-step processes, provide a clear overview followed by detailed steps:

```markdown
## Workflow Overview

Processing a document involves:

1. Validate input (run validate.py)
2. Extract content (run extract.py)
3. Transform data (run transform.py)
4. Generate output (run generate.py)

## Step 1: Validate Input

[Details for step 1]

## Step 2: Extract Content

[Details for step 2]
```

**Key principles:**
- Number steps explicitly
- Reference scripts by name
- Keep overview concise; details in individual sections

## Conditional Workflows

For tasks with branching logic, use decision trees:

```markdown
## Workflow Selection

1. Determine the operation type:
   - **Creating new content?** → See "Creation Workflow"
   - **Editing existing content?** → See "Editing Workflow"
   - **Analyzing content?** → See "Analysis Workflow"

## Creation Workflow

[Steps for creation]

## Editing Workflow

[Steps for editing]
```

**Alternative: Table format**

```markdown
| Condition | Action |
|-----------|--------|
| File exists | Use editing workflow |
| File missing | Use creation workflow |
| Read-only | Use analysis workflow |
```

## Output Templates

### Strict Templates (API responses, data formats)

```markdown
## Output Format

ALWAYS use this exact structure:

# Report Title

## Summary
[One paragraph overview]

## Findings
- Finding 1
- Finding 2

## Recommendations
1. Action 1
2. Action 2
```

### Flexible Templates (reports, documentation)

```markdown
## Output Format

Suggested structure (adapt as needed):

# Report Title

## Summary
[Overview - adjust length to content]

## Details
[Organize by topic; add/remove sections as appropriate]
```

## Input/Output Examples

For skills where output quality depends on examples:

```markdown
## Examples

**Input:** User uploaded quarterly sales data
**Output:**
- Created summary chart in output/sales-q4.png
- Identified top 3 performing regions
- Generated trend analysis

**Input:** User asks to compare two datasets
**Output:**
- Created comparison table
- Highlighted significant differences
- Noted data quality issues
```

## Progressive Disclosure

### Single Domain with Depth

```markdown
# Main Skill

## Quick Start

[Essential workflow - 5-10 lines]

## Common Operations

[Most frequent use cases]

## Advanced Features

See references/advanced.md for:
- Complex configurations
- Edge case handling
- Performance optimization
```

### Multiple Domains

```markdown
# API Client Skill

## Domain Selection

- **Authentication** → See references/auth.md
- **Data Operations** → See references/data.md
- **Admin Tasks** → See references/admin.md

## Quick Start

[Universal setup steps]
```

### Multiple Frameworks/Variants

```markdown
# Deployment Skill

## Provider Selection

Choose your target:
- **AWS** → See references/aws.md
- **GCP** → See references/gcp.md
- **Azure** → See references/azure.md

## Common Workflow

1. Configure credentials
2. Select provider-specific guide
3. Follow deployment steps
```

## Tables for Quick Reference

```markdown
## Quick Reference

| Script | Purpose | When to Use |
|--------|---------|-------------|
| init.py | Create new resource | Starting fresh |
| update.py | Modify existing | Changing config |
| validate.py | Check correctness | Before deployment |
| cleanup.py | Remove resources | After testing |
```

## Error Recovery Patterns

```markdown
## Troubleshooting

### Common Issues

| Error | Cause | Solution |
|-------|-------|----------|
| Permission denied | Missing auth | Run `auth.py` first |
| Not found | Wrong path | Check working directory |
| Timeout | Slow network | Increase timeout to 60s |

### Recovery Steps

If operation fails:
1. Check error message in output
2. Verify prerequisites are met
3. Retry with --verbose flag
4. See references/debugging.md for advanced troubleshooting
```

## Skill Chaining

When skills work together:

```markdown
## Integration with Other Skills

### Typical Workflow

1. Use **explore-skill** to understand the codebase
2. Use **this-skill** to make changes
3. Use **review-skill** to validate changes

### Handoff Pattern

After completing [operation], invoke [other-skill] with:
- Context: [what was done]
- Artifacts: [files created]
- Next step: [what other-skill should do]
```
