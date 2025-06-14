import redis
import logging
import json
from typing import Any, Optional
from .settings import settings

# 配置日志
logger = logging.getLogger(__name__)

# 创建Redis连接池
try:
    redis_client = redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,  # 自动解码响应
        socket_timeout=5,       # 套接字超时
        socket_connect_timeout=5, # 连接超时
    )
    logger.info("Redis连接池创建成功")
except Exception as e:
    logger.error(f"Redis连接池创建失败: {str(e)}")
    redis_client = None

def get_redis_client():
    """
    获取Redis客户端实例
    
    Returns:
        Redis客户端实例
    """
    if not redis_client:
        logger.warning("Redis客户端未初始化，尝试重新连接")
        try:
            return redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
            )
        except Exception as e:
            logger.error(f"Redis重新连接失败: {str(e)}")
            return None
    return redis_client

class CacheManager:
    """缓存管理器"""
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """获取缓存值"""
        if not redis_client:
            return None
        
        try:
            value = redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"获取缓存失败: {str(e)}")
            return None
    
    @staticmethod
    def set(key: str, value: Any, expire: int = 3600) -> bool:
        """设置缓存值"""
        if not redis_client:
            return False
        
        try:
            serialized_value = json.dumps(value)
            redis_client.set(key, serialized_value, ex=expire)
            return True
        except Exception as e:
            logger.error(f"设置缓存失败: {str(e)}")
            return False
    
    @staticmethod
    def delete(key: str) -> bool:
        """删除缓存值"""
        if not redis_client:
            return False
        
        try:
            redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"删除缓存失败: {str(e)}")
            return False
    
    @staticmethod
    def clear_all() -> bool:
        """清空所有缓存"""
        if not redis_client:
            return False
        
        try:
            redis_client.flushdb()
            return True
        except Exception as e:
            logger.error(f"清空缓存失败: {str(e)}")
            return False

# 创建缓存管理器实例
cache = CacheManager() 