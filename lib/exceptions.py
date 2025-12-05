"""
自定義例外類別

定義專案中使用的所有自定義例外
"""


class InternalAPIException(Exception):
    """基礎例外類別"""

    def __init__(self, message: str = "Internal API Error", code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class SAFConnectionError(InternalAPIException):
    """SAF 連線錯誤"""

    def __init__(self, message: str = "Failed to connect to SAF server"):
        super().__init__(message=message, code="SAF_CONNECTION_ERROR")


class SAFAuthenticationError(InternalAPIException):
    """SAF 認證錯誤"""

    def __init__(self, message: str = "SAF authentication failed"):
        super().__init__(message=message, code="SAF_AUTH_ERROR")


class SAFAPIError(InternalAPIException):
    """SAF API 呼叫錯誤"""

    def __init__(
        self, 
        message: str = "SAF API call failed", 
        status_code: int = None,
        error_code: str = "SAF_API_ERROR"
    ):
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message=message, code=error_code)


class ConfigurationError(InternalAPIException):
    """設定錯誤"""

    def __init__(self, message: str = "Configuration error"):
        super().__init__(message=message, code="CONFIG_ERROR")


class ValidationError(InternalAPIException):
    """驗證錯誤"""

    def __init__(self, message: str = "Validation error", field: str = None):
        self.field = field
        super().__init__(message=message, code="VALIDATION_ERROR")
