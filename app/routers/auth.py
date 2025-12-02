"""
認證相關路由
"""

from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.config import Settings, get_settings
from app.models.schemas import APIResponse, AuthInfo, LoginRequest, LoginResponse
from app.services.saf_client import SAFClient
from lib.exceptions import SAFAuthenticationError, SAFConnectionError
from lib.logger import get_logger
from lib.utils import format_response

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = get_logger(__name__)


def get_saf_client(settings: Settings = Depends(get_settings)) -> SAFClient:
    """取得 SAF Client 依賴"""
    return SAFClient(settings)


@router.post("/login", response_model=APIResponse, summary="登入 SAF 系統")
async def login(
    request: LoginRequest,
    client: SAFClient = Depends(get_saf_client)
):
    """
    登入 SAF 系統並取得認證資訊
    
    - **username**: SAF 帳號
    - **password**: SAF 密碼
    
    返回使用者 ID、名稱和信箱，後續 API 呼叫需要使用這些資訊
    """
    try:
        result = await client.login(request.username, request.password)
        return format_response(
            success=True,
            data=LoginResponse(**result).model_dump()
        )
    except SAFAuthenticationError as e:
        logger.warning(f"Authentication failed for user: {request.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=format_response(
                success=False,
                message=str(e),
                error_code="AUTH_FAILED"
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


@router.post("/login-with-config", response_model=APIResponse, summary="使用設定檔登入")
async def login_with_config(
    client: SAFClient = Depends(get_saf_client)
):
    """
    使用 .env 設定檔中的帳密登入 SAF 系統
    
    需要在 .env 檔案中設定 SAF_USERNAME 和 SAF_PASSWORD
    """
    try:
        result = await client.login_with_config()
        return format_response(
            success=True,
            data=LoginResponse(**result).model_dump()
        )
    except SAFAuthenticationError as e:
        logger.warning(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=format_response(
                success=False,
                message=str(e),
                error_code="AUTH_FAILED"
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


def get_auth_info(
    authorization: Optional[str] = Header(None, description="使用者 ID"),
    authorization_name: Optional[str] = Header(None, alias="Authorization-Name", description="使用者名稱")
) -> AuthInfo:
    """
    從 Header 取得認證資訊
    
    用於需要認證的 API 端點
    """
    if not authorization or not authorization_name:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=format_response(
                success=False,
                message="Missing authorization headers. "
                        "Please provide 'Authorization' (user ID) and 'Authorization-Name' (username).",
                error_code="MISSING_AUTH"
            )
        )
    
    try:
        user_id = int(authorization)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=format_response(
                success=False,
                message="Invalid Authorization header. User ID must be an integer.",
                error_code="INVALID_AUTH"
            )
        )
    
    return AuthInfo(user_id=user_id, username=authorization_name)
