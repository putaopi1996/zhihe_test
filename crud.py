# crud.py
# =============================================
# 数据库操作函数 (CRUD)
# =============================================
# CRUD = Create(创建), Read(读取), Update(更新), Delete(删除)

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Tuple, Optional, Dict
import models
import schemas


# =============================================
# 用户相关操作
# =============================================

def get_user_by_uid(db: Session, ycy_uid: str) -> Optional[models.User]:
    """通过易次元UID查找用户"""
    return db.query(models.User).filter(models.User.ycy_uid == ycy_uid).first()


def get_users_paginated(db: Session, page: int, page_size: int) -> Tuple[List[models.User], int]:
    """分页获取用户列表"""
    total = db.query(models.User).count()
    users = db.query(models.User).offset((page - 1) * page_size).limit(page_size).all()
    return users, total


def create_or_update_user(db: Session, user_data: schemas.UserImport) -> models.User:
    """创建或更新用户"""
    existing = db.query(models.User).filter(models.User.ycy_uid == user_data.ycy_id).first()
    
    if existing:
        existing.nickname = user_data.nickname
        existing.qq = user_data.qq
        existing.zhihe_count = user_data.zhihe
        db.commit()
        db.refresh(existing)
        return existing
    else:
        new_user = models.User(
            ycy_uid=user_data.ycy_id,
            nickname=user_data.nickname,
            qq=user_data.qq,
            zhihe_count=user_data.zhihe,
            has_claimed=False
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user


def update_user(db: Session, user_id: int, data: schemas.UserUpdate) -> Optional[models.User]:
    """更新用户信息"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None
    
    if data.nickname is not None:
        user.nickname = data.nickname
    if data.qq is not None:
        user.qq = data.qq
    if data.zhihe_count is not None:
        user.zhihe_count = data.zhihe_count
    if data.has_claimed is not None:
        user.has_claimed = data.has_claimed
        if not data.has_claimed:
            user.claimed_at = None
    
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    """删除用户"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True


# =============================================
# 卡密相关操作
# =============================================

def get_cards_paginated(
    db: Session, 
    page: int, 
    page_size: int,
    value: Optional[int] = None,
    used: Optional[bool] = None
) -> Tuple[List[models.Card], int]:
    """分页获取卡密列表（可筛选）"""
    query = db.query(models.Card)
    
    if value is not None:
        query = query.filter(models.Card.value == value)
    if used is not None:
        query = query.filter(models.Card.is_used == used)
    
    total = query.count()
    cards = query.offset((page - 1) * page_size).limit(page_size).all()
    return cards, total


def add_cards(db: Session, content: str, value: int) -> int:
    """批量添加卡密"""
    lines = content.strip().split('\n')
    count = 0
    
    for line in lines:
        code = line.strip()
        if code:
            # 检查是否已存在
            existing = db.query(models.Card).filter(models.Card.code == code).first()
            if not existing:
                card = models.Card(code=code, value=value, is_used=False)
                db.add(card)
                count += 1
    
    db.commit()
    return count


def update_card(db: Session, card_id: int, data: schemas.CardUpdate) -> Optional[models.Card]:
    """更新卡密信息"""
    card = db.query(models.Card).filter(models.Card.id == card_id).first()
    if not card:
        return None
    
    if data.code is not None:
        card.code = data.code
    if data.value is not None:
        card.value = data.value
    if data.is_used is not None:
        card.is_used = data.is_used
        if not data.is_used:
            card.used_by = None
            card.used_at = None
    
    db.commit()
    db.refresh(card)
    return card


def delete_card(db: Session, card_id: int) -> bool:
    """删除卡密"""
    card = db.query(models.Card).filter(models.Card.id == card_id).first()
    if not card:
        return False
    db.delete(card)
    db.commit()
    return True


def get_available_cards_count(db: Session) -> Dict[str, int]:
    """获取各面值可用卡密数量"""
    result = {}
    for value in [10, 5, 3, 1]:
        count = db.query(models.Card).filter(
            models.Card.value == value,
            models.Card.is_used == False
        ).count()
        result[str(value)] = count
    return result


# =============================================
# 卡密分配算法
# =============================================

def calculate_card_combination(target: int) -> Optional[Dict[int, int]]:
    """
    计算凑出目标数字的卡密组合
    
    使用贪心算法：优先使用大面值的卡密
    返回格式: {面值: 数量} 例如 {10: 1, 5: 1, 3: 1} 表示18
    """
    if target <= 0:
        return None
    
    result = {10: 0, 5: 0, 3: 0, 1: 0}
    remaining = target
    
    # 贪心：从大到小尝试
    for value in [10, 5, 3, 1]:
        if remaining >= value:
            count = remaining // value
            result[value] = count
            remaining -= count * value
    
    if remaining != 0:
        return None
    
    return result


def allocate_cards_for_user(
    db: Session, 
    user: models.User, 
    combination: Dict[int, int]
) -> Optional[List[str]]:
    """
    为用户分配卡密
    
    1. 检查库存是否充足
    2. 标记卡密为已使用
    3. 更新用户状态
    """
    import datetime
    
    allocated_cards = []
    
    # 检查库存并分配
    for value, count in combination.items():
        if count <= 0:
            continue
        
        available = db.query(models.Card).filter(
            models.Card.value == value,
            models.Card.is_used == False
        ).limit(count).all()
        
        if len(available) < count:
            # 库存不足，回滚
            return None
        
        for card in available:
            card.is_used = True
            card.used_by = user.ycy_uid
            card.used_at = datetime.datetime.now()
            allocated_cards.append(card.code)
    
    # 更新用户状态
    user.has_claimed = True
    user.claimed_at = datetime.datetime.now()
    
    db.commit()
    return allocated_cards
