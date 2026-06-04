import os
import json
from datetime import datetime, timezone


SCHEDULE_FILE = "channel_schedule.json"
CHANNEL_START_DATE = "2026-06-04"


class ScheduleManager:
    def __init__(self):
        self.start_date = datetime.strptime(CHANNEL_START_DATE, "%Y-%m-%d").replace(tzinfo=timezone.utc)

    def get_week_number(self):
        now = datetime.now(timezone.utc)
        days_passed = (now - self.start_date).days
        week = (days_passed // 7) + 1
        return week

    def should_publish_today(self):
        week = self.get_week_number()
        today = datetime.now(timezone.utc).weekday()
        print("Week number: " + str(week))
        print("Today weekday: " + str(today) + " (0=Mon, 2=Wed, 4=Fri)")

        if week == 1:
            allowed_days = [2]
        elif week == 2:
            allowed_days = [2, 4]
        else:
            allowed_days = [2, 4]

        should = today in allowed_days
        print("Should publish today: " + str(should))
        return should
