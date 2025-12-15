# Internal API Server

用於取得 SAF (Silicon Motion) 網站資訊的 API Server。

## 功能特色

- 🔐 SAF 登入認證
- 📊 取得專案列表
- 📈 專案統計摘要
- 🐳 Docker 容器化部署
- 📚 自動產生 API 文件 (Swagger UI)

## 快速開始

### 1. 複製設定檔

```bash
cp .env.example .env
```

### 2. 編輯 `.env` 填入您的 SAF 帳密

```env
SAF_USERNAME=your_username
SAF_PASSWORD=your_password
```

### 3. 選擇執行方式

#### 方式 A: 本地開發

```bash
# 建立虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝依賴
pip install -r requirements-dev.txt

# 啟動開發伺服器
./scripts/run_dev.sh
# 或
uvicorn app.main:app --reload --port 8080
```

#### 方式 B: Docker 部署

```bash
# 建置並啟動
docker-compose up -d

# 查看日誌
docker-compose logs -f

# 停止
docker-compose down
```

### 4. 存取 API

- **API 首頁**: http://localhost:8080
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **健康檢查**: http://localhost:8080/health

## API 端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/health` | GET | 健康檢查 |
| `/config` | GET | 取得設定資訊 |
| `/api/v1/auth/login` | POST | 登入 SAF |
| `/api/v1/auth/login-with-config` | POST | 使用設定檔登入 |
| `/api/v1/projects` | GET | 取得專案列表 |
| `/api/v1/projects/summary` | GET | 取得專案統計 |
| `/api/v1/projects/{project_id}/firmwares` | GET | 取得專案 Firmware 列表 |
| `/api/v1/projects/{project_uid}/test-summary` | GET | 取得專案測試摘要 |
| `/api/v1/projects/{project_uid}/firmware-summary` | GET | 取得 Firmware 詳細摘要 |
| `/api/v1/projects/{project_uid}/full-summary` | GET | 取得完整專案摘要 |
| `/api/v1/projects/{project_uid}/test-details` | GET | 取得測試項目詳細資料 |
| `/api/v1/projects/{project_id}/dashboard` | GET | 取得專案儀表板 |
| `/api/v1/projects/known-issues` | POST | 取得 Known Issues 列表 |

詳細 API 使用說明請參考 [docs/API.md](docs/API.md)。

## 使用範例

### 登入

```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

### 取得專案列表

```bash
curl http://localhost:8080/api/v1/projects \
  -H "Authorization: 150" \
  -H "Authorization-Name: your_username"
```

## 測試

```bash
# 執行所有測試
./scripts/run_tests.sh

# 只執行單元測試
./scripts/run_tests.sh unit

# 執行並產生覆蓋率報告
./scripts/run_tests.sh coverage
```

## 專案結構

```
internal_api/
├── app/                    # 主應用程式
│   ├── main.py            # FastAPI 入口
│   ├── config.py          # 設定管理
│   ├── routers/           # API 路由
│   ├── services/          # 業務邏輯
│   ├── models/            # 資料模型
│   └── middlewares/       # 中介軟體
├── lib/                   # 共用函式庫
├── tests/                 # 測試
├── scripts/               # 工具腳本
├── docs/                  # 文件
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 環境變數

| 變數 | 說明 | 預設值 |
|------|------|--------|
| `SAF_BASE_URL` | SAF 網站 URL | `https://saf.siliconmotion.com.tw` |
| `SAF_LOGIN_PORT` | SAF 登入 Port | `8000` |
| `SAF_API_PORT` | SAF API Port | `3004` |
| `SAF_USERNAME` | SAF 帳號 | - |
| `SAF_PASSWORD` | SAF 密碼 | - |
| `API_PORT` | API Server Port | `8080` |
| `DEBUG` | 除錯模式 | `false` |
| `LOG_LEVEL` | 日誌等級 | `INFO` |

## 授權

MIT License
