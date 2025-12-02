"""
測試 SAF Client
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from app.services.saf_client import SAFClient
from app.config import Settings
from lib.exceptions import SAFAuthenticationError, SAFConnectionError, SAFAPIError


class TestSAFClient:
    """測試 SAF Client"""
    
    @pytest.fixture
    def saf_client(self, test_settings):
        """建立測試用 SAF Client"""
        return SAFClient(test_settings)
    
    @pytest.mark.asyncio
    async def test_login_success(self, saf_client, mock_saf_login_response):
        """測試登入成功"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_saf_login_response
        
        with patch.object(httpx.AsyncClient, 'post', return_value=mock_response):
            with patch.object(httpx.AsyncClient, '__aenter__', return_value=AsyncMock(post=AsyncMock(return_value=mock_response))):
                with patch.object(httpx.AsyncClient, '__aexit__', return_value=None):
                    # 使用 patch 來模擬 _get_client
                    mock_client = AsyncMock()
                    mock_client.post.return_value = mock_response
                    mock_client.__aenter__.return_value = mock_client
                    mock_client.__aexit__.return_value = None
                    
                    with patch.object(saf_client, '_get_client', return_value=mock_client):
                        result = await saf_client.login("test_user", "test_pass")
                        
                        assert result["id"] == 150
                        assert result["name"] == "test_user"
    
    @pytest.mark.asyncio
    async def test_login_authentication_error(self, saf_client):
        """測試登入認證失敗"""
        mock_response = AsyncMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Invalid credentials"}
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        
        with patch.object(saf_client, '_get_client', return_value=mock_client):
            with pytest.raises(SAFAuthenticationError):
                await saf_client.login("wrong_user", "wrong_pass")
    
    @pytest.mark.asyncio
    async def test_get_all_projects_success(self, saf_client, mock_saf_projects_response):
        """測試取得專案列表成功"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_saf_projects_response
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        
        with patch.object(saf_client, '_get_client', return_value=mock_client):
            result = await saf_client.get_all_projects(
                user_id=150,
                username="test_user"
            )
            
            assert result["total"] == 2
            assert len(result["data"]) == 2
    
    @pytest.mark.asyncio
    async def test_login_with_config_success(self, test_settings, mock_saf_login_response):
        """測試使用設定檔登入成功"""
        client = SAFClient(test_settings)
        
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_saf_login_response
        
        mock_http_client = AsyncMock()
        mock_http_client.post.return_value = mock_response
        mock_http_client.__aenter__.return_value = mock_http_client
        mock_http_client.__aexit__.return_value = None
        
        with patch.object(client, '_get_client', return_value=mock_http_client):
            result = await client.login_with_config()
            
            assert result["id"] == 150
    
    @pytest.mark.asyncio
    async def test_login_with_config_no_credentials(self):
        """測試使用設定檔登入但未設定帳密"""
        settings = Settings(
            saf_username=None,
            saf_password=None,
            _env_file=None
        )
        client = SAFClient(settings)
        
        with pytest.raises(SAFAuthenticationError) as exc_info:
            await client.login_with_config()
        
        assert "not configured" in str(exc_info.value)
