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


@router.get(
    "/{project_id}/firmwares",
    response_model=APIResponse,
    summary="取得專案的 Firmware 列表"
)
async def get_project_firmwares(
    project_id: str,
    auth: AuthInfo = Depends(get_auth_info),
    client: SAFClient = Depends(get_saf_client)
):
    """
    依 Project ID 取得該專案下所有的 Firmware 版本列表
    
    回傳每個 firmware 的:
    - **fw**: Firmware 名稱 (如 MASTX9KA, G200X9R1)
    - **subVersion**: 子版本 (如 AA)
    - **projectUid**: 對應的 Project UID
    
    需要在 Header 中提供認證資訊：
    - **Authorization**: 使用者 ID (從登入 API 取得)
    - **Authorization-Name**: 使用者名稱 (從登入 API 取得)
    """
    try:
        result = await client.get_fws_by_project_id(
            user_id=auth.user_id,
            username=auth.username,
            project_id=project_id
        )
        
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
                    message=f"Project not found: {project_id}",
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


def _parse_percentage_string(pct_str: str) -> float:
    """
    解析百分比字串
    
    Args:
        pct_str: 如 "61/61 (100%)" 或 "0%" 或 "100%"
        
    Returns:
        百分比數值 (0.0 - 100.0)
    """
    if not pct_str:
        return 0.0
    
    try:
        # 嘗試找到括號內的百分比 "61/61 (100%)"
        if "(" in pct_str and "%" in pct_str:
            start = pct_str.rfind("(") + 1
            end = pct_str.rfind("%")
            return float(pct_str[start:end])
        
        # 直接是百分比 "100%" 或 "0%"
        if "%" in pct_str:
            return float(pct_str.replace("%", ""))
        
        return 0.0
    except (ValueError, IndexError):
        return 0.0


def _parse_fraction_string(frac_str: str) -> tuple:
    """
    解析分數字串
    
    Args:
        frac_str: 如 "0/140 (0%)" 或 "61/61 (100%)"
        
    Returns:
        (numerator, denominator) 元組
    """
    if not frac_str:
        return (0, 0)
    
    try:
        # 取得分數部分 "0/140"
        if "/" in frac_str:
            frac_part = frac_str.split("(")[0].strip()
            parts = frac_part.split("/")
            return (int(parts[0]), int(parts[1]))
        return (0, 0)
    except (ValueError, IndexError):
        return (0, 0)


