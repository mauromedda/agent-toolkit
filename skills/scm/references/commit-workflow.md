# ABOUTME: Integrated commit workflow with Trivy security scanning for Claude Code
# ABOUTME: Documents the pre-commit security checkpoint and remediation planning process

# Secure Commit Workflow

**Parent**: `scm/SKILL.md`

This document defines the integrated commit workflow that includes security vulnerability scanning before commits.

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SECURE COMMIT WORKFLOW                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  START: User requests commit ("/commit-push" or "/commit-push-pr")      │
│                           │                                             │
│                           ▼                                             │
│              ┌────────────────────────┐                                 │
│              │  PHASE 1: DETECT       │                                 │
│              │  Analyze staged files  │                                 │
│              └───────────┬────────────┘                                 │
│                          │                                              │
│         ┌────────────────┼────────────────┐                             │
│         ▼                ▼                ▼                             │
│   ┌───────────┐   ┌───────────┐   ┌───────────┐                         │
│   │Dependencies│   │Dockerfile │   │   IaC    │                         │
│   │  changed?  │   │ changed?  │   │ changed? │                         │
│   └─────┬─────┘   └─────┬─────┘   └─────┬─────┘                         │
│         │               │               │                               │
│         └───────────────┼───────────────┘                               │
│                         │                                               │
│              ┌──────────▼───────────┐                                   │
│              │  Any triggers hit?   │                                   │
│              └──────────┬───────────┘                                   │
│                         │                                               │
│           ┌─────────────┴─────────────┐                                 │
│           ▼                           ▼                                 │
│       [YES]                        [NO]                                 │
│           │                           │                                 │
│           ▼                           │                                 │
│  ┌────────────────────┐               │                                 │
│  │  PHASE 2: SCAN     │               │                                 │
│  │  Run Trivy scans   │               │                                 │
│  └─────────┬──────────┘               │                                 │
│            │                          │                                 │
│   ┌────────┴────────┐                 │                                 │
│   ▼                 ▼                 │                                 │
│ [VULN]          [CLEAN]               │                                 │
│   │                 │                 │                                 │
│   ▼                 └────────┬────────┘                                 │
│  ┌────────────────────┐      │                                          │
│  │  PHASE 3: REMEDIATE│      │                                          │
│  │  Generate plan     │      │                                          │
│  │  Report findings   │      │                                          │
│  └─────────┬──────────┘      │                                          │
│            │                 │                                          │
│            ▼                 │                                          │
│   [User fixes issues]        │                                          │
│            │                 │                                          │
│            └────► RESTART ◄──┘                                          │
│                      │                                                  │
│                      ▼                                                  │
│         ┌────────────────────────┐                                      │
│         │  PHASE 4: REVIEW       │                                      │
│         │  Gemini (if threshold) │                                      │
│         └───────────┬────────────┘                                      │
│                     │                                                   │
│                     ▼                                                   │
│         ┌────────────────────────┐                                      │
│         │  PHASE 5: COMMIT       │                                      │
│         │  Conventional Commits  │                                      │
│         └───────────┬────────────┘                                      │
│                     │                                                   │
│                     ▼                                                   │
│         ┌────────────────────────┐                                      │
│         │  PHASE 6: PUSH/PR      │                                      │
│         └────────────────────────┘                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Detect Security-Relevant Changes

### Scan Trigger Files

| Category | File Patterns | Scan Type |
|----------|---------------|-----------|
| **Go** | `go.mod`, `go.sum` | `trivy fs` |
| **Python** | `requirements*.txt`, `pyproject.toml`, `Pipfile*`, `poetry.lock` | `trivy fs` |
| **Node.js** | `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` | `trivy fs` |
| **Ruby** | `Gemfile`, `Gemfile.lock` | `trivy fs` |
| **Rust** | `Cargo.toml`, `Cargo.lock` | `trivy fs` |
| **Java** | `pom.xml`, `build.gradle*` | `trivy fs` |
| **Container** | `Dockerfile*`, `*.dockerfile`, `docker-compose*.yml` | `trivy config` + `trivy image` |
| **IaC** | `*.tf`, `*.hcl`, `*.yaml` (k8s), `*.yml` (CF) | `trivy config` |

### Detection Command

```bash
# Check staged files for security-relevant changes
git diff --cached --name-only | grep -E "\
(go\.(mod|sum))|\
(requirements.*\.txt|pyproject\.toml|Pipfile|poetry\.lock)|\
(package.*\.json|yarn\.lock|pnpm-lock\.yaml)|\
(Gemfile|Gemfile\.lock)|\
(Cargo\.(toml|lock))|\
(pom\.xml|build\.gradle)|\
(Dockerfile|\.dockerfile|docker-compose)|\
(\.tf$|\.hcl$)\
"
```

If the command produces output, proceed to Phase 2.

---

## Phase 2: Security Scanning

### Scan Commands by Type

**Filesystem Scan (Dependencies)**

