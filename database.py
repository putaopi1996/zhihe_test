# database.py
# 这个文件负责设置数据库连接
# 就像是建立通往仓库（数据库）的道路

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库文件的位置
# ./database.db 表示在当前目录下创建一个名为 database.db 的文件
SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"

# 创建数据库引擎
# check_same_thread=False 是 SQLite 在多线程环境下的特殊配置
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 创建会话工厂
# 每次我们需要通过代码操作数据库时，都需要向这个工厂"申请"一个会话(Session)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建所有模型的基类
# 后面我们定义的 "User" (用户) 和 "Card" (卡密) 表都会继承这个类
Base = declarative_base()

# 这是一个辅助函数，用于获取数据库会话
# 它的作用是：打开会话 -> 让你使用 -> 无论成功还是报错，最后都确保关闭会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