def _transform_firmware_summary(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    將 SAF 原始資料轉換為 Firmware 詳細摘要格式
    
    SAF API 回傳結構：
    {
        "projectId": "...",
        "projectName": "...",
        "fws": [{
            "projectUid": "...",
            "fwName": "...",
            "subVersionName": "...",
            "internalSummary_1": {
                "name": "...",
                "totalStmsSampleCount": 140,
                "sampleUsedRate": "0%",
                "totalTestItems": 61,
                "passedCnt": 44,
                "failedCnt": 16,
                "completionRate": "61/61 (100%)",
                "conditionalPassedCnt": 1
            },
            "internalSummary_2": {
                "realTestCount": 61
            },
            "externalSummary": {
                "totalSampleQuantity": 140,
                "sampleUtilizationRate": "0/140 (0%)",
                "passedCnt": 44,
                "failedCnt": 16,
                "sampleTestItemCompletionRate": "61/61 (100%)",
                "sampleTestItemFailRate": "16/61 (26%)",
                "testItemExecutionRate": "39/39 (100%)",
                "testItemFailRate": "14/39 (36%)",
                "conditionalPassedCnt": 1,
                "itemPassedCnt": 25,
                "itemFailedCnt": 14,
                "totalItemCnt": 39
            }
        }]
    }
    """
    # 取得第一個 firmware 的資料
    fws = raw_data.get("fws", [])
    if not fws:
        return {
            "project_uid": "",
            "fw_name": "",
            "sub_version": "",
            "task_name": "",
            "overview": {
                "total_test_items": 0,
                "passed": 0,
                "failed": 0,
                "conditional_passed": 0,
                "completion_rate": 0.0,
                "pass_rate": 0.0
            },
            "sample_stats": {
                "total_samples": 0,
                "samples_used": 0,
                "utilization_rate": 0.0
            },
            "test_item_stats": {
                "total_items": 0,
                "passed_items": 0,
                "failed_items": 0,
                "execution_rate": 0.0,
                "fail_rate": 0.0
            }
        }
    
    fw = fws[0]
    project_uid = fw.get("projectUid", "")
    fw_name = fw.get("fwName", "")
    sub_version = fw.get("subVersionName", "")
    
    # 解析 internalSummary_1
    internal_1 = fw.get("internalSummary_1", {})
    task_name = internal_1.get("name", "")
    total_samples = internal_1.get("totalStmsSampleCount", 0)
    sample_used_rate = _parse_percentage_string(internal_1.get("sampleUsedRate", "0%"))
    total_test_items = internal_1.get("totalTestItems", 0)
    passed_cnt = internal_1.get("passedCnt", 0)
    failed_cnt = internal_1.get("failedCnt", 0)
    completion_rate = _parse_percentage_string(internal_1.get("completionRate", "0%"))
    conditional_passed = internal_1.get("conditionalPassedCnt", 0)
    
    # 計算通過率
    total_tests = passed_cnt + failed_cnt
    pass_rate = (passed_cnt / total_tests * 100) if total_tests > 0 else 0.0
    
    # 計算已使用樣本數
    samples_used = int(total_samples * sample_used_rate / 100) if total_samples > 0 else 0
    
    # 解析 externalSummary
    external = fw.get("externalSummary", {})
    total_item_cnt = external.get("totalItemCnt", 0)
    item_passed_cnt = external.get("itemPassedCnt", 0)
    item_failed_cnt = external.get("itemFailedCnt", 0)
    execution_rate = _parse_percentage_string(external.get("testItemExecutionRate", "0%"))
    fail_rate = _parse_percentage_string(external.get("testItemFailRate", "0%"))
    
    return {
        "project_uid": project_uid,
        "fw_name": fw_name,
        "sub_version": sub_version,
        "task_name": task_name,
        "overview": {
            "total_test_items": total_test_items,
            "passed": passed_cnt,
            "failed": failed_cnt,
            "conditional_passed": conditional_passed,
            "completion_rate": round(completion_rate, 2),
            "pass_rate": round(pass_rate, 2)
        },
        "sample_stats": {
            "total_samples": total_samples,
            "samples_used": samples_used,
            "utilization_rate": round(sample_used_rate, 2)
        },
        "test_item_stats": {
            "total_items": total_item_cnt,
            "passed_items": item_passed_cnt,
            "failed_items": item_failed_cnt,
            "execution_rate": round(execution_rate, 2),
            "fail_rate": round(fail_rate, 2)
        }
    }


@router.get(
    "/{project_uid}/firmware-summary",
    response_model=APIResponse,
    summary="取得 Firmware 詳細摘要"
)
async def get_firmware_summary(
    project_uid: str,
    auth: AuthInfo = Depends(get_auth_info),
    client: SAFClient = Depends(get_saf_client)
):
    """
    取得單一 Firmware 的詳細測試統計
    
    包含：
    - **overview**: 總覽統計 (總測試項目、通過/失敗數、完成率、通過率)
    - **sample_stats**: 樣本統計 (總樣本數、已使用數、利用率)
    - **test_item_stats**: 測試項目統計 (項目數、執行率、失敗率)
    
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
        
        # 轉換為 Firmware 詳細摘要格式
        result = _transform_firmware_summary(raw_data)
        
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


def _parse_result_string(result_str: str) -> Dict[str, int]:
    """
    解析結果字串
    
    SAF API 回傳格式: Ongoing/Passed/Conditional Passed/Failed/Interrupted
    (注意：不是 PASS/FAIL/ONGOING/CANCEL/CHECK)
    
    Args:
        result_str: 如 "0/8/0/0/0" (Ongoing/Passed/Conditional/Failed/Interrupted)
        
    Returns:
        {'ongoing': 0, 'pass': 8, 'conditional_pass': 0, 'fail': 0, 'check': 0}
    """
    parts = result_str.split("/")
    if len(parts) != 5:
        return {"ongoing": 0, "pass": 0, "conditional_pass": 0, "fail": 0, "check": 0}
    
    try:
        return {
            "ongoing": int(parts[0]),
            "pass": int(parts[1]),
            "conditional_pass": int(parts[2]),
            "fail": int(parts[3]),
            "check": int(parts[4]),
        }
    except ValueError:
        return {"ongoing": 0, "pass": 0, "conditional_pass": 0, "fail": 0, "check": 0}


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
                "total_conditional_pass": 0,
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
                        "ongoing": 0,
                        "pass": 0,
                        "conditional_pass": 0,
                        "fail": 0,
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
                        "ongoing": 0, "pass": 0, "conditional_pass": 0, "fail": 0, "check": 0
                    }
                
                # 累加
                for key in ["ongoing", "pass", "conditional_pass", "fail", "check"]:
                    categories_map[cat_name]["results_by_capacity"][capacity][key] += result[key]
                    categories_map[cat_name]["total"][key] += result[key]
    
    # 計算總計和 pass rate
    total_ongoing = 0
    total_pass = 0
    total_conditional_pass = 0
    total_fail = 0
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
        
        total_ongoing += cat_data["total"]["ongoing"]
        total_pass += cat_data["total"]["pass"]
        total_conditional_pass += cat_data["total"]["conditional_pass"]
        total_fail += cat_data["total"]["fail"]
        total_check += cat_data["total"]["check"]
    
    overall_total = total_ongoing + total_pass + total_conditional_pass + total_fail + total_check
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
            "total_ongoing": total_ongoing,
            "total_pass": total_pass,
            "total_conditional_pass": total_conditional_pass,
            "total_fail": total_fail,
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


