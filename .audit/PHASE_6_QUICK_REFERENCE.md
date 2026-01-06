# PHASE 6 QUICK REFERENCE: GITHUB CONFIGURATION (15-20 MIN)

> **Guardian**: Leo | **Ministry**: Bauer
> **Status**: IMMEDIATE NEXT STEP
> **Blocker**: NONE — Proceed now

---

## STEP 1: ADD GITHUB SECRETS (5 MIN)

**Navigate**: <https://github.com/RylanLabs/rylan-labs-common/settings/secrets/actions>

### 1a: Add GALAXY_API_KEY

```
Name:  GALAXY_API_KEY
Value: <paste from rylanlabs-private-vault/keys/ansible-galaxy/api-key.txt>
```

Click "Add secret"

### 1b: Add VAULT_SSH_KEY

```
Name:  VAULT_SSH_KEY
Value: <paste SSH private key for vault access>
```

Click "Add secret"

**Verify**:

```bash
gh secret list --repo RylanLabs/rylan-labs-common
```

Expected: Both secrets listed

---

## STEP 2: CONFIGURE BRANCH PROTECTION (7-10 MIN)

**Navigate**: <https://github.com/RylanLabs/rylan-labs-common/settings/branches>

**Click "Add rule"** and configure:

```
Branch name pattern: master

☑ Require a pull request before merging
  ☑ Require approvals: 1
  ☑ Dismiss stale pull request approvals

☑ Require status checks to pass before merging
  ☑ Require branches to be up to date

  Search and ADD these 4 checks:
  ☑ lint-ansible
  ☑ lint-python
  ☑ test-units
  ☑ validate-syntax

☑ Require conversation resolution
☑ Do not allow bypassing
```

Click "Create"

---

## STEP 3: CREATE PRODUCTION ENVIRONMENT (3-5 MIN)

**Navigate**: <https://github.com/RylanLabs/rylan-labs-common/settings/environments>

**Click "New environment"** and configure:

```
Name: production
Required reviewers: [Add yourself - Travis]
Wait timer: 0 minutes
```

Click "Save protection rules"

---

## VERIFICATION

```bash
# Verify all 3 steps complete
gh secret list --repo RylanLabs/rylan-labs-common
# Expected: GALAXY_API_KEY, VAULT_SSH_KEY

# Verify branch protection (GUI confirmation)
# Expected: "master" shows 1 rule with status checks

# Verify production environment (GUI confirmation)
# Expected: "production" environment listed
```

---

## NEXT: PHASE 7

Once Phase 6 complete, run:

```bash
cd /home/egx570/repos/rylan-labs-common
gh pr create \
  --title "feat(ci): Bootstrap GitHub Actions CI/CD infrastructure" \
  --base master \
  --head feature/ci-pr-validation
```

Then monitor: `gh pr checks --watch`

---

**Status**: MANUAL STEPS ONLY (No code execution)
**Time**: 15-20 minutes
**Then**: PHASE 7 (automated via gh CLI)
