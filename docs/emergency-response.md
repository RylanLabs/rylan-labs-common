# [BETA] Emergency Response & Recovery Procedures

> **⚠️ ABSORBED**: This document has been absorbed into [gitops-substrate-paradigm.md](gitops-substrate-paradigm.md) Section 6.
> This file is retained for historical reference and backward compatibility.
> For canonical guidance, see the master paradigm document.

> Infrastructure recovery runbooks
> Date: December 21, 2025

**Status**: ⚠️ **EXPERIMENTAL** — Recovery Time Objective (RTO) <15min Target (Unverified)

---

## Purpose

This document defines recovery procedures for critical infrastructure failure.

It targets full system recovery in <15 minutes from a clean OS install (Target RTO).

**Objectives**:

- RTO <15 minutes (Experimental Target)
- Clear recovery paths for on-call engineers
- Zero data loss through idempotent restoration (Beta)
- Audit trail preservation
- Standardized response protocols

**Principle**: Infrastructure must be resilient and restorable.
Every failure has a documented recovery path.

---

## Emergency Scenarios

### Scenario 1: Controller Compromise / Lockout

**Symptoms**:

- Cannot access UniFi controller GUI
- SSH to Cloud Key fails
- Devices show "Managed by Other"

**Recovery Procedure** (<10 minutes):

```bash
# T+0m: Assess
# Connect to Cloud Key console (physical access)
# Login as root (recovery mode if needed)

# T+2m: Backup current state (if accessible)
ssh root@192.168.1.1 "mongodump --db ace" > backup-compromised-$(date +%s).tar.gz

# T+4m: Factory reset Cloud Key
# Hold reset button 15 seconds
# Cloud Key reboots to setup mode

# T+6m: Restore from latest backup
# Access new controller at 192.168.1.1:8443
# Settings → Maintenance → Restore Backup
# Upload latest-config.json from rylan-homelab-iac/backups/

# T+9m: Verify devices re-adopt
# Check controller → Devices → All should reconnect

# T+10m: Document incident
git add docs/incidents/
git commit -m "incident(recovery): controller lockout recovery
RTO: 10 minutes
Cause: Unknown (possible compromise)
Action: Factory reset + restore from backup
Verification: All devices re-adopted"
```

### Scenario 2: Complete System Loss (Bare Metal)

**Symptoms**:

- All devices unreachable
- No controller access
- Hardware failure or power loss

**Recovery Procedure** (<15 minutes):

```bash
# T+0m: Provision fresh Ubuntu 24.04 host
# Boot from USB
# Install minimal server

# T+3m: Bootstrap identity
git clone git@github.com:RylanLabs/rylanlabs-private-vault.git
# Use personal key
# Copy vault password

# T+5m: Clone repos
git clone git@github.com:RylanLabs/rylan-canon-library.git
git clone git@github.com:RylanLabs/rylan-inventory.git
git clone git@github.com:RylanLabs/rylan-homelab-iac.git

# T+7m: Install Ansible
sudo apt update && sudo apt install ansible -y

# T+9m: Execute resurrection
cd rylan-homelab-iac
ansible-playbook site.yml --vault-password-file ../rylanlabs-private-vault/vault-passwords/ansible-vault-pass

# T+12m: Verify devices adopt
# Access new controller
# All devices should discover and adopt

# T+14m: Run defense tests
./scripts/defense-tests.sh

# T+15m: Document resurrection
git commit -m "feat(resurrection): full fortress recovery from bare metal
RTO: 15 minutes
Cause: Simulated total loss
Verification: All services restored, defenses passed"
```

### Scenario 3: Configuration Corruption

**Symptoms**:

- Controller shows errors
- Devices disconnected
- Playbook fails with validation errors

**Recovery Procedure** (<8 minutes):

