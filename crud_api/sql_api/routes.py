"""CRUD + time-series endpoints over the regions / time_periods / energy_readings
tables defined in `Database design/sql/schema.sql`.
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from utils import derive_time_features

from .database import get_db
from .models import ReadingCreate, ReadingOut, ReadingUpdate

router = APIRouter(prefix="/api/sql/readings", tags=["SQL - energy_readings"])

READING_SELECT = """
    SELECT er.reading_id, r.region_name, tp.datetime, er.consumption_mw,
           tp.year, tp.month, tp.day, tp.hour, tp.day_of_week, tp.is_weekend, tp.season
    FROM energy_readings er
    JOIN regions r ON er.region_id = r.region_id
    JOIN time_periods tp ON er.period_id = tp.period_id
"""


def _row_to_reading(row: dict) -> dict:
    return {
        "id": row["reading_id"],
        "region_name": row["region_name"],
        "datetime": row["datetime"],
        "consumption_mw": row["consumption_mw"],
        "year": row["year"],
        "month": row["month"],
        "day": row["day"],
        "hour": row["hour"],
        "day_of_week": row["day_of_week"],
        "is_weekend": bool(row["is_weekend"]),
        "season": row["season"],
    }


def _fetch_reading(conn, reading_id: int):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(READING_SELECT + " WHERE er.reading_id = %s", (reading_id,))
    row = cursor.fetchone()
    cursor.close()
    return _row_to_reading(row) if row else None


@router.post("", response_model=ReadingOut, status_code=201)
def create_reading(payload: ReadingCreate, conn=Depends(get_db)):
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "INSERT INTO regions (region_name) VALUES (%s) "
        "ON DUPLICATE KEY UPDATE region_id = LAST_INSERT_ID(region_id)",
        (payload.region_name,),
    )
    region_id = cursor.lastrowid

    features = derive_time_features(payload.datetime)
    cursor.execute(
        """
        INSERT INTO time_periods (datetime, year, month, day, hour, day_of_week, is_weekend, season)
        VALUES (%(datetime)s, %(year)s, %(month)s, %(day)s, %(hour)s, %(day_of_week)s, %(is_weekend)s, %(season)s)
        ON DUPLICATE KEY UPDATE period_id = LAST_INSERT_ID(period_id)
        """,
        {"datetime": payload.datetime, **features},
    )
    period_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO energy_readings (region_id, period_id, consumption_mw) VALUES (%s, %s, %s)",
        (region_id, period_id, payload.consumption_mw),
    )
    reading_id = cursor.lastrowid
    conn.commit()
    cursor.close()

    return _fetch_reading(conn, reading_id)


@router.get("/latest", response_model=ReadingOut)
def get_latest_reading(conn=Depends(get_db)):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(READING_SELECT + " ORDER BY tp.datetime DESC LIMIT 1")
    row = cursor.fetchone()
    cursor.close()
    if row is None:
        raise HTTPException(404, "No readings found")
    return _row_to_reading(row)


@router.get("/range", response_model=list[ReadingOut])
def get_readings_in_range(
    start: datetime = Query(..., description="e.g. 2004-10-01T00:00:00"),
    end: datetime = Query(..., description="e.g. 2004-10-03T23:59:59"),
    conn=Depends(get_db),
):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        READING_SELECT + " WHERE tp.datetime BETWEEN %s AND %s ORDER BY tp.datetime ASC",
        (start, end),
    )
    rows = cursor.fetchall()
    cursor.close()
    return [_row_to_reading(r) for r in rows]


@router.get("/{reading_id}", response_model=ReadingOut)
def get_reading(reading_id: int, conn=Depends(get_db)):
    reading = _fetch_reading(conn, reading_id)
    if reading is None:
        raise HTTPException(404, "Reading not found")
    return reading


@router.put("/{reading_id}", response_model=ReadingOut)
def update_reading(reading_id: int, payload: ReadingUpdate, conn=Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE energy_readings SET consumption_mw = %s WHERE reading_id = %s",
        (payload.consumption_mw, reading_id),
    )
    updated = cursor.rowcount
    conn.commit()
    cursor.close()
    if not updated:
        raise HTTPException(404, "Reading not found")
    return _fetch_reading(conn, reading_id)


@router.delete("/{reading_id}", status_code=204)
def delete_reading(reading_id: int, conn=Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM energy_readings WHERE reading_id = %s", (reading_id,))
    deleted = cursor.rowcount
    conn.commit()
    cursor.close()
    if not deleted:
        raise HTTPException(404, "Reading not found")
