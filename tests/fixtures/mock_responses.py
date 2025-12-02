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