```bash
trivy fs \
    --severity CRITICAL,HIGH \
    --exit-code 1 \
    --ignore-unfixed \
    --format table \
    .
```

**Dockerfile Configuration Scan**

```bash
trivy config \
    --severity CRITICAL,HIGH \
    --exit-code 1 \
    --format table \
    .
```

**Container Image Scan** (if Dockerfile changed and image can be built)

```bash
# Build temporary image
docker build -t trivy-scan-temp:latest .

# Scan image
trivy image \
    --severity CRITICAL,HIGH \
    --exit-code 1 \
    --ignore-unfixed \
    --format table \
    trivy-scan-temp:latest

# Cleanup
docker rmi trivy-scan-temp:latest
```

### Severity Policy

| Severity | Exit Code | Action | Commit Allowed |
|----------|-----------|--------|----------------|
| CRITICAL | 1 | Generate remediation plan | NO |
| HIGH | 1 | Generate remediation plan | NO |
| MEDIUM | 0 | Log warning | YES |
| LOW | 0 | Informational | YES |

---

## Phase 3: Remediation Planning

When vulnerabilities are found, generate a remediation plan.

### Remediation Plan Template

```markdown
# Vulnerability Remediation Plan

**Generated**: [timestamp]
**Scan Type**: [fs/config/image]
**Total Findings**: [count] (CRITICAL: X, HIGH: Y)

## Vulnerabilities

| Severity | Package | CVE | Installed | Fixed |
|----------|---------|-----|-----------|-------|
| CRITICAL | lodash | CVE-2021-23337 | 4.17.15 | 4.17.21 |
| HIGH | minimist | CVE-2021-44906 | 1.2.5 | 1.2.6 |

## Remediation Steps

### Priority 1: CRITICAL

1. **lodash** (CVE-2021-23337)
   - Current: 4.17.15
   - Fix: Upgrade to 4.17.21
   - Command: `npm install lodash@4.17.21`

### Priority 2: HIGH

1. **minimist** (CVE-2021-44906)
   - Current: 1.2.5
   - Fix: Upgrade to 1.2.6
   - Command: `npm install minimist@1.2.6`

## Verification

After remediation, verify with:
```bash
trivy fs --severity CRITICAL,HIGH --exit-code 1 .
```

## Exceptions

If a vulnerability cannot be fixed (no patch available, false positive):

1. Document justification in `.trivyignore`:
   ```
   # CVE-XXXX-YYYY: Not exploitable in our context because [reason]
   CVE-XXXX-YYYY
   ```

2. Create tracking issue for future remediation
```

### Remediation Commands by Package Manager

| Package Manager | Upgrade Command | Lock File Update |
|-----------------|-----------------|------------------|
| **Go** | `go get package@vX.Y.Z` | `go mod tidy` |
| **Python (uv)** | `uv pip install package==X.Y.Z` | `uv pip compile` |
| **Python (pip)** | `pip install package==X.Y.Z` | `pip freeze > requirements.txt` |
| **Node (npm)** | `npm install package@X.Y.Z` | Automatic |
| **Node (yarn)** | `yarn add package@X.Y.Z` | Automatic |
| **Rust** | `cargo update -p package` | Automatic |

---

## Phase 4: Code Review (Conditional)

After security scan passes, check if Gemini review is needed:

| Condition | Action |
|-----------|--------|
| >100 lines changed | Call Gemini review |
| >3 files with logic changes | Call Gemini review |
| Security-related code changes | Call Gemini review |
| Performance-critical changes | Call Gemini review |

See: `~/.claude/skills/gemini-review/SKILL.md`

---

## Phase 5: Commit

Follow Conventional Commits format:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

See: `~/.claude/skills/scm/SKILL.md` for full commit guidelines.

---

## Phase 6: Push / PR

### Push Only (`/commit-push`)

```bash
git push origin HEAD
```

### Push and Create PR (`/commit-push-pr`)

```bash
git push origin HEAD
gh pr create --title "..." --body "..."
```

---

## Quick Reference Checklist

Before committing with dependency/container changes:

- [ ] Ran detection command to identify scan triggers
- [ ] Executed appropriate Trivy scans
- [ ] No CRITICAL vulnerabilities present
- [ ] No HIGH vulnerabilities present
- [ ] Any exceptions documented in `.trivyignore` with justification
- [ ] Remediation plan followed (if vulnerabilities were found)
- [ ] Verification scan passed
- [ ] Gemini review completed (if thresholds met)
- [ ] Commit message follows Conventional Commits

---

## Integration Points

| Skill | Integration |
|-------|-------------|
| `trivy/SKILL.md` | Scan commands and remediation strategies |
| `scm/SKILL.md` | Commit formatting and Git workflow |
| `gemini-review/SKILL.md` | Code review thresholds |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Trivy not installed | `brew install trivy` |
| Slow scans | Use `--skip-update` after initial DB download |
| False positive | Add to `.trivyignore` with documented justification |
| Transitive dependency vuln | Use package manager override mechanism |
| Cannot build Docker image | Run `trivy config` only; skip image scan |
