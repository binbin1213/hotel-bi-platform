from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uuid
import os
import logging
from typing import Optional
from app.config.database import get_db
from app.config.settings import settings
from app.schemas import FileUploadRequest, FileUploadResponse, ErrorResponse
from app.services.data_service import DataService
from app.utils.file_handler import save_upload_file

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter()

@router.post(
    "/upload/file",
    response_model=FileUploadResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="上传数据文件",
    description="上传Excel、CSV等数据文件进行处理"
)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    file_type: str = Form("excel"),
    overwrite: bool = Form(False),
    db: Session = Depends(get_db)
):
    """上传数据文件"""
    try:
        # 验证文件类型
        filename = file.filename
        if not filename:
            raise HTTPException(status_code=400, detail="未提供文件名")
        
        file_extension = filename.split(".")[-1].lower()
        allowed_extensions = settings.ALLOWED_EXTENSIONS
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文件类型，允许的类型: {', '.join(allowed_extensions)}"
            )
        
        # 验证文件大小
        file_size = 0
        chunk_size = 1024 * 1024  # 1MB
        chunk = await file.read(chunk_size)
        while chunk:
            file_size += len(chunk)
            if file_size > settings.MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"文件太大，最大允许大小: {settings.MAX_UPLOAD_SIZE / (1024 * 1024)}MB"
                )
            chunk = await file.read(chunk_size)
        
        # 重置文件指针
        await file.seek(0)
        
        # 生成唯一文件ID
        file_id = str(uuid.uuid4())
        
        # 保存文件
        save_path = await save_upload_file(file, file_id)
        
        # 创建后台任务处理文件
        data_service = DataService(db)
        task_id = data_service.process_file_async(
            background_tasks,
            save_path,
            file_type,
            overwrite
        )
        
        return FileUploadResponse(
            success=True,
            message="文件上传成功，正在处理",
            file_id=file_id,
            file_name=filename,
            task_id=task_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@router.get(
    "/upload/status/{task_id}",
    response_model=FileUploadResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="获取上传任务状态",
    description="根据任务ID获取上传处理任务的状态"
)
async def get_upload_status(
    task_id: str,
    db: Session = Depends(get_db)
):
    """获取上传任务状态"""
    try:
        data_service = DataService(db)
        task_status = data_service.get_task_status(task_id)
        
        if not task_status:
            raise HTTPException(status_code=404, detail=f"未找到任务ID: {task_id}")
        
        return FileUploadResponse(
            success=True,
            message=f"任务状态: {task_status.status}",
            file_id=task_status.result_data.get("file_id") if task_status.result_data else "",
            file_name=task_status.result_data.get("file_name") if task_status.result_data else "",
            task_id=task_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}") 