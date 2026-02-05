# Network Versioning Discipline — RylanLabs Canon

> Canonical standard — SemVer tracking for Network Infrastructure
> Version: v2.0.0
> Date: 2026-01-14
> Agent: Carter (Identity) | Ministry: Bootstrap

---

## Overview

Network configurations (VLANs, Subnets, Firewall rules) are code. To prevent drift across multiple sites or deployments, all network schemes must follow **Semantic Versioning (SemVer)**.

### The Carter Mandate (Identity)

- **`network_scheme.version`**: All network configuration files MUST include a top-level version field.
- **Immutable History**: Once a version is deployed to production, any change requires a version bump.
- **Drift Detection**: CI must fail if the content of `network_scheme.yml` changes but the version number remains the same.

---

## SemVer for Networks

- **MAJOR (X.0.0)**: Breaking changes. IP scheme re-addressing, deletion of primary VLANs, change in management plane.
- **MINOR (0.X.0)**: Non-breaking additions. Adding a new VLAN, adding a new subnet, expanding a DHCP pool.
- **PATCH (0.0.X)**: Bug fixes or descriptive updates. Renaming a VLAN description, fixing a typo in a DNS entry.

---

## Implementation

### Manifest Requirement
Every site-specific `group_vars/network_scheme.yml` must lead with:

```yaml
network_scheme:
  version: "1.0.0"
  vlans: [...]
```

### Validation (Bauer)
The CI pipeline checks the version field vs. Git history:
- **Rule**: If `network_scheme.yml` appears in the git diff, the version string *must* be different from the previous commit.
- **Tool**: Handled by `scripts/validate-network-version.sh` (or integrated into common validators).

---

## Operations

### Deployment
1. **Carter**: Assign a new version number to the proposed scheme.
2. **Bauer**: Verify the scheme against the `validate-security-posture.sh` rules.
3. **Beale**: Apply the scheme to the target environment.
4. **Whitaker (Automation)**: Update the site-inventory with the new version tag.

---

## Remediations
- **Stale Version Detected**: If a deployment is attempted with a version already in the audit log but with different hashes, the deployment is **ABORTED**.
- **Manual Overrides**: Are considered drift. The system will attempt to "re-apply" the versioned state to override manual changes.
