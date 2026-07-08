"""MongoDB connection for the `energy_readings` collection defined in
`Database design/mongodb/collection_design.js`. Override via env vars if needed.
"""
import os

from pymongo import MongoClient
from pymongo.collection import Collection

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "energy_db")

_client = MongoClient(MONGO_URI)


def get_collection() -> Collection:
    return _client[MONGO_DB_NAME]["energy_readings"]
