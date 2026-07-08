"""End-to-end tests for the Mongo CRUD + time-series endpoints.

Runs against mongomock instead of a real MongoDB instance, since Task 3's
handoff notes said these routes were never exercised in a real environment.
"""
import mongomock
import pytest
from fastapi.testclient import TestClient

from main import app
from mongo_api.database import get_collection

BASE = "/api/mongo/readings"


@pytest.fixture
def client():
    collection = mongomock.MongoClient()["energy_db"]["energy_readings"]
    app.dependency_overrides[get_collection] = lambda: collection
    yield TestClient(app)
    app.dependency_overrides.clear()


def _create(client, region="AEP", dt="2004-10-01T01:00:00", mw=13478.0):
    return client.post(BASE, json={
        "region_name": region,
        "datetime": dt,
        "consumption_mw": mw,
    })


def test_create_reading_derives_time_features(client):
    resp = _create(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["region_name"] == "AEP"
    assert body["year"] == 2004
    assert body["month"] == 10
    assert body["day"] == 1
    assert body["hour"] == 1
    assert body["day_of_week"] == 4
    assert body["is_weekend"] is False
    assert body["season"] == "Autumn"


def test_get_reading_by_id(client):
    created = _create(client).json()
    resp = client.get(f"{BASE}/{created['id']}")
    assert resp.status_code == 200
    assert resp.json() == created


def test_get_reading_invalid_id_returns_404_not_500(client):
    resp = client.get(f"{BASE}/not-a-valid-object-id")
    assert resp.status_code == 404


def test_get_reading_missing_id_returns_404(client):
    resp = client.get(f"{BASE}/64b64b64b64b64b64b64b64")
    assert resp.status_code == 404


def test_get_latest_reading(client):
    _create(client, dt="2004-10-01T01:00:00", mw=100)
    newest = _create(client, dt="2004-10-01T03:00:00", mw=300).json()
    _create(client, dt="2004-10-01T02:00:00", mw=200)

    resp = client.get(f"{BASE}/latest")
    assert resp.status_code == 200
    assert resp.json()["id"] == newest["id"]


def test_get_latest_reading_empty_collection_returns_404(client):
    resp = client.get(f"{BASE}/latest")
    assert resp.status_code == 404


def test_get_readings_in_range(client):
    _create(client, dt="2004-10-01T00:00:00", mw=1)
    inside_a = _create(client, dt="2004-10-01T10:00:00", mw=2).json()
    inside_b = _create(client, dt="2004-10-01T20:00:00", mw=3).json()
    _create(client, dt="2004-10-02T00:00:00", mw=4)

    resp = client.get(
        f"{BASE}/range",
        params={"start": "2004-10-01T01:00:00", "end": "2004-10-01T23:59:59"},
    )
    assert resp.status_code == 200
    ids = [r["id"] for r in resp.json()]
    assert ids == [inside_a["id"], inside_b["id"]]


def test_update_reading(client):
    created = _create(client, mw=100).json()
    resp = client.put(f"{BASE}/{created['id']}", json={"consumption_mw": 999})
    assert resp.status_code == 200
    assert resp.json()["consumption_mw"] == 999


def test_update_reading_not_found(client):
    resp = client.put(
        f"{BASE}/64b64b64b64b64b64b64b64", json={"consumption_mw": 999}
    )
    assert resp.status_code == 404


def test_update_reading_invalid_id_returns_404_not_500(client):
    resp = client.put(f"{BASE}/not-a-valid-object-id", json={"consumption_mw": 999})
    assert resp.status_code == 404


def test_delete_reading(client):
    created = _create(client).json()
    resp = client.delete(f"{BASE}/{created['id']}")
    assert resp.status_code == 204
    assert client.get(f"{BASE}/{created['id']}").status_code == 404


def test_delete_reading_not_found(client):
    resp = client.delete(f"{BASE}/64b64b64b64b64b64b64b64")
    assert resp.status_code == 404


def test_delete_reading_invalid_id_returns_404_not_500(client):
    resp = client.delete(f"{BASE}/not-a-valid-object-id")
    assert resp.status_code == 404
