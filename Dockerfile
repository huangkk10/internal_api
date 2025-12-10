# 使用 Python 3.11 slim 映像檔
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 設定環境變數
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# 設定 Proxy（用於 pip 安裝）
ARG HTTP_PROXY=http://10.10.10.190:3128
ARG HTTPS_PROXY=http://10.10.10.190:3128
ENV http_proxy=$HTTP_PROXY
ENV https_proxy=$HTTPS_PROXY

# 複製依賴檔案
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# 清除 Proxy 環境變數（運行時不需要）
ENV http_proxy=
ENV https_proxy=

# 複製應用程式碼
COPY app/ ./app/
COPY lib/ ./lib/
COPY tests/ ./tests/

# 暴露端口
EXPOSE 8080

# 健康檢查（使用 Python 代替 curl）
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# 啟動指令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
