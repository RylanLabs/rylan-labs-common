<!-- markdownlint-disable MD013 MD024 MD001 MD029 MD040 MD025 -->
# Ansible Role: rylanlab.common.hardening_management

**Component**: Security Hardening & Isolation
**Compliance**: Production-Grade (Seven Pillars)

## Description

Security hardening role for critical infrastructure. Configures firewall rules, SSH hardening, and VLAN isolation. Focuses on minimal attack surface and validated configuration state.

## Requirements

- Ansible >= 2.14
- Python >= 3.11
- Target systems: Ubuntu 22.04+, RHEL 9+
- Sudo/root access required for firewall/network configuration

## Role Variables

### Defaults (see `defaults/main.yml`)

```yaml
hardening_firewall_max_rules: 10
hardening_ssh_hardening: true
hardening_vlan_isolation: true
hardening_ids_enabled: false
hardening_audit_mode: false
hardening_emergency_port: 222
```

### Required Variables

```yaml
hardening_firewall_rules: []      # Max 10 rules per Production Standards
hardening_allowed_ssh_users: []   # List of users allowed SSH access
```

## Dependencies

None.

## Example Playbook

```yaml
---
- name: Apply Hardening Security Hardening
  hosts: firewalls
  roles:
    - role: rylanlab.common.hardening_management
      vars:
        hardening_firewall_rules:
          - port: 22
            proto: tcp
            source: 192.168.1.0/24
          - port: 443
            proto: tcp
            source: 0.0.0.0/0
        hardening_ssh_hardening: true
        hardening_allowed_ssh_users:
          - admin
          - deploy
```

## Security Features

- **Firewall**: nftables/iptables with ≤10 rules (Production Standards constraint)
- **SSH Hardening**: Key-only auth, rate limiting, fail2ban integration
- **VLAN Isolation**: VLAN 99 quarantine segment (if applicable)
- **IDS Integration**: Optional Suricata/Snort hooks for network monitoring
- **Emergency Port**: Failsafe SSH port for emergency recovery

## 3-Domain Integration

**Hardening's Role in 3-Domain Pattern**:

- **Identity** (Identity): SSH key validation and user authentication
- **Audit** (Auditor): Security compliance reports and audit trails
- **Hardening** (Bastille): Firewall and hardening enforcement

## Compliance Constraints

- **Max 10 Firewall Rules**: Production Standards requirement for hardware offload safety
- **No PII**: No sensitive data stored in role variables
- **Reversible**: All changes documented for rollback procedures
- **Idempotent**: Safe to run multiple times without side effects

## License

MIT

## Author

RylanLabs (@RylanLabs)
<https://github.com/RylanLabs/rylan-labs-common>
