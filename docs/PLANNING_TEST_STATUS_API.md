# Test Status API 規劃文件

## 1. 需求概述

建立一個 API，可以查詢 SAF 系統的測試狀態 (`/api/status`)，支援依專案名稱搜尋測試工作的詳細資訊。

---

## 2. SAF 原始 API 分析

### 2.1 請求資訊

| 項目 | 內容 |
|------|------|
| **URL** | `https://saf.siliconmotion.com.tw:3004/api/status` |
| **Method** | POST |
| **Content-Type** | application/json |

### 2.2 Query Parameters

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `page` | int | 否 | 頁碼，預設 1 |
| `size` | int | 否 | 每頁筆數，預設 50 |

### 2.3 Request Headers

| Header | 說明 |
|--------|------|
| `Authorization` | 使用者 ID (數字字串，如 "150") |
| `Authorization_name` | 使用者名稱 |
| `Content-Type` | application/json |

### 2.4 Request Body

```json
{
  "userId": 150,
  "q": "new_project_name = \"Client_PCIe_Micron_Springsteen_SM2508_Micron B68S TLC\"",
  "sort": {}
}
```

| 欄位 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `userId` | int | 是 | 使用者 ID |
| `q` | string | 是 | 查詢條件，格式為 `欄位名 = "值"` |
| `sort` | object | 否 | 排序條件，可為空物件 `{}` |

#### 查詢語法 (`q` 欄位)

- 格式: `欄位名 = "值"`
- 可查詢欄位 (推測):
  - `new_project_name`: 完整專案名稱
  - `projectName`: 專案名稱 (短名)
  - `testStatus`: 測試狀態
  - `sampleId`: 樣品 ID
  - 其他欄位待確認

### 2.5 Response Body

```json
{
  "items": [
    {
      "testJobId": "f30964a6da3f11f08e7e0242ac280004",
      "isNotification": true,
      "testItem": "Primary Drive Firmware Upgrade Check",
      "testStatus": "PASS",
      "allStatus": ["CHECK", "PASS", "FAIL", "INTERRUPT", "ONGOING", "CANCEL", "CONDITIONAL PASS"],
      "sampleId": "SSD-X-05498",
      "platform": "NB-SSD-0736",
      "position": "SAF1001-0736",
      "mainboardManufacturer": "Dell",
      "mainboardModel": "Latitude 5420",
      "projectName": "Springsteen",
      "fw": "GB10YCFS",
      "duration": 7200,
      "startTime": "2025-12-16T02:00:00+00:00",
      "endTime": "2025-12-16T04:00:00+00:00",
      "user": "tk.chang",
      "updatedAt": "2025-12-16T05:27:44+00:00",
      "logPath": "/SAF_Workspace/prod/test_log/...",
      "driver": "Microsoft",
      "filesystem": "NTFS",
      "slot": "M.2",
      "aspm": "Default",
      "osName": "Windows11 x64 23H2 (OS Build 22631.4169)"
    }
  ],
  "total": 100,
  "page": 1,
  "size": 50
}
```

#### Response 欄位說明

| 欄位 | 類型 | 說明 |
|------|------|------|
| `testJobId` | string | 測試工作 ID (UUID) |
| `isNotification` | boolean | 是否發送通知 |
| `testItem` | string | 測試項目名稱 |
| `testStatus` | string | 測試狀態 |
| `allStatus` | string[] | 所有可能的狀態值 |
| `sampleId` | string | 樣品 ID |
| `platform` | string | 測試平台 |
| `position` | string | 測試位置 |
| `mainboardManufacturer` | string | 主機板製造商 |
| `mainboardModel` | string | 主機板型號 |
| `projectName` | string | 專案名稱 (短名) |
| `fw` | string | 韌體版本 |
| `duration` | int | 測試持續時間 (秒) |
| `startTime` | string | 開始時間 (ISO 8601) |
| `endTime` | string | 結束時間 (ISO 8601) |
| `user` | string | 執行測試的使用者 |
| `updatedAt` | string | 更新時間 (ISO 8601) |
| `logPath` | string | 測試日誌路徑 |
| `driver` | string | 驅動程式 |
| `filesystem` | string | 檔案系統 |
| `slot` | string | 插槽類型 |
| `aspm` | string | ASPM 設定 |
| `osName` | string | 作業系統名稱 |

---

## 3. 新 API 設計

