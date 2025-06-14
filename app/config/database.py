from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
from .settings import settings

# 配置日志
logger = logging.getLogger(__name__)

# 创建数据库引擎
try:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,  # 连接池健康检查
        pool_size=5,         # 连接池大小
        max_overflow=10,     # 最大溢出连接数
        pool_recycle=3600,   # 连接回收时间（秒）
    )
    logger.info("数据库引擎创建成功")
except Exception as e:
    logger.error(f"数据库引擎创建失败: {str(e)}")
    raise

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 初始化数据库
def init_db():
    try:
        # 创建所有表
        # 注意: 生产环境应该使用迁移工具如Alembic
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"数据库表创建失败: {str(e)}")
        raise 