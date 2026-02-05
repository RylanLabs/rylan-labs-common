# RylanLabs Tiered Satellite Hierarchy — Action Checklist

**Date**: February 5, 2026  
**For**: Trinity Council + Engineering Leadership  
**Format**: Actionable, checked off as completed

---

## Pre-Phase A (NOW): Approval & Sign-Off

- [ ] **Trinity Council Review**: Carter, Bauer, Beale, Whitaker, Lazarus review all three docs:
  - `TIERED_SATELLITE_HIERARCHY_CANONICAL.md` (comprehensive)
  - `TIERED_SATELLITE_HIERARCHY_EXECUTIVE_SUMMARY.md` (1-page view)
  - `TIERED_SATELLITE_SYNTHESIS_ANALYSIS.md` (Grok/Leo reconciliation)

- [ ] **Stakeholder Buy-In**: 
  - [ ] Engineering Lead sign-off
  - [ ] DevOps Team sign-off
  - [ ] Security Lead (Beale) sign-off
  - [ ] Audit Lead (Bauer) sign-off

- [ ] **Create `MIGRATION-CHECKLIST-A.md`** in `.audit/`
  - Document baseline before Phase A validation
  - Assign owners/dates for each sub-task

- [ ] **Announce to Organization**: Email with three docs + quick reference card

---

## Phase A (NOW → Feb 28, 2026): Tier 0-2 Validation & Zero-Symlink Lockdown

### Tier 0: rylan-canon-library

- [ ] **Repository Audit**:
  - [ ] Run `git submodule status --recursive`
  - [ ] Verify all submodules initialized
  - [ ] Check last commit signature (GPG)

- [ ] **Content Audit**:
  - [ ] `common.mk` exists and correct (7 universal targets)
  - [ ] `canon-manifest.yaml` complete (all sacred files listed)
  - [ ] `scripts/validate*.sh` present (whitaker-scan.sh, validate-sops.sh, etc.)
  - [ ] `seven-pillars.md` current and reference-able

- [ ] **Version Lock**:
  - [ ] Tag current HEAD as `v2.x.y` (SemVer)
  - [ ] Update `Makefile` in downstream repos with MIN_CANON_VERSION

### Tier 0.5: rylanlabs-private-vault

- [ ] **GPG Key Audit**:
  - [ ] All keys valid >30 days (Sentinel check)
  - [ ] Key rotation scheduled (quarterly)
  - [ ] `.sops.yaml` encryption rules validated

- [ ] **Secrets Integrity**:
  - [ ] All vault files decryptable (spot-check)
  - [ ] No plaintext secrets in `.gitleaks` exceptions
  - [ ] Vault repo `.gitignore` enforces no decrypted files

- [ ] **Access Control**:
  - [ ] Repo membership: Beale (owner) + 1 backup signer only
  - [ ] CI/CD GPG signing enforced
  - [ ] Quarterly rotation audit passed

### Tier 1: rylan-inventory

- [ ] **Manifest Completeness**:
  - [ ] `device-manifest.yml`: All devices have MAC + hostname + VLAN + zone
  - [ ] No duplicates (MAC uniqueness check)
  - [ ] `vlan-schema.yml`: All 10 zones defined (Internal, Servers, Trusted, VoIP, IoT, Hotspot, External, DMZ, VPN, Gateway)
  - [ ] `firewall-zone-matrix.yml`: Deny-all default + explicit allow rules

- [ ] **Discovery Validation**:
  - [ ] `discovery-fetch-live-devices.yml` playbook runs successfully
  - [ ] Live state diff <5% from manifest (acceptable variance)
  - [ ] `.audit/device-discovery-snapshots/` populated

- [ ] **OON Objects**:
  - [ ] `vars/oon_objects.yml` complete (IP Sets, Port Objects, Device Sets)
  - [ ] No circular references in object hierarchy
  - [ ] Schema validated against `schemas/oon-schema.json`

### Tier 2: rylan-labs-shared-configs

