"""Preprocessing pipeline for the PJM hourly energy data.

Task 4's forecast script imports these functions so a new record gets
prepared exactly the same way the training data was.
"""
from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def load_series(region="PJME", raw_dir=RAW_DIR):
    """Read one region's file and return a time-indexed MW series."""
    path = Path(raw_dir) / f"{region}_hourly.csv"
    df = pd.read_csv(path, parse_dates=["Datetime"])
    df = df.set_index("Datetime").sort_index()
    # the raw files repeat a few hours around the autumn DST switch
    df = df[~df.index.duplicated(keep="first")]
    return df


def make_hourly(df):
    """Put the series on a gap-free hourly grid and fill the holes."""
    full = pd.date_range(df.index.min(), df.index.max(), freq="h")
    df = df.reindex(full)
    df = df.interpolate(method="time", limit_direction="both")
    df.index.name = "Datetime"
    return df


def add_time_features(df):
    idx = df.index
    df["hour"] = idx.hour
    df["dayofweek"] = idx.dayofweek
    df["month"] = idx.month
    df["year"] = idx.year
    df["is_weekend"] = (idx.dayofweek >= 5).astype(int)
    return df


def add_lag_features(df, target, lags=(1, 24, 168)):
    # 1h = last hour, 24h = same hour yesterday, 168h = same hour last week
    for lag in lags:
        df[f"lag_{lag}h"] = df[target].shift(lag)
    return df


def add_rolling_features(df, target, windows=(24, 168)):
    for w in windows:
        # shift(1) keeps the window in the past so we don't leak the current value
        past = df[target].shift(1)
        df[f"roll_mean_{w}h"] = past.rolling(w).mean()
        df[f"roll_std_{w}h"] = past.rolling(w).std()
    return df


def build_features(region="PJME", raw_dir=RAW_DIR, dropna=True):
    """Load a region and return it with calendar, lag and rolling features."""
    target = f"{region}_MW"
    df = load_series(region, raw_dir)
    df = make_hourly(df)
    df = add_time_features(df)
    df = add_lag_features(df, target)
    df = add_rolling_features(df, target)
    if dropna:
        df = df.dropna()
    return df


def time_split(df, test_size=0.2):
    """Chronological split — never shuffle a time series."""
    cut = int(len(df) * (1 - test_size))
    return df.iloc[:cut], df.iloc[cut:]
