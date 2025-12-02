#!/bin/bash
# ============================================
# 開發環境啟動腳本
# ============================================

set -e

# 顏色設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Internal API Server (Development)${NC}"

# 確保在專案根目錄
cd "$(dirname "$0")/.."

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
fi

# 啟動虛擬環境
source venv/bin/activate

# 檢查依賴
if [ ! -f "venv/.installed" ]; then
    echo -e "${YELLOW}📦 Installing dependencies...${NC}"
    pip install -r requirements-dev.txt
    touch venv/.installed
fi

# 檢查 .env 檔案
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from example...${NC}"
    cp .env.example .env
    echo -e "${RED}❗ Please edit .env file with your SAF credentials${NC}"
fi

# 啟動開發伺服器
echo -e "${GREEN}🌐 Starting server at http://localhost:8080${NC}"
echo -e "${GREEN}📚 API docs at http://localhost:8080/docs${NC}"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
