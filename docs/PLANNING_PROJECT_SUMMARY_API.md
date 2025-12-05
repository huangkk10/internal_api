# Project Summary API 規劃文件

> 建立日期: 2025-12-06  
> 功能目的: 新增單一專案測試摘要 API，取得專案的測試結果詳細統計

---

## 1. 功能概述

### 1.1 目標
- 新增 `/api/v1/projects/{project_uid}/test-summary` 端點
- 封裝 SAF 的 `listOneProjectSummary` API
- 提供專案測試結果的詳細統計（分類別、分容量）

### 1.2 對應 SAF API

| 項目 | 說明 |
|------|------|
| **端點** | `POST https://saf.siliconmotion.com.tw:3004/api/project/listOneProjectSummary` |
| **認證方式** | Header: `Authorization` (user id), `Authorization_name` (username) |
| **Content-Type** | `application/json` |
| **Request Body** | `{"projectId": "", "projectUid": "<project_uid>"}` |

### 1.3 SAF API 回應結構

```json
{
  "key": "00e11fc25a3f454e9e3860ff67dd2c07",
  "projectName": "YMTC 232L TLC BIC5 B27B",
  "testResultByMainCategory": [
    {
      "mainCategory": "Compatibility",
      "testResultByCapacity": [
        {
          "capacity": "512GB",
          "result": "8/0/0/0/0"  // PASS/FAIL/ONGOING/CANCEL/CHECK
        },
        {
          "capacity": "1024GB",
          "result": "12/0/0/0/0"
        }
      ]
    },
    {
      "mainCategory": "Function",
      "testResultByCapacity": [...]
    }
  ]
}
```

### 1.4 測試類別 (Main Categories)

| 類別 | 說明 |
|------|------|
| Compatibility | 相容性測試 |
| Function | 功能測試 |
| Performance | 效能測試 |
| Protocol | 協定測試 |
| Reliability | 可靠性測試 |
| Security | 安全性測試 |
| UNITest | 單元測試 |

### 1.5 結果格式

結果以 `PASS/FAIL/ONGOING/CANCEL/CHECK` 格式呈現，例如：
- `"8/0/0/0/0"` = 8 PASS, 0 FAIL, 0 ONGOING, 0 CANCEL, 0 CHECK
- `"0/1/0/0/0"` = 0 PASS, 1 FAIL, 0 ONGOING, 0 CANCEL, 0 CHECK

---

## 2. API 設計

### 2.1 新增端點

| 路由 | 方法 | 說明 | 對應 SAF API |
|------|------|------|--------------|
| `/api/v1/projects/{project_uid}/test-summary` | GET | 取得專案測試摘要 | `POST :3004/api/project/listOneProjectSummary` |

### 2.2 請求格式

```
GET /api/v1/projects/{project_uid}/test-summary
```

**Path 參數:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `project_uid` | string | ✅ | 專案 UID (從 `/api/v1/projects` 取得) |

**Headers:**
| Header | 說明 |
|--------|------|
| `Authorization` | 使用者 ID |
| `Authorization-Name` | 使用者名稱 |

### 2.3 回應格式

#### 成功回應 (200)

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
            "pass": 8, "fail": 0, "ongoing": 0, "cancel": 0, "check": 0,
            "total": 8, "pass_rate": 100.0
          },
          "1024GB": {
            "pass": 12, "fail": 0, "ongoing": 0, "cancel": 0, "check": 0,
            "total": 12, "pass_rate": 100.0
          }
        },
        "total": {
          "pass": 20, "fail": 0, "ongoing": 0, "cancel": 0, "check": 0,
          "total": 20, "pass_rate": 100.0
        }
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

#### 錯誤回應

| HTTP 狀態 | 錯誤碼 | 說明 |
|----------|--------|------|
| 401 | `MISSING_AUTH` | 缺少認證 Header |
| 404 | `PROJECT_NOT_FOUND` | 找不到專案 |
| 502 | `SAF_API_ERROR` | SAF API 呼叫失敗 |
| 503 | `CONNECTION_ERROR` | 無法連接 SAF |

### 2.4 cURL 範例

```bash
# 取得專案測試摘要
curl http://localhost:8080/api/v1/projects/00e11fc25a3f454e9e3860ff67dd2c07/test-summary \
  -H "Authorization: 150" \
  -H "Authorization-Name: Chunwei.Huang"
```

---

## 3. 實作規劃

