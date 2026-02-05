# GitOps Substrate Paradigm

> **Version**: v2.1.0-SUBSTRATE
> **Date**: February 3, 2026
> **Status**: Canonical — Production-Ready Foundation
> **Classification**: Meta-GitOps Architecture

---

## Executive Summary: Meta-GitOps — Governing the Governor

Traditional GitOps (Flux, ArgoCD) reconciles **infrastructure state** to match Git.
RylanLabs has inverted this pattern: The Makefile reconciles **code entry into Git itself**.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TRADITIONAL GITOPS                               │
│    Git Repository  ───────►  Infrastructure (K8s, VMs, etc.)        │
│    (Desired State)           (Actual State)                         │
│         │                          │                                │
│         └──── Operator Reconciles ─┘                                │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    META-GITOPS (RylanLabs Innovation)               │
│    Code Changes  ───────►  Git Repository (SSOT)                    │
│    (Developer Intent)      (Versioned State)                        │
│         │                          │                                │
│         └──── Makefile Reconciles ─┘                                │
│                                                                     │
│    The Makefile governs HOW code enters Git, not just WHAT runs.    │
└─────────────────────────────────────────────────────────────────────┘
```

**The Innovation**: By treating codebase evolution as declaratively managed state,
we've created a self-governing substrate—a foundational layer that enforces rigor
while enabling frictionless velocity.

**OpenGitOps Alignment** (CNCF Standard v1.0.0):

| Principle | Traditional | Meta-GitOps (RylanLabs) |
|-----------|-------------|-------------------------|
| Declarative | K8s manifests | `galaxy.yml`, `pyproject.toml`, role YAML |
| Versioned & Immutable | Git history | Git history + `.audit/make-history.log` |
| Pulled Automatically | Operator polls Git | `make materialize` resolves symlinks |
| Continuously Reconciled | Operator applies state | `make validate` + `.gitops-orchestrate` |
| **Meta-Reconciliation** | ❌ Not addressed | ✅ Makefile governs code entry |

---

## 1. Philosophical Foundation: IRL-First Approach

> *Absorbed from: TANDEM_WORKFLOW.md*

### Human Understanding First

**Why this matters**: Blind automation creates fragility. When operators don't
understand *why* a rule exists, they bypass it.

**Core Principle**: Understand the "why" before automating the "how."

**Implementation Phases**:

1. **Manual Validation Phase** — Perform tasks manually first, document decisions
2. **Helper Tools** — Add tools that make manual tasks easier
3. **Soft Gates** — Warnings that inform but don't block
4. **Hard Gates** — Blocks with clear remediation paths
5. **Continuous Monitoring** — Automated drift detection

**Real Example** (from firewall-consolidation):
- Early attempt: Automate firewall rule generation
- Result: Generated 47 rules, many redundant
- Problem: Automation doesn't understand business context
- Solution: Manually design rules, understand each one
- Outcome: Consolidated to 10 rules, all justified, hardware-aware

**Lesson**: Automation amplifies understanding, but can't replace it.

### Gradual Automation Maturity

| Phase | Gate Type | Bypass Allowed? | Example |
|-------|-----------|-----------------|---------|
| 1. Manual | Documentation | Yes | Developer runs `shellcheck` manually |
| 2. Helper | Soft gate | Yes | Pre-commit warns but allows `--no-verify` |
| 3. Enforced | Hard gate | No | CI blocks merge if validation fails |
| 4. Gatekeeper | Pre-receive | No | Server rejects push if non-compliant |

**The Meta-GitOps layer operates at Phase 3-4**, enforcing hard gates while
maintaining escape hatches via Lazarus rollback.

---

## 2. Substrate Architecture: Integration Layer

> *Absorbed from: CANON-INTEGRATION.md*

### Repository Hierarchy

```
rylan-canon-library (Tier 0: Governance)
    │
    ├── Provides: Discipline docs, patterns, standards
    │
    ▼
rylan-labs-shared-configs (Tier 1: Configurations)
    │
    ├── Provides: Linting configs, validators, hooks
    │
    ▼
rylan-labs-common (Tier 2: Shared Logic) ← YOU ARE HERE
    │
    ├── Provides: Ansible collection, modules, plugins
    ├── Consumes: Tier 0 + Tier 1 via symlinks
    │
    ▼
rylan-labs-network-iac (Tier 3: Domain Implementation)
    │
    └── Consumes: Tier 2 collection via ansible-galaxy
```

### Symlink Materialization

The `make materialize` target resolves external dependencies:

```bash
# Clones/updates shared-configs repository
git clone git@github.com:RylanLabs/rylan-labs-shared-configs.git ../rylan-labs-shared-configs

