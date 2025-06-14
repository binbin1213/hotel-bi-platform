from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.settings import settings

# 使用OAuth2PasswordBearer作为令牌获取方式
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

# JWT相关配置
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌
    
    Args:
        data: 要编码到令牌中的数据
        expires_delta: 可选的过期时间增量
        
    Returns:
        JWT令牌字符串
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    获取当前用户
    
    Args:
        token: JWT令牌
        db: 数据库会话
        
    Returns:
        当前用户信息
        
    Raises:
        HTTPException: 如果令牌无效或用户不存在
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的身份验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码JWT令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # 这里应该从数据库中获取用户信息
    # 由于项目可能还没有完整的用户模型，我们先返回一个简单的用户对象
    # 在实际项目中，应该查询数据库获取完整的用户信息
    
    # 模拟从数据库获取用户
    # user = db.query(User).filter(User.id == user_id).first()
    # if user is None:
    #     raise credentials_exception
    
    # 简化版本，直接返回用户ID和角色
    user = {
        "id": user_id,
        "username": payload.get("username", "unknown"),
        "role": payload.get("role", "user"),
        "is_active": True
    }
    
    return user


async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    获取当前活跃用户
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        当前活跃用户
        
    Raises:
        HTTPException: 如果用户不活跃
    """
    if not current_user.get("is_active", False):
        raise HTTPException(status_code=400, detail="用户不活跃")
        
    return current_user 