from app.api.v1.upload import router as upload_router
from app.api.v1.data import router as data_router
from app.api.v1.reports import router as reports_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.tasks import router as tasks_router

# 导出所有路由
__all__ = [
    "upload_router",
    "data_router",
    "reports_router",
    "dashboard_router",
    "tasks_router"
] 