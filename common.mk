# rylan-labs-common/common.mk
# Guardian: Bauer | Ministry: Oversight
# Shared logic for the RylanLabs Mesh Substrate
# Purpose: Provide DRY, idempotent targets for mesh reconciliation
# Agent: Bauer (Verification)
# Author: RylanLabs canonical
# Date: 2026-02-05
# Compliance: Hellodeolu v7, Seven Pillars (Idempotency, Audit Logging, Validation)

SHELL := /usr/bin/bash
.SHELLFLAGS := -euo pipefail -c
.ONESHELL:

# --- Pathing & Identity ---
CANON_ROOT ?= .
VAULT_ROOT ?= $(shell realpath ../rylanlabs-private-vault 2>/dev/null || echo "../rylanlabs-private-vault")
GPG_KEY_ID ?= security@rylan.local

# --- Global Mesh Gates (No-Bypass) ---
# Check for unsigned commits and identity expiry on every invocation
# Note: Silenced to keep help output clean, but will exit 1 on failure
_GATES := $(shell bash scripts/whitaker-scan.sh >/dev/null 2>&1 && bash scripts/sentinel-expiry.sh >/dev/null 2>&1 || echo "FAIL")
ifeq ($(_GATES),FAIL)
  $(error [FAIL] Mesh Compliance Gates not met. Run 'make warm-session' or fix drift.)
endif

# --- Constants ---
DOMAIN_NAME := rylanlabs.io
GPG_KEY_ID  := F5FFF5CB35A8B1F38304FC28AC4A4D261FD62D75
CANON_ROOT  ?= .

