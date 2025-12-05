"""
測試專案 API
"""

import pytest
from unittest.mock import patch, AsyncMock

from tests.fixtures.mock_responses import (
    PROJECTS_RESPONSE, 
    EMPTY_PROJECTS_RESPONSE,
    PROJECT_TEST_SUMMARY_RESPONSE,
    EMPTY_PROJECT_TEST_SUMMARY_RESPONSE
)
from lib.exceptions import SAFAPIError, SAFConnectionError


class TestProjectsEndpoint:
    """測試專案端點"""
    
    @patch("app.routers.projects.SAFClient")
    def test_get_projects_success(self, mock_client_class, client, auth_headers):
        """測試取得專案列表成功"""
        mock_instance = AsyncMock()
        mock_instance.get_all_projects.return_value = PROJECTS_RESPONSE
        mock_client_class.return_value = mock_instance
        
        response = client.get(
            "/api/v1/projects",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total"] == 642
    
    def test_get_projects_unauthorized(self, client):
        """測試未授權存取"""
        response = client.get("/api/v1/projects")
        
        assert response.status_code == 401
        data = response.json()
        assert "Missing authorization" in data["detail"]["message"]
    
    def test_get_projects_invalid_auth(self, client):
        """測試無效的授權"""
        response = client.get(
            "/api/v1/projects",
            headers={
                "Authorization": "not_a_number",
                "Authorization-Name": "test_user"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid Authorization" in data["detail"]["message"]
    
    @patch("app.routers.projects.SAFClient")
    def test_get_projects_with_pagination(self, mock_client_class, client, auth_headers):
        """測試帶分頁的專案列表"""
        mock_instance = AsyncMock()
        mock_instance.get_all_projects.return_value = PROJECTS_RESPONSE
        mock_client_class.return_value = mock_instance
        
        response = client.get(
            "/api/v1/projects?page=2&size=20",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # 驗證 SAF Client 被正確呼叫
        mock_instance.get_all_projects.assert_called_once()
        call_kwargs = mock_instance.get_all_projects.call_args[1]
        assert call_kwargs["page"] == 2
        assert call_kwargs["size"] == 20


class TestProjectsSummaryEndpoint:
    """測試專案摘要端點"""
    
    @patch("app.routers.projects.SAFClient")
    def test_get_summary_success(self, mock_client_class, client, auth_headers):
        """測試取得專案摘要成功"""
        mock_instance = AsyncMock()
        mock_instance.get_all_projects.return_value = PROJECTS_RESPONSE
        mock_client_class.return_value = mock_instance
        
        response = client.get(
            "/api/v1/projects/summary",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "total" in data["data"]
        assert "by_customer" in data["data"]
        assert "by_controller" in data["data"]
    
    @patch("app.routers.projects.SAFClient")
    def test_get_summary_empty(self, mock_client_class, client, auth_headers):
        """測試空專案列表的摘要"""
        mock_instance = AsyncMock()
        mock_instance.get_all_projects.return_value = EMPTY_PROJECTS_RESPONSE
        mock_client_class.return_value = mock_instance
        
        response = client.get(
            "/api/v1/projects/summary",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] == 0
        assert data["data"]["by_customer"] == {}
        assert data["data"]["by_controller"] == {}


class TestProjectTestSummaryEndpoint:
    """測試專案測試摘要端點"""
    
    @patch("app.routers.projects.SAFClient")
    def test_get_test_summary_success(self, mock_client_class, client, auth_headers):
        """測試取得專案測試摘要成功"""
        mock_instance = AsyncMock()
        mock_instance.get_project_test_summary.return_value = PROJECT_TEST_SUMMARY_RESPONSE
        mock_client_class.return_value = mock_instance
        
        response = client.get(
            "/api/v1/projects/test-project-uid-001/test-summary",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["project_uid"] == "test-project-uid-001"
        assert data["data"]["project_name"] == "Test_Project_Name"
        assert "512GB" in data["data"]["capacities"]
        assert "1024GB" in data["data"]["capacities"]
        assert len(data["data"]["categories"]) == 3
    
    @patch("app.routers.projects.SAFClient")
    def test_get_test_summary_includes_summary_stats(self, mock_client_class, client, auth_headers):
        """測試測試摘要包含統計資料"""
        mock_instance = AsyncMock()
        mock_instance.get_project_test_summary.return_value = PROJECT_TEST_SUMMARY_RESPONSE
        mock_client_class.return_value = mock_instance
        
        response = client.get(
            "/api/v1/projects/test-project-uid-001/test-summary",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        summary = data["data"]["summary"]
        
        assert "total_pass" in summary
        assert "total_fail" in summary
        assert "total_ongoing" in summary
        assert "overall_total" in summary
        assert "overall_pass_rate" in summary
    
    @patch("app.routers.projects.SAFClient")
    def test_get_test_summary_empty_project(self, mock_client_class, client, auth_headers):
        """測試空專案的測試摘要"""
        mock_instance = AsyncMock()
        mock_instance.get_project_test_summary.return_value = EMPTY_PROJECT_TEST_SUMMARY_RESPONSE
        mock_client_class.return_value = mock_instance
        
        response = client.get(
            "/api/v1/projects/empty-project-uid/test-summary",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["categories"] == []
        assert data["data"]["summary"]["overall_total"] == 0
    
    def test_get_test_summary_unauthorized(self, client):
        """測試未授權存取"""
        response = client.get("/api/v1/projects/some-uid/test-summary")
        
        assert response.status_code == 401
    
    @patch("app.routers.projects.SAFClient")
    def test_get_test_summary_project_not_found(self, mock_client_class, client, auth_headers):
        """測試專案不存在"""
        mock_instance = AsyncMock()
        mock_instance.get_project_test_summary.side_effect = SAFAPIError(
            "Project not found",
            status_code=404,
            error_code="PROJECT_NOT_FOUND"
        )
        mock_client_class.return_value = mock_instance
        
        response = client.get(
            "/api/v1/projects/non-existent-uid/test-summary",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    @patch("app.routers.projects.SAFClient")
    def test_get_test_summary_connection_error(self, mock_client_class, client, auth_headers):
        """測試連線錯誤"""
        mock_instance = AsyncMock()
        mock_instance.get_project_test_summary.side_effect = SAFConnectionError(
            "Connection failed"
        )
        mock_client_class.return_value = mock_instance
        
        response = client.get(
            "/api/v1/projects/some-uid/test-summary",
            headers=auth_headers
        )
        
        assert response.status_code == 503
