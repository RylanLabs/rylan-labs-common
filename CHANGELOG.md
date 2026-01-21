# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2026-01-21

### Added

- **Sanitized Network Playbooks**: Ported production-ready playbooks from `rylan-labs-network-iac`.
  - `playbooks/example-vlan-bootstrap.yml`: Automated VLAN infrastructure setup.
  - `playbooks/example-firewall-rules.yml`: Production-grade firewall hardening rules.
- **Variable Namespace Alignment**: Unified `unifi_controller_*` variables with `rylanlabs-private-vault` (Option A).
- **Hardening Enhancements**: Added explicit `simulation_mode` support to `unifi_api` module and roles.
- **Galaxy Readiness**: Implemented `build_ignore` and tag sanitization for reliable publishing.

### Fixed

- **API Param Mismatch**: Added missing `site` and `simulation_mode` to `unifi_api.py` `argument_spec`.
- **Doc Collision**: Removed redundant `DOCUMENTATION` block to prevent `ansible-doc` failures and improve clarity.
- **Payload Optimization**: Reduced collection size from 38MB to 1.4MB by excluding build artifacts.

## [1.1.4] - 2026-01-06

### Added (1.1.4)

- **Role Documentation**: README.md files for all roles (Galaxy requirement)
  - `roles/infrastructure_verify/README.md`: Verification and audit role documentation
  - `roles/hardening_management/README.md`: Security hardening role documentation
  - `roles/identity_management/README.md`: Identity management role documentation
  - Each README includes: description, requirements, variables, examples, 3-Domain integration, license

### Documentation (1.1.4)

- Role READMEs include 3-Domain pattern alignment (Identity Domain/Verification Domain/Hardening Domain)
- Each role documented with requirements, variables, and example playbooks
- Security features and compliance constraints documented
- Production Standards v6 constraints documented (e.g., max 10 firewall rules)

### Compliance (1.1.4)

- **Galaxy Requirement**: Every role now has README.md file
- **Ansible Standards**: Role documentation follows Ansible Galaxy conventions
- **Seven Pillars**: Documentation pillar reinforced with comprehensive role guides
- **3-Domain Alignment**: Each role's 3-Domain role and ministry documented

## [1.1.3] - 2026-01-06

### Fixed (1.1.3)

- **Galaxy Role Naming**: Removed hyphens from role names per Galaxy validation requirements
  - Changed: `audit-verify` → `infrastructure_verify`
  - Changed: `hardening-harden` → `hardening_management`
  - Changed: `identity-identity` → `identity_management`
  - Pattern: Galaxy only accepts `[a-z0-9_]` in role names (no hyphens)

- **Module Documentation**: Added DOCUMENTATION block to unifi_api module
  - Enables `ansible-doc -t module rylanlab.common.unifi_api` support
  - Includes OPTIONS, EXAMPLES, RETURN sections per Ansible standards
  - Galaxy validation now passes for module documentation check

### Changed (1.1.3)

- **Playbook Role References**: Updated all playbook role references to use new underscores naming
- **README.md**: Updated all role name documentation to reflect new naming convention
- **3-Domain Alignment**: Role names now comply with Galaxy standards while maintaining Identity Domain/Verification
Domain/Hardening Domain pattern

### Compliance (1.1.3)

- **Ansible Galaxy Standards**: All role names and module documentation now compliant
- **Breaking Change**: Role names changed from hyphens to underscores (update playbooks accordingly)
- **No Bypass**: All validations enforced before Galaxy publication

## [1.1.2] - 2026-01-06

### Fixed (1.1.2)

- **Galaxy Tag Validation**: Removed hyphens from tags to comply with Ansible Galaxy format requirements
  - Changed: `ci-cd` → `cicd`
  - Changed: `seven-pillars` → `seven_pillars`
  - Changed: `github-template` → `github_template`
  - Changed: `shared-configs-integrated` → `shared_configs_integrated`
  - Pattern: Galaxy only accepts `[a-z0-9_]` in tags (no hyphens)

- **Galaxy Publish Workflow**: Tags now pass Galaxy validation checks
  - Enables successful collection publication to Ansible Galaxy
  - Resolves blocking issue preventing PR #3 merge

### Compliance (1.1.2)

- **Ansible Galaxy Standards**: All tags now compliant with Galaxy naming conventions
- **No Bypass**: Validation enforced before publish attempt

## [1.1.1] - 2026-01-06

### Added (1.1.1)

- **GitHub Template Repository**: Repository enabled as GitHub template in Settings
  - `templates/role-template/`: Skeleton Ansible role structure for new roles
  - `templates/playbook-template.yml`: 3-Domain-aligned playbook bootstrap template
  - README.md "Using as GitHub Template" section with `gh repo create` instructions
  - Galaxy.yml tagged with `template` and `github-template` for discoverability

- **Symlink CI Support**: Configuration for GitHub Actions symlink resolution
  - `.github/workflows/ci.yml` includes symlink validation job (if symlinks present)
  - Documentation for symlink-to-regular-file conversion for CI compatibility
  - Audit trail: symlink resolution strategy and path resolution verification

### Fixed (1.1.1)

- Symlink path resolution in GitHub Actions environment
  - Config files (.yamllint, pyproject.toml) now regular files for CI compatibility
  - Pre-commit hooks updated to reference root-level config files
  - Symlinks optional for consumers: recommend `install-to-repo.sh` post-clone for local development

