from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from typing import Callable

# 导入API路由
from app.api.v1.upload import router as upload_router
from app.api.v1.data import router as data_router
from app.api.v1.reports import router as reports_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.tasks import router as tasks_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="酒店业BI报告平台",
    description="智能化酒店业务数据分析与报告生成平台",
    version="0.1.0",
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求处理时间中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        logger.error(f"请求处理异常: {str(e)}")
        process_time = time.time() - start_time
        return JSONResponse(
            status_code=500,
            content={"detail": "内部服务器错误", "error": str(e)},
            headers={"X-Process-Time": str(process_time)},
        )

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "hotel-bi-platform"}

# 包含API路由
app.include_router(upload_router, prefix="/api/v1", tags=["上传"])
app.include_router(data_router, prefix="/api/v1", tags=["数据"])
app.include_router(reports_router, prefix="/api/v1", tags=["报告"])
app.include_router(dashboard_router, prefix="/api/v1", tags=["仪表盘"])
app.include_router(tasks_router, prefix="/api/v1", tags=["任务"])

# 应用启动事件
@app.on_event("startup")
async def startup_event():
    logger.info("应用启动")
    # 初始化数据库
    from app.config.database import init_db
    try:
        init_db()
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")

# 应用关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("应用关闭")
    # 可以在这里添加资源清理操作

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 