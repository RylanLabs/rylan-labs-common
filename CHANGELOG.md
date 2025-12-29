# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
