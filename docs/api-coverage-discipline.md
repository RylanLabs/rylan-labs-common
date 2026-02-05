# API Coverage Discipline — RylanLabs Canon

> Canonical standard — Endpoint discovery and documentation
> Version: v2.0.0
> Date: 2026-01-14
> Agent: Bauer (Verification) | Domain: Documentation

---

## Overview

The **API Coverage Discipline** ensures that all infrastructure discovery (e.g., UniFi, Proxmox API endpoints) is systematically tracked. This prevents "Dark APIs" that are used in playbooks but lack DR documentation.

### Core Metrics (Bauer)

- **Target Coverage**: >80% for all production-grade API integrations.
- **Guardian Mapping**: Every endpoint must be mapped to a Guardian (Carter/Identity, Bauer/Verification, Beale/Hardening).
- **Drift Tolerance**: Zero. If an endpoint is used in a playbook, it *must* be in the coverage manifest.

---

## Tracking Mechanism

Coverage is tracked via `.audit/api/coverage.json`.

```json
{
    "total_endpoints": 20,
    "documented": 16,
    "coverage_pct": 80,
    "missing": ["/network/wan/status", "/security/threats/history"],
    "guardian_mapping": {
        "network": "Carter",
        "security": "Beale"
    }
}
```

### Automation: `track-endpoint-coverage.py`
This script parses discovery logs and cross-references them with the documented endpoint list.
- **Pre-commit**: Blocks merges if coverage drops below 80% without an explicit exemption.
- **CI**: Fails if new endpoints are detected in discovery but missing from the manifest.

---

## Guardian Responsibilities

### Carter (Identity)
- Document endpoints related to device identity, radio configurations, and port mappings.
- Ensure authentication schemes (Tokens, Cookies) are documented and versioned.

### Bauer (Verification)
- Document telemetry endpoints, client lists, and status monitors.
- Ensure error responses and rate limits are clearly defined.

### Beale (Hardening)
- Document firewall rules, threat management, and isolation settings.
- Ensure endpoints exposing sensitive metadata are restricted.

---

## Remediations
1. **IDENTIFY**: Run discovery scans against the API.
2. **DOCUMENT**: Map missing endpoints to Guardians and Purpose.
3. **UPDATE**: Commit changes to `.audit/api/coverage.json`.
4. **VERIFY**: Ensure CI pipeline turns GREEN.
