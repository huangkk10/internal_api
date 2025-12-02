# Internal API Server 專案規劃文件

> 建立日期: 2025-12-02  
> 專案目的: 建立一個 API Server，用於取得 SAF (Silicon Motion) 網站的資訊

---

## 1. 專案概述

### 1.1 目標
- 封裝 SAF 網站的 API，提供統一的存取介面
- 簡化認證流程，自動管理 Session
- 提供乾淨的 RESTful API 供內部系統使用

### 1.2 SAF 網站資訊
| 項目 | 說明 |
|------|------|
| 登入 API | `https://saf.siliconmotion.com.tw:8000/api/login` |
| 資料 API | `https://saf.siliconmotion.com.tw:3004/api/*` |
| 認證方式 | Header: `Authorization` (user id), `Authorization_name` (username) |
| 網路限制 | 需繞過 Proxy (`--noproxy '*'`) |

---

## 2. 技術選型

| 項目 | 選擇 | 原因 |
|------|------|------|
| **語言** | Python 3.10+ | 快速開發、豐富生態系 |
| **Web 框架** | FastAPI | 高效能、自動 API 文件、型別支援 |
| **HTTP Client** | httpx | 支援 async、可控制 proxy |
| **資料驗證** | Pydantic | FastAPI 原生整合 |
| **環境變數** | python-dotenv | 安全管理敏感資訊 |
| **ASGI Server** | Uvicorn | 高效能、支援熱重載 |

---

## 3. 專案結構

```
internal_api/
│
├── docs/                         # 📚 文件
│   ├── PLANNING.md               #    本規劃文件
│   ├── API.md                    #    API 使用說明
│   ├── DEVELOPMENT.md            #    開發指南
│   ├── DEPLOYMENT.md             #    部署指南
│   ├── CHANGELOG.md              #    版本更新紀錄
│   └── images/                   #    文件用圖片
│       └── architecture.png      #    架構圖
│
├── lib/                          # 📦 共用函式庫
│   ├── __init__.py
│   ├── exceptions.py             #    自定義例外
│   ├── logger.py                 #    日誌工具
│   ├── utils.py                  #    通用工具函數
│   └── decorators.py             #    裝飾器
│
├── app/                          # 🚀 主應用程式
│   ├── __init__.py               #    套件初始化
│   ├── main.py                   #    FastAPI 應用入口
│   ├── config.py                 #    設定管理
│   │
│   ├── routers/                  # 📡 API 路由
│   │   ├── __init__.py
│   │   ├── auth.py               #    認證相關路由
│   │   └── projects.py           #    專案資料路由
│   │
│   ├── services/                 # ⚙️ 業務邏輯服務
│   │   ├── __init__.py
│   │   └── saf_client.py         #    SAF API 封裝
│   │
│   ├── models/                   # 📦 資料模型
│   │   ├── __init__.py
│   │   └── schemas.py            #    Pydantic 資料模型
│   │
│   └── middlewares/              # 🔗 中介軟體
│       ├── __init__.py
│       └── error_handler.py      #    全域錯誤處理
│
├── tests/                        # 🧪 測試
│   ├── __init__.py
│   ├── conftest.py               #    pytest 共用 fixtures
│   │
│   ├── unit/                     # 單元測試
│   │   ├── __init__.py
│   │   ├── test_config.py        #    測試設定模組
│   │   ├── test_schemas.py       #    測試資料模型
│   │   ├── test_saf_client.py    #    測試 SAF Client
│   │   └── test_lib.py           #    測試共用函式庫
│   │
│   ├── integration/              # 整合測試
│   │   ├── __init__.py
│   │   ├── test_auth_api.py      #    測試認證 API
│   │   └── test_projects_api.py  #    測試專案 API
│   │
│   └── fixtures/                 # 測試資料
│       ├── __init__.py
│       ├── mock_responses.py     #    模擬 SAF API 回應
│       └── sample_data.json      #    範例測試資料
│
├── scripts/                      # 📜 工具腳本
│   ├── run_dev.sh                #    開發環境啟動腳本
│   ├── run_tests.sh              #    執行測試腳本
│   └── generate_docs.sh          #    產生文件腳本
│
├── Dockerfile                    # 🐳 Docker 映像檔定義
├── docker-compose.yml            #    Docker Compose 編排
├── .dockerignore                 #    Docker 忽略檔案
│
├── requirements.txt              # 📋 生產環境依賴
├── requirements-dev.txt          #    開發/測試環境依賴
├── pyproject.toml                #    專案設定 (pytest, black, etc.)
├── pytest.ini                    #    pytest 設定 (選用)
│
├── .env                          # 🔐 環境變數 (不入版控)
├── .env.example                  #    環境變數範例
├── .gitignore                    #    Git 忽略檔案
└── README.md                     #    專案說明
```

