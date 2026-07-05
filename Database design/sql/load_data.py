"""
load_data.py
Reads AEP_hourly.csv and loads it into the MySQL database.

Requirements:
    pip install mysql-connector-python pandas

Usage:
    python load_data.py
"""

import pandas as pd
import mysql.connector
from datetime import datetime

# --- Database connection settings (change password to yours) ---
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "your_password_here",
    "database": "energy_db"
}

CSV_PATH = "AEP_hourly.csv"  # put this file in the same folder as this script


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
    print("Connecting to MySQL...")
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    print("Reading CSV...")
    df = pd.read_csv(CSV_PATH, parse_dates=["Datetime"])
    df.columns = ["datetime", "consumption_mw"]
    df = df.dropna()
    df = df.sort_values("datetime").reset_index(drop=True)

    # Insert region
    cursor.execute("""
        INSERT IGNORE INTO regions (region_name, description)
        VALUES ('AEP', 'American Electric Power - Midwest and Appalachia')
    """)
    conn.commit()
    cursor.execute("SELECT region_id FROM regions WHERE region_name = 'AEP'")
    region_id = cursor.fetchone()[0]

    print(f"Loading {len(df)} rows...")

    for i, row in df.iterrows():
        dt = row["datetime"]
        mw = float(row["consumption_mw"])

        # Insert time period
        cursor.execute("""
            INSERT IGNORE INTO time_periods
                (datetime, year, month, day, hour, day_of_week, is_weekend, season)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            dt,
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.weekday(),
            dt.weekday() >= 5,
            get_season(dt.month)
        ))

        # Get the period_id
        cursor.execute("SELECT period_id FROM time_periods WHERE datetime = %s", (dt,))
        period_id = cursor.fetchone()[0]

        # Insert reading
        cursor.execute("""
            INSERT IGNORE INTO energy_readings (region_id, period_id, consumption_mw)
            VALUES (%s, %s, %s)
        """, (region_id, period_id, mw))

        if i % 5000 == 0:
            conn.commit()
            print(f"  {i} / {len(df)} rows inserted...")

    conn.commit()
    cursor.close()
    conn.close()
    print("Done. All data loaded successfully.")


if __name__ == "__main__":
    load()
