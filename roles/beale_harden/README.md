# Ansible Role: beale_harden

**Guardian**: Beale (Bastille)  
**Ministry**: Security Hardening  
**Compliance**: T3-ETERNAL v∞.5.3, Seven Pillars, Hellodeolu v6

## Description

Security hardening role implementing Beale Doctrine. Configures firewalls (≤10 rules per Hellodeolu v6), SSH hardening, VLAN isolation, and optional IDS integration. Part of the Trinity pattern for infrastructure automation.

## Requirements

- Ansible >= 2.14
- Python >= 3.11
- Target systems: Debian/Ubuntu (nftables/iptables), RHEL/CentOS (firewalld)
- Sudo/root access required
- Network connectivity to manage interfaces

## Role Variables

### Defaults (see `defaults/main.yml`)

```yaml
beale_firewall_max_rules: 10
beale_ssh_hardening: true
beale_vlan_isolation: true
beale_ids_enabled: false
beale_audit_mode: false
beale_emergency_port: 222
```

### Required Variables

```yaml
beale_firewall_rules: []      # Max 10 rules per Hellodeolu v6
beale_allowed_ssh_users: []   # List of users allowed SSH access
```

## Dependencies

None.

## Example Playbook

```yaml
---
- name: Apply Beale Security Hardening
  hosts: firewalls
  roles:
    - role: rylanlab.common.beale_harden
      vars:
        beale_firewall_rules:
          - port: 22
            proto: tcp
            source: 192.168.1.0/24
          - port: 443
            proto: tcp
            source: 0.0.0.0/0
        beale_ssh_hardening: true
        beale_allowed_ssh_users:
          - admin
          - deploy
```

## Security Features

- **Firewall**: nftables/iptables with ≤10 rules (Hellodeolu v6 constraint)
- **SSH Hardening**: Key-only auth, rate limiting, fail2ban integration
- **VLAN Isolation**: VLAN 99 quarantine segment (if applicable)
- **IDS Integration**: Optional Suricata/Snort hooks for network monitoring
- **Emergency Port**: Failsafe SSH port for emergency recovery

## Trinity Integration

**Beale's Role in Trinity Pattern**:
- **Carter** (Identity): SSH key validation and user authentication
- **Bauer** (Auditor): Security compliance reports and audit trails
- **Beale** (Bastille): Firewall and hardening enforcement

## Compliance Constraints

- **Max 10 Firewall Rules**: Hellodeolu v6 requirement for hardware offload safety
- **No PII**: No sensitive data stored in role variables
- **Reversible**: All changes documented for rollback procedures
- **Idempotent**: Safe to run multiple times without side effects

## License

MIT

## Author

RylanLabs (@RylanLabs)  
https://github.com/RylanLabs/rylan-labs-common
