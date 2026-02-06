# RylanLabs Tier 3 Makefile: rylan-labs-common
# Maturity: Level 5 (Autonomous)

CANON_ROOT := ..

-include common.mk

# Collection-specific targets
extract-collection: ## Audit and extract logic from legacy paths (Grok Value Add)
	@$(call log_info, Auditing logic for extraction opportunities)
	@python3 scripts/three_domain_validator.py --workspace .
	@$(call log_success, Logic extraction coverage validated.)
