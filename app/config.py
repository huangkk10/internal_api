"""
應用程式設定模組

使用 Pydantic Settings 管理環境變數和設定
"""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    應用程式設定
    
    優先順序: 環境變數 > .env 檔案 > 預設值
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # ========== SAF 連線設定 ==========
    saf_base_url: str = Field(
        default="https://saf.siliconmotion.com.tw",
        description="SAF 網站基礎 URL"
    )
    saf_login_port: int = Field(
        default=8000,
        description="SAF 登入 API Port"
    )
    saf_api_port: int = Field(
        default=3004,
        description="SAF 資料 API Port"
    )
    
    # ========== SAF 認證資訊 ==========
    saf_username: Optional[str] = Field(
        default=None,
        description="SAF 登入帳號"
    )
    saf_password: Optional[str] = Field(
        default=None,
        description="SAF 登入密碼"
    )
    
    # ========== API Server 設定 ==========
    api_host: str = Field(
        default="0.0.0.0",
        description="API Server 監聽 Host"
    )
    api_port: int = Field(
        default=8080,
        description="API Server 監聽 Port"
    )
    debug: bool = Field(
        default=False,
        description="是否開啟除錯模式"
    )
    
    # ========== 日誌設定 ==========
    log_level: str = Field(
        default="INFO",
        description="日誌等級 (DEBUG, INFO, WARNING, ERROR)"
    )
    
    # ========== 計算屬性 ==========
    @property
    def saf_login_url(self) -> str:
        """SAF 登入 API 完整 URL"""
        return f"{self.saf_base_url}:{self.saf_login_port}/api/login"
    
    @property
    def saf_api_base_url(self) -> str:
        """SAF 資料 API 基礎 URL"""
        return f"{self.saf_base_url}:{self.saf_api_port}/api"
    
    @property
    def has_credentials(self) -> bool:
        """是否已設定認證資訊"""
        return bool(self.saf_username and self.saf_password)


@lru_cache()
def get_settings() -> Settings:
    """
    取得應用程式設定 (單例模式)
    
    使用 lru_cache 確保只建立一次 Settings 實例
    """
    return Settings()


# 方便直接 import 使用
settings = get_settings()
