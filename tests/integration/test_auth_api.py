"""
測試認證 API
"""

import pytest
from unittest.mock import patch, AsyncMock

from tests.fixtures.mock_responses import LOGIN_SUCCESS_RESPONSE


class TestHealthEndpoint:
    """測試健康檢查端點"""
    
    def test_health_check(self, client):
        """測試健康檢查"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data


class TestRootEndpoint:
    """測試根端點"""
    
    def test_root(self, client):
        """測試 API 首頁"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Internal API Server"
        assert "version" in data


class TestConfigEndpoint:
    """測試設定端點"""
    
    def test_get_config(self, client):
        """測試取得設定"""
        response = client.get("/config")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "saf_base_url" in data["data"]
        assert "has_credentials" in data["data"]


class TestLoginEndpoint:
    """測試登入端點"""
    
    @patch("app.routers.auth.SAFClient")
    def test_login_success(self, mock_client_class, client):
        """測試登入成功"""
        # 設定 mock
        mock_instance = AsyncMock()
        mock_instance.login.return_value = LOGIN_SUCCESS_RESPONSE
        mock_client_class.return_value = mock_instance
        
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "test_user", "password": "test_pass"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == 150
        assert data["data"]["name"] == "Chunwei.Huang"
    
    def test_login_missing_credentials(self, client):
        """測試缺少認證資訊"""
        response = client.post(
            "/api/v1/auth/login",
            json={}
        )
        
        assert response.status_code == 422  # Validation Error
    
    def test_login_missing_password(self, client):
        """測試缺少密碼"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "test_user"}
        )
        
        assert response.status_code == 422


class TestLoginWithConfigEndpoint:
    """測試使用設定檔登入端點"""
    
    @patch("app.routers.auth.SAFClient")
    def test_login_with_config_success(self, mock_client_class, client):
        """測試使用設定檔登入成功"""
        mock_instance = AsyncMock()
        mock_instance.login_with_config.return_value = LOGIN_SUCCESS_RESPONSE
        mock_client_class.return_value = mock_instance
        
        response = client.post("/api/v1/auth/login-with-config")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
