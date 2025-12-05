"""
專案相關路由
"""

from typing import Any, Dict, List, Optional

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


def _parse_result_string(result_str: str) -> Dict[str, int]:
    """
    解析結果字串
    
    Args:
        result_str: 如 "8/0/0/0/0" (PASS/FAIL/ONGOING/CANCEL/CHECK)
        
    Returns:
        {'pass': 8, 'fail': 0, 'ongoing': 0, 'cancel': 0, 'check': 0}
    """
    parts = result_str.split("/")
    if len(parts) != 5:
        return {"pass": 0, "fail": 0, "ongoing": 0, "cancel": 0, "check": 0}
    
    try:
        return {
            "pass": int(parts[0]),
            "fail": int(parts[1]),
            "ongoing": int(parts[2]),
            "cancel": int(parts[3]),
            "check": int(parts[4]),
        }
    except ValueError:
        return {"pass": 0, "fail": 0, "ongoing": 0, "cancel": 0, "check": 0}


def _transform_test_summary(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    將 SAF 原始資料轉換為友善格式
    
    SAF API 回傳結構：
    {
        "projectId": "...",
        "projectName": "...",
        "fws": [{
            "projectUid": "...",
            "fwName": "...",
            "plans": [{
                "testPlanName": "...",
                "categoryItems": [{
                    "categoryName": "...",
                    "totalTestItems": 5,
                    "sizeResult": [{"size": "256GB", "result": "0/1/0/0/0"}, ...],
                    "total": "0/1/0/0/0"
                }, ...]
            }]
        }]
    }
    """
    project_name = raw_data.get("projectName", "")
    
    # 取得第一個 firmware 的資料
    fws = raw_data.get("fws", [])
    if not fws:
        return {
            "project_uid": "",
            "project_name": project_name,
            "capacities": [],
            "categories": [],
            "summary": {
                "total_pass": 0,
                "total_fail": 0,
                "total_ongoing": 0,
                "total_cancel": 0,
                "total_check": 0,
                "overall_total": 0,
                "overall_pass_rate": 0.0
            }
        }
    
    fw = fws[0]
    project_uid = fw.get("projectUid", "")
    
    # 取得測試項目
    plans = fw.get("plans", [])
    if not plans:
        return {
            "project_uid": project_uid,
            "project_name": project_name,
            "capacities": [],
            "categories": [],
            "summary": {
                "total_pass": 0,
                "total_fail": 0,
                "total_ongoing": 0,
                "total_cancel": 0,
                "total_check": 0,
                "overall_total": 0,
                "overall_pass_rate": 0.0
            }
        }
    
    # 收集所有容量
    all_capacities = set()
    
    # 依 categoryName 分組測試項目
    categories_map: Dict[str, Dict[str, Any]] = {}
    
    # 處理所有 plans
    for plan in plans:
        # SAF API 回傳 categoryItems (依類別彙整的摘要)
        category_items = plan.get("categoryItems", [])
        
        for item in category_items:
            cat_name = item.get("categoryName", "Unknown")
            
            if cat_name not in categories_map:
                categories_map[cat_name] = {
                    "name": cat_name,
                    "results_by_capacity": {},
                    "total": {
                        "pass": 0,
                        "fail": 0,
                        "ongoing": 0,
                        "cancel": 0,
                        "check": 0,
                    }
                }
            
            # 累加各容量的結果
            for size_data in item.get("sizeResult", []):
                capacity = size_data.get("size", "Unknown")
                result_str = size_data.get("result", "0/0/0/0/0")
                
                all_capacities.add(capacity)
                
                result = _parse_result_string(result_str)
                
                # 初始化容量結果
                if capacity not in categories_map[cat_name]["results_by_capacity"]:
                    categories_map[cat_name]["results_by_capacity"][capacity] = {
                        "pass": 0, "fail": 0, "ongoing": 0, "cancel": 0, "check": 0
                    }
                
                # 累加
                for key in ["pass", "fail", "ongoing", "cancel", "check"]:
                    categories_map[cat_name]["results_by_capacity"][capacity][key] += result[key]
                    categories_map[cat_name]["total"][key] += result[key]
    
    # 計算總計和 pass rate
    total_pass = 0
    total_fail = 0
    total_ongoing = 0
    total_cancel = 0
    total_check = 0
    
    categories = []
    for cat_name, cat_data in categories_map.items():
        # 計算各容量的 total 和 pass_rate
        for capacity, cap_result in cat_data["results_by_capacity"].items():
            cap_total = sum(cap_result.values())
            cap_pass_rate = (cap_result["pass"] / cap_total * 100) if cap_total > 0 else 0.0
            cap_result["total"] = cap_total
            cap_result["pass_rate"] = round(cap_pass_rate, 2)
        
        # 計算 category 的 total 和 pass_rate
        cat_total = sum(cat_data["total"].values())
        cat_pass_rate = (cat_data["total"]["pass"] / cat_total * 100) if cat_total > 0 else 0.0
        cat_data["total"]["total"] = cat_total
        cat_data["total"]["pass_rate"] = round(cat_pass_rate, 2)
        
        categories.append(cat_data)
        
        total_pass += cat_data["total"]["pass"]
        total_fail += cat_data["total"]["fail"]
        total_ongoing += cat_data["total"]["ongoing"]
        total_cancel += cat_data["total"]["cancel"]
        total_check += cat_data["total"]["check"]
    
    overall_total = total_pass + total_fail + total_ongoing + total_cancel + total_check
    overall_pass_rate = (total_pass / overall_total * 100) if overall_total > 0 else 0.0
    
    # 排序容量 (按數字大小)
    def sort_capacity(cap: str) -> int:
        try:
            return int(cap.replace("GB", "").replace("TB", "000"))
        except ValueError:
            return 0
    
    sorted_capacities = sorted(list(all_capacities), key=sort_capacity)
    
    # 排序 categories (按名稱)
    categories.sort(key=lambda x: x["name"])
    
    return {
        "project_uid": project_uid,
        "project_name": project_name,
        "capacities": sorted_capacities,
        "categories": categories,
        "summary": {
            "total_pass": total_pass,
            "total_fail": total_fail,
            "total_ongoing": total_ongoing,
            "total_cancel": total_cancel,
            "total_check": total_check,
            "overall_total": overall_total,
            "overall_pass_rate": round(overall_pass_rate, 2)
        }
    }


@router.get(
    "/{project_uid}/test-summary",
    response_model=APIResponse,
    summary="取得專案測試摘要"
)
async def get_project_test_summary(
    project_uid: str,
    auth: AuthInfo = Depends(get_auth_info),
    client: SAFClient = Depends(get_saf_client)
):
    """
    取得單一專案的測試結果摘要
    
    包含各測試類別 (Compatibility, Function, Performance 等) 的測試結果，
    並依容量 (512GB, 1024GB, 2048GB, 4096GB) 分類統計。
    
    結果格式: PASS/FAIL/ONGOING/CANCEL/CHECK
    
    需要在 Header 中提供認證資訊：
    - **Authorization**: 使用者 ID (從登入 API 取得)
    - **Authorization-Name**: 使用者名稱 (從登入 API 取得)
    """
    try:
        # 取得原始資料
        raw_data = await client.get_project_test_summary(
            user_id=auth.user_id,
            username=auth.username,
            project_uid=project_uid
        )
        
        # 轉換為友善格式
        result = _transform_test_summary(raw_data)
        
        return format_response(
            success=True,
            data=result
        )
        
    except SAFAPIError as e:
        if hasattr(e, 'error_code') and e.error_code == "PROJECT_NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=format_response(
                    success=False,
                    message=f"Project not found: {project_uid}",
                    error_code="PROJECT_NOT_FOUND"
                )
            )
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
