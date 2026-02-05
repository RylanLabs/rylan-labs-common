# RylanLabs Satellite Architecture — Quick Reference Card

**For**: Teams/Architects needing the 1-page view  
**Updated**: February 5, 2026

---

## 6-Tier Architecture (Visual)

```
TIER 0 (Root/SSOT)
├─ rylan-canon-library
│  └─ Seven Pillars, Trinity, common.mk, validation scripts
│
├─ TIER 0.5 (Secrets/Vault)
│  └─ rylanlabs-private-vault
│     └─ GPG/SOPS encrypted assets, rotation schedule
│
├─ TIER 1 (Inventory/SSOT)
│  └─ rylan-inventory
│     └─ device-manifest.yml, VLAN schema, OON objects, IP allocations
│
└─ TIER 2 (Shared Configs)
   └─ rylan-labs-shared-configs
      └─ Linting (.yamllint, pyproject.toml), CI templates, common.mk

        ↓
   TIER 3 (Common Libraries)
   └─ rylan-labs-common ← EXTRACT HERE (Phase B)
      ├─ Trinity Roles (carter-identity, bauer-verify, beale-harden)
      ├─ Custom Modules (unifi_api, zone_resolver, flatten_oon_groups)
      ├─ Validation Scripts (validate-isolation, whitaker-scan, sentinel-expiry)
      ├─ Exception Handling (exceptions.py, audit_trail_writer.py)
      └─ Publish as: rylanlabs.unifi (Ansible Galaxy collection)

        ↓
   TIERED 4 (Service Implementations)
   ├─ rylan-labs-network-iac ← REFACTOR HERE (Phase C: May-Jun)
   │  └─ Network provisioning, zones, VPN, ports (LIVE NOW)
   │
   ├─ rylanlabs-monitoring
   │  └─ D3-Early: Phase B/C validation metrics (Jun-Jul)
   │  └─ D3-Full: Alerts, Loki, Grafana, Anomaly Detection (Aug-Sep)
   │
   ├─ rylanlabs-aaa-core
   │  └─ Samba AD, FreeRADIUS, OPA, 802.1X (Jun-Jul 2026)
   │
   ├─ rylanlabs-policy-engine
   │  └─ Rego-based policies, compliance, ML (Aug 2026)
   │
   ├─ rylanlabs-threat-intel
   │  └─ MISP, OTX, anomaly detection (Sep-Oct 2026)
   │
   └─ rylanlabs-unifi-plugin
      └─ CoA, LDAP, real-time events (Sep-Oct 2026)
```

---

## Naming Convention (Settled)

| Prefix | Type | Examples |
|--------|------|----------|
| `rylan-labs-` | Infrastructure/DevOps (mature) | network-iac, shared-configs, common |
| `rylanlabs-` | Shared/Service (identity-first) | aaa-core, policy-engine, monitoring |
| `rylan-` | Canonical/Special (SSOT only) | canon-lib, inventory |

---

## Submodule Dependencies (Critical)

```
ALL Tier 4 repos include:
  submodules/
    canon-lib/ ─────────────┐
    shared-configs-lib/     ├─ Via git submodule
    inventory-hub/          │
    vault-hub/              │
    common-lib/             ┘
    
Included via: make resolve (materializes files, zero symlinks)
```

---

## Validation Gates (5-Gate Trinity System)

| Gate | Guardian | Pass/Fail |
|------|----------|-----------|
| 🔐 **Carter** | Identity | SSH key + GPG + manifest complete |
| 📊 **Bauer** | Audit | State diff + drift detection + logs |
| 🛡️ **Beale** | Security | Secrets scanned + firewall rules + certs |
| ⚔️ **Whitaker** | Offensive | Penetration testing + bypass detection |
| 🆘 **Lazarus** | Recovery | RTO validated + rollback tested |

**Result**: ALL gates must PASS to merge/deploy.

---

## Makefile Universal Targets (All Repos)

```bash
make resolve          # Materialize submodules (zero symlinks)
make validate         # Run all 5 validation gates (Trinity Council)
make secure           # Gitleaks + Secret scanning
make cascade          # Publish changes mesh-wide
make drill            # RTO recovery testing (Lazarus)
make warm-session     # 8-hour GPG password-less session
make org-audit        # Nightly mesh compliance check (Bauer)
make mesh-remediate   # Force-inject standards (human-approved)
```

---

## Timeline: 4 Phases (NOW → Oct 2026)

| Phase | Duration | Goal | Status |
|-------|----------|------|--------|
| **A** | NOW→Feb 28 | Tier 0-2 validated, zero symlinks | 95% ✅ |
| **B** | Mar 1→Apr 30 | Extract Tier 3 + Canary Rollout | 🚀 NEXT |
| **C** | May 1→Jun 15 | Refactor Tier 4a (flagship) | Planned |
| **D1-D5** | Jun 16→Oct 31 | Deploy satellites (AAA→D3→Policy→Threat→Plugin) | Planned |

---

## Current State Snapshot

| Component | Status | Owner | Notes |
|-----------|--------|-------|-------|
| Tier 0 (Canon) | ✅ Live | Bauer | Stable, no breaking changes |
| Tier 0.5 (Vault) | ✅ Live | Beale | GPG keys rotated Q1 2026 |
| Tier 1 (Inventory) | ✅ Live | Carter | device-manifest locked |
| Tier 2 (Configs) | ✅ Live | Bauer | Linting validated across mesh |
| Tier 3 (Common) | 🔨 Extracting | Trinity | Mar 1 kickoff (Phase B) |
| Tier 4a (Network) | ✅ Live | Carter | <7min RTO, 100% audit trail |
| Tier 4b-f (Services) | 🚀 Planned | Various | Phased Q2-Q4 2026 |