### 3.1 目錄說明

| 目錄 | 用途 |
|------|------|
| `docs/` | 專案文件 (規劃、API、開發指南等) |
| `lib/` | 共用函式庫 (例外、日誌、工具函數) |
| `app/` | 主要應用程式碼 |
| `app/routers/` | FastAPI 路由定義 |
| `app/services/` | 業務邏輯、外部 API 封裝 |
| `app/models/` | Pydantic 資料模型 |
| `app/middlewares/` | FastAPI 中介軟體 |
| `tests/` | 所有測試程式碼 |
| `tests/unit/` | 單元測試 (不需外部服務) |
| `tests/integration/` | 整合測試 (測試完整 API) |
| `tests/fixtures/` | 測試用的模擬資料和 fixtures |
| `scripts/` | 常用操作腳本 |

### 3.2 docs/ 文件規劃

| 檔案 | 內容 |
|------|------|
| `PLANNING.md` | 專案規劃文件 (本文件) |
| `API.md` | API 端點說明、請求/回應範例 |
| `DEVELOPMENT.md` | 開發環境設定、程式碼規範 |
| `DEPLOYMENT.md` | Docker 部署、生產環境設定 |
| `CHANGELOG.md` | 版本更新紀錄 (遵循 Keep a Changelog) |
| `images/` | 文件用圖片 (架構圖、流程圖) |

### 3.3 lib/ 共用函式庫規劃

#### `lib/exceptions.py` - 自定義例外

```python
class InternalAPIException(Exception):
    """基礎例外類別"""
    pass

class SAFConnectionError(InternalAPIException):
    """SAF 連線錯誤"""
    pass

class SAFAuthenticationError(InternalAPIException):
    """SAF 認證錯誤"""
    pass

class SAFAPIError(InternalAPIException):
    """SAF API 呼叫錯誤"""
    pass
```

#### `lib/logger.py` - 日誌工具

```python
import logging
from app.config import settings

def get_logger(name: str) -> logging.Logger:
    """取得設定好的 logger"""
    logger = logging.getLogger(name)
    logger.setLevel(settings.log_level)
    # ... 設定 handler 和 formatter
    return logger
```

#### `lib/utils.py` - 通用工具函數

```python
from datetime import datetime
from typing import Any, Dict

def timestamp_to_datetime(ts: Dict[str, Any]) -> datetime:
    """將 SAF 的 timestamp 格式轉換為 datetime"""
    pass

def format_response(success: bool, data: Any = None, message: str = None) -> Dict:
    """統一回應格式"""
    return {
        "success": success,
        "data": data,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
```

#### `lib/decorators.py` - 裝飾器

```python
import functools
from lib.logger import get_logger

def log_execution(func):
    """記錄函數執行的裝飾器"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.info(f"Executing {func.__name__}")
        result = await func(*args, **kwargs)
        logger.info(f"Completed {func.__name__}")
        return result
    return wrapper

def retry(max_attempts: int = 3, delay: float = 1.0):
    """重試裝飾器"""
    pass
```

---

## 4. API 設計

### 4.1 路由規劃

| 路由 | 方法 | 說明 | 對應 SAF API |
|------|------|------|--------------|
| `/health` | GET | 健康檢查 | - |
| `/api/v1/auth/login` | POST | 登入 SAF 取得認證 | `POST :8000/api/login` |
| `/api/v1/projects` | GET | 取得所有專案列表 | `POST :3004/api/project/listAllProjectsDetails` |
| `/api/v1/projects/{project_uid}` | GET | 取得單一專案詳情 | 待確認 |

### 4.2 回應格式

```json
{
  "success": true,
  "data": { ... },
  "message": null,
  "timestamp": "2025-12-02T10:00:00Z"
}
```

### 4.3 錯誤回應格式

```json
{
  "success": false,
  "data": null,
  "message": "Error description",
  "timestamp": "2025-12-02T10:00:00Z"
}
```

---

## 5. 核心模組設計

### 5.1 SAF Client (`services/saf_client.py`)

