# API 使用說明

本文件說明 Internal API Server 的所有 API 端點使用方式。

## 基本資訊

- **Base URL**: `http://localhost:8080`
- **API 版本**: v1
- **API 前綴**: `/api/v1`

## 認證方式

大部分 API 需要在 Header 中提供認證資訊：

| Header | 說明 |
|--------|------|
| `Authorization` | 使用者 ID (從登入 API 取得) |
| `Authorization-Name` | 使用者名稱 |

---

## 端點列表

### 1. 健康檢查

檢查服務是否正常運行。

```
GET /health
```

**回應範例:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2025-12-02T10:00:00Z"
}
```

---

### 2. 登入

使用帳號密碼登入 SAF 系統。

```
POST /api/v1/auth/login
```

**請求 Body:**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**回應範例:**
```json
{
  "success": true,
  "data": {
    "id": 150,
    "name": "your_username",
    "mail": "your_username@siliconmotion.com"
  },
  "message": null,
  "timestamp": "2025-12-02T10:00:00Z"
}
```

**cURL 範例:**
```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

---

### 3. 使用設定檔登入

使用 `.env` 檔案中設定的帳密登入。

```
POST /api/v1/auth/login-with-config
```

**回應**: 同登入 API

**cURL 範例:**
```bash
curl -X POST http://localhost:8080/api/v1/auth/login-with-config
```

---

### 4. 取得專案列表

取得所有專案的詳細資訊。

```
GET /api/v1/projects
```

**Query 參數:**
| 參數 | 類型 | 說明 | 預設值 |
|------|------|------|--------|
| `page` | int | 頁碼 | 1 |
| `size` | int | 每頁筆數 (1-100) | 50 |

**Headers:**
- `Authorization`: 使用者 ID
- `Authorization-Name`: 使用者名稱

**回應範例:**
```json
{
  "success": true,
  "data": {
    "page": 1,
    "size": 50,
    "total": 642,
    "data": [
      {
        "key": "abc123",
        "projectUid": "abc123",
        "projectName": "Channel",
        "customer": "ADATA",
        "controller": "SM2508",
        "fw": "FWY1027A",
        "taskId": "SVDFWV-12345"
      }
    ]
  },
  "message": null,
  "timestamp": "2025-12-02T10:00:00Z"
}
```

**cURL 範例:**
```bash
curl http://localhost:8080/api/v1/projects \
  -H "Authorization: 150" \
  -H "Authorization-Name: your_username"
```

---

### 5. 取得專案統計摘要

取得專案的統計資訊。

```
GET /api/v1/projects/summary
```

**Headers:**
- `Authorization`: 使用者 ID
- `Authorization-Name`: 使用者名稱

**回應範例:**
```json
{
  "success": true,
  "data": {
    "total": 642,
    "by_customer": {
      "ADATA": 50,
      "SSK": 30,
      "Transcend": 25
    },
    "by_controller": {
      "SM2508": 100,
      "SM2269XT": 80,
      "SM2268XT2": 60
    }
  },
  "message": null,
  "timestamp": "2025-12-02T10:00:00Z"
}
```

---

### 6. 取得專案測試摘要

取得單一專案的測試結果摘要，包含各測試類別和容量的統計。

```
GET /api/v1/projects/{project_uid}/test-summary
```

**Path 參數:**
| 參數 | 類型 | 說明 |
|------|------|------|
| `project_uid` | string | 專案 UID (從專案列表取得) |

**Headers:**
- `Authorization`: 使用者 ID
- `Authorization-Name`: 使用者名稱

**回應範例:**
```json
{
  "success": true,
  "data": {
    "project_uid": "00e11fc25a3f454e9e3860ff67dd2c07",
    "project_name": "YMTC 232L TLC BIC5 B27B",
    "capacities": ["512GB", "1024GB", "2048GB", "4096GB"],
    "categories": [
      {
        "name": "Compatibility",
        "results_by_capacity": {
          "512GB": {
            "pass": 8,
            "fail": 0,
            "ongoing": 0,
            "cancel": 0,
            "check": 0,
            "total": 8,
            "pass_rate": 100.0
          },
          "1024GB": {
            "pass": 12,
            "fail": 1,
            "ongoing": 0,
            "cancel": 0,
            "check": 0,
            "total": 13,
            "pass_rate": 92.31
          }
        },
        "total": {
          "pass": 20,
          "fail": 1,
          "ongoing": 0,
          "cancel": 0,
          "check": 0,
          "total": 21,
          "pass_rate": 95.24
        }
      },
      {
        "name": "Function",
        "results_by_capacity": { "..." : "..." },
        "total": { "..." : "..." }
      }
    ],
    "summary": {
      "total_pass": 150,
      "total_fail": 2,
      "total_ongoing": 5,
      "total_cancel": 0,
      "total_check": 0,
      "overall_total": 157,
      "overall_pass_rate": 95.54
    }
  },
  "message": null,
  "timestamp": "2025-12-06T10:00:00Z"
}
```

