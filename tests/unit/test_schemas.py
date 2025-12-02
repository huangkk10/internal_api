"""
測試 Pydantic Schemas
"""

import pytest
from datetime import datetime

from app.models.schemas import (
    LoginRequest,
    LoginResponse,
    AuthInfo,
    Project,
    ProjectListResponse,
    APIResponse,
    HealthResponse,
)


class TestLoginSchemas:
    """測試登入相關 Schemas"""
    
    def test_login_request_valid(self):
        """測試有效的登入請求"""
        request = LoginRequest(username="test_user", password="test_pass")
        assert request.username == "test_user"
        assert request.password == "test_pass"
    
    def test_login_request_missing_fields(self):
        """測試缺少必要欄位"""
        with pytest.raises(ValueError):
            LoginRequest(username="test_user")
    
    def test_login_response(self):
        """測試登入回應"""
        response = LoginResponse(id=150, name="test", mail="test@test.com")
        assert response.id == 150
        assert response.name == "test"
        assert response.mail == "test@test.com"
    
    def test_auth_info(self):
        """測試認證資訊"""
        auth = AuthInfo(user_id=150, username="test_user")
        assert auth.user_id == 150
        assert auth.username == "test_user"


class TestProjectSchemas:
    """測試專案相關 Schemas"""
    
    def test_project_minimal(self):
        """測試最小專案資料"""
        project = Project(
            key="test-key",
            projectUid="test-uid",
            projectId="test-id",
            projectName="Test Project"
        )
        assert project.key == "test-key"
        assert project.projectUid == "test-uid"
        assert project.projectId == "test-id"
        assert project.projectName == "Test Project"
    
    def test_project_full(self):
        """測試完整專案資料"""
        project = Project(
            key="test-key",
            projectUid="test-uid",
            projectId="test-id",
            projectName="Test Project",
            productCategory="Client_PCIe",
            customer="ADATA",
            controller="SM2508",
            subVersion="AC",
            nand="Micron B58R TLC",
            fw="FWY1027A",
            pl="test.user",
            status=0,
            visible=True,
            taskId="SVDFWV-12345",
            nasLogFolder="SVD_6Y"
        )
        assert project.customer == "ADATA"
        assert project.controller == "SM2508"
        assert project.taskId == "SVDFWV-12345"
    
    def test_project_with_children(self):
        """測試包含子專案的專案"""
        child = Project(
            key="child-key",
            projectUid="child-uid",
            projectId="parent-id",
            projectName="Child Project"
        )
        parent = Project(
            key="parent-key",
            projectUid="parent-uid",
            projectId="parent-id",
            projectName="Parent Project",
            children=[child]
        )
        assert len(parent.children) == 1
        assert parent.children[0].key == "child-key"
    
    def test_project_list_response(self):
        """測試專案列表回應"""
        response = ProjectListResponse(
            data=[],
            page=1,
            size=50,
            total=100
        )
        assert response.page == 1
        assert response.size == 50
        assert response.total == 100


class TestAPIResponse:
    """測試通用 API 回應"""
    
    def test_success_response(self):
        """測試成功回應"""
        response = APIResponse(
            success=True,
            data={"key": "value"}
        )
        assert response.success is True
        assert response.data == {"key": "value"}
        assert response.message is None
    
    def test_error_response(self):
        """測試錯誤回應"""
        response = APIResponse(
            success=False,
            message="Error occurred",
            error_code="ERR_001"
        )
        assert response.success is False
        assert response.message == "Error occurred"
        assert response.error_code == "ERR_001"
    
    def test_response_has_timestamp(self):
        """測試回應包含時間戳記"""
        response = APIResponse(success=True)
        assert response.timestamp is not None
        assert isinstance(response.timestamp, datetime)


class TestHealthResponse:
    """測試健康檢查回應"""
    
    def test_health_response(self):
        """測試健康檢查回應"""
        response = HealthResponse(status="healthy", version="0.1.0")
        assert response.status == "healthy"
        assert response.version == "0.1.0"
        assert response.timestamp is not None