- [ ] **Linting Configs**:
  - [ ] `.yamllint` synced across repos (checksum match)
  - [ ] `pyproject.toml` synced (Ruff, MyPy, Pylint rules identical)
  - [ ] `.shellcheckrc`, `.markdownlint.json`, `.gitleaks.toml` all present

- [ ] **CI/CD Templates**:
  - [ ] `.github/workflows/validate-pr.yml` functional
  - [ ] `.github/workflows/audit-trail.yml` appends to `.audit/`
  - [ ] `.github/workflows/compliance-gate.yml` enforces 5 Trinity gates

- [ ] **common.mk**:
  - [ ] `-include common.mk` in all Tier 3+ repos
  - [ ] Universal targets work: `make resolve`, `make validate`, `make cascade`

### Phase A Sign-Off

- [ ] **Run Validation Across All Tier 0-2 Repos**:
  ```bash
  for repo in canon-lib vault-hub inventory shared-configs-lib; do
    cd "submodules/$repo"
    make validate  # Must pass all gates
  done
  ```

- [ ] **Zero-Symlink Verification**:
  - [ ] Count symlinks in all repos: `find . -type l | wc -l` = 0
  - [ ] All scripts materialized (not symlinked)

- [ ] **Create `.audit/tier-0-2-validation.json`**:
  ```json
  {
    "phase": "A",
    "date": "2026-02-XX",
    "tiers_validated": [0, 0.5, 1, 2],
    "symlink_count": 0,
    "gates_passed": ["carter", "bauer", "beale", "whitaker", "lazarus"],
    "sign_off_by": ["Bauer", "Whitaker"],
    "approved": true
  }
  ```

- [ ] **Sign `MIGRATION-CHECKLIST-A.md`**:
  - [ ] Bauer (Verification): ________________
  - [ ] Whitaker (Offensive): ________________
  - [ ] Trinity Council Lead: ________________

- [ ] **Phase A Complete**: Announce readiness for Phase B kickoff (Mar 1)

---

## Phase B (Mar 1 → Apr 30, 2026): Tier 3 Extraction & Galaxy Publishing

### Task 1: Repository Setup

- [ ] **Create `rylan-labs-common` repository**:
  - [ ] Initialize GitHub repo
  - [ ] Add CODEOWNERS file (Trinity Council)
  - [ ] Enable branch protection (require 2 reviews + all checks pass)
  - [ ] Add `.gitleaks.toml` from shared-configs-lib

- [ ] **Initial Directory Structure**:
  ```
  rylan-labs-common/
    roles/
      carter-identity/
      bauer-verify/
      beale-harden/
    plugins/
      modules/
      filters/
    scripts/
    lib/
    tests/
    galaxy.yml
    README.md
  ```

### Task 2: Extract Trinity Roles (With Canary Rollout)

- [ ] **carter-identity** (from network-iac):
  - [ ] Copy `roles/carter-identity/` to common
  - [ ] Remove network-iac-specific vars (e.g., hardcoded VLAN IDs)
  - [ ] Move to `defaults/main.yml` (customizable per consumer)
  - [ ] Add role-level `README.md` with examples
  - [ ] **Canary Rollout**: Deploy `carter-identity` to staging for 7 days; verify MAC registration.
  - [ ] Test: Role idempotent when run 3x

- [ ] **bauer-verify** (from network-iac):
  - [ ] Copy `roles/bauer-verify/` to common
  - [ ] Refactor to accept inventory paths as variables
  - [ ] Add role-level README + validation rules
  - [ ] **Canary Rollout**: Deploy `bauer-verify` to staging; verify drift detection.
  - [ ] Test: Drift detection works on foreign manifests

- [ ] **beale-harden** (from network-iac):
  - [ ] Copy `roles/beale-harden/` to common
  - [ ] Parameterize firewall rule templates
  - [ ] Add zone matrix validation (generic)
  - [ ] **Canary Rollout**: Deploy `beale-harden` to staging; verify zone isolation.
  - [ ] Test: Rules deploy safely on test UXG instance

### Task 3: Extract Custom Modules & Plugins

