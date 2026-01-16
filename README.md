<!-- markdownlint-disable MD013 MD024 MD001 MD029 MD040 MD025 -->
# Production Ansible Collection

> Production-Grade Infrastructure-as-Code — RylanLabs Common
> Version: v1.2.1
> Status: Release Candidate (v1.2.1) — see branch `release/v1.2.1-final`

---

## Purpose

`rylanlabs.common` is a production-grade Ansible collection for infrastructure automation.
It bundles roles for standardized tasks (Identity for authentication, Audit for verification,
Hardening for security), modules for custom operations (e.g., UniFi API), and plugins for extensions.
Designed for public distribution via Ansible Galaxy. It enables modular, idempotent deployments while following infrastructure-as-code best practices.
All code enforces safety-first validation and "junior-at-3-AM" deployability.

**Objectives**:

- Centralize reusable code to eliminate duplication across domain repos.
- Enforce infrastructure-as-code best practices in every role/module.
- Support high availability with built-in safety handlers.
- Facilitate modular workflows for bootstrap, validation, and hardening.

---

## Core Principles Applied

1. **Idempotency**: Roles use pre-checks for safe re-runs.
2. **Error Handling**: Fail loud with context; remediation in docs.
3. **Audit Logging**: Structured logs to `.audit/` for every execution.
4. **Documentation Clarity**: FQCN examples; junior-readable guides in `docs/`.
5. **Safety Constraints**: Built-in limits for firewall rules and VLANs to prevent overload.

**Execution Alignment**:

- **Identity**: `identity_management` role bootstraps auth services.
- **Audit**: `infrastructure_verify` enforces linting and state validation.
- **Hardening**: `hardening_management` applies firewall and isolation policies.

---

## Directory Structure

```bash
rylan-labs-common/
├── .audit/                     # Structured JSON audit logs
├── .github/                    # CI/CD workflows and GitHub Actions
├── docs/                       # Documentation files
│   ├── EMERGENCY_RESPONSE.md   # Incident recovery procedures
│   ├── INTEGRATION_GUIDE.md    # Tandem setup and ansible.cfg
│   ├── SEVEN_PILLARS.md        # Compliance framework
│   └── TANDEM_WORKFLOW.md      # Execution and dataflow
├── meta/                       # Collection metadata
│   └── runtime.yml             # Ansible reqs and dependencies
├── playbooks/                  # Example playbooks
│   ├── example-bootstrap.yml    # Complete sequence demo (Identity -> Audit -> Hardening)
│   ├── example-identity.yml     # Identity management role demonstration
│   ├── example-verify.yml       # Audit and verification role demonstration
│   ├── example-harden.yml       # Security hardening role demonstration
│   ├── example-vlan-bootstrap.yml # Network: VLAN infrastructure provisioning
│   └── example-firewall-rules.yml # Hardening: Production-grade firewall rules
├── plugins/                    # Custom extensions
│   ├── modules/                # Python modules
│   │   └── unifi_api.py        # UniFi API queries
│   ├── inventory/              # Inventory plugins
│   │   └── unifi_dynamic_inventory.py  # Dynamic UniFi inventory
│   └── module_utils/           # Shared utils
│       └── rylan_utils.py      # Audit/rollback helpers
├── roles/                      # Reusable roles
│   ├── infrastructure_verify/  # Verification tasks
│   │   ├── defaults/           # main.yml with vars
│   │   ├── tasks/              # main.yml
│   │   └── handlers/           # Service restarts
│   ├── hardening_management/   # Hardening tasks
│   │   ├── defaults/           # main.yml
│   │   ├── tasks/              # main.yml
│   │   └── handlers/           # Rollbacks
│   └── identity_management/    # Identity tasks
│       ├── defaults/           # main.yml
│       ├── tasks/              # main.yml
│       └── handlers/           # Audits
├── scripts/                    # Validation utilities
├── tests/                      # Unit/integration tests (skeleton)
├── .gitignore                  # Ignore builds/tests
├── .pre-commit-config.yaml     # Hooks (ansible-lint, etc.)
├── .yamllint                   # YAML rules
├── CHANGELOG.md                # Version history
├── galaxy.yml                  # Collection metadata
├── LICENSE                     # MIT
├── Makefile                    # Build/validate tasks
├── pyproject.toml              # Python linting
├── rylanlab-common-1.2.1.tar.gz  # Built archive (v1.2.1)
└── README.md                   # This file
```bash

---

## Features

### Core Roles

#### identity_management

- **Purpose**: Bootstrap centralized identity services (RADIUS, LDAP).
- **Defaults** (`defaults/main.yml`):

  ```yaml
  identity_management_enabled: false
  identity_providers: []
  identity_management_audit_enabled: false
  ```

- **Tasks**: Install packages, configure authentication, audit events.

### infrastructure_verify

- **Purpose**: Validate configuration, run linting, and audit logging.
- **Defaults**:

  ```yaml
  infrastructure_verify_enabled: false
  infrastructure_verify_audit_enabled: true
  infrastructure_loki_endpoint: ""
  infrastructure_log_retention_days: 90
  ```

- **Tasks**: Run validation checks and log auditing.

#### hardening_management

- **Purpose**: Firewall rules, VLAN isolation, and security enforcement.
- **Defaults**:

  ```yaml
  hardening_management_enabled: false
  hardening_management_firewall_rules: []
  hardening_management_vlan_configs: []
  ```

- **Tasks**: Configure security policies and enforce infrastructure isolation.