### 3.1 API Endpoint

```
POST /api/v1/test-status/search
```

### 3.2 Request Schema

```json
{
  "query": "new_project_name = \"Client_PCIe_Micron_Springsteen_SM2508_Micron B68S TLC\"",
  "page": 1,
  "size": 50,
  "sort": {}
}
```

| 欄位 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `query` | string | 是 | 查詢條件 |
| `page` | int | 否 | 頁碼，預設 1 |
| `size` | int | 否 | 每頁筆數，預設 50，最大 100 |
| `sort` | object | 否 | 排序條件 |

### 3.3 Response Schema

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "test_job_id": "f30964a6da3f11f08e7e0242ac280004",
        "test_item": "Primary Drive Firmware Upgrade Check",
        "test_status": "PASS",
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
    "total": 100,
    "page": 1,
    "size": 50
  },
  "message": null,
  "timestamp": "2025-12-16T06:00:00Z"
}
```

---

## 4. 實作計畫

### 4.1 修改檔案清單

| 檔案 | 動作 | 說明 |
|------|------|------|
| `app/models/schemas.py` | 修改 | 新增 Request/Response Schema |
| `app/services/saf_client.py` | 修改 | 新增 `search_test_status()` 方法 |
| `app/routers/projects.py` | 修改 | 新增 `/test-status/search` 路由 |
| `tests/unit/test_schemas.py` | 修改 | 新增 Schema 測試 |
| `tests/unit/test_saf_client.py` | 修改 | 新增 SAF Client 測試 |
| `tests/integration/test_projects_api.py` | 修改 | 新增 API 整合測試 |

### 4.2 實作步驟

#### Step 1: 新增 Schemas (`app/models/schemas.py`)

```python
# ========== Test Status 相關 ==========

class TestStatusSearchRequest(BaseModel):
    """測試狀態搜尋請求"""
    query: str = Field(..., description="查詢條件，格式: 欄位名 = \"值\"")
    page: int = Field(1, ge=1, description="頁碼")
    size: int = Field(50, ge=1, le=100, description="每頁筆數")
    sort: Optional[Dict[str, Any]] = Field(default_factory=dict, description="排序條件")


class TestStatusItem(BaseModel):
    """測試狀態項目"""
    test_job_id: str = Field(..., description="測試工作 ID")
    test_item: str = Field(..., description="測試項目名稱")
    test_status: str = Field(..., description="測試狀態")
    sample_id: str = Field(..., description="樣品 ID")
    platform: str = Field("", description="測試平台")
    position: str = Field("", description="測試位置")
    mainboard_manufacturer: str = Field("", description="主機板製造商")
    mainboard_model: str = Field("", description="主機板型號")
    project_name: str = Field("", description="專案名稱")
    fw: str = Field("", description="韌體版本")
    duration: int = Field(0, description="測試持續時間 (秒)")
    start_time: Optional[str] = Field(None, description="開始時間")
    end_time: Optional[str] = Field(None, description="結束時間")
    user: str = Field("", description="執行測試的使用者")
    updated_at: Optional[str] = Field(None, description="更新時間")
    log_path: str = Field("", description="測試日誌路徑")
    driver: str = Field("", description="驅動程式")
    filesystem: str = Field("", description="檔案系統")
    slot: str = Field("", description="插槽類型")
    aspm: str = Field("", description="ASPM 設定")
    os_name: str = Field("", description="作業系統名稱")


class TestStatusSearchResponse(BaseModel):
    """測試狀態搜尋回應"""
    items: List[TestStatusItem] = Field(default_factory=list, description="測試狀態列表")
    total: int = Field(0, description="總筆數")
    page: int = Field(1, description="頁碼")
    size: int = Field(50, description="每頁筆數")
