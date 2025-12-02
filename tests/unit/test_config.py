"""
測試設定模組
"""

import pytest
from app.config import Settings


class TestSettings:
    """測試 Settings 類別"""
    
    def test_default_values(self):
        """測試預設值"""
        settings = Settings(
            _env_file=None  # 不讀取 .env 檔案
        )
        assert settings.saf_base_url == "https://saf.siliconmotion.com.tw"
        assert settings.saf_login_port == 8000
        assert settings.saf_api_port == 3004
        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 8080
        assert settings.debug is False
        assert settings.log_level == "INFO"
    
    def test_custom_values(self):
        """測試自訂值"""
        settings = Settings(
            saf_base_url="https://custom.url.com",
            saf_login_port=9000,
            saf_api_port=9001,
            saf_username="custom_user",
            saf_password="custom_pass",
            api_port=3000,
            debug=True,
            _env_file=None
        )
        assert settings.saf_base_url == "https://custom.url.com"
        assert settings.saf_login_port == 9000
        assert settings.saf_api_port == 9001
        assert settings.saf_username == "custom_user"
        assert settings.saf_password == "custom_pass"
        assert settings.api_port == 3000
        assert settings.debug is True
    
    def test_saf_login_url_property(self):
        """測試登入 URL 計算屬性"""
        settings = Settings(
            saf_base_url="https://test.com",
            saf_login_port=9000,
            _env_file=None
        )
        assert settings.saf_login_url == "https://test.com:9000/api/login"
    
    def test_saf_api_base_url_property(self):
        """測試 API 基礎 URL 計算屬性"""
        settings = Settings(
            saf_base_url="https://test.com",
            saf_api_port=9001,
            _env_file=None
        )
        assert settings.saf_api_base_url == "https://test.com:9001/api"
    
    def test_has_credentials_true(self):
        """測試有認證資訊"""
        settings = Settings(
            saf_username="user",
            saf_password="pass",
            _env_file=None
        )
        assert settings.has_credentials is True
    
    def test_has_credentials_false_no_username(self):
        """測試無帳號"""
        settings = Settings(
            saf_username=None,
            saf_password="pass",
            _env_file=None
        )
        assert settings.has_credentials is False
    
    def test_has_credentials_false_no_password(self):
        """測試無密碼"""
        settings = Settings(
            saf_username="user",
            saf_password=None,
            _env_file=None
        )
        assert settings.has_credentials is False
    
    def test_has_credentials_false_empty(self):
        """測試空值"""
        settings = Settings(
            saf_username="",
            saf_password="",
            _env_file=None
        )
        assert settings.has_credentials is False
