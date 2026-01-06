# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.2] - 2026-01-06

### Fixed

- **Galaxy Tag Validation**: Removed hyphens from tags to comply with Ansible Galaxy format requirements
  - Changed: `ci-cd` → `cicd`
  - Changed: `seven-pillars` → `seven_pillars`
  - Changed: `github-template` → `github_template`
  - Changed: `shared-configs-integrated` → `shared_configs_integrated`
  - Pattern: Galaxy only accepts `[a-z0-9_]` in tags (no hyphens)

- **Galaxy Publish Workflow**: Tags now pass Galaxy validation checks
  - Enables successful collection publication to Ansible Galaxy
  - Resolves blocking issue preventing PR #3 merge

### Compliance

- **Ansible Galaxy Standards**: All tags now compliant with Galaxy naming conventions
- **No Bypass**: Validation enforced before publish attempt

## [1.1.1] - 2026-01-06

### Added

- **GitHub Template Repository**: Repository enabled as GitHub template in Settings
  - `templates/role-template/`: Skeleton Ansible role structure for new roles
  - `templates/playbook-template.yml`: Trinity-aligned playbook bootstrap template
  - README.md "Using as GitHub Template" section with `gh repo create` instructions
  - Galaxy.yml tagged with `template` and `github-template` for discoverability

- **Symlink CI Support**: Configuration for GitHub Actions symlink resolution
  - `.github/workflows/ci.yml` includes symlink validation job (if symlinks present)
  - Documentation for symlink-to-regular-file conversion for CI compatibility
  - Audit trail: symlink resolution strategy and path resolution verification

### Fixed

- Symlink path resolution in GitHub Actions environment
  - Config files (.yamllint, pyproject.toml) now regular files for CI compatibility
  - Pre-commit hooks updated to reference root-level config files
  - Symlinks optional for consumers: recommend `install-to-repo.sh` post-clone for local development

### Documentation

- Updated `docs/INTEGRATION_GUIDE.md` with "Symlink Architecture" section
- Template creation validated: Test repo created successfully
- Confirms template structure is complete and cloneable
- Downstream repos (iac, network-iac) can now use as bootstrap template

### Compliance

- **Seven Pillars**: Idempotency, Audit Logging, Documentation
- **Trinity Pattern**: Template includes Carter, Bauer, Beale role references
- **Hellodeolu v6**: Template RTO <15min, junior-deployable bootstrap instructions

## [1.0.2] - 2025-12-30

### Added

- **GitHub Actions CI/CD Pipeline** (Trinity-aligned, Seven Pillars enforced):
  - `pr-validation.yml`: Pull request quality gate (ansible-lint, ruff, mypy, pytest, Seven Pillars validation)
  - `build-and-artifact.yml`: Collection build + smoke test + 30-day artifact retention
  - `galaxy-publish.yml`: Galaxy publish with version validation, manual approval gate, release notes automation
  - `security-scan.yml`: Weekly security scans (bandit, pip-audit, ansible-lint security profile, vault rotation checks)
- **Validation & Integration Scripts**:
  - `.github/scripts/validate-seven-pillars.sh`: Comprehensive compliance checker (idempotency, error handling, audit logging, documentation, validation, reversibility, observability)
  - `.github/scripts/sync-vault-secrets.sh`: Vault-to-GitHub Secrets synchronization (SSH-based, audit-logged)
- **Audit Infrastructure**:
  - `.audit/` directory structure: ci-runs, builds, galaxy-publish, security-scans, pillars-validation, vault-syncs
  - JSON audit logs for all CI operations (RTO <15min, Hellodeolu v6 compliance)
- **Documentation**:
  - README.md: CI/CD workflow descriptions, quality badges, integration architecture diagram
  - Governance metadata: Guardian (Leo), Ministry (Bauer), Compliance (Trinity/Seven Pillars)

### Changed

- README.md: Enhanced with Core Principles section, directory tree, Mermaid tandem ecosystem architecture
- Package structure: Added `__init__.py` markers to plugins/ subdirectories for test import support

### Security

- GitHub Secrets required: `GALAXY_API_KEY` (Galaxy publish), `VAULT_SSH_KEY` (vault sync)
- Production environment gate: Manual approval required for Galaxy publish (Hellodeolu v6 safeguard)
- No-bypass culture: All standards enforced via CI; no manual override allowed

## [1.0.1] - 2025-12-29

### Added

- Example playbooks demonstrating Trinity workflows and UniFi integration (playbooks/):
  - `example-bootstrap.yml` (Carter → Bauer → Beale full sequence)
  - `example-unifi-integration.yml` (dynamic inventory + UniFi API demo)
  - `example-validate-only.yml` (Bauer compliance audit — read-only)
  - `example-recovery.yml` (Emergency recovery with confirmation gate and rollback handlers)
- Documentation updates:
  - `README.md`: "Example Playbooks" section
  - `docs/INTEGRATION_GUIDE.md`: "Getting Started" quick-start and usage notes

## [1.0.0] - 2025-12-28

### Added

- Initial production release of rylanlabs.common Ansible collection
- **Roles**:
  - `carter-identity`: Identity guardian (AD/RADIUS/LDAP)
  - `bauer-verify`: Verification guardian (validation/audit)
  - `beale-harden`: Hardening guardian (firewall/isolation)
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
  - Seven Pillars: idempotency, error handling, functionality, audit logging, failure recovery, security hardening, documentation
  - Trinity alignment: Carter/Bauer/Beale principles
  - Grade A+ (95+/100)

### Fixed

- N/A (initial release)

### Deprecated

- N/A (initial release)

### Removed

- N/A (initial release)

### Security

- Firewall validation via beale-harden role
- Network isolation enforcement
- Audit logging to structured trail and Loki
- No secrets, no data, no doctrine (code only)

---

## Future Roadmap

- **1.1.0**: Extraction of roles from rylan-labs-iac Phase B
- **1.2.0**: UniFi API enhancements (additional WLAN variants)
- **1.3.0**: Whitaker red-team integration
- **2.0.0**: Full multi-cloud support (AWS, Azure, GCP)
- **10.0.0**: Trinity ecosystem maturity (canon + common + inventory unified)
