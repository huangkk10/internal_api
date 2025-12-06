# ListOneProjectSummary API 完整規劃文件

> 建立日期: 2025-12-07  
> 更新日期: 2025-12-07  
> 功能目的: 詳細記錄 SAF `listOneProjectSummary` API 的完整回應結構與資料應用

---

## 1. 功能概述

### 1.1 目標
- 記錄 SAF `listOneProjectSummary` API 完整的回應結構
- 規劃如何利用完整資料提供更豐富的 API 功能
- 目前已實作基本版本，此文件規劃進階功能

### 1.2 對應 SAF API

| 項目 | 說明 |
|------|------|
| **端點** | `POST https://saf.siliconmotion.com.tw:3004/api/project/listOneProjectSummary` |
| **認證方式** | Header: `Authorization` (user id), `Authorization_name` (username) |
| **Content-Type** | `application/json` |
| **Request Body** | `{"projectId": "", "projectUid": "<project_uid>"}` |

---

## 2. SAF API 完整回應結構

### 2.1 頂層結構

```json
{
  "projectId": "8e9fe3fa43694a2c8a7cef9e42620f60",
  "projectName": "Client_PCIe_Micron_Springsteen_SM2508_Micron B58R TLC",
  "fws": [
    { /* Firmware 詳細資料 */ }
  ]
}
```

### 2.2 Firmware 物件結構 (`fws[]`)

```json
{
  "projectUid": "1de4830a914b42ffb92ddd201d7ca923",
  "fwName": "G200X85A_OPAL",
  "subVersionName": "AA",
  
  "internalSummary_1": { /* 內部摘要 1 */ },
  "internalSummary_2": { /* 內部摘要 2 */ },
  "externalSummary": { /* 外部摘要 */ },
  
  "plansSummary": [ /* 測試計劃摘要 */ ]
}
```

### 2.3 內部摘要 1 (`internalSummary_1`)

```json
{
  "name": "[SVDFWV-33916][Micron][Springsteen][SM2508][AA][Micron B58R TLC]",
  "totalStmsSampleCount": 140,
  "sampleUsedRate": "0%",
  "totalTestItems": 61,
  "passedCnt": 44,
  "failedCnt": 16,
  "completionRate": "61/61 (100%)",
  "conditionalPassedCnt": 1
}
```

| 欄位 | 類型 | 說明 |
|------|------|------|
| `name` | string | 完整專案識別名稱 |
| `totalStmsSampleCount` | int | 總樣本數量 |
| `sampleUsedRate` | string | 樣本使用率 |
| `totalTestItems` | int | 總測試項目數 |
| `passedCnt` | int | 通過數量 |
| `failedCnt` | int | 失敗數量 |
| `completionRate` | string | 完成率 (格式: "完成/總數 (百分比)") |
| `conditionalPassedCnt` | int | 條件通過數量 |

### 2.4 內部摘要 2 (`internalSummary_2`)

```json
{
  "realTestCount": 61
}
```

| 欄位 | 類型 | 說明 |
|------|------|------|
| `realTestCount` | int | 實際測試數量 |

### 2.5 外部摘要 (`externalSummary`)

```json
{
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
```

| 欄位 | 類型 | 說明 |
|------|------|------|
| `totalSampleQuantity` | int | 總樣本數量 |
| `sampleUtilizationRate` | string | 樣本利用率 |
| `passedCnt` | int | 通過的樣本測試項目數 |
| `failedCnt` | int | 失敗的樣本測試項目數 |
| `sampleTestItemCompletionRate` | string | 樣本測試項目完成率 |
| `sampleTestItemFailRate` | string | 樣本測試項目失敗率 |
| `testItemExecutionRate` | string | 測試項目執行率 |
| `testItemFailRate` | string | 測試項目失敗率 |
| `conditionalPassedCnt` | int | 條件通過數 |
| `itemPassedCnt` | int | 通過的測試項目數 |
| `itemFailedCnt` | int | 失敗的測試項目數 |
| `totalItemCnt` | int | 總測試項目數 |

### 2.6 測試計劃摘要 (`plansSummary[]`)

```json
{
  "testPlanName": "TestPlan_Name",
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
```

---

## 3. 現有實作狀態

### 3.1 已實作

| 功能 | 端點 | 說明 |
|------|------|------|
| 基本測試摘要 | `GET /projects/{project_uid}/test-summary` | 依類別、容量統計測試結果 |

### 3.2 目前使用的資料

目前實作主要使用 `plansSummary` 中的 `categoryItems` 資料，提供：
- 各類別 (Compatibility, Function, Performance 等) 的測試結果
- 各容量 (512GB, 1024GB 等) 的測試結果
- 結果格式: PASS/FAIL/ONGOING/CANCEL/CHECK

