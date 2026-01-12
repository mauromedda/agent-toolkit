# ABOUTME: Detailed workflow logic for spec-driven development
# ABOUTME: State machines, decision trees, and phase transitions

# Spec-Driven Development Workflow

Detailed implementation logic for each phase.

---

## State Machine

```
                    ┌─────────────┐
                    │   START     │
                    └──────┬──────┘
                           │ /spec.plan
                           v
                    ┌─────────────┐
          ┌────────>│    DRAFT    │<────────┐
          │         └──────┬──────┘         │
          │                │                │
          │    ┌───────────┼───────────┐    │
          │    │           │           │    │
          │    v           v           v    │
          │ /spec.refine    /spec.clarify    questions?
          │    │           │           │    │
          │    └───────────┼───────────┘    │
          │                │                │
          │                v                │
          │         ┌─────────────┐         │
          │    NO   │  Questions  │  YES    │
          └─────────┤  Resolved?  ├─────────┘
                    └──────┬──────┘
                           │ YES + /spec.tasks
                           v
                    ┌─────────────┐
                    │  APPROVED   │
                    └──────┬──────┘
                           │ /spec.run
                           v
                    ┌─────────────┐
          ┌────────>│ IN_PROGRESS │<────────┐
          │         └──────┬──────┘         │
          │                │                │
          │           ┌────┴────┐           │
          │           v         v           │
          │       blocked?   next task      │
          │           │         │           │
          │           v         │           │
          │      back to        └───────────┘
          │      DRAFT
          │
          │         all tasks done
          │                │
          │                v
          │         ┌─────────────┐
          └─────────┤  COMPLETED  │
                    └─────────────┘
```

---

## Phase 1: `/spec.plan` - Decision Tree

```
/spec.plan <intent>
    │
    ├─> Does specs/ exist?
    │       │
    │       ├─ NO ──> Create specs/ directory
    │       │         Create specs/README.md (default template)
    │       │
    │       └─ YES ─> Read specs/README.md for overrides
    │
    ├─> Detect project languages
    │       │
    │       ├─ Found go.mod ──────> primary: golang
    │       ├─ Found pyproject.toml > primary: python
    │       ├─ Found package.json ─> primary: typescript
    │       ├─ Found Cargo.toml ──> primary: rust
    │       ├─ Found *.tf ────────> primary: terraform
    │       └─ None found ────────> ASK user
    │
    ├─> Check README.md overrides
    │       │
    │       └─ Override found? ──> Use override instead
    │
    ├─> Generate slug from intent
    │       │
    │       └─ "I want to build user auth" ──> "user-auth"
    │
    ├─> Create specs/{slug}.md
    │       │
    │       └─ Use template, fill:
    │           - Status: DRAFT
    │           - Created: today
    │           - Objective: from intent
    │
    ├─> Analyze intent for questions
    │       │
    │       ├─ Scope unclear? ──────> Add scope question
    │       ├─ Edge cases? ─────────> Add edge case questions
    │       ├─ Integration points? ─> Add integration questions
    │       ├─ Security concerns? ──> Add security questions
    │       └─ Performance needs? ──> Add performance questions
    │
    └─> OUTPUT:
            - Spec file path
            - Detected language
            - Open questions (MUST be non-empty for new specs)
            - Next action: /spec.clarify or /spec.refine
```

### Question Generation Heuristics

| Intent Contains | Generate Questions About |
|-----------------|-------------------------|
| "API", "endpoint" | Auth, rate limiting, versioning |
| "database", "data" | Schema, migrations, backups |
| "user", "auth" | Providers, sessions, permissions |
| "file", "upload" | Size limits, formats, storage |
| "async", "background" | Retry policy, failure handling |
| "integration" | Error handling, timeouts |

---

## Phase 2: `/spec.refine` - Decision Tree

```
/spec.refine [section] [--gemini "prompt"]
    │
    ├─> Find active spec
    │       │
    │       ├─ No DRAFT specs ──> ERROR: "No active spec"
    │       └─ Multiple DRAFT ──> Use most recently modified
    │
    ├─> Load project context
    │       │
    │       ├─ Read specs/README.md
    │       ├─ Identify language skill to invoke
    │       └─ Load design-patterns skill
    │
    ├─> --gemini flag provided?
    │       │
    │       ├─ YES ─> Execute:
    │       │         gemini -m gemini-3-pro-preview "<prompt>" .
    │       │         Parse response, update spec
    │       │
    │       └─ NO ──> Analyze spec internally
    │
    ├─> Section specified?
    │       │
    │       ├─ "requirements" ──> Focus on FR/NFR refinement
    │       ├─ "solution" ─────> Focus on Technical Strategy
    │       ├─ "architecture" ─> Load design-patterns, analyze
    │       └─ None ───────────> Holistic refinement
    │
    ├─> Research actions
    │       │
    │       ├─ Search codebase for similar patterns
    │       ├─ Check language skill for conventions
    │       ├─ Identify reusable components
    │       └─ Note integration points
    │
    ├─> Update spec sections
    │       │
    │       ├─ Fill Technical Strategy if empty
    │       ├─ Add design decisions with rationale
    │       └─ Update requirements based on findings
    │
    ├─> Re-evaluate questions
    │       │
    │       ├─ Mark answered questions as resolved
    │       ├─ Add NEW questions if research reveals gaps
    │       └─ Count remaining open questions
    │
    └─> OUTPUT:
            - Changes made to spec
            - Remaining open questions
            - If questions == 0: "Ready for /spec.tasks"
            - If questions > 0: "Use /spec.clarify to resolve"
```

