# rylan-labs-common/common.mk
# Guardian: Bauer | Ministry: Oversight
# Shared logic for the RylanLabs Mesh Substrate

SHELL := /usr/bin/bash
.SHELLFLAGS := -euo pipefail -c
.ONESHELL:

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
		jq -n \
			--arg ts "$$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
			--arg act "$(1)" \
			--arg grd "$(2)" \
			--arg sts "$(3)" \
			--arg dur "$(4)" \
			--arg det "$(5)" \
			'{"timestamp": $$ts, "action": $$act, "guardian": $$grd, "status": $$sts, "duration_ms": ($$dur | tonumber), "details": $$det}' \
			>> .audit/audit-trail.jsonl; \
	else \
		echo "[\$$(date -Iseconds)] [AUDIT] action=$(1) guardian=$(2) status=$(3) duration=$(4) details=$(5)" >> .audit/audit-trail.log; \
	fi
endef

# --- Common Targets ---
.PHONY: help-common validate publish cascade org-audit mesh-remediate resolve re-init refresh-readme test

test: ## Run Bauer unit tests (Pytest)
	@$(call log_info, Running Bauer unit tests)
	@pytest tests/unit/ && STATUS="PASS" || STATUS="FAIL"; \
	$(call log_audit,test,Bauer,$$STATUS,0,Pytest suite execution); \
	if [ "$$STATUS" = "FAIL" ]; then exit 1; fi

help: ## Show shared targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(lastword $(MAKEFILE_LIST)) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

resolve: ## Materialize symlinks for Windows/WSL/CI compatibility (Agnosticism Pattern)
	@$(call log_info, Materializing symlinks to literal files)
	@find . -type l -not -path '*/.*' -exec bash -c ' \
		target=$$(readlink -f "{}"); \
		if [ -e "$$target" ]; then \
			rm "{}"; \
			cp -r "$$target" "{}"; \
			chmod -R u+w "{}"; \
		else \
			echo "Warning: Broken symlink {} -> $$target"; \
		fi' \;
	@$(MAKE) refresh-readme
	@$(call log_success, Symlinks materialized.)

refresh-readme: ## Auto-generate README tier metadata from canon-manifest
	@$(call log_info, Refreshing README Metadata)
	@if [ -f canon-manifest.yaml ]; then \
		RESULTS=$$(python3 -c "import yaml; d=yaml.safe_load(open('canon-manifest.yaml')); print(f\"{d.get('tier','0')}|{d.get('tier_name','UNKNOWN')}|{','.join(d.get('dependencies', []))}|{d.get('maturity_level','0')}|{d.get('guardian','UNKNOWN')}\")" 2>/dev/null || echo "0|UNKNOWN|None|0|UNKNOWN"); \
		IFS='|' read -r TIER TIER_NAME DEPS MATURITY GUARDIAN <<< "$$RESULTS"; \
		ML5_SCORE=$$([ -f .audit/maturity-level-5-scorecard.yml ] && python3 -c "import yaml; d=yaml.safe_load(open('.audit/maturity-level-5-scorecard.yml')); print(d.get('overall_score', '0.0/10'))" 2>/dev/null || echo "N/A"); \
		printf "## Repository Metadata\n\n| Attribute | Value |\n| :--- | :--- |\n| **Tier** | %s (%s) |\n| **Dependencies** | %s |\n| **Maturity Level** | %s |\n| **ML5 Compliance** | %s |\n| **Guardian** | %s |\n| **Last Updated** | %s |\n\n---\n" \
			"$$TIER" "$$TIER_NAME" "$$DEPS" "$$MATURITY" "$$ML5_SCORE" "$$GUARDIAN" "$$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
			> .audit/readme-metadata.tmp; \
		if grep -q "<!-- METADATA_START -->" README.md; then \
			python3 -c "import sys; content=open('.audit/readme-metadata.tmp').read(); readme=open('README.md').read(); start='<!-- METADATA_START -->'; end='<!-- METADATA_END -->'; import re; new_readme = re.sub(f'{start}.*?{end}', f'{start}\\n{content}\\n{end}', readme, flags=re.DOTALL); open('README.md', 'w').write(new_readme)" 2>/dev/null; \
			$(call log_success, README metadata refresh); \
		fi; \
		rm -f .audit/readme-metadata.tmp; \
	fi
	@$(call log_audit,refresh-readme,Carter,PASS,0,README metadata auto-generated)

re-init: ## Re-sync repository with Canon Hub symlinks (Lazarus)
	@$(call log_info, Re-syncing with Canon Hub)
	@../rylan-canon-library/scripts/auto-migrate.sh