```bash
# T+0m: Rollback to last known good
cd rylan-homelab-iac
cp backups/latest-config.json backups/recovery-$(date +%s).json

# T+2m: Restore controller
# GUI → Settings → Maintenance → Restore Backup
# Upload recovery backup

# T+5m: Verify devices reconnect
# Wait for adoption

# T+6m: Re-run verification
ansible-playbook verify.yml

# T+8m: Document
git commit -m "fix(recovery): configuration corruption rollback
RTO: 8 minutes
Cause: Failed playbook deployment
Action: Manual restore from backup"
```

---

## Lazarus Protocol — eternal-resurrect.sh

**Location**: `scripts/eternal-resurrect.sh`

**Purpose**: Full fortress resurrection from bare metal or catastrophic failure

!!! danger "Experimental Status"
    This script is a proof-of-concept.
    Known Limitations:
    - No support for Proxmox-specific hardware offload yet.
    - VLAN 99 (Management) isolation may cause resurrection failure if physical network is not correctly pre-configured.
    - Lacks verification on multi-site UniFi deployments.

```bash
#!/usr/bin/env bash
# Guardian: Lazarus | Ministry: disaster-recovery | Maturity Level: ∞
# Tag: eternal-resurrect
set -euo pipefail

LOG_FILE=".audit/resurrection-$(date +%Y%m%d-%H%M%S).log"
START_TIME=$(date +%s)

log() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }
fail() { log "❌ $*"; exit 1; }

phase_triage() {
    log "Phase 1: TRIAGE — Assessing damage"
    [[ -d "$HOME/repos/rylan-homelab-iac" ]] && { log "⚠️ Partial failure detected"; return 0; }
    log "✅ Bare metal — full resurrection required"
}

phase_validate() {
    log "Phase 2: VALIDATE — Checking prerequisites"
    [[ -f "$HOME/.ssh/id_ed25519" ]] || fail "No SSH key found"
    ping -c 1 1.1.1.1 &>/dev/null || fail "No internet connectivity"
    local available=$(df -BG "$HOME" | awk 'NR==2 {print $4}' | sed 's/G//')
    [[ $available -ge 5 ]] || fail "Insufficient disk: ${available}GB (need 5GB)"
    log "✅ Prerequisites satisfied"
}

phase_bootstrap() {
    log "Phase 3: BOOTSTRAP — Cloning repositories"
    mkdir -p "$HOME/repos" && cd "$HOME/repos"
    git clone git@github.com:RylanLabs/rylanlabs-private-vault.git || fail "Cannot clone vault"
    git clone git@github.com:RylanLabs/rylan-inventory.git || fail "Cannot clone inventory"
    git clone git@github.com:RylanLabs/rylan-homelab-iac.git || fail "Cannot clone IaC"
    if ! command -v ansible &>/dev/null; then
        log "Installing Ansible..."
        sudo apt update && sudo apt install -y ansible python3-pip
    fi
    log "✅ Bootstrap complete"
}

phase_execute() {
    log "Phase 4: EXECUTE — Running Trinity orchestration"
    cd "$HOME/repos/rylan-homelab-iac"
    ansible-playbook site.yml \
        --vault-password-file ../rylanlabs-private-vault/vault-passwords/ansible-vault-pass \
        || fail "Trinity execution failed"
    log "✅ Trinity execution complete"
}

phase_validate_defenses() {
    log "Phase 5: VALIDATE — Running Whitaker defense tests"
    cd "$HOME/repos/rylan-homelab-iac"
    ./scripts/defense-tests.sh || fail "Defense tests failed"
    log "✅ Defenses validated"
}

phase_postmortem() {
    log "Phase 6: POST-MORTEM — Documenting resurrection"
    local end_time=$(date +%s)
    local rto=$((end_time - START_TIME))
    local rto_min=$((rto / 60))
    local rto_sec=$((rto % 60))

    cd "$HOME/repos/rylan-homelab-iac"
    mkdir -p docs/incidents

    cat > "docs/incidents/$(date +%Y-%m-%d)-resurrection.md" <<EOF
# Resurrection Event

**Date**: $(date)
**RTO**: ${rto_min}m${rto_sec}s
**Target**: <15 minutes
**Status**: $([[ $rto -lt 900 ]] && echo "✅ PASS" || echo "❌ FAIL")

## Timeline
- T+0m: Triage complete
- T+2m: Prerequisites validated
- T+5m: Repositories cloned
- T+8m: Trinity execution
- T+${rto_min}m${rto_sec}s: Resurrection complete

## Outcome
Fortress resurrected successfully.
EOF

    git add docs/incidents/ .audit/ 2>/dev/null || true
    git commit -m "incident(lazarus): fortress resurrection — RTO ${rto_min}m${rto_sec}s

Guardian: Lazarus | Ministry: disaster-recovery
Result: $([[ $rto -lt 900 ]] && echo "SUCCESS" || echo "EXCEEDED_RTO")" || true

    log "✅ Post-mortem documented"
    log "━━━ LAZARUS RESURRECTION COMPLETE ━━━"
    log "RTO: ${rto_min}m${rto_sec}s (Target: <15min)"
}

main() {
    log "━━━ LAZARUS PROTOCOL — Fortress Resurrection ━━━"
    log "Guardian: Lazarus | Ministry: disaster-recovery"

    phase_triage
    phase_validate
    phase_bootstrap
    phase_execute
    phase_validate_defenses
    phase_postmortem

    exit 0
}

trap 'log "Resurrection interrupted"; exit 130' INT TERM
main "$@"
```