### 3.1 修改檔案清單

| 檔案 | 操作 | 說明 |
|------|------|------|
| `app/models/schemas.py` | 新增 | 新增資料模型 |
| `app/services/saf_client.py` | 修改 | 新增 SAF API 呼叫方法 |
| `app/routers/projects.py` | 修改 | 新增路由端點 |
| `tests/unit/test_saf_client.py` | 修改 | 新增單元測試 |
| `tests/integration/test_projects_api.py` | 修改 | 新增整合測試 |
| `tests/fixtures/mock_responses.py` | 修改 | 新增模擬資料 |
| `docs/API.md` | 修改 | 更新 API 文件 |
| `README.md` | 修改 | 更新端點列表 |

### 3.2 資料模型 (`app/models/schemas.py`)

```python
# ========== 專案測試摘要相關 ==========

class TestResultCount(BaseModel):
    """測試結果計數"""
    pass_count: int = Field(0, alias="pass", description="通過數")
    fail: int = Field(0, description="失敗數")
    ongoing: int = Field(0, description="進行中")
    cancel: int = Field(0, description="取消數")
    check: int = Field(0, description="待確認數")
    total: int = Field(0, description="總數")
    pass_rate: float = Field(0.0, description="通過率 (%)")

    class Config:
        populate_by_name = True


class CategoryResult(BaseModel):
    """單一類別的測試結果"""
    name: str = Field(..., description="類別名稱")
    results_by_capacity: Dict[str, TestResultCount] = Field(
        default_factory=dict,
        description="各容量的測試結果"
    )
    total: TestResultCount = Field(
        default_factory=TestResultCount,
        description="該類別總計"
    )


class ProjectTestSummary(BaseModel):
    """專案測試摘要"""
    project_uid: str = Field(..., description="專案 UID")
    project_name: str = Field(..., description="專案名稱")
    capacities: List[str] = Field(default_factory=list, description="所有容量")
    categories: List[CategoryResult] = Field(
        default_factory=list,
        description="各類別測試結果"
    )
    summary: TestResultCount = Field(
        default_factory=TestResultCount,
        description="總體統計"
    )
```

### 3.3 SAF Client 方法 (`app/services/saf_client.py`)

```python
@retry(max_attempts=3, delay=1.0, exceptions=(httpx.ConnectError, httpx.TimeoutException))
@log_execution
async def get_project_test_summary(
    self,
    user_id: int,
    username: str,
    project_uid: str
) -> Dict[str, Any]:
    """
    取得單一專案的測試摘要
    
    Args:
        user_id: 使用者 ID
        username: 使用者名稱
        project_uid: 專案 UID
        
    Returns:
        包含測試摘要的字典
        
    Raises:
        SAFAPIError: API 呼叫失敗
        SAFConnectionError: 連線失敗
    """
    url = f"{self.settings.saf_api_base_url}/project/listOneProjectSummary"
    self.logger.debug(f"Getting project test summary from: {url}")
    
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Authorization": str(user_id),
        "Authorization_name": username,
    }
    
    try:
        async with self._get_client() as client:
            response = await client.post(
                url,
                headers=headers,
                json={
                    "projectId": "",
                    "projectUid": project_uid,
                },
            )
            
            if response.status_code == 200:
                data = response.json()
                self.logger.info(f"Retrieved test summary for project: {project_uid}")
                return data
            elif response.status_code == 404:
                raise SAFAPIError(
                    f"Project not found: {project_uid}",
                    status_code=404,
                    error_code="PROJECT_NOT_FOUND"
                )
            else:
                raise SAFAPIError(
                    f"Failed to get project test summary: {response.status_code}",
                    status_code=response.status_code
                )
                
    except httpx.ConnectError as e:
        self.logger.error(f"Connection error: {e}")
        raise SAFConnectionError(f"Failed to connect to SAF: {e}")
    except httpx.TimeoutException as e:
        self.logger.error(f"Timeout error: {e}")
        raise SAFConnectionError(f"Connection timeout: {e}")
```

### 3.4 路由端點 (`app/routers/projects.py`)

