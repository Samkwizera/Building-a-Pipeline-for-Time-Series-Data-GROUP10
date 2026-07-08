"""
Task 4 -- Prediction / Forecast Script
Group 10 -- Hourly Energy Consumption (PJM), https://www.kaggle.com/datasets/robikscube/hourly-energy-consumption

What this does, in order (matching the assignment brief exactly):
  1. FETCH   a window of recent readings from Task 3's real API
             (GET /api/{sql|mongo}/readings/latest and /range).
  2. PREPROCESS the fetched readings with the *same* functions Samuel used in
     src/preprocessing.py for Task 1, so serving-time features can never drift
     from training-time features.
  3. LOAD    the trained model saved at models/aep_forecaster.joblib.
  4. PREDICT the next hour's AEP_MW and print/report it.

-----------------------------------------------------------------------------
NOTE ON MODEL CHOICE:
Task 2/3's database only has AEP_hourly.csv loaded (see
`Database design/sql/load_data.py`), and the API returns whatever's in the DB
with no region filter. Samuel's original models/pjme_forecaster.joblib was
trained on PJME, a different series -- so it can't be used against this API.
We retrained the *same* tuned HistGradientBoostingRegressor, with the exact
same src/preprocessing.py pipeline, on AEP instead (see aep_forecaster.joblib).
Mention this in the group report: "Task 4 retrained Task 1's model
architecture on AEP to match the region actually loaded into the database."
-----------------------------------------------------------------------------

Usage:
    # With Task 3's real API running (see README step 2-3):
    python forecast.py --api-base http://127.0.0.1:8000 --backend sql
    python forecast.py --api-base http://127.0.0.1:8000 --backend mongo

    # Without the API running, to sanity-check the rest of the pipeline:
    python forecast.py --mock

Task 3's real API contract (from task3/sql_api/routes.py and
task3/mongo_api/routes.py):

    GET {api_base}/api/{backend}/readings/latest
        -> {"id": 1, "region_name": "AEP", "datetime": "2018-01-02T03:00:00",
            "consumption_mw": 13780.0, "year": 2018, "month": 1, ...}

    GET {api_base}/api/{backend}/readings/range?start=...&end=...
        -> [ ...same shape as above... ]

    (No region filter param exists -- the DB only has AEP loaded, so every
    record returned already is AEP.)
"""
from __future__ import annotations

import argparse
import sys
from datetime import timedelta
from pathlib import Path

import pandas as pd
import joblib
import requests

sys.path.append(str(Path(__file__).resolve().parent))
from src.preprocessing import (
    make_hourly,
    add_time_features,
    add_lag_features,
    add_rolling_features,
)

MODEL_PATH = Path(__file__).resolve().parent / "models" / "aep_forecaster.joblib"
MOCK_CSV = Path(__file__).resolve().parent / "data" / "raw" / "AEP_hourly.csv"

# Need enough history to fill the longest lag/rolling window with no NaNs.
# lag_168h + a 168h rolling mean shifted by 1 => 169 hours minimum; pad for safety.
MIN_HISTORY_HOURS = 169
DEFAULT_HISTORY_HOURS = 24 * 14  # two weeks, comfortable margin


# --------------------------------------------------------------------------- #
# 1. FETCH
# --------------------------------------------------------------------------- #
def fetch_latest_timestamp(api_base: str, backend: str) -> pd.Timestamp:
    """GET the single latest record so we know the end of the window to pull."""
    url = f"{api_base}/api/{backend}/readings/latest"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    record = resp.json()
    return pd.to_datetime(record["datetime"])


def fetch_range(
    api_base: str, backend: str, start: pd.Timestamp, end: pd.Timestamp
) -> list[dict]:
    """GET all records between start and end (inclusive)."""
    url = f"{api_base}/api/{backend}/readings/range"
    params = {"start": start.isoformat(), "end": end.isoformat()}
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def fetch_recent_readings(api_base: str, backend: str, region: str, hours: int) -> pd.DataFrame:
    """Fetch the last `hours` of readings from the API as a datetime-indexed frame."""
    latest_ts = fetch_latest_timestamp(api_base, backend)
    start_ts = latest_ts - timedelta(hours=hours)
    records = fetch_range(api_base, backend, start_ts, latest_ts)
    if not records:
        raise RuntimeError(f"API returned no records between {start_ts} and {latest_ts}")
    return _records_to_frame(records, region)


