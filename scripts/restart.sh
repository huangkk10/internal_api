#!/bin/bash
# ============================================
# 重新啟動腳本
# 
# 用於重新載入環境變數（如 .env 變更後）
# ============================================

set -e

# 顏色設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 確保在專案根目錄
cd "$(dirname "$0")/.."

echo -e "${CYAN}🔄 Internal API 重新啟動腳本${NC}"
echo ""

# 檢測運行模式
detect_mode() {
    if docker-compose ps 2>/dev/null | grep -q "internal-api.*Up"; then
        echo "docker"
    elif pgrep -f "uvicorn app.main:app" > /dev/null 2>&1; then
        echo "dev"
    else
        echo "none"
    fi
}

# 重新啟動 Docker 容器
restart_docker() {
    echo -e "${YELLOW}🐳 偵測到 Docker 模式${NC}"
    echo -e "${YELLOW}🛑 停止容器...${NC}"
    docker-compose down
    echo -e "${GREEN}🚀 重新啟動容器...${NC}"
    docker-compose up -d
    echo ""
    echo -e "${GREEN}✅ Docker 容器已重新啟動！${NC}"
    echo -e "${GREEN}🌐 API: http://localhost:8080${NC}"
    echo -e "${GREEN}📚 Docs: http://localhost:8080/docs${NC}"
}

# 重新啟動開發伺服器
restart_dev() {
    echo -e "${YELLOW}💻 偵測到開發模式${NC}"
    echo -e "${YELLOW}🛑 停止現有程序...${NC}"
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    sleep 1
    
    # 啟動虛擬環境
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    echo -e "${GREEN}🚀 重新啟動開發伺服器...${NC}"
    echo ""
    nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8080 > /dev/null 2>&1 &
    sleep 2
    
    if pgrep -f "uvicorn app.main:app" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 開發伺服器已重新啟動！${NC}"
        echo -e "${GREEN}🌐 API: http://localhost:8080${NC}"
        echo -e "${GREEN}📚 Docs: http://localhost:8080/docs${NC}"
    else
        echo -e "${RED}❌ 啟動失敗，請手動執行 ./scripts/run_dev.sh${NC}"
        exit 1
    fi
}

# 主程式
MODE=$(detect_mode)

case "$MODE" in
    docker)
        restart_docker
        ;;
    dev)
        restart_dev
        ;;
    none)
        echo -e "${YELLOW}⚠️  未偵測到運行中的服務${NC}"
        echo ""
        echo "請選擇啟動方式："
        echo "  1) Docker 模式"
        echo "  2) 開發模式"
        echo ""
        read -p "請輸入選項 (1/2): " choice
        case "$choice" in
            1)
                echo ""
                restart_docker
                ;;
            2)
                echo ""
                restart_dev
                ;;
            *)
                echo -e "${RED}❌ 無效選項${NC}"
                exit 1
                ;;
        esac
        ;;
esac

echo ""
echo -e "${CYAN}💡 提示：環境變數已重新載入${NC}"
