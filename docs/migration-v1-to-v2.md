# Migration Guide: rylanlab.common v1.x → v2.0.0

## Overview
Standardization on community-friendly naming schemes and Agent roles has introduced breaking changes to role names and module namespaces.

## Breaking Changes: Role Names
Legacy personified roles have been consolidated into standardized functional roles. Update your playbooks accordingly.

| Legacy Role (v1.x) | New Role (v2.0.0) | Agent |
| :--- | :--- | :--- |
| `carter_identity` / `identity_management` | `identity_management` | Carter |
| `bauer_verify` / `infrastructure_verify` | `verification_audit` | Bauer |
| `beale_harden` / `hardening_management` | `infrastructure_fortification` | Beale |
| (New) | `adversarial_simulation` | Whitaker |

## Breaking Changes: Module Usage
Native modules replace raw `uri` tasks and legacy scripts.

**OLD (v1.x):**
```yaml
- name: Create firewall group
  uri:
    url: "{{ unifi_host }}/api/s/default/rest/firewallgroup"
    method: POST
```

**NEW (v2.0.0):**
```yaml
- name: Create firewall group
  rylanlab.common.unifi_group:
    name: internal_networks
    type: address-group
    members: ["10.0.30.0/24"]
```

## Audit Logging
Manual audit logging to `.audit/` is now deprecated. Roles automatically utilize the `rylan_audit_logger` utility at the end of every task block.

## Migration Checklist
- [ ] Update `requirements.yml` to `rylanlab.common: ">=2.0.0"`.
- [ ] Search and replace hyphenated role names with snake_case underscored ones.
- [ ] Replace `beale_harden` references with `infrastructure_fortification`.
- [ ] Replace `bauer_verify` references with `verification_audit`.
- [ ] Test all playbooks with `ansible-playbook --check`.
