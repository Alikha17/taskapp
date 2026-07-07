import app as app_module


def test_health():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_index_handles_backend_down(monkeypatch):
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()
    monkeypatch.setattr(app_module, "BACKEND_URL", "http://127.0.0.1:1")
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"unreachable" in resp.data
