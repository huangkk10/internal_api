"""
測試共用函式庫
"""

import pytest
from datetime import datetime, timezone

from lib.exceptions import (
    InternalAPIException,
    SAFConnectionError,
    SAFAuthenticationError,
    SAFAPIError,
)
from lib.utils import (
    format_response,
    timestamp_to_datetime,
    flatten_projects,
    safe_get,
    truncate_string,
)


class TestExceptions:
    """測試自定義例外"""
    
    def test_internal_api_exception(self):
        """測試基礎例外"""
        exc = InternalAPIException("Test error", "TEST_CODE")
        assert exc.message == "Test error"
        assert exc.code == "TEST_CODE"
        assert str(exc) == "Test error"
    
    def test_saf_connection_error(self):
        """測試連線錯誤"""
        exc = SAFConnectionError("Connection failed")
        assert exc.code == "SAF_CONNECTION_ERROR"
        assert "Connection failed" in exc.message
    
    def test_saf_authentication_error(self):
        """測試認證錯誤"""
        exc = SAFAuthenticationError()
        assert exc.code == "SAF_AUTH_ERROR"
    
    def test_saf_api_error(self):
        """測試 API 錯誤"""
        exc = SAFAPIError("API call failed", status_code=500)
        assert exc.code == "SAF_API_ERROR"
        assert exc.status_code == 500


class TestUtils:
    """測試工具函數"""
    
    def test_format_response_success(self):
        """測試成功回應格式"""
        response = format_response(success=True, data={"key": "value"})
        
        assert response["success"] is True
        assert response["data"] == {"key": "value"}
        assert response["message"] is None
        assert "timestamp" in response
    
    def test_format_response_error(self):
        """測試錯誤回應格式"""
        response = format_response(
            success=False,
            message="Error occurred",
            error_code="ERR_001"
        )
        
        assert response["success"] is False
        assert response["message"] == "Error occurred"
        assert response["error_code"] == "ERR_001"
    
    def test_timestamp_to_datetime_valid(self):
        """測試有效的 timestamp 轉換"""
        ts = {
            "seconds": {
                "low": 1763563286,
                "high": 0,
                "unsigned": False
            }
        }
        result = timestamp_to_datetime(ts)
        
        assert result is not None
        assert isinstance(result, datetime)
    
    def test_timestamp_to_datetime_none(self):
        """測試空值"""
        result = timestamp_to_datetime(None)
        assert result is None
    
    def test_timestamp_to_datetime_invalid(self):
        """測試無效格式 - 缺少 seconds 會返回 epoch 時間"""
        result = timestamp_to_datetime({"invalid": "data"})
        # 缺少 seconds 時，會得到 timestamp=0，即 epoch 時間
        assert result == datetime(1970, 1, 1, 0, 0, tzinfo=timezone.utc)
    
    def test_flatten_projects_simple(self):
        """測試展平簡單專案列表"""
        projects = [
            {"key": "1", "name": "Project 1"},
            {"key": "2", "name": "Project 2"},
        ]
        result = flatten_projects(projects)
        
        assert len(result) == 2
    
    def test_flatten_projects_with_children(self):
        """測試展平包含子專案的列表"""
        projects = [
            {
                "key": "1",
                "name": "Project 1",
                "children": [
                    {"key": "1-1", "name": "Child 1"},
                    {"key": "1-2", "name": "Child 2"},
                ]
            },
        ]
        result = flatten_projects(projects)
        
        assert len(result) == 3
        assert result[0]["key"] == "1"
        assert result[1]["key"] == "1-1"
        assert result[2]["key"] == "1-2"
    
    def test_safe_get_simple(self):
        """測試簡單取值"""
        data = {"a": 1}
        assert safe_get(data, "a") == 1
    
    def test_safe_get_nested(self):
        """測試巢狀取值"""
        data = {"a": {"b": {"c": 1}}}
        assert safe_get(data, "a", "b", "c") == 1
    
    def test_safe_get_missing(self):
        """測試缺失的鍵"""
        data = {"a": 1}
        assert safe_get(data, "b") is None
        assert safe_get(data, "b", default="default") == "default"
    
    def test_truncate_string_short(self):
        """測試短字串不截斷"""
        result = truncate_string("hello", max_length=10)
        assert result == "hello"
    
    def test_truncate_string_long(self):
        """測試長字串截斷"""
        result = truncate_string("hello world", max_length=8)
        assert result == "hello..."
        assert len(result) == 8
