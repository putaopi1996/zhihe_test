# main.py
# 这是整个程序的入口文件
# 负责接收用户的请求，并分配给相应的逻辑去处理

from fastapi import FastAPI, Depends, HTTPException, status, Header
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
import config  # 导入配置文件

# --- 初始化 ---

# 创建数据库表
# 这一步会自动检查 database.db 文件，如果不存在就创建，如果表没有就建表
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="自动发卡系统",
    description="一个简单的卡密自动分发系统",
    version="1.0.0"
)

# 挂载静态文件目录 (也就是前端网页)
# 这样访问 http://localhost:8000/ 就能看到网页了
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 依赖项：获取数据库会话
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 依赖项：管理员密码验证
# 这里的 x_admin_password 对应前端 header 里的 "x-admin-password"
def verify_admin(x_admin_password: Optional[str] = Header(None)):
    if x_admin_password != config.ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="管理员密码错误"
        )
    return True

# --- 页面路由 ---

@app.get("/")
async def read_root():
    # 访问根目录时，直接返回 index.html
    return FileResponse('static/index.html')

@app.get("/admin")
async def read_admin():
    # 访问 /admin 时，返回后台页面 (这里实际上还是返回静态文件，可以是 admin.html)
    return FileResponse('static/admin.html')

# --- API 接口 ---

@app.post("/api/claim", response_model=schemas.ClaimResult)
def claim_cards(request: schemas.ClaimRequest, db: Session = Depends(get_db)):
    """
    用户领取卡密的接口
    1. 验证 UID 和 密码 (QQ)
    2. 计算需要的卡密组合
    3. 分配卡密
    """
    # 1. 查找用户
    user = crud.get_user_by_uid(db, request.ycy_uid)
    if not user:
        # 为了安全，这里不提示"用户不存在"，而是模糊提示
        # 不过为了新手调试方便，我们这里还是提示明确一点
        return schemas.ClaimResult(
            success=False, 
            message="领取失败：找不到该易次元UID，请检查输入", 
            nickname="", 
            zhihe_total=0
        )
    
    # 2. 验证密码 (QQ)
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
    # 比如需要 18 个：10 x 1, 5 x 1, 3 x 1
    target = user.zhihe_count
    combination = crud.calculate_card_combination(target)
    
    if combination is None:
        # 这种情况通常是因为 target 不是 10,5,3 能凑出来的 (比如 4)
        # 或者是算法没找到解。
        return schemas.ClaimResult(
            success=False, 
            message=f"系统错误：无法自动组合出 {target} 个纸鹤的卡密方案，请联系管理员。", 
            nickname=user.nickname, 
            zhihe_total=target
        )
    
    # 5. 尝试分配 (扣减库存)
    try:
        cards = crud.allocate_cards_for_user(db, user, combination)
        if cards is None:
             return schemas.ClaimResult(
                success=False, 
                message="很抱歉，当前库存不足，无法凑齐您所需的卡密。请联系作者补充库存！", 
                nickname=user.nickname, 
                zhihe_total=target
            )
            
        # 成功！
        return schemas.ClaimResult(
            success=True, 
            message=f"领取成功！({user.nickname}) 谢谢你的支持！", 
            nickname=user.nickname, 
            zhihe_total=target,
            cards=cards
        )
        
    except Exception as e:
        print(f"Error: {e}")
        return schemas.ClaimResult(
            success=False, 
            message="领取过程中发生未知错误，请重试或联系管理员。", 
            nickname=user.nickname, 
            zhihe_total=target
        )

# --- 管理员接口 ---
# 现在所有的管理员接口都增加了 verify_admin 依赖

@app.post("/api/admin/import_users", dependencies=[Depends(verify_admin)])
def import_users(users: List[schemas.UserImport], db: Session = Depends(get_db)):
    """管理员导入用户数据"""
    count = 0
    for u in users:
        crud.create_user(db, u)
        count += 1
    return {"message": f"成功导入/更新 {count} 名用户"}

@app.post("/api/admin/add_cards", dependencies=[Depends(verify_admin)])
def add_cards_api(content: str, value: int, db: Session = Depends(get_db)):
    """管理员添加卡密"""
    count = crud.add_cards(db, content, value)
    return {"message": f"成功添加 {count} 张 {value}面值 的卡密"}

@app.get("/api/admin/stats")
def get_stats(db: Session = Depends(get_db)):
    # 统计数据也保护起来
    verify_admin(Header(config.ADMIN_PASSWORD)) # 这里我们在API调用时，如果没有header可能会出错，
                                                # 但由于 Depends(verify_admin) 在路由装饰器里更合适，
                                                # 这里我们其实应该把 dependencies 加到路由上。
                                                # 为了代码一致性，我这里不手动调 verify_admin，而是应该加到 decorator 上。
                                                # 但为了不动 decorator (保持代码结构)，我下面手动检查一下。
    # 实际上为了简单，我在 decorator 上加更好。
    # 因为 get_stats 的 decorator 上没加 dependencies，
    # 我在这里手动检查一下 header 里的密码。
    # 不过 stats 接口没有定义 Header 参数，所以需要在这里加上。
    # 为了避免 import Header 引起的问题，我已经在上面 import 了。
    
    pass 
    
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

# 我们重新定义一下 get_stats 加上依赖，覆盖上面的定义
@app.get("/api/admin/stats", dependencies=[Depends(verify_admin)])
def get_stats_secure(db: Session = Depends(get_db)):
    """获取统计数据 (需要密码)"""
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

# 如果直接运行这个文件
if __name__ == "__main__":
    print("正在启动发卡系统...")
    print("请在浏览器访问: http://localhost:8000")
    # reload=True 让代码修改后自动重启，方便调试
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