```python
@router.get(
    "/{project_uid}/test-summary",
    response_model=APIResponse,
    summary="取得專案測試摘要"
)
async def get_project_test_summary(
    project_uid: str,
    auth: AuthInfo = Depends(get_auth_info),
    client: SAFClient = Depends(get_saf_client)
):
    """
    取得單一專案的測試結果摘要
    
    包含各測試類別 (Compatibility, Function, Performance 等) 的測試結果，
    並依容量 (512GB, 1024GB, 2048GB, 4096GB) 分類統計。
    
    結果格式: PASS/FAIL/ONGOING/CANCEL/CHECK
    """
    try:
        # 取得原始資料
        raw_data = await client.get_project_test_summary(
            user_id=auth.user_id,
            username=auth.username,
            project_uid=project_uid
        )
        
        # 轉換為友善格式
        result = _transform_test_summary(raw_data)
        
        return format_response(
            success=True,
            data=result
        )
        
    except SAFAPIError as e:
        if e.error_code == "PROJECT_NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=format_response(
                    success=False,
                    message=f"Project not found: {project_uid}",
                    error_code="PROJECT_NOT_FOUND"
                )
            )
        logger.error(f"SAF API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=format_response(
                success=False,
                message=str(e),
                error_code="SAF_API_ERROR"
            )
        )
    except SAFConnectionError as e:
        logger.error(f"SAF connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=format_response(
                success=False,
                message="Unable to connect to SAF server",
                error_code="CONNECTION_ERROR"
            )
        )


def _parse_result_string(result_str: str) -> Dict[str, int]:
    """
    解析結果字串
    
    Args:
        result_str: 如 "8/0/0/0/0" (PASS/FAIL/ONGOING/CANCEL/CHECK)
        
    Returns:
        {'pass': 8, 'fail': 0, 'ongoing': 0, 'cancel': 0, 'check': 0}
    """
    parts = result_str.split("/")
    if len(parts) != 5:
        return {"pass": 0, "fail": 0, "ongoing": 0, "cancel": 0, "check": 0}
    
    try:
        return {
            "pass": int(parts[0]),
            "fail": int(parts[1]),
            "ongoing": int(parts[2]),
            "cancel": int(parts[3]),
            "check": int(parts[4]),
        }
    except ValueError:
        return {"pass": 0, "fail": 0, "ongoing": 0, "cancel": 0, "check": 0}


def _transform_test_summary(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    將 SAF 原始資料轉換為友善格式
    """
    project_uid = raw_data.get("key", "")
    project_name = raw_data.get("projectName", "")
    categories_raw = raw_data.get("testResultByMainCategory", [])
    
    # 收集所有容量
    all_capacities = set()
    categories = []
    
    # 總計
    total_pass = 0
    total_fail = 0
    total_ongoing = 0
    total_cancel = 0
    total_check = 0
    
    for cat_data in categories_raw:
        cat_name = cat_data.get("mainCategory", "Unknown")
        results_by_capacity = {}
        
        cat_pass = 0
        cat_fail = 0
        cat_ongoing = 0
        cat_cancel = 0
        cat_check = 0
        
        for cap_data in cat_data.get("testResultByCapacity", []):
            capacity = cap_data.get("capacity", "Unknown")
            result_str = cap_data.get("result", "0/0/0/0/0")
            
            all_capacities.add(capacity)
            
            result = _parse_result_string(result_str)
            result_total = sum(result.values())
            pass_rate = (result["pass"] / result_total * 100) if result_total > 0 else 0.0
            
            results_by_capacity[capacity] = {
                **result,
                "total": result_total,
                "pass_rate": round(pass_rate, 2)
            }
            
            cat_pass += result["pass"]
            cat_fail += result["fail"]
            cat_ongoing += result["ongoing"]
            cat_cancel += result["cancel"]
            cat_check += result["check"]
        
        cat_total = cat_pass + cat_fail + cat_ongoing + cat_cancel + cat_check
        cat_pass_rate = (cat_pass / cat_total * 100) if cat_total > 0 else 0.0
        
        categories.append({
            "name": cat_name,
            "results_by_capacity": results_by_capacity,
            "total": {
                "pass": cat_pass,
                "fail": cat_fail,
                "ongoing": cat_ongoing,
                "cancel": cat_cancel,
                "check": cat_check,
                "total": cat_total,
                "pass_rate": round(cat_pass_rate, 2)
            }
        })
        
        total_pass += cat_pass
        total_fail += cat_fail
        total_ongoing += cat_ongoing
        total_cancel += cat_cancel
        total_check += cat_check
    
    overall_total = total_pass + total_fail + total_ongoing + total_cancel + total_check
    overall_pass_rate = (total_pass / overall_total * 100) if overall_total > 0 else 0.0
    
    # 排序容量 (按數字大小)
    def sort_capacity(cap: str) -> int:
        try:
            return int(cap.replace("GB", "").replace("TB", "000"))
        except ValueError:
            return 0
    
    sorted_capacities = sorted(list(all_capacities), key=sort_capacity)
    
    return {
        "project_uid": project_uid,
        "project_name": project_name,
        "capacities": sorted_capacities,
        "categories": categories,
        "summary": {
            "total_pass": total_pass,
            "total_fail": total_fail,
            "total_ongoing": total_ongoing,
            "total_cancel": total_cancel,
            "total_check": total_check,
            "overall_total": overall_total,
            "overall_pass_rate": round(overall_pass_rate, 2)
        }
    }
```

