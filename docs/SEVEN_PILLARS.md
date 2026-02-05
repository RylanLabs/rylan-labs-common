# Seven Pillars of Production-Grade Code

> **⚠️ ABSORBED**: This document has been absorbed into [GITOPS-SUBSTRATE-PARADIGM.md](GITOPS-SUBSTRATE-PARADIGM.md) Section 4.
> This file is retained for historical reference and backward compatibility.
> For canonical guidance, see the master paradigm document.

> Canonical definition — Infrastructure-as-Code standards
> Version: v2.0.0
> Date: 2026-01-13

---

## The Pillars (Production-Grade — Non-Negotiable)

### 1. Idempotency

**Principle**: Multiple executions produce identical outcome — no side effects on re-run.

**Why**: Junior-at-3-AM must re-run safely. Prevents drift, enables automation.

**Canon**:

- Check state before action
- Declarative source of truth (YAML/JSON)
- No destructive ops without guard

**Example**:

```bash
# BAD — appends every run
echo "key=value" >> /etc/config

# GOOD — idempotent
if ! grep -q "^key=" /etc/config; then
  echo "key=value" >> /etc/config
fi
```

**Validation**: Run script twice — second run must change nothing.

---

### 2. Error Handling

**Principle**: Fail fast, fail loud, provide context.

**Why**: 3-AM failures need immediate actionable diagnosis.

**Canon**:

- `set -euo pipefail` mandatory
- Trap ERR + EXIT
- Meaningful exit codes
- Actionable messages (what + how to fix)

**Example**:

```bash
#!/usr/bin/env bash
set -euo pipefail

trap 'echo "ERROR at line $LINENO (exit $?)"; exit 1' ERR

if [[ ! -f "$CONFIG" ]]; then
  echo "❌ Config missing: $CONFIG" >&2
  echo "   Create: cp config.example.yaml $CONFIG" >&2
  exit 3
fi
```

**Exit Codes**:

- 0 success
- 1 generic error
- 2 usage
- 3 config
- 4 network
- 5 permission

---

### 3. Functionality

**Principle**: Does exactly one thing, perfectly.

**Why**: Single responsibility → composable, testable, maintainable.

**Canon**:

- Clear purpose in header
- `--help` + `--dry-run`
- Manual test 3× before commit
- Document inputs/outputs/prereqs

**Example**:

```bash
#!/usr/bin/env bash
# Purpose: Backup UniFi controller config
# Usage: ./backup.sh [--dry-run]
# Prereq: UNIFI_TOKEN set, curl/jq installed
# Output: .backups/config-YYYYMMDD-HHMMSS.json
```

---

### 4. Audit Logging

**Principle**: Every action traceable.

**Why**: Forensics, compliance, blameless post-mortems.

**Canon**:

- Timestamped to stderr
- Success + failure logged
- Git commits explain WHY
- Structured when complex

**Example**:

```bash
log() { echo "[$(date -Iseconds)] $*" >&2; }

log "Starting VLAN 10 creation"
log_success "VLAN 10 created"
log_error "Failed — check permissions"
```

---

### 5. Failure Recovery

**Principle**: Graceful degradation + clear recovery path.

**Why**: Partial failures must not leave broken state.

**Canon**:

- Backup before destructive change
- Trap cleanup
- Rollback instructions in error
- Stateful resume optional

**Example**:

```bash
trap 'rm -f "$TEMP_FILE"' EXIT

if [[ -f "$CONFIG" ]]; then
  cp "$CONFIG" "$CONFIG.bak"
  echo "Backup: $CONFIG.bak" >&2
fi
```

---

### 6. Security Hardening

**Principle**: Assume hostile environment.

**Why**: Default secure > default convenient.

**Canon**:

- No cleartext secrets
- Input validation
- Least privilege
- Secure temp files (`mktemp`)
- No `eval`

**Example**:

```bash
TEMP=$(mktemp)
chmod 600 "$TEMP"
trap 'rm -f "$TEMP"' EXIT
```

---

### 7. Documentation Clarity

**Principle**: Junior at 3 AM can run and understand.

**Why**: Knowledge transfer > clever code.

**Canon**:

- Header: purpose, usage, prereqs, output
- Inline comments for non-obvious
- Clear names
- README quick-start
- Examples

**Example Header**:

```bash
#!/usr/bin/env bash
# Script: backup-unifi.sh
# Purpose: Backup UniFi controller configuration
# Agent:
# Author: rylanlab canonical
# Date: 19/12/2025
```

---

**Trinity Alignment**:

- Carter: Identity (prereqs, auth)
- Bauer: Verification (audit, validation)
- Beale: Hardening (security, recovery)

**Hellodeolu v6 Outcomes (Target State)**:

!!! info "Implementation Status"
    This repository is currently in an **Experimental** phase.
    While the Seven Pillars are our non-negotiable target, the current implementation (v1.2.2)
    is a Work-in-Progress.

- **Junior-at-3-AM deployable**: Target (Beta testing in progress)
- **Pre-commit 100% green**: ENFORCED (with some security suppressions)
- **One-command resurrection**: Experimental (Unverified for all environments)

**The fortress demands these pillars. We are building the foundation.**
