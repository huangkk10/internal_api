"""
測試專案相關功能
"""

import pytest

from app.routers.projects import _parse_result_string, _transform_test_summary


class TestParseResultString:
    """測試結果字串解析"""
    
    def test_parse_normal_result(self):
        """測試解析正常結果"""
        result = _parse_result_string("8/1/2/0/1")
        assert result == {
            "pass": 8, "fail": 1, "ongoing": 2, "cancel": 0, "check": 1
        }
    
    def test_parse_all_zeros(self):
        """測試解析全零結果"""
        result = _parse_result_string("0/0/0/0/0")
        assert result == {
            "pass": 0, "fail": 0, "ongoing": 0, "cancel": 0, "check": 0
        }
    
    def test_parse_all_pass(self):
        """測試解析全通過結果"""
        result = _parse_result_string("100/0/0/0/0")
        assert result == {
            "pass": 100, "fail": 0, "ongoing": 0, "cancel": 0, "check": 0
        }
    
    def test_parse_invalid_format(self):
        """測試解析無效格式"""
        result = _parse_result_string("invalid")
        assert result == {
            "pass": 0, "fail": 0, "ongoing": 0, "cancel": 0, "check": 0
        }
    
    def test_parse_incomplete_format(self):
        """測試解析不完整格式"""
        result = _parse_result_string("1/2/3")
        assert result == {
            "pass": 0, "fail": 0, "ongoing": 0, "cancel": 0, "check": 0
        }
    
    def test_parse_empty_string(self):
        """測試解析空字串"""
        result = _parse_result_string("")
        assert result == {
            "pass": 0, "fail": 0, "ongoing": 0, "cancel": 0, "check": 0
        }


