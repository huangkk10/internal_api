"""
通用工具函數

提供專案中常用的工具函數
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union


def format_response(
    success: bool,
    data: Any = None,
    message: Optional[str] = None,
    error_code: Optional[str] = None
) -> Dict[str, Any]:
    """
    統一 API 回應格式
    
    Args:
        success: 請求是否成功
        data: 回應資料
        message: 訊息 (通常用於錯誤訊息)
        error_code: 錯誤代碼
        
    Returns:
        格式化的回應字典
        
    Example:
        >>> format_response(True, {"id": 1})
        {'success': True, 'data': {'id': 1}, 'message': None, 'timestamp': '...'}
    """
    response = {
        "success": success,
        "data": data,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if error_code:
        response["error_code"] = error_code
    
    return response


def timestamp_to_datetime(ts: Dict[str, Any]) -> Optional[datetime]:
    """
    將 SAF 的 timestamp 格式轉換為 datetime
    
    SAF 回傳的 timestamp 格式:
    {
        "seconds": {
            "low": 1763563286,
            "high": 0,
            "unsigned": false
        }
    }
    
    Args:
        ts: SAF timestamp 字典
        
    Returns:
        datetime 物件，如果轉換失敗則返回 None
    """
    if not ts:
        return None
    
    try:
        seconds = ts.get("seconds", {})
        if isinstance(seconds, dict):
            timestamp = seconds.get("low", 0)
        else:
            timestamp = seconds
        
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)
    except (TypeError, ValueError, OSError):
        return None


def flatten_projects(projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    將巢狀的專案結構展平
    
    SAF 回傳的專案資料可能包含 children，此函數將所有專案展平為單一列表
    
    Args:
        projects: 專案列表 (可能包含巢狀 children)
        
    Returns:
        展平後的專案列表
    """
    result = []
    
    for project in projects:
        # 複製專案資料 (排除 children)
        flat_project = {k: v for k, v in project.items() if k != "children"}
        result.append(flat_project)
        
        # 遞迴處理 children
        children = project.get("children", [])
        if children:
            result.extend(flatten_projects(children))
    
    return result


def safe_get(data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """
    安全地從巢狀字典中取得值
    
    Args:
        data: 資料字典
        keys: 鍵值路徑
        default: 預設值
        
    Returns:
        找到的值或預設值
        
    Example:
        >>> data = {"a": {"b": {"c": 1}}}
        >>> safe_get(data, "a", "b", "c")
        1
        >>> safe_get(data, "a", "x", "y", default="not found")
        'not found'
    """
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
        else:
            return default
        if result is None:
            return default
    return result


def truncate_string(s: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截斷字串
    
    Args:
        s: 原始字串
        max_length: 最大長度
        suffix: 截斷後綴
        
    Returns:
        截斷後的字串
    """
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix
