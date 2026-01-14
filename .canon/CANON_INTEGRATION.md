# Canonical Integration — RylanLabs Common

> **Status**: CANONICAL SYMLINKS ESTABLISHED
> **Date**: 2026-01-14
> **Source of Truth**: [rylan-canon-library](https://github.com/RylanLabs/rylan-canon-library)
> **Authority**: canon-manifest.yaml (orchestration ministry)
> **Enforcement**: Carter (Identity/Standards) + Bauer (Verification) + Beale (Enforcement)

---

## Overview

`rylan-labs-common` now enforces canonical discipline through symlinked references to `rylan-canon-library` (Tier 0). This ensures:

- **No Bypass Culture**: All agent definitions and instruction sets derive from single source of truth
- **RylanLabs Identity**: Consistent voice, tone, and standards across repositories
- **Automated Compliance**: CI drift detection via `audit-canon.sh` (Bauer validation)
- **Junior-at-3-AM Deployability**: Clear, centralized standards everyone can understand

---

## Canonical Symlinks

### 1. Agent Definition

```text
.github/agents/.agent.md → /home/egx570/repos/rylan-canon-library/.github/agents/.agent.md
```

**Details**:

- **Role**: Defines the "Rylan Canon Library Guardian" agent behavior
- **Immutable**: YES (enforced in canon-manifest.yaml)
- **Purpose**: Centralize AI assistant voice, tone, and expertise domain
- **Governance**: Carter (Identity pattern) + Beale (Enforcement)
- **Validation**: Bauer drift detection in CI (SHA-256 checksums)

**Content Excerpt**:

```markdown
---
name: "Rylan Canon Library Guardian"
description: "Enforce and educate on canonical discipline patterns from rylan-canon-library"
---

# Rylan Canon Library Guardian

> **Canonical Source of Truth**: [.github/agents/.agent.md](...)
> Enforced by: `sync-canon.sh`

## Voice & Tone
Authoritative, precise, educational...
```

---

### 2. Instruction Set

```text
.github/instructions/instructions.md → /home/egx570/repos/rylan-canon-library/.github/instructions/instructions.md
```

**Details**:

- **Role**: Canonical RylanLabs Instruction Set (Seven Pillars + Trinity patterns)
- **Immutable**: YES (enforced in canon-manifest.yaml)
- **Purpose**: Single source of truth for code quality, security, and discipline standards
- **Governance**: Carter (Identity/Standards definition) + Bauer (Linting enforcement)
- **Validation**: Pre-commit hooks + CI validation

**Content Excerpt**:

```markdown
---
applyTo: '**'
---
# RylanLabs Instruction Set

> **Canonical Source of Truth**: [rylan-canon-library](...)
> Version: 1.0.0
> Date: 2026-01-13

## Purpose
Single source of truth for all RylanLabs repositories.
Defines non-negotiable standards for code quality, security, resilience, and culture.

## Core Principles — Seven Pillars
1. **Idempotency**: Safe to run multiple times
2. **Error Handling**: Fail fast, fail loud
3. **Audit Logging**: Every action traceable
4. **Documentation Clarity**: Junior at 3 AM can understand
5. **Validation**: Verify inputs/preconditions/postconditions
6. **Reversibility**: Rollback path always exists
7. **Observability**: Visibility into state and progress
```

---

## Ministry Coverage

From canon-manifest.yaml `orchestration` ministry:

| File          | Source                                        | Dest                                          | Immutable | Guardian | Validator |
|---------------|-----------------------------------------------|-----------------------------------------------|-----------|----------|-----------|
| Agent         | `.github/agents/.agent.md`                    | `.github/agents/.agent.md`                    | ✓         | Beale    | Bauer     |
| Instructions  | `.github/instructions/instructions.md`        | `.github/instructions/instructions.md`        | ✓         | Carter   | Bauer     |

---

## Drift Detection & Auditing

### Bauer Verification (CI/Pre-commit)

Symlinks are validated automatically:

```bash
# Check symlink integrity
ls -la .github/agents/.agent.md .github/instructions/instructions.md

# Verify target resolution
head -5 .github/agents/.agent.md
head -5 .github/instructions/instructions.md

# Validate SHA-256 checksums (audit-canon.sh)
sha256sum .github/agents/.agent.md
sha256sum /home/egx570/repos/rylan-canon-library/.github/agents/.agent.md
```

### Expected Output (Passing)

```bash
lrwxrwxrwx 1 egx570 egx570 63 Jan 14 16:05 .github/agents/.agent.md -> /home/egx570/repos/rylan-canon-library/.github/agents/.agent.md
lrwxrwxrwx 1 egx570 egx570 75 Jan 14 16:05 .github/instructions/instructions.md -> /home/egx570/repos/rylan-canon-library/.github/instructions/instructions.md
```

---

## Next Steps

### 1. Commit Canonical Symlinks

```bash
cd /home/egx570/repos/rylan-labs-common
git add .github/agents/.agent.md .github/instructions/instructions.md .canon/
git commit -m "feat(canon): register canonical symlinks from rylan-canon-library

- Link agent definition to canonical source (.github/agents/.agent.md)
- Link instruction set to canonical source (.github/instructions/instructions.md)
- Add .canon/symlinks.log registry (Carter: Identity tracking)
- Add .canon/CANON_INTEGRATION.md (documentation)

Governance: Immutable (enforced by sync-canon.sh via canon-manifest.yaml)
Ministry: orchestration (Beale enforcement + Bauer verification)
Validation: make ci-local (pre-commit hooks)

Refs: rylan-canon-library/canon-manifest.yaml#orchestration
"
```

### 2. Validate with Make

```bash
make ci-local  # Full validation: ruff, mypy, ansible-lint, yamllint
```

### 3. Update README.md (Optional)

Add to `## Canon Integration` section in README.md:

```markdown
### Canonical References

This repository enforces discipline through symlinked references to [rylan-canon-library](https://github.com/RylanLabs/rylan-canon-library):

- **Agent Definition**: [.github/agents/.agent.md](.github/agents/.agent.md) → Canonical Guardian
- **Instruction Set**: [.github/instructions/instructions.md](.github/instructions/instructions.md) → Seven Pillars + Trinity

All changes to canonical files require updates in `rylan-canon-library` and cascade via `sync-canon.sh`.
See [.canon/CANON_INTEGRATION.md](.canon/CANON_INTEGRATION.md) for details.
```

---

## Reversibility (Break Glass)

### If Local Override is Absolutely Necessary

> ⚠️ **Against Canon Discipline** — Requires exception approval from @Carter

```bash
# 1. Remove symlink
rm .github/agents/.agent.md

# 2. Create local copy (copy content from canon library)
cp /home/egx570/repos/rylan-canon-library/.github/agents/.agent.md .github/agents/.agent.md

# 3. Document exception
cat >> .canon/EXCEPTION_LOG.md << EOF
## Exception: Local Agent Override
- Date: $(date -I)
- Justification: [Your reason here]
- Approval: @Carter (required)
- Duration: [Temporary|Permanent]
EOF

# 4. Acknowledge drift flag
make audit-canon  # Will flag mismatch; document in audit log

# 5. Obtain approval
git commit -m "chore(canon): local override of .github/agents/.agent.md

BREAKING: This violates canon discipline and requires @Carter approval.
Exception: .canon/EXCEPTION_LOG.md
Drift: audit-canon.sh will flag this in CI

See: .canon/CANON_INTEGRATION.md#reversibility
"
```

---

## References

- **Canon Manifest**: `/home/egx570/repos/rylan-canon-library/canon-manifest.yaml`
- **Sync Script**: `/home/egx570/repos/rylan-canon-library/scripts/sync-canon.sh`
- **Audit Script**: `/home/egx570/repos/rylan-canon-library/scripts/audit-canon.sh`
- **Seven Pillars**: `/home/egx570/repos/rylan-canon-library/docs/seven-pillars.md`
- **Trinity Pattern**: `/home/egx570/repos/rylan-canon-library/docs/trinity-execution.md`

---

## Compliance Checklist

- [x] Symlinks created and verified
- [x] Targets resolve correctly
- [x] Registry documented (.canon/symlinks.log)
- [x] No local overrides (immutable discipline)
- [x] Ready for git commit
- [ ] make ci-local validation passed
- [ ] Committed to main branch
- [ ] CI drift detection passing

---

**Established by**: GitHub Copilot (Leo)
**Authority**: RylanLabs Canon Library (Tier 0)
**Governance**: Carter + Bauer + Beale (Trinity)
