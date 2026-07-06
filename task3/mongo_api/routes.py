"""CRUD + time-series endpoints over the `energy_readings` collection defined in
`Database design/mongodb/collection_design.js`.
"""
from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, Query
from pymongo import ReturnDocument

from utils import derive_time_features

from .database import get_collection
from .models import ReadingCreate, ReadingOut, ReadingUpdate

router = APIRouter(prefix="/api/mongo/readings", tags=["MongoDB - energy_readings"])


def _doc_to_reading(doc: dict) -> dict:
    tf = doc["time_features"]
    return {
        "id": str(doc["_id"]),
        "region_name": doc["region"],
        "datetime": doc["datetime"],
        "consumption_mw": doc["consumption_mw"],
        "year": tf["year"],
        "month": tf["month"],
        "day": tf["day"],
        "hour": tf["hour"],
        "day_of_week": tf["day_of_week"],
        "is_weekend": tf["is_weekend"],
        "season": tf["season"],
    }


def _to_object_id(reading_id: str):
    try:
        return ObjectId(reading_id)
    except InvalidId:
        return None


@router.post("", response_model=ReadingOut, status_code=201)
def create_reading(payload: ReadingCreate, col=Depends(get_collection)):
    doc = {
        "region": payload.region_name,
        "datetime": payload.datetime,
        "consumption_mw": payload.consumption_mw,
        "time_features": derive_time_features(payload.datetime),
    }
    result = col.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _doc_to_reading(doc)


@router.get("/latest", response_model=ReadingOut)
def get_latest_reading(col=Depends(get_collection)):
    doc = col.find_one(sort=[("datetime", -1)])
    if doc is None:
        raise HTTPException(404, "No readings found")
    return _doc_to_reading(doc)


@router.get("/range", response_model=list[ReadingOut])
def get_readings_in_range(
    start: datetime = Query(..., description="e.g. 2004-10-01T00:00:00"),
    end: datetime = Query(..., description="e.g. 2004-10-01T23:59:59"),
    col=Depends(get_collection),
):
    cursor = col.find({"datetime": {"$gte": start, "$lte": end}}).sort("datetime", 1)
    return [_doc_to_reading(d) for d in cursor]


@router.get("/{reading_id}", response_model=ReadingOut)
def get_reading(reading_id: str, col=Depends(get_collection)):
    oid = _to_object_id(reading_id)
    doc = col.find_one({"_id": oid}) if oid else None
    if doc is None:
        raise HTTPException(404, "Reading not found")
    return _doc_to_reading(doc)


@router.put("/{reading_id}", response_model=ReadingOut)
def update_reading(reading_id: str, payload: ReadingUpdate, col=Depends(get_collection)):
    oid = _to_object_id(reading_id)
    doc = (
        col.find_one_and_update(
            {"_id": oid},
            {"$set": {"consumption_mw": payload.consumption_mw}},
            return_document=ReturnDocument.AFTER,
        )
        if oid
        else None
    )
    if doc is None:
        raise HTTPException(404, "Reading not found")
    return _doc_to_reading(doc)


@router.delete("/{reading_id}", status_code=204)
def delete_reading(reading_id: str, col=Depends(get_collection)):
    oid = _to_object_id(reading_id)
    deleted = col.delete_one({"_id": oid}).deleted_count if oid else 0
    if not deleted:
        raise HTTPException(404, "Reading not found")
