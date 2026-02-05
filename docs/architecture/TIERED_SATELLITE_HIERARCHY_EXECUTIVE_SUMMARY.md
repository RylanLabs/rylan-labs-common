# RylanLabs Tiered Satellite Hierarchy — Executive Summary

**Date**: February 5, 2026  
**Prepared By**: Trinity Council (Carter/Bauer/Beale/Whitaker/Lazarus)  
**Status**: READY FOR ADOPTION

---

## The Big Picture: What Changed & Why?

### From: Symlink Fragility → To: Git-Native Robustness

**Old Model**: Fragile symlinks (prone to drift/breakage) scattered across repos.

**New Model**: Robust Git submodules + Makefile meta-reconcilers enforcing idempotent state.

---

## The 6-Tier Canonical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ TIER 0: Immutable Standards Root                            │
│ rylan-canon-library (Seven Pillars, Trinity, common.mk)     │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ TIER 0.5:    │ │ TIER 1:      │ │ TIER 2:      │
│ Secrets      │ │ Inventory    │ │ Shared Cfgs  │
│ (Vault)      │ │ (SSOT)       │ │ (Linting)    │
└────────┬─────┘ └──────┬───────┘ └──────┬───────┘
         │              │               │
         └──────────────┼───────────────┘
                        ▼
         ┌──────────────────────────────┐
         │ TIER 3: Common Libraries     │
         │ rylan-labs-common (Galaxy)   │
         │ - Trinity Roles              │
         │ - Custom Modules             │
         │ - Validation Scripts         │
         └──────────────┬───────────────┘
                        │
        ┌───────────────┼───────────────┬──────────────────┐
        ▼               ▼               ▼                  ▼
    ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐
    │ TIER 4a    │ │ TIER 4b    │ │ TIER 4c    │ │ TIER 4d/e/f│
    │ Network    │ │ AAA Core   │ │ Policy     │ │ Monitoring │
    │ IaC        │ │ (RADIUS)   │ │ Engine     │ │ & Threat   │
    │ (Flagship) │ │ (Identity) │ │ (OPA)      │ │ Intel      │
    └────────────┘ └────────────┘ └────────────┘ └────────────┘
     (LIVE)         (Q2 2026)      (Q2-Q3)        (Q3-Q4)
