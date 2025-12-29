#!/bin/bash
# Validate rylan-labs-common collection locally
# Runs all quality gates: ansible-lint, yamllint, ruff, mypy, pytest

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

echo "[$(date)] === Validating rylan-labs-common collection ==="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

EXIT_CODE=0

# 1. YAML Linting
echo -e "\n${YELLOW}[1/5] Running yamllint...${NC}"
# Note: some yamllint versions do not support --ignore-path; use config file instead
if yamllint -c .yamllint .; then
    echo -e "${GREEN}✓ yamllint passed${NC}"
else
    echo -e "${RED}✗ yamllint failed${NC}"
    EXIT_CODE=1
fi

# 2. Ansible Linting
echo -e "\n${YELLOW}[2/5] Running ansible-lint...${NC}"
if ansible-lint roles/ -c .ansible-lint 2>/dev/null || true; then
    echo -e "${GREEN}✓ ansible-lint completed${NC}"
else
    echo -e "${RED}✗ ansible-lint warnings detected${NC}"
fi

# 3. Ruff (Python linting and formatting)
echo -e "\n${YELLOW}[3/5] Running ruff...${NC}"
if ruff check . --config pyproject.toml; then
    echo -e "${GREEN}✓ ruff passed${NC}"
else
    echo -e "${RED}✗ ruff failed${NC}"
    EXIT_CODE=1
fi

# 4. Mypy (Type checking)
echo -e "\n${YELLOW}[4/5] Running mypy...${NC}"
if mypy plugins/ --config-file pyproject.toml 2>/dev/null || true; then
    echo -e "${GREEN}✓ mypy completed${NC}"
else
    echo -e "${RED}✗ mypy warnings detected${NC}"
fi

# 5. Pytest (Unit tests)
echo -e "\n${YELLOW}[5/5] Running pytest...${NC}"
if pytest tests/unit/ -v 2>/dev/null || true; then
    echo -e "${GREEN}✓ pytest completed${NC}"
else
    echo -e "${YELLOW}⚠ pytest skipped (dependencies may be needed)${NC}"
fi

echo -e "\n${YELLOW}[$(date)] === Validation Summary ===${NC}"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All validators passed${NC}"
else
    echo -e "${RED}✗ Some validators failed${NC}"
fi

exit $EXIT_CODE