```python
class SAFClient:
    """SAF API 封裝類別"""
    
    async def login(username: str, password: str) -> AuthResponse
    async def get_all_projects(auth: AuthInfo) -> List[Project]
    async def get_project_detail(auth: AuthInfo, project_uid: str) -> Project
```

**關鍵實作要點:**
- 使用 `httpx.AsyncClient(trust_env=False)` 繞過系統 Proxy
- 實作連線重試機制
- 統一錯誤處理

### 5.2 設定管理 (`config.py`)

```python
class Settings(BaseSettings):
    # SAF 設定
    SAF_BASE_URL: str = "https://saf.siliconmotion.com.tw"
    SAF_LOGIN_PORT: int = 8000
    SAF_API_PORT: int = 3004
    
    # 預設認證 (可選)
    SAF_USERNAME: Optional[str] = None
    SAF_PASSWORD: Optional[str] = None
    
    # Server 設定
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8080
    DEBUG: bool = False
```

---

## 6. 資料模型

### 6.1 認證相關

```python
class LoginRequest(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    id: int
    name: str
    mail: str
```

### 6.2 專案相關

```python
class Project(BaseModel):
    key: str
    projectUid: str
    projectId: str
    projectName: str
    productCategory: str
    customer: str
    controller: str
    subVersion: str
    nand: str
    fw: str
    pl: str
    status: int
    visible: bool
    taskId: Optional[str]
    nasLogFolder: Optional[str]
    children: Optional[List['Project']]
```

---

## 7. 環境變數

### 7.1 `.env.example` (範本檔案，可 commit)

```env
# ============================================
# SAF API Server 環境變數設定
# ============================================
# 複製此檔案為 .env 並填入實際值
# cp .env.example .env
# ============================================

# --------------------------------------------
# SAF 連線設定
# --------------------------------------------
SAF_BASE_URL=https://saf.siliconmotion.com.tw
SAF_LOGIN_PORT=8000
SAF_API_PORT=3004

# --------------------------------------------
# SAF 認證資訊 (必填)
# --------------------------------------------
# 您的 SAF 帳號
SAF_USERNAME=your_username_here
# 您的 SAF 密碼
SAF_PASSWORD=your_password_here

# --------------------------------------------
# API Server 設定
# --------------------------------------------
API_HOST=0.0.0.0
API_PORT=8080
DEBUG=false

# --------------------------------------------
# 日誌設定
# --------------------------------------------
LOG_LEVEL=INFO
```

### 7.2 `.env` (實際設定檔，不可 commit)

```env
# SAF 連線設定
SAF_BASE_URL=https://saf.siliconmotion.com.tw
SAF_LOGIN_PORT=8000
SAF_API_PORT=3004

# SAF 認證資訊
SAF_USERNAME=Chunwei.Huang
SAF_PASSWORD=your_actual_password

# API Server 設定
API_HOST=0.0.0.0
API_PORT=8080
DEBUG=true

# 日誌設定
LOG_LEVEL=DEBUG
```

### 7.3 Config 模組設計 (`app/config.py`)

```python
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """
    應用程式設定
    
    優先順序: 環境變數 > .env 檔案 > 預設值
    """
    
    # ========== SAF 連線設定 ==========
    saf_base_url: str = Field(
        default="https://saf.siliconmotion.com.tw",
        description="SAF 網站基礎 URL"
    )
    saf_login_port: int = Field(
        default=8000,
        description="SAF 登入 API Port"
    )
    saf_api_port: int = Field(
        default=3004,
        description="SAF 資料 API Port"
    )
    
    # ========== SAF 認證資訊 ==========
    saf_username: Optional[str] = Field(
        default=None,
        description="SAF 登入帳號"
    )
    saf_password: Optional[str] = Field(
        default=None,
        description="SAF 登入密碼"
    )
    
    # ========== API Server 設定 ==========
    api_host: str = Field(
        default="0.0.0.0",
        description="API Server 監聽 Host"
    )
    api_port: int = Field(
        default=8080,
        description="API Server 監聽 Port"
    )
    debug: bool = Field(
        default=False,
        description="是否開啟除錯模式"
    )
    
    # ========== 日誌設定 ==========
    log_level: str = Field(
        default="INFO",
        description="日誌等級 (DEBUG, INFO, WARNING, ERROR)"
    )
    
    # ========== 計算屬性 ==========
    @property
    def saf_login_url(self) -> str:
        """SAF 登入 API 完整 URL"""
        return f"{self.saf_base_url}:{self.saf_login_port}/api/login"
    
    @property
    def saf_api_base_url(self) -> str:
        """SAF 資料 API 基礎 URL"""
        return f"{self.saf_base_url}:{self.saf_api_port}/api"
    
    @property
    def has_credentials(self) -> bool:
        """是否已設定認證資訊"""
        return bool(self.saf_username and self.saf_password)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  # 環境變數不區分大小寫


@lru_cache()
def get_settings() -> Settings:
    """
    取得應用程式設定 (單例模式)
    
    使用 lru_cache 確保只建立一次 Settings 實例
    """
    return Settings()


# 方便直接 import 使用
settings = get_settings()
```

