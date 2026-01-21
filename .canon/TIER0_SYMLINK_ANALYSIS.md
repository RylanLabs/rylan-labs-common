<!-- markdownlint-disable MD013 MD024 MD001 MD029 MD040 MD025 -->
# Deep Dive: Tier 0 Repo Analysis — Canonical Symlinks Required

## Tier 0 Repositories Identified

1. **rylan-canon-library** (Primary Source of Truth - Tier 0)
   - Role: Define and enforce RylanLabs discipline patterns
   - Authority: canon-manifest.yaml (v1.0.0)
   - Ministries: ansible, security, network, api, playbook, rotation, validation, orchestration

2. **rylan-labs-shared-configs** (Tier 0.5 - Dual Consumer/Source)
   - Role: Consume canon patterns + provide linting configs to downstream
   - Already has extensive symlinks to canon-library
   - Reference model for what rylan-labs-common should replicate

## Analysis: What's Missing in rylan-labs-common

### Currently Symlinked (✓)

- `.github/agents/.agent.md` → Agent definition
- `.github/instructions/instructions.md` → Instruction set

### NOT YET SYMLINKED (Need Implementation)

From canon-manifest.yaml orchestration ministries and supporting validators:

#### 1. **VALIDATION MINISTRY** (Pre-commit & CI enforcement)

- `.markdownlint.json` ← CRITICAL (Markdown discipline)
- `.yamllint` ← CRITICAL (YAML validation)
- `.pre-commit-config.yaml` ← CRITICAL (Git hooks)

#### 2. **ORCHESTRATION MINISTRY** (Already done)

- ✓ `.github/agents/.agent.md`
- ✓ `.github/instructions/instructions.md`

#### 3. **DOCUMENTATION MINISTRY** (Discipline guides)

- `docs/ansible-vault-discipline.md` ← Admin discipline
- `docs/security-posture-discipline.md` ← Hardening discipline
- `docs/three_domain-execution.md` ← Execution framework
- `docs/network-versioning-discipline.md` ← Network governance
- `docs/api-coverage-discipline.md` ← API tracking
- `docs/rotation-discipline.md` ← Credential lifecycle

#### 4. **VALIDATION SCRIPTS MINISTRY** (CI/Pre-commit tools)

- `scripts/validate-bash.sh` ← Bash quality (shfmt, shellcheck)
- `scripts/validate-ansible.sh` ← Ansible validation
- `scripts/validate-python.sh` ← Python validation (ruff, mypy, bandit)
- `scripts/validate-yaml.sh` ← YAML validation
- `scripts/playbook-structure-linter.py` ← 7-task 3-Domain enforcement
- `scripts/track-endpoint-coverage.py` ← API coverage tracking
- `scripts/validate-security-posture.sh` ← Security hardening checks
- `scripts/validate-rotation-readiness.sh` ← Rotation pre-flight checks

#### 5. **ANSIBLE MINISTRY** (IaC discipline)

- `templates/ansible.cfg.template` ← Ansible config template (customizable)
- May also need: `.yamllint` for Ansible vault segregation rules

#### 6. **SUPPORTING CONFIGS** (Templates & Standards)

- `templates/pyproject.toml.template` ← Python ruff/mypy config
- `templates/pre-commit-config.yaml.template` ← Pre-commit template

---

## WHY Each Symlink is Necessary

### Critical (MUST HAVE - Blocks commits)

1. **`.markdownlint.json`** ← MD022, MD031, MD060 compliance
   - Why: rylan-labs-common has extensive `.md` docs
   - Governance: Verification Domain (consistency enforcement)
   - Impact: Pre-commit hook validates all docs
   - Current State: Missing (custom rules will diverge from canon)

2. **`.yamllint`** ← YAML linting rules
   - Why: Collection has roles/tasks in YAML
   - Governance: Verification Domain (vault segregation, file naming patterns)
   - Impact: Pre-commit hook validates all YAML
   - Current State: Missing (will allow inconsistent vault patterns)

3. **`.pre-commit-config.yaml`** ← Git hooks framework
   - Why: Enforce ruff, mypy, ansible-lint, shellcheck
   - Governance: Identity Domain (standards) + Verification Domain (enforcement)
   - Impact: Blocks commits if linting fails
   - Current State: Likely exists locally but may diverge from canon

### High Priority (Should Have - Enables validation)

4. **`scripts/validate-bash.sh`** ← Bash portability
   - Why: Collection has shell scripts in playbooks/plugins
   - Governance: Hardening Domain (hardening - security scripts must be portable)
   - Impact: Pre-commit hook runs before commits
   - Evidence: 3-Domain pattern requires shell portability

