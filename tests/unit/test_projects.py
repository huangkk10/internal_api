"""
測試專案相關功能
"""

import pytest

from app.routers.projects import (
    _parse_result_string,
    _transform_test_summary,
    _parse_percentage_string,
    _parse_fraction_string,
    _transform_firmware_summary,
)


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


class TestParsePercentageString:
    """測試百分比字串解析"""
    
    def test_parse_bracket_format(self):
        """測試解析括號格式: 61/61 (100%)"""
        result = _parse_percentage_string("61/61 (100%)")
        assert result == 100.0
    
    def test_parse_simple_percentage(self):
        """測試解析簡單百分比: 0%"""
        result = _parse_percentage_string("0%")
        assert result == 0.0
    
    def test_parse_percentage_with_decimal(self):
        """測試解析帶小數的百分比: 26%"""
        result = _parse_percentage_string("26%")
        assert result == 26.0
    
    def test_parse_partial_bracket(self):
        """測試解析部分完成: 16/61 (26%)"""
        result = _parse_percentage_string("16/61 (26%)")
        assert result == 26.0
    
    def test_parse_empty_string(self):
        """測試解析空字串"""
        result = _parse_percentage_string("")
        assert result == 0.0
    
    def test_parse_none(self):
        """測試解析 None"""
        result = _parse_percentage_string(None)
        assert result == 0.0
    
    def test_parse_invalid(self):
        """測試解析無效字串"""
        result = _parse_percentage_string("invalid")
        assert result == 0.0


class TestParseFractionString:
    """測試分數字串解析"""
    
    def test_parse_fraction_with_bracket(self):
        """測試解析帶括號分數: 0/140 (0%)"""
        numerator, denominator = _parse_fraction_string("0/140 (0%)")
        assert numerator == 0
        assert denominator == 140
    
    def test_parse_simple_fraction(self):
        """測試解析簡單分數: 61/61"""
        numerator, denominator = _parse_fraction_string("61/61")
        assert numerator == 61
        assert denominator == 61
    
    def test_parse_empty_string(self):
        """測試解析空字串"""
        numerator, denominator = _parse_fraction_string("")
        assert numerator == 0
        assert denominator == 0
    
    def test_parse_none(self):
        """測試解析 None"""
        numerator, denominator = _parse_fraction_string(None)
        assert numerator == 0
        assert denominator == 0