# --- Terminal Styling ---
B_CYAN  := \033[1;36m
B_GREEN := \033[1;32m
B_RED   := \033[1;31m
NC      := \033[0m

# --- Shared Helpers ---
define log_info
	echo "$(B_CYAN)[INFO]$(NC) $(1)"
endef

define log_success
	echo "$(B_GREEN)[OK]$(NC) $(1)"
endef

define log_error
	echo "$(B_RED)[FAIL]$(NC) $(1)"
endef

define log_audit
	mkdir -p .audit/; \
	if command -v jq >/dev/null 2>&1; then \
		ENTRY=$$(jq -n \
			--arg ts "$$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
			--arg act "$(1)" \
			--arg grd "$(2)" \
			--arg sts "$(3)" \
			--arg dur "$(4)" \
			--arg det "$(5)" \
			'{"timestamp": $$ts, "action": $$act, "guardian": $$grd, "status": $$sts, "duration_ms": ($$dur | tonumber), "details": $$det}'); \
		echo "$$ENTRY" >> .audit/audit-trail.jsonl; \
		if [[ -n "$${GPG_KEY_ID:-}" ]]; then \
			echo "$$ENTRY" | gpg --armor --local-user "$$GPG_KEY_ID" --detach-sign >> .audit/audit-trail.jsonl.asc 2>/dev/null || true; \
		fi; \
	else \
		echo "[\$$(date -Iseconds)] [AUDIT] action=$(1) guardian=$(2) status=$(3) duration=$(4) details=$(5)" >> .audit/audit-trail.log; \
	fi
endef

# --- Common Targets ---
.PHONY: help-common validate publish cascade org-audit mesh-remediate resolve re-init refresh-readme test

test: ## Run Bauer unit tests (Pytest) | guardian: Bauer | timing: 30s
	@$(call log_info, Running Bauer unit tests)
	@START=$$(date +%s%3N); \
	pytest tests/unit/ && STATUS="PASS" || STATUS="FAIL"; \
	END=$$(date +%s%3N); \
	$(call log_audit,test,Bauer,$$STATUS,$$((END-START)),Pytest suite execution); \
	if [ "$$STATUS" = "FAIL" ]; then exit 1; fi

help: ## Show shared targets | guardian: Bauer | timing: <5s
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(lastword $(MAKEFILE_LIST)) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

resolve: ## Materialize symlinks for Windows/WSL/CI compatibility (Agnosticism Pattern) | guardian: Beale | timing: 15s
	@$(call log_info, Materializing symlinks to literal files)
	@START=$$(date +%s%3N); \
	find . -type l -not -path '*/.*' -exec bash -c ' \
		target=$$(readlink -f "{}"); \
		if [ -e "$$target" ]; then \
			if ! [ -e "{}" ] || ! diff -qr "{}" "$$target" >/dev/null 2>&1; then \
				rm -rf "{}"; \
				cp -r "$$target" "{}"; \
				chmod -R u+w "{}"; \
			fi \
		else \
			echo "Warning: Broken symlink {} -> $$target"; \
		fi' \; && STATUS="PASS" || STATUS="FAIL"; \
	END=$$(date +%s%3N); \
	$(MAKE) refresh-readme; \
	$(call log_audit,resolve,Beale,$$STATUS,$$((END-START)),Symlinks materialized); \
	if [ "$$STATUS" = "FAIL" ]; then exit 1; fi

refresh-readme: ## Auto-generate README tier metadata from canon-manifest | guardian: Carter | timing: <10s
	@$(call log_info, Refreshing README Metadata)
	@START=$$(date +%s%3N); \
	if [ -f canon-manifest.yaml ]; then \
		RESULTS=$$(python3 -c "import yaml; d=yaml.safe_load(open('canon-manifest.yaml')); print(f\"{d.get('tier','0')}|{d.get('tier_name','UNKNOWN')}|{','.join(d.get('dependencies', []))}|{d.get('maturity_level','0')}|{d.get('guardian','UNKNOWN')}\")" 2>/dev/null || echo "0|UNKNOWN|None|0|UNKNOWN"); \
		IFS='|' read -r TIER TIER_NAME DEPS MATURITY GUARDIAN <<< "$$RESULTS"; \
		ML5_SCORE=$$([ -f .audit/maturity-level-5-scorecard.yml ] && python3 -c "import yaml; d=yaml.safe_load(open('.audit/maturity-level-5-scorecard.yml')); print(d.get('overall_score', '0.0/10'))" 2>/dev/null || echo "N/A"); \
		printf "## Repository Metadata\n\n| Attribute | Value |\n| :--- | :--- |\n| **Tier** | %s (%s) |\n| **Dependencies** | %s |\n| **Maturity Level** | %s |\n| **ML5 Compliance** | %s |\n| **Guardian** | %s |\n| **Last Updated** | %s |\n\n---\n" \
			"$$TIER" "$$TIER_NAME" "$$DEPS" "$$MATURITY" "$$ML5_SCORE" "$$GUARDIAN" "$$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
			> .audit/readme-metadata.tmp; \
		if grep -q "<!-- METADATA_START -->" README.md; then \
			python3 -c "import sys, re; content=open('.audit/readme-metadata.tmp').read(); readme=open('README.md').read(); start='<!-- METADATA_START -->'; end='<!-- METADATA_END -->'; new_readme = re.sub(f'{start}.*?{end}', f'{start}\\n{content}\\n{end}', readme, flags=re.DOTALL); open('README.md', 'w').write(new_readme)" 2>/dev/null; \
			$(call log_success, README metadata refresh); \
		fi; \
		rm -f .audit/readme-metadata.tmp; \
		STATUS="PASS"; \
	else \
		STATUS="FAIL"; \
		$(call log_error, canon-manifest.yaml missing); \
	fi; \
	END=$$(date +%s%3N); \
	$(call log_audit,refresh-readme,Carter,$$STATUS,$$((END-START)),README metadata auto-generated)

re-init: ## Re-sync repository with Canon Hub symlinks (Lazarus) | guardian: Lazarus | timing: 20s
	@$(call log_info, Re-syncing with Canon Hub)
	@START=$$(date +%s%3N); \
	../rylan-canon-library/scripts/auto-migrate.sh && STATUS="PASS" || STATUS="FAIL"; \
	END=$$(date +%s%3N); \
	$(call log_audit,re-init,Lazarus,$$STATUS,$$((END-START)),Re-sync completed); \
	if [ "$$STATUS" = "FAIL" ]; then exit 1; fi

validate: ## Run standard Whitaker gates (Validator Suite) | guardian: Whitaker | timing: 30s
	@$(call log_info, Running Whitaker Compliance Gates...)
	@START=$$(date +%s%3N); \
	if [ -x scripts/validate.sh ]; then \
		./scripts/validate.sh && STATUS="PASS" || STATUS="FAIL"; \
	else \
		$(call log_info, No scripts/validate.sh found, performing basic check...); \
		for file in Makefile README.md .gitleaks.toml; do \
			if [ ! -f "$$file" ]; then \
				$(call log_error, Missing $$file); \
				STATUS="FAIL"; \
				break; \
			fi; \
		done; \
		if [ "$${STATUS:-}" != "FAIL" ]; then \
			$(call log_success, Basic scaffolding valid.); \
			STATUS="PASS"; \
		fi; \
	fi; \
	END=$$(date +%s%3N); \
	$(call log_audit,validate,Whitaker,$$STATUS,$$((END-START)),Compliance gates executed); \
	if [ "$$STATUS" = "FAIL" ]; then exit 1; fi

publish: ## Sync state to mesh (Carter) | Options: ARGS="--dry-run --force" | guardian: Carter | timing: 60s
	@$(call log_info, Publishing state to mesh)
	@START=$$(date +%s%3N); \
	if [ -f ./galaxy.yml ]; then \
		if [ -f ./scripts/publish-gate.sh ]; then \
			./scripts/publish-gate.sh $(ARGS) && STATUS="PASS" || STATUS="FAIL"; \
		elif [ -f $(CANON_ROOT)/scripts/publish-gate.sh ]; then \
			$(CANON_ROOT)/scripts/publish-gate.sh $(ARGS) && STATUS="PASS" || STATUS="FAIL"; \
		else \
			$(call log_error, publish-gate.sh not found); \
			STATUS="FAIL"; \
		fi; \
	else \
		if [ -f ./scripts/publish-cascade.sh ]; then \
			./scripts/publish-cascade.sh && STATUS="PASS" || STATUS="FAIL"; \
		else \
			$(call log_info, No collection or cascade script found. Skipping Galaxy publish.); \
			STATUS="PASS"; \
		fi; \
	fi; \
	END=$$(date +%s%3N); \
	$(call log_audit,publish,Carter,$$STATUS,$$((END-START)),State synced); \
	if [ "$$STATUS" = "FAIL" ]; then exit 1; fi

cascade: ## Distribute secrets/state through mesh (Beale) | guardian: Beale | timing: 2m
	@$(call log_info, Cascading mesh updates)
	@START=$$(date +%s%3N); \
	./scripts/publish-cascade.sh --cascade && STATUS="PASS" || STATUS="FAIL"; \
	END=$$(date +%s%3N); \
	$(call log_audit,cascade,Beale,$$STATUS,$$((END-START)),Mesh updates cascaded); \
	if [ "$$STATUS" = "FAIL" ]; then exit 1; fi

org-audit: ## Multi-repo compliance scan (Whitaker) | guardian: Whitaker | timing: 5m
	@$(call log_info, Starting organizational audit)
	@START=$$(date +%s%3N); \
	./scripts/org-audit.sh && STATUS="PASS" || STATUS="FAIL"; \
	END=$$(date +%s%3N); \
	$(call log_audit,org-audit,Whitaker,$$STATUS,$$((END-START)),Org audit completed); \
	if [ "$$STATUS" = "FAIL" ]; then exit 1; fi

mesh-remediate: ## Force drift back to green (Lazarus) | guardian: Lazarus | timing: 5m
	@$(call log_info, Remediating mesh drift)
	@START=$$(date +%s%3N); \
	./scripts/mesh-remediate.sh && STATUS="PASS" || STATUS="FAIL"; \
	END=$$(date +%s%3N); \
	$(call log_audit,mesh-remediate,Lazarus,$$STATUS,$$((END-START)),Drift remediated); \
	if [ "$$STATUS" = "FAIL" ]; then exit 1; fi
##@ Maturity Level 5 Validation

.PHONY: ml5-validate ml5-init ml5-report inject-canon

ml5-init: ## Initialize ML5 scorecard from Tier 0 template (Bauer) | Idempotent: Skips if exists
	@$(call log_info, Initializing ML5 Scorecard from $(CANON_ROOT)/templates/ml5-scorecard.yml)
	@START=$$(date +%s%3N); \
	mkdir -p .audit/; \
	if [ ! -f .audit/maturity-level-5-scorecard.yml ]; then \
		cp $(CANON_ROOT)/templates/ml5-scorecard.yml .audit/maturity-level-5-scorecard.yml; \
		repo_name=$$(basename "$$(pwd)"); \
		sed -i "s/repository: .*/repository: $$repo_name/" .audit/maturity-level-5-scorecard.yml; \
		sed -i "s/date_assessed: .*/date_assessed: $$(date -u +%Y-%m-%dT%H:%M:%SZ)/" .audit/maturity-level-5-scorecard.yml; \
		STATUS="PASS"; \
		$(call log_success, Scorecard initialized); \
	else \
		STATUS="SKIP"; \
		$(call log_info, Scorecard already exists); \
	fi; \
	END=$$(date +%s%3N); \
	$(call log_audit,ml5-init,Bauer,$$STATUS,$$((END-START)),Scorecard initialized from Tier 0)

ml5-validate: ## Run ML5 scorecard validation drill (Whitaker) | Adversarial: Integrates simulation
	@$(call log_info, Running ML5 Validation Drill)
	@START=$$(date +%s%3N); \
	$(CANON_ROOT)/scripts/validate-ml5-scorecard.sh .audit/maturity-level-5-scorecard.yml && STATUS="PASS" || STATUS="FAIL"; \
	END=$$(date +%s%3N); \
	$(call log_audit,ml5-validate,Whitaker,$$STATUS,$$((END-START)),ML5 scorecard validation completion); \
	if [ "$$STATUS" = "FAIL" ]; then exit 1; fi

ml5-report: ## Generate ML5 compliance report | Observability: JSON output
	@$(call log_info, ML5 Compliance Report)
	@START=$$(date +%s%3N); \
	if [ -f $(CANON_ROOT)/scripts/ml5-report-helper.py ]; then \
		python3 $(CANON_ROOT)/scripts/ml5-report-helper.py .audit/maturity-level-5-scorecard.yml && STATUS="PASS" || STATUS="FAIL"; \
	elif [ -f scripts/ml5-report-helper.py ]; then \
		python3 scripts/ml5-report-helper.py .audit/maturity-level-5-scorecard.yml && STATUS="PASS" || STATUS="FAIL"; \
	else \
		STATUS="FAIL"; \
		$(call log_error, ml5-report-helper.py not found); \
	fi; \
	END=$$(date +%s%3N); \
	$(call log_audit,ml5-report,Bauer,$$STATUS,$$((END-START)),Report generated); \
	if [ "$$STATUS" = "FAIL" ]; then exit 1; fi

inject-canon: ## Inject Tier 0 Canon into satellite (Bootstrap) | Idempotent: Verifies before copy
	@$(call log_info, Injecting Tier 0 Canon into satellite)
	@START=$$(date +%s%3N); \
	mkdir -p .audit/; \
	if ! diff -q $(CANON_ROOT)/common.mk common.mk >/dev/null 2>&1; then cp $(CANON_ROOT)/common.mk .; fi; \
	if ! diff -q $(CANON_ROOT)/canon-manifest.yaml canon-manifest.yaml >/dev/null 2>&1; then cp $(CANON_ROOT)/canon-manifest.yaml .; fi; \
	$(MAKE) ml5-init; \
	$(MAKE) refresh-readme; \
	STATUS="PASS"; \
	END=$$(date +%s%3N); \
	$(call log_audit,inject-canon,Bauer,$$STATUS,$$((END-START)),Tier 0 injection complete); \
	$(call log_success, Injection complete. Run 'make resolve' to materialize mesh logic)

##@ Resilience & Reversibility (Lazarus)

.PHONY: rollback-canon

rollback-canon: ## Revert Phase 0 injection (Emergency Only) | Reversibility: <15min RTO
	@$(call log_info, Reverting Phase 0 TSH injection)
	@START=$$(date +%s%3N); \
	git checkout main -- docs/architecture/ docs/seven-pillars.md docs/README.md canon-manifest.yaml Makefile common.mk && STATUS="PASS" || STATUS="FAIL"; \
	END=$$(date +%s%3N); \
	$(call log_audit,rollback-canon,Lazarus,$$STATUS,$$((END-START)),Injection reverted); \
	$(call log_success, Phase 0 injection reverted to main state); \
	if [ "$$STATUS" = "FAIL" ]; then exit 1; fi