```

#### Step 2: 新增 SAF Client 方法 (`app/services/saf_client.py`)

```python
@retry(max_attempts=3, delay=1.0, exceptions=(httpx.ConnectError, httpx.TimeoutException))
@log_execution
async def search_test_status(
    self,
    user_id: int,
    username: str,
    query: str,
    page: int = 1,
    size: int = 50,
    sort: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    搜尋測試狀態
    
    Args:
        user_id: 使用者 ID
        username: 使用者名稱
        query: 查詢條件，格式: 欄位名 = "值"
        page: 頁碼
        size: 每頁筆數
        sort: 排序條件
        
    Returns:
        包含測試狀態列表的字典
    """
    url = f"{self.settings.saf_api_base_url}/status"
    
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Authorization": str(user_id),
        "Authorization_name": username,
    }
    
    try:
        async with self._get_client() as client:
            response = await client.post(
                f"{url}?page={page}&size={size}",
                headers=headers,
                json={
                    "userId": user_id,
                    "q": query,
                    "sort": sort or {},
                },
            )
            
            if response.status_code == 200:
                data = response.json()
                items_count = len(data.get("items", []))
                self.logger.info(f"Retrieved {items_count} test status items")
                return data
            else:
                raise SAFAPIError(
                    f"Failed to search test status: {response.status_code}",
                    status_code=response.status_code
                )
                
    except httpx.ConnectError as e:
        self.logger.error(f"Connection error: {e}")
        raise SAFConnectionError(f"Failed to connect to SAF: {e}")
    except httpx.TimeoutException as e:
        self.logger.error(f"Timeout error: {e}")
        raise SAFConnectionError(f"Connection timeout: {e}")
```

#### Step 3: 新增 Router (`app/routers/projects.py`)

```python
@router.post(
    "/test-status/search",
    response_model=APIResponse,
    summary="搜尋測試狀態"
)
async def search_test_status(
    request: TestStatusSearchRequest,
    auth: AuthInfo = Depends(get_auth_info),
    client: SAFClient = Depends(get_saf_client)
):
    """
    搜尋測試狀態
    
    查詢語法範例：
    - `new_project_name = "Client_PCIe_Micron_Springsteen_SM2508_Micron B68S TLC"`
    - `projectName = "Springsteen"`
    - `testStatus = "PASS"`
    - `sampleId = "SSD-X-05498"`
    """
    try:
        raw_data = await client.search_test_status(
            user_id=auth.user_id,
            username=auth.username,
            query=request.query,
            page=request.page,
            size=request.size,
            sort=request.sort
        )
        
        # 轉換為 snake_case 格式
        result = _transform_test_status_response(raw_data)
        
        return format_response(
            success=True,
            data=result
        )
        
    except SAFAPIError as e:
        # ... 錯誤處理
```

---

## 5. 測試計畫

### 5.1 單元測試

- [ ] `TestStatusSearchRequest` Schema 驗證
- [ ] `TestStatusItem` Schema 驗證
- [ ] `search_test_status()` 方法測試 (mock httpx)

### 5.2 整合測試

- [ ] 成功搜尋測試狀態
- [ ] 分頁功能測試
- [ ] 無結果測試
- [ ] 認證失敗測試

---

## 6. 待確認事項

1. [x] 確認 `q` 欄位支援的所有查詢欄位 - 已確認支援 `new_project_name`, `projectName`, `testStatus`, `sampleId`
2. [x] 確認 `sort` 欄位的格式和支援的排序欄位 - 可為空物件 `{}`
3. [x] 確認回應是否有其他欄位未列出 - 已完整列出
4. [ ] 確認是否需要額外的便利 API (如直接用專案名稱查詢)

---

## 7. 時程估計

| 項目 | 時間 | 狀態 |
|------|------|------|
| Schema 定義 | 15 分鐘 | ✅ 完成 |
| SAF Client 方法 | 20 分鐘 | ✅ 完成 |
| Router 實作 | 20 分鐘 | ✅ 完成 |
| 單元測試 | 30 分鐘 | ⏳ 待完成 |
| 整合測試 | 20 分鐘 | ⏳ 待完成 |
| 文件更新 | 15 分鐘 | ✅ 完成 |
| **總計** | **約 2 小時** | |

---

## 8. 實作記錄

### 2025-12-16 完成項目

1. **Schema 新增** (`app/models/schemas.py`)
   - `TestStatusSearchRequest`: 搜尋請求模型
   - `TestStatusItem`: 測試狀態項目模型
   - `TestStatusSearchResponse`: 搜尋回應模型

2. **SAF Client 方法** (`app/services/saf_client.py`)
   - `search_test_status()`: 搜尋測試狀態的非同步方法

3. **Router 路由** (`app/routers/projects.py`)
   - `POST /api/v1/projects/test-status/search`: 搜尋測試狀態端點
   - `_transform_test_status_item()`: 資料轉換函數

4. **文件更新** (`docs/API.md`)
   - 新增第 9 節「搜尋測試狀態」完整文件
