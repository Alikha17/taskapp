import mongomock
import pytest

import app as app_module


@pytest.fixture(autouse=True)
def use_mock_mongo(monkeypatch):
    mock_client = mongomock.MongoClient()
    mock_db = mock_client["taskdb"]
    monkeypatch.setattr(app_module, "tasks_collection", mock_db["tasks"])
    yield


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_create_task_missing_title(client):
    resp = client.post("/tasks", json={})
    assert resp.status_code == 400


def test_create_and_get_task(client):
    resp = client.post("/tasks", json={"title": "Write unit tests"})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["title"] == "Write unit tests"
    assert body["done"] is False

    task_id = body["id"]
    resp2 = client.get(f"/tasks/{task_id}")
    assert resp2.status_code == 200
    assert resp2.get_json()["id"] == task_id


def test_get_task_invalid_id(client):
    resp = client.get("/tasks/not-a-valid-id")
    assert resp.status_code == 400


def test_delete_task(client):
    created = client.post("/tasks", json={"title": "Temp task"}).get_json()
    task_id = created["id"]

    resp = client.delete(f"/tasks/{task_id}")
    assert resp.status_code == 200

    resp2 = client.get(f"/tasks/{task_id}")
    assert resp2.status_code == 404


def test_list_tasks(client):
    client.post("/tasks", json={"title": "Task A"})
    client.post("/tasks", json={"title": "Task B"})

    resp = client.get("/tasks")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2
