"""
測試用模擬回應資料
"""


# SAF 登入回應
LOGIN_SUCCESS_RESPONSE = {
    "id": 150,
    "name": "Chunwei.Huang",
    "mail": "Chunwei.Huang@siliconmotion.com"
}

LOGIN_FAILED_RESPONSE = {
    "error": "Invalid credentials"
}


# SAF 專案列表回應
PROJECTS_RESPONSE = {
    "page": 1,
    "size": 50,
    "total": 642,
    "data": [
        {
            "key": "abc123",
            "projectUid": "abc123",
            "projectId": "proj-001",
            "projectName": "Channel",
            "productCategory": "Client_PCIe",
            "customer": "ADATA",
            "controller": "SM2268XT2",
            "subVersion": "AA",
            "nand": "Solidigm N38E QLC",
            "fw": "PKGY1118A_FWY1118A",
            "pl": "stanley.kuan",
            "visible": True,
            "status": 0,
            "createdBy": "stanley.kuan",
            "createdAt": {
                "seconds": {
                    "low": 1763563286,
                    "high": 0,
                    "unsigned": False
                }
            },
            "updatedBy": "stanley.kuan",
            "updatedAt": {
                "seconds": {
                    "low": 1764599539,
                    "high": 0,
                    "unsigned": False
                }
            },
            "taskId": "SVDFWV-54702",
            "nasLogFolder": "SVD_6Y",
            "children": []
        },
        {
            "key": "def456",
            "projectUid": "def456",
            "projectId": "proj-002",
            "projectName": "Channel",
            "productCategory": "Client_PCIe",
            "customer": "SSK",
            "controller": "SM2508",
            "subVersion": "AC",
            "nand": "Micron B58R TLC",
            "fw": "FWY1027A_PKGY1027V1",
            "pl": "daniel.kuo",
            "visible": True,
            "status": 0,
            "taskId": "SVDFWV-53363",
            "children": [
                {
                    "key": "def456-child",
                    "projectUid": "def456-child",
                    "projectId": "proj-002",
                    "projectName": "Channel",
                    "customer": "SSK",
                    "controller": "SM2508",
                    "status": 0,
                    "visible": True,
                }
            ]
        }
    ]
}


# 空的專案列表回應
EMPTY_PROJECTS_RESPONSE = {
    "page": 1,
    "size": 50,
    "total": 0,
    "data": []
}


# SAF 專案測試摘要回應 (實際 SAF API 結構)
PROJECT_TEST_SUMMARY_RESPONSE = {
    "projectId": "proj-001",
    "projectName": "Test_Project_Name",
    "fws": [
        {
            "projectUid": "test-project-uid-001",
            "fwName": "FW_Version_1",
            "subVersionName": "AA",
            "internalSummary_1": {
                "name": "[TEST-001][Test][Project][AA]",
                "sampleUsedRate": "50%",
                "totalTestItems": 10,
                "passedCnt": 8,
                "failedCnt": 2,
                "completionRate": "100%"
            },
            "plans": [
                {
                    "testPlanName": "Test_Plan_1",
                    "categoryItems": [
                        {
                            "categoryName": "Compatibility",
                            "totalTestItems": 2,
                            "sizeResult": [
                                {"size": "512GB", "result": "8/0/0/0/0"},
                                {"size": "1024GB", "result": "10/1/0/0/0"}
                            ],
                            "total": "18/1/0/0/0"
                        },
                        {
                            "categoryName": "Function",
                            "totalTestItems": 3,
                            "sizeResult": [
                                {"size": "512GB", "result": "13/2/1/0/0"},
                                {"size": "1024GB", "result": "22/0/0/0/0"}
                            ],
                            "total": "35/2/1/0/0"
                        },
                        {
                            "categoryName": "Performance",
                            "totalTestItems": 2,
                            "sizeResult": [
                                {"size": "512GB", "result": "5/0/0/0/0"},
                                {"size": "1024GB", "result": "6/0/1/0/0"}
                            ],
                            "total": "11/0/1/0/0"
                        }
                    ]
                }
            ]
        }
    ]
}


# 空的專案測試摘要回應
EMPTY_PROJECT_TEST_SUMMARY_RESPONSE = {
    "projectId": "empty-proj",
    "projectName": "Empty Project",
    "fws": []
}


# SAF Firmware 列表回應 (ListFWsByProjectId)
FWS_BY_PROJECT_ID_RESPONSE = {
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
        },
        {
            "fw": "G200X9PA",
            "subVersion": "AA",
            "projectUid": "8f6bf9fbe4e14e3dbfe5c5fa70d6af2e3"
        },
        {
            "fw": "G200X9QA",
            "subVersion": "AA",
            "projectUid": "aab7e05f8458470db6511112a88529d4"
        },
        {
            "fw": "G200X9NM",
            "subVersion": "AA",
            "projectUid": "82973456eea14acc863185615b762b8c"
        }
    ]
}


# 空的 Firmware 列表回應
EMPTY_FWS_RESPONSE = {
    "fws": []
}


# SAF Firmware 詳細摘要回應 (完整的 listOneProjectSummary)
FIRMWARE_SUMMARY_RESPONSE = {
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
            },
            "plans": [
                {
                    "testPlanName": "Test_Plan_1",
                    "categoryItems": [
                        {
                            "categoryName": "Compatibility",
                            "totalTestItems": 10,
                            "sizeResult": [
                                {"size": "512GB", "result": "8/0/0/0/0"},
                                {"size": "1024GB", "result": "10/1/0/0/0"}
                            ],
                            "total": "18/1/0/0/0"
                        }
                    ]
                }
            ]
        }
    ]
}


# 空的 Firmware 詳細摘要回應
EMPTY_FIRMWARE_SUMMARY_RESPONSE = {
    "projectId": "empty-proj",
    "projectName": "Empty Project",
    "fws": []
}