**測試類別說明:**
| 類別 | 說明 |
|------|------|
| Compatibility | 相容性測試 |
| Function | 功能測試 |
| Performance | 效能測試 |
| Protocol | 協定測試 |
| Reliability | 可靠性測試 |
| Security | 安全性測試 |
| UNITest | 單元測試 |

**cURL 範例:**
```bash
# 先從專案列表取得 project_uid
curl http://localhost:8080/api/v1/projects \
  -H "Authorization: 150" \
  -H "Authorization-Name: your_username"

# 取得專案測試摘要
curl http://localhost:8080/api/v1/projects/00e11fc25a3f454e9e3860ff67dd2c07/test-summary \
  -H "Authorization: 150" \
  -H "Authorization-Name: your_username"
```

---

### 7. 取得 Firmware 詳細摘要

取得單一 Firmware 的詳細測試統計資訊。

```
GET /api/v1/projects/{project_uid}/firmware-summary
```

**Path 參數:**
| 參數 | 類型 | 說明 |
|------|------|------|
| `project_uid` | string | 專案 UID (從 Firmware 列表取得) |

**Headers:**
- `Authorization`: 使用者 ID
- `Authorization-Name`: 使用者名稱

**回應範例:**
```json
{
  "success": true,
  "data": {
    "project_uid": "1de4830a914b42ffb92ddd201d7ca923",
    "fw_name": "G200X85A_OPAL",
    "sub_version": "AA",
    "task_name": "[SVDFWV-33916][Micron][Springsteen][SM2508][AA][Micron B58R TLC]",
    "overview": {
      "total_test_items": 61,
      "passed": 44,
      "failed": 16,
      "conditional_passed": 1,
      "completion_rate": 100.0,
      "pass_rate": 73.33
    },
    "sample_stats": {
      "total_samples": 140,
      "samples_used": 0,
      "utilization_rate": 0.0
    },
    "test_item_stats": {
      "total_items": 39,
      "passed_items": 25,
      "failed_items": 14,
      "execution_rate": 100.0,
      "fail_rate": 36.0
    }
  },
  "message": null,
  "timestamp": "2025-12-07T10:00:00Z"
}
```

**回應欄位說明:**

| 區塊 | 欄位 | 說明 |
|------|------|------|
| **overview** | `total_test_items` | 總測試項目數 |
| | `passed` | 通過數 |
| | `failed` | 失敗數 |
| | `conditional_passed` | 條件通過數 |
| | `completion_rate` | 完成率 (%) |
| | `pass_rate` | 通過率 (%) |
| **sample_stats** | `total_samples` | 總樣本數 |
| | `samples_used` | 已使用樣本數 |
| | `utilization_rate` | 樣本利用率 (%) |
| **test_item_stats** | `total_items` | 總測試項目數 |
| | `passed_items` | 通過項目數 |
| | `failed_items` | 失敗項目數 |
| | `execution_rate` | 執行率 (%) |
| | `fail_rate` | 失敗率 (%) |

**cURL 範例:**
```bash
curl http://localhost:8080/api/v1/projects/1de4830a914b42ffb92ddd201d7ca923/firmware-summary \
  -H "Authorization: 150" \
  -H "Authorization-Name: your_username"
```

---

### 8. 取得專案 Firmware 列表

依 Project ID 取得該專案下所有的 Firmware 版本列表。

```
GET /api/v1/projects/{project_id}/firmwares
```

**Path 參數:**
| 參數 | 類型 | 說明 |
|------|------|------|
| `project_id` | string | 專案 ID (從專案列表取得) |

**Headers:**
- `Authorization`: 使用者 ID
- `Authorization-Name`: 使用者名稱