### Documentation (1.1.1)

- Updated `docs/INTEGRATION_GUIDE.md` with "Symlink Architecture" section
- Template creation validated: Test repo created successfully
- Confirms template structure is complete and cloneable
- Downstream repos (iac, network-iac) can now use as bootstrap template

### Compliance (1.1.1)

- **Seven Pillars**: Idempotency, Audit Logging, Documentation
- **3-Domain Pattern**: Template includes Identity Domain, Verification Domain, Hardening Domain role references
- **Production Standards v6**: Template RTO <15min, junior-deployable bootstrap instructions

## [1.0.2] - 2025-12-30

### Added (1.0.2)

- **GitHub Actions CI/CD Pipeline** (3-Domain-aligned, Seven Pillars enforced):
  - `pr-validation.yml`: Pull request quality gate (ansible-lint, ruff, mypy, pytest, Seven Pillars validation)
  - `build-and-artifact.yml`: Collection build + smoke test + 30-day artifact retention
  - `galaxy-publish.yml`: Galaxy publish with version validation, manual approval gate, release notes automation
  - `security-scan.yml`: Weekly security scans (bandit, pip-audit, ansible-lint security profile, vault rotation checks)
- **Validation & Integration Scripts**:
  - `.github/scripts/validate-seven-pillars.sh`: Comprehensive compliance checker (idempotency, error handling, audit
logging, documentation, validation, reversibility, observability)
  - `.github/scripts/sync-vault-secrets.sh`: Vault-to-GitHub Secrets synchronization (SSH-based, audit-logged)
- **Audit Infrastructure**:
  - `.audit/` directory structure: ci-runs, builds, galaxy-publish, security-scans, pillars-validation, vault-syncs
  - JSON audit logs for all CI operations (RTO <15min, Production Standards v6 compliance)
- **Documentation**:
  - README.md: CI/CD workflow descriptions, quality badges, integration architecture diagram
  - Governance metadata: Guardian (Leo), Ministry (Verification Domain), Compliance (3-Domain/Seven Pillars)

### Changed (1.0.2)

- README.md: Enhanced with Core Principles section, directory tree, Mermaid tandem ecosystem architecture
- Package structure: Added `__init__.py` markers to plugins/ subdirectories for test import support

### Security (1.0.2)

- GitHub Secrets required: `GALAXY_API_KEY` (Galaxy publish), `VAULT_SSH_KEY` (vault sync)
- Production environment gate: Manual approval required for Galaxy publish (Production Standards v6 safeguard)
- No-bypass culture: All standards enforced via CI; no manual override allowed

## [1.0.1] - 2025-12-29

### Added (1.0.1)

- Example playbooks demonstrating 3-Domain workflows and UniFi integration (playbooks/):
  - `example-bootstrap.yml` (Identity Domain → Verification Domain → Hardening Domain full sequence)
  - `example-unifi-integration.yml` (dynamic inventory + UniFi API demo)
  - `example-validate-only.yml` (Verification Domain compliance audit — read-only)
  - `example-recovery.yml` (Emergency recovery with confirmation gate and rollback handlers)
- Documentation updates:
  - `README.md`: "Example Playbooks" section
  - `docs/INTEGRATION_GUIDE.md`: "Getting Started" quick-start and usage notes

## [1.0.0] - 2025-12-28

### Added (1.0.0)

- Initial production release of rylanlabs.common Ansible collection
- **Roles**:
  - `identity-identity`: Identity guardian (AD/RADIUS/LDAP)
  - `audit-verify`: Verification guardian (validation/audit)
  - `hardening-harden`: Hardening guardian (firewall/isolation)
- **Plugins**:
  - `unifi_api`: UniFi controller API access
  - `unifi_dynamic_inventory`: Dynamic inventory from UniFi
  - `rylan_utils`: Shared module utilities
- **Quality**:
  - Pre-commit hooks (yamllint, ansible-lint, ruff, mypy)
  - Unit tests (pytest)
  - Integration test framework
  - Validation scripts
- **Documentation**:
  - README.md (comprehensive usage guide)
  - INTEGRATION_GUIDE.md (tandem workflow)
  - SEVEN_PILLARS.md (compliance framework)
  - TANDEM_WORKFLOW.md (execution example)
  - EMERGENCY_RESPONSE.md (incident recovery)
- **Compliance**:
  - Seven Pillars: idempotency, error handling, functionality, audit logging, failure recovery, security hardening,
documentation
  - 3-Domain alignment: Identity Domain/Verification Domain/Hardening Domain principles
  - Grade A+ (95+/100)

### Fixed (1.0.0)

- N/A (initial release)

### Deprecated (1.0.0)

- N/A (initial release)

### Removed (1.0.0)

- N/A (initial release)

### Security (1.0.0)

- Firewall validation via hardening-harden role
- Network isolation enforcement
- Audit logging to structured trail and Loki
- No secrets, no data, no doctrine (code only)

---

## Future Roadmap

- **1.1.0**: Extraction of roles from rylan-labs-iac Phase B
- **1.2.0**: UniFi API enhancements (additional WLAN variants)
- **1.3.0**: Whitaker red-team integration
- **2.0.0**: Full multi-cloud support (AWS, Azure, GCP)
- **10.0.0**: 3-Domain ecosystem maturity (canon + common + inventory unified)