validate: ## Run standard Whitaker gates (Validator Suite)
	@$(call log_info, Running Whitaker Compliance Gates...)
	@if [ -x scripts/validate.sh ]; then \
		./scripts/validate.sh; \
	else \
		$(call log_info, No scripts/validate.sh found, performing basic check...); \
		for file in Makefile README.md .gitleaks.toml; do \
			if [ ! -f "$$file" ]; then \
				$(call log_error, Missing $$file); \
				exit 1; \
			fi; \
		done; \
		$(call log_success, Basic scaffolding valid.); \
	fi

publish: ## Sync state to mesh (Carter)
	@$(call log_info, Publishing state to mesh)
	@./scripts/publish-cascade.sh

cascade: ## Distribute secrets/state through mesh (Beale)
	@$(call log_info, Cascading mesh updates)
	@./scripts/publish-cascade.sh --cascade

org-audit: ## Multi-repo compliance scan (Whitaker)
	@$(call log_info, Starting organizational audit)
	@./scripts/org-audit.sh

mesh-remediate: ## Force drift back to green (Lazarus)
	@$(call log_info, Remediating mesh drift)
	@./scripts/mesh-remediate.sh
##@ Maturity Level 5 Validation

.PHONY: ml5-validate ml5-init ml5-report inject-canon

ml5-init: ## Initialize ML5 scorecard from Tier 0 template (Bauer)
	@$(call log_info, Initializing ML5 Scorecard from $(CANON_ROOT)/templates/ml5-scorecard.yml)
	@mkdir -p .audit/
	@if [ ! -f .audit/maturity-level-5-scorecard.yml ]; then \
		cp $(CANON_ROOT)/templates/ml5-scorecard.yml .audit/maturity-level-5-scorecard.yml; \
		repo_name=$$(basename "$$(pwd)"); \
		sed -i "s/repository: .*/repository: $$repo_name/" .audit/maturity-level-5-scorecard.yml 2>/dev/null || true; \
		sed -i "s/date_assessed: .*/date_assessed: $$(date -u +%Y-%m-%dT%H:%M:%SZ)/" .audit/maturity-level-5-scorecard.yml; \
		$(call log_success, Scorecard initialized at .audit/maturity-level-5-scorecard.yml); \
		$(call log_audit,ml5-init,Bauer,PASS,0,Scorecard initialized from Tier 0); \
	else \
		$(call log_info, Scorecard already exists.); \
	fi

ml5-validate: ## Run ML5 scorecard validation drill (Whitaker)
	@$(call log_info, Running ML5 Validation Drill)
	@START=$$(date +%s%3N); \
	$(CANON_ROOT)/scripts/validate-ml5-scorecard.sh .audit/maturity-level-5-scorecard.yml && STATUS="PASS" || STATUS="FAIL"; \
	END=$$(date +%s%3N); \
	$(call log_audit,ml5-validate,Bauer,$$STATUS,$$((END-START)),ML5 scorecard validation completion); \
	if [ "$$STATUS" = "FAIL" ]; then exit 1; fi

ml5-report: ## Generate ML5 compliance report
	@$(call log_info, ML5 Compliance Report)
	@if [ -f $(CANON_ROOT)/scripts/ml5-report-helper.py ]; then \
		python3 $(CANON_ROOT)/scripts/ml5-report-helper.py .audit/maturity-level-5-scorecard.yml; \
	elif [ -f scripts/ml5-report-helper.py ]; then \
		python3 scripts/ml5-report-helper.py .audit/maturity-level-5-scorecard.yml; \
	else \
		$(call log_error, ml5-report-helper.py not found); \
	fi

inject-canon: ## Inject Tier 0 Canon into satellite (Bootstrap)
	@$(call log_info, Injecting Tier 0 Canon into satellite)
	@mkdir -p .audit/
	@cp $(CANON_ROOT)/common.mk .
	@cp $(CANON_ROOT)/canon-manifest.yaml .
	@$(MAKE) ml5-init
	@$(MAKE) refresh-readme
	@$(call log_audit,inject-canon,Bauer,PASS,0,Tier 0 injection into satellite complete)
	@$(call log_success, Injection complete. Run 'make resolve' to materialize mesh logic)

##@ Resilience & Reversibility (Lazarus)

.PHONY: rollback-canon

rollback-canon: ## Revert Phase 0 injection (Emergency Only)
	@$(call log_info, Reverting Phase 0 TSH injection)
	@git checkout main -- docs/architecture/ docs/seven-pillars.md docs/README.md canon-manifest.yaml Makefile common.mk
	@$(call log_success, Phase 0 injection reverted to main state)