**回應範例:**
```json
{
  "success": true,
  "data": {
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
      }
    ]
  },
  "message": null,
  "timestamp": "2025-12-07T10:00:00Z"
}
```

**cURL 範例:**
```bash
curl http://localhost:8080/api/v1/projects/8e9fe3fa43694a2c8a7cef9e42620f60/firmwares \
  -H "Authorization: 150" \
  -H "Authorization-Name: your_username"
```

---

### 9. 取得完整專案摘要

取得專案的完整摘要，包含所有 Firmware 的詳細統計資訊與聚合統計。

```
GET /api/v1/projects/{project_uid}/full-summary
```

**Path 參數:**
| 參數 | 類型 | 說明 |
|------|------|------|
| `project_uid` | string | 專案 UID (從專案列表取得) |

**Headers:**
- `Authorization`: 使用者 ID
- `Authorization-Name`: 使用者名稱

**回應範例:**
```json
{
  "success": true,
  "data": {
    "project_id": "12345",
    "project_name": "YMTC 232L TLC BIC5 B27B",
    "total_firmwares": 2,
    "firmwares": [
      {
        "project_uid": "1de4830a914b42ffb92ddd201d7ca923",
        "fw_name": "G200X85A",
        "sub_version": "AA",
        "internal_summary": {
          "task_name": "[SVDFWV-33916][Micron][Springsteen][SM2508][AA]",
          "total_samples": 140,
          "sample_used_rate": 50.0,
          "total_test_items": 61,
          "passed": 44,
          "failed": 16,
          "conditional_passed": 1,
          "completion_rate": 100.0,
          "real_test_count": 60
        },
        "external_summary": {
          "total_sample_quantity": 140,
          "sample_utilization_rate": 50.0,
          "passed": 100,
          "failed": 20,
          "sample_completion_rate": 85.71,
          "sample_fail_rate": 14.29,
          "execution_rate": 100.0,
          "item_fail_rate": 26.23,
          "item_passed": 45,
          "item_failed": 16,
          "total_items": 61
        }
      },
      {
        "project_uid": "2de4830a914b42ffb92ddd201d7ca924",
        "fw_name": "G200X86A",
        "sub_version": "AB",
        "internal_summary": { "..." : "..." },
        "external_summary": { "..." : "..." }
      }
    ],
    "aggregated_stats": {
      "total_test_items": 122,
      "total_passed": 88,
      "total_failed": 32,
      "total_conditional_passed": 2,
      "overall_pass_rate": 73.33
    }
  },
  "message": null,
  "timestamp": "2025-12-07T10:00:00Z"
}
```

**回應欄位說明:**

| 區塊 | 欄位 | 說明 |
|------|------|------|
| **根層級** | `project_id` | 專案 ID |
| | `project_name` | 專案名稱 |
| | `total_firmwares` | Firmware 總數 |
| **internal_summary** | `task_name` | 任務名稱 |
| | `total_samples` | STMS 總樣本數 |
| | `sample_used_rate` | 樣本使用率 (%) |
| | `total_test_items` | 總測試項目數 |
| | `passed` | 通過數 |
| | `failed` | 失敗數 |
| | `conditional_passed` | 條件通過數 |
| | `completion_rate` | 完成率 (%) |
| | `real_test_count` | 實際測試數 |
| **external_summary** | `total_sample_quantity` | 總樣本數量 |
| | `sample_utilization_rate` | 樣本利用率 (%) |
| | `passed` | 樣本通過數 |
| | `failed` | 樣本失敗數 |
| | `sample_completion_rate` | 樣本完成率 (%) |
| | `sample_fail_rate` | 樣本失敗率 (%) |
| | `execution_rate` | 測試項目執行率 (%) |
| | `item_fail_rate` | 測試項目失敗率 (%) |
| | `item_passed` | 項目通過數 |
| | `item_failed` | 項目失敗數 |
| | `total_items` | 總項目數 |
| **aggregated_stats** | `total_test_items` | 所有 FW 測試項目總和 |
| | `total_passed` | 所有 FW 通過總數 |
| | `total_failed` | 所有 FW 失敗總數 |
| | `total_conditional_passed` | 所有 FW 條件通過總數 |
| | `overall_pass_rate` | 整體通過率 (%) |