5. **`scripts/validate-ansible.sh`** ← Playbook validation
   - Why: Collection ships Ansible roles and example playbooks
   - Governance: Verification Domain (pre-commit integration)
   - Impact: ansible-lint validation in CI
   - Evidence: galaxy.yml indicates Ansible collection

6. **`scripts/validate-python.sh`** ← Python code quality
   - Why: Collection has Python modules (`plugins/modules/*.py`)
   - Governance: Verification Domain (code coverage, type checking)
   - Impact: ruff, mypy, bandit validation
   - Evidence: `plugins/module_utils/rylan_utils.py`

7. **`scripts/validate-yaml.sh`** ← YAML consistency
   - Why: Collection has many YAML configs
   - Governance: Verification Domain (yamllint enforcement)
   - Impact: Pre-commit hook validation
   - Evidence: roles/*/defaults/*.yml, roles/*/vars/*.yml

### Documentation (Should Have - Education)

8. **`docs/three_domain-execution.md`** ← 7-task framework
   - Why: 3-Domain pattern is governance foundation
   - Governance: Identity Domain (identity/education)
   - Impact: README references, developer onboarding
   - Evidence: Instructions mention "Seven Pillars"

9. **`docs/security-posture-discipline.md`** ← Hardening Domain hardening
   - Why: Collection implements `hardening_harden` role
   - Governance: Hardening Domain (hardening patterns)
   - Impact: Role developers understand constraints
   - Evidence: roles/hardening_harden/ exists

10. **`docs/ansible-vault-discipline.md`** ← Vault patterns
    - Why: Collection handles vault operations
    - Governance: Identity Domain (identity via vault segregation)
    - Impact: Developers understand vault structure
    - Evidence: roles/identity_identity/ works with vault

11. **`docs/api-coverage-discipline.md`** ← API tracking
    - Why: Collection has `plugins/modules/unifi_api.py`
    - Governance: Verification Domain (coverage tracking for DR)
    - Impact: API endpoint coverage in .audit/api/
    - Evidence: UniFi API module exists

---

## Recommended Priority Order

### Phase 1: BLOCKERS (These prevent local divergence)

1. `.markdownlint.json` ← Markdown linting
2. `.yamllint` ← YAML validation
3. `.pre-commit-config.yaml` (if not already present)

### Phase 2: VALIDATORS (These enable CI/pre-commit)

4. `scripts/validate-bash.sh`
5. `scripts/validate-ansible.sh`
6. `scripts/validate-python.sh`
7. `scripts/validate-yaml.sh`

### Phase 3: LINTERS (These enforce 3-Domain)

8. `scripts/playbook-structure-linter.py` ← 7-task structure
9. `scripts/validate-security-posture.sh` ← Hardening Domain hardening

### Phase 4: DOCS (These educate developers)

10. `docs/three_domain-execution.md`
11. `docs/security-posture-discipline.md`
12. `docs/ansible-vault-discipline.md`
13. `docs/api-coverage-discipline.md`

### Phase 5: OPTIONAL (Domain-specific)

14. `scripts/track-endpoint-coverage.py` ← If API coverage tracking enabled
15. `scripts/validate-rotation-readiness.sh` ← If rotation enabled
16. `docs/rotation-discipline.md` ← If rotation enabled

---

## Summary Table

| Ministry | File | Immutable | Priority | Reason |
|----------|------|-----------|----------|--------|
| validation | `.markdownlint.json` | YES | P0 | Blocks docs with wrong formatting |
| validation | `.yamllint` | YES | P0 | Blocks YAML with wrong vault patterns |
| validation | `.pre-commit-config.yaml` | NO | P0 | Git hooks framework (customize local paths) |
| validation | `scripts/validate-bash.sh` | YES | P1 | Pre-commit hook for shell scripts |
| validation | `scripts/validate-ansible.sh` | YES | P1 | Pre-commit hook for playbooks |
| validation | `scripts/validate-python.sh` | YES | P1 | Pre-commit hook for Python modules |
| validation | `scripts/validate-yaml.sh` | YES | P1 | Pre-commit hook for YAML |
| playbook | `scripts/playbook-structure-linter.py` | YES | P2 | Enforce 7-task 3-Domain workflow |
| security | `scripts/validate-security-posture.sh` | YES | P2 | Hardening validation (Hardening Domain) |
| ansible | `templates/ansible.cfg.template` | NO | P3 | Customizable Ansible config |
| docs | `docs/three_domain-execution.md` | YES | P3 | Education: 7-task framework |
| docs | `docs/security-posture-discipline.md` | YES | P3 | Education: Hardening Domain patterns |
| docs | `docs/ansible-vault-discipline.md` | YES | P3 | Education: Vault governance |
| docs | `docs/api-coverage-discipline.md` | YES | P3 | Education: API tracking |
