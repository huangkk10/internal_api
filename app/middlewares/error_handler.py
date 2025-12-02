"""
全域錯誤處理中介軟體
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from lib.exceptions import InternalAPIException
from lib.logger import get_logger
from lib.utils import format_response

logger = get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    全域錯誤處理中介軟體
    
    捕捉所有未處理的例外，返回統一的錯誤格式
    """
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
            
        except InternalAPIException as e:
            logger.error(f"Internal API Exception: {e.code} - {e.message}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=format_response(
                    success=False,
                    message=e.message,
                    error_code=e.code
                )
            )
            
        except Exception as e:
            logger.exception(f"Unhandled exception: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=format_response(
                    success=False,
                    message="An unexpected error occurred",
                    error_code="INTERNAL_ERROR"
                )
            )
