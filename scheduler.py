from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


def build_scheduler(job_func) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        job_func,
        CronTrigger(hour=21, minute=0, timezone="Europe/Madrid"),
    )
    return scheduler
