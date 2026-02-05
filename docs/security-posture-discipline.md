# Security Posture Discipline — RylanLabs Canon

> Canonical standard — Network isolation and firewall hardening
> Version: v2.0.0
> Date: 2026-01-14
> Agent: Beale (Hardening) | Ministry: Hardening

---

## Overview

The **Security Posture Discipline** defines the non-negotiable requirements for network hardening. Every RylanLabs deployment must prioritize **Deny-All** defaults and **Explicit Isolation** over convenience.

### The Beale Mandates (Hardening)

1. **Deny-All Default**: All firewall policies must explicitly default to `deny-all` or `drop`.
2. **IoT Isolation**: VLAN 90 must have `device_isolation` enabled and zero access to internal subnets.
3. **Guest Isolation**: VLAN 80 must have `device_isolation` enabled and zero access to internal subnets.
4. **Implicit Deny between Hub/Spoke**: No traffic is allowed between branch locations unless specifically authorized via `Carter` identity verification.

---

## Technical Standards

### 1. Firewall Rule Ordering

Rules must be ordered logically to ensure efficiency and safety:

1. **Drop Invalid**: Drop packets with invalid states.
2. **Allow Established/Related**: Maintain session state.
3. **Allow Trusted Subnets**: Explicit access for MANAGEMENT (VLAN 1) and SERVERS (VLAN 10).
4. **Drop All**: The final catch-all rule.

### 2. Isolation Verification

Integrated into `validate-security-posture.sh`:

- **JQ Query**: `jq -e '.vlans[] | select(.id==90) | .device_isolation == true'`
- **Action**: CI job fails if any config exposes VLAN 90 to the MANAGEMENT plane.

---

## Operational Workflow

### Carter (Identity)

- Define the `owner` of each firewall rule for audit traceability.
- Verify that only authorized administrative roles have access to management subnets.

### Bauer (Verification)

- Audit current firewall rulesets against the canonical `network_scheme.yml`.
- Flag rules that use overly broad targets (e.g., `0.0.0.0/0` internal traffic).

### Beale (Hardening)

- Refine rule order based on breach simulations.
- Enforce encrypted transit for all inter-VLAN communications where possible.

---

## Remediations

- **Conflict Detected**: If a rule conflicts with isolation policy, the **Bauer** verification job must fail the deployment.
- **Legacy Cleanup**: Any rule without a `Carter` identity tag must be documented or replaced during the next maintenance window.
