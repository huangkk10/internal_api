#!/bin/bash
# ============================================
# Docker 建置與執行腳本
# ============================================

set -e

# 顏色設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 確保在專案根目錄
cd "$(dirname "$0")/.."

# 檢查 .env 檔案
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from example...${NC}"
    cp .env.example .env
    echo -e "${RED}❗ Please edit .env file with your SAF credentials before running${NC}"
    exit 1
fi

case "${1:-help}" in
    build)
        echo -e "${GREEN}🔨 Building Docker image...${NC}"
        docker-compose build
        echo -e "${GREEN}✅ Build completed!${NC}"
        ;;
    up)
        echo -e "${GREEN}🚀 Starting container...${NC}"
        docker-compose up -d
        echo -e "${GREEN}✅ Container started!${NC}"
        echo -e "${GREEN}🌐 API available at http://localhost:8080${NC}"
        echo -e "${GREEN}📚 API docs at http://localhost:8080/docs${NC}"
        ;;
    down)
        echo -e "${YELLOW}🛑 Stopping container...${NC}"
        docker-compose down
        echo -e "${GREEN}✅ Container stopped!${NC}"
        ;;
    logs)
        docker-compose logs -f
        ;;
    restart)
        echo -e "${YELLOW}🔄 Restarting container...${NC}"
        docker-compose restart
        echo -e "${GREEN}✅ Container restarted!${NC}"
        ;;
    status)
        docker-compose ps
        ;;
    shell)
        echo -e "${GREEN}🐚 Opening shell in container...${NC}"
        docker-compose exec internal-api /bin/bash
        ;;
    *)
        echo "Usage: $0 {build|up|down|logs|restart|status|shell}"
        echo ""
        echo "Commands:"
        echo "  build   - Build Docker image"
        echo "  up      - Start container in background"
        echo "  down    - Stop and remove container"
        echo "  logs    - View container logs"
        echo "  restart - Restart container"
        echo "  status  - Show container status"
        echo "  shell   - Open shell in container"
        ;;
esac
