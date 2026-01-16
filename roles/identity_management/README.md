<!-- markdownlint-disable MD013 MD024 MD001 MD029 MD040 MD025 -->
# Ansible Role: rylanlab.common.identity_management

**Component**: Identity & Authentication Management
**Compliance**: Production-Grade (Seven Pillars)

## Description

Identity management and standards enforcement role. Manages authentication services (RADIUS, LDAP), SSH keys, and system identity validation. This role ensures a standardized identity fabric across infrastructure.

## Requirements

- Ansible >= 2.14
- Python >= 3.11
- Target systems: Ubuntu 22.04+, RHEL 9+

## Role Variables

### Defaults (see `defaults/main.yml`)

```yaml
identity_ssh_key_path: ~/.ssh/authorized_keys
identity_enforce_naming: true
identity_user_management: true
identity_management_validation: true
identity_management_audit_enabled: true
```

### Required Variables

```yaml
identity_authorized_keys: []  # List of SSH public keys to deploy
identity_managed_users: []    # List of user account definitions
```

## Dependencies

None.

## Example Playbook

```yaml
---
- name: Deploy Identity Identity Management
  hosts: all
  roles:
    - role: rylanlab.common.identity_management
      vars:
        identity_authorized_keys:
          - ssh-ed25519 AAAAC3... admin@rylan
          - ssh-ed25519 AAAAC3... deploy@rylan
        identity_managed_users:
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

## 3-Domain Integration

**Identity's Role in 3-Domain Pattern**:

- **Identity** (Identity): Primary guardian for system identity enforcement
- **Audit** (Auditor): Logs identity changes for audit trail
- **Hardening** (Bastille): Validates SSH hardening and security compliance

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
<https://github.com/RylanLabs/rylan-labs-common>
