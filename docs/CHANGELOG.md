# Changelog

本專案的所有重要變更都會記錄在此文件中。

格式基於 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)，
版本號遵循 [語意化版本](https://semver.org/lang/zh-TW/)。

## [Unreleased]

### 計畫中
- 加入更多 SAF API 端點
- Redis 快取機制
- CI/CD 設定

---

## [0.1.0] - 2025-12-02

### 新增
- 🎉 專案初始化
- 🔐 SAF 登入認證 API (`/api/v1/auth/login`)
- 🔐 使用設定檔登入 API (`/api/v1/auth/login-with-config`)
- 📊 取得專案列表 API (`/api/v1/projects`)
- 📈 專案統計摘要 API (`/api/v1/projects/summary`)
- ❤️ 健康檢查端點 (`/health`)
- ⚙️ 設定資訊端點 (`/config`)
- 🐳 Docker 支援 (Dockerfile, docker-compose.yml)
- 🧪 pytest 測試框架
- 📚 自動 API 文件 (Swagger UI, ReDoc)

### 技術細節
- 使用 FastAPI 框架
- 使用 httpx 作為 HTTP Client (繞過 Proxy)
- 使用 Pydantic v2 進行資料驗證
- 使用 Pydantic Settings 管理環境變數