### 7.4 Config 使用方式

```python
# 方式 1: 直接 import settings
from app.config import settings

print(settings.saf_username)
print(settings.saf_login_url)

# 方式 2: 使用 Dependency Injection (推薦用於 FastAPI)
from fastapi import Depends
from app.config import Settings, get_settings

@app.get("/info")
async def get_info(settings: Settings = Depends(get_settings)):
    return {
        "saf_url": settings.saf_base_url,
        "has_credentials": settings.has_credentials
    }
```

### 7.5 `.gitignore` 設定

```gitignore
# 環境變數 (包含敏感資訊)
.env
.env.local
.env.*.local

# 保留範本
!.env.example
```

### 7.6 設定檔安全性注意事項

| 檔案 | 是否 Commit | 說明 |
|------|-------------|------|
| `.env.example` | ✅ 是 | 範本檔，不含真實密碼 |
| `.env` | ❌ 否 | 實際設定，包含密碼 |
| `app/config.py` | ✅ 是 | 程式碼，不含密碼 |

### 7.7 首次設定流程

```bash
# 1. 複製範本檔案
cp .env.example .env

# 2. 編輯 .env 填入您的帳號密碼
nano .env
# 或
code .env

# 3. 確認設定正確
python -c "from app.config import settings; print(f'User: {settings.saf_username}')"
```

---

## 8. 開發計畫

### Phase 1: 基礎建設 (Day 1)
- [ ] 初始化專案結構 (所有目錄)
- [ ] 設定 Python 虛擬環境
- [ ] 安裝依賴套件 (requirements.txt, requirements-dev.txt)
- [ ] 建立基本設定檔 (.env, .gitignore, pyproject.toml)
- [ ] 建立共用函式庫 (lib/)

### Phase 2: 核心功能 (Day 1-2)
- [ ] 實作 Config 模組 (`app/config.py`)
- [ ] 實作 SAF Client (`app/services/saf_client.py`)
- [ ] 實作資料模型 (`app/models/schemas.py`)
- [ ] 實作登入 API (`/api/v1/auth/login`)
- [ ] 實作專案列表 API (`/api/v1/projects`)

### Phase 3: 測試 (Day 2)
- [ ] 建立 pytest 設定 (pyproject.toml, conftest.py)
- [ ] 建立測試 fixtures (mock_responses.py, sample_data.json)
- [ ] 撰寫單元測試 (test_config.py, test_saf_client.py, test_lib.py)
- [ ] 撰寫整合測試 (test_auth_api.py, test_projects_api.py)
- [ ] 執行測試並確保通過

### Phase 4: Docker 部署 (Day 2-3)
- [ ] 建立 Dockerfile
- [ ] 建立 docker-compose.yml
- [ ] 建立 .dockerignore
- [ ] 測試容器建置與執行
- [ ] 測試其他電腦連線

### Phase 5: 文件完善 (Day 3)
- [ ] 撰寫 README.md
- [ ] 撰寫 API.md (API 使用說明)
- [ ] 撰寫 DEVELOPMENT.md (開發指南)
- [ ] 撰寫 DEPLOYMENT.md (部署指南)
- [ ] 建立 CHANGELOG.md

### Phase 6: 擴充 (未來)
- [ ] 加入更多 SAF API 端點
- [ ] Redis 快取機制
- [ ] CI/CD 設定
- [ ] SSL/HTTPS 支援

---

## 9. 依賴套件

### 9.1 `requirements.txt` (生產環境)

```
# Web Framework
fastapi>=0.104.0
uvicorn[standard]>=0.24.0

# HTTP Client
httpx>=0.25.0

# Data Validation
pydantic>=2.5.0
pydantic-settings>=2.1.0

# Environment
python-dotenv>=1.0.0
python-multipart>=0.0.6
```

