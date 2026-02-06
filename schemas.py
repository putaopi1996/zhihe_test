# schemas.py
# =============================================
# 数据格式定义 (Pydantic Schemas)
# =============================================
# 这些类定义了前端和后端之间传递数据的格式

from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


# =============================================
# 用户领取相关
# =============================================

class ClaimRequest(BaseModel):
    """用户领取请求"""
    ycy_uid: str      # 易次元UID
    qq: str           # QQ号（密码）


class ClaimResult(BaseModel):
    """领取结果"""
    success: bool
    message: str
    nickname: str
    zhihe_total: int
    cards: Optional[List[str]] = None


# =============================================
# 用户管理相关
# =============================================

class UserImport(BaseModel):
    """导入用户时的数据格式"""
    ycy_id: str
    nickname: str
    qq: str
    zhihe: int


class UserInfo(BaseModel):
    """用户信息（返回给前端）"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    ycy_uid: str
    nickname: str
    qq: str
    zhihe_count: int
    has_claimed: bool
    claimed_at: Optional[datetime] = None


class UserUpdate(BaseModel):
    """更新用户时的数据格式"""
    nickname: Optional[str] = None
    qq: Optional[str] = None
    zhihe_count: Optional[int] = None
    has_claimed: Optional[bool] = None


class UserListResponse(BaseModel):
    """用户列表响应"""
    users: List[UserInfo]
    total: int
    page: int
    page_size: int


# =============================================
# 卡密管理相关
# =============================================

class CardInfo(BaseModel):
    """卡密信息（返回给前端）"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    code: str
    value: int
    is_used: bool
    used_by: Optional[str] = None
    used_at: Optional[datetime] = None


class CardAddRequest(BaseModel):
    """添加卡密请求"""
    content: str
    value: int


class CardUpdate(BaseModel):
    """更新卡密时的数据格式"""
    code: Optional[str] = None
    value: Optional[int] = None
    is_used: Optional[bool] = None


class CardListResponse(BaseModel):
    """卡密列表响应"""
    cards: List[CardInfo]
    total: int
    page: int
    page_size: int
