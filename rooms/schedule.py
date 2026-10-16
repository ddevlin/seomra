from datetime import date, timedelta


def week_start(day):
    """Monday of the week containing ``day``."""
    return day - timedelta(days=day.weekday())


def week_days(start):
    return [start + timedelta(days=i) for i in range(7)]


def parse_date_param(value, default):
    """Parse an ISO date from a query string; any problem returns ``default``."""
    if not value:
        return default
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return default