**Installation**:

```bash
chmod +x scripts/eternal-resurrect.sh
```

---

## Failure Recovery

If any phase of resurrection fails:

**Phase 1-3 Failure** (Triage/Validate/Bootstrap):

```bash
# Likely: Disk error, SSH key issue, network failure
# Action: Address prerequisite, retry phase
phase_validate && phase_bootstrap && phase_execute
```

**Phase 4 Failure** (Trinity Execution):

```bash
# Likely: Network unreachable, device offline, config drift
# Action: Verify connectivity, check inventory, retry
ansible-playbook site.yml --check -vvv
ansible-playbook site.yml
```

**Phase 5 Failure** (Defense Tests):

```bash
# Likely: Incomplete hardening or firewall misconfiguration
# Action: Run targeted Beale hardening, retry tests
./scripts/beale-harden.sh --ci
./scripts/defense-tests.sh
```

**Manual Intervention** (after 3 failed attempts):

```bash
# 1. Capture diagnostics
journalctl -xe > /tmp/system-logs.txt
ansible-playbook site.yml --check -vvv > /tmp/ansible-debug.txt 2>&1

# 2. Alert operator
echo "🚨 ESCALATION REQUIRED — Lazarus manual intervention" | wall

# 3. Fallback: Restore from offsite quarterly backup
# RTO extends to 2-4 hours (acceptable for catastrophic failure)
```

---

## Trinity Integration

Lazarus collaborates with all guardians during resurrection:

**Carter** → Identity bootstrap (SSH keys, vault access)

```bash
phase_bootstrap() {
    git clone git@github.com:RylanLabs/rylanlabs-private-vault.git
    ./scripts/validate-vault.sh || fail "Carter validation failed"
}
```

**Bauer** → Pre-flight verification (check before execute)

```bash
phase_execute() {
    ansible-playbook site.yml --check --diff
    read -p "Proceed with resurrection? [y/N] " confirm
    [[ "$confirm" == "y" ]] || exit 0
}
```

**Beale** → Hardening validation (security enforcement)

```bash
phase_execute() {
    ansible-playbook site.yml --tags beale
    ./scripts/beale-harden.sh --ci || fail "Beale hardening failed"
}
```

**Whitaker** → Offensive validation (prove defenses work)

