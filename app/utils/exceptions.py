from fastapi import HTTPException
from typing import Dict, Any, Optional

class AppException(Exception):
    """应用自定义异常基类"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "success": False,
            "error": self.message,
        }
        if self.error_code:
            result["error_code"] = self.error_code
        if self.details:
            result["details"] = self.details
        return result
    
    def to_http_exception(self) -> HTTPException:
        """转换为HTTP异常"""
        return HTTPException(
            status_code=self.status_code,
            detail=self.to_dict()
        )

class ValidationError(AppException):
    """数据验证错误"""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details
        )

class NotFoundError(AppException):
    """资源未找到错误"""
    
    def __init__(
        self,
        message: str,
        resource_type: str,
        resource_id: Any
    ):
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details={
                "resource_type": resource_type,
                "resource_id": resource_id
            }
        )

class DatabaseError(AppException):
    """数据库错误"""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR",
            details=details
        )

class FileError(AppException):
    """文件处理错误"""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=500,
            error_code="FILE_ERROR",
            details=details
        )

class AIServiceError(AppException):
    """AI服务错误"""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=500,
            error_code="AI_SERVICE_ERROR",
            details=details
        ) 