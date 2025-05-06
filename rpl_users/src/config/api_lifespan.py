from datetime import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import contextmanager

from fastapi import FastAPI
from rpl_users.src.deps.schedule import cleanup_validation_tokens_job


@contextmanager
def token_cleaner_lifespan(app: FastAPI):
    scheduler = BackgroundScheduler(timezone=timezone.utc)
    scheduler.configure(
        job_defaults={
            "coalesce": True,
            "max_instances": 1,
        }
    )
    scheduler.add_job(
        func=cleanup_validation_tokens_job,
        trigger=CronTrigger(
            day_of_week="sat",
            hour=0,
            minute=0,
            second=0,
        ),
        id="weekly_data_cleanup",
        replace_existing=True,
    )
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown()
