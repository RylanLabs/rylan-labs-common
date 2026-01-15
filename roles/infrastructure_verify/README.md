<!-- markdownlint-disable MD013 MD024 MD001 MD029 MD040 MD025 -->
# Ansible Role: rylanlab.common.infrastructure_verify

**Component**: Infrastructure Verification & Audit
**Compliance**: Production-Grade (Seven Pillars)

## Description

Verification and audit role for infrastructure. Validates configuration state, checks compliance with security baselines, and generates structured audit logs.

## Requirements

- Ansible >= 2.14
- Python >= 3.11
- Target systems: Ubuntu 22.04+, RHEL 9+

## Role Variables

### Defaults (see `defaults/main.yml`)

```yaml
infrastructure_audit_log_path: /var/log/audit-audit.log
infrastructure_validation_strict: true
infrastructure_report_format: json
infrastructure_three_domain_mode: true
infrastructure_verify_audit_enabled: true
```

### Required Variables

```yaml
infrastructure_target_systems: []  # List of systems to audit
```

## Dependencies

None.

## Example Playbook

```yaml
---
- name: Run Audit Verification Audit
  hosts: all
  roles:
    - role: rylanlab.common.infrastructure_verify
      vars:
        infrastructure_target_systems:
          - web01
          - db01
        infrastructure_validation_strict: true
        infrastructure_verify_audit_enabled: true
```

## 3-Domain Integration

**Audit's Role in 3-Domain Pattern**:

- **Identity** (Identity): Validates system identity and SSH keys
- **Audit** (Auditor): Generates compliance reports and audit logs
- **Hardening** (Bastille): Checks firewall and security hardening compliance

## Audit Logging

All verification results logged to `{{ infrastructure_audit_log_path }}` in JSON format. Logs include:

- System state snapshots
- Compliance validation results
- Timestamp and audit metadata

## Features

- System state validation
- Compliance checking against Seven Pillars framework
- JSON audit log generation
- Loki integration support (optional)
- 3-Domain pattern alignment

## License

MIT

## Author

RylanLabs (@RylanLabs)
<https://github.com/RylanLabs/rylan-labs-common>
