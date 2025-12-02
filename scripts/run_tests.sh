#!/bin/bash
# ============================================
# 執行測試腳本
# ============================================

set -e

# 顏色設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧪 Running Tests${NC}"

# 確保在專案根目錄
cd "$(dirname "$0")/.."

# 啟動虛擬環境 (如果存在)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 執行測試
case "${1:-all}" in
    unit)
        echo -e "${BLUE}Running unit tests...${NC}"
        pytest tests/unit/ -v
        ;;
    integration)
        echo -e "${BLUE}Running integration tests...${NC}"
        pytest tests/integration/ -v
        ;;
    coverage)
        echo -e "${BLUE}Running tests with coverage...${NC}"
        pytest --cov=app --cov=lib --cov-report=html --cov-report=term-missing
        echo -e "${GREEN}📊 Coverage report: htmlcov/index.html${NC}"
        ;;
    fast)
        echo -e "${BLUE}Running fast tests (no slow markers)...${NC}"
        pytest -v -m "not slow"
        ;;
    *)
        echo -e "${BLUE}Running all tests...${NC}"
        pytest -v
        ;;
esac

echo -e "${GREEN}✅ Tests completed!${NC}"