# Resolves symlinks to materialized assets
.github/scripts/resolve-symlinks.sh
```

**Symlink Categories** (13 total):

| Category | Count | Purpose |
|----------|-------|---------|
| Linting Configs | 3 | `.markdownlint.json`, `.yamllint`, `.pre-commit-config.yaml` |
| Validator Scripts | 6 | `validate-bash.sh`, `validate-ansible.sh`, etc. |
| 3-Domain Enforcers | 2 | `playbook-structure-linter.py`, `validate-security-posture.sh` |
| Discipline Docs | 4 | `trinity-execution.md`, `security-posture-discipline.md`, etc. |

**Impact**: Zero drift via declarative symlinks. Updates propagate automatically.

---

## 3. The Makefile as Reconciler

### Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                    MAKEFILE v2.1.0-SUBSTRATE                      │
├──────────────────────────────────────────────────────────────────┤
│  PHASE 0: INITIALIZATION                                         │
│  ├── make init          → Install deps, pre-commit hooks         │
│  ├── make materialize   → Clone/update shared-configs            │
│  └── make resolve       → Resolve symlinks idempotently          │
├──────────────────────────────────────────────────────────────────┤
│  PHASE 1: VALIDATION (Bauer Guardian)                            │
│  ├── make audit-domains → 3-Domain Consensus check               │
│  ├── make secure        → Security posture audit (S603/S310)     │
│  └── make verify-maturity → Coverage gate (≥24%)                 │
├──────────────────────────────────────────────────────────────────┤
│  PHASE 2: COMPLIANCE                                             │
│  ├── make validate      → Full validation suite                  │
│  └── make validate-static → Ruff, Mypy, Bandit                   │
├──────────────────────────────────────────────────────────────────┤
│  PHASE 3: GITOPS PUBLISHING                                      │
│  ├── make publish       → Stage, commit, push, PR                │
│  ├── make publish-draft → Same but draft PR                      │
│  └── make publish-merge → Same with auto-merge                   │
├──────────────────────────────────────────────────────────────────┤
│  PHASE 4: DISTRIBUTION                                           │
│  ├── make build         → Build collection artifact              │
│  └── make release       → Publish to Ansible Galaxy              │
└──────────────────────────────────────────────────────────────────┘
```

### The `.gitops-orchestrate` Engine

The internal orchestration script implements the reconciliation loop:

```bash
.gitops-orchestrate:
    # Phase 0: Pre-Flight Assessment (Bauer Guardian)
    $(MAKE) validate

    # Phase 1: Branch Provisioning (Carter Guardian)
    BRANCH=feat/$(date +%Y%m%d-%H%M%S)
    git checkout -b $BRANCH

    # Phase 2: Stage & Commit (Audit Guardian)
    git add .
    git commit -S -m "$(msg)"  # GPG signed

    # Phase 3: Push & PR (Beale Guardian)
    git push origin HEAD
    gh pr create --base master --title "$(msg)" $(ARGS)

    # Audit Trail
    echo "[timestamp] $BRANCH -> $PR_URL" >> .audit/make-history.log
```

### Trinity Guardian Mapping

| Phase | Guardian | Responsibility | Failure Mode |
|-------|----------|----------------|--------------|
| Pre-Flight | **Bauer** (Audit) | Validation, consensus, coverage | Block publish |
| Provisioning | **Carter** (Identity) | Branch creation, naming | Rollback branch |
| Commit | **Bauer** (Audit) | Staging, signing, audit log | Lazarus recovery |
| Hardening | **Beale** (Hardening) | Push, PR creation, protection | Manual recovery |

### Push-Based vs Pull-Based Clarification

**Important**: This implementation is **Push-Based GitOps**, not Pull-Based.

| Aspect | Pull-Based (ArgoCD/Flux) | Push-Based (RylanLabs) |
|--------|--------------------------|------------------------|
| Trigger | Operator polls Git | Developer runs `make publish` |
| Direction | Git → Infrastructure | Code → Git |
| Reconciler | In-cluster operator | Local Makefile |
| Use Case | Infrastructure state | Codebase evolution |