```

---

## Key Decisions & Rationale

| Decision | Rationale | Impact |
|----------|-----------|--------|
| **Keep `rylan-canon-library` name** | Established signal for SSOT; avoids rename churn | Zero disruption; canonical precedent |
| **Use `rylan-labs-` prefix for infrastructure repos** | Mature, production-ready signal | Clarity in GitHub search/filtering |
| **Use `rylanlabs-` prefix for shared/service repos** | Identity-first; signals containment/sharing | Consistent with Trinity agents (aaa-core, monitoring) |
| **Extract Tier 3 to separate Galaxy collection** | DRY principle; reduce duplication across satellites | Enable scaling from 1 to 10+ satellites; reuse roles/modules |
| **Consolidate playbooks 99→7** | Cognitive load reduction; easier onboarding | Junior-at-3-AM ready; <7min RTO |
| **Phased Tier 4 rollout (D1→D5)** | De-risk critical path (AAA before policy); parallel non-blocking | 6-month runway; full coverage by Oct 2026 |

---

## Current State: Where We Are Today

✅ **Tiers 0-2**: Deployed, stable, audited (95% complete)
- rylan-canon-library (Seven Pillars, Trinity patterns)
- rylanlabs-private-vault (GPG/SOPS encrypted)
- rylan-inventory (device-manifest SSOT locked)
- rylan-labs-shared-configs (linting/CI validated)

🔄 **Tier 3**: Extraction in progress
- Currently embedded in rylan-labs-network-iac
- Needs: Extract roles, modules, plugins → rylan-labs-common
- Publish to Ansible Galaxy as `rylanlabs.unifi` collection
- Timeline: Mar 1 — Apr 30, 2026 (Phase B)

✅ **Tier 4a**: rylan-labs-network-iac (Flagship, production)
- Current: Monolithic (99 playbooks, 1000+ LOC)
- Target: Refactored (7 core playbooks, Galaxy collection consumption)
- Timeline: May 1 — Jun 15, 2026 (Phase C)

🚀 **Tier 4b-4f**: Planned satellite services
- **AAA Core** (Jun 16 — Jul 31): Samba HA, FreeRADIUS, OPA
- **Monitoring (Early)** (Jun 1 — Jul 15): Core metrics/logs for Phase B/C validation.
- **Policy Engine** (Aug 1 — Aug 31): Rego-based compliance
- **Monitoring (Full)** (Aug 1 — Sep 30): Loki/Grafana/Prometheus stack
- **Threat Intel** (Sep 1 — Oct 15): MISP/OTX feeds + anomaly detection
- **UniFi Plugin** (Sep 1 — Oct 31): Real-time CoA/LDAP integration

---

## Migration Timeline at a Glance

| Phase | Duration | Goals | Status |
|-------|----------|-------|--------|
| **A** | NOW→Feb 28 | Validate Tiers 0-2, zero symlinks | 95% Done |
| **B** | Mar 1→Apr 30 | Extract Tier 3 (Galaxy collection) | 🚀 NEXT |
| **C** | May 1→Jun 15 | Refactor Tier 4a (flagship overhaul) | Planned |
| **D1** | Jun 16→Jul 31 | Deploy AAA Core (identity) | Planned |
| **D2-D5** | Aug 1→Oct 31 | Deploy Policy, Monitoring, Threat Intel | Planned |

---

## The Seven Pillars in Action

Every repo must enforce these principles:

1. **Idempotency**: Run twice, get same result (no drift)
2. **Error Handling**: Fail fast, fail loud (clear context)
3. **Audit Logging**: Every action → `.audit/audit-trail.jsonl` (immutable)
4. **Documentation**: Header comments with Purpose/Safety/RTO (Junior-at-3-AM)
5. **Validation**: Pre-flight gates (Carter/Bauer/Beale/Whitaker/Lazarus)
6. **Reversibility**: Rollback path exists, tested (<15min RTO)
7. **Observability**: Metrics exported to Prometheus, logs to Loki

---

## Validation Gates: The Trinity Council

All changes pass through five gates:

| Gate | Guardian | Checks | Failure Mode |
|------|----------|--------|--------------|
| **Carter** | Identity | SSH key, GPG signature, manifest completeness | Reject commit |
| **Bauer** | Verification | State diff, drift detection, audit trail | Alert + remediate |
| **Beale** | Hardening | Secret scanning, firewall rules, cert expiry | Block merge |
| **Whitaker** | Offensive | Penetration testing, bypass detection | Block deployment |
| **Lazarus** | Recovery | RTO validation, backup integrity, rollback testing | Block deployment |

---

## Key Architectural Principles

### 1. Git-Native (No Symlinks)

**Why?**: Symlinks break in CI/CD, WSL, multi-branch workflows.

**How?**: All dependencies via Git submodules. `make resolve` materializes files (copies, not links).

### 2. Tiered Boundaries (Maturity Level 5)

**Why?**: Enforce escalating trust/validation levels.

**How**:
- Tier 0-2: Governance, secrets, inventory (SSOT = immutable)
- Tier 3: Reusable logic (Galaxy-published, tested)
- Tier 4: Satellite implementations (consume Tier 0-3, domain-specific)

### 3. Meta-Reconciliation via Makefile

**Why?**: Uniform operational interface across mesh.

**How**: All repos expose `make resolve`, `make validate`, `make cascade`, `make drill`.

### 4. No-Bypass Culture

**Why?**: Prevent accidental/malicious bypasses (drift, secrets leakage, zone violations).

**How**: Every change requires passing all Trinity gates. Emergency override requires incident + post-mortem.

---

## What Gets Built: Tier 4 Services Roadmap

### Tier 4a: Network IaC (Flagship) — LIVE NOW

Provisions UniFi network (UXG-Max baseline, Hellodeolu v7 zones, firewall rules, VLAN isolation).

**KPIs**: RTO <7min, <1% drift over 30 days, 100% audit trail.

### Tier 4b: AAA Core — Q2 2026

Orchestrates authentication (Samba AD HA, FreeRADIUS, 802.1X, dynamic VLAN assignment, OPA policies).

**KPIs**: Auth latency <100ms, cert rotation 100% automated, zero credential bypass.

### Tier 4c: Policy Engine — Q2-Q3 2026

Enforces policies-as-code (OPA Rego, compliance mappings, ML anomaly detection).

**KPIs**: Policy eval <50ms, false-positive rate <5%, 100% CIS benchmark coverage.

### Tier 4d: Monitoring — Q3 2026

Unified observability (Loki logs, Prometheus metrics, Grafana dashboards, alerts).

**KPIs**: Query latency <1s, 30-day retention, <99th percentile response <500ms.

### Tier 4e: Threat Intel — Q3-Q4 2026

Real-time threat feeds (MISP, OTX, Abuse.ch), dynamic deny lists, anomaly response.

**KPIs**: Feed ingest latency <5min, false-positive rate <5%, auto-quarantine <1min.

### Tier 4f: UniFi Plugin — Q4 2026

Custom UniFi OS plugin (CoA events, LDAP watcher, real-time zone reassignments).

**KPIs**: Event latency <500ms, zone change <2sec, 100% LDAP sync.

---

## Naming Convention (Settled)

### Why Two Prefixes?

**`rylan-labs-`** = Infrastructure/DevOps (production, provisioning)
- `rylan-labs-network-iac`
- `rylan-labs-shared-configs`
- `rylan-labs-common`

**`rylanlabs-`** = Shared/Service (identity, monitoring, policies)
- `rylanlabs-private-vault`
- `rylanlabs-aaa-core`
- `rylanlabs-policy-engine`
- `rylanlabs-monitoring`
- `rylanlabs-threat-intel`
- `rylanlabs-unifi-plugin`

**Benefit**: GitHub search filters clearly; naming convention self-documents repo type.

---

## What Needs to Happen NOW (Phase B Start)

### Tier 3 Extraction (Mar 1 — Apr 15, 2026)

1. **Create `rylan-labs-common` repo** with structure:
   ```
   roles/
     carter-identity/
     bauer-verify/
     beale-harden/
   plugins/
     modules/unifi_api.py
     filters/zone_resolver.py
     filters/flatten_oon_groups.py
   scripts/
     validate-isolation.sh
     whitaker-scan.sh
     sentinel-expiry.sh
   lib/
     exceptions.py
     audit_trail_writer.py
   galaxy.yml
   tests/
   ```

2. **Extract from flagship** (`rylan-labs-network-iac`)
   - Copy roles, modules, filters, scripts
   - Refactor to remove network-iac-specific assumptions
   - Add full test suite + documentation

3. **Publish to Ansible Galaxy**
   - Collection: `rylanlabs.unifi` v2.1.0
   - Include MANIFEST.md, per-role README

4. **Update flagship** to consume collection
   - `requirements.yml`: Add `collections: [rylanlabs.unifi]`
   - `make resolve` pulls from Galaxy or local submodule

5. **Validation**
   - All playbooks still idempotent (run twice = same result)
   - Whitaker adversarial testing (no new bypass vectors)
   - Bauer audit (zero new PII leakage)

---

## Success Criteria for Phase B

- ✅ `rylan-labs-common` repo created + Galaxy published
- ✅ `rylan-labs-network-iac` refactored to consume collection
- ✅ All 7 core playbooks pass validation gates (Carter/Bauer/Beale/Whitaker/Lazarus)
- ✅ RTO validated <7min bootstrap from clean state
- ✅ Zero symlinks across both repos
- ✅ `MIGRATION-CHECKLIST-B.md` signed by Trinity Council

---

## Bottom Line: Where We're Headed

**By October 2026**, RylanLabs will have:

✅ **Zero symlink drift** (pure Git submodules)  
✅ **RTO <15min** (full stack recovery, <7min network-iac)  
✅ **100% audit trail** (immutable `.audit/` logs)  
✅ **Autonomous remediation** (Sentinel Loop + Bauer audits)  
✅ **Unlimited scalability** (Hellodeolu v7 zones/rules)  
✅ **Zero-trust identity** (802.1X + OPA + Samba HA)  
✅ **Maturity Level 5** (Autonomous, self-healing, no-bypass enforced)

This is the **canonical, battle-tested architecture** for RylanLabs infrastructure at scale.

---

**Next Step**: Schedule Phase B kickoff meeting (Trinity Council + engineering team).  
**Recommendation**: Start Tier 3 extraction immediately; it's critical path for all Phase D services.