### 9.2 `requirements-dev.txt` (開發/測試環境)

```
# 包含生產環境依賴
-r requirements.txt

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0
httpx>=0.25.0               # 用於 TestClient

# Code Quality
black>=23.0.0
isort>=5.12.0
flake8>=6.1.0
mypy>=1.7.0

# Development
ipython>=8.0.0
```

---

## 10. 測試規劃 (pytest)

### 10.1 pytest 設定 (`pyproject.toml`)

```toml
[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
    "-ra",
]
markers = [
    "unit: Unit tests (no external dependencies)",
    "integration: Integration tests (may need services)",
    "slow: Slow tests",
]
filterwarnings = [
    "ignore::DeprecationWarning",
]

[tool.coverage.run]
source = ["app"]
branch = true
omit = [
    "*/tests/*",
    "*/__init__.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
show_missing = true
```

### 10.2 共用 Fixtures (`tests/conftest.py`)

```python
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.config import Settings, get_settings


# ========== Settings Fixtures ==========

@pytest.fixture
def test_settings() -> Settings:
    """測試用設定"""
    return Settings(
        saf_base_url="https://saf.test.com",
        saf_login_port=8000,
        saf_api_port=3004,
        saf_username="test_user",
        saf_password="test_password",
        debug=True,
    )


@pytest.fixture
def override_settings(test_settings):
    """覆蓋應用程式設定"""
    app.dependency_overrides[get_settings] = lambda: test_settings
    yield test_settings
    app.dependency_overrides.clear()


# ========== Client Fixtures ==========

@pytest.fixture
def client(override_settings) -> TestClient:
    """同步測試客戶端"""
    return TestClient(app)


@pytest.fixture
async def async_client(override_settings) -> AsyncClient:
    """非同步測試客戶端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# ========== Mock Fixtures ==========

@pytest.fixture
def mock_saf_login_response():
    """模擬 SAF 登入回應"""
    return {
        "id": 150,
        "name": "test_user",
        "mail": "test_user@test.com"
    }


@pytest.fixture
def mock_saf_projects_response():
    """模擬 SAF 專案列表回應"""
    return {
        "page": 1,
        "size": 50,
        "total": 2,
        "data": [
            {
                "key": "project-1",
                "projectUid": "uid-1",
                "projectName": "Test Project 1",
                "customer": "Customer A",
                "controller": "SM2508",
            },
            {
                "key": "project-2",
                "projectUid": "uid-2",
                "projectName": "Test Project 2",
                "customer": "Customer B",
                "controller": "SM2269XT",
            }
        ]
    }


@pytest.fixture
def mock_httpx_client():
    """模擬 httpx AsyncClient"""
    with patch("httpx.AsyncClient") as mock:
        mock_instance = AsyncMock()
        mock.return_value.__aenter__.return_value = mock_instance
        yield mock_instance
```

### 10.3 測試範例

#### 單元測試: `tests/unit/test_config.py`

```python
import pytest
from app.config import Settings


class TestSettings:
    """測試設定模組"""
    
    def test_default_values(self):
        """測試預設值"""
        settings = Settings()
        assert settings.saf_base_url == "https://saf.siliconmotion.com.tw"
        assert settings.saf_login_port == 8000
        assert settings.api_port == 8080
    
    def test_saf_login_url_property(self):
        """測試登入 URL 計算屬性"""
        settings = Settings(
            saf_base_url="https://test.com",
            saf_login_port=9000
        )
        assert settings.saf_login_url == "https://test.com:9000/api/login"
    
    def test_has_credentials_true(self):
        """測試有認證資訊"""
        settings = Settings(
            saf_username="user",
            saf_password="pass"
        )
        assert settings.has_credentials is True
    
    def test_has_credentials_false(self):
        """測試無認證資訊"""
        settings = Settings()
        assert settings.has_credentials is False
```

#### 單元測試: `tests/unit/test_saf_client.py`