class TestTransformFirmwareSummary:
    """測試 Firmware 詳細摘要轉換"""
    
    @pytest.fixture
    def sample_firmware_data(self):
        """範例 Firmware 詳細資料"""
        return {
            "projectId": "8e9fe3fa43694a2c8a7cef9e42620f60",
            "projectName": "Client_PCIe_Micron_Springsteen_SM2508_Micron B58R TLC",
            "fws": [
                {
                    "projectUid": "1de4830a914b42ffb92ddd201d7ca923",
                    "fwName": "G200X85A_OPAL",
                    "subVersionName": "AA",
                    "internalSummary_1": {
                        "name": "[SVDFWV-33916][Micron][Springsteen][SM2508][AA][Micron B58R TLC]",
                        "totalStmsSampleCount": 140,
                        "sampleUsedRate": "0%",
                        "totalTestItems": 61,
                        "passedCnt": 44,
                        "failedCnt": 16,
                        "completionRate": "61/61 (100%)",
                        "conditionalPassedCnt": 1
                    },
                    "internalSummary_2": {
                        "realTestCount": 61
                    },
                    "externalSummary": {
                        "totalSampleQuantity": 140,
                        "sampleUtilizationRate": "0/140 (0%)",
                        "passedCnt": 44,
                        "failedCnt": 16,
                        "sampleTestItemCompletionRate": "61/61 (100%)",
                        "sampleTestItemFailRate": "16/61 (26%)",
                        "testItemExecutionRate": "39/39 (100%)",
                        "testItemFailRate": "14/39 (36%)",
                        "conditionalPassedCnt": 1,
                        "itemPassedCnt": 25,
                        "itemFailedCnt": 14,
                        "totalItemCnt": 39
                    }
                }
            ]
        }
    
    def test_transform_basic_info(self, sample_firmware_data):
        """測試基本資訊轉換"""
        result = _transform_firmware_summary(sample_firmware_data)
        
        assert result["project_uid"] == "1de4830a914b42ffb92ddd201d7ca923"
        assert result["fw_name"] == "G200X85A_OPAL"
        assert result["sub_version"] == "AA"
        assert "[SVDFWV-33916]" in result["task_name"]
    
    def test_transform_overview_stats(self, sample_firmware_data):
        """測試總覽統計轉換"""
        result = _transform_firmware_summary(sample_firmware_data)
        overview = result["overview"]
        
        assert overview["total_test_items"] == 61
        assert overview["passed"] == 44
        assert overview["failed"] == 16
        assert overview["conditional_passed"] == 1
        assert overview["completion_rate"] == 100.0
        # pass_rate = 44 / (44+16) * 100 = 73.33
        assert overview["pass_rate"] == round(44/60*100, 2)
    
    def test_transform_sample_stats(self, sample_firmware_data):
        """測試樣本統計轉換"""
        result = _transform_firmware_summary(sample_firmware_data)
        sample_stats = result["sample_stats"]
        
        assert sample_stats["total_samples"] == 140
        assert sample_stats["samples_used"] == 0  # 0% of 140
        assert sample_stats["utilization_rate"] == 0.0
    
    def test_transform_test_item_stats(self, sample_firmware_data):
        """測試項目統計轉換"""
        result = _transform_firmware_summary(sample_firmware_data)
        test_item_stats = result["test_item_stats"]
        
        assert test_item_stats["total_items"] == 39
        assert test_item_stats["passed_items"] == 25
        assert test_item_stats["failed_items"] == 14
        assert test_item_stats["execution_rate"] == 100.0
        assert test_item_stats["fail_rate"] == 36.0
    
    def test_transform_empty_fws(self):
        """測試空 fws 資料"""
        raw_data = {
            "projectId": "empty-proj",
            "projectName": "Empty Project",
            "fws": []
        }
        
        result = _transform_firmware_summary(raw_data)
        
        assert result["project_uid"] == ""
        assert result["fw_name"] == ""
        assert result["sub_version"] == ""
        assert result["overview"]["total_test_items"] == 0
        assert result["sample_stats"]["total_samples"] == 0
        assert result["test_item_stats"]["total_items"] == 0
    
    def test_transform_with_used_samples(self):
        """測試有已使用樣本的情況"""
        raw_data = {
            "projectId": "proj",
            "projectName": "Project",
            "fws": [
                {
                    "projectUid": "uid",
                    "fwName": "FW",
                    "subVersionName": "AA",
                    "internalSummary_1": {
                        "name": "Test",
                        "totalStmsSampleCount": 100,
                        "sampleUsedRate": "50%",
                        "totalTestItems": 10,
                        "passedCnt": 8,
                        "failedCnt": 2,
                        "completionRate": "100%",
                        "conditionalPassedCnt": 0
                    },
                    "externalSummary": {
                        "totalSampleQuantity": 100,
                        "totalItemCnt": 10,
                        "itemPassedCnt": 8,
                        "itemFailedCnt": 2,
                        "testItemExecutionRate": "100%",
                        "testItemFailRate": "20%"
                    }
                }
            ]
        }
        
        result = _transform_firmware_summary(raw_data)
        
        assert result["sample_stats"]["total_samples"] == 100
        assert result["sample_stats"]["samples_used"] == 50  # 50% of 100
        assert result["sample_stats"]["utilization_rate"] == 50.0


# =============================================================================
# Phase 2: 完整專案摘要測試
# =============================================================================

from app.routers.projects import (
    _transform_firmware_detail,
    _aggregate_firmware_stats,
    _transform_full_summary,
)


