import os
from dotenv import load_dotenv

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.jobstores.base import JobLookupError
import pytz


load_dotenv("config.env")

tz = pytz.timezone(os.getenv("TZ"))


scheduler = AsyncIOScheduler(timezone=tz)
jobstore = SQLAlchemyJobStore(
    url=f'sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), "jobs.db")}'
)
scheduler.add_jobstore(jobstore, "default")


def delete_job(job_id: str):
    scheduler.remove_job(job_id=job_id, jobstore="default")


def start_scheduler():
    scheduler.start()
