---
applyTo: '**'
---
# RylanLabs Infrastructure as Code (IaC) — Instruction Set v1.0

> Canonical guidance for rylan-labs-iac
> Date: December 22, 2025
> Status: BOOTSTRAP READY
> Extracted from: rylan-canon-library v4.6.0 + UniFi research + Trinity patterns
> Compliance: Seven Pillars ✓ | Hellodeolu v6 ✓ | T3-ETERNAL v9.5 ✓

---

## Purpose

**rylan-labs-iac** is the unified infrastructure-as-code repository for RylanLabs. It leverages Ansible for idempotent automation of:

- **Network**: UniFi API (devices, clients, VLANs, firewall rules)
- **Identity**: Carter pattern (LDAP/RADIUS/802.1X integration)
- **Verification**: Bauer pattern (audits, validations, state checks)
- **Hardening**: Beale pattern (firewall rules, isolation, secrets)

**Core Principles**:
1. **IRL-First**: Manual API exploration before Ansible automation
2. **No Bypass Culture**: All changes require review, validation, audit trail
3. **Junior-at-3-AM Deployable**: RTO <15min from clean system
4. **Local GREEN = CI GREEN**: No shortcuts, mandatory validation gates
5. **Seven Pillars Compliant**: Idempotency, error handling, audit logging, docs, validation, reversibility, observability

---

## Non-Negotiable Outcomes (Hellodeolu v6)

| Requirement | Status | Notes |
|------------|--------|-------|
| Zero PII leakage | ENFORCED | Presidio redaction, VLAN isolation |
| Max 10 firewall rules | ENFORCED | UniFi hardware offload safe |
| RTO <15min | VALIDATED | orchestrator.sh tested |
| Junior deployable | ENFORCED | make init && make deploy |
| Pre-commit GREEN | ENFORCED | Ruff 10/10, mypy, bandit |
| Local validation | MANDATORY | make ci-local before commit |
| 100% audit trail | REQUIRED | .audit/ folder with commit logs |

---

## Sacred Trinity Pattern (Non-Negotiable)

### Carter (Identity) — 2003

**Responsibility**: Programmable authentication infrastructure.

```
├── ansible/roles/carter-identity/
│   ├── tasks/configure-ldap.yml
│   ├── tasks/configure-radius.yml
│   ├── tasks/configure-802.1x.yml
│   └── handlers/restart-services.yml
├── ansible/group_vars/identity_tier/
│   └── ldap-config.yml (Vault-encrypted)
└── tests/test_carter_auth.py
```

**Idempotency**: Role runs safely multiple times; existing configs validated not recreated.  
**Error Handling**: Explicit fail if auth service unreachable; audit logged.  
**Observability**: Grafana dashboard tracks auth requests/failures.

### Bauer (Verification) — 2005

**Responsibility**: Trust nothing, verify everything.

```
├── ansible/roles/bauer-verify/
│   ├── tasks/audit-state.yml
│   ├── tasks/validate-policies.yml
│   ├── tasks/generate-report.yml
│   └── handlers/alert-on-drift.yml
├── ansible/group_vars/verify_tier/
│   └── validation-rules.yml
└── tests/test_bauer_audit.py
```

**Idempotency**: Audits safe; create no side effects.  
**Error Handling**: Drift alerts logged; optional email to ops.  
**Audit Logging**: All validation results stored in `.audit/audit-results/`.

### Beale (Hardening) — 2005

**Responsibility**: Network is first line of defense.

```
├── ansible/roles/beale-harden/
│   ├── tasks/firewall-rules.yml
│   ├── tasks/vlan-isolation.yml
│   ├── tasks/secret-mgmt.yml
│   └── handlers/emergency-rollback.yml
├── ansible/group_vars/hardening_tier/
│   └── firewall-policy.yml (Vault-encrypted)
└── tests/test_beale_firewall.py
```

**Idempotency**: Firewall rules re-apply safely (PUT idempotent).  
**Error Handling**: Rule conflicts detected pre-deploy; fail safe.  
**Reversibility**: eternal-resurrect.sh rolls back within 2min.

---

## Bootstrap Phases (5-Phase Roadmap, Sequential)

### Phase 1: Identity Bootstrap (Carter Identity) — 3min RTO

**Goal**: Establish repo identity, CI/CD, auth baseline.

**Human Gate**: Confirm main branch protection policy [y/N]

```bash
cd rylan-labs-iac
make init                    # Install deps, setup pre-commit
make validate               # Run all validators
git commit -m "feat(carter): identity bootstrap"
```

**Deliverables**:
- ✅ Repo initialized, CI/CD live
- ✅ Pre-commit hooks active
- ✅ All validators GREEN
- ✅ .audit/ structure established

### Phase 2: Verification & Validation (Bauer Audits) — 5min RTO

**Goal**: Enable state auditing, policy validation.

**Human Gate**: Confirm Ansible inventory ready [y/N]

```bash
make ci-local                # Full CI simulation
ansible-playbook playbooks/bauer-audit.yml --check
make validate-ansible
git commit -m "feat(bauer): audit framework"
```

**Deliverables**:
- ✅ Ansible syntax validated
- ✅ Dynamic inventory functional
- ✅ Audit playbooks dry-run GREEN
- ✅ CI workflow GREEN

---
