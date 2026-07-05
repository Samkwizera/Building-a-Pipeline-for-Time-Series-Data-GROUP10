"""
basically load_data.py  (MongoDB version)
Reads AEP_hourly.csv and loads it into MongoDB.

Requirements:
    pip install pymongo pandas

Usage:
    python load_data.py
"""

import pandas as pd
from pymongo import MongoClient, ASCENDING
from datetime import datetime

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME   = "energy_db"
CSV_PATH  = "AEP_hourly.csv"  # put this file in the same folder as this script


def get_season(month):
    if month in (12, 1, 2):
        return "Winter"
    elif month in (3, 4, 5):
        return "Spring"
    elif month in (6, 7, 8):
        return "Summer"
    else:
        return "Autumn"


def load():
    print("Connecting to MongoDB...")
    client = MongoClient(MONGO_URI)
    db     = client[DB_NAME]
    col    = db["energy_readings"]

    # Create indexes before inserting
    col.create_index([("datetime", ASCENDING)])
    col.create_index([("region",   ASCENDING)])

    print("Reading CSV...")
    df = pd.read_csv(CSV_PATH, parse_dates=["Datetime"])
    df.columns = ["datetime", "consumption_mw"]
    df = df.dropna()
    df = df.sort_values("datetime").reset_index(drop=True)

    print(f"Preparing {len(df)} documents...")

    batch = []
    for _, row in df.iterrows():
        dt = row["datetime"].to_pydatetime()
        batch.append({
            "region":         "AEP",
            "datetime":       dt,
            "consumption_mw": float(row["consumption_mw"]),
            "time_features": {
                "year":        dt.year,
                "month":       dt.month,
                "day":         dt.day,
                "hour":        dt.hour,
                "day_of_week": dt.weekday(),
                "is_weekend":  dt.weekday() >= 5,
                "season":      get_season(dt.month)
            }
        })

        if len(batch) == 5000:
            col.insert_many(batch)
            batch = []
            print(f"  Inserted batch up to {dt}...")

    if batch:
        col.insert_many(batch)

    print(f"Done. Total documents in collection: {col.count_documents({})}")
    client.close()


if __name__ == "__main__":
    load()
