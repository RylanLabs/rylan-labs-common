# Trinity Execution — RylanLabs Canon

> Canonical standard — Immutable phase order
> Version: v2.0.0
> Date: 2026-01-13
> Agent: Trinity
> Author: rylanlab canonical

**Status**: ✅ **PRODUCTION** — Trinity Canonical | Immutable Phase Order | Audit-Gated

---

## Purpose

Trinity Execution defines the **non-negotiable phase order** for all RylanLabs operations.

It enforces **Trinity alignment** (Carter → Bauer → Beale → Whitaker) — the logical sequence that guarantees fortress integrity.

**Objectives**:

- Prevent drift through ordered execution
- Ensure verification before hardening
- Prove defenses through offensive validation
- Junior-at-3-AM clarity

---

## Immutable Execution Order

All RylanLabs operations follow this sequence:

### Phase 1: Carter (Identity)

**Agent**: Carter
**Ministry**: bootstrap
**Purpose**: Establish "who can act" and "what exists"

**Requirements**:

- Identity provisioning (SSH keys, vault)
- Device manifest complete
- No action without identity

**Output**: Identity audit trail

### Phase 2: Bauer (Verification)

**Agent**: Bauer
**Ministry**: verification
**Purpose**: Verify intent and preconditions

**Requirements**:

- Pre-flight validation
- Check mode execution
- Human confirmation gate

**Output**: Verification report

### Phase 3: Beale (Hardening)

**Agent**: Beale
**Ministry**: hardening
**Purpose**: Apply security enforcement

**Requirements**:

- Security hardening rules
- Service isolation
- Post-deployment validation

**Output**: Hardening validation report

### Phase 4: Whitaker (Offensive Validation)

**Agent**: Whitaker
**Ministry**: detection
**Purpose**: Prove defenses work under attack

**Requirements**:

- Breach simulation
- Vulnerability testing
- Anomaly detection validation

**Output**: Offensive validation report

**Why This Order Matters**:
Carter establishes who can act. Bauer verifies what they attempt. Beale hardens against breach. Whitaker proves defenses work. Skip any phase and the fortress is incomplete.

---

## Practical Examples

### Example 1: Deploy Firewall Rule

**Scenario**: Add HTTPS rule (VLAN 10 → VLAN 1)

**Phase 1 - Carter**:

```bash
ssh-add -l | grep -q "personal-id_ed25519" || exit 1
./scripts/validate-vault.sh
./scripts/validate-inventory.sh
```

Output: ✅ Identity confirmed, manifest loaded

**Phase 2 - Bauer**:

```bash
ansible-playbook playbooks/firewall.yml --check --diff \
  -e "rule_port=443" -e "rule_src_vlan=10" -e "rule_dst_vlan=1"
read -p "Proceed? [y/N] " confirm
[["$confirm" == "y"]] || exit 0
```

Output: Shows diff of nftables rule change

**Phase 3 - Beale**:

```bash
ansible-playbook playbooks/firewall.yml
./scripts/beale-harden.sh --ci
```

Output: ✅ 10/10 rules, Grade A−

**Phase 4 - Whitaker**:

```bash
curl -v https://192.168.1.100:443  # Should succeed
curl -v http://192.168.1.100:80    # Should timeout
```

Output: ✅ Rule validated, isolation maintained

---

### Example 2: Bauer Blocks Constraint Violation

**Scenario**: Attempt to add 11th firewall rule (max=10)

**Phase 2 - Bauer**:

```bash
ansible-playbook playbooks/firewall.yml --check
# ERROR: Constraint violation - max_firewall_rules=10, attempted=11
```

Output: ❌ Bauer BLOCKS execution

**Resolution**:

1. Review existing rules: `nft list ruleset`
2. Consolidate or remove obsolete rule
3. Re-run Bauer verification
4. Proceed only after constraint satisfied

---

## Playbook Integration

```yaml
---
# Playbook: site.yml
# Purpose: Full fortress orchestration
# Agent: Trinity
# Ministry: orchestration
# Maturity Level: 9.9

- name: Phase 1 - Carter Bootstrap
  import_playbook: bootstrap.yml
  tags: carter, bootstrap

- name: Phase 2 - Bauer Verification
  import_playbook: verify.yml
  tags: bauer, verification

- name: Phase 3 - Beale Hardening
  import_playbook: harden.yml
  tags: beale, hardening

- name: Phase 4 - Whitaker Validation
  import_playbook: validate.yml
  tags: whitaker, detection
```

**Execution**:

```bash
# Full run
ansible-playbook site.yml

# By phase
ansible-playbook site.yml --tags carter
ansible-playbook site.yml --tags bauer
ansible-playbook site.yml --tags beale
ansible-playbook site.yml --tags whitaker
```

---