---

## 4. 進階功能規劃

### 4.1 新增端點: 專案完整摘要

**目標**: 提供更完整的專案統計資訊

**端點**: `GET /api/v1/projects/{project_uid}/full-summary`

**回應格式**:

```json
{
  "success": true,
  "data": {
    "project_id": "8e9fe3fa43694a2c8a7cef9e42620f60",
    "project_name": "Client_PCIe_Micron_Springsteen_SM2508_Micron B58R TLC",
    "firmwares": [
      {
        "project_uid": "1de4830a914b42ffb92ddd201d7ca923",
        "fw_name": "G200X85A_OPAL",
        "sub_version": "AA",
        "internal_summary": {
          "task_name": "[SVDFWV-33916][Micron][Springsteen][SM2508][AA][Micron B58R TLC]",
          "total_samples": 140,
          "sample_used_rate": "0%",
          "total_test_items": 61,
          "passed_count": 44,
          "failed_count": 16,
          "conditional_passed_count": 1,
          "completion_rate": "100%",
          "real_test_count": 61
        },
        "external_summary": {
          "total_sample_quantity": 140,
          "sample_utilization_rate": "0%",
          "sample_test_item_completion_rate": "100%",
          "sample_test_item_fail_rate": "26%",
          "test_item_execution_rate": "100%",
          "test_item_fail_rate": "36%",
          "item_passed_count": 25,
          "item_failed_count": 14,
          "total_item_count": 39
        },
        "test_plans": [
          {
            "name": "TestPlan_Name",
            "categories": [
              {
                "name": "Compatibility",
                "total_test_items": 10,
                "results_by_size": {
                  "512GB": {"pass": 8, "fail": 0, "ongoing": 0, "cancel": 0, "check": 0},
                  "1024GB": {"pass": 10, "fail": 1, "ongoing": 0, "cancel": 0, "check": 0}
                },
                "total": {"pass": 18, "fail": 1, "ongoing": 0, "cancel": 0, "check": 0}
              }
            ]
          }
        ]
      }
    ]
  }
}
```

### 4.2 新增端點: Firmware 詳細摘要

**目標**: 取得單一 Firmware 的詳細測試統計

**端點**: `GET /api/v1/projects/{project_uid}/firmware-summary`

**回應格式**:

```json
{
  "success": true,
  "data": {
    "project_uid": "1de4830a914b42ffb92ddd201d7ca923",
    "fw_name": "G200X85A_OPAL",
    "sub_version": "AA",
    
    "overview": {
      "total_test_items": 61,
      "passed": 44,
      "failed": 16,
      "conditional_passed": 1,
      "completion_rate": 100.0,
      "pass_rate": 72.13
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
      "fail_rate": 35.90
    },
    
    "categories": [
      {
        "name": "Compatibility",
        "results": {"pass": 18, "fail": 1, "total": 19, "pass_rate": 94.74}
      },
      {
        "name": "Function", 
        "results": {"pass": 35, "fail": 2, "total": 37, "pass_rate": 94.59}
      }
    ]
  }
}
```

### 4.3 新增端點: 專案比較

**目標**: 比較同一專案下不同 Firmware 版本的測試結果

**端點**: `GET /api/v1/projects/{project_id}/compare`

**Query 參數**:
| 參數 | 類型 | 說明 |
|------|------|------|
| `fw_uids` | string | 要比較的 Firmware UIDs (逗號分隔) |

**回應格式**:

```json
{
  "success": true,
  "data": {
    "project_id": "8e9fe3fa43694a2c8a7cef9e42620f60",
    "project_name": "Client_PCIe_Micron_Springsteen_SM2508_Micron B58R TLC",
    "comparison": [
      {
        "fw_name": "G200X85A_OPAL",
        "sub_version": "AA",
        "pass_rate": 72.13,
        "total_tests": 61,
        "passed": 44,
        "failed": 16
      },
      {
        "fw_name": "G200X85A",
        "sub_version": "AB",
        "pass_rate": 85.00,
        "total_tests": 60,
        "passed": 51,
        "failed": 9
      }
    ],
    "best_performer": {
      "fw_name": "G200X85A",
      "sub_version": "AB",
      "pass_rate": 85.00
    }
  }
}
```

---

## 5. 實作優先順序

### Phase 1: 基礎功能 (已完成 ✅)
- [x] `GET /projects/{project_uid}/test-summary` - 基本測試摘要

### Phase 2: 進階摘要 (規劃中)
- [ ] `GET /projects/{project_uid}/firmware-summary` - Firmware 詳細摘要
- [ ] 資料轉換函數優化