class TestTransformFirmwareDetail:
    """測試 Firmware 詳細轉換"""
    
    def test_transform_basic(self):
        """測試基本轉換"""
        fw_data = {
            "projectUid": "SM2508-YMTC",
            "fwName": "FW_A",
            "subVersionName": "AA",
            "internalSummary_1": {
                "name": "TaskA",
                "totalStmsSampleCount": 100,
                "sampleUsedRate": "80%",
                "totalTestItems": 50,
                "passedCnt": 40,
                "failedCnt": 5,
                "conditionalPassedCnt": 3,
                "completionRate": "96%"
            },
            "internalSummary_2": {
                "realTestCount": 45
            },
            "externalSummary": {
                "totalSampleQuantity": 100,
                "sampleUtilizationRate": "75%",
                "passedCnt": 70,
                "failedCnt": 5,
                "sampleTestItemCompletionRate": "75%",
                "sampleTestItemFailRate": "6.67%",
                "testItemExecutionRate": "90%",
                "testItemFailRate": "10%",
                "itemPassedCnt": 45,
                "itemFailedCnt": 5,
                "totalItemCnt": 50
            }
        }
        
        result = _transform_firmware_detail(fw_data)
        
        assert result["project_uid"] == "SM2508-YMTC"
        assert result["fw_name"] == "FW_A"
        assert result["sub_version"] == "AA"
        
        # Internal summary
        internal = result["internal_summary"]
        assert internal["task_name"] == "TaskA"
        assert internal["total_samples"] == 100
        assert internal["sample_used_rate"] == 80.0
        assert internal["total_test_items"] == 50
        assert internal["passed"] == 40
        assert internal["failed"] == 5
        assert internal["conditional_passed"] == 3
        assert internal["completion_rate"] == 96.0
        assert internal["real_test_count"] == 45
        
        # External summary
        external = result["external_summary"]
        assert external["total_sample_quantity"] == 100
        assert external["sample_utilization_rate"] == 75.0
        assert external["passed"] == 70
        assert external["failed"] == 5
        assert external["sample_completion_rate"] == 75.0
        assert external["sample_fail_rate"] == 6.67
        assert external["execution_rate"] == 90.0
        assert external["item_fail_rate"] == 10.0
        assert external["item_passed"] == 45
        assert external["item_failed"] == 5
        assert external["total_items"] == 50
    
    def test_transform_empty_data(self):
        """測試空資料"""
        fw_data = {}
        
        result = _transform_firmware_detail(fw_data)
        
        assert result["project_uid"] == ""
        assert result["fw_name"] == ""
        assert result["sub_version"] == ""
        assert result["internal_summary"]["total_samples"] == 0
        assert result["external_summary"]["total_items"] == 0
    
    def test_transform_partial_data(self):
        """測試部分資料"""
        fw_data = {
            "projectUid": "TEST",
            "fwName": "FW_TEST",
            "internalSummary_1": {
                "totalStmsSampleCount": 50
            }
        }
        
        result = _transform_firmware_detail(fw_data)
        
        assert result["project_uid"] == "TEST"
        assert result["fw_name"] == "FW_TEST"
        assert result["internal_summary"]["total_samples"] == 50
        assert result["internal_summary"]["passed"] == 0


class TestAggregateFirmwareStats:
    """測試 Firmware 統計聚合"""
    
    def test_aggregate_multiple_firmwares(self):
        """測試多個 Firmware 聚合"""
        firmwares = [
            {
                "internal_summary": {
                    "total_test_items": 100,
                    "passed": 80,
                    "failed": 10,
                    "conditional_passed": 5
                }
            },
            {
                "internal_summary": {
                    "total_test_items": 50,
                    "passed": 40,
                    "failed": 5,
                    "conditional_passed": 3
                }
            }
        ]
        
        result = _aggregate_firmware_stats(firmwares)
        
        assert result["total_test_items"] == 150
        assert result["total_passed"] == 120
        assert result["total_failed"] == 15
        assert result["total_conditional_passed"] == 8
        # Pass rate: 120 / (120 + 15) = 88.89%
        assert result["overall_pass_rate"] == 88.89
    
    def test_aggregate_empty_list(self):
        """測試空列表"""
        firmwares = []
        
        result = _aggregate_firmware_stats(firmwares)
        
        assert result["total_test_items"] == 0
        assert result["total_passed"] == 0
        assert result["total_failed"] == 0
        assert result["overall_pass_rate"] == 0.0
    
    def test_aggregate_single_firmware(self):
        """測試單一 Firmware"""
        firmwares = [
            {
                "internal_summary": {
                    "total_test_items": 10,
                    "passed": 10,
                    "failed": 0,
                    "conditional_passed": 0
                }
            }
        ]
        
        result = _aggregate_firmware_stats(firmwares)
        
        assert result["total_passed"] == 10
        assert result["total_failed"] == 0
        assert result["overall_pass_rate"] == 100.0
    
    def test_aggregate_all_failed(self):
        """測試全部失敗"""
        firmwares = [
            {
                "internal_summary": {
                    "total_test_items": 10,
                    "passed": 0,
                    "failed": 10,
                    "conditional_passed": 0
                }
            }
        ]
        
        result = _aggregate_firmware_stats(firmwares)
        
        assert result["overall_pass_rate"] == 0.0