**cURL 範例:**
```bash
curl http://localhost:8080/api/v1/projects/00e11fc25a3f454e9e3860ff67dd2c07/full-summary \
  -H "Authorization: 150" \
  -H "Authorization-Name: your_username"
```

---

### 6. 取得測試項目詳細資料

取得專案的所有測試項目詳細資料，包含每個測試項目的結果。

```
GET /api/v1/projects/{project_uid}/test-details
```

**Path Parameters:**

| 參數 | 類型 | 說明 |
|------|------|------|
| `project_uid` | string | 專案 UID |

**Headers:**

| Header | 必填 | 說明 |
|--------|------|------|
| Authorization | 是 | 使用者 ID |
| Authorization-Name | 是 | 使用者名稱 |

**回應欄位:**

| 區塊 | 欄位 | 說明 |
|------|------|------|
| (root) | `project_uid` | 專案 UID |
| | `project_name` | 專案名稱 |
| | `fw_name` | Firmware 名稱 |
| | `sub_version` | 子版本 |
| | `capacities` | 所有容量列表 |
| | `total_items` | 總測試項目數 |
| **details[]** | `category_name` | 測試類別名稱 |
| | `test_item_name` | 測試項目名稱 |
| | `size_results` | 各容量的測試結果 |
| | `total` | 該測試項目的總計 |
| | `sample_capacity` | 使用的樣品容量配置 |
| | `note` | 測試說明/備註 |
| **summary** | `total_ongoing` | 進行中總數 |
| | `total_passed` | 通過總數 |
| | `total_conditional_passed` | 條件通過總數 |
| | `total_failed` | 失敗總數 |
| | `total_interrupted` | 中斷總數 |
| | `overall_total` | 總數 |
| | `pass_rate` | 通過率 (%) |

**結果格式說明:**

result 欄位格式為: `Ongoing/Passed/Conditional Passed/Failed/Interrupted`

例如: `"0/1/0/0/0"` 表示 0 個進行中、1 個通過、0 個條件通過、0 個失敗、0 個中斷

**cURL 範例:**
```bash
curl http://localhost:8080/api/v1/projects/bcd1b61fd256475a9d05e986f8e6cfd8/test-details \
  -H "Authorization: 150" \
  -H "Authorization-Name: your_username"
```

**回應範例:**
```json
{
  "success": true,
  "data": {
    "project_uid": "bcd1b61fd256475a9d05e986f8e6cfd8",
    "project_name": "Client_PCIe_Micron_Springsteen_SM2508_Micron B68S TLC",
    "fw_name": "PH10YC3H_Pyrite_512Byte",
    "sub_version": "AC",
    "capacities": ["512GB", "1024GB", "2048GB", "4096GB"],
    "total_items": 95,
    "details": [
      {
        "category_name": "Functionality",
        "test_item_name": "Primary Drive Firmware Upgrade Check",
        "size_results": [
          {
            "size": "512GB",
            "result": {
              "ongoing": 0,
              "passed": 1,
              "conditional_passed": 0,
              "failed": 0,
              "interrupted": 0,
              "total": 1
            }
          }
        ],
        "total": {
          "ongoing": 0,
          "passed": 4,
          "conditional_passed": 0,
          "failed": 0,
          "interrupted": 0,
          "total": 4
        },
        "sample_capacity": "512GB(1),1024GB(1),2048GB(1),4096GB(1)",
        "note": "a. 開卡Old FW..."
      }
    ],
    "summary": {
      "total_ongoing": 0,
      "total_passed": 226,
      "total_conditional_passed": 34,
      "total_failed": 6,
      "total_interrupted": 0,
      "overall_total": 266,
      "pass_rate": 97.41
    }
  },
  "timestamp": "2025-12-10T10:00:00Z"
}
```

---

### 7. 取得專案儀表板

取得專案儀表板資料，顯示所有 Firmware 的測試進度概覽。

```
GET /api/v1/projects/{project_id}/dashboard
```

**Path Parameters:**

| 參數 | 類型 | 說明 |
|------|------|------|
| `project_id` | string | 專案 ID |

**Headers:**

| Header | 必填 | 說明 |
|--------|------|------|
| Authorization | 是 | 使用者 ID |
| Authorization-Name | 是 | 使用者名稱 |

**回應欄位:**

