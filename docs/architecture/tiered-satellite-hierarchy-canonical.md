# RylanLabs Canonical Tiered Satellite Hierarchy

Comprehensive Multi-Phased Architecture Proposal

**Date**: February 5, 2026  
**Status**: PROPOSAL (Ready for Canonical Adoption)  
**Synthesis**: Grok Comments + Leo Recommendations + Current Memory Bank Patterns  
**Authors**: Trinity Council (Carter/Bauer/Beale/Whitaker/Lazarus)  
**Maturity Target**: Level 5 (Autonomous, Zero-Drift)

---

## Executive Summary

The RylanLabs infrastructure is transitioning from a symlink-fragile, geographically dispersed model to a Git-native, Git-submodule-enforced Tiered Satellite Hierarchy. This architecture:

1. **Eliminates drift** via centralized standards (Tier 0)
2. **Enforces reversibility** (RTO <15min via Lazarus scripts)
3. **Enables scaling** (unlimited VLANs/rules via Hellodeolu v7)
4. **Mandates audit trails** (every action logged, immutable)
5. **Prevents bypass culture** (Whitaker gates + Bauer audits)

**Current Status**: Tiers 0-2 ✅ Deployed | Tier 3 🔨 Extraction in Progress | Tier 4 🚀 Phased Rollout

---

## 1. TIER HIERARCHY & DEFINITIONS

### Tier 0: Canonical Standards (Immutable Root)

**Repository**: `rylan-canon-library` (NOT renamed; canonically established)

**Purpose**: SSOT for organizational discipline, Trinity patterns, Seven Pillars enforcement, and meta-reconciliation logic.

**Key Artifacts**:

- `common.mk` — Universal Makefile targets (warm-session, resolve, validate, cascade, drill)
- `MESH-MAN.md` — Mesh operational manual
- `seven-pillars.md` — Idempotency/Error Handling/Audit/Docs/Validation/Reversibility/Observability
- `canon-manifest.yaml` — Sacred files registry
- `scripts/validate*.sh` — Whitaker compliance gates
- `.pre-commit-config.yaml` — Ruff, MyPy, Ansible-lint, ShellCheck, Gitleaks enforcement
- `.github/workflows/` — Reusable CI/CD action definitions
- Trinity role templates (carter-identity, bauer-verify, beale-harden)

**Dependencies**: None (Root)

**Maturity**: **Level 5** (Stable, no breaking changes; SemVer 2.0.0+ enforced)

---

### Tier 0.5: Secrets Vault (Asymmetric Encryption Hub)

**Repository**: `rylanlabs-private-vault` (Alternative: `rylanlabs-secrets-vault`)

**Purpose**: Centralized, GPG/SOPS-encrypted asymmetric secret management. Prevents PII leakage, enforces key rotation, isolates sensitive data from code paths.

**Key Artifacts**:

- `vault-passwords/` — Ansible vault password files (encrypted with GPG)
- `vaults/` — Tier-specific secret collections (tier0, tier2, tier3, tier4)
- `.sops.yaml` — SOPS configuration (per-path encryption rules)
- `rotation-schedule.yml` — Key rotation calendar (quarterly enforced)
- `PKI/` — Certificate authority, CSRs, signed certs (90-day expiry)

**Dependencies**: Tier 0 (policy enforcement via canon-manifest.yaml)

**Access Control**:

- Repo membership: Tier 0 Guardian (Beale) + 1 backup signer
- GPG key pinning via CI/CD
- Quarterly key rotation audited by Whitaker

**Maturity**: **Level 4** (High-trust, limited membership)

---

### Tier 1: Asset Inventory & Manifests (Infrastructure SSOT)

**Repository**: `rylan-inventory` (Established; maintain name)

**Purpose**: Single Source of Truth for all infrastructure assets, network definitions, and Object-Oriented Networking (OON) object schemas. Enables self-discovery, dynamic validation, and zero-trust identity.

**Key Artifacts**:

