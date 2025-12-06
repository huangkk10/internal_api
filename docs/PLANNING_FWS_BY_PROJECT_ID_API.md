# ListFWsByProjectId API 規劃文件

> 建立日期: 2025-12-07  
> 功能目的: 新增依 Project ID 取得 Firmware 列表 API

---

## 1. 功能概述

### 1.1 目標
- 新增 `/api/v1/projects/{project_id}/firmwares` 端點
- 封裝 SAF 的 `ListFWsByProjectId` API
- 提供專案下所有 Firmware 版本列表

### 1.2 對應 SAF API

| 項目 | 說明 |
|------|------|
| **端點** | `POST https://saf.siliconmotion.com.tw:3004/api/project/ListFWsByProjectId` |
| **認證方式** | Header: `Authorization` (user id), `Authorization_name` (username) |
| **Content-Type** | `application/json` |
| **Request Body** | `{"projectId": "<project_id>"}` |

### 1.3 SAF API 回應結構

```json
{
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
```

### 1.4 回應欄位說明

| 欄位 | 類型 | 說明 |
|------|------|------|
| `fw` | string | Firmware 名稱 |
| `subVersion` | string | 子版本 (如 AA, AB, AC) |
| `projectUid` | string | 對應的 Project UID，可用於查詢測試摘要 |

---

## 2. API 設計

### 2.1 新增端點

| 路由 | 方法 | 說明 | 對應 SAF API |
|------|------|------|--------------|
| `/api/v1/projects/{project_id}/firmwares` | GET | 取得專案 Firmware 列表 | `POST :3004/api/project/ListFWsByProjectId` |

### 2.2 請求格式

```
GET /api/v1/projects/{project_id}/firmwares
```

**Path 參數:**
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `project_id` | string | ✅ | 專案 ID (從 `/api/v1/projects` 取得) |

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

#### 錯誤回應

| HTTP 狀態 | 錯誤碼 | 說明 |
|----------|--------|------|
| 401 | `MISSING_AUTH` | 缺少認證 Header |
| 404 | `PROJECT_NOT_FOUND` | 找不到專案 |
| 502 | `SAF_API_ERROR` | SAF API 呼叫失敗 |
| 503 | `CONNECTION_ERROR` | 無法連接 SAF |

### 2.4 cURL 範例

```bash
# 取得專案 Firmware 列表
curl http://localhost:8080/api/v1/projects/8e9fe3fa43694a2c8a7cef9e42620f60/firmwares \
  -H "Authorization: 150" \
  -H "Authorization-Name: Chunwei.Huang"
```

---

## 3. 實作規劃

### 3.1 修改檔案清單

| 檔案 | 操作 | 說明 |
|------|------|------|
| `app/services/saf_client.py` | 修改 | 新增 `get_fws_by_project_id()` 方法 |
| `app/routers/projects.py` | 修改 | 新增路由端點 |
| `tests/unit/test_saf_client.py` | 修改 | 新增單元測試 |
| `tests/fixtures/mock_responses.py` | 修改 | 新增模擬資料 |
| `tests/conftest.py` | 修改 | 新增 fixture |

### 3.2 SAF Client 方法

```python
@retry(max_attempts=3, delay=1.0, exceptions=(httpx.ConnectError, httpx.TimeoutException))
@log_execution
async def get_fws_by_project_id(
    self,
    user_id: int,
    username: str,
    project_id: str
) -> Dict[str, Any]:
    """
    依 Project ID 取得 Firmware 列表
    """
    url = f"{self.settings.saf_api_base_url}/project/ListFWsByProjectId"
    
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Authorization": str(user_id),
        "Authorization_name": username,
    }
    
    async with self._get_client() as client:
        response = await client.post(
            url,
            headers=headers,
            json={"projectId": project_id},
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise SAFAPIError("Project not found", status_code=404, error_code="PROJECT_NOT_FOUND")
        else:
            raise SAFAPIError(f"Failed: {response.status_code}", status_code=response.status_code)
```

### 3.3 路由端點

```python
@router.get(
    "/{project_id}/firmwares",
    response_model=APIResponse,
    summary="取得專案的 Firmware 列表"
)
async def get_project_firmwares(
    project_id: str,
    auth: AuthInfo = Depends(get_auth_info),
    client: SAFClient = Depends(get_saf_client)
):
    """依 Project ID 取得該專案下所有的 Firmware 版本列表"""
    result = await client.get_fws_by_project_id(
        user_id=auth.user_id,
        username=auth.username,
        project_id=project_id
    )
    return format_response(success=True, data=result)
```

---

## 4. 實作狀態

✅ **已完成** (2025-12-07)

- [x] SAF Client 方法: `get_fws_by_project_id()`
- [x] Router 端點: `GET /projects/{project_id}/firmwares`
- [x] 單元測試
- [x] Mock 資料

---

## 5. 使用場景

### 5.1 查詢專案下所有 Firmware 版本

```bash
# 1. 登入取得認證
# 2. 取得專案列表，找到 projectId
# 3. 依 projectId 取得 Firmware 列表
curl http://localhost:8080/api/v1/projects/8e9fe3fa43694a2c8a7cef9e42620f60/firmwares \
  -H "Authorization: 150" \
  -H "Authorization-Name: Chunwei.Huang"
```

### 5.2 取得特定 Firmware 的測試摘要

```bash
# 從 Firmware 列表取得 projectUid，再查詢測試摘要
curl http://localhost:8080/api/v1/projects/5d5b7d9763fb45bda79579f85a9a02f5/test-summary \
  -H "Authorization: 150" \
  -H "Authorization-Name: Chunwei.Huang"
```

---

## 6. 關聯 API

| API | 說明 |
|-----|------|
| `GET /projects` | 取得所有專案列表，可取得 `projectId` |
| `GET /projects/{project_id}/firmwares` | 依 projectId 取得 Firmware 列表 |
| `GET /projects/{project_uid}/test-summary` | 依 projectUid 取得測試摘要 |

