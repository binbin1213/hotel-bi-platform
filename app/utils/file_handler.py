import os
import logging
import shutil
from typing import Optional, List, Dict, Any, Union
from fastapi import UploadFile
from minio import Minio
from minio.error import S3Error
from ..config.settings import settings

# 配置日志
logger = logging.getLogger(__name__)

# 本地上传目录
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# MinIO客户端
try:
    minio_client = Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE
    )
    
    # 确保存储桶存在
    if not minio_client.bucket_exists(settings.MINIO_BUCKET_NAME):
        minio_client.make_bucket(settings.MINIO_BUCKET_NAME)
        logger.info(f"创建存储桶: {settings.MINIO_BUCKET_NAME}")
    
except Exception as e:
    logger.error(f"MinIO客户端初始化失败: {str(e)}")
    minio_client = None

async def save_upload_file(upload_file: UploadFile, file_id: str) -> str:
    """保存上传文件，返回保存路径"""
    try:
        # 确保文件名有效
        filename = upload_file.filename
        if not filename:
            filename = f"{file_id}"
        
        # 文件扩展名
        file_extension = filename.split(".")[-1] if "." in filename else ""
        
        # 构建保存路径
        save_filename = f"{file_id}.{file_extension}" if file_extension else file_id
        save_path = os.path.join(UPLOAD_DIR, save_filename)
        
        # 保存文件到本地
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        # 如果MinIO可用，上传到MinIO
        if minio_client:
            try:
                minio_client.fput_object(
                    settings.MINIO_BUCKET_NAME,
                    f"uploads/{save_filename}",
                    save_path
                )
                logger.info(f"文件上传到MinIO: {save_filename}")
                
                # 可以选择删除本地文件
                # os.remove(save_path)
                # return f"minio://{settings.MINIO_BUCKET_NAME}/uploads/{save_filename}"
            except S3Error as e:
                logger.error(f"MinIO上传失败: {str(e)}")
        
        return save_path
        
    except Exception as e:
        logger.error(f"保存上传文件失败: {str(e)}")
        raise

async def get_file_url(file_path: str, expires: int = 3600) -> str:
    """获取文件的访问URL"""
    try:
        # 检查是否为MinIO路径
        if file_path.startswith("minio://"):
            if not minio_client:
                raise Exception("MinIO客户端未初始化")
            
            # 解析MinIO路径
            parts = file_path[8:].split("/", 1)
            bucket_name = parts[0]
            object_name = parts[1]
            
            # 生成预签名URL
            url = minio_client.presigned_get_object(
                bucket_name,
                object_name,
                expires=expires
            )
            return url
        else:
            # 本地文件路径，返回相对路径
            if os.path.exists(file_path):
                return f"/static/uploads/{os.path.basename(file_path)}"
            else:
                raise Exception(f"文件不存在: {file_path}")
    
    except Exception as e:
        logger.error(f"获取文件URL失败: {str(e)}")
        raise

def delete_file(file_path: str) -> bool:
    """删除文件"""
    try:
        # 检查是否为MinIO路径
        if file_path.startswith("minio://"):
            if not minio_client:
                raise Exception("MinIO客户端未初始化")
            
            # 解析MinIO路径
            parts = file_path[8:].split("/", 1)
            bucket_name = parts[0]
            object_name = parts[1]
            
            # 删除对象
            minio_client.remove_object(bucket_name, object_name)
            logger.info(f"MinIO文件已删除: {file_path}")
            return True
        else:
            # 删除本地文件
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"本地文件已删除: {file_path}")
                return True
            else:
                logger.warning(f"要删除的文件不存在: {file_path}")
                return False
    
    except Exception as e:
        logger.error(f"删除文件失败: {str(e)}")
        return False

def upload_file_to_minio(file_path: str, file_key: str) -> bool:
    """
    上传文件到MinIO存储
    
    Args:
        file_path: 本地文件路径
        file_key: MinIO中的文件键
        
    Returns:
        bool: 上传是否成功
    """
    try:
        # 创建MinIO客户端
        client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        
        # 确保存储桶存在
        if not client.bucket_exists(settings.MINIO_BUCKET_NAME):
            client.make_bucket(settings.MINIO_BUCKET_NAME)
        
        # 上传文件
        client.fput_object(
            settings.MINIO_BUCKET_NAME,
            file_key,
            file_path
        )
        
        return True
    except Exception as e:
        logger.error(f"上传文件到MinIO失败: {str(e)}")
        return False

def generate_download_url(file_key: str, expires=3600) -> str:
    """
    生成MinIO文件的临时下载URL
    
    Args:
        file_key: MinIO中的文件键
        expires: URL过期时间（秒），默认1小时
        
    Returns:
        str: 临时下载URL
    """
    try:
        # 创建MinIO客户端
        client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        
        # 生成临时URL
        url = client.presigned_get_object(
            settings.MINIO_BUCKET_NAME,
            file_key,
            expires=expires
        )
        
        return url
    except Exception as e:
        logger.error(f"生成下载URL失败: {str(e)}")
        return "" 