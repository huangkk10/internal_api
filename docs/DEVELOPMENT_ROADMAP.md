# Internal API 開發階段規劃

> 建立日期: 2025-12-07  
> 版本: 1.0  
> 目的: 規劃 Internal API 的完整開發階段與里程碑

---

## 📋 總覽

### 目前完成狀態

| 功能 | 端點 | 狀態 |
|------|------|------|
| 健康檢查 | `GET /health` | ✅ 完成 |
| 登入 | `POST /api/v1/auth/login` | ✅ 完成 |
| 設定檔登入 | `POST /api/v1/auth/login-with-config` | ✅ 完成 |
| 專案列表 | `GET /api/v1/projects` | ✅ 完成 |
| 專案統計 | `GET /api/v1/projects/summary` | ✅ 完成 |
| 測試摘要 | `GET /api/v1/projects/{project_uid}/test-summary` | ✅ 完成 |
| Firmware 列表 | `GET /api/v1/projects/{project_id}/firmwares` | ✅ 完成 |

### 待開發功能

| 功能 | 端點 | 優先級 |
|------|------|--------|
| Firmware 詳細摘要 | `GET /api/v1/projects/{project_uid}/firmware-summary` | 🔴 高 |
| 完整專案摘要 | `GET /api/v1/projects/{project_uid}/full-summary` | 🟡 中 |
| Firmware 版本比較 | `GET /api/v1/projects/{project_id}/compare` | 🟢 低 |

---

## 🚀 Phase 1: Firmware 詳細摘要 (優先級: 高)

### 目標
提供單一 Firmware 的完整測試統計資訊，包含內部/外部摘要數據。

### 端點
```
GET /api/v1/projects/{project_uid}/firmware-summary
```

