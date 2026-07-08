from datetime import datetime

from pydantic import BaseModel, Field


class ReadingCreate(BaseModel):
    region_name: str = Field(..., examples=["AEP"])
    datetime: datetime
    consumption_mw: float


class ReadingUpdate(BaseModel):
    consumption_mw: float


class ReadingOut(BaseModel):
    id: int
    region_name: str
    datetime: datetime
    consumption_mw: float
    year: int
    month: int
    day: int
    hour: int
    day_of_week: int
    is_weekend: bool
    season: str
