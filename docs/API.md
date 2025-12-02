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
