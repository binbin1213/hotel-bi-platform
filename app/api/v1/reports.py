from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
import logging
from typing import List, Optional, Dict, Any
from app.config.database import get_db
from app.schemas import ReportGenerationRequest, ReportResponse, ErrorResponse, PaginatedResponse, ReportCreate
from typing import List
from app.services.report_service import ReportService
from datetime import datetime
import json
from app.utils.file_handler import generate_download_url
from app.models import Report
# 删除不存在的导入
from app.tasks.report_generation import generate_pdf_report, generate_ppt_report
from app.tasks.ai_analysis import generate_ai_analysis
from app.services.ai_service import AIService
from app.api.middleware.auth import get_current_user
import app.models as models
import app.tasks as tasks

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter()

@router.post(
    "/reports/generate",
    response_model=ReportResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="生成报告",
    description="根据请求生成分析报告"
)
async def generate_report(
    request: ReportGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """生成报告"""
    try:
        report_service = ReportService(db)
        report = report_service.create_report(request)
        
        # 在后台任务中生成报告
        task_id = report_service.generate_report_async(
            background_tasks,
            report.id,
            request.include_ai_analysis,
            request.output_formats
        )
        
        # 更新报告状态
        report.status = "processing"
        db.commit()
        
        return ReportResponse(**report.to_dict())
        
    except Exception as e:
        logger.error(f"报告生成请求失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"报告生成请求失败: {str(e)}")

@router.get(
    "/reports",
    response_model=PaginatedResponse,
    responses={500: {"model": ErrorResponse}},
    summary="获取报告列表",
    description="分页获取报告列表"
)
async def get_reports(
    page: int = 1,
    size: int = 10,
    report_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取报告列表"""
    try:
        report_service = ReportService(db)
        reports, total = report_service.get_reports(
            page=page,
            size=size,
            report_type=report_type,
            status=status
        )
        
        # 计算总页数
        pages = (total + size - 1) // size
        
        # 转换为响应模型
        items = [ReportResponse(**report.to_dict()) for report in reports]
        
        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"获取报告列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取报告列表失败: {str(e)}")

@router.get(
    "/reports/{report_id}",
    response_model=ReportResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="获取报告详情",
    description="根据ID获取报告详情"
)
async def get_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """获取报告详情"""
    try:
        report_service = ReportService(db)
        report = report_service.get_report_by_id(report_id)
        
        if not report:
            raise HTTPException(status_code=404, detail=f"未找到报告ID: {report_id}")
        
        return ReportResponse(**report.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取报告详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取报告详情失败: {str(e)}")

@router.delete(
    "/reports/{report_id}",
    response_model=dict,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="删除报告",
    description="根据ID删除报告"
)
async def delete_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """删除报告"""
    try:
        report_service = ReportService(db)
        success = report_service.delete_report(report_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"未找到报告ID: {report_id}")
        
        return {"success": True, "message": "报告删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除报告失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除报告失败: {str(e)}")

@router.post("/{report_id}/generate-pdf", response_model=dict)
async def create_pdf_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    生成PDF格式的报告
    """
    # 检查报告是否存在
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    # 创建任务
    task = models.TaskStatus(
        task_type="generate_pdf_report",
        status="pending",
        created_at=datetime.utcnow()
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # 启动异步任务
    celery_task = tasks.generate_pdf_report.delay(report_id)
    
    # 更新任务ID
    task.task_id = celery_task.id
    db.commit()
    
    return {
        "task_id": task.task_id,
        "status": task.status,
        "message": "PDF报告生成任务已创建"
    }

@router.post("/{report_id}/generate-ppt", response_model=dict)
async def create_ppt_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    生成PPT格式的报告
    """
    # 检查报告是否存在
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    # 创建任务
    task = models.TaskStatus(
        task_type="generate_ppt_report",
        status="pending",
        created_at=datetime.utcnow()
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # 启动异步任务
    celery_task = tasks.generate_ppt_report.delay(report_id)
    
    # 更新任务ID
    task.task_id = celery_task.id
    db.commit()
    
    return {
        "task_id": task.task_id,
        "status": task.status,
        "message": "PPT报告生成任务已创建"
    }

@router.get("/{report_id}/download/{file_type}", response_model=dict)
async def get_report_download_url(
    report_id: int,
    file_type: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取报告文件的下载链接
    
    file_type: pdf或ppt
    """
    # 检查报告是否存在
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    # 检查文件类型是否有效
    if file_type not in ["pdf", "ppt"]:
        raise HTTPException(status_code=400, detail="无效的文件类型，必须是pdf或ppt")
    
    # 检查报告文件是否存在
    if not report.file_paths:
        raise HTTPException(status_code=404, detail="报告文件不存在")
    
    file_paths = json.loads(report.file_paths)
    if file_type not in file_paths:
        raise HTTPException(status_code=404, detail=f"报告{file_type}文件不存在")
    
    # 生成下载URL
    download_url = generate_download_url(file_paths[file_type])
    
    return {
        "file_url": download_url,
        "file_type": file_type,
        "expires_in": 3600  # URL有效期1小时
    }

@router.post("/", response_model=ReportResponse)
def create_report(
    report_data: ReportCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """创建报告"""
    # 创建报告记录
    new_report = Report(
        title=report_data.title,
        description=report_data.description,
        report_type=report_data.report_type,
        content_data=report_data.content_data,
        status="pending",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    # 启动异步任务生成报告
    if report_data.report_type in ["pdf", "ppt"]:
        background_tasks.add_task(generate_report.delay, new_report.id)
    
    # 如果需要AI分析，启动AI分析任务
    if report_data.content_data.get("need_ai_analysis", False):
        background_tasks.add_task(generate_ai_analysis.delay, new_report.id)
    
    return new_report

@router.get("/", response_model=List[ReportResponse])
def list_reports(
    skip: int = 0,
    limit: int = 10,
    report_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取报告列表"""
    query = db.query(Report)
    
    if report_type:
        query = query.filter(Report.report_type == report_type)
    
    if status:
        query = query.filter(Report.status == status)
    
    total = query.count()
    reports = query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": reports
    }

@router.post("/{report_id}/regenerate")
def regenerate_report(report_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """重新生成报告"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    report.status = "pending"
    report.updated_at = datetime.utcnow()
    db.commit()
    
    # 启动异步任务重新生成报告
    if report.report_type in ["pdf", "ppt"]:
        background_tasks.add_task(generate_report.delay, report.id)
    
    return {"message": "报告重新生成任务已启动"}

@router.post("/{report_id}/analyze")
def analyze_report(report_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """对报告进行AI分析"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    # 启动AI分析任务
    background_tasks.add_task(generate_ai_analysis.delay, report.id)
    
    return {"message": "AI分析任务已启动"}

@router.get("/{report_id}/analysis", response_model=Dict[str, Any])
def get_report_analysis(
    report_id: int,
    analysis_type: str = Query("comprehensive", description="分析类型: comprehensive, revenue, operational, competitive, forecast"),
    db: Session = Depends(get_db)
):
    """获取报告的AI分析结果"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    # 如果报告已有AI分析结果
    if report.ai_insights:
        return report.ai_insights
    
    # 如果没有分析结果，但有内容数据，尝试即时生成
    if report.content_data:
        try:
            ai_service = AIService(db)
            hotel_ids = report.content_data.get("hotel_ids", [])
            date_range = report.content_data.get("date_range", {})
            
            analysis_result = ai_service.generate_analysis(
                hotel_ids=hotel_ids,
                date_range=date_range,
                analysis_type=analysis_type
            )
            
            # 更新报告的AI分析结果
            report.ai_insights = analysis_result
            report.updated_at = datetime.utcnow()
            db.commit()
            
            return analysis_result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"生成AI分析失败: {str(e)}")
    
    raise HTTPException(status_code=404, detail="报告没有AI分析结果或内容数据")
