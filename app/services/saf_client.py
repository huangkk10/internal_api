"""
SAF API Client

封裝對 SAF 網站的所有 API 呼叫
"""

from typing import Any, Dict, List, Optional

import httpx

from app.config import Settings, get_settings
from lib.decorators import log_execution, retry
from lib.exceptions import SAFAPIError, SAFAuthenticationError, SAFConnectionError
from lib.logger import LoggerMixin


class SAFClient(LoggerMixin):
    """
    SAF API 客戶端
    
    封裝對 SAF 網站的所有 API 呼叫，處理認證和錯誤
    
    Example:
        >>> client = SAFClient()
        >>> auth = await client.login("username", "password")
        >>> projects = await client.get_all_projects(auth["id"], auth["name"])
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        初始化 SAF Client
        
        Args:
            settings: 設定物件，如果不提供則使用預設設定
        """
        self.settings = settings or get_settings()
        
        # httpx 客戶端設定 - 繞過 proxy
        self._client_kwargs = {
            "trust_env": False,  # 不使用系統 proxy
            "timeout": 30.0,
            "verify": True,  # SSL 驗證
        }
    
    def _get_client(self) -> httpx.AsyncClient:
        """取得 httpx 非同步客戶端"""
        return httpx.AsyncClient(**self._client_kwargs)
    
    @retry(max_attempts=3, delay=1.0, exceptions=(httpx.ConnectError, httpx.TimeoutException))
    @log_execution
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        登入 SAF 系統
        
        Args:
            username: SAF 帳號
            password: SAF 密碼
            
        Returns:
            包含 id, name, mail 的字典
            
        Raises:
            SAFAuthenticationError: 認證失敗
            SAFConnectionError: 連線失敗
        """
        url = self.settings.saf_login_url
        self.logger.debug(f"Logging in to SAF: {url}")
        
        try:
            async with self._get_client() as client:
                response = await client.post(
                    url,
                    data={
                        "username": username,
                        "password": password,
                    },
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.logger.info(f"Login successful for user: {data.get('name')}")
                    return data
                elif response.status_code == 401:
                    raise SAFAuthenticationError("Invalid username or password")
                else:
                    raise SAFAPIError(
                        f"Login failed with status code: {response.status_code}",
                        status_code=response.status_code
                    )
                    
        except httpx.ConnectError as e:
            self.logger.error(f"Connection error: {e}")
            raise SAFConnectionError(f"Failed to connect to SAF: {e}")
        except httpx.TimeoutException as e:
            self.logger.error(f"Timeout error: {e}")
            raise SAFConnectionError(f"Connection timeout: {e}")
    
    @retry(max_attempts=3, delay=1.0, exceptions=(httpx.ConnectError, httpx.TimeoutException))
    @log_execution
    async def get_all_projects(
        self,
        user_id: int,
        username: str,
        page: int = 1,
        size: int = 50
    ) -> Dict[str, Any]:
        """
        取得所有專案列表
        
        Args:
            user_id: 使用者 ID (從登入取得)
            username: 使用者名稱 (從登入取得)
            page: 頁碼
            size: 每頁筆數
            
        Returns:
            包含專案列表的字典
            
        Raises:
            SAFAPIError: API 呼叫失敗
            SAFConnectionError: 連線失敗
        """
        url = f"{self.settings.saf_api_base_url}/project/listAllProjectsDetails"
        self.logger.debug(f"Getting projects from: {url}")
        
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
                        "page": page,
                        "size": size,
                    },
                )
                
                if response.status_code == 200:
                    data = response.json()
                    total = data.get("total", 0)
                    self.logger.info(f"Retrieved {total} projects")
                    return data
                else:
                    raise SAFAPIError(
                        f"Failed to get projects: {response.status_code}",
                        status_code=response.status_code
                    )
                    
        except httpx.ConnectError as e:
            self.logger.error(f"Connection error: {e}")
            raise SAFConnectionError(f"Failed to connect to SAF: {e}")
        except httpx.TimeoutException as e:
            self.logger.error(f"Timeout error: {e}")
            raise SAFConnectionError(f"Connection timeout: {e}")
    
    async def login_with_config(self) -> Dict[str, Any]:
        """
        使用設定檔中的帳密登入
        
        Returns:
            包含 id, name, mail 的字典
            
        Raises:
            SAFAuthenticationError: 未設定帳密或認證失敗
        """
        if not self.settings.has_credentials:
            raise SAFAuthenticationError(
                "SAF credentials not configured. "
                "Please set SAF_USERNAME and SAF_PASSWORD in .env file."
            )
        
        return await self.login(
            self.settings.saf_username,
            self.settings.saf_password
        )

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
            user_id: 使用者 ID (從登入取得)
            username: 使用者名稱 (從登入取得)
            query: 查詢條件，格式: 欄位名 = "值"
            page: 頁碼
            size: 每頁筆數
            sort: 排序條件
            
        Returns:
            包含測試狀態列表的字典，格式如:
            {
                "items": [...],
                "total": 100,
                "page": 1,
                "size": 50
            }
            
        Raises:
            SAFAPIError: API 呼叫失敗
            SAFConnectionError: 連線失敗
        """
        url = f"{self.settings.saf_api_base_url}/status"
        self.logger.debug(f"Searching test status from: {url}")
        
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
                    total = data.get("total", 0)
                    self.logger.info(f"Retrieved {items_count} test status items (total: {total})")
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
        
        Args:
            user_id: 使用者 ID (從登入取得)
            username: 使用者名稱 (從登入取得)
            project_id: 專案 ID
            
        Returns:
            包含 firmware 列表的字典，格式如:
            {
                "fws": [
                    {"fw": "MASTX9KA", "subVersion": "AA", "projectUid": "..."},
                    ...
                ]
            }
            
        Raises:
            SAFAPIError: API 呼叫失敗
            SAFConnectionError: 連線失敗
        """
        url = f"{self.settings.saf_api_base_url}/project/ListFWsByProjectId"
        self.logger.debug(f"Getting FWs by project ID from: {url}")
        
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
                        "projectId": project_id,
                    },
                )
                
                if response.status_code == 200:
                    data = response.json()
                    fws_count = len(data.get("fws", []))
                    self.logger.info(f"Retrieved {fws_count} firmwares for project: {project_id}")
                    return data
                elif response.status_code == 404:
                    raise SAFAPIError(
                        f"Project not found: {project_id}",
                        status_code=404,
                        error_code="PROJECT_NOT_FOUND"
                    )
                else:
                    raise SAFAPIError(
                        f"Failed to get FWs by project ID: {response.status_code}",
                        status_code=response.status_code
                    )
                    
        except httpx.ConnectError as e:
            self.logger.error(f"Connection error: {e}")
            raise SAFConnectionError(f"Failed to connect to SAF: {e}")
        except httpx.TimeoutException as e:
            self.logger.error(f"Timeout error: {e}")
            raise SAFConnectionError(f"Connection timeout: {e}")

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
            user_id: 使用者 ID (從登入取得)
            username: 使用者名稱 (從登入取得)
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

    @retry(max_attempts=3, delay=1.0, exceptions=(httpx.ConnectError, httpx.TimeoutException))
    @log_execution
    async def list_known_issues(
        self,
        user_id: int,
        username: str,
        project_id: Optional[List[str]] = None,
        root_id: Optional[List[str]] = None,
        show_disable: bool = True
    ) -> Dict[str, Any]:
        """
        取得所有 Known Issues 列表
        
        Args:
            user_id: 使用者 ID (從登入取得)
            username: 使用者名稱 (從登入取得)
            project_id: 專案 ID 列表 (可選，空列表表示全部)
            root_id: Root ID 列表 (可選，空列表表示全部)
            show_disable: 是否顯示停用的 issues (預設 True)
            
        Returns:
            包含 known issues 列表的字典
            
        Raises:
            SAFAPIError: API 呼叫失敗
            SAFConnectionError: 連線失敗
        """
        url = f"{self.settings.saf_api_base_url}/knownIssue/ListAllKnownIssue"
        self.logger.debug(f"Getting known issues from: {url}")
        
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
                        "projectId": project_id or [],
                        "rootId": root_id or [],
                        "showDisable": show_disable,
                    },
                )
                
                if response.status_code == 200:
                    data = response.json()
                    items_count = len(data.get("items", []))
                    self.logger.info(f"Retrieved {items_count} known issues")
                    return data
                else:
                    raise SAFAPIError(
                        f"Failed to get known issues: {response.status_code}",
                        status_code=response.status_code
                    )
                    
        except httpx.ConnectError as e:
            self.logger.error(f"Connection error: {e}")
            raise SAFConnectionError(f"Failed to connect to SAF: {e}")
        except httpx.TimeoutException as e:
            self.logger.error(f"Timeout error: {e}")
            raise SAFConnectionError(f"Connection timeout: {e}")

    @retry(max_attempts=3, delay=1.0, exceptions=(httpx.ConnectError, httpx.TimeoutException))
    @log_execution
    async def get_project_dashboard(
        self,
        user_id: int,
        username: str,
        project_id: str
    ) -> Dict[str, Any]:
        """
        取得專案儀表板資料
        
        Args:
            user_id: 使用者 ID (從登入取得)
            username: 使用者名稱 (從登入取得)
            project_id: 專案 ID
            
        Returns:
            包含專案儀表板資料的字典
            
        Raises:
            SAFAPIError: API 呼叫失敗
            SAFConnectionError: 連線失敗
        """
        url = f"{self.settings.saf_api_base_url}/project/GetProjectDashBoard"
        self.logger.debug(f"Getting project dashboard from: {url}")
        
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
                        "projectId": project_id,
                    },
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.logger.info(f"Retrieved dashboard for project: {project_id}")
                    return data
                elif response.status_code == 404:
                    raise SAFAPIError(
                        f"Project not found: {project_id}",
                        status_code=404,
                        error_code="PROJECT_NOT_FOUND"
                    )
                else:
                    raise SAFAPIError(
                        f"Failed to get project dashboard: {response.status_code}",
                        status_code=response.status_code
                    )
                    
        except httpx.ConnectError as e:
            self.logger.error(f"Connection error: {e}")
            raise SAFConnectionError(f"Failed to connect to SAF: {e}")
        except httpx.TimeoutException as e:
            self.logger.error(f"Timeout error: {e}")
            raise SAFConnectionError(f"Connection timeout: {e}")


# 建立預設客戶端實例
saf_client = SAFClient()
