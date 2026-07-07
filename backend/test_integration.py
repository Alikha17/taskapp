import os

import pytest
from pymongo import MongoClient

import app as app_module

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")


@pytest.fixture(autouse=True)
def real_mongo():
    real_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    real_client.admin.command("ping")

    test_db = real_client["taskdb_integration_test"]
    app_module.tasks_collection = test_db["tasks"]

    yield

    test_db.drop_collection("tasks")


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c


def test_full_task_lifecycle_against_real_db(client):
    create_resp = client.post("/tasks", json={"title": "Integration task"})
    assert create_resp.status_code == 201
    task_id = create_resp.get_json()["id"]

    list_resp = client.get("/tasks")
    assert any(t["id"] == task_id for t in list_resp.get_json())

    get_resp = client.get(f"/tasks/{task_id}")
    assert get_resp.status_code == 200

    del_resp = client.delete(f"/tasks/{task_id}")
    assert del_resp.status_code == 200

    final_get = client.get(f"/tasks/{task_id}")
    assert final_get.status_code == 404