- [ ] **unifi_api module**:
  - [ ] Copy `plugins/modules/unifi_api.py` to common
  - [ ] Add comprehensive docstrings (DOCUMENTATION, EXAMPLES, RETURN)
  - [ ] Add unit tests (test_unifi_api.py)
  - [ ] Test: Module passes ansible-test

- [ ] **zone_resolver filter**:
  - [ ] Copy `plugins/filters/zone_resolver.py` to common
  - [ ] Add docstrings + unit tests
  - [ ] Test: Resolves devices correctly

- [ ] **flatten_oon_groups filter**:
  - [ ] Copy/create `plugins/filters/flatten_oon_groups.py`
  - [ ] Add docstrings + unit tests
  - [ ] Test: Handles circular references gracefully

- [ ] **presencio_redactor filter**:
  - [ ] Create `plugins/filters/presencio_redactor.py`
  - [ ] Add PII redaction logic (MAC, IP, hostname)
  - [ ] Test: No PII in stdout/logs

### Task 4: Extract Validation & Utility Scripts

- [ ] **validate-isolation.sh**:
  - [ ] Copy from network-iac to common/scripts/
  - [ ] Make generic (accept zone definitions as arg)
  - [ ] Add unit tests

- [ ] **whitaker-scan.sh**:
  - [ ] Copy from canon-lib to common/scripts/
  - [ ] Ensure portable (no repo-specific paths)

- [ ] **sentinel-expiry.sh**:
  - [ ] Copy from canon-lib to common/scripts/
  - [ ] Add cert/key expiry checks

- [ ] **playbook-structure-linter.py**:
  - [ ] Copy from canon-lib to common/scripts/
  - [ ] Add docstring + examples

### Task 5: Exception Handling & Observability

- [ ] **app/exceptions.py**:
  - [ ] Create canonical exception hierarchy
  - [ ] Include: UniFiError, UniFiAPIError, AnsibleValidationError, ManifestDriftError, etc.
  - [ ] Add docstrings per exception

- [ ] **lib/audit_trail_writer.py**:
  - [ ] Create centralized audit logger
  - [ ] Writes append-only to `.audit/audit-trail.jsonl`
  - [ ] Includes: timestamp, user, action, state-before/after, exit-code, hash

### Task 6: Galaxy Publication

- [ ] **Create `galaxy.yml`**:
  ```yaml
  namespace: rylanlabs
  name: unifi
  version: 2.1.0
  description: RylanLabs Unified UniFi API collection (Trinity roles + modules)
  authors:
    - RylanLabs Trinity Council
  repository: https://github.com/RylanLabs/rylan-labs-common
  ```

- [ ] **Create `MANIFEST.md`**:
  - [ ] Overview of collection
  - [ ] List all roles, modules, filters, scripts
  - [ ] Dependencies (ansible>=2.9, python>=3.6)
  - [ ] Installation: `ansible-galaxy collection install rylanlabs.unifi:>=2.1.0`

- [ ] **Per-role README**:
  - [ ] Purpose
  - [ ] Variables (required/optional)
  - [ ] Example playbook

- [ ] **Publish to Ansible Galaxy**:
  - [ ] Create Galaxy account (if not exists)
  - [ ] Publish collection: `ansible-galaxy collection publish`
  - [ ] Tag release: `git tag v2.1.0`
  - [ ] Verify on Galaxy: https://galaxy.ansible.com/ui/repo/published/rylanlabs/unifi/

### Task 7: Testing & CI/CD

- [ ] **Unit Tests**:
  - [ ] `tests/unit/` directory with pytest tests
  - [ ] Aim for 90%+ code coverage
  - [ ] Test all exception paths

- [ ] **Integration Tests**:
  - [ ] `tests/integration/` with ansible-test integration tests
  - [ ] Spin up test UniFi instance (Docker)
  - [ ] Test roles against real API

- [ ] **CI/CD**:
  - [ ] `.github/workflows/test.yml` runs unit + integration tests
  - [ ] `.github/workflows/publish.yml` publishes to Galaxy on tag

### Task 8: Integration & Refactoring

