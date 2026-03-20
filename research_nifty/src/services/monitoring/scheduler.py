from __future__ import annotations

from apscheduler.schedulers.blocking import BlockingScheduler

from config import get_settings


def run_daily(job, hour: int = 18, minute: int = 0) -> None:
    settings = get_settings()
    scheduler = BlockingScheduler(timezone=settings.scheduler_timezone)
    scheduler.add_job(job, "cron", hour=hour, minute=minute)
    scheduler.start()
