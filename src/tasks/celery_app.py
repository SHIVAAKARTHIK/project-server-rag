from celery import Celery

from src.config import settings


celery_app = Celery(
    "six_figure_rag",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "src.tasks.document_tasks",
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    worker_prefetch_multiplier=1,  # For long-running tasks
    
    # Beat schedule for periodic tasks (if needed)
    beat_schedule={
        # Add scheduled tasks here if needed
    }
)