---

## 4. 測試規劃

### 4.1 模擬資料 (`tests/fixtures/mock_responses.py`)

```python
MOCK_PROJECT_TEST_SUMMARY = {
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
        }
    ]
}
```

### 4.2 單元測試

```python
# tests/unit/test_projects.py

class TestParseResultString:
    """測試結果字串解析"""
    
    def test_parse_normal_result(self):
        result = _parse_result_string("8/1/2/0/1")
        assert result == {
            "pass": 8, "fail": 1, "ongoing": 2, "cancel": 0, "check": 1
        }
    
    def test_parse_all_zeros(self):
        result = _parse_result_string("0/0/0/0/0")
        assert result == {
            "pass": 0, "fail": 0, "ongoing": 0, "cancel": 0, "check": 0
        }
    
    def test_parse_invalid_format(self):
        result = _parse_result_string("invalid")
        assert result == {
            "pass": 0, "fail": 0, "ongoing": 0, "cancel": 0, "check": 0
        }


class TestTransformTestSummary:
    """測試資料轉換"""
    
    def test_transform_basic(self):
        result = _transform_test_summary(MOCK_PROJECT_TEST_SUMMARY)
        
        assert result["project_uid"] == "test-project-uid-001"
        assert result["project_name"] == "Test Project Name"
        assert "512GB" in result["capacities"]
        assert len(result["categories"]) == 2
        
    def test_transform_calculates_totals(self):
        result = _transform_test_summary(MOCK_PROJECT_TEST_SUMMARY)
        
        # 驗證總計
        summary = result["summary"]
        assert summary["total_pass"] == 53  # 8+10+15+20
        assert summary["total_fail"] == 3   # 0+1+2+0
```

### 4.3 整合測試

```python
# tests/integration/test_projects_api.py

class TestProjectTestSummaryAPI:
    """測試專案測試摘要 API"""
    
    @patch("app.services.saf_client.SAFClient.get_project_test_summary")
    def test_get_test_summary_success(
        self, mock_get_summary, client: TestClient
    ):
        mock_get_summary.return_value = MOCK_PROJECT_TEST_SUMMARY
        
        response = client.get(
            "/api/v1/projects/test-uid/test-summary",
            headers={
                "Authorization": "150",
                "Authorization-Name": "test_user"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["project_uid"] == "test-project-uid-001"
    
    def test_get_test_summary_unauthorized(self, client: TestClient):
        response = client.get("/api/v1/projects/test-uid/test-summary")
        assert response.status_code == 401
    
    @patch("app.services.saf_client.SAFClient.get_project_test_summary")
    def test_get_test_summary_not_found(
        self, mock_get_summary, client: TestClient
    ):
        mock_get_summary.side_effect = SAFAPIError(
            "Project not found",
            status_code=404,
            error_code="PROJECT_NOT_FOUND"
        )
        
        response = client.get(
            "/api/v1/projects/invalid-uid/test-summary",
            headers={
                "Authorization": "150",
                "Authorization-Name": "test_user"
            }
        )
        
        assert response.status_code == 404
```

---

## 5. 文件更新

### 5.1 更新 README.md API 端點表格

```markdown
| 端點 | 方法 | 說明 |
|------|------|------|
| `/health` | GET | 健康檢查 |
| `/config` | GET | 取得設定資訊 |
| `/api/v1/auth/login` | POST | 登入 SAF |
| `/api/v1/auth/login-with-config` | POST | 使用設定檔登入 |
| `/api/v1/projects` | GET | 取得專案列表 |
| `/api/v1/projects/summary` | GET | 取得專案統計 |
| `/api/v1/projects/{project_uid}/test-summary` | GET | 取得專案測試摘要 | ← 新增
```

