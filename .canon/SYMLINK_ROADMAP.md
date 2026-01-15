# Canonical Symlink Implementation Roadmap

> **Status**: RESEARCH COMPLETE — Ready for phased implementation
> **Date**: 2026-01-14
> **Authority**: canon-manifest.yaml v1.0.0
> **Source**: rylan-canon-library (Tier 0) + rylan-labs-shared-configs (Tier 0.5)

---

## Phase 1: BLOCKERS (ASAP — Prevents local divergence)

**Duration**: 1-2 hours
**Impact**: Stops linting rule divergence immediately
**Governance**: Verification Domain (consistency enforcement)

### 1.1 → `.markdownlint.json`

```bash
# Symlink creation
ln -sf /home/egx570/repos/rylan-canon-library/.markdownlint.json \
       /home/egx570/repos/rylan-labs-common/.markdownlint.json
```

**Why**: Enforces MD022, MD031, MD060 compliance across all `.md` files

**Evidence**: Repository has 5+ markdown files:

- README.md
- CHANGELOG.md
- docs/SEVEN_PILLARS.md
- docs/EMERGENCY_RESPONSE.md
- docs/INTEGRATION_GUIDE.md

**Governance**: Verification Domain (consistency via pre-commit hook)

**Immutable**: YES (never edit locally)

### 1.2 → `.yamllint`

```bash
# Symlink creation
ln -sf /home/egx570/repos/rylan-canon-library/.yamllint \
       /home/egx570/repos/rylan-labs-common/.yamllint
```

**Why**: Enforces vault segregation patterns and YAML file naming

**Evidence**: 50+ YAML files across:

