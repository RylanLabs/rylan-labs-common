# Canon Integration Architecture

> **⚠️ ABSORBED**: This document has been absorbed into [gitops-substrate-paradigm.md](gitops-substrate-paradigm.md) Section 2.
> This file is retained for historical reference and backward compatibility.
> For canonical guidance, see the master paradigm document.

**Repository Role**: Pure Consumer of `rylan-canon-library` v2.0.0

---

## Overview

`rylan-labs-common` integrates with canonical infrastructure-as-code standards
defined in `rylan-canon-library`. This integration establishes:

- Zero drift via symlinks to canonical linting and validators
- Pre-commit hooks that validate code before commit
- Guardian alignment: Identity, Audit, Hardening patterns enforced
- Local access to 3-Domain, security, vault, and API disciplines

---

## Symlink Map (13 Total)

### Linting Configs (3 symlinks)

Ensures all repos enforce identical code formatting and style rules.

| Symlink | Source | Purpose |
| --- | --- | --- |
| `.markdownlint.json` | shared-configs | Markdown rules (MD013, MD024) |
| `.yamllint` | shared-configs | YAML formatting (160-char limit) |
| `.pre-commit-config.yaml` | shared-configs | Git hooks (ruff, mypy, lint) |

**Impact**: Developers cannot commit code that violates linting rules.

### Validator Scripts (6 symlinks)

Invoked by pre-commit hooks to validate code.

| Script | Source | Languages |
| --- | --- | --- |
| `scripts/validate-bash.sh` | shared-configs | Bash/Shell |
| `scripts/validate-ansible.sh` | shared-configs | Ansible |
| `scripts/validate-python.sh` | shared-configs | Python |
| `scripts/validate-yaml.sh` | shared-configs | YAML |
| `scripts/playbook-structure-linter.py` | shared-configs | 3-Domain validation |
| `scripts/validate-security-posture.sh` | shared-configs | Security audit |

**Impact**: Pre-commit hooks now functional. Immediate validation feedback.

### 3-Domain Enforcers (2 symlinks)

Enforce the sacred 3-Domain pattern and security requirements.

| Enforcer | Source | Requirement |
| --- | --- | --- |
| `playbook-structure-linter.py` | shared-configs | 7-task 3-Domain structure |
| `validate-security-posture.sh` | shared-configs | Production Standards compliance |

**Impact**: Playbooks must follow 3-Domain. Prevents ad-hoc tasks.

### Discipline Docs (4 symlinks)

Developer reference material for standards and best practices.

| Document | Lines | Purpose |
| --- | --- | --- |
| `three_domain-execution.md` | 335 | 3-Domain pattern execution |
| `security-posture-discipline.md` | 56 | Security hardening |
| `ansible-vault-discipline.md` | 75 | Secrets management |
| `api-coverage-discipline.md` | 66 | API coverage requirements |

**Impact**: Developers have canonical reference locally.

---

## Integration Pattern

```text
rylan-labs-common (Pure Consumer)
    ├─ Inherits from rylan-canon-library
    │   └─ Discipline docs (three_domain, security, vault, api)
    │
    ├─ Inherits from rylan-labs-shared-configs
    │   ├─ Linting configs
    │   └─ Validators + enforcers
    │
    └─ Provides to: None (Ansible Galaxy collection)
```

This is a **pure consumer architecture**:

- ✅ Inherits everything from canonical sources
- ❌ Does not provide configs to other repos
- ✅ Automatically inherits updates
- ✅ Zero maintenance burden

---

## Developer Workflow

### Installation

```bash
git clone https://github.com/RylanLabs/rylan-labs-common.git
cd rylan-labs-common
pre-commit install
cat docs/disciplines/three_domain-execution.md
```

### Commit Workflow

```bash
git add playbooks/my-playbook.yml
git commit -m "feat(playbook): Add my-playbook"

# Pre-commit validates:
# ✓ Markdown linting
# ✓ YAML linting
# ✓ Bash validation
# ✓ Ansible validation
# ✓ Python validation
# ✓ 3-Domain structure
# ✓ Security posture
```

### Manual Validation

```bash
pre-commit run --all-files
./scripts/validate-ansible.sh
python3 scripts/playbook-structure-linter.py playbooks/*.yml
```

---

## Symlink Maintenance

### Verify Symlinks

```bash
find . -type l | grep -E "(canon|shared-configs)"
find . -type l -exec test ! -e {} \; -print
readlink -f .yamllint
```

### Update on Canon Changes

When canon library updates:

```bash
cd ~/repos/rylan-canon-library && git pull
cd ~/repos/rylan-labs-shared-configs && git pull
# Symlinks automatically resolve to new versions
pre-commit run --all-files
git commit -m "chore: Sync canon symlinks to latest"
```

---

## Troubleshooting

### Broken Symlink

```bash
find . -type l -exec test ! -e {} \; -print
ls -la ../rylan-canon-library/docs/three_domain-execution.md
ln -sf ../../../rylan-canon-library/docs/three_domain-execution.md \
  docs/disciplines/three_domain-execution.md
```

### Pre-Commit Failures

```bash
pre-commit uninstall
pre-commit install
pre-commit run --all-files --verbose
```

### Symlinks Not Working

```bash
cd docs/disciplines && ls -la three_domain-execution.md
head three_domain-execution.md
cd ~/repos && git clone https://github.com/RylanLabs/rylan-canon-library.git
```

---

## CI/CD Integration

### Audit Job

The `.github/workflows/galaxy-publish.yml` includes `audit-canon-drift`:

1. Clones `rylan-canon-library` v2.0.0
2. Verifies zero symlink drift
3. Fails build if drift detected
4. Publishes to Galaxy only on pass

### Compliance Metrics

```text
Current Status (2026-01-14):
  ✅ 13/13 symlinks present
  ✅ 0 broken links
  ✅ Pre-commit hooks functional (12 hooks)
  ✅ All validators passing
  ✅ Compliance: 100% (up from 13%)
  ✅ Guardian Alignment: A+
```

---

## References

- **Canon Library**: [rylan-canon-library](https://github.com/RylanLabs/rylan-canon-library)
- **Shared Configs**: [rylan-labs-shared-configs](https://github.com/RylanLabs/rylan-labs-shared-configs)
- **Metadata**: `.canon-metadata.yml`

**Integration Status**: ✅ COMPLETE
**Compliance Score**: 100/100