### 5.2 更新 docs/API.md

在文件中新增完整的 API 使用說明，包含請求、回應範例和 cURL 指令。

---

## 6. 開發步驟

### Phase 1: 準備 (15 分鐘)
- [ ] 閱讀並確認規劃文件
- [ ] 確認 SAF API 回應結構

### Phase 2: 資料模型 (15 分鐘)
- [ ] 新增 `TestResultCount` schema
- [ ] 新增 `CategoryResult` schema
- [ ] 新增 `ProjectTestSummary` schema

### Phase 3: SAF Client (20 分鐘)
- [ ] 新增 `get_project_test_summary()` 方法
- [ ] 撰寫單元測試

### Phase 4: 路由端點 (30 分鐘)
- [ ] 新增 `_parse_result_string()` 輔助函數
- [ ] 新增 `_transform_test_summary()` 轉換函數
- [ ] 新增 `/projects/{project_uid}/test-summary` 端點
- [ ] 撰寫整合測試

### Phase 5: 測試與文件 (20 分鐘)
- [ ] 執行所有測試確認通過
- [ ] 更新 README.md
- [ ] 更新 docs/API.md
- [ ] 手動測試 API

### Phase 6: 部署 (10 分鐘)
- [ ] 重新建置 Docker 映像
- [ ] 重新啟動容器
- [ ] 驗證 API 功能

---

## 7. 使用流程

```
┌─────────────────────────────────────────────────────────────────┐
│                        使用流程                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 登入取得認證                                                  │
│     POST /api/v1/auth/login                                     │
│     → 取得 user_id, username                                     │
│                                                                 │
│  2. 取得專案列表                                                  │
│     GET /api/v1/projects                                        │
│     → 找到目標專案的 projectUid                                   │
│                                                                 │
│  3. 取得專案測試摘要                                              │
│     GET /api/v1/projects/{projectUid}/test-summary              │
│     → 取得各類別、各容量的測試結果統計                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 完整 cURL 範例

```bash
# Step 1: 登入
LOGIN_RESULT=$(curl -s -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}')

USER_ID=$(echo $LOGIN_RESULT | jq -r '.data.id')
USERNAME=$(echo $LOGIN_RESULT | jq -r '.data.name')

echo "Logged in as: $USERNAME (ID: $USER_ID)"

# Step 2: 取得專案列表，找到目標專案
curl -s http://localhost:8080/api/v1/projects \
  -H "Authorization: $USER_ID" \
  -H "Authorization-Name: $USERNAME" | jq '.data.data[0].projectUid'

# Step 3: 取得專案測試摘要
PROJECT_UID="00e11fc25a3f454e9e3860ff67dd2c07"

curl -s http://localhost:8080/api/v1/projects/$PROJECT_UID/test-summary \
  -H "Authorization: $USER_ID" \
  -H "Authorization-Name: $USERNAME" | jq
```

---

## 8. 預估時間

| 階段 | 預估時間 |
|------|---------|
| Phase 1: 準備 | 15 分鐘 |
| Phase 2: 資料模型 | 15 分鐘 |
| Phase 3: SAF Client | 20 分鐘 |
| Phase 4: 路由端點 | 30 分鐘 |
| Phase 5: 測試與文件 | 20 分鐘 |
| Phase 6: 部署 | 10 分鐘 |
| **總計** | **約 2 小時** |

---

## 9. 注意事項

1. **projectUid vs projectId**: SAF API 需要 `projectUid`，不是 `projectId`
2. **結果格式**: 結果字串格式為 `PASS/FAIL/ONGOING/CANCEL/CHECK`
3. **容量排序**: 容量需按數字大小排序 (512GB < 1024GB < 2048GB)
4. **錯誤處理**: 專案不存在時應返回 404
5. **效能考量**: 此 API 回應時間約 1-2 秒，可考慮加入快取

---

## 10. 未來擴展

可考慮新增的功能：

1. **快取機制**: 使用 Redis 快取測試摘要，減少 SAF API 呼叫
2. **篩選功能**: 支援只查詢特定類別或容量的結果
3. **歷史記錄**: 追蹤測試結果的變化趨勢
4. **批次查詢**: 支援一次查詢多個專案的摘要
5. **Webhook**: 當測試結果變化時發送通知