- roles/*/defaults/*.yml
- roles/*/vars/*.yml
- roles/*/tasks/*.yml
- playbooks/*.yml

**Governance**: Verification Domain (vault pattern segregation via pre-commit hook)

**Immutable**: YES (never edit locally)

### 1.3 → `.pre-commit-config.yaml` (Customizable Template)

```bash
# If file doesn't exist, copy from template
cp /home/egx570/repos/rylan-canon-library/templates/pre-commit-config.yaml.template \
   /home/egx570/repos/rylan-labs-common/.pre-commit-config.yaml

# Edit to customize local paths (if needed)
# Then ensure all validators exist (Phase 2)
```

**Why**: Framework for ruff, mypy, ansible-lint, shellcheck

**Governance**: Identity Domain (standards) + Verification Domain (enforcement)

**Immutable**: NO (customizable but should track canonical version)

---

## Phase 2: VALIDATORS (This Week — Enable CI/pre-commit)

**Duration**: 1-2 hours
**Impact**: Automates code quality checks in every commit
**Governance**: Verification Domain (validation enforcement)

### 2.1 → `scripts/validate-bash.sh`

```bash
ln -sf /home/egx570/repos/rylan-canon-library/scripts/validate-bash.sh \
       /home/egx570/repos/rylan-labs-common/scripts/validate-bash.sh
```

**Why**: Enforces shfmt + shellcheck for shell scripts
**Evidence**: playbooks/* contain embedded bash scripts
**Governance**: Hardening Domain (security scripts must be portable)
**Immutable**: YES

### 2.2 → `scripts/validate-ansible.sh`

```bash
ln -sf /home/egx570/repos/rylan-canon-library/scripts/validate-ansible.sh \
       /home/egx570/repos/rylan-labs-common/scripts/validate-ansible.sh
```

**Why**: Enforces ansible-lint validation
**Evidence**: galaxy.yml indicates Ansible collection
**Governance**: Verification Domain (ansible-lint CI enforcement)
**Immutable**: YES

### 2.3 → `scripts/validate-python.sh`

```bash
ln -sf /home/egx570/repos/rylan-canon-library/scripts/validate-python.sh \
       /home/egx570/repos/rylan-labs-common/scripts/validate-python.sh
```

**Why**: Enforces ruff + mypy + bandit for Python code
**Evidence**:

- plugins/modules/*.py
- plugins/module_utils/*.py
- tests/unit/*.py

**Governance**: Verification Domain (type safety + test coverage)
**Immutable**: YES

### 2.4 → `scripts/validate-yaml.sh`

```bash
ln -sf /home/egx570/repos/rylan-canon-library/scripts/validate-yaml.sh \
       /home/egx570/repos/rylan-labs-common/scripts/validate-yaml.sh
```

**Why**: Enforces yamllint validation across all YAML
**Evidence**: 50+ YAML files (roles, defaults, vars, playbooks)
**Governance**: Verification Domain (yamllint enforcement)
**Immutable**: YES

---

## Phase 3: TRINITY ENFORCERS (This Sprint — Enforce structure)

**Duration**: 1-2 hours
**Impact**: Validates playbook structure and security posture
**Governance**: Verification Domain + Hardening Domain

### 3.1 → `scripts/playbook-structure-linter.py`

```bash
ln -sf /home/egx570/repos/rylan-canon-library/scripts/playbook-structure-linter.py \
       /home/egx570/repos/rylan-labs-common/scripts/playbook-structure-linter.py
```

**Why**: Enforces 7-task 3-Domain workflow (GATHER→PROCESS→APPLY→VERIFY→AUDIT→REPORT→FINALIZE)

**Evidence**:

- playbooks/example-bootstrap.yml
- playbooks/example-recovery.yml
- playbooks/example-unifi-integration.yml
- playbooks/example-validate-only.yml

**Governance**: Verification Domain (3-Domain structure enforcement)
**Immutable**: YES

### 3.2 → `scripts/validate-security-posture.sh`

```bash
ln -sf /home/egx570/repos/rylan-canon-library/scripts/validate-security-posture.sh \
       /home/egx570/repos/rylan-labs-common/scripts/validate-security-posture.sh
```

**Why**: Validates hardening rules (deny-all defaults, guest isolation)

**Evidence**: roles/hardening_harden/ implements hardening

**Governance**: Hardening Domain (hardening enforcement)
**Immutable**: YES

---

## Phase 4: DOCUMENTATION (Next Sprint — Educate developers)

**Duration**: 30 minutes
**Impact**: Developers have source-of-truth references
**Governance**: Identity Domain (identity/education)

### 4.1 → `docs/three_domain-execution.md`

```bash
ln -sf /home/egx570/repos/rylan-canon-library/docs/three_domain-execution.md \
       /home/egx570/repos/rylan-labs-common/docs/three_domain-execution.md
```

**Why**: Documents 7-task 3-Domain pattern
**Governance**: Identity Domain (standards education)
**Immutable**: YES

### 4.2 → `docs/security-posture-discipline.md`

```bash
ln -sf /home/egx570/repos/rylan-canon-library/docs/security-posture-discipline.md \
       /home/egx570/repos/rylan-labs-common/docs/security-posture-discipline.md
```

**Why**: Documents hardening discipline for hardening_harden role
**Governance**: Hardening Domain (hardening patterns)
**Immutable**: YES

### 4.3 → `docs/ansible-vault-discipline.md`

```bash
ln -sf /home/egx570/repos/rylan-canon-library/docs/ansible-vault-discipline.md \
       /home/egx570/repos/rylan-labs-common/docs/ansible-vault-discipline.md
```

**Why**: Documents vault patterns for identity_identity role
**Governance**: Identity Domain (identity/vault governance)
**Immutable**: YES

### 4.4 → `docs/api-coverage-discipline.md`

```bash
ln -sf /home/egx570/repos/rylan-canon-library/docs/api-coverage-discipline.md \
       /home/egx570/repos/rylan-labs-common/docs/api-coverage-discipline.md
```

**Why**: Documents API endpoint coverage tracking for UniFi module
**Governance**: Verification Domain (API coverage for DR)
**Immutable**: YES

---

## Phase 5: OPTIONAL (If adoption of advanced patterns)

**Duration**: 1-2 hours (only if needed)

### 5.1 → `scripts/track-endpoint-coverage.py`

```bash
ln -sf /home/egx570/repos/rylan-canon-library/scripts/track-endpoint-coverage.py \
       /home/egx570/repos/rylan-labs-common/scripts/track-endpoint-coverage.py
```

**When**: When .audit/api/coverage.json tracking is enabled
**Evidence**: plugins/modules/unifi_api.py uses UniFi endpoints

### 5.2 → `scripts/validate-rotation-readiness.sh`

```bash
ln -sf /home/egx570/repos/rylan-canon-library/scripts/validate-rotation-readiness.sh \
       /home/egx570/repos/rylan-labs-common/scripts/validate-rotation-readiness.sh
```

**When**: When credential rotation workflows are enabled

### 5.3 → `docs/rotation-discipline.md`

```bash
ln -sf /home/egx570/repos/rylan-canon-library/docs/rotation-discipline.md \
       /home/egx570/repos/rylan-labs-common/docs/rotation-discipline.md
```

**When**: When credential rotation workflows are enabled

---

## Summary by Timeline

| Phase | Files | Priority | Timeline | Blocker? |
|-------|-------|----------|----------|----------|
| 1 | 3 (.markdownlint.json, .yamllint, .pre-commit-config.yaml) | P0 | ASAP | YES |
| 2 | 4 (validate-*.sh) | P1 | This week | YES |
| 3 | 2 (playbook-structure-linter.py, validate-security-posture.sh) | P2 | This sprint | NO |
| 4 | 4 (discipline docs) | P3 | Next sprint | NO |
| 5 | 3 (optional) | P4 | On-demand | NO |

---

## Verification Commands

After each phase, run:

```bash
# Verify symlinks created
find /home/egx570/repos/rylan-labs-common -type l | grep -E "\.json|\.yaml|scripts|docs"

# Verify they resolve correctly
ls -la .markdownlint.json .yamllint scripts/validate-*.sh

# Test linting (Phase 1)
markdownlint README.md

# Test validation hooks (Phase 2)
bash scripts/validate-bash.sh playbooks/

# Run full CI simulation (Phase 2+)
make ci-local
```

---

## Commit Strategy

After each phase, commit separately:

```bash
# Phase 1
git add .markdownlint.json .yamllint .pre-commit-config.yaml
git commit -m "feat(canon): symlink validation configs (Phase 1 BLOCKERS)"

# Phase 2
git add scripts/validate-*.sh
git commit -m "feat(canon): symlink validation scripts (Phase 2 VALIDATORS)"

# Phase 3
git add scripts/playbook-structure-linter.py scripts/validate-security-posture.sh
git commit -m "feat(canon): symlink 3-Domain & security enforcers (Phase 3)"

# Phase 4
git add docs/three_domain-execution.md docs/*-discipline.md
git commit -m "feat(canon): symlink canonical documentation (Phase 4)"
```

---

## Why This Order?

1. **Phase 1 first**: Linting configs block divergence immediately
2. **Phase 2 before 3**: Validators must work before enforcers run
3. **Phase 3 before 4**: Structure enforcement before documentation
4. **Phase 4 educational**: Docs don't block commits but help developers
5. **Phase 5 optional**: Only when features are actually needed

---

## Reference

- **Source Authority**: /home/egx570/repos/rylan-canon-library/canon-manifest.yaml
- **Analysis Detail**: .canon/TIER0_SYMLINK_ANALYSIS.md
- **Current Status**: .canon/symlinks.log (agent + instructions only)
