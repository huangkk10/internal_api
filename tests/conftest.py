"""
Pytest 共用 Fixtures

提供測試中常用的 fixtures
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.config import Settings, get_settings


# ========== Settings Fixtures ==========

@pytest.fixture
def test_settings() -> Settings:
    """測試用設定"""
    return Settings(
        saf_base_url="https://saf.test.com",
        saf_login_port=8000,
        saf_api_port=3004,
        saf_username="test_user",
        saf_password="test_password",
        debug=True,
        log_level="DEBUG",
    )


@pytest.fixture
def override_settings(test_settings):
    """覆蓋應用程式設定"""
    app.dependency_overrides[get_settings] = lambda: test_settings
    yield test_settings
    app.dependency_overrides.clear()


# ========== Client Fixtures ==========

@pytest.fixture
def client(override_settings) -> TestClient:
    """同步測試客戶端"""
    return TestClient(app)


# ========== Mock Response Fixtures ==========

@pytest.fixture
def mock_saf_login_response():
    """模擬 SAF 登入回應"""
    return {
        "id": 150,
        "name": "test_user",
        "mail": "test_user@siliconmotion.com"
    }


@pytest.fixture
def mock_saf_projects_response():
    """模擬 SAF 專案列表回應"""
    return {
        "page": 1,
        "size": 50,
        "total": 2,
        "data": [
            {
                "key": "project-1",
                "projectUid": "uid-1",
                "projectId": "proj-001",
                "projectName": "Test Project 1",
                "productCategory": "Client_PCIe",
                "customer": "Customer A",
                "controller": "SM2508",
                "subVersion": "AC",
                "nand": "Micron B58R TLC",
                "fw": "FWY1027A",
                "pl": "test.user",
                "status": 0,
                "visible": True,
                "taskId": "SVDFWV-12345",
            },
            {
                "key": "project-2",
                "projectUid": "uid-2",
                "projectId": "proj-002",
                "projectName": "Test Project 2",
                "productCategory": "Client_PCIe",
                "customer": "Customer B",
                "controller": "SM2269XT",
                "subVersion": "AB",
                "nand": "SanDisk BiCS5 TLC",
                "fw": "FWY1015A",
                "pl": "another.user",
                "status": 0,
                "visible": True,
                "taskId": "SVDFWV-12346",
                "children": [
                    {
                        "key": "project-2-1",
                        "projectUid": "uid-2-1",
                        "projectId": "proj-002",
                        "projectName": "Test Project 2",
                        "customer": "Customer B",
                        "controller": "SM2269XT",
                        "status": 0,
                        "visible": True,
                    }
                ]
            }
        ]
    }


@pytest.fixture
def mock_httpx_response():
    """模擬 httpx Response"""
    def _create_response(status_code: int, json_data: dict):
        response = AsyncMock()
        response.status_code = status_code
        response.json.return_value = json_data
        return response
    return _create_response


@pytest.fixture
def auth_headers():
    """認證用的 Headers"""
    return {
        "Authorization": "150",
        "Authorization-Name": "test_user"
    }


@pytest.fixture
def mock_project_test_summary_response():
    """模擬 SAF 專案測試摘要回應"""
    return {
        "key": "test-project-uid-001",
        "projectName": "Test Project Name",
        "testResultByMainCategory": [
            {
                "mainCategory": "Compatibility",
                "testResultByCapacity": [
                    {"capacity": "512GB", "result": "8/0/0/0/0"},
                    {"capacity": "1024GB", "result": "10/1/0/0/0"},
                ]
            },
            {
                "mainCategory": "Function",
                "testResultByCapacity": [
                    {"capacity": "512GB", "result": "15/2/1/0/0"},
                    {"capacity": "1024GB", "result": "20/0/0/0/0"},
                ]
            },
            {
                "mainCategory": "Performance",
                "testResultByCapacity": [
                    {"capacity": "512GB", "result": "5/0/0/0/0"},
                    {"capacity": "1024GB", "result": "6/0/1/0/0"},
                ]
            }
        ]
    }


@pytest.fixture
def mock_fws_by_project_id_response():
    """模擬 SAF Firmware 列表回應"""
    return {
        "fws": [
            {
                "fw": "MASTX9KA",
                "subVersion": "AA",
                "projectUid": "5d5b7d9763fb45bda79579f85a9a02f5"
            },
            {
                "fw": "G200X9R1",
                "subVersion": "AA",
                "projectUid": "52fbea8419254b6b8f7a0e361e73ec03"
            },
            {
                "fw": "BRCHX9QA",
                "subVersion": "AA",
                "projectUid": "143f42edb154413ca3b8c57db15f554a"
            }
        ]
    }