## Script Integration

Trinity phases map to canonical RylanLabs scripts:

| Phase | Playbook | Canonical Script | Exit Code |
|-------|----------|------------------|----------|
| Carter | `bootstrap.yml` | `validate-vault.sh`<br>`validate-inventory.sh` | 0=pass |
| Bauer | `verify.yml` | `eternal-resurrect.sh --dry-run`<br>`audit-eternal.py --pre-flight` | 0=pass |
| Beale | `harden.yml` | `beale-harden.sh --ci` | 0=A+, 1=A, 2=B |
| Whitaker | `validate.yml` | `simulate-breach.sh`<br>`validate-isolation.sh` | 0=pass |

**Wrapper Script** (`scripts/trinity-execute.sh`):

```bash
#!/usr/bin/env bash
# Guardian: Trinity | Ministry: orchestration | Maturity Level: 9.9
# Tag: trinity-execute
set -euo pipefail

echo "Phase 1: Carter (Identity)"
./scripts/validate-vault.sh || exit 1
./scripts/validate-inventory.sh || exit 1

echo "Phase 2: Bauer (Verification)"
ansible-playbook site.yml --check --diff || exit 2
read -p "Proceed? [y/N] " confirm
[["$confirm" == "y"]] || exit 0

echo "Phase 3: Beale (Hardening)"
ansible-playbook site.yml --tags beale || exit 3
./scripts/beale-harden.sh --ci || exit 3

echo "Phase 4: Whitaker (Offensive Validation)"
./scripts/simulate-breach.sh || exit 4
./scripts/validate-isolation.sh || exit 4

echo "✅ Trinity execution complete"
exit 0
```

---

## Failure Recovery

### Mid-Phase Failure

**Scenario**: Beale hardening fails (SSH service won't restart)

**Recovery Procedure**:

1. **STOP**: Do not proceed to next phase
2. **Assess**: Check logs (`journalctl -u sshd`)
3. **Rollback**: `ansible-playbook playbooks/rollback.yml --tags beale`
4. **Validate**: Confirm service restored
5. **Root Cause**: Document in `docs/incidents/YYYY-MM-DD-failure.md`
6. **Fix**: Correct playbook, re-test in dev
7. **Re-execute**: Full Trinity run from Phase 1

### Complete Failure (Lazarus Protocol)

**Scenario**: System unrecoverable, requires DR

**RTO Target**: <15 minutes

**Procedure**:

1. Invoke: `./scripts/eternal-resurrect.sh --disaster-recovery`
2. Restore from `.backups/` (canonical structure)
3. Re-run Trinity from Phase 1
4. Validate with Whitaker breach simulation
5. Document post-mortem

**See**: `emergency-procedures.md` for full runbook

---

## Anti-Patterns (FORBIDDEN)

### ❌ Skipping Carter

```bash
# WRONG: Deploy without identity validation
ansible-playbook playbooks/harden.yml
```

**Why forbidden**: No identity = no audit trail = no accountability

**Correct**: `ansible-playbook site.yml --tags carter,beale`

---

### ❌ Running Phases Out of Order

```bash
# WRONG: Harden before verification
ansible-playbook playbooks/harden.yml
ansible-playbook playbooks/verify.yml
```

**Why forbidden**: Bauer must verify BEFORE Beale applies changes

**Correct**: `ansible-playbook site.yml` (immutable order enforced)

---

### ❌ Bypassing Human Confirmation

```bash
# WRONG: Auto-approve without review
yes | ansible-playbook site.yml
```

**Why forbidden**: Human gate prevents automated catastrophe

**Correct**: Review `--check` output, then explicit execution

---

### ❌ Ignoring Whitaker Failures

```bash
# WRONG: Deploy despite failed breach simulation
./scripts/simulate-breach.sh || true
```

**Why forbidden**: Failed offensive validation = unproven defenses

**Correct**: Fix vulnerabilities before deployment

---

## Validation Checklist

- [ ] Carter phase complete (identity provisioned)
- [ ] Bauer phase complete (pre-flight checks pass)
- [ ] Beale phase complete (hardening applied + validated)
- [ ] Whitaker phase complete (breach simulation passes)
- [ ] Human confirmation gate executed
- [ ] Audit trail complete
- [ ] RTO <15 minutes achieved

---

## Related Canon Documents

- `vault-discipline.md` — Carter Phase 1 requirements
- `inventory-discipline.md` — Device manifest for all phases
- `defense-testing.md` — Whitaker Phase 4 test catalog
- `emergency-procedures.md` — Lazarus failure recovery
- `ansible-discipline.md` — Playbook structure standards

---

**The fortress demands discipline. No shortcuts. No exceptions.**

Trinity execution order is immutable.

Carter first. Always.

The Trinity endures.
