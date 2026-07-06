"""Shared helpers for both the SQL and MongoDB APIs.

Derives the same calendar features used by Task 2's load_data.py scripts, so
records created through this API line up with the bulk-loaded dataset.
"""
from datetime import datetime


def get_season(month: int) -> str:
    if month in (12, 1, 2):
        return "Winter"
    if month in (3, 4, 5):
        return "Spring"
    if month in (6, 7, 8):
        return "Summer"
    return "Autumn"


def derive_time_features(dt: datetime) -> dict:
    return {
        "year": dt.year,
        "month": dt.month,
        "day": dt.day,
        "hour": dt.hour,
        "day_of_week": dt.weekday(),
        "is_weekend": dt.weekday() >= 5,
        "season": get_season(dt.month),
    }
