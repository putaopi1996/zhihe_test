# models.py
# 这个文件定义了数据库中有哪些表，以及表里有哪些列
# 就像是设计仓库里的货架结构

from sqlalchemy import Boolean, Column, Integer, String, DateTime
from database import Base
import datetime

# 用户表模型
class User(Base):
    # __tablename__ 定义了数据库中这张表的名字
    __tablename__ = "users"

    # Column 表示这是一列
    # Integer 是整数, String 是字符串, Boolean 是布尔值(True/False)
    # primary_key=True 表示这是主键，每个用户都有独一无二的ID
    # index=True 表示为这一列建立索引，查找速度更快
    id = Column(Integer, primary_key=True, index=True)
    
    # 易次元UID，必须唯一 (unique=True)
    ycy_uid = Column(String, unique=True, index=True, comment="易次元UID")
    
    # 用户昵称
    nickname = Column(String, comment="用户昵称")
    
    # QQ号，这里用作领取密码
    qq = Column(String, comment="QQ号(即密码)")
    
    # 这个用户应该领取多少个纸鹤
    zhihe_count = Column(Integer, default=0, comment="应得纸鹤数量")
    
    # 是否已经领取过了
    has_claimed = Column(Boolean, default=False, comment="是否已领取")
    
    # 领取时间，如果没领就是空
    claimed_at = Column(DateTime, nullable=True, comment="领取时间")

# 卡密表模型
class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    
    # 卡密的内容，比如 "ABCD-1234-EFGH"
    content = Column(String, unique=True, index=True, comment="卡密内容")
    
    # 这张卡密值多少纸鹤：10, 5, 或 3
    value = Column(Integer, index=True, comment="面值")
    
    # 是否已经被发给别人了
    is_used = Column(Boolean, default=False, comment="是否已使用")
    
    # 是被哪个UID领走的
    used_by_uid = Column(String, nullable=True, index=True, comment="使用者UID")