| 區塊 | 欄位 | 說明 |
|------|------|------|
| (root) | `project_id` | 專案 ID |
| | `project_name` | 專案名稱 |
| | `total_firmwares` | Firmware 總數 |
| **firmwares[]** | `fw_name` | Firmware 名稱 |
| | `sub_version` | 子版本 |
| | `passed` | 通過數 |
| | `failed` | 失敗數 |
| | `ongoing` | 進行中數 |
| | `interrupted` | 中斷數 |
| | `total` | 總測試項目數 |
| | `pass_rate` | 通過率 (%) |
| | `completion_rate` | 完成率 (%) |
| **summary** | `total_passed` | 通過總數 |
| | `total_failed` | 失敗總數 |
| | `total_ongoing` | 進行中總數 |
| | `total_interrupted` | 中斷總數 |
| | `overall_total` | 總數 |
| | `overall_pass_rate` | 整體通過率 (%) |

**cURL 範例:**
```bash
curl http://localhost:8080/api/v1/projects/123/dashboard \
  -H "Authorization: 150" \
  -H "Authorization-Name: your_username"
```

**回應範例:**
```json
{
  "success": true,
  "data": {
    "project_id": "123",
    "project_name": "Client_PCIe_Micron_Springsteen_SM2508",
    "total_firmwares": 2,
    "firmwares": [
      {
        "fw_name": "PH10YC3H_Pyrite_512Byte",
        "sub_version": "AC",
        "passed": 226,
        "failed": 6,
        "ongoing": 0,
        "interrupted": 0,
        "total": 266,
        "pass_rate": 97.41,
        "completion_rate": 87.22
      },
      {
        "fw_name": "PH10YC4H_Opal_4KB",
        "sub_version": "AB",
        "passed": 180,
        "failed": 10,
        "ongoing": 5,
        "interrupted": 0,
        "total": 200,
        "pass_rate": 94.74,
        "completion_rate": 95.0
      }
    ],
    "summary": {
      "total_passed": 406,
      "total_failed": 16,
      "total_ongoing": 5,
      "total_interrupted": 0,
      "overall_total": 466,
      "overall_pass_rate": 96.21
    }
  },
  "timestamp": "2025-12-10T10:00:00Z"
}
```

---

### 8. 取得 Known Issues 列表

取得所有 Known Issues 列表，可依專案或 Root ID 篩選。

```
POST /api/v1/projects/known-issues
```

**Query Parameters:**

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `project_id` | string[] | 否 | 篩選的專案 ID 列表 (可多選) |
| `root_id` | string[] | 否 | 篩選的 Root ID 列表 (可多選) |
| `show_disable` | boolean | 否 | 是否顯示停用的 Issues (預設 true) |

**Headers:**

| Header | 必填 | 說明 |
|--------|------|------|
| Authorization | 是 | 使用者 ID |
| Authorization-Name | 是 | 使用者名稱 |

**回應欄位:**

| 區塊 | 欄位 | 說明 |
|------|------|------|
| (root) | `items` | Known Issues 列表 |
| | `total` | 總筆數 |
| **items[]** | `id` | Issue ID |
| | `project_id` | 專案 ID |
| | `project_name` | 專案名稱 |
| | `root_id` | Root ID |
| | `test_item_name` | 測試項目名稱 |
| | `issue_id` | Issue 編號 (如 Oakgate-1) |
| | `case_name` | Case 名稱 |
| | `case_path` | Case 路徑 |
| | `created_by` | 建立者 |
| | `created_at` | 建立時間 |
| | `jira_id` | JIRA ID |
| | `note` | 備註 |
| | `is_enable` | 是否啟用 |
| | `jira_link` | JIRA 連結 |

**cURL 範例:**

```bash
# 取得所有 Known Issues
curl -X POST "http://localhost:8080/api/v1/projects/known-issues" \
  -H "Authorization: 150" \
  -H "Authorization-Name: your_username"

# 篩選特定專案的 Known Issues
curl -X POST "http://localhost:8080/api/v1/projects/known-issues?project_id=ca63e07024db4af69cbfbe64933f5a9d" \
  -H "Authorization: 150" \
  -H "Authorization-Name: your_username"

# 篩選多個專案
curl -X POST "http://localhost:8080/api/v1/projects/known-issues?project_id=proj1&project_id=proj2" \
  -H "Authorization: 150" \
  -H "Authorization-Name: your_username"

# 只顯示啟用的 Issues
curl -X POST "http://localhost:8080/api/v1/projects/known-issues?show_disable=false" \
  -H "Authorization: 150" \
  -H "Authorization-Name: your_username"
```