class TestTransformTestSummary:
    """測試資料轉換 (使用實際 SAF API 結構)"""
    
    @pytest.fixture
    def sample_raw_data(self):
        """範例原始資料 (SAF API 實際回傳結構)"""
        return {
            "projectId": "proj-001",
            "projectName": "Test Project",
            "fws": [
                {
                    "projectUid": "test-uid-001",
                    "fwName": "FW_V1",
                    "plans": [
                        {
                            "testPlanName": "Test Plan",
                            "categoryItems": [
                                {
                                    "categoryName": "Compatibility",
                                    "totalTestItems": 2,
                                    "sizeResult": [
                                        {"size": "512GB", "result": "8/0/0/0/0"},
                                        {"size": "1024GB", "result": "10/2/0/0/0"},
                                    ],
                                    "total": "18/2/0/0/0"
                                },
                                {
                                    "categoryName": "Function",
                                    "totalTestItems": 3,
                                    "sizeResult": [
                                        {"size": "512GB", "result": "15/1/0/0/0"},
                                        {"size": "1024GB", "result": "20/0/0/0/0"},
                                    ],
                                    "total": "35/1/0/0/0"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    
    def test_transform_basic(self, sample_raw_data):
        """測試基本轉換"""
        result = _transform_test_summary(sample_raw_data)
        
        assert result["project_uid"] == "test-uid-001"
        assert result["project_name"] == "Test Project"
        assert "512GB" in result["capacities"]
        assert "1024GB" in result["capacities"]
        assert len(result["categories"]) == 2
    
    def test_transform_capacities_sorted(self, sample_raw_data):
        """測試容量排序"""
        result = _transform_test_summary(sample_raw_data)
        
        # 512GB 應該在 1024GB 之前
        capacities = result["capacities"]
        assert capacities.index("512GB") < capacities.index("1024GB")
    
    def test_transform_calculates_category_totals(self, sample_raw_data):
        """測試計算類別總計"""
        result = _transform_test_summary(sample_raw_data)
        
        # Compatibility: 8+10=18 pass, 0+2=2 fail
        compat_cat = next(c for c in result["categories"] if c["name"] == "Compatibility")
        assert compat_cat["total"]["pass"] == 18
        assert compat_cat["total"]["fail"] == 2
        assert compat_cat["total"]["total"] == 20
    
    def test_transform_calculates_overall_summary(self, sample_raw_data):
        """測試計算總體摘要"""
        result = _transform_test_summary(sample_raw_data)
        
        summary = result["summary"]
        # Compatibility: 18 pass, 2 fail = 20
        # Function: 35 pass, 1 fail = 36
        # Total: 53 pass, 3 fail = 56
        assert summary["total_pass"] == 53
        assert summary["total_fail"] == 3
        assert summary["overall_total"] == 56
    
    def test_transform_calculates_pass_rate(self, sample_raw_data):
        """測試計算通過率"""
        result = _transform_test_summary(sample_raw_data)
        
        summary = result["summary"]
        # 53 / 56 * 100 = 94.64...
        expected_rate = round(53 / 56 * 100, 2)
        assert summary["overall_pass_rate"] == expected_rate
    
    def test_transform_empty_fws(self):
        """測試空 fws 資料"""
        raw_data = {
            "projectId": "empty-proj",
            "projectName": "Empty Project",
            "fws": []
        }
        
        result = _transform_test_summary(raw_data)
        
        assert result["project_uid"] == ""
        assert result["project_name"] == "Empty Project"
        assert result["capacities"] == []
        assert result["categories"] == []
        assert result["summary"]["overall_total"] == 0
        assert result["summary"]["overall_pass_rate"] == 0.0
    
    def test_transform_empty_plans(self):
        """測試空 plans 資料"""
        raw_data = {
            "projectId": "proj",
            "projectName": "Project",
            "fws": [
                {
                    "projectUid": "uid-001",
                    "fwName": "FW",
                    "plans": []
                }
            ]
        }
        
        result = _transform_test_summary(raw_data)
        
        assert result["project_uid"] == "uid-001"
        assert result["project_name"] == "Project"
        assert result["capacities"] == []
        assert result["categories"] == []
        assert result["summary"]["overall_total"] == 0
    
    def test_transform_capacity_with_tb(self):
        """測試 TB 容量排序"""
        raw_data = {
            "projectId": "proj",
            "projectName": "Project",
            "fws": [
                {
                    "projectUid": "uid",
                    "fwName": "FW",
                    "plans": [
                        {
                            "testPlanName": "Plan",
                            "categoryItems": [
                                {
                                    "categoryName": "Test",
                                    "totalTestItems": 3,
                                    "sizeResult": [
                                        {"size": "1TB", "result": "1/0/0/0/0"},
                                        {"size": "512GB", "result": "1/0/0/0/0"},
                                        {"size": "2TB", "result": "1/0/0/0/0"},
                                    ],
                                    "total": "3/0/0/0/0"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = _transform_test_summary(raw_data)
        capacities = result["capacities"]
        
        # 512GB < 1TB < 2TB
        assert capacities.index("512GB") < capacities.index("1TB")
        assert capacities.index("1TB") < capacities.index("2TB")
    
    def test_transform_multiple_items_same_category(self):
        """測試同一類別多個項目累加"""
        raw_data = {
            "projectId": "proj",
            "projectName": "Project",
            "fws": [
                {
                    "projectUid": "uid",
                    "fwName": "FW",
                    "plans": [
                        {
                            "testPlanName": "Plan",
                            "categoryItems": [
                                {
                                    "categoryName": "Same Category",
                                    "totalTestItems": 1,
                                    "sizeResult": [
                                        {"size": "512GB", "result": "5/0/0/0/0"},
                                    ],
                                    "total": "5/0/0/0/0"
                                },
                                {
                                    "categoryName": "Same Category",
                                    "totalTestItems": 1,
                                    "sizeResult": [
                                        {"size": "512GB", "result": "3/2/0/0/0"},
                                    ],
                                    "total": "3/2/0/0/0"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = _transform_test_summary(raw_data)
        
        # 應該只有一個類別，且結果累加
        assert len(result["categories"]) == 1
        cat = result["categories"][0]
        assert cat["name"] == "Same Category"
        assert cat["results_by_capacity"]["512GB"]["pass"] == 8  # 5 + 3
        assert cat["results_by_capacity"]["512GB"]["fail"] == 2  # 0 + 2
        assert cat["total"]["pass"] == 8
        assert cat["total"]["fail"] == 2


class TestResultByCapacity:
    """測試各容量結果計算"""
    
    def test_capacity_result_includes_all_fields(self):
        """測試容量結果包含所有欄位"""
        raw_data = {
            "projectId": "proj",
            "projectName": "Project",
            "fws": [
                {
                    "projectUid": "uid",
                    "fwName": "FW",
                    "plans": [
                        {
                            "testPlanName": "Plan",
                            "categoryItems": [
                                {
                                    "categoryName": "Test",
                                    "totalTestItems": 1,
                                    "sizeResult": [
                                        {"size": "512GB", "result": "8/2/1/0/1"},
                                    ],
                                    "total": "8/2/1/0/1"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = _transform_test_summary(raw_data)
        cap_result = result["categories"][0]["results_by_capacity"]["512GB"]
        
        assert cap_result["pass"] == 8
        assert cap_result["fail"] == 2
        assert cap_result["ongoing"] == 1
        assert cap_result["cancel"] == 0
        assert cap_result["check"] == 1
        assert cap_result["total"] == 12
        assert cap_result["pass_rate"] == round(8/12*100, 2)
