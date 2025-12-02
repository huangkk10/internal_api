"""
專案相關路由
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.config import Settings, get_settings
from app.models.schemas import APIResponse, AuthInfo, ProjectListResponse
from app.routers.auth import get_auth_info
from app.services.saf_client import SAFClient
from lib.exceptions import SAFAPIError, SAFConnectionError
from lib.logger import get_logger
from lib.utils import format_response

router = APIRouter(prefix="/projects", tags=["Projects"])
logger = get_logger(__name__)


def get_saf_client(settings: Settings = Depends(get_settings)) -> SAFClient:
    """取得 SAF Client 依賴"""
    return SAFClient(settings)


@router.get("", response_model=APIResponse, summary="取得所有專案列表")
async def get_all_projects(
    page: int = Query(1, ge=1, description="頁碼"),
    size: int = Query(50, ge=1, le=100, description="每頁筆數"),
    auth: AuthInfo = Depends(get_auth_info),
    client: SAFClient = Depends(get_saf_client)
):
    """
    取得所有專案的詳細資訊列表
    
    需要在 Header 中提供認證資訊：
    - **Authorization**: 使用者 ID (從登入 API 取得)
    - **Authorization-Name**: 使用者名稱 (從登入 API 取得)
    
    支援分頁：
    - **page**: 頁碼 (預設 1)
    - **size**: 每頁筆數 (預設 50，最大 100)
    """
    try:
        result = await client.get_all_projects(
            user_id=auth.user_id,
            username=auth.username,
            page=page,
            size=size
        )
        
        return format_response(
            success=True,
            data=result
        )
        
    except SAFAPIError as e:
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


@router.get("/summary", response_model=APIResponse, summary="取得專案摘要統計")
async def get_projects_summary(
    auth: AuthInfo = Depends(get_auth_info),
    client: SAFClient = Depends(get_saf_client)
):
    """
    取得專案的摘要統計資訊
    
    包含：
    - 總專案數
    - 各客戶的專案數量
    - 各控制器的專案數量
    """
    try:
        result = await client.get_all_projects(
            user_id=auth.user_id,
            username=auth.username,
            page=1,
            size=1000  # 取得所有專案以計算統計
        )
        
        projects = result.get("data", [])
        
        # 計算統計
        customers = {}
        controllers = {}
        
        def count_projects(project_list):
            for project in project_list:
                customer = project.get("customer", "Unknown")
                controller = project.get("controller", "Unknown")
                
                customers[customer] = customers.get(customer, 0) + 1
                controllers[controller] = controllers.get(controller, 0) + 1
                
                # 遞迴處理 children
                children = project.get("children", [])
                if children:
                    count_projects(children)
        
        count_projects(projects)
        
        summary = {
            "total": result.get("total", 0),
            "by_customer": dict(sorted(customers.items(), key=lambda x: x[1], reverse=True)),
            "by_controller": dict(sorted(controllers.items(), key=lambda x: x[1], reverse=True)),
        }
        
        return format_response(
            success=True,
            data=summary
        )
        
    except SAFAPIError as e:
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
