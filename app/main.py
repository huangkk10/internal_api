"""
FastAPI 應用程式入口

Internal API Server - 用於取得 SAF (Silicon Motion) 網站資訊
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import get_settings
from app.middlewares.error_handler import ErrorHandlerMiddleware
from app.models.schemas import APIResponse, HealthResponse
from app.routers import auth, projects
from lib.logger import setup_logging, get_logger
from lib.utils import format_response

# 取得設定
settings = get_settings()

# 設定日誌
setup_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    # 啟動時
    logger.info(f"Starting Internal API Server v{__version__}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"SAF URL: {settings.saf_base_url}")
    
    yield
    
    # 關閉時
    logger.info("Shutting down Internal API Server")


# 建立 FastAPI 應用
app = FastAPI(
    title="Internal API Server",
    description="API Server for accessing SAF (Silicon Motion) data",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# 加入 CORS 中介軟體
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應該限制來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 加入錯誤處理中介軟體
app.add_middleware(ErrorHandlerMiddleware)

# 註冊路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")


# ========== 根路由 ==========

@app.get("/", summary="API 首頁")
async def root():
    """API Server 首頁，顯示基本資訊"""
    return {
        "name": "Internal API Server",
        "version": __version__,
        "description": "API Server for accessing SAF (Silicon Motion) data",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse, summary="健康檢查")
async def health_check():
    """
    健康檢查端點
    
    用於 Docker 健康檢查和負載平衡器探測
    """
    return HealthResponse(
        status="healthy",
        version=__version__,
        timestamp=datetime.now(timezone.utc)
    )


@app.get("/config", response_model=APIResponse, summary="取得設定資訊")
async def get_config():
    """
    取得目前的設定資訊 (不包含敏感資訊)
    """
    return format_response(
        success=True,
        data={
            "saf_base_url": settings.saf_base_url,
            "saf_login_port": settings.saf_login_port,
            "saf_api_port": settings.saf_api_port,
            "api_host": settings.api_host,
            "api_port": settings.api_port,
            "debug": settings.debug,
            "log_level": settings.log_level,
            "has_credentials": settings.has_credentials,
        }
    )


# ========== 主程式入口 ==========

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
