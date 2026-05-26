from datetime import date, timedelta

MONDAY_WEEKDAY_INDEX = 0


def current_week_monday() -> date:
    today = date.today()
    return today - timedelta(days=today.weekday() - MONDAY_WEEKDAY_INDEX)