**回應範例:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "a3e25c0d83b34d8599e9870b368e74",
        "project_id": "ca63e07024db4af69cbfbe64933f5a9d",
        "project_name": "Enterprise_PCIe_SMI_Montitan_SM8366_Kioxia BiCS8 TLC",
        "root_id": "STC-61",
        "test_item_name": "OGT_MS_OCP2.0 Test suite",
        "issue_id": "Oakgate-1",
        "case_name": "Namespace Basic Data 2.0 v0.56",
        "case_path": "Namespace Basic Data 2.0 v0.56",
        "created_by": "Sunny.Fan",
        "created_at": "2025-09-12 09:58:28",
        "jira_id": "SVDFWV-43236",
        "note": "Script issue",
        "is_enable": true,
        "jira_link": "https://jira.siliconmotion.com.tw:8443/browse/SVDFWV-43236"
      },
      {
        "id": "000bcba87b354f14a29c3884bf5d4608",
        "project_id": "ca63e07024db4af69cbfbe64933f5a9d",
        "project_name": "Enterprise_PCIe_SMI_Montitan_SM8366_Kioxia BiCS8 TLC",
        "root_id": "STC-61",
        "test_item_name": "OGT_MS_OCP2.0 Test suite",
        "issue_id": "Oakgate-2",
        "case_name": "IO Commands 2.0 v0.56",
        "case_path": "IO Commands 2.0 v0.56",
        "created_by": "Sunny.Fan",
        "created_at": "2025-09-12 09:58:48",
        "jira_id": "SVDFWV-43236",
        "note": "script issue",
        "is_enable": true,
        "jira_link": "https://jira.siliconmotion.com.tw:8443/browse/SVDFWV-43236"
      }
    ],
    "total": 2
  },
  "timestamp": "2025-12-15T10:00:00Z"
}
```

---

### 9. 搜尋測試狀態

搜尋 SAF 測試狀態，支援依專案名稱、測試狀態等條件查詢測試工作的詳細資訊。

```
POST /api/v1/projects/test-status/search
```

**Request Body:**

| 欄位 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `query` | string | 是 | 查詢條件，格式: `欄位名 = "值"` |
| `page` | int | 否 | 頁碼 (預設 1) |
| `size` | int | 否 | 每頁筆數 (預設 50，最大 100) |
| `sort` | object | 否 | 排序條件 |

**查詢語法範例:**

| 查詢欄位 | 範例 | 說明 |
|----------|------|------|
| `new_project_name` | `new_project_name = "Client_PCIe_Micron_Springsteen_SM2508_Micron B68S TLC"` | 依完整專案名稱查詢 |
| `projectName` | `projectName = "Springsteen"` | 依專案短名查詢 |
| `testStatus` | `testStatus = "PASS"` | 依測試狀態查詢 |
| `sampleId` | `sampleId = "SSD-X-05498"` | 依樣品 ID 查詢 |

**Headers:**

| Header | 必填 | 說明 |
|--------|------|------|
| Authorization | 是 | 使用者 ID |
| Authorization-Name | 是 | 使用者名稱 |

**回應欄位:**

| 區塊 | 欄位 | 說明 |
|------|------|------|
| (root) | `items` | 測試狀態列表 |
| | `total` | 總筆數 |
| | `page` | 目前頁碼 |
| | `size` | 每頁筆數 |
| **items[]** | `test_job_id` | 測試工作 ID |
| | `is_notification` | 是否發送通知 |
| | `test_item` | 測試項目名稱 |
| | `test_status` | 測試狀態 |
| | `all_status` | 所有可能的狀態值 |
| | `sample_id` | 樣品 ID |
| | `platform` | 測試平台 |
| | `position` | 測試位置 |
| | `mainboard_manufacturer` | 主機板製造商 |
| | `mainboard_model` | 主機板型號 |
| | `project_name` | 專案名稱 |
| | `fw` | 韌體版本 |
| | `duration` | 測試持續時間 (秒) |
| | `start_time` | 開始時間 |
| | `end_time` | 結束時間 |
| | `user` | 執行測試的使用者 |
| | `updated_at` | 更新時間 |
| | `log_path` | 測試日誌路徑 |
| | `driver` | 驅動程式 |
| | `filesystem` | 檔案系統 |
| | `slot` | 插槽類型 |
| | `aspm` | ASPM 設定 |
| | `os_name` | 作業系統名稱 |

**測試狀態說明:**

| 狀態 | 說明 |
|------|------|
| `PASS` | 通過 |
| `FAIL` | 失敗 |
| `ONGOING` | 進行中 |
| `CANCEL` | 取消 |
| `CHECK` | 待確認 |
| `INTERRUPT` | 中斷 |
| `CONDITIONAL PASS` | 條件通過 |
| `QUEUED` | 排隊中 |

**cURL 範例:**

```bash
# 依專案名稱搜尋
curl -X POST "http://localhost:8080/api/v1/projects/test-status/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: 150" \
  -H "Authorization-Name: your_username" \
  -d '{
    "query": "new_project_name = \"Client_PCIe_Micron_Springsteen_SM2508_Micron B68S TLC\"",
    "page": 1,
    "size": 50
  }'