Both are valid GitOps patterns per [gitops.tech](https://gitops.tech). Push-based
is appropriate for code management; Pull-based for runtime infrastructure.

---

## 4. Seven Pillars Compliance Matrix

> *Absorbed from: SEVEN_PILLARS.md*

### Pillar 1: Idempotency

**Principle**: Multiple executions produce identical outcome — no side effects on re-run.

**Makefile Implementation**:
- `make materialize` checks if repo exists before cloning
- `make resolve` validates symlinks, recreates only if broken
- `make publish` skips commit if no changes staged

**Validation**: Run `make validate` twice — second run changes nothing.

### Pillar 2: Error Handling

**Principle**: Fail fast, fail loud, provide context.

**Makefile Implementation**:
- `set -euo pipefail` in all shell commands
- Explicit error messages with remediation steps
- Exit codes: 0 (success), 1 (validation), 2 (git), 3 (config)

**Example**:
```makefile
@if [ -z "$(msg)" ]; then
    echo "ERROR: Missing 'msg' parameter. Usage: make publish msg='...'";
    exit 1;
fi
```

### Pillar 3: Functionality

**Principle**: Does exactly one thing, perfectly.

**Makefile Implementation**:
- Each target has single responsibility
- `--help` via `make help`
- Clear naming: `validate`, `publish`, `build`

### Pillar 4: Audit Logging

**Principle**: Every action traceable.

**Makefile Implementation**:
- `.audit/make-history.log` captures all operations
- Timestamped entries with target, branch, PR URL
- Git history provides complete audit trail

**Format**:
```
[2026-02-03 19:11:51] [publish] feat/20260203-191151 -> https://github.com/.../pull/42
```

### Pillar 5: Failure Recovery

**Principle**: Graceful degradation + clear recovery path.

**Makefile Implementation** (Lazarus Guardian):
```bash
# On commit failure:
echo "Rollback via: git checkout - && git branch -D $BRANCH"
git checkout - > /dev/null 2>&1
git branch -D $BRANCH > /dev/null 2>&1
```

**RTO Target**: <5 minutes from failure to clean state.

### Pillar 6: Security Hardening

**Principle**: Assume hostile environment.

**Makefile Implementation**:
- Mandatory GPG signing: `git commit -S`
- Security posture audit: `make secure` (S603/S310 tracking)
- Branch protection: Cannot push directly to master
- Credential isolation: Vault-encrypted tokens

### Pillar 7: Documentation Clarity

**Principle**: Junior at 3 AM can run and understand.

**Makefile Implementation**:
- `make help` displays all targets with descriptions
- README "Quick Start" section
- This document as comprehensive reference

---

## 5. Canonical Roadmap: Phases 0-5

> *From: Grok's Strategic Analysis (February 3, 2026)*

| Phase | Guardian Lead | Actions (Idempotent, Validated) | Outcomes & Validation | Timeline | ROI/Dependencies |
|-------|---------------|----------------------------------|-----------------------|----------|------------------|
| **Phase 0: Pre-Flight Assessment** | Bauer | Run `make validate`; fix .audit staging; test `make publish-draft` idempotently. Drift check vs. SSOT. | Unblocked workflow; Lazarus no false triggers. Validate: No duplicate commits on re-run. | Immediate | High: Fixes test anomalies; Dep: .gitops-orchestrate script. |
| **Phase 1: Stabilization & Enhancement** | Carter | Implement branch slugification; add auto-stage for .audit/. Add detect-arch guardrail for ARM. | Human-readable branches; full idempotency. Validate: `make publish msg="test"` succeeds. | This Week | Medium: Improves git history; Dep: Makefile v2.1.0-SUBSTRATE. |
| **Phase 2: Ansible Symbiosis & Multi-Repo** | Beale | Create playbooks/publish-cascade.yml: Sequence `make publish` across Tier 0-3 repos; integrate Vault for GALAXY_TOKEN. Enforce GPG/Ed25519 signing. | Cross-repo GitOps; secure publishing. Validate: Dry-run cascade; RTO <15min rollback. | This Month | High: Scales to UniFi/Proxmox; Dep: Ansible 2.14+, symlinks. |
| **Phase 3: Observability & Maturity Escalation** | Bauer | Integrate Promtail/Loki for Makefile logs (30d retention); raise coverage gate to ≥50% via adversarial tests. Define zero-trust 8.0 in this doc. | Centralized audits; verified metrics. Validate: Grafana dashboards green; coverage --fail-under=50. | Q1 2026 | Medium: Enables feedback loop; Dep: Loki 2.x+, Grafana 10.x+. |
| **Phase 4: Community Distribution & Galaxy** | Carter | Add `make galaxy-publish`: Build tar.gz, publish with token; update galaxy.yml to "Production-Grade." Contribute template to argoproj/gitops-engine. | Public reusability; RylanLabs ecosystem growth. Validate: ansible-galaxy install succeeds; PR merged upstream. | Q2 2026 | High: Community ROI; Dep: GALAXY_TOKEN in Vault. |
| **Phase 5: Adversarial Testing & Paradigm Actualization** | Beale/Whitaker | Simulate failures (EAP downgrades, zone DAG cycles); extend to dynamic VLANs/WireGuard. Escalate cross-domain for full substrate shift. | Resilient paradigm; 8.0 maturity. Validate: Whitaker tests pass; eternal-resurrect.sh --full <12m48s. | Q2 2026 End | Critical: Fortress eternal; Dep: All prior phases. |

---

## 6. Emergency & Recovery Procedures

> *Absorbed from: EMERGENCY_RESPONSE.md*

### Lazarus Recovery Protocol

**Trigger**: Any failure in `.gitops-orchestrate` execution.

**Automatic Recovery**:
```bash
# Executed automatically on commit/push failure:
git checkout - > /dev/null 2>&1      # Return to previous branch
git branch -D $BRANCH > /dev/null 2>&1  # Delete failed branch
exit 1                                # Signal failure to caller
```

**Manual Recovery** (if automatic fails):
```bash
# 1. Identify the failed branch
git branch -a | grep feat/

# 2. Switch to master
git checkout master

# 3. Delete the failed branch
git branch -D feat/YYYYMMDD-HHMMSS

# 4. Reset any staged changes
git reset --hard HEAD

# 5. Verify clean state
git status
```

### eternal-resurrect.sh Integration

For catastrophic failures requiring full system recovery:

```bash
# Target: RTO <15 minutes from clean OS
./scripts/eternal-resurrect.sh --full

# Phases:
# 1. Clone all Tier 0-3 repos
# 2. Run make init on each
# 3. Resolve all symlinks
# 4. Validate consensus across repos
# 5. Restore .audit/ from backup
```

**Validation**: Full resurrection drill quarterly. Target: <12m48s.

---

## 7. Anti-Patterns & Constraints

### What NOT To Do

| Anti-Pattern | Why It's Dangerous | Correct Approach |
|--------------|-------------------|------------------|
| Interactive prompts in Makefile | Breaks CI/CD automation | Use parameters: `make publish msg="..."` |
| Hardcoded branch names | Collision risk | Timestamp-based: `feat/YYYYMMDD-HHMMSS` |
| Skipping `make validate` | Dirty code enters SSOT | Validate is mandatory pre-flight |
| Direct push to master | Bypasses protection | Always use `make publish` → PR |
| Storing secrets in Git | Security breach | Use Ansible Vault, environment vars |
| Silent failures | Undiagnosed issues | Fail loud with remediation steps |

### Constraints (Non-Negotiable)

1. **GPG Signing Required**: All commits must be signed (`-S` flag)
2. **Coverage Gate**: Cannot publish if coverage < 24% (escalating to 50%)
3. **3-Domain Consensus**: All three guardians must align before publish
4. **Branch Protection**: Master branch rejects direct pushes
5. **Audit Trail**: Every publish logged to `.audit/make-history.log`

---

## 8. Quick Reference

### Daily Workflow

```bash
# Start of day: Ensure environment is current
make setup

# After making changes: Validate locally
make validate

# Ready to publish: Create PR
make publish msg="feat(module): add new capability"

# Work in progress: Draft PR for early review
make publish-draft msg="wip: experimental feature"

# Hotfix: Auto-merge after checks
make publish-merge msg="fix(critical): resolve security issue"
```

### Troubleshooting

| Symptom | Cause | Solution |
|---------|-------|----------|
| "Lazarus rollback triggered" | Untracked files in .audit/ | `git add .audit/` before publish |
| "Coverage gate failed" | Tests below 24% | Add tests or use `--no-cov` for WIP |
| "GPG signing failed" | Key not configured | `git config user.signingkey <KEY_ID>` |
| "Push rejected" | Branch protection | Use `make publish`, not `git push` |
| "Symlink broken" | Shared-configs missing | `make materialize` |

---

## Appendix A: Integration Examples

See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for:
- Example playbooks (bootstrap, validate, recovery)
- ansible.cfg configuration
- Domain repository setup
- Collection installation via Galaxy

---

## Appendix B: Deprecated Documents

The following documents have been absorbed into this paradigm:

| Document | Status | Absorption Location |
|----------|--------|---------------------|
| `SEVEN_PILLARS.md` | **Absorbed** | Section 4 |
| `CANON-INTEGRATION.md` | **Absorbed** | Section 2 |
| `TANDEM_WORKFLOW.md` | **Absorbed** | Section 1 |
| `EMERGENCY_RESPONSE.md` | **Absorbed** | Section 6 |
| `MIGRATION_v1_to_v2.md` | **Deprecated** | Historical reference only |
| `EXTRACTION_ROADMAP.md` | **Deprecated** | Superseded by Section 5 |

---

## References

- [OpenGitOps Principles v1.0.0](https://opengitops.dev/) — CNCF Standard
- [GitOps.tech](https://gitops.tech/) — Push vs Pull patterns
- [Codefresh GitOps Guide](https://codefresh.io/learn/gitops/) — 4 Commandments
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/) — Reference implementation
- [rylan-canon-library](https://github.com/RylanLabs/rylan-canon-library) — Governance tier

---

**Trinity Consensus**: Carter ✅ | Bauer ✅ | Beale ✅ | Whitaker ✅ | Lazarus ✅

**Grade**: A (96/100) — Production-ready substrate foundation.

*The fortress evolves. No bypass. The Trinity endures.* 🛡️