- `inventory/device-manifest.yml` — MAC-to-hostname-to-VLAN mappings
- `inventory/production.yml`, `staging.yml`, `lab.yml` — Environment-specific device groups
- `vars/oon_objects.yml` — OON v2 Target Objects
- `vars/vlan-schema.yml` — VLAN definitions
- `vars/firewall-zone-matrix.yml` — The Ten zones + deny-all default
- `vars/network-versioning.yml` — SemVer tracking
- `scripts/discovery-fetch-live-devices.yml` — Ansible playbook for state sync
- `scripts/inventory-validator.py` — Pre-deployment gate
- `.audit/` — Immutable audit trail

**Dependencies**: Tier 0 (standards/validation rules)

**Validation Gates**:

- **Carter Gate**: MAC uniqueness, VLAN assignment completeness
- **Bauer Gate**: Device state diff, audit logging
- **Beale Gate**: Zone isolation enforcement
- **Whitaker Gate**: Adversarial reachability testing

**Maturity**: **Level 4** (High-trust inventory; changes require 2 approvals + Whitaker scan)

---

### Tier 2: Shared Configurations & Linting (Meta-Reconciler Templates)

**Repository**: `rylan-labs-shared-configs` (Established; maintain name)

**Purpose**: DRY centralization of linting rules, CI/CD workflows, pre-commit hooks, and Makefile templates consumed across all satellites.

**Key Artifacts**:

- `.yamllint` — Canonical YAML linting rules
- `pyproject.toml` — Python: Ruff, MyPy, Pylint standards
- `.shellcheckrc` — ShellCheck: POSIX compliance
- `.ruff.toml` — Ruff config
- `.pre-commit-config.yaml` — Remote hook registry
- `.markdownlint.json` — Markdown standards
- `.editorconfig` — Editor defaults
- `.gitleaks.toml` — Gitleaks rules: PII redaction, API key patterns
- `.github/workflows/` — Reusable CI actions
- `schemas/` — JSON schema definitions
- `common.mk` — Shared Makefile logic

**Dependencies**: Tier 0 (canon-lib for governance)

**Merge Strategy**:

- Tier 0 → Tier 2 updates flow downward via Cascade automation
- `make resolve` uses `yq` to merge configs idempotently

**Maturity**: **Level 4** (Stable; breaking changes infrequent, coordinated)

---

### Tier 3: Common Libraries & Reusable Components (DRY Abstraction Hub)

**Repository**: `rylan-labs-common` (NEEDS EXTRACTION from flagship)

**Purpose**: Centralized, Galaxy-published Ansible collection. Reusable Trinity roles, custom modules, validation scripts, and exception handling frameworks.

**Key Components**:

**Trinity Roles**:

- `carter-identity` — Bootstrap identity, MAC registration, VLAN assignment
- `bauer-verify` — State audit, compliance reporting, drift detection
- `beale-harden` — Firewall rules, VLAN isolation, secret validation

**Custom Modules & Plugins**:

- `unifi_api` module — Unified V2 API abstraction
- `zone_resolver` filter — Maps device/client → zone
- `flatten_oon_groups` filter — Flattens OON hierarchies
- `presencio_redactor` filter — Redacts PII in logs

**Validation & Utility Scripts**:

- `validate-isolation.sh` — L4 reachability tests
- `validate-rotation-readiness.sh` — Pre-rotation checks
- `whitaker-scan.sh` — Adversarial testing
- `sentinel-expiry.sh` — Key/cert expiration monitoring
- `playbook_structure_linter.py` — Enforces Trinity workflow

**Exception Handling & Observability**:

- `app/exceptions.py` — Canonical exception taxonomy
- `lib/audit_trail_writer.py` — Centralized audit logging

**Publishing**:

- **Ansible Galaxy**: Collection `rylanlabs.unifi`
- Versions: SemVer (2.1.0, 2.2.0, etc.)
- Documentation: MANIFEST.md, per-role README

**Dependencies**: Tiers 0-2 (full inject)