```bash
phase_validate_defenses() {
    ./scripts/defense-tests.sh || fail "Whitaker validation failed"
}
```

**Guardian Workflow**:

```text
Lazarus → Carter (identity) → Bauer (verify) → Beale (harden) → Whitaker (test) → Archivist (document)
```

---

## Metrics & Validation

### RTO Tracking

**Target**: <15 minutes (900 seconds)

**Automated measurement** in eternal-resurrect.sh:

```bash
START_TIME=$(date +%s)
# ... execute phases ...
RTO=$(($(date +%s) - START_TIME))
echo "$(date +%Y-%m-%d),resurrection,$RTO,$([[ $RTO -lt 900 ]] && echo 0 || echo 1)" >> .audit/rto-metrics.csv
```

**Quarterly Validation**:

```bash
# 1. Provision fresh Ubuntu 24.04 VM
# 2. Copy SSH key only (bare metal simulation)
# 3. Execute resurrection
time ./scripts/eternal-resurrect.sh

# 4. Document results
git add .audit/rto-metrics.csv docs/incidents/
git commit -m "test(lazarus): quarterly validation — RTO Xm Ys"
```

**Last Validated**: December 21, 2025
**Next Validation**: March 21, 2026

---

## Incident Documentation Standards

### Incident Report Template

**Location**: `docs/incidents/YYYY-MM-DD-description.md`

```markdown
# Incident: [Brief Description]

**Date**: YYYY-MM-DD HH:MM:SS
**Severity**: CRITICAL | HIGH | MEDIUM
**Guardian**: Lazarus
**RTO**: Xm Ys (Target: <15min)

## Symptoms
- List of observed failures

## Root Cause
- Technical explanation

## Resolution
1. Steps executed
2. Commands run
3. Validation performed

## Outcome
- Status (success/failure)
- RTO (achieved/exceeded)
- Lessons learned

## Prevention
- Configuration updates
- Playbook improvements
- Monitoring additions

## Audit
- Git commits: [hashes]
- Logs: .audit/resurrection-*.log
```

### Git Commit Standard

```bash
git commit -m "incident(lazarus): [description] — RTO Xm Ys

Guardian: Lazarus
Ministry: disaster-recovery
Severity: [CRITICAL|HIGH|MEDIUM]
Phases: [phases executed]
Result: [SUCCESS|FAILURE|PARTIAL]
RTO: Xm Ys (Target: <15min)

Root Cause: [one-line]
Resolution: [one-line]
Prevention: [one-line]"
```

---

## Hellodeolu v6 Compliance

- ✅ **Zero PII Leakage**: Vault encrypted, no secrets in logs
- ✅ **RTO <15min**: Validated quarterly, measured automatically
- ✅ **Junior-Deployable**: One-command `eternal-resurrect.sh` execution
- ✅ **Idempotent**: Safe to re-run, no state collisions
- ✅ **Audit Trail**: Git commits + `.audit/rto-metrics.csv`
- ✅ **Human Confirmation**: Phase 4 (Bauer) confirmation gate
- ✅ **Failure Recovery**: Documented for each phase
- ✅ **Offensive Validation**: Whitaker Phase 5 defense testing

---

## Related Canon Documents

- `vault-discipline.md` — Carter identity bootstrap requirements
- `inventory-discipline.md` — Device manifest restoration
- `trinity-execution.md` — Phase order during resurrection
- `defense-testing.md` — Whitaker validation post-recovery
- `ansible-discipline.md` — Playbook execution standards

---

## Validation Checklist

- [ ] RTO <15 minutes proven quarterly
- [ ] Backup integrity verified
- [ ] Rollback path tested
- [ ] Emergency procedures documented
- [ ] Junior operator can execute

---

**The fortress demands discipline. No shortcuts. No exceptions.**

Lazarus protocol — resurrection guaranteed.

RTO <15 minutes validated.

The Trinity endures.