# 依測試狀態搜尋
curl -X POST "http://localhost:8080/api/v1/projects/test-status/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: 150" \
  -H "Authorization-Name: your_username" \
  -d '{
    "query": "testStatus = \"PASS\"",
    "page": 1,
    "size": 10
  }'

# 依樣品 ID 搜尋
curl -X POST "http://localhost:8080/api/v1/projects/test-status/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: 150" \
  -H "Authorization-Name: your_username" \
  -d '{
    "query": "sampleId = \"SSD-X-05498\"",
    "page": 1,
    "size": 20
  }'
```

**回應範例:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "test_job_id": "f30964a6da3f11f08e7e0242ac280004",
        "is_notification": true,
        "test_item": "Primary Drive Firmware Upgrade Check",
        "test_status": "PASS",
        "all_status": ["CHECK", "PASS", "FAIL", "INTERRUPT", "ONGOING", "CANCEL", "CONDITIONAL PASS"],
        "sample_id": "SSD-X-05498",
        "platform": "NB-SSD-0736",
        "position": "SAF1001-0736",
        "mainboard_manufacturer": "Dell",
        "mainboard_model": "Latitude 5420",
        "project_name": "Springsteen",
        "fw": "GB10YCFS",
        "duration": 7200,
        "start_time": "2025-12-16T02:00:00+00:00",
        "end_time": "2025-12-16T04:00:00+00:00",
        "user": "tk.chang",
        "updated_at": "2025-12-16T05:27:44+00:00",
        "log_path": "/SAF_Workspace/prod/test_log/...",
        "driver": "Microsoft",
        "filesystem": "NTFS",
        "slot": "M.2",
        "aspm": "Default",
        "os_name": "Windows11 x64 23H2 (OS Build 22631.4169)"
      }
    ],
    "total": 50612,
    "page": 1,
    "size": 50
  },
  "timestamp": "2025-12-16T06:00:00Z"
}
```

---

## 錯誤回應

所有錯誤都會返回統一的格式：

```json
{
  "success": false,
  "data": null,
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-12-02T10:00:00Z"
}
```

### 常見錯誤碼

| 錯誤碼 | HTTP 狀態 | 說明 |
|--------|----------|------|
| `AUTH_FAILED` | 401 | 認證失敗 |
| `MISSING_AUTH` | 401 | 缺少認證 Header |
| `INVALID_AUTH` | 400 | 無效的認證資訊 |
| `PROJECT_NOT_FOUND` | 404 | 找不到專案 |
| `CONNECTION_ERROR` | 503 | 無法連接 SAF 伺服器 |
| `SAF_API_ERROR` | 502 | SAF API 呼叫失敗 |
| `INTERNAL_ERROR` | 500 | 內部錯誤 |

---

## 其他電腦連線

如果您的 API Server 運行在 IP 為 `192.168.1.100` 的主機上：

```bash
# 健康檢查
curl http://192.168.1.100:8080/health

# 登入
curl -X POST http://192.168.1.100:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# 取得專案
curl http://192.168.1.100:8080/api/v1/projects \
  -H "Authorization: 150" \
  -H "Authorization-Name: your_username"
```