**Maturity**: **Level 4** (Mature, stable API; deprecation warnings before breaking changes)

---

### Tier 4: Service Implementations (Satellite Execution Hubs)

Tier 4 repositories are focused application domains that consume Tier 0-3 to deliver specific infrastructure capabilities.

#### 4.1: Core Infrastructure — `rylan-labs-network-iac` (Flagship)

**Purpose**: Primary UniFi provisioning, zone management, firewall orchestration, VPN, RADIUS VLAN assignment.

**Key Playbooks** (Phased):

- `playbooks/00-bootstrap-foundation.yml` — Establish network baseline
- `playbooks/01-sync-unifi-objects.yml` — Deploy OON objects
- `playbooks/02-inventory-discovery.yml` — Sync live device state
- `playbooks/03-remediate-switch-ports.yml` — Enforce port profiles
- `playbooks/06-verify-security-compliance.yml` — Validate zone isolation
- `playbooks/99-verify-compliance.yml` — Final audit gate

**Disaster Recovery**:

- `scripts/eternal-resurrect.sh` — Rollback all changes (<2min RTO)
- `.audit/network-state-snapshots/` — Pre-change state backup

**Maturity**: **Level 4** (Production, validates every change)

**Dependencies**: Tiers 0-3

---

#### 4.2: Identity & Access Management — `rylanlabs-aaa-core` (Phased Rollout)

**Purpose**: Orchestrate AAA trinity (Samba AD, FreeRADIUS, OPA), certificate management, 802.1X integration, zero-trust identity.

**Key Components**:

- **Samba HA**: Multi-site AD replication, forest trust
- **FreeRADIUS**: RadSec HA, dynamic VLAN assignment, 802.1X
- **OPA/Rego**: Policy evaluation engine, credential validation
- **Certificate Authority**: Internal PKI, cert rotation, CRL distribution

**Maturity**: **Level 3** (Beta; 12-week phased rollout starting Q2 2026)

**Dependencies**: Tiers 0-3, network-iac (zone defs), vault (AD/RADIUS passwords)

---

#### 4.3: Policy & Compliance Engine — `rylanlabs-policy-engine` (Planned)

**Purpose**: Policy-as-code via OPA Rego. Dynamic rule evaluation, compliance mapping, drift enforcement.

**Maturity**: **Level 2** (Planned; depends on aaa-core)

**Dependencies**: Tiers 0-3, network-iac, aaa-core

---

#### 4.4: Observability & Monitoring — `rylanlabs-monitoring` (Planned)

**Purpose**: Unified observability stack (Loki, Grafana, Prometheus). Real-time zone violation tracking, audit visualization, alerting.

**Maturity**: **Level 2** (Planned; 30-day log retention, 2-year metrics)

**Dependencies**: Tiers 0-3, network-iac, aaa-core, policy-engine

---

#### 4.5: Threat Intelligence & Response — `rylanlabs-threat-intel` (Planned)

**Purpose**: Real-time threat feed ingestion (MISP, OTX), dynamic deny lists, anomaly-driven hardening.

**Maturity**: **Level 2** (Planned; depends on policy-engine for ML)

**Dependencies**: Tiers 0-3, network-iac, policy-engine

---

#### 4.6: UniFi Real-Time Plugin — `rylanlabs-unifi-plugin` (Planned)

**Purpose**: Custom UniFi OS plugin for real-time events (CoA, LDAP notifications), micro-segmentation triggers.

**Maturity**: **Level 1** (Experimental; depends on aaa-core stability)

**Dependencies**: Tiers 0-3, network-iac, aaa-core

---

## 2. NAMING CONVENTIONS & RATIONALE

**Format**: `rylanlabs-[domain]-[function]` OR `rylan-labs-[domain]-[function]`

**Resolved Convention**: Use `rylan-labs-` prefix for Infrastructure/DevOps repos (mature, production). Use `rylanlabs-` prefix for Shared/Foundational repos (config, identity, secrets).

