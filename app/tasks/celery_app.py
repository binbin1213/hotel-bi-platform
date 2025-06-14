from celery import Celery
import logging
from ..config.settings import settings

# 配置日志
logger = logging.getLogger(__name__)

# 创建Celery实例
celery_app = Celery(
    "hotel_bi",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# 配置Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1小时
    worker_max_tasks_per_child=200,
    worker_prefetch_multiplier=4,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# 自动发现任务
celery_app.autodiscover_tasks(["app.tasks"])

@celery_app.task(bind=True)
def debug_task(self):
    """调试任务"""
    logger.info(f"Request: {self.request!r}")
    return {"status": "ok"}