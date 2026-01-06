# role-template

**Bootstrap template for RylanLabs Ansible roles**

## Overview

This is a skeleton Ansible role template for creating new roles in the
rylan-labs-common collection. Use this as a starting point for role development.

## Requirements

- Ansible 2.15+
- Python 3.11+
- Seven Pillars compliance (Idempotency, Error Handling, Functionality, Audit
  Logging, Failure Recovery, Security Hardening, Documentation)

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `role_name` | `role-template` | Role name |
| `role_version` | `1.0.0` | Role semantic version |
| `enabled` | `true` | Enable/disable role |
| `log_level` | `info` | Log verbosity level |
| `audit_enabled` | `true` | Enable audit logging |

## Dependencies

None (customize as needed)

## Example Playbook

```yaml
---
- name: Deploy role-template
  hosts: localhost
  gather_facts: true
  roles:
    - role: rylanlab.common.role_template
      vars:
        role_name: "custom-role"
        log_level: debug
```

## Trinity Alignment

- **Carter (Identity)**: Role metadata, configuration identity
- **Bauer (Verification)**: Task validation, assertion checks
- **Beale (Hardening)**: Handler resilience, error recovery

## Compliance

- ✓ Idempotency: All tasks are repeatable
- ✓ Error Handling: Assertions validate preconditions
- ✓ Audit Logging: Debug statements document execution
- ✓ Failure Recovery: Handlers manage error states
- ✓ Security: No hardcoded secrets (use vault)
- ✓ Documentation: Inline comments + README

## License

MIT - See LICENSE in root repository
