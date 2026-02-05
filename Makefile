# RylanLabs Tier 3 Makefile: rylan-labs-common
# Maturity: Level 5 (Autonomous)

CANON_ROOT := ..

-include common.mk

# Collection build targets
build: ## Build the galaxy collection
	ansible-galaxy collection build --force

publish: build ## Build and publish the collection to Galaxy
	ansible-galaxy collection publish $$(ls rylanlabs-unifi-*.tar.gz | head -n 1)