def load_mock_readings(region: str, hours: int) -> pd.DataFrame:
    """Local stand-in for the API: read the tail of the raw CSV (Task 1's data source)."""
    csv_path = MOCK_CSV.parent / f"{region}_hourly.csv"
    df = pd.read_csv(csv_path, parse_dates=["Datetime"])
    df = df.set_index("Datetime").sort_index()
    df = df[~df.index.duplicated(keep="first")]
    df = df.tail(hours + 1)
    df.index.name = "datetime"
    return df.rename(columns={f"{region}_MW": f"{region}_MW"})  # no-op, keeps column name explicit


def _records_to_frame(records: list[dict], region: str) -> pd.DataFrame:
    """Turn a list of API JSON records into the 1-column frame preprocessing.py expects."""
    target_col = f"{region}_MW"
    df = pd.DataFrame(records)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.set_index("datetime").sort_index()
    df = df.rename(columns={"consumption_mw": target_col})
    return df[[target_col]]


# --------------------------------------------------------------------------- #
# 2. PREPROCESS (reuses Samuel's Task 1 functions -- do not reimplement here)
# --------------------------------------------------------------------------- #
def build_latest_feature_row(raw: pd.DataFrame, region: str) -> pd.DataFrame:
    target = f"{region}_MW"
    df = make_hourly(raw)
    df = add_time_features(df)
    df = add_lag_features(df, target)
    df = add_rolling_features(df, target)
    df = df.dropna()
    if df.empty:
        raise RuntimeError(
            "Not enough history to build lag/rolling features -- "
            f"need at least {MIN_HISTORY_HOURS} consecutive hourly readings."
        )
    return df.iloc[[-1]]  # the most recent fully-featured row


# --------------------------------------------------------------------------- #
# 3 & 4. LOAD MODEL + PREDICT
# --------------------------------------------------------------------------- #
def load_model(model_path: Path = MODEL_PATH):
    bundle = joblib.load(model_path)
    return bundle["model"], bundle["features"], bundle["target"]


def forecast_next_hour(feature_row: pd.DataFrame, model, features: list[str]) -> tuple[pd.Timestamp, float]:
    X = feature_row[features]
    pred = float(model.predict(X)[0])
    next_hour = feature_row.index[-1] + timedelta(hours=1)
    return next_hour, pred


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main():
    parser = argparse.ArgumentParser(description="Task 4: forecast the next hour of PJME demand.")
    parser.add_argument("--api-base", default="http://127.0.0.1:8000", help="Task 3 API base URL")
    parser.add_argument("--backend", choices=["sql", "mongo"], default="sql", help="which Task 3 backend to hit")
    parser.add_argument("--region", default="AEP", help="region code (must match the trained model's target)")
    parser.add_argument("--hours", type=int, default=DEFAULT_HISTORY_HOURS, help="hours of history to pull")
    parser.add_argument("--mock", action="store_true", help="skip the API, read the local CSV instead")
    args = parser.parse_args()

    if args.hours < MIN_HISTORY_HOURS:
        parser.error(f"--hours must be >= {MIN_HISTORY_HOURS} to fill every lag/rolling window")

    model, features, target = load_model()
    print(f"Loaded model for target '{target}' expecting features: {features}")

    if args.mock:
        print(f"[mock mode] reading last {args.hours}h of {args.region}_hourly.csv (no API call)")
        raw = load_mock_readings(args.region, args.hours)
    else:
        print(f"Fetching last {args.hours}h of '{args.region}' readings from {args.api_base} ({args.backend})")
        try:
            raw = fetch_recent_readings(args.api_base, args.backend, args.region, args.hours)
        except requests.exceptions.ConnectionError:
            sys.exit(
                f"Could not reach {args.api_base} -- is Task 3's API running?\n"
                f"To test the rest of the pipeline without it, rerun with --mock."
            )
        except requests.exceptions.HTTPError as e:
            sys.exit(f"API returned an error: {e}")
        except (KeyError, ValueError) as e:
            sys.exit(
                f"Got a response but couldn't parse it ({e}). "
                f"Check that the field names match what this script expects "
                f"(see the EDIT_HERE comments near fetch_latest_timestamp/_records_to_frame)."
            )

    feature_row = build_latest_feature_row(raw, args.region)
    next_hour, prediction = forecast_next_hour(feature_row, model, features)

    last_known_time = feature_row.index[-1]
    last_known_value = feature_row[target].iloc[0] if target in feature_row.columns else None

    print("-" * 60)
    print(f"Last known reading : {last_known_time}  ->  {last_known_value}")
    print(f"Forecast for       : {next_hour}")
    print(f"Predicted {target} : {prediction:,.2f} MW")
    print("-" * 60)
    return {"timestamp": str(next_hour), "region": args.region, "prediction_mw": prediction}


if __name__ == "__main__":
    main()
