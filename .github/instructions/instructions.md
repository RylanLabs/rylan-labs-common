---
applyTo: '**'
---
# RylanLabs Instruction Set

> Canonical instruction set — RylanLabs standard  
> Organization: RylanLabs  
> Version: 1.0.0  
> Date: 04/02/2026

---

## Purpose

Single source of truth (SSOT) for all RylanLabs repositories and the organizational mesh.  
Defines non-negotiable standards for code quality, security, resilience, automation, and culture, homogenized to Maturity Level 5 (Autonomous) principles.

**Objectives**:

- Production-grade code and infrastructure everywhere (GitOps reconciled)
- Junior-at-3-AM deployable with password-less, self-remediating workflows
- Zero drift, zero bypass—hard gates enforced
- Understanding over blind compliance—IRL-First education
- Sustainable discipline through dynamic mesh and continuous compliance

**Alignment with OpenGitOps/CNCF Principles** (Cross-ref: [opengitops.dev](https://opengitops.dev/)):  
Declarative state in Git as SSOT; versioned/immutable history; pull-based reconciliation via cascade; continuous auditing via Whitaker/Sentinel.

---

## Core Principles — Seven Pillars (Updated for Maturity Level 5)

1. **Idempotency**  
   Safe to run multiple times—identical outcome (e.g., cascade re-runs yield no changes). Cross-ref: [Red Hat GitOps](https://www.redhat.com/en/topics/devops/what-is-gitops) for reconciled states.

2. **Error Handling**  
   Fail fast, fail loud, provide context (e.g., Whitaker detects drifts, blocks with JSON reports).

3. **Audit Logging**  
   Every action traceable—timestamped, structured JSON in .audit/ (e.g., org-audit matrices). Cross-ref: [NIST SP 800-57](https://csrc.nist.gov/pubs/sp/800/57/pt/1/final) for audit in key mgmt.

4. **Documentation Clarity**  
   Junior at 3 AM can understand and execute (e.g., MESH-MAN.md as auto-generated SSOT for Makefile targets).

5. **Validation**  
   Verify inputs, preconditions, postconditions (e.g., pre-merge gates in compliance-gate.yml block YELLOW).

6. **Reversibility**  
   Rollback path always exists (e.g., Lazarus RTO <15min, git submodule deinit for common.mk).

7. **Observability**  
   Visibility into state and progress (e.g., Loki/ELK-ready JSON from generate-compliance-report.sh). Cross-ref: [Datadog DevOps Pillars](https://www.datadoghq.com/blog/engineering/devops-pillars-observability/) for metrics.

**Hellodeolu v7 Alignment** (Updated from v6):  
All pillars mandatory with asymmetric security (SOPS/GPG) and dynamic mesh reconciliation. No exceptions—enforced by hard gates.

---

## Development Standards

### Bash Canon (Homogenized for Mesh)

```bash
#!/usr/bin/env bash
# Script: <kebab-case-name>.sh
# Purpose: <one-line purpose>
# Agent: <Carter|Bauer|Beale|Whitaker|Lazarus>
# Author: RylanLabs canonical
# Date: YYYY-MM-DD
set -euo pipefail
IFS=$'\n\t'
# Whitaker Gate: Exit on unsigned or drifted state
whitaker-scan.sh || exit 1
# Sentinel Gate: Block on expiry <14 days
sentinel-expiry.sh || exit 1
Mandatory (Cross-ref: Mechanical Rock Bash Guide for set -euo pipefail; Medium Bash Secrets for fail-loud):

set -euo pipefail
Trap ERR + EXIT cleanup
ShellCheck clean
kebab-case filenames
snake_case functions
UPPER_SNAKE_CASE constants
Integrate Whitaker/Sentinel for gates
SOPS/GPG for secrets handling

Python Canon (Homogenized for Maturity)

mypy --strict (type checking)
ruff check --select ALL (linting)
ruff format (formatting)
bandit -r . -ll (security scans)
pytest --cov-fail-under=80 (testing/coverage)
pyproject.toml only (dependencies)

Mandatory (Cross-ref: RealPython Code Quality for ruff/mypy; Medium Modern Python for uv/ruff stack; GeeksforGeeks Python in DevOps for pytest/bandit):

uv for dependency management
Integrate with Whitaker for pre-commit scans


Operational Standards
Junior-at-3-AM Deployable (Password-less, Self-Remediating):

One-command from clean system (e.g., make setup-maturity)
Clear errors + remediation (e.g., auto-PR on YELLOW drift)
Pre/post validation (e.g., Whitaker/Sentinel gates)
Rollback built-in (e.g., Lazarus <15min RTO)

Security (Asymmetric/Hybrid):

No cleartext secrets—SOPS/GPG enforced
Least privilege—topic-driven routing
SSH/GPG key-only
chmod 600 secrets; gitleaks pre-flight

Version Control (Mesh-Aligned):

Semantic versioning with mesh-vX.Y
Branch protection on main (require signed commits)
Required review + compliance-gate.yml
Canonical commit format (conventional commits)

Commit Format:
text<type>(<scope>): <subject>

<body: what + why + Whitaker proof>

<footer: BREAKING CHANGE or closes #issue>
Types: feat, fix, docs, refactor, test, chore, security

Cultural Canon
No-Bypass Culture (Zero Exceptions)

No --no-verify, [ci skip], manual overrides—hard gates block
Bypass attempt → loud failure + discussion/PR required
Right way = only way—enforced by compliance-gate.yml/auto-PR
Cross-ref: Enterprisers Project DevSecOps Culture for "security as culture"; SecurityJourney DevOps Fails for no-exceptions mindset.

IRL-First Approach (Understanding Over Enforcement)

Learn principles manually (e.g., manual cascade before automation)
Practice with feedback (e.g., dry-run drills)
Validate understanding (e.g., Whitaker simulations)
Introduce automation (e.g., event-driven Actions)
Maintain human oversight (e.g., approval gates)

Philosophy: Discipline through understanding, not enforcement—fostered by self-auditing mesh and junior-friendly docs.

Trinity Alignment (Expanded with Whitaker/Lazarus)
Identity (Carter)
Bootstrap identity (Samba AD/DC, RADIUS, 802.1X, GPG/SOPS keys).
Everything starts with who you are—persistent warmth for password-less.
Verification (Bauer)
Verify everything (SSH hardening, GitHub keys, zero lint debt, Sentinel expiry).
Nothing passes unverified—drift detection in validate.
Hardening (Beale)
Harden the host, detect the breach (Bastille automation, Snort/Suricata, gitleaks).
Fortress walls + early warning—hard gates enforced.
Adversarial (Whitaker)
Simulate threats (spoof scans, tamper drills).
Offensive validation tests all—integrated in gates.
Recovery (Lazarus)
Ensure reversibility (<15min RTO via revocation/rollback).
Fortress endures—built-in for all ops.
Execution Order:

Carter → Identity first
Bauer → Verify intent
Beale → Harden + detect
Whitaker → Adversarial test
Lazarus → Recover if failed

Cross-ref: Sysdig Secure DevOps Culture for integrated security pillars.

Repository Structure (Mandatory for Multi-Repo Mesh)
textrepo/
├── .rylan/              # Submodule for common.mk (DRY abstraction)
├── .github/
│   ├── workflows/       # Actions for governance/gate (e.g., repo-governance.yml)
│   └── instructions/    # Instruction sets for agents/automation
├── docs/                # Documentation (e.g., MESH-MAN.md, REPOS.md)
├── scripts/             # Operational scripts (e.g., org-audit.sh, mesh-remediate.sh)
├── src/                 # Source code
├── tests/               # Test suite
├── .audit/              # Structured JSON logs/matrices
├── .gitleaks.toml       # Leak detection config
├── .pre-commit-config.yaml  # Hooks for lint/format
├── Makefile             # Meta-GitOps reconciler (include .rylan/common.mk)
├── REPOS.md             # Org governance SSOT
└── MESH-MAN.md          # Auto-generated man page
Cross-ref: Thoughtworks Multi-Repo for boundaries; Microsoft Azure Repo Best Practices for multi-repo tiers; GeeksforGeeks GitHub Org for .github/docs/scripts structure.

Validation Gates (Pre-Merge in CI/CD)

All linters PASS (ruff, shellcheck)
Tests PASS + coverage (pytest --cov-fail-under=80)
Security scans clean (bandit, gitleaks)
Documentation updated (MESH-MAN.md auto-gen)
Seven Pillars demonstrated (e.g., idempotency in cascade)
No bypass attempts (compliance-gate.yml blocks YELLOW)

Cross-ref: GeeksforGeeks GitHub Actions Test Before Merge for PR triggers/gates; GitHub Blog Governance Actions for status checks/pre-merge validation.