class TestTransformFullSummary:
    """測試完整專案摘要轉換"""
    
    def test_transform_basic(self):
        """測試基本轉換"""
        raw_data = {
            "projectId": "12345",
            "projectName": "TestProject",
            "fws": [
                {
                    "projectUid": "proj-uid",
                    "fwName": "FW_A",
                    "subVersionName": "AA",
                    "internalSummary_1": {
                        "name": "Task1",
                        "totalStmsSampleCount": 100,
                        "sampleUsedRate": "50%",
                        "totalTestItems": 20,
                        "passedCnt": 15,
                        "failedCnt": 3,
                        "conditionalPassedCnt": 2,
                        "completionRate": "90%"
                    },
                    "internalSummary_2": {
                        "realTestCount": 18
                    },
                    "externalSummary": {
                        "totalSampleQuantity": 100,
                        "sampleUtilizationRate": "60%",
                        "passedCnt": 50,
                        "failedCnt": 10,
                        "sampleTestItemCompletionRate": "60%",
                        "sampleTestItemFailRate": "16.67%",
                        "testItemExecutionRate": "80%",
                        "testItemFailRate": "15%",
                        "itemPassedCnt": 16,
                        "itemFailedCnt": 4,
                        "totalItemCnt": 20
                    }
                }
            ]
        }
        
        result = _transform_full_summary(raw_data)
        
        assert result["project_id"] == "12345"
        assert result["project_name"] == "TestProject"
        assert result["total_firmwares"] == 1
        assert len(result["firmwares"]) == 1
        
        # 檢查 firmware detail
        fw = result["firmwares"][0]
        assert fw["fw_name"] == "FW_A"
        assert fw["internal_summary"]["passed"] == 15
        
        # 檢查聚合統計
        stats = result["aggregated_stats"]
        assert stats["total_test_items"] == 20
        assert stats["total_passed"] == 15
        assert stats["total_failed"] == 3
    
    def test_transform_multiple_firmwares(self):
        """測試多個 Firmware"""
        raw_data = {
            "projectId": "project-1",
            "projectName": "Multi FW Project",
            "fws": [
                {
                    "fwName": "FW_1",
                    "internalSummary_1": {
                        "totalTestItems": 10,
                        "passedCnt": 8,
                        "failedCnt": 2,
                        "conditionalPassedCnt": 0
                    }
                },
                {
                    "fwName": "FW_2",
                    "internalSummary_1": {
                        "totalTestItems": 20,
                        "passedCnt": 15,
                        "failedCnt": 5,
                        "conditionalPassedCnt": 0
                    }
                }
            ]
        }
        
        result = _transform_full_summary(raw_data)
        
        assert result["total_firmwares"] == 2
        assert len(result["firmwares"]) == 2
        
        stats = result["aggregated_stats"]
        assert stats["total_test_items"] == 30
        assert stats["total_passed"] == 23
        assert stats["total_failed"] == 7
    
    def test_transform_empty_fws(self):
        """測試沒有 Firmware"""
        raw_data = {
            "projectId": "empty-proj",
            "projectName": "Empty Project",
            "fws": []
        }
        
        result = _transform_full_summary(raw_data)
        
        assert result["project_id"] == "empty-proj"
        assert result["total_firmwares"] == 0
        assert result["firmwares"] == []
        assert result["aggregated_stats"]["total_passed"] == 0