```python
import pytest
from unittest.mock import AsyncMock, patch
from app.services.saf_client import SAFClient


class TestSAFClient:
    """測試 SAF Client"""
    
    @pytest.mark.asyncio
    async def test_login_success(self, mock_httpx_client, mock_saf_login_response):
        """測試登入成功"""
        mock_httpx_client.post.return_value = AsyncMock(
            status_code=200,
            json=lambda: mock_saf_login_response
        )
        
        client = SAFClient()
        result = await client.login("user", "pass")
        
        assert result["id"] == 150
        assert result["name"] == "test_user"
    
    @pytest.mark.asyncio
    async def test_login_failure(self, mock_httpx_client):
        """測試登入失敗"""
        mock_httpx_client.post.return_value = AsyncMock(
            status_code=401,
            json=lambda: {"error": "Unauthorized"}
        )
        
        client = SAFClient()
        with pytest.raises(Exception):
            await client.login("wrong", "wrong")
```

#### 整合測試: `tests/integration/test_auth_api.py`

```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock


class TestAuthAPI:
    """測試認證 API"""
    
    def test_health_check(self, client: TestClient):
        """測試健康檢查端點"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    @patch("app.services.saf_client.SAFClient.login")
    def test_login_success(self, mock_login, client: TestClient, mock_saf_login_response):
        """測試登入 API 成功"""
        mock_login.return_value = mock_saf_login_response
        
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "test", "password": "test"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == 150
    
    def test_login_missing_credentials(self, client: TestClient):
        """測試缺少認證資訊"""
        response = client.post(
            "/api/v1/auth/login",
            json={}
        )
        
        assert response.status_code == 422  # Validation Error
```

#### 整合測試: `tests/integration/test_projects_api.py`

```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


class TestProjectsAPI:
    """測試專案 API"""
    
    @patch("app.services.saf_client.SAFClient.get_all_projects")
    def test_get_projects_success(self, mock_get_projects, client: TestClient, mock_saf_projects_response):
        """測試取得專案列表成功"""
        mock_get_projects.return_value = mock_saf_projects_response
        
        response = client.get(
            "/api/v1/projects",
            headers={
                "Authorization": "150",
                "Authorization-Name": "test_user"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total"] == 2
    
    def test_get_projects_unauthorized(self, client: TestClient):
        """測試未授權存取"""
        response = client.get("/api/v1/projects")
        
        assert response.status_code == 401
```

### 10.4 測試資料 (`tests/fixtures/sample_data.json`)

```json
{
  "login_response": {
    "id": 150,
    "name": "Chunwei.Huang",
    "mail": "Chunwei.Huang@siliconmotion.com"
  },
  "project_sample": {
    "key": "abc123",
    "projectUid": "abc123",
    "projectId": "proj-001",
    "projectName": "Channel",
    "productCategory": "Client_PCIe",
    "customer": "ADATA",
    "controller": "SM2508",
    "subVersion": "AC",
    "nand": "Micron B58R TLC",
    "fw": "FWY1027A_PKGY1027V1",
    "pl": "test.user",
    "status": 0,
    "visible": true,
    "taskId": "SVDFWV-12345"
  }
}
```

### 10.5 執行測試指令

```bash
# 執行所有測試
pytest

# 執行並顯示覆蓋率
pytest --cov=app --cov-report=html

# 只執行單元測試
pytest tests/unit/ -v

# 只執行整合測試
pytest tests/integration/ -v

# 執行特定標記的測試
pytest -m unit
pytest -m integration

# 執行單一測試檔案
pytest tests/unit/test_config.py -v

# 執行單一測試函數
pytest tests/unit/test_config.py::TestSettings::test_default_values -v

# 顯示 print 輸出
pytest -s

# 失敗時進入偵錯模式
pytest --pdb
```

### 10.6 測試腳本 (`scripts/run_tests.sh`)

```bash
#!/bin/bash
set -e

echo "🧪 Running tests..."

# 確保在專案根目錄
cd "$(dirname "$0")/.."

# 啟動虛擬環境 (如果存在)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 執行測試
case "${1:-all}" in
    unit)
        echo "Running unit tests..."
        pytest tests/unit/ -v
        ;;
    integration)
        echo "Running integration tests..."
        pytest tests/integration/ -v
        ;;
    coverage)
        echo "Running tests with coverage..."
        pytest --cov=app --cov-report=html --cov-report=term-missing
        echo "📊 Coverage report: htmlcov/index.html"
        ;;
    *)
        echo "Running all tests..."
        pytest -v
        ;;
esac

echo "✅ Tests completed!"
```

---

## 10. 執行方式

### 開發環境

