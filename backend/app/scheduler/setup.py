from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.scheduler.jobs.daily_oil_fetch_job import run_daily_oil_fetch
from app.scheduler.jobs.weekly_oil_revision_job import run_weekly_oil_revision

DAILY_FETCH_HOUR = 0
DAILY_FETCH_MINUTE = 0

WEEKLY_REVISION_DAY = "mon"
WEEKLY_REVISION_HOUR = 1
WEEKLY_REVISION_MINUTE = 0

SCHEDULER_TIMEZONE = "UTC"

DAILY_OIL_FETCH_JOB_ID = "daily_oil_fetch"
WEEKLY_OIL_REVISION_JOB_ID = "weekly_oil_revision"

_scheduler = AsyncIOScheduler(timezone=SCHEDULER_TIMEZONE)


def start_scheduler() -> None:
    _scheduler.add_job(
        run_daily_oil_fetch,
        trigger=CronTrigger(hour=DAILY_FETCH_HOUR, minute=DAILY_FETCH_MINUTE),
        id=DAILY_OIL_FETCH_JOB_ID,
        replace_existing=True,
    )
    _scheduler.add_job(
        run_weekly_oil_revision,
        trigger=CronTrigger(
            day_of_week=WEEKLY_REVISION_DAY,
            hour=WEEKLY_REVISION_HOUR,
            minute=WEEKLY_REVISION_MINUTE,
        ),
        id=WEEKLY_OIL_REVISION_JOB_ID,
        replace_existing=True,
    )
    _scheduler.start()


def shutdown_scheduler() -> None:
    _scheduler.shutdown()
