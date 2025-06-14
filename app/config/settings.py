import os
from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # 应用基本配置
    APP_NAME: str = "酒店业BI报告平台"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/hotel_bi")
    
    # Redis配置
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # AI服务配置
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_API_URL: str = os.getenv("AI_API_URL", "https://api.deepseek.com/v1/chat/completions")
    AI_MODEL: str = os.getenv("AI_MODEL", "deepseek-chat")
    AI_TIMEOUT: int = int(os.getenv("AI_TIMEOUT", "60"))
    
    # 文件存储配置
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "false").lower() == "true"
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "hotel-bi")
    
    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-jwt")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "your-encryption-key-must-be-32-bytes-long=")
    
    # CORS配置
    CORS_ORIGINS: List[str] = ["*"]
    
    # 上传文件配置
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = ["xlsx", "xls", "csv", "json"]
    
    # Celery配置
    CELERY_BROKER_URL: str = REDIS_URL
    CELERY_RESULT_BACKEND: str = REDIS_URL
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建设置实例
settings = Settings()

# 环境特定配置
if settings.ENVIRONMENT == "production":
    # 生产环境特定配置
    settings.DEBUG = False
    settings.CORS_ORIGINS = ["https://yourproductiondomain.com"]
elif settings.ENVIRONMENT == "testing":
    # 测试环境特定配置
    settings.DEBUG = True 