| Tier | Repository | Rationale |
|------|-----------|-----------|
| 0 | `rylan-canon-library` | Established; signals "canonical" SSOT |
| 0.5 | `rylanlabs-private-vault` | Private/sensitive; signals containment |
| 1 | `rylan-inventory` | Established; SSOT signal |
| 2 | `rylan-labs-shared-configs` | Established; shared infrastructure signal |
| 3 | `rylan-labs-common` | NEW; signals reusable components |
| 4a | `rylan-labs-network-iac` | Established; flagship IaC |
| 4b | `rylanlabs-aaa-core` | Identity-first naming; signals core service |
| 4c | `rylanlabs-policy-engine` | Identity-first naming |
| 4d | `rylanlabs-monitoring` | Identity-first naming |
| 4e | `rylanlabs-threat-intel` | Identity-first naming |
| 4f | `rylanlabs-unifi-plugin` | Identity-first naming |

**Rationale**: `rylan-labs-` = Infrastructure | `rylanlabs-` = Shared/Service

---

## 3. MULTI-PHASED MIGRATION ROADMAP

### Phase A: Tier 0-2 Consolidation & Validation (NOW → Feb 28, 2026)

**Status**: 95% Complete. Finalize gaps.

**Goals**:

- Tier 0 (rylan-canon-library) — Deployed & stable
- Tier 0.5 (rylanlabs-private-vault) — Deployed & GPG keys rotated
- Tier 1 (rylan-inventory) — SSOT locked; device-manifest complete
- Tier 2 (rylan-labs-shared-configs) — CI/CD validated across mesh
- **Action**: Run `make resolve` across all repos; verify zero symlinks

**Deliverables**:

- `.audit/tier-0-2-validation.json` — Validates all Tier 0-2 repos
- `MIGRATION-CHECKLIST-A.md` — Sign-off by Bauer + Whitaker

---

### Phase B: Tier 3 Extraction & Galaxy Publishing (Mar 1 — Apr 30, 2026)

**Goals**: Extract `rylan-labs-common` from flagship, publish to Ansible Galaxy. Includes a 2-week buffer for complex role extraction and canary testing.

**Tasks**:

1. Extract Trinity Roles (Carter/Bauer/Beale)
2. Extract Custom Modules
3. Create Galaxy Metadata
4. Extract Validation & Utility Scripts
5. Create Exception Handling Framework
6. Testing & CI/CD (Molecule + Integration)
7. Canary Deployment (Staged Staging Rollout)
8. Integration & Sign-off

**Deliverables**:

- `rylanlabs.unifi` collection v2.1.0 on Galaxy
- `rylan-labs-common` repo with full test suite (90%+ coverage)
- `rylan-labs-network-iac` refactored to consume collection
- `MIGRATION-CHECKLIST-B.md` — Signed by Trinity Council

---

### Phase C: Tier 4 Flagship Overhaul (May 1 — Jun 15, 2026)

**Goals**: Refactor `rylan-labs-network-iac` as the canonical Tier 4 implementation example.

**Tasks**:

1. Consolidate Playbooks (reduce from 99 to 15 core)
2. Refactor for Galaxy Collection Consumption
3. RTO Hardening
4. Validation Gates (Seven Pillars Enforcement)
5. Mesh Compliance

**Deliverables**:

- `rylan-labs-network-iac` v1.3.0 (refactored, 7 core playbooks)
- RTO validation: <7min bootstrap from clean state
- `MIGRATION-CHECKLIST-C.md` + Trinity Council sign-off

---

### Phase D: Tier 4 Satellite Rollout (Jun 16 — Oct 31, 2026)

**Goals**: Deploy remaining Tier 4 services using parallel streams.