---

## Phase 3: `/spec.clarify` - Decision Tree

```
/spec.clarify <response>
    │
    ├─> Find active spec
    │       │
    │       └─ ERROR if no DRAFT spec found
    │
    ├─> Parse response format
    │       │
    │       ├─ "Q1: answer, Q2: answer" ──> Map to numbered Qs
    │       ├─ "1. answer 2. answer" ─────> Map by position
    │       └─ Free text ─────────────────> Apply to first open Q
    │
    ├─> For each answered question
    │       │
    │       ├─ Identify target section
    │       │       │
    │       │       ├─ Scope answer ──────> Requirements
    │       │       ├─ Technical choice ──> Technical Strategy
    │       │       ├─ Constraint ────────> Non-Functional Reqs
    │       │       └─ Edge case ─────────> Requirements + Tests
    │       │
    │       ├─ Update target section with answer
    │       └─ Remove from Open Questions
    │
    ├─> Analyze answer for new questions
    │       │
    │       ├─ Answer introduces new concept? ──> Add question
    │       ├─ Answer has "maybe" or "or"? ────> Add clarification
    │       └─ Answer contradicts existing? ───> Add resolution Q
    │
    ├─> Count remaining questions
    │       │
    │       ├─ 0 questions ──> "Spec ready for /spec.tasks"
    │       └─ N questions ──> "N questions remaining"
    │
    └─> OUTPUT:
            - What was updated
            - Remaining questions (if any)
            - Next action recommendation
```

---

## Phase 4: `/spec.tasks` - Decision Tree

```
/spec.tasks
    │
    ├─> Find active spec
    │       │
    │       ├─ No spec ───────────> ERROR: "Use /spec.plan first"
    │       └─ COMPLETED spec ────> ERROR: "Spec already done"
    │
    ├─> Validate readiness
    │       │
    │       ├─ Open Questions > 0?
    │       │       │
    │       │       └─ YES ──> ERROR: "Resolve questions first"
    │       │                  List remaining questions
    │       │                  Suggest: "/spec.clarify"
    │       │
    │       └─ Technical Strategy empty?
    │               │
    │               └─ YES ──> ERROR: "Need technical approach"
    │                          Suggest: "/spec.refine solution"
    │
    ├─> Mark spec as APPROVED
    │
    ├─> Analyze spec for task breakdown
    │       │
    │       ├─ Identify components from Technical Strategy
    │       ├─ Identify integration points
    │       ├─ Order by dependencies
    │       └─ Group into phases
    │
    ├─> Generate tasks (HIGH-LEVEL)
    │       │
    │       ├─ Phase 1: Foundation
    │       │       └─ Setup, scaffolding, interfaces
    │       │
    │       ├─ Phase 2: Core Implementation
    │       │       └─ Main components, one task per component
    │       │
    │       └─ Phase 3: Integration & Polish
    │               └─ Wiring, tests, docs
    │
    ├─> Create specs/{slug}.tasks.md
    │       │
    │       ├─ Link to spec
    │       ├─ Context summary
    │       ├─ Task list with acceptance criteria
    │       └─ Completion checklist
    │
    ├─> Present for review
    │       │
    │       └─ ASK: "Review tasks. Missing anything?"
    │
    └─> OUTPUT:
            - Task file path
            - Task count
            - "Use /spec.run to start execution"
```

---

## Phase 5: `/spec.run` - Decision Tree

