# Ansible Role: bauer_verify

**Guardian**: Bauer (Auditor)  
**Ministry**: Verification & Audit  
**Compliance**: T3-ETERNAL v∞.5.3, Seven Pillars, Hellodeolu v6

## Description

Verification and audit role for RylanLabs infrastructure. Validates system state, checks compliance, and generates audit logs. Part of the Trinity pattern for infrastructure automation.

## Requirements

- Ansible >= 2.14
- Python >= 3.11
- Target systems: Debian/Ubuntu, RHEL/CentOS
- Sudo/root access required for system audits

## Role Variables

### Defaults (see `defaults/main.yml`)

```yaml
bauer_audit_log_path: /var/log/bauer-audit.log
bauer_validation_strict: true
bauer_report_format: json
bauer_trinity_mode: true
bauer_audit_enabled: true
```

### Required Variables

```yaml
bauer_target_systems: []  # List of systems to audit
```

## Dependencies

None.

## Example Playbook

```yaml
---
- name: Run Bauer Verification Audit
  hosts: all
  roles:
    - role: rylanlab.common.bauer_verify
      vars:
        bauer_target_systems:
          - web01
          - db01
        bauer_validation_strict: true
        bauer_audit_enabled: true
```

## Trinity Integration

**Bauer's Role in Trinity Pattern**:
- **Carter** (Identity): Validates system identity and SSH keys
- **Bauer** (Auditor): Generates compliance reports and audit logs
- **Beale** (Bastille): Checks firewall and security hardening compliance

## Audit Logging

All verification results logged to `{{ bauer_audit_log_path }}` in JSON format. Logs include:
- System state snapshots
- Compliance validation results
- Timestamp and audit metadata

## Features

- System state validation
- Compliance checking against Seven Pillars framework
- JSON audit log generation
- Loki integration support (optional)
- Trinity pattern alignment

## License

MIT

## Author

RylanLabs (@RylanLabs)  
https://github.com/RylanLabs/rylan-labs-common
