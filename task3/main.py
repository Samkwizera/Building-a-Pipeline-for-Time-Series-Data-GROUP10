"""Task 3 API entrypoint.

Run from inside this folder:
    uvicorn main:app --reload

Docs available at http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI

from mongo_api.routes import router as mongo_router
from sql_api.routes import router as sql_router

app = FastAPI(
    title="Energy Time-Series API",
    description="CRUD + time-series query endpoints over the energy_readings "
    "data, backed by MySQL and MongoDB.",
    version="1.0.0",
)

app.include_router(sql_router)
app.include_router(mongo_router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok"}
