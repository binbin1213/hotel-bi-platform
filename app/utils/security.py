import os
import jwt
import time
import logging
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from fastapi import Request, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer

from ..config.settings import settings

logger = logging.getLogger(__name__)

# OAuth2 配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class SecurityUtils:
    """安全工具类，提供认证、授权和数据安全相关功能"""
    
    @staticmethod
    def generate_password_hash(password: str) -> str:
        """
        生成密码哈希
        
        Args:
            password: 明文密码
            
        Returns:
            str: 密码哈希
        """
        # 生成随机盐值
        salt = secrets.token_hex(16)
        
        # 使用SHA-256算法和盐值哈希密码
        password_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
        
        # 返回格式: hash$salt
        return f"{password_hash}${salt}"
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        验证密码
        
        Args:
            password: 待验证的明文密码
            password_hash: 存储的密码哈希
            
        Returns:
            bool: 密码是否正确
        """
        try:
            # 分离哈希和盐值
            stored_hash, salt = password_hash.split("$")
            
            # 使用相同的盐值哈希输入的密码
            computed_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
            
            # 比较哈希值
            return secrets.compare_digest(stored_hash, computed_hash)
        except Exception as e:
            logger.error(f"验证密码失败: {str(e)}")
            return False
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        创建访问令牌
        
        Args:
            data: 令牌数据
            expires_delta: 过期时间，如果为None则使用默认过期时间
            
        Returns:
            str: JWT令牌
        """
        to_encode = data.copy()
        
        # 设置过期时间
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        
        # 使用JWT算法和密钥创建令牌
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        解码令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            Dict[str, Any]: 令牌数据
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌已过期",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """
        清理输入字符串，防止XSS攻击
        
        Args:
            input_str: 输入字符串
            
        Returns:
            str: 清理后的字符串
        """
        if not isinstance(input_str, str):
            return str(input_str)
        
        # 替换可能导致XSS的字符
        replacements = {
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#x27;",
            "/": "&#x2F;",
            "&": "&amp;"
        }
        
        for char, replacement in replacements.items():
            input_str = input_str.replace(char, replacement)
        
        return input_str
    
    @staticmethod
    def validate_ip(ip: str) -> bool:
        """
        验证IP地址格式
        
        Args:
            ip: IP地址
            
        Returns:
            bool: IP地址是否有效
        """
        import re
        
        # IPv4地址正则表达式
        ipv4_pattern = r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$"
        match = re.match(ipv4_pattern, ip)
        
        if match:
            # 验证每个数字是否在0-255之间
            for i in range(1, 5):
                num = int(match.group(i))
                if num < 0 or num > 255:
                    return False
            return True
        
        # IPv6地址验证
        # 简化的IPv6验证，实际应用可能需要更复杂的验证
        ipv6_pattern = r"^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$"
        if re.match(ipv6_pattern, ip):
            return True
        
        return False
    
    @staticmethod
    def rate_limit(request: Request, limit: int = 100, window: int = 60) -> bool:
        """
        简单的速率限制实现
        
        Args:
            request: 请求对象
            limit: 在指定时间窗口内允许的最大请求数
            window: 时间窗口（秒）
            
        Returns:
            bool: 是否允许请求
        """
        client_ip = request.client.host
        
        # 在实际应用中，这里应该使用Redis等外部存储来跟踪请求
        # 这里使用简化的实现
        current_time = int(time.time())
        key = f"rate_limit:{client_ip}:{current_time // window}"
        
        # 这里应该从Redis等获取当前计数
        # 简化实现，假设总是允许请求
        return True
    
    @staticmethod
    def encrypt_data(data: str) -> str:
        """
        加密数据
        
        Args:
            data: 待加密的数据
            
        Returns:
            str: 加密后的数据
        """
        # 在实际应用中，应该使用AES等加密算法
        # 这里使用简化的实现
        from cryptography.fernet import Fernet
        
        key = settings.ENCRYPTION_KEY.encode()
        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode())
        
        return encrypted_data.decode()
    
    @staticmethod
    def decrypt_data(encrypted_data: str) -> str:
        """
        解密数据
        
        Args:
            encrypted_data: 加密的数据
            
        Returns:
            str: 解密后的数据
        """
        # 在实际应用中，应该使用AES等加密算法
        # 这里使用简化的实现
        from cryptography.fernet import Fernet
        
        key = settings.ENCRYPTION_KEY.encode()
        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data.encode())
        
        return decrypted_data.decode()

# 依赖函数，用于获取当前用户
async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    获取当前用户
    
    Args:
        token: JWT令牌
        
    Returns:
        Dict[str, Any]: 用户信息
    """
    try:
        payload = SecurityUtils.decode_token(token)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 在实际应用中，这里应该从数据库获取用户信息
        # 简化实现，直接返回令牌中的数据
        return payload
    except Exception as e:
        logger.error(f"获取当前用户失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

# 权限检查函数
def check_permissions(required_permissions: List[str]):
    """
    创建权限检查依赖
    
    Args:
        required_permissions: 所需权限列表
        
    Returns:
        函数: 权限检查依赖函数
    """
    async def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> bool:
        user_permissions = current_user.get("permissions", [])
        
        # 检查用户是否具有所有所需权限
        for permission in required_permissions:
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"权限不足，需要权限: {permission}"
                )
        
        return True
    
    return permission_checker