```bash
# 建立虛擬環境
python -m venv venv
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 啟動開發伺服器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### API 文件
啟動後可存取:
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

---

## 11. 注意事項

1. **Proxy 問題**: SAF 網站需繞過公司 Proxy，使用 `trust_env=False`
2. **敏感資訊**: 帳號密碼請使用環境變數，不要 commit 到版控
3. **Port 區分**: 登入用 8000、API 用 3004

---

## 12. Docker 部署

### 12.1 Dockerfile

```dockerfile
# 使用 Python 3.11 slim 映像檔
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 設定環境變數
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴檔案
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY app/ ./app/

# 暴露端口
EXPOSE 8080

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 啟動指令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 12.2 docker-compose.yml

```yaml
version: '3.8'

services:
  internal-api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: internal-api-server
    restart: unless-stopped
    ports:
      - "8080:8080"           # 對外開放端口
    environment:
      - SAF_BASE_URL=${SAF_BASE_URL:-https://saf.siliconmotion.com.tw}
      - SAF_LOGIN_PORT=${SAF_LOGIN_PORT:-8000}
      - SAF_API_PORT=${SAF_API_PORT:-3004}
      - SAF_USERNAME=${SAF_USERNAME}
      - SAF_PASSWORD=${SAF_PASSWORD}
      - API_HOST=0.0.0.0
      - API_PORT=8080
      - DEBUG=${DEBUG:-false}
    env_file:
      - .env                  # 從 .env 檔案讀取環境變數
    networks:
      - internal-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

networks:
  internal-network:
    driver: bridge
```

### 12.3 .dockerignore

```
# Git
.git
.gitignore

# Python
__pycache__
*.py[cod]
*$py.class
*.so
.Python
venv/
.venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# 文件
docs/
*.md
!README.md

# 測試
tests/
.pytest_cache/
.coverage

# 環境變數 (敏感資訊)
.env
.env.local

# Docker
Dockerfile
docker-compose*.yml
```

### 12.4 Docker 操作指令

#### 建置與啟動

```bash
# 建置映像檔
docker-compose build

# 啟動容器 (背景執行)
docker-compose up -d

# 查看日誌
docker-compose logs -f

# 停止容器
docker-compose down
```

#### 單獨使用 Docker

```bash
# 建置映像檔
docker build -t internal-api:latest .

# 執行容器
docker run -d \
  --name internal-api-server \
  -p 8080:8080 \
  --env-file .env \
  internal-api:latest

# 查看日誌
docker logs -f internal-api-server

# 停止並移除
docker stop internal-api-server
docker rm internal-api-server
```

### 12.5 網路架構

```
┌─────────────────────────────────────────────────────────────────┐
│                        公司內部網路                               │
│                                                                 │
│  ┌──────────────┐         ┌──────────────┐                     │
│  │   Client A   │────────▶│              │                     │
│  │  (其他電腦)   │         │   Docker     │      ┌────────────┐ │
│  └──────────────┘         │   Container  │      │            │ │
│                           │              │─────▶│  SAF 網站   │ │
│  ┌──────────────┐         │  internal-   │      │  :8000     │ │
│  │   Client B   │────────▶│  api-server  │      │  :3004     │ │
│  │  (其他電腦)   │         │              │      │            │ │
│  └──────────────┘         │   :8080      │      └────────────┘ │
│                           └──────────────┘                     │
│                                                                 │
│  Client 存取: http://<host-ip>:8080/api/v1/projects            │
└─────────────────────────────────────────────────────────────────┘
```

### 12.6 其他電腦連線方式

假設運行 Docker 的主機 IP 為 `192.168.1.100`：

```bash
# 健康檢查
curl http://192.168.1.100:8080/health

# 登入
curl -X POST http://192.168.1.100:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# 取得專案列表 (帶認證)
curl http://192.168.1.100:8080/api/v1/projects \
  -H "Authorization: 150" \
  -H "Authorization-Name: Chunwei.Huang"
```

### 12.7 防火牆設定

如果其他電腦無法連線，請確認：

```bash
# 開放 8080 port (Ubuntu/Debian)
sudo ufw allow 8080/tcp

# 開放 8080 port (CentOS/RHEL)
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload

# 檢查 Docker 是否正常監聽
sudo netstat -tlnp | grep 8080
```

---

## 13. 參考資料

- [FastAPI 官方文件](https://fastapi.tiangolo.com/)
- [httpx 官方文件](https://www.python-httpx.org/)
- [Pydantic 官方文件](https://docs.pydantic.dev/)
