"""
Pydantic 資料模型 (Schemas)

定義 API 請求和回應的資料結構
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ========== 認證相關 ==========

class LoginRequest(BaseModel):
    """登入請求"""
    username: str = Field(..., description="SAF 帳號")
    password: str = Field(..., description="SAF 密碼")


class LoginResponse(BaseModel):
    """登入回應"""
    id: int = Field(..., description="使用者 ID")
    name: str = Field(..., description="使用者名稱")
    mail: str = Field(..., description="使用者信箱")


class AuthInfo(BaseModel):
    """認證資訊 (用於後續 API 呼叫)"""
    user_id: int = Field(..., description="使用者 ID")
    username: str = Field(..., description="使用者名稱")


# ========== 專案相關 ==========

class Project(BaseModel):
    """專案資料"""
    key: str = Field(..., description="專案 Key")
    projectUid: str = Field(..., description="專案 UID")
    projectId: str = Field(..., description="專案 ID")
    projectName: str = Field(..., description="專案名稱")
    productCategory: Optional[str] = Field(None, description="產品類別")
    customer: Optional[str] = Field(None, description="客戶")
    controller: Optional[str] = Field(None, description="控制器")
    subVersion: Optional[str] = Field(None, description="子版本")
    nand: Optional[str] = Field(None, description="NAND 類型")
    fw: Optional[str] = Field(None, description="韌體版本")
    pl: Optional[str] = Field(None, description="負責人")
    status: int = Field(0, description="狀態")
    visible: bool = Field(True, description="是否可見")
    taskId: Optional[str] = Field(None, description="Task ID")
    nasLogFolder: Optional[str] = Field(None, description="NAS Log 資料夾")
    createdBy: Optional[str] = Field(None, description="建立者")
    createdAt: Optional[Dict[str, Any]] = Field(None, description="建立時間")
    updatedBy: Optional[str] = Field(None, description="更新者")
    updatedAt: Optional[Dict[str, Any]] = Field(None, description="更新時間")
    children: Optional[List["Project"]] = Field(None, description="子專案")

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """專案列表回應"""
    data: List[Project] = Field(..., description="專案列表")
    page: int = Field(1, description="頁碼")
    size: int = Field(50, description="每頁筆數")
    total: int = Field(0, description="總筆數")


# ========== 通用回應 ==========

class APIResponse(BaseModel):
    """通用 API 回應"""
    success: bool = Field(..., description="是否成功")
    data: Optional[Any] = Field(None, description="回應資料")
    message: Optional[str] = Field(None, description="訊息")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="時間戳記")
    error_code: Optional[str] = Field(None, description="錯誤代碼")


class HealthResponse(BaseModel):
    """健康檢查回應"""
    status: str = Field("healthy", description="服務狀態")
    version: str = Field(..., description="API 版本")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="時間戳記")


# ========== 專案測試摘要相關 ==========

class TestResultCount(BaseModel):
    """測試結果計數"""
    pass_count: int = Field(0, alias="pass", description="通過數")
    fail: int = Field(0, description="失敗數")
    ongoing: int = Field(0, description="進行中")
    cancel: int = Field(0, description="取消數")
    check: int = Field(0, description="待確認數")
    total: int = Field(0, description="總數")
    pass_rate: float = Field(0.0, description="通過率 (%)")

    class Config:
        populate_by_name = True


class CategoryResult(BaseModel):
    """單一類別的測試結果"""
    name: str = Field(..., description="類別名稱")
    results_by_capacity: Dict[str, TestResultCount] = Field(
        default_factory=dict,
        description="各容量的測試結果"
    )
    total: TestResultCount = Field(
        default_factory=TestResultCount,
        description="該類別總計"
    )


class ProjectTestSummary(BaseModel):
    """專案測試摘要"""
    project_uid: str = Field(..., description="專案 UID")
    project_name: str = Field(..., description="專案名稱")
    capacities: List[str] = Field(default_factory=list, description="所有容量")
    categories: List[CategoryResult] = Field(
        default_factory=list,
        description="各類別測試結果"
    )
    summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="總體統計"
    )


# 解決 Project 自我參照
Project.model_rebuild()