### 預計回應
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
    }
  }
}
```

### 實作任務

| # | 任務 | 預估時間 | 依賴 |
|---|------|---------|------|
| 1.1 | 新增 Schema: `FirmwareSummary`, `OverviewStats`, `SampleStats`, `TestItemStats` | 30 分鐘 | - |
| 1.2 | 新增資料轉換函數: `_transform_firmware_summary()` | 45 分鐘 | 1.1 |
| 1.3 | 新增 Router 端點: `get_firmware_summary()` | 30 分鐘 | 1.2 |
| 1.4 | 新增單元測試 | 30 分鐘 | 1.3 |
| 1.5 | 更新 API 文件 | 15 分鐘 | 1.3 |

### 總預估時間: 2.5 小時

### 驗收標準
- [ ] API 正確回傳 Firmware 詳細摘要
- [ ] 所有百分比格式正確解析
- [ ] 單元測試通過率 100%
- [ ] API 文件已更新

---

## 🚀 Phase 2: 完整專案摘要 (優先級: 中)

### 目標
提供專案下所有 Firmware 的完整摘要資訊，一次取得所有資料。

### 端點
```
GET /api/v1/projects/{project_uid}/full-summary
```

### 預計回應
```json
{
  "success": true,
  "data": {
    "project_id": "8e9fe3fa43694a2c8a7cef9e42620f60",
    "project_name": "Client_PCIe_Micron_Springsteen_SM2508_Micron B58R TLC",
    "total_firmwares": 3,
    "firmwares": [
      {
        "project_uid": "...",
        "fw_name": "G200X85A_OPAL",
        "sub_version": "AA",
        "internal_summary": { /* ... */ },
        "external_summary": { /* ... */ },
        "test_plans": [ /* ... */ ]
      }
    ],
    "aggregated_stats": {
      "total_test_items": 183,
      "total_passed": 132,
      "total_failed": 48,
      "overall_pass_rate": 72.13
    }
  }
}
```

### 實作任務

| # | 任務 | 預估時間 | 依賴 |
|---|------|---------|------|
| 2.1 | 新增 Schema: `FullProjectSummary`, `InternalSummary`, `ExternalSummary` | 45 分鐘 | Phase 1 |
| 2.2 | 新增資料轉換函數: `_transform_full_summary()` | 60 分鐘 | 2.1 |
| 2.3 | 新增聚合統計函數: `_aggregate_firmware_stats()` | 30 分鐘 | 2.2 |
| 2.4 | 新增 Router 端點: `get_full_summary()` | 30 分鐘 | 2.3 |
| 2.5 | 新增單元測試 | 45 分鐘 | 2.4 |
| 2.6 | 更新 API 文件 | 15 分鐘 | 2.4 |

### 總預估時間: 3.5 小時

### 驗收標準
- [ ] API 正確回傳完整專案摘要
- [ ] 聚合統計數據正確
- [ ] 處理多個 Firmware 的情況
- [ ] 單元測試通過率 100%

---

## 🚀 Phase 3: Firmware 版本比較 (優先級: 低)

### 目標
比較同一專案下不同 Firmware 版本的測試結果，找出最佳版本。

### 端點
```
GET /api/v1/projects/{project_id}/compare?fw_uids=uid1,uid2,uid3
```

### 預計回應
```json
{
  "success": true,
  "data": {
    "project_id": "8e9fe3fa43694a2c8a7cef9e42620f60",
    "project_name": "Client_PCIe_Micron_Springsteen_SM2508_Micron B58R TLC",
    "comparison": [
      {
        "project_uid": "...",
        "fw_name": "G200X85A_OPAL",
        "sub_version": "AA",
        "pass_rate": 72.13,
        "total_tests": 61,
        "passed": 44,
        "failed": 16,
        "trend": null
      },
      {
        "project_uid": "...",
        "fw_name": "G200X85A",
        "sub_version": "AB",
        "pass_rate": 85.00,
        "total_tests": 60,
        "passed": 51,
        "failed": 9,
        "trend": "up"
      }
    ],
    "best_performer": {
      "fw_name": "G200X85A",
      "sub_version": "AB",
      "pass_rate": 85.00
    },
    "worst_performer": {
      "fw_name": "G200X85A_OPAL",
      "sub_version": "AA",
      "pass_rate": 72.13
    }
  }
}
```

### 實作任務

| # | 任務 | 預估時間 | 依賴 |
|---|------|---------|------|
| 3.1 | 新增 Schema: `ComparisonResult`, `FirmwareComparison` | 30 分鐘 | Phase 2 |
| 3.2 | 新增 SAF Client 方法: 批次取得多個 Firmware 摘要 | 45 分鐘 | 3.1 |
| 3.3 | 新增比較邏輯函數: `_compare_firmwares()` | 45 分鐘 | 3.2 |
| 3.4 | 新增 Router 端點: `compare_firmwares()` | 30 分鐘 | 3.3 |
| 3.5 | 新增單元測試 | 45 分鐘 | 3.4 |
| 3.6 | 更新 API 文件 | 15 分鐘 | 3.4 |

### 總預估時間: 3.5 小時

### 驗收標準
- [ ] 支援比較 2-10 個 Firmware 版本
- [ ] 正確識別最佳/最差版本
- [ ] 計算趨勢 (up/down/same)
- [ ] 單元測試通過率 100%

---

## 📅 時程規劃

### 開發時程表

```
Week 1 (2025-12-07 ~ 2025-12-13)
├── Phase 1: Firmware 詳細摘要
│   ├── Day 1-2: Schema 設計 & 資料轉換
│   └── Day 3: Router & 測試 & 文件
│
Week 2 (2025-12-14 ~ 2025-12-20)
├── Phase 2: 完整專案摘要
│   ├── Day 1-2: Schema 設計 & 資料轉換
│   ├── Day 3: 聚合統計
│   └── Day 4: Router & 測試 & 文件
│
Week 3 (2025-12-21 ~ 2025-12-27)
├── Phase 3: Firmware 版本比較
│   ├── Day 1-2: SAF Client & 比較邏輯
│   └── Day 3-4: Router & 測試 & 文件
│
Week 4 (2025-12-28 ~ 2025-12-31)
├── 整合測試 & 部署
│   ├── Day 1: 整合測試
│   ├── Day 2: 效能優化
│   └── Day 3: 正式部署
```

### 里程碑

| 里程碑 | 日期 | 交付項目 |
|--------|------|---------|
| M1: Phase 1 完成 | 2025-12-13 | Firmware 詳細摘要 API |
| M2: Phase 2 完成 | 2025-12-20 | 完整專案摘要 API |
| M3: Phase 3 完成 | 2025-12-27 | Firmware 版本比較 API |
| M4: 正式發布 | 2025-12-31 | 完整功能上線 |

---

## 📊 風險評估

### 技術風險

| 風險 | 機率 | 影響 | 緩解措施 |
|------|------|------|---------|
| SAF API 回應格式變更 | 低 | 高 | 建立完整的錯誤處理機制 |
| 效能問題 (大量資料) | 中 | 中 | 實作分頁與快取機制 |
| 百分比解析錯誤 | 低 | 低 | 建立完整的單元測試 |

### 緩解策略

1. **錯誤處理**: 所有 API 都有完整的 try-catch 與錯誤回應
2. **快取機制**: 考慮在 Phase 4 加入 Redis 快取
3. **監控**: 使用 logging 記錄所有 API 呼叫

---

## 🔧 技術細節

### 檔案修改清單

```
app/
├── models/
│   └── schemas.py          # 新增資料模型
├── routers/
│   └── projects.py         # 新增路由端點
├── services/
│   └── saf_client.py       # (如需要) 新增方法
tests/
├── unit/
│   ├── test_projects.py    # 新增單元測試
│   └── test_saf_client.py  # 新增單元測試
├── fixtures/
│   └── mock_responses.py   # 新增模擬資料
└── conftest.py             # 新增 fixtures
docs/
├── API.md                  # 更新 API 文件
└── CHANGELOG.md            # 更新變更日誌
```

### 命名規範

| 類型 | 規範 | 範例 |
|------|------|------|
| Schema 類別 | PascalCase | `FirmwareSummary` |
| 端點函數 | snake_case | `get_firmware_summary` |
| 轉換函數 | _snake_case (私有) | `_transform_firmware_summary` |
| API 路徑 | kebab-case | `/firmware-summary` |

---

## ✅ 檢查清單

### 每個 Phase 完成前的檢查

- [ ] 所有新增功能都有對應的單元測試
- [ ] 測試覆蓋率 > 80%
- [ ] API 文件已更新
- [ ] CHANGELOG 已更新
- [ ] 程式碼已通過 linting
- [ ] 已在本地環境測試通過
- [ ] 已在 Docker 環境測試通過

### 正式發布前的檢查

- [ ] 所有 Phase 功能測試通過
- [ ] 整合測試通過
- [ ] 效能測試通過 (回應時間 < 2秒)
- [ ] API 文件完整
- [ ] README 已更新
- [ ] Docker 映像已建置並推送

---

## 📝 附錄

### A. 相關文件

- [PLANNING_PROJECT_SUMMARY_API.md](./PLANNING_PROJECT_SUMMARY_API.md) - 原始規劃文件
- [PLANNING_PROJECT_SUMMARY_FULL_API.md](./PLANNING_PROJECT_SUMMARY_FULL_API.md) - 完整摘要規劃
- [PLANNING_FWS_BY_PROJECT_ID_API.md](./PLANNING_FWS_BY_PROJECT_ID_API.md) - Firmware 列表 API
- [API.md](./API.md) - API 使用文件

### B. SAF API 參考

| SAF API | 用途 |
|---------|------|
| `/project/listAllProjectsDetails` | 取得所有專案 |
| `/project/ListFWsByProjectId` | 取得 Firmware 列表 |
| `/project/listOneProjectSummary` | 取得專案測試摘要 |

### C. 聯絡資訊

如有問題，請聯繫：
- 專案負責人: Chunwei.Huang
- Email: Chunwei.Huang@siliconmotion.com