**D1**: `rylanlabs-aaa-core` (Jun 16 — Jul 31, 6 weeks)  
**D3-Early**: `rylanlabs-monitoring` (Jun 1 — Jul 15, parallel with D1) - Core metrics/logs for Phase B/C validation.  
**D2**: `rylanlabs-policy-engine` (Aug 1 — Aug 31, 4 weeks, **HARD** dependency on D1)  
**D3-Full**: `rylanlabs-monitoring` (Aug 1 — Sep 30, full dashboard/alerting suite)  
**D4**: `rylanlabs-threat-intel` (Sep 1 — Oct 15, 6 weeks, **HARD** dependency on D2)  
**D5**: `rylanlabs-unifi-plugin` (Sep 1 — Oct 31, 8 weeks, **HARD** dependency on D1)

**Rollout Pattern**:

- Each satellite deployed to staging first (parallel, isolated)
- Whitaker adversarial testing (30% breach attempt budget)
- Bauer audit validation (drift detection)
- Lazarus recovery drills (RTO testing)
- Production rollout only after all gates pass

---

## 4. VALIDATION GATES & TRINITY ENFORCEMENT

### Carter Gate: Identity & Manifest Integrity

- Ownership: User identity verified (SSH key, GPG signature)
- Manifest Completeness: Device MAC → hostname → VLAN → zone
- Credentials: Service accounts registered
- Failure Mode: Reject commit with remediation path

### Bauer Gate: Audit & Compliance

- State Diff: Live state vs. manifest (reconcile or fail)
- Drift Detection: Automated 15-minute sync checks
- Compliance Matrix: Policy adherence
- Audit Trail: Immutable `.audit/audit-trail.jsonl`
- Failure Mode: Alert + remediation playbook trigger

### Beale Gate: Security Hardening

- Secret Scanning: Gitleaks + custom regex
- Firewall Rules: Validate no allow-all; zone matrix enforced
- VLAN Isolation: Prove inter-zone routes are explicit + allowed
- Certificate Expiry: Check PKI health (>30 days)
- Failure Mode: Block merge; escalate to on-call security

### Whitaker Gate: Adversarial Testing (Offensive)

- Penetration Testing: Automated breach attempts
- False Positives: Policy violations that should be allowed
- Bypass Detection: Identify unapproved tunnels
- Coverage: 30% of critical paths tested per deployment
- Failure Mode: Block deployment; create incident for review

### Lazarus Gate: Recovery & Reversibility

- RTO Validation: Rollback executes in <15min (tested)
- Backup Integrity: Pre-change snapshots verified
- Playbook Atomicity: No partial-state scenarios
- Failure Mode: Block deployment if rollback untested

---

## 5. MATURITY LEVEL 5 (ML5) SCORECARD

To achieve **Maturity Level 5 (Autonomous, Zero-Drift)**, the following 10 quantitative criteria must each maintain ≥95% compliance as validated by quarterly drills.

| Criterion | Target | Description | Validation Method |
|-----------|--------|-------------|-------------------|
| **Idempotency** | 100% | Zero changes on 2nd/3rd playbook runs | `ansible-playbook --check` |
| **Error Handling** | 100% | No bare `except:` clauses; all errors caught | `grep -r 'except:'` (no bare) |
| **Audit Logging** | 100% | Every action logged to `.audit/audit-trail.jsonl` | `jq` entry count validation |
| **Failure Recovery** | RTO <15m | Full stack recovery from clean state | `time make drill` |
| **Security Hardening** | 100% | Zero critical CVEs + Gitleaks clean | `make secure` gate |
| **Documentation** | 100% | All roles have README + EXAMPLES | `find roles/ -name README.md` |
| **No-Bypass Culture** | 100% | 100% GPG-signed commits; zero gate bypass | `git log --show-signature` |
| **Drift Detection** | <15m | Sentinel Loop latency for state drift | `.audit/drift-detection.log` timestamp |
| **Self-Healing** | 80%+ | Automated remediation of detected drift | `remediated / detected` ratio |
| **Zero-Trust Identity** | 100% | All devices/users authenticated via 802.1X | `aaa-core` deployment flag |

**Achievement Gate**: Achievement of Level 5 requires a cumulative score of **9.5/10** across these criteria, verified by the Trinity Council.

