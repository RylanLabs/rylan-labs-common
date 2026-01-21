# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.2] - 2026-01-21

### Added

- **Trinity 7-Task Pattern**: Modernized example playbooks to follow the high-consciousness Trinity workflow
  (Gather, Process, Apply, Verify, Compliance, Report, Finalize).
- **Beale Guardian Deployment**: Re-engineered `example-firewall-rules.yml` to implement a proper "Default-Deny"
  posture while maintaining UniFi ASIC hardware offload performance (Hellodeolu v6: ≤10 rules).
- **Whitaker Breach Simulation**: Added `scripts/simulate-breach.sh` for post-deployment verification of
  firewall effectiveness via mock probe payloads.
- **Hardware-Aware Constraints**: Added pre-flight logic to enforce device architectural limits
  (max 5 VLANs, max 10 firewall rules) to ensure production stability.
- **Audit Directory Automation**: Ensuring `.audit/` structured logging directory is automatically created
  during playbook pre-flight.
- **Educational Catalog**: Added `playbooks/README.md` to guide community users through production-grade patterns.

### Fixed

- **Playbook Authentication**: Standardized all example playbooks to use `unifi_api_key` and environment
  variable lookups.
- **Linting & Code Quality**: Resolved all `yamllint` trailing-space issues and enforced 120-char line limits
  in documentation.
- **Variable Namespace**: Final alignment of `unifi_*` vars across all examples for 100% vault compatibility.

## [1.2.1] - 2026-01-21

### Added (1.2.1)

- **Sanitized Network Playbooks**: Ported production-ready playbooks from `rylan-labs-network-iac`.
  - `playbooks/example-vlan-bootstrap.yml`: Automated VLAN infrastructure setup.
  - `playbooks/example-firewall-rules.yml`: Production-grade firewall hardening rules.
- **Variable Namespace Alignment**: Unified `unifi_controller_*` variables with `rylanlabs-private-vault` (Option A).
- **Hardening Enhancements**: Added explicit `simulation_mode` support to `unifi_api` module and roles.
- **Galaxy Readiness**: Implemented `build_ignore` and tag sanitization for reliable publishing.

### Fixed (1.2.1)

- **API Param Mismatch**: Added missing `site` and `simulation_mode` to `unifi_api.py` `argument_spec`.
- **Doc Collision**: Removed redundant `DOCUMENTATION` block to prevent `ansible-doc` failures.
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