- [ ] **Update `rylan-labs-network-iac`**:
  - [ ] Add `submodules/common-lib` as git submodule
  - [ ] Update `requirements.yml`: `collections: [{name: rylanlabs.unifi, version: ">=2.1.0"}]`
  - [ ] Remove local `roles/` directory (use Galaxy)
  - [ ] Update playbooks to use `rylanlabs.unifi.carter_identity`, etc.

- [ ] **Test Flagship Still Works**:
  - [ ] Run: `ansible-playbook playbooks/00-bootstrap-foundation.yml --check`
  - [ ] Verify no role not found errors
  - [ ] Test idempotency: Run twice, no changes second time

### Task 9: Validation Gates (Phase B)

- [ ] **Carter Gate**: 
  - [ ] Manifest completeness (all roles have vars documented)

- [ ] **Bauer Gate**:
  - [ ] Audit trail appends to `.audit/` on extraction
  - [ ] No drift between canon-lib and common-lib

- [ ] **Beale Gate**:
  - [ ] Secret scanning passes (no hardcoded keys in roles)
  - [ ] gitleaks.toml enforced

- [ ] **Whitaker Gate**:
  - [ ] Adversarial testing: Attempt to bypass role validations
  - [ ] Test bypass vectors (empty vars, invalid inputs)

- [ ] **Lazarus Gate**:
  - [ ] RTO validation: How long to rollback to using local roles?
  - [ ] Backup plan if Galaxy offline

### Phase B Sign-Off

- [ ] **Create `.audit/tier-3-extraction.json`**:
  ```json
  {
    "phase": "B",
    "date": "2026-04-15",
    "extracted_artifacts": ["roles/3", "modules/4", "filters/3", "scripts/5"],
    "galaxy_collection": "rylanlabs.unifi:2.1.0",
    "galaxy_url": "https://galaxy.ansible.com/ui/repo/published/rylanlabs/unifi/",
    "test_coverage": "91%",
    "all_gates_pass": true,
    "sign_off_by": ["Trinity Council"]
  }
  ```

- [ ] **Sign `MIGRATION-CHECKLIST-B.md`**:
  - [ ] Carter (Identity): ________________
  - [ ] Bauer (Verification): ________________
  - [ ] Beale (Hardening): ________________
  - [ ] Whitaker (Offensive): ________________
  - [ ] Lazarus (Recovery): ________________
  - [ ] Trinity Council Lead: ________________

- [ ] **Announce Phase B Complete**: Green light for Phase C (Apr 16)

---

## Phase C (Apr 16 → May 31, 2026): Tier 4a Flagship Refactoring

- [ ] **Consolidate Playbooks** (99 → 7 core):
  - [ ] Keep: 00-bootstrap-foundation, 01-sync-unifi-objects, 02-inventory-discovery, 03-remediate-switch-ports, 06-verify-security-compliance, 99-verify-compliance, plus 1 utility
  - [ ] Archive rest to `archive/playbooks/`

- [ ] **Update to Galaxy Collection**:
  - [ ] `requirements.yml` includes rylanlabs.unifi
  - [ ] Playbooks reference roles as `rylanlabs.unifi.carter_identity`
  - [ ] Verify all playbooks run idempotent

- [ ] **RTO Hardening**:
  - [ ] `eternal-resurrect.sh` tested, documented
  - [ ] Pre-change snapshots captured to `.audit/`

- [ ] **Validation Gates**:
  - [ ] All seven pillars enforced (see Phase A for per-pillar checks)

- [ ] **Sign `MIGRATION-CHECKLIST-C.md`**: Trinity Council approval

---

## Phase D (Jun 1 → Oct 31, 2026): Tier 4 Satellite Rollout

### D1: rylanlabs-aaa-core (Jun 1 → Jul 15)

- [ ] **Repository Setup**: Create repo, structure
- [ ] **Samba HA Bootstrap**: Roles, playbooks, tests
- [ ] **FreeRADIUS Deployment**: RadSec, 802.1X, dynamic VLAN
- [ ] **OPA Integration**: Policy evaluation engine
- [ ] **Validation**: All 5 gates pass
- [ ] **Whitaker Penetration**: AD compromise attempts, MitM 802.1X
- [ ] **Sign-Off**: Beale + Bauer approve