def _transform_firmware_detail(fw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    將單一 Firmware 資料轉換為詳細格式
    
    Args:
        fw_data: SAF API 回傳的單一 firmware 資料
        
    Returns:
        FirmwareDetail 格式的字典
    """
    project_uid = fw_data.get("projectUid", "")
    fw_name = fw_data.get("fwName", "")
    sub_version = fw_data.get("subVersionName", "")
    
    # 解析 internalSummary_1
    internal_1 = fw_data.get("internalSummary_1", {})
    task_name = internal_1.get("name", "")
    total_samples = internal_1.get("totalStmsSampleCount", 0)
    sample_used_rate = _parse_percentage_string(internal_1.get("sampleUsedRate", "0%"))
    total_test_items = internal_1.get("totalTestItems", 0)
    passed = internal_1.get("passedCnt", 0)
    failed = internal_1.get("failedCnt", 0)
    conditional_passed = internal_1.get("conditionalPassedCnt", 0)
    completion_rate = _parse_percentage_string(internal_1.get("completionRate", "0%"))
    
    # 解析 internalSummary_2
    internal_2 = fw_data.get("internalSummary_2", {})
    real_test_count = internal_2.get("realTestCount", 0)
    
    # 解析 externalSummary
    external = fw_data.get("externalSummary", {})
    total_sample_quantity = external.get("totalSampleQuantity", 0)
    sample_utilization_rate = _parse_percentage_string(external.get("sampleUtilizationRate", "0%"))
    ext_passed = external.get("passedCnt", 0)
    ext_failed = external.get("failedCnt", 0)
    sample_completion_rate = _parse_percentage_string(external.get("sampleTestItemCompletionRate", "0%"))
    sample_fail_rate = _parse_percentage_string(external.get("sampleTestItemFailRate", "0%"))
    execution_rate = _parse_percentage_string(external.get("testItemExecutionRate", "0%"))
    item_fail_rate = _parse_percentage_string(external.get("testItemFailRate", "0%"))
    item_passed = external.get("itemPassedCnt", 0)
    item_failed = external.get("itemFailedCnt", 0)
    total_items = external.get("totalItemCnt", 0)
    
    return {
        "project_uid": project_uid,
        "fw_name": fw_name,
        "sub_version": sub_version,
        "internal_summary": {
            "task_name": task_name,
            "total_samples": total_samples,
            "sample_used_rate": round(sample_used_rate, 2),
            "total_test_items": total_test_items,
            "passed": passed,
            "failed": failed,
            "conditional_passed": conditional_passed,
            "completion_rate": round(completion_rate, 2),
            "real_test_count": real_test_count
        },
        "external_summary": {
            "total_sample_quantity": total_sample_quantity,
            "sample_utilization_rate": round(sample_utilization_rate, 2),
            "passed": ext_passed,
            "failed": ext_failed,
            "sample_completion_rate": round(sample_completion_rate, 2),
            "sample_fail_rate": round(sample_fail_rate, 2),
            "execution_rate": round(execution_rate, 2),
            "item_fail_rate": round(item_fail_rate, 2),
            "item_passed": item_passed,
            "item_failed": item_failed,
            "total_items": total_items
        }
    }


def _aggregate_firmware_stats(firmwares: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    聚合所有 Firmware 的統計數據
    
    Args:
        firmwares: Firmware 詳細資料列表
        
    Returns:
        聚合統計字典
    """
    total_test_items = 0
    total_passed = 0
    total_failed = 0
    total_conditional_passed = 0
    
    for fw in firmwares:
        internal = fw.get("internal_summary", {})
        total_test_items += internal.get("total_test_items", 0)
        total_passed += internal.get("passed", 0)
        total_failed += internal.get("failed", 0)
        total_conditional_passed += internal.get("conditional_passed", 0)
    
    # 計算通過率 (不含條件通過)
    total_tests = total_passed + total_failed
    overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0.0
    
    return {
        "total_test_items": total_test_items,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "total_conditional_passed": total_conditional_passed,
        "overall_pass_rate": round(overall_pass_rate, 2)
    }


def _transform_full_summary(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    將 SAF 原始資料轉換為完整專案摘要格式
    
    Args:
        raw_data: SAF API 回傳的原始資料
        
    Returns:
        FullProjectSummary 格式的字典
    """
    project_id = raw_data.get("projectId", "")
    project_name = raw_data.get("projectName", "")
    fws = raw_data.get("fws", [])
    
    # 轉換所有 Firmware 資料
    firmwares = [_transform_firmware_detail(fw) for fw in fws]
    
    # 聚合統計
    aggregated_stats = _aggregate_firmware_stats(firmwares)
    
    return {
        "project_id": project_id,
        "project_name": project_name,
        "total_firmwares": len(firmwares),
        "firmwares": firmwares,
        "aggregated_stats": aggregated_stats
    }


@router.get(
    "/{project_uid}/full-summary",
    response_model=APIResponse,
    summary="取得完整專案摘要"
)
async def get_full_project_summary(
    project_uid: str,
    auth: AuthInfo = Depends(get_auth_info),
    client: SAFClient = Depends(get_saf_client)
):
    """
    取得專案的完整摘要，包含所有 Firmware 的詳細統計資訊
    
    包含：
    - **firmwares**: 所有 Firmware 的詳細資料
        - **internal_summary**: 內部摘要 (樣本數、測試項目數、通過/失敗數等)
        - **external_summary**: 外部摘要 (執行率、失敗率等)
    - **aggregated_stats**: 聚合統計 (所有 Firmware 的總計)
    
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
        
        # 轉換為完整專案摘要格式
        result = _transform_full_summary(raw_data)
        
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


def _parse_detail_result_string(result_str: str) -> Dict[str, int]:
    """
    解析 details 的結果字串
    
    格式: Ongoing/Passed/Conditional Passed/Failed/Interrupted
    
    Args:
        result_str: 如 "0/1/0/0/0"
        
    Returns:
        {'ongoing': 0, 'passed': 1, 'conditional_passed': 0, 'failed': 0, 'interrupted': 0, 'total': 1}
    """
    parts = result_str.split("/")
    if len(parts) != 5:
        return {
            "ongoing": 0,
            "passed": 0,
            "conditional_passed": 0,
            "failed": 0,
            "interrupted": 0,
            "total": 0
        }
    
    try:
        ongoing = int(parts[0])
        passed = int(parts[1])
        conditional_passed = int(parts[2])
        failed = int(parts[3])
        interrupted = int(parts[4])
        total = ongoing + passed + conditional_passed + failed + interrupted
        
        return {
            "ongoing": ongoing,
            "passed": passed,
            "conditional_passed": conditional_passed,
            "failed": failed,
            "interrupted": interrupted,
            "total": total
        }
    except ValueError:
        return {
            "ongoing": 0,
            "passed": 0,
            "conditional_passed": 0,
            "failed": 0,
            "interrupted": 0,
            "total": 0
        }


def _transform_test_details(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    將 SAF 原始資料轉換為測試項目詳細資料格式
    
    Args:
        raw_data: SAF API 回傳的原始資料
        
    Returns:
        TestDetailsResponse 格式的字典
    """
    project_name = raw_data.get("projectName", "")
    
    # 取得第一個 firmware 的資料
    fws = raw_data.get("fws", [])
    if not fws:
        return {
            "project_uid": "",
            "project_name": project_name,
            "fw_name": "",
            "sub_version": "",
            "capacities": [],
            "total_items": 0,
            "details": [],
            "summary": {
                "total_ongoing": 0,
                "total_passed": 0,
                "total_conditional_passed": 0,
                "total_failed": 0,
                "total_interrupted": 0,
                "overall_total": 0,
                "pass_rate": 0.0
            }
        }
    
    fw = fws[0]
    project_uid = fw.get("projectUid", "")
    fw_name = fw.get("fwName", "")
    sub_version = fw.get("subVersionName", "")
    
    # 取得 details 資料
    raw_details = fw.get("details", [])
    
    # 收集所有容量
    all_capacities = set()
    
    # 總計統計
    total_ongoing = 0
    total_passed = 0
    total_conditional_passed = 0
    total_failed = 0
    total_interrupted = 0
    
    # 轉換 details
    details = []
    for item in raw_details:
        category_name = item.get("categoryName", "Unknown")
        test_item_name = item.get("testItemName", "Unknown")
        sample_capacity = item.get("sampleCapacity", "")
        note = item.get("note", "")
        
        # 處理各容量的結果
        size_results = []
        for size_data in item.get("sizeResult", []):
            size = size_data.get("size", "Unknown")
            result_str = size_data.get("result", "0/0/0/0/0")
            
            all_capacities.add(size)
            result = _parse_detail_result_string(result_str)
            
            size_results.append({
                "size": size,
                "result": result
            })
        
        # 處理該測試項目的總計
        total_str = item.get("total", "0/0/0/0/0")
        item_total = _parse_detail_result_string(total_str)
        
        # 累加到總計
        total_ongoing += item_total["ongoing"]
        total_passed += item_total["passed"]
        total_conditional_passed += item_total["conditional_passed"]
        total_failed += item_total["failed"]
        total_interrupted += item_total["interrupted"]
        
        details.append({
            "category_name": category_name,
            "test_item_name": test_item_name,
            "size_results": size_results,
            "total": item_total,
            "sample_capacity": sample_capacity,
            "note": note
        })
    
    # 計算通過率 (passed / (passed + failed))
    completed_tests = total_passed + total_failed
    pass_rate = (total_passed / completed_tests * 100) if completed_tests > 0 else 0.0
    
    # 排序容量 (按數字大小)
    def sort_capacity(cap: str) -> int:
        try:
            return int(cap.replace("GB", "").replace("TB", "000"))
        except ValueError:
            return 0
    
    sorted_capacities = sorted(list(all_capacities), key=sort_capacity)
    
    overall_total = (
        total_ongoing + total_passed + total_conditional_passed +
        total_failed + total_interrupted
    )
    
    return {
        "project_uid": project_uid,
        "project_name": project_name,
        "fw_name": fw_name,
        "sub_version": sub_version,
        "capacities": sorted_capacities,
        "total_items": len(details),
        "details": details,
        "summary": {
            "total_ongoing": total_ongoing,
            "total_passed": total_passed,
            "total_conditional_passed": total_conditional_passed,
            "total_failed": total_failed,
            "total_interrupted": total_interrupted,
            "overall_total": overall_total,
            "pass_rate": round(pass_rate, 2)
        }
    }


@router.get(
    "/{project_uid}/test-details",
    response_model=APIResponse,
    summary="取得測試項目詳細資料"
)
async def get_project_test_details(
    project_uid: str,
    auth: AuthInfo = Depends(get_auth_info),
    client: SAFClient = Depends(get_saf_client)
):
    """
    取得專案的所有測試項目詳細資料
    
    包含每個測試項目的：
    - **category_name**: 測試類別名稱
    - **test_item_name**: 測試項目名稱
    - **size_results**: 各容量的測試結果
    - **total**: 該測試項目的總計
    - **sample_capacity**: 使用的樣品容量配置
    - **note**: 測試說明/備註
    
    結果格式: Ongoing/Passed/Conditional Passed/Failed/Interrupted
    
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
        
        # 轉換為測試項目詳細資料格式
        result = _transform_test_details(raw_data)
        
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


def _transform_dashboard(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    將 SAF 原始資料轉換為專案儀表板格式
    
    Args:
        raw_data: SAF API 回傳的原始資料
        
    Returns:
        ProjectDashboard 格式的字典
    """
    project_id = raw_data.get("projectId", "")
    project_name = raw_data.get("projectName", "")
    fws = raw_data.get("fws", [])
    
    # 總計統計
    total_passed = 0
    total_failed = 0
    total_ongoing = 0
    total_interrupted = 0
    overall_total = 0
    
    # 轉換 Firmware 資料
    firmwares = []
    for fw in fws:
        fw_name = fw.get("fwName", "")
        sub_version = fw.get("subVersionName", "")
        passed = fw.get("itemPassedCnt", 0) or 0
        failed = fw.get("itemFailedCnt", 0) or 0
        ongoing = fw.get("itemOngoingCnt", 0) or 0
        interrupted = fw.get("itemInterruptCnt", 0) or 0
        total = fw.get("totalItemCnt", 0) or 0
        
        # 計算通過率: passed / (passed + failed) * 100
        completed = passed + failed
        pass_rate = (passed / completed * 100) if completed > 0 else 0.0
        
        # 計算完成率: (passed + failed) / total * 100
        completion_rate = (completed / total * 100) if total > 0 else 0.0
        
        firmwares.append({
            "fw_name": fw_name,
            "sub_version": sub_version,
            "passed": passed,
            "failed": failed,
            "ongoing": ongoing,
            "interrupted": interrupted,
            "total": total,
            "pass_rate": round(pass_rate, 2),
            "completion_rate": round(completion_rate, 2)
        })
        
        # 累加到總計
        total_passed += passed
        total_failed += failed
        total_ongoing += ongoing
        total_interrupted += interrupted
        overall_total += total
    
    # 計算整體通過率
    overall_completed = total_passed + total_failed
    overall_pass_rate = (total_passed / overall_completed * 100) if overall_completed > 0 else 0.0
    
    return {
        "project_id": project_id,
        "project_name": project_name,
        "total_firmwares": len(firmwares),
        "firmwares": firmwares,
        "summary": {
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_ongoing": total_ongoing,
            "total_interrupted": total_interrupted,
            "overall_total": overall_total,
            "overall_pass_rate": round(overall_pass_rate, 2)
        }
    }


@router.get(
    "/{project_id}/dashboard",
    response_model=APIResponse,
    summary="取得專案儀表板"
)
async def get_project_dashboard(
    project_id: str,
    auth: AuthInfo = Depends(get_auth_info),
    client: SAFClient = Depends(get_saf_client)
):
    """
    取得專案儀表板資料，顯示所有 Firmware 的測試進度概覽
    
    包含每個 Firmware 的：
    - **fw_name**: Firmware 名稱
    - **sub_version**: 子版本
    - **passed**: 通過數
    - **failed**: 失敗數
    - **ongoing**: 進行中
    - **interrupted**: 中斷數
    - **total**: 總測試項目數
    - **pass_rate**: 通過率 (%)
    - **completion_rate**: 完成率 (%)
    
    需要在 Header 中提供認證資訊：
    - **Authorization**: 使用者 ID (從登入 API 取得)
    - **Authorization-Name**: 使用者名稱 (從登入 API 取得)
    """
    try:
        # 取得原始資料
        raw_data = await client.get_project_dashboard(
            user_id=auth.user_id,
            username=auth.username,
            project_id=project_id
        )
        
        # 轉換為儀表板格式
        result = _transform_dashboard(raw_data)
        
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
                    message=f"Project not found: {project_id}",
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


def _transform_known_issue(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    將 SAF 原始 Known Issue 資料轉換為友善格式
    
    Args:
        item: SAF API 回傳的單一 known issue 資料
        
    Returns:
        轉換後的 known issue 字典
    """
    return {
        "id": item.get("id", ""),
        "project_id": item.get("projectId", ""),
        "project_name": item.get("projectName", ""),
        "root_id": item.get("rootId", ""),
        "test_item_name": item.get("testItemName", ""),
        "issue_id": item.get("issueId", ""),
        "case_name": item.get("caseName", ""),
        "case_path": item.get("casePath", ""),
        "created_by": item.get("createdBy", ""),
        "created_at": item.get("createdAt", ""),
        "jira_id": item.get("jiraId", ""),
        "note": item.get("note", ""),
        "is_enable": item.get("isEnable", True),
        "jira_link": item.get("jiraLink", ""),
    }


@router.post(
    "/known-issues",
    response_model=APIResponse,
    summary="取得 Known Issues 列表"
)
async def get_known_issues(
    project_id: Optional[List[str]] = Query(
        default=None,
        description="篩選的專案 ID 列表"
    ),
    root_id: Optional[List[str]] = Query(
        default=None,
        description="篩選的 Root ID 列表"
    ),
    show_disable: bool = Query(
        default=True,
        description="是否顯示停用的 Issues"
    ),
    auth: AuthInfo = Depends(get_auth_info),
    client: SAFClient = Depends(get_saf_client)
):
    """
    取得所有 Known Issues 列表
    
    可透過以下參數篩選：
    - **project_id**: 專案 ID 列表 (可多選)
    - **root_id**: Root ID 列表 (可多選)
    - **show_disable**: 是否顯示停用的 Issues (預設 true)
    
    回傳每個 Known Issue 的：
    - **id**: Issue ID
    - **project_id**: 專案 ID
    - **project_name**: 專案名稱
    - **root_id**: Root ID
    - **test_item_name**: 測試項目名稱
    - **issue_id**: Issue 編號 (如 Oakgate-1)
    - **case_name**: Case 名稱
    - **case_path**: Case 路徑
    - **created_by**: 建立者
    - **created_at**: 建立時間
    - **jira_id**: JIRA ID
    - **note**: 備註
    - **is_enable**: 是否啟用
    - **jira_link**: JIRA 連結
    
    需要在 Header 中提供認證資訊：
    - **Authorization**: 使用者 ID (從登入 API 取得)
    - **Authorization-Name**: 使用者名稱 (從登入 API 取得)
    """
    try:
        # 呼叫 SAF API
        raw_data = await client.list_known_issues(
            user_id=auth.user_id,
            username=auth.username,
            project_id=project_id or [],
            root_id=root_id or [],
            show_disable=show_disable
        )
        
        # 轉換資料格式
        items = raw_data.get("items", [])
        transformed_items = [_transform_known_issue(item) for item in items]
        
        result = {
            "items": transformed_items,
            "total": len(transformed_items)
        }
        
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