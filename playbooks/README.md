# Playbook Examples

This directory contains production-grade examples demonstrating how to use the
`rylanlab.common` collection following the **Trinity 7-Task Pattern**.

## Trinity 7-Task Pattern

All production playbooks in this collection follow a standardized workflow to
ensure safety, idempotency, and auditability:

1. **GATHER**: Retrieve the current state of the infrastructure.
2. **PROCESS**: Validate constraints and calculate necessary changes.
3. **APPLY**: Execute the changes (Identity/Hardening logic).
4. **VERIFY**: Confirm the infrastructure reached the desired state.
5. **COMPLIANCE**: Assert health and policy adherence.
6. **REPORT**: Generate a persistent audit log in `.audit/`.
7. **FINALIZE**: Provide actionable feedback to the operator.

---

## Example Catalog

### 1. VLAN Infrastructure Bootstrap (Carter Guardian)

**File**: [example-vlan-bootstrap.yml](example-vlan-bootstrap.yml)

**Purpose**: Provisions a canonical VLAN scheme (Management, IoT, Guest).

- **Constraints**: Enforces max 5 corporate VLANs (hardware offload limit).
- **Safety**: Defaults to `simulation_mode: true`.

### 2. Network Hardening (Beale Guardian)

**File**: [example-firewall-rules.yml](example-firewall-rules.yml)

**Purpose**: Deploys a "Default-Deny" firewall policy with VLAN isolation.

- **Constraints**: Enforces max 10 rules (Hellodeolu v6 hardware limit).
- **Verification**: Includes automatic Whitaker breach simulation hooks.

### 3. Identity Management

**File**: [example-identity.yml](example-identity.yml)

**Purpose**: Demonstration of provisioning identity-linked services.

### 4. Holistic Bootstrap

**File**: [example-bootstrap.yml](example-bootstrap.yml)

**Purpose**: A full sequence demonstrating the interaction between Identity,
Audit, and Hardening roles.

---

## Usage Guide

Most examples require a UniFi API key and host specification.

### Simulation Mode (Safe)

```bash
ansible-playbook playbooks/example-firewall-rules.yml
```

### Production Deployment

```bash
export UNIFI_API_KEY='your-key-here'
export UNIFI_HOST='https://192.168.1.1:443'

ansible-playbook playbooks/example-firewall-rules.yml \
  -e unifi_simulation_mode=false
```

Audit trails for every run are stored in the `.audit/` directory at the project root.