### D2: rylanlabs-policy-engine (Jul 16 → Aug 15)

- [ ] **Repository Setup**: Create repo, structure
- [ ] **Rego Policies**: Firewall rules, zone isolation, compliance
- [ ] **YAML Policies**: Compliance mappings (CIS, PCI-DSS)
- [ ] **Dynamic Evaluation**: Runtime policy checks
- [ ] **Validation**: Rego unit tests (100% coverage)
- [ ] **Sign-Off**: Bauer + Whitaker approve

### D3: rylanlabs-monitoring (Jul 1 → Aug 31, parallel)

- [ ] **Repository Setup**: Create repo, structure
- [ ] **Prometheus**: Scrape configs, alerting rules
- [ ] **Loki**: Log aggregation setup
- [ ] **Grafana**: 3 dashboards (network, AAA, audit)
- [ ] **Alerts**: Zone violations, cert expiry, auth spike
- [ ] **Validation**: Query latency <1s, retention validated
- [ ] **Sign-Off**: Bauer + Lazarus approve

### D4: rylanlabs-threat-intel (Aug 16 → Sep 30)

- [ ] **Repository Setup**: Create repo, structure
- [ ] **Feed Ingestion**: MISP, OTX, Abuse.ch, GreyNoise
- [ ] **Dynamic Deny Lists**: Auto-update firewall IP Sets
- [ ] **Anomaly Detection**: Isolation Forests ML model
- [ ] **Response Playbooks**: Auto-quarantine suspicious devices
- [ ] **Validation**: False-positive rate <5%, latency <5min
- [ ] **Sign-Off**: Beale + Whitaker approve

### D5: rylanlabs-unifi-plugin (Sep 1 → Oct 31, post-D1)

- [ ] **Repository Setup**: Create repo, structure
- [ ] **Node.js Plugin**: UniFi event hooks
- [ ] **CoA Integration**: Real-time VLAN reassignment
- [ ] **LDAP Watcher**: React to AD group changes
- [ ] **Event Streaming**: Send to Loki
- [ ] **Validation**: Event latency <500ms
- [ ] **Sign-Off**: Carter + Lazarus approve

### Phase D Sign-Off

- [ ] **Create `.audit/tier-4-deployment.json`**:
  ```json
  {
    "phase": "D",
    "date": "2026-10-31",
    "satellites_deployed": ["aaa-core", "policy-engine", "monitoring", "threat-intel", "unifi-plugin"],
    "maturity_level": 5,
    "rto_network_iac": "<7min",
    "rto_full_stack": "<15min",
    "all_gates_pass": true,
    "sign_off_by": ["Trinity Council"]
  }
  ```

- [ ] **Final Sign-Off**: All Trinity agents approve → **Maturity Level 5 ACHIEVED**

---

## Post-Migration (Nov 2026+): Operations & Maintenance

- [ ] **Quarterly Key Rotation**: rylanlabs-private-vault
- [ ] **Nightly Org-Audit**: `make org-audit` across mesh
- [ ] **Monthly Whitaker Scans**: Adversarial testing on all repos
- [ ] **Quarterly Lazarus Drills**: RTO validation, recovery testing
- [ ] **6-Month Retrospective**: Review maturity, plan enhancements

---

## Success Metrics (By October 2026)

- [ ] **Zero Symlink Drift**: All repos checked (target: 0)
- [ ] **RTO <7min**: Network-iac bootstrap from clean state
- [ ] **RTO <15min**: Full stack (all Tier 4 services)
- [ ] **100% Audit Trail**: Every action immutable in `.audit/`
- [ ] **Maturity Level 5**: Autonomous, self-healing, no-bypass enforced
- [ ] **Zero-Trust Identity**: 802.1X + OPA + Samba HA deployed
- [ ] **Unlimited Scalability**: Hellodeolu v7 zones/rules tested
- [ ] **All Trinity Gates**: Carter/Bauer/Beale/Whitaker/Lazarus automated

---

**This checklist is living. Update it as tasks complete. Share progress in weekly Trinity Council meetings.**


