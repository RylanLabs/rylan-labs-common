.PHONY: help validate ci-local pre-commit-install clean build

SHELL := /bin/bash
.DEFAULT_GOAL := help

help:
	@echo "rylan-labs-common Makefile Targets"
	@echo "===================================="
	@echo "make validate              - Run all validators (ansible-lint, yamllint, ruff, mypy, pytest)"
	@echo "make ci-local              - Full CI validation (equivalent to make validate)"
	@echo "make pre-commit-install    - Install pre-commit hooks"
	@echo "make pre-commit-run        - Run pre-commit hooks on all files"
	@echo "make clean                 - Remove build artifacts and cache"
	@echo "make build                 - Build Ansible collection package"
	@echo "make help                  - Show this help message"

validate:
	@./scripts/validate-collection.sh

ci-local: validate
	@echo "[✓] CI validation complete (LOCAL GREEN)"

pre-commit-install:
	@echo "Installing pre-commit hooks..."
	@pre-commit install
	@echo "[✓] Pre-commit hooks installed"

pre-commit-run:
	@echo "Running pre-commit on all files..."
	@pre-commit run --all-files

clean:
	@echo "Cleaning build artifacts..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@rm -rf build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache
	@echo "[✓] Cleaned"

build: ci-local
	@echo "Building collection package..."
	@ansible-galaxy collection build
	@echo "[✓] Collection built"