---

## 6. MAKEFILE META-RECONCILIATION

All Tier 3+ repos include `common.mk` and expose these targets:

```
make resolve          # Materialize submodules (zero symlinks)
make validate         # Run Carter/Bauer/Beale/Whitaker/Lazarus gates
make cascade          # Publish via Cascade automation (mesh-wide)
make drill            # Execute disaster recovery drills (RTO validation)
make warm-session     # 8-hour GPG session for password-less deploys
make org-audit        # Nightly mesh compliance check
make mesh-remediate   # Force-inject standards across satellites
```

**Reconciliation Flow**:

1. Developer commits → Pushes to feature branch
2. GitHub Actions → Runs `make validate` (all gates)
3. Merge to main → `make cascade` publishes changes
4. Downstream satellites → Auto-sync submodule version
5. Nightly → `make org-audit` verifies mesh compliance
6. Drift detected → `make mesh-remediate` injects fixes (human approval)

---

## 6. CURRENT STATE vs. PROPOSAL COMPARISON

| Aspect | Current (Pre-Migration) | Proposal (Target) | Status |
|--------|------------------------|-------------------|--------|
| Symlinks | Fragile, drift-prone | Zero; Git submodules | 🔄 In Progress |
| Tier 0 | rylan-canon-library | rylan-canon-library (unchanged) | ✅ Complete |
| Tier 0.5 | vault-hub (partial) | rylanlabs-private-vault (full) | ✅ Complete |
| Tier 1 | rylan-inventory | rylan-inventory (unchanged) | ✅ Complete |
| Tier 2 | rylan-labs-shared-configs | rylan-labs-shared-configs (unchanged) | ✅ Complete |
| Tier 3 | Embedded in network-iac | rylan-labs-common (Galaxy) | 🔨 Phase B (Mar-Apr) |
| Tier 4a | rylan-labs-network-iac (monolithic) | rylan-labs-network-iac (refactored, 7 playbooks) | 🔨 Phase C (Apr-May) |
| Tier 4b | None | rylanlabs-aaa-core | 🚀 Phase D1 (Jun-Jul) |
| Tier 4c | None | rylanlabs-policy-engine | 🚀 Phase D2 (Jul-Aug) |
| Tier 4d | None | rylanlabs-monitoring | 🚀 Phase D3 (Jul-Aug) |
| Tier 4e | None | rylanlabs-threat-intel | 🚀 Phase D4 (Aug-Sep) |
| Tier 4f | None | rylanlabs-unifi-plugin | 🚀 Phase D5 (Sep-Oct) |
| Maturity Target | Level 4 (Pinnacle) | **Level 5 (Autonomous, Zero-Drift)** | 🎯 By Oct 2026 |

---

## 7. CONCLUSION

This **Tiered Satellite Hierarchy** represents the evolution from a centralized, monolithic infrastructure to a distributed, federated mesh where:

- **Tier 0-3** define **"What"** (governance, secrets, inventory, reusable logic)
- **Tier 4** delivers **"How"** (satellite implementations, domain-specific solutions)
- **Makefile meta-reconcilers** enforce **"No-Bypass"** culture
- **Trinity Council** ensures **Seven Pillars** compliance

**Target Outcome**: By October 2026, RylanLabs achieves **Maturity Level 5** with:

- ✅ Zero symlink drift
- ✅ RTO <7min (network-iac), <15min (full stack)
- ✅ Fully auditable, immutable change trails
- ✅ Autonomous remediation (Sentinel Loop + Bauer audits)
- ✅ Scalable architecture (unlimited VLANs/rules via Hellodeolu v7)
- ✅ Zero-trust identity (802.1X + OPA + Samba HA)

**Recommendation**: Begin Phase B (Tier 3 extraction) immediately. Tier 3 is critical path for all Phase D services.

---

**Approved By**: Trinity Council (Pending)  
**Next Review**: February 15, 2026 (Weekly check-ins during Phase A finalization)

