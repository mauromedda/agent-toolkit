# ABOUTME: Templates for spec-driven development artifacts
# ABOUTME: Spec files, task files, and README configuration

# Spec-Driven Development Templates

Copy and adapt these templates when creating spec artifacts.

---

## Spec File Template

**Filename**: `specs/{feature-slug}.md`

```markdown
# Spec: {Feature Name}

**Status**: DRAFT | APPROVED | IN_PROGRESS | COMPLETED
**Created**: {YYYY-MM-DD}
**Last Updated**: {YYYY-MM-DD}

---

## 1. Objective

{One paragraph: What are we building and WHY? What user/business value does it provide?}

---

## 2. Requirements

### Functional Requirements

- [ ] FR1: {System must do X when Y happens}
- [ ] FR2: {User can perform Z action}
- [ ] FR3: {Component A integrates with B}

### Non-Functional Requirements

- [ ] NFR1: Performance - {e.g., Response time < 200ms}
- [ ] NFR2: Security - {e.g., Authentication required, input validation}
- [ ] NFR3: Reliability - {e.g., 99.9% uptime, graceful degradation}

### Out of Scope

- {Explicitly list what we are NOT building}
- {Prevents scope creep}

---

## 3. Technical Strategy

### Language & Stack

- **Primary Language**: {Go/Python/TypeScript/etc.}
- **Framework**: {If applicable}
- **Dependencies**: {Key libraries/tools}

### Architecture

{Brief description of the architectural approach}

**Key Components**:
1. {Component A} - {Purpose}
2. {Component B} - {Purpose}
3. {Component C} - {Purpose}

**Data Flow**:
```
{Simple ASCII diagram if helpful}
Input -> Processing -> Output
```

### Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| {Decision 1} | {Choice} | {Why} |
| {Decision 2} | {Choice} | {Why} |

---

## 4. Acceptance Criteria

{How do we know this feature is complete?}

- [ ] AC1: {Specific, testable criterion}
- [ ] AC2: {Specific, testable criterion}
- [ ] AC3: {Specific, testable criterion}

---

## 5. Open Questions

{Questions that MUST be answered before /tasks}

1. {Question about scope/behavior?}
2. {Question about edge cases?}
3. {Question about integration?}

---

## 6. References

- {Link to related docs}
- {Link to existing code}
- {Link to external resources}
```

---

## Task File Template

**Filename**: `specs/{feature-slug}.tasks.md`

```markdown
# Tasks: {Feature Name}

**Spec**: ./{feature-slug}.md
**Created**: {YYYY-MM-DD}
**Status**: PENDING | IN_PROGRESS | COMPLETED

---

## Context

{2-3 sentence summary from spec: what we're building and key technical decisions}

---

## Prerequisites

- [ ] {Any setup needed before starting}
- [ ] {Dependencies to install}
- [ ] {Configuration to set}

---

## Tasks

### Phase 1: Foundation

- [ ] **Task 1**: {High-level task description}
  - Acceptance: {How to verify completion}
  - Files: {Expected files to create/modify}

- [ ] **Task 2**: {High-level task description}
  - Acceptance: {How to verify completion}
  - Files: {Expected files to create/modify}

### Phase 2: Core Implementation

- [ ] **Task 3**: {High-level task description}
  - Acceptance: {How to verify completion}
  - Files: {Expected files to create/modify}

- [ ] **Task 4**: {High-level task description}
  - Acceptance: {How to verify completion}
  - Files: {Expected files to create/modify}

### Phase 3: Integration & Polish

- [ ] **Task 5**: {Integration task}
  - Acceptance: {How to verify completion}

- [ ] **Task 6**: {Documentation/cleanup task}
  - Acceptance: {How to verify completion}

---

## Completion Checklist

- [ ] All tasks marked complete
- [ ] All tests passing
- [ ] Pre-commit hooks passing
- [ ] Spec acceptance criteria met
- [ ] Code reviewed (if >100 lines or >3 files)

---

## Notes

{Space for execution notes, blockers encountered, decisions made during implementation}
```

---

## README Configuration Template

**Filename**: `specs/README.md`

```markdown
# Specs Configuration

Project-specific overrides for spec-driven development.

---

## Language Configuration

```yaml
primary: golang          # Main language for this project
secondary:               # Additional languages
  - python
  - bash
```

---

## Project Conventions

### Required Spec Sections

- [ ] Security considerations (for all specs)
- [ ] Rollback plan (for infrastructure changes)
- [ ] Migration strategy (for data changes)

### Naming Conventions

- Spec files: `{feature-name}.md` (kebab-case)
- Task files: `{feature-name}.tasks.md`
- Branch naming: `feature/{spec-name}`

---

## Workflow Overrides

### Before `/tasks`

- {Any project-specific validation}
- {Required approvals}

### During `/run`

- Always invoke `/trivy` for security scan
- Require Gemini review for specs touching auth/*
- Run integration tests after each task

### After Completion

- {Deployment steps}
- {Notification requirements}

---

## Custom Templates

Override default templates:

```yaml
spec_template: ./templates/spec.md
task_template: ./templates/tasks.md
```

---

## Auto-Invoke Rules

| Condition | Action |
|-----------|--------|
| Files in `internal/auth/` | Always security review |
| Changes to `*.tf` | Run `terraform validate` |
| New dependencies | Run `/trivy` scan |

---

## Team Notes

{Project-specific guidance, gotchas, or context}
```

---

## Minimal Spec Template (Quick Start)

For simple features, use this condensed version:

```markdown
# Spec: {Feature Name}

**Status**: DRAFT

## Objective
{What and why in 2-3 sentences}

## Requirements
- [ ] {Requirement 1}
- [ ] {Requirement 2}

## Approach
{Brief technical strategy}

## Open Questions
1. {Question?}
```

---

## Task Checklist Format

Alternative compact format for simple task lists:

```markdown
# Tasks: {Feature Name}
**Spec**: ./{slug}.md

## Checklist
- [ ] Set up project structure
- [ ] Implement core logic
- [ ] Add tests
- [ ] Wire up integration
- [ ] Update documentation

## Done When
- All tests pass
- Pre-commit hooks pass
```
