# main.py
# =============================================
# 卡密发放系统 v2.0 - 主程序
# =============================================
# 这是整个系统的入口文件，负责定义所有的 API 接口

from fastapi import FastAPI, Depends, HTTPException, status, Header, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
import os

import models
import schemas
import crud
import database
import config

# =============================================
# 初始化
# =============================================

# 创建数据库表
models.Base.metadata.create_all(bind=database.engine)

# 创建 FastAPI 应用
app = FastAPI(
    title="自动发卡系统",
    description="支持用户领取和后台管理的卡密系统",
    version=config.VERSION
)

# 创建静态文件目录（如果不存在）
if not os.path.exists("static"):
    os.makedirs("static")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")


# =============================================
# 依赖项（Dependency Injection）
# =============================================

def get_db():
    """获取数据库会话"""
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_admin_password(x_admin_password: str = Header(..., alias="X-Admin-Password")):
    """
    验证管理员密码
    
    - 这个函数会被用作依赖项，所有需要管理员权限的接口都会先执行这个验证
    - 密码通过 HTTP Header 传递，Header 名称是 "X-Admin-Password"
    - 如果密码错误，直接返回 401 错误，阻止后续操作
    """
    if x_admin_password != config.ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="管理员密码错误",
            headers={"WWW-Authenticate": "Password"}
        )
    return True


# =============================================
# 页面路由
# =============================================

@app.get("/")
async def index():
    """首页 - 用户领取页面"""
    return FileResponse("static/index.html")


@app.get("/admin")
async def admin_page():
    """管理后台页面"""
    return FileResponse("static/admin.html")


# =============================================
# 用户领取 API
# =============================================

@app.post("/api/claim", response_model=schemas.ClaimResult)
def claim_cards(request: schemas.ClaimRequest, db: Session = Depends(get_db)):
    """
    用户领取卡密接口
    
    流程:
    1. 验证用户是否存在
    2. 验证密码（QQ号）是否正确
    3. 检查是否已领取
    4. 计算卡密组合
    5. 分配卡密
    """
    # 1. 查找用户
    user = crud.get_user_by_uid(db, request.ycy_uid)
    if not user:
        return schemas.ClaimResult(
            success=False,
            message="领取失败：找不到该易次元UID，请检查输入",
            nickname="",
            zhihe_total=0
        )
    
    # 2. 验证密码
    if user.qq != request.qq:
        return schemas.ClaimResult(
            success=False,
            message="领取失败：QQ号(密码)错误，请重新输入",
            nickname=user.nickname,
            zhihe_total=user.zhihe_count
        )
    
    # 3. 检查是否已领取
    if user.has_claimed:
        return schemas.ClaimResult(
            success=False,
            message=f"你 ({user.nickname}) 已经领取过了，不能重复领取哦！",
            nickname=user.nickname,
            zhihe_total=user.zhihe_count
        )
    
    # 4. 计算卡密组合
    target = user.zhihe_count
    combination = crud.calculate_card_combination(target)
    
    if combination is None:
        return schemas.ClaimResult(
            success=False,
            message=f"系统错误：无法自动组合出 {target} 个纸鹤的卡密方案，请联系管理员。",
            nickname=user.nickname,
            zhihe_total=target
        )
    
    # 5. 分配卡密
    try:
        cards = crud.allocate_cards_for_user(db, user, combination)
        if cards is None:
            return schemas.ClaimResult(
                success=False,
                message="很抱歉，当前库存不足，无法凑齐您所需的卡密。请联系作者补充库存！",
                nickname=user.nickname,
                zhihe_total=target
            )
        
        return schemas.ClaimResult(
            success=True,
            message="领取成功！谢谢你的支持！",
            nickname=user.nickname,
            zhihe_total=target,
            cards=cards
        )
    except Exception as e:
        print(f"领取错误: {e}")
        return schemas.ClaimResult(
            success=False,
            message="领取过程中发生错误，请重试或联系管理员。",
            nickname=user.nickname,
            zhihe_total=target
        )


# =============================================
# 管理员 API - 统计
# =============================================

@app.get("/api/admin/stats")
def get_stats(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_password)  # 密码验证
):
    """获取系统统计数据"""
    stocks = crud.get_available_cards_count(db)
    total_users = db.query(models.User).count()
    claimed_users = db.query(models.User).filter(models.User.has_claimed == True).count()
    
    return {
        "stock": stocks,
        "users": {
            "total": total_users,
            "claimed": claimed_users
        }
    }


# =============================================
# 管理员 API - 用户管理
# =============================================

@app.get("/api/admin/users", response_model=schemas.UserListResponse)
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_password)
):
    """获取用户列表（分页）"""
    users, total = crud.get_users_paginated(db, page, page_size)
    return schemas.UserListResponse(
        users=[schemas.UserInfo.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size
    )


@app.post("/api/admin/users/import")
def import_users(
    users: List[schemas.UserImport],
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_password)
):
    """批量导入用户"""
    count = 0
    for u in users:
        crud.create_or_update_user(db, u)
        count += 1
    return {"message": f"成功导入/更新 {count} 名用户"}


@app.put("/api/admin/users/{user_id}")
def update_user(
    user_id: int,
    data: schemas.UserUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_password)
):
    """修改用户信息"""
    user = crud.update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"message": "修改成功", "user": schemas.UserInfo.model_validate(user)}


@app.delete("/api/admin/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_password)
):
    """删除用户"""
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"message": "删除成功"}


# =============================================
# 管理员 API - 卡密管理
# =============================================

@app.get("/api/admin/cards", response_model=schemas.CardListResponse)
def list_cards(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    value: Optional[int] = Query(None),
    used: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_password)
):
    """获取卡密列表（分页，可筛选）"""
    cards, total = crud.get_cards_paginated(db, page, page_size, value, used)
    return schemas.CardListResponse(
        cards=[schemas.CardInfo.model_validate(c) for c in cards],
        total=total,
        page=page,
        page_size=page_size
    )


@app.post("/api/admin/cards/add")
def add_cards(
    request: schemas.CardAddRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_password)
):
    """添加卡密 (通过 Body 传递)"""
    count = crud.add_cards(db, request.content, request.value)
    return {"message": f"成功添加 {count} 张 {request.value}面值 的卡密"}


@app.put("/api/admin/cards/{card_id}")
def update_card(
    card_id: int,
    data: schemas.CardUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_password)
):
    """修改卡密信息"""
    card = crud.update_card(db, card_id, data)
    if not card:
        raise HTTPException(status_code=404, detail="卡密不存在")
    return {"message": "修改成功", "card": schemas.CardInfo.model_validate(card)}


@app.delete("/api/admin/cards/{card_id}")
def delete_card(
    card_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_password)
):
    """删除卡密"""
    success = crud.delete_card(db, card_id)
    if not success:
        raise HTTPException(status_code=404, detail="卡密不存在")
    return {"message": "删除成功"}


# =============================================
# 启动入口
# =============================================

if __name__ == "__main__":
    print("=" * 50)
    print("  卡密发放系统 v2.0 启动中...")
    print("  访问地址: http://localhost:8000")
    print("  后台地址: http://localhost:8000/admin")
    print("=" * 50)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