### Custom Plugins & Modules

#### unifi_api.py (modules/)

- Queries UniFi for topology/WLAN/clients.

#### unifi_dynamic_inventory.py (inventory/)

- Generates inventory from UniFi controller.

#### rylan_utils.py (module_utils/)

- Shared: Logging, validation, rollback.

---

## Installation

Via Galaxy:

```bash
ansible-galaxy install rylanlabs.common
```bash

From Source:

```bash
git clone https://github.com/RylanLabs/rylan-labs-common.git
cd rylan-labs-common
ansible-galaxy collection install . --force
# Or install the packaged tarball directly (from repo root):
# ansible-galaxy collection install rylanlab-common-1.2.1.tar.gz --force
```bash

---

## Standards & Validation

This collection follows high-standard development practices for infrastructure automation.

**Key Features**:

- Linting configs synchronized with production standards.
- Pre-commit hooks enforce modular patterns and YAML best practices.
- Validators run locally to ensure CI parity.
- Architectural disciplines documented in `docs/disciplines/`.

**For Developers**:

```bash
# Install pre-commit hooks (one-time)
pre-commit install

# Run validators manually
pre-commit run --all-files
```bash

**For Maintainers**: See `docs/` for architecture and validation manifests.

---

## Implementation & Quality

This collection implements the **Seven Pillars** as follows:

- **Idempotency**: All roles support `--check` mode; second runs report zero changes.
- **Error Handling**: Uses `block/rescue` for critical operations with automated rollback handlers.
- **Audit Logging**: Structured JSON trails generated in `.audit/` for all deployments.
- **Security**: Firewalls and VLAN isolation validated via `validate-security-posture.sh`.

---

## Emergency Procedures

**Target RTO**: < 15 minutes for all incidents.

| Scenario | Recovery Strategy | Target |
| --- | --- | --- |
| Collection Missing | `ansible-galaxy collection install . --force` | 2 min |
| Task Failure | Identify tags via `-vvv` and re-run specific tags | 5 min |
| Service Down | Check reachability; fallback to static credentials | 8 min |
| Full Reset | Run `scripts/example-recovery.yml` with domain tags | 15 min |

For detailed runbooks, see [docs/EMERGENCY_RESPONSE.md](docs/EMERGENCY_RESPONSE.md) (Canonical Link).

---

## Usage

### Example Playbook

```yaml
- name: Bootstrap Infrastructure
  hosts: all
  roles:
    - rylanlabs.common.identity_management
    - rylanlabs.common.infrastructure_verify
    - rylanlabs.common.hardening_management
```bash

### Dynamic Inventory

Configure `unifi_inventory.yml`; use `-i unifi_inventory.yml`.

### Playbooks (playbooks/)

- `example-bootstrap.yml`: Complete sequence.
- `example-identity.yml`: Identity management.
- `example-verify.yml`: Audit and verification.
- `example-harden.yml`: Security hardening.

---

## Tandem Integration

With `rylan-canon-library`: Bootstrap hooks/validators.
With `rylan-inventory`: Dynamic plugin pulls manifests.

**Architecture Flowchart**:

```mermaid
graph TD
    A[rylan-canon-library<br/>Doctrine/Templates] -->|Bootstrap Hooks| B[rylan-labs-common<br/>Roles/Modules/Plugins]
    B -->|ansible-galaxy install| C[Domain Repos<br/>e.g., rylan-labs-iac]
    D[rylan-inventory<br/>Manifests/Data] -->|Dynamic Plugin| B
    B -->|Playbooks/Roles| E[Deployment<br/>3-Domain Sequence]
    subgraph "Tandem Ecosystem"
        A --> B --> C
        D --> B
    end
```bash

---

## Quality Assurance

Local: `make ci-local` (`ansible-lint`, `ruff`, `mypy`, etc.).
Pre-commit: `make pre-commit-install`.

---

## Seven Pillars Compliance

- Idempotency: Pre-checks in roles.
- Error Handling: `failed_when` clauses.
- Audit Logging: Loki integration.
- Documentation: Extensive `docs/`.
- Validation: Makefile targets.
- Reversibility: Rollback handlers.
- Observability: `nmap`/Loki.

---

## Emergency Response

| Scenario         | Domain   | Action                              | RTO   |
|------------------|----------|-------------------------------------|-------|
| Install Fail     | Audit    | `--force install`                   | 2min  |
| Role Drift       | Identity | Validate-only playbook              | 5min  |
| Hardening Breach | Hardening| Recovery playbook `--tags hardening`| 10min |
| Full Reset       | Recovery | `eternal-resurrect.sh --common`     | 15min |

---

## Documentation

- INTEGRATION_GUIDE.md: Setup/ansible.cfg.
- SEVEN_PILLARS.md: Framework.
- TANDEM_WORKFLOW.md: Dataflow.
- EMERGENCY_RESPONSE.md: Procedures.

---

## Versioning

SemVer: MAJOR.MINOR.PATCH. CHANGELOG.md tracks.

---

## License

MIT. See LICENSE.

---

## Authors

RylanLabs Team <team@rylanlabs.com>

---

## Support & Contribution

Issues: <https://github.com/RylanLabs/rylan-labs-common/issues>.
PRs follow Seven Pillars.

---

**Last Updated**: 2026-01-15
**Status**: Release Candidate (v1.2.1) — PR branch `release/v1.2.1-final`
**Infrastructure-as-Code requires discipline. All changes must be validated.**
