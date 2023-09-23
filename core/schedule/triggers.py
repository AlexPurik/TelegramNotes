import os
from dotenv import load_dotenv

from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

import pytz
from datetime import datetime, timedelta


load_dotenv("config.env")

tz = pytz.timezone(os.getenv("TZ"))


class OffsetTrigger:
    def __new__(self, days=0, hours=0, minutes=0, seconds=0):
        offset = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        now = datetime.now(tz)
        run_date = now + offset
        return DateTrigger(run_date=run_date, timezone=tz)
