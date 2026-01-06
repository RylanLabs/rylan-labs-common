# Ansible Role: carter_identity

**Guardian**: Carter (Guardian)  
**Ministry**: Identity & Standards Enforcement  
**Compliance**: T3-ETERNAL v∞.5.3, Seven Pillars, Hellodeolu v6

## Description

Identity management and standards enforcement role. Manages SSH keys, user accounts, naming conventions, and system identity validation. Part of the Trinity pattern for infrastructure automation.

## Requirements

- Ansible >= 2.14
- Python >= 3.11
- Target systems: Debian/Ubuntu, RHEL/CentOS
- Sudo/root access required for user management

## Role Variables

### Defaults (see `defaults/main.yml`)

```yaml
carter_ssh_key_path: ~/.ssh/authorized_keys
carter_enforce_naming: true
carter_user_management: true
carter_identity_validation: true
carter_audit_enabled: true
```

### Required Variables

```yaml
carter_authorized_keys: []  # List of SSH public keys to deploy
carter_managed_users: []    # List of user account definitions
```

## Dependencies

None.

## Example Playbook

```yaml
---
- name: Deploy Carter Identity Management
  hosts: all
  roles:
    - role: rylanlab.common.carter_identity
      vars:
        carter_authorized_keys:
          - ssh-ed25519 AAAAC3... admin@rylan
          - ssh-ed25519 AAAAC3... deploy@rylan
        carter_managed_users:
          - name: admin
            state: present
            groups: sudo
          - name: deploy
            state: present
            groups: docker
```

## Identity Features

- **SSH Key Management**: Authorized keys deployment and rotation
- **User Account Management**: Creation, modification, state management
- **Naming Enforcement**: Python/Bash file naming standards validation
- **System Identity**: Hostname, domain, and certificate validation
- **Audit Logging**: All identity changes logged for compliance

## Trinity Integration

**Carter's Role in Trinity Pattern**:
- **Carter** (Identity): Primary guardian for system identity enforcement
- **Bauer** (Auditor): Logs identity changes for audit trail
- **Beale** (Bastille): Validates SSH hardening and security compliance

## Standards Enforcement

- **SSH Key Types**: Ed25519 preferred, RSA 4096+ acceptable
- **User Naming**: `[a-z_]+` pattern enforced
- **Hostname Convention**: Lowercase, no special characters
- **No Default Passwords**: Key-only authentication enforced

## Security Features

- SSH public key deployment without exposing private keys
- Automated user lifecycle management
- Compliance validation against system identity standards
- Audit trail for all identity modifications

## License

MIT

## Author

RylanLabs (@RylanLabs)  
https://github.com/RylanLabs/rylan-labs-common