---

## Key Principles (Must Not Break)

1. **Idempotency**: Run twice = same result (no drift)
2. **Error Handling**: Fail fast, fail loud (clear messages)
3. **Audit Logging**: Every action → immutable `.audit/audit-trail.jsonl`
4. **Documentation**: Header comments (Purpose/Safety/RTO)
5. **Validation**: All changes pass 5 Trinity gates
6. **Reversibility**: Rollback path <15min RTO (tested)
7. **Observability**: Metrics → Prometheus, logs → Loki

---

## "Why" Summary

| Challenge | Solution | Owner |
|-----------|----------|-------|
| Symlink drift | Git submodules only | Trinity Council |
| Config duplication | Tier 2 centralization + cascade | Bauer |
| Role duplication | Tier 3 Galaxy collection | Carter |
| Bypass culture | 5 validation gates mandatory | Whitaker |
| Slow recovery | RTO <15min validation + Lazarus drills | Lazarus |
| Audit gaps | Immutable `.audit/` trails | Bauer |
| Unknown state | Bauer nightly reconciliation + Sentinel Loop | Bauer |

---

## Decision: Repo Name Changes?

**Recommendation**: Minimal changes, maximum clarity.

### KEEP (No Rename)
- `rylan-canon-library` ← Canonical precedent
- `rylan-inventory` ← SSOT signal
- `rylan-labs-shared-configs` ← Established

### NEW (Create)
- `rylan-labs-common` ← Tier 3 extraction (signals reusability)
- `rylanlabs-aaa-core` ← Identity-first naming (signals service tier)
- `rylanlabs-policy-engine` ← Service naming convention
- `rylanlabs-monitoring` ← Service naming convention
- `rylanlabs-threat-intel` ← Service naming convention
- `rylanlabs-unifi-plugin` ← Service naming convention

**Benefit**: Zero disruption to existing repos; new naming convention self-documents tier/purpose.

---

## Critical Path Dependencies

```
Phase A (Tiers 0-2) ──→ Phase B (Tier 3) ──→ Phase C (Tier 4a) ──→ Phase D (Tier 4b-f)
    ✅ NOW              🚀 Mar-Apr           Apr-May              Jun-Oct
  (Can start!)      (Blocks Phase C)    (Blocks Phase D)    (Parallel streams)
```

**Bottleneck**: Tier 3 extraction. Once complete, Phase D streams can run in parallel.

---

## Phase B Critical Deliverables

To unblock Phase C and all of Phase D:

- [ ] `rylan-labs-common` repo initialized
- [ ] Trinity roles extracted (carter, bauer, beale)
- [ ] Custom modules extracted (unifi_api, zone_resolver, etc.)
- [ ] Validation scripts extracted (validate-isolation, whitaker-scan, etc.)
- [ ] Full test suite (90%+ coverage)
- [ ] Ansible Galaxy published: `rylanlabs.unifi` v2.1.0
- [ ] `rylan-labs-network-iac` refactored to consume collection
- [ ] All 5 validation gates PASS
- [ ] Whitaker adversarial testing complete (no new bypass vectors)
- [ ] `MIGRATION-CHECKLIST-B.md` signed by Trinity Council

---

## Success Metrics (Phase D Target: Oct 2026)

| Metric | Target | Current |
|--------|--------|---------|
| Maturity Level | 5 (Autonomous) | 4 (Pinnacle) |
| Symlink Count | 0 | Several (Phase A) |
| RTO (network-iac) | <7min | <7min ✅ |
| RTO (full stack) | <15min | N/A (Phase D) |
| Audit Trail Completeness | 100% | 95% |
| Drift Detection Latency | 15min | 15min ✅ |
| Zero-Trust Coverage | 100% (AAA+Policy) | 0% (Q2 rollout) |
| Observability Coverage | 100% (Loki+Grafana) | 20% (basic logs) |

---

## Who Owns What?

| Component | Owner | Backup |
|-----------|-------|--------|
| Tier 0 (Canon) | Bauer (Verification) | Whitaker (Offensive) |
| Tier 0.5 (Vault) | Beale (Hardening) | Bauer (Verification) |
| Tier 1 (Inventory) | Carter (Identity) | Bauer (Verification) |
| Tier 2 (Configs) | Bauer (Verification) | Whitaker (Standards) |
| Tier 3 (Common) | Trinity Council (Joint) | Engineering leads |
| Tier 4a (Network) | Carter (Identity) | Beale (Hardening) |
| Tier 4b (AAA) | Carter (Identity) | Lazarus (Recovery) |
| Tier 4c (Policy) | Beale (Hardening) | Bauer (Verification) |
| Tier 4d (Monitoring) | Bauer (Verification) | Lazarus (Recovery) |
| Tier 4e (Threat) | Beale (Hardening) | Whitaker (Offensive) |
| Tier 4f (Plugin) | Carter (Identity) | Lazarus (Recovery) |

---

## One-Liner: What Is This?

**RylanLabs Tiered Satellite Hierarchy** = Git-native, zero-symlink, five-gate-validated, self-healing infrastructure mesh at Maturity Level 5.

---

**Print this. Pin it. Reference it daily.**


