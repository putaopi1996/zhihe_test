# schemas.py
# 这个文件定义了前端和后端交互的数据格式
# 就像是快递单的格式规范，确保收发双方都能看懂

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# 基础的用户信息
class UserBase(BaseModel):
    ycy_uid: str
    nickname: str
    zhihe_count: int

# 创建用户时需要的数据
class UserCreate(UserBase):
    qq: str  # 只有在创建或验证时才需要传密码

# 返回给前端的用户信息 (通常不包含敏感信息，但这里因为是小应用，返回也无妨，主要是不返回密码)
class UserResponse(UserBase):
    id: int
    has_claimed: bool
    claimed_at: Optional[datetime] = None

    class Config:
        orm_mode = True  # 允许从ORM模型读取数据

# 批量导入用户的请求格式
class UserImport(BaseModel):
    ycy_id: str
    nickname: str
    qq: str
    zhihe: int

# 基础的卡密信息
class CardBase(BaseModel):
    content: str
    value: int

# 创建卡密时需要的数据
class CardCreate(CardBase):
    pass

# 返回给前端的卡密信息
class CardResponse(CardBase):
    id: int
    is_used: bool

    class Config:
        orm_mode = True

# 用户领取请求
class ClaimRequest(BaseModel):
    ycy_uid: str
    qq: str

# 领取成功后的返回结果
class ClaimResult(BaseModel):
    success: bool
    message: str
    nickname: str
    zhihe_total: int
    cards: List[CardResponse] = []
