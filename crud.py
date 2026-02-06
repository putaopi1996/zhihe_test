# crud.py
# 这个文件负责具体的"干活"逻辑：增删改查数据库，以及计算卡密分配
# CRUD = Create(增), Read(查), Update(改), Delete(删)

from sqlalchemy.orm import Session
from sqlalchemy import func
import models, schemas
import datetime

# --- 核心算法 ---

def calculate_card_combination(target_amount: int):
    """
    核心算法：计算凑出目标数量所需的 10, 5, 3 面值组合。
    优先消耗大面值。
    返回一个字典: {10: count, 5: count, 3: count} 或者 None (如果凑不出来)
    """
    # 暴力尝试/回溯法。因为数值通常不大，这非常快。
    # 优先尝试最多的 10
    max_10 = target_amount // 10
    for num_10 in range(max_10, -1, -1):
        remainder_10 = target_amount - (num_10 * 10)
        
        # 尝试 5
        max_5 = remainder_10 // 5
        for num_5 in range(max_5, -1, -1):
            remainder_5 = remainder_10 - (num_5 * 5)
            
            # 尝试 3
            max_3 = remainder_5 // 3
            for num_3 in range(max_3, -1, -1):
                remainder_3 = remainder_5 - (num_3 * 3)

                # 剩下的直接用 1 填充 (因为 1 是最小单位，所以一定能除尽)
                num_1 = remainder_3
                return {10: num_10, 5: num_5, 3: num_3, 1: num_1}
    
    return None # 理论上有了1之后，只要是正整数都能凑出来

# --- 用户相关操作 ---

def get_user_by_uid(db: Session, ycy_uid: str):
    """根据易次元UID查找用户"""
    return db.query(models.User).filter(models.User.ycy_uid == ycy_uid).first()

def create_user(db: Session, user: schemas.UserImport):
    """创建新用户"""
    # 先检查是否存在，存在则更新，不存在则创建
    db_user = get_user_by_uid(db, user.ycy_id)
    if db_user:
        db_user.nickname = user.nickname
        db_user.qq = user.qq
        db_user.zhihe_count = user.zhihe
        # 注意：不重置 has_claimed，如果用户已经领过了 update 也没用
    else:
        db_user = models.User(
            ycy_uid=user.ycy_id,
            nickname=user.nickname,
            qq=user.qq,
            zhihe_count=user.zhihe
        )
        db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- 卡密相关操作 ---

def add_cards(db: Session, cards_content: str, value: int):
    """
    批量添加卡密
    cards_content: 多行字符串，一行一个卡密
    value: 面值
    """
    count = 0
    lines = cards_content.strip().split('\n')
    for line in lines:
        code = line.strip()
        if not code:
            continue
        # 检查是否已存在
        exists = db.query(models.Card).filter(models.Card.content == code).first()
        if not exists:
            new_card = models.Card(content=code, value=value)
            db.add(new_card)
            count += 1
    db.commit()
    return count

def get_available_cards_count(db: Session):
    """统计当前各面值卡密的可用库存"""
    stats = {}
    for val in [10, 5, 3, 1]:
        count = db.query(models.Card).filter(
            models.Card.value == val, 
            models.Card.is_used == False
        ).count()
        stats[val] = count
    return stats

def allocate_cards_for_user(db: Session, user: models.User, combination: dict):
    """
    为用户实际分配卡密 (数据库事务操作)
    user: 用户对象
    combination: {10: count, 5: count, 3: count} 算法算出来的结果
    """
    allocated_cards = []
    
    # 检查库存并锁定卡密
    for val, count in combination.items():
        if count == 0:
            continue
            
        # 查找可用卡密，使用 limit 取出需要的数量
        # with_for_update() 在某些数据库(如Postgres/MySQL)可以加锁避免并发问题
        # SQLite 对并发支持默认是锁库的，所以简单的查询即可，但在高并发下可能需要更严谨的处理
        # 这里对于新手项目，直接查询更新即可
        cards = db.query(models.Card).filter(
            models.Card.value == val,
            models.Card.is_used == False
        ).limit(count).all()
        
        if len(cards) < count:
            return None # 库存不足！
            
        allocated_cards.extend(cards)
    
    # 执行分配
    try:
        for card in allocated_cards:
            card.is_used = True
            card.used_by_uid = user.ycy_uid
        
        user.has_claimed = True
        user.claimed_at = datetime.datetime.now()
        
        db.commit()
        return allocated_cards
    except Exception as e:
        db.rollback()
        raise e