### Phase 3: 完整資料 (規劃中)
- [ ] `GET /projects/{project_uid}/full-summary` - 完整專案摘要
- [ ] 包含所有 internal/external summary 資料

### Phase 4: 比較功能 (規劃中)
- [ ] `GET /projects/{project_id}/compare` - Firmware 版本比較
- [ ] 趨勢分析功能

---

## 6. 資料欄位對照表

### 6.1 內部摘要欄位對照

| SAF 欄位 | API 欄位 | 說明 |
|----------|----------|------|
| `totalStmsSampleCount` | `total_samples` | 總樣本數 |
| `sampleUsedRate` | `sample_used_rate` | 樣本使用率 |
| `totalTestItems` | `total_test_items` | 總測試項目數 |
| `passedCnt` | `passed_count` | 通過數 |
| `failedCnt` | `failed_count` | 失敗數 |
| `completionRate` | `completion_rate` | 完成率 |
| `conditionalPassedCnt` | `conditional_passed_count` | 條件通過數 |
| `realTestCount` | `real_test_count` | 實際測試數 |

### 6.2 外部摘要欄位對照

| SAF 欄位 | API 欄位 | 說明 |
|----------|----------|------|
| `totalSampleQuantity` | `total_sample_quantity` | 總樣本數量 |
| `sampleUtilizationRate` | `sample_utilization_rate` | 樣本利用率 |
| `sampleTestItemCompletionRate` | `sample_test_item_completion_rate` | 樣本測試項目完成率 |
| `sampleTestItemFailRate` | `sample_test_item_fail_rate` | 樣本測試項目失敗率 |
| `testItemExecutionRate` | `test_item_execution_rate` | 測試項目執行率 |
| `testItemFailRate` | `test_item_fail_rate` | 測試項目失敗率 |
| `itemPassedCnt` | `item_passed_count` | 通過測試項目數 |
| `itemFailedCnt` | `item_failed_count` | 失敗測試項目數 |
| `totalItemCnt` | `total_item_count` | 總測試項目數 |

---

## 7. 使用流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           完整使用流程                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. 登入取得認證                                                          │
│     POST /api/v1/auth/login                                             │
│     → 取得 user_id, username                                             │
│                                                                         │
│  2. 取得專案列表                                                          │
│     GET /api/v1/projects                                                │
│     → 取得 projectId 和 projectUid                                        │
│                                                                         │
│  3. 取得專案下的 Firmware 列表                                            │
│     GET /api/v1/projects/{projectId}/firmwares                          │
│     → 取得各 Firmware 的 projectUid                                       │
│                                                                         │
│  4. 取得 Firmware 測試摘要                                                │
│     GET /api/v1/projects/{projectUid}/test-summary                      │
│     → 取得測試結果統計                                                     │
│                                                                         │
│  5. (進階) 取得 Firmware 詳細摘要                                          │
│     GET /api/v1/projects/{projectUid}/firmware-summary                  │
│     → 取得完整統計資訊                                                     │
│                                                                         │
│  6. (進階) 比較不同 Firmware 版本                                          │
│     GET /api/v1/projects/{projectId}/compare?fw_uids=uid1,uid2          │
│     → 取得版本比較結果                                                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 8. 注意事項

1. **projectId vs projectUid**:
   - `projectId`: 專案 ID，用於取得 Firmware 列表
   - `projectUid`: Firmware 的唯一識別碼，用於取得測試摘要

2. **百分比格式**:
   - SAF 回傳格式: `"61/61 (100%)"` 或 `"0%"`
   - 需要解析字串取得數值

3. **結果格式**:
   - `PASS/FAIL/ONGOING/CANCEL/CHECK`
   - 例如: `"8/0/0/0/0"` = 8 PASS, 0 FAIL, 0 ONGOING, 0 CANCEL, 0 CHECK

4. **條件通過 (Conditional Passed)**:
   - 某些測試項目為條件通過
   - 需要特別標示，不計入一般通過數

---

## 9. 預估時程

| Phase | 功能 | 預估時間 |
|-------|------|---------|
| Phase 2 | Firmware 詳細摘要 | 2 小時 |
| Phase 3 | 完整專案摘要 | 3 小時 |
| Phase 4 | 比較功能 | 4 小時 |
| **總計** | | **約 9 小時** |

---

## 10. 相關文件

- [PLANNING_PROJECT_SUMMARY_API.md](./PLANNING_PROJECT_SUMMARY_API.md) - 原始規劃文件
- [PLANNING_FWS_BY_PROJECT_ID_API.md](./PLANNING_FWS_BY_PROJECT_ID_API.md) - Firmware 列表 API
- [API.md](./API.md) - API 使用文件