```
/spec.run [task#]
    │
    ├─> Find task file
    │       │
    │       ├─ No .tasks.md ──> ERROR: "Use /spec.tasks first"
    │       └─ Found ─────────> Load task list
    │
    ├─> Select task
    │       │
    │       ├─ task# provided ──> Select specific task
    │       └─ No task# ────────> Select first unchecked
    │
    ├─> All tasks done?
    │       │
    │       └─ YES ──> Mark spec COMPLETED
    │                  OUTPUT: "All tasks complete!"
    │
    ├─> Load execution context
    │       │
    │       ├─ Read linked spec
    │       ├─ Read specs/README.md for overrides
    │       ├─ Detect file types for task
    │       └─ Queue language skill invocation
    │
    ├─> Execute task with TDD
    │       │
    │       ├─ Invoke TodoWrite for sub-steps
    │       │
    │       ├─> RED: Write failing test
    │       │       │
    │       │       ├─ Invoke language skill
    │       │       ├─ Create test file
    │       │       ├─ Run test, confirm FAIL
    │       │       └─ COMMIT: "test: add failing test for X"
    │       │
    │       ├─> GREEN: Minimal implementation
    │       │       │
    │       │       ├─ Invoke language skill
    │       │       ├─ Write minimal code
    │       │       ├─ Run test, confirm PASS
    │       │       └─ COMMIT: "feat: implement X"
    │       │
    │       └─> REFACTOR: Clean up
    │               │
    │               ├─ Apply Boy Scout Rule
    │               ├─ Run all tests, confirm PASS
    │               └─ COMMIT: "refactor: clean up X"
    │
    ├─> Check Gemini threshold
    │       │
    │       ├─ >100 lines OR >3 files? ──> Invoke Gemini review
    │       └─ Under threshold ──────────> Skip
    │
    ├─> Update task file
    │       │
    │       └─ Mark task [x] complete
    │
    ├─> Blocked?
    │       │
    │       ├─ YES ──> Document blocker
    │       │          Add question to spec
    │       │          Mark spec back to DRAFT
    │       │          OUTPUT: "Blocked. Use /spec.clarify"
    │       │
    │       └─ NO ───> Continue
    │
    └─> OUTPUT:
            - Task completed
            - Files modified
            - Tests passing
            - "Continue to next task? /spec.run"
```

---

## Iterative Refinement Loop

The core principle: **No ambiguity at execution time**.

```
┌─────────────────────────────────────────────────────────┐
│                  CLARITY GATE                           │
│                                                         │
│  Before /spec.tasks can proceed, ALL must be true:           │
│                                                         │
│  [ ] Open Questions section is EMPTY                    │
│  [ ] Technical Strategy is FILLED                       │
│  [ ] All requirements are SPECIFIC (no "maybe")         │
│  [ ] Acceptance criteria are TESTABLE                   │
│                                                         │
│  If ANY fails ──> Block and redirect to /spec.refine|/spec.clarify│
└─────────────────────────────────────────────────────────┘
```

### Ambiguity Signals

Watch for these in specs; they indicate need for `/spec.clarify`:

| Signal | Example | Action |
|--------|---------|--------|
| "maybe", "possibly" | "Maybe OAuth" | Clarify: Which auth? |
| "or", "either" | "REST or GraphQL" | Clarify: Which one? |
| "etc.", "and more" | "validation, etc." | Clarify: Full list? |
| "TBD", "TODO" | "Error handling TBD" | Clarify: What handling? |
| "later", "future" | "Add caching later" | Remove or scope now |
| Vague adjectives | "fast", "secure" | Clarify: Specific metric? |

---

## Error Recovery

### Blocked During Execution

```
Situation: /spec.run encounters unexpected complexity

1. STOP execution immediately
2. Document the blocker in task file:
   ```
   - [ ] **Task N**: Description
     - BLOCKED: [Describe the issue]
     - Needs: [What clarification is needed]
   ```
3. Update spec:
   - Add question to Open Questions
   - Change status back to DRAFT
4. Notify user:
   - "Execution blocked: [issue]"
   - "Added question to spec. Use /spec.clarify to resolve."
```

### Conflicting Requirements

```
Situation: Spec has contradictory requirements

1. Identify the conflict
2. Add clarifying question:
   "FR1 says X, but FR3 implies Y. Which takes precedence?"
3. Block /spec.tasks until resolved
```

### Missing Context

```
Situation: Can't proceed without external information

1. Check if info exists in codebase (search)
2. Check if specs/README.md provides guidance
3. If not found: Add question, block progression
```

---

## Session Resume Protocol

When Claude Code session is resumed:

```
1. Check specs/ directory exists
2. If exists:
   a. Find specs with status IN_PROGRESS
   b. Find .tasks.md with unchecked items
   c. Report findings:
      "Found: specs/auth.md (IN_PROGRESS)
       Tasks: 3/7 complete
       Next: Task 4 - Implement user repository"
   d. Ask: "Continue with /spec.run?"

3. If DRAFT specs exist:
   a. Report open questions count
   b. Suggest: "Use /spec.clarify to resolve N questions"
```
