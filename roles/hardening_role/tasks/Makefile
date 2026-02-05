# RylanLabs Task Overlay — infrastructure_fortification Tasks
# Purpose: Logic and data verification for task execution blocks

.PHONY: help verify-logic verify-data

help: ## Display task-level verification help
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make \033[33m<target>\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[33m%-25s\033[0m %s\n", $$1, $$2 } ' $(MAKEFILE_LIST)

verify-logic: ## Verify task logic against canonical patterns
	@echo "▶ Verifying task logic for Infrastructure Fortification..."
	@grep -r "ansible.builtin.uri" . || echo "⚠ No API calls found in tasks."

verify-data: ## Verify data structures required by these tasks
	@echo "▶ Verifying data dependencies for Infrastructure Fortification..."
	@test -f ../../../vars/oon_objects.yml || (echo "❌ Missing oon_objects.yml" && exit 1)
