import os

import requests
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend-service:80")


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}, 200


@app.route("/", methods=["GET"])
def index():
    try:
        resp = requests.get(f"{BACKEND_URL}/tasks", timeout=5)
        tasks = resp.json() if resp.status_code == 200 else []
        error = None if resp.status_code == 200 else "Could not load tasks"
    except requests.RequestException:
        tasks = []
        error = "Backend service is unreachable"
    return render_template("index.html", tasks=tasks, error=error)


@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title")
    if title:
        try:
            requests.post(f"{BACKEND_URL}/tasks", json={"title": title}, timeout=5)
        except requests.RequestException:
            pass
    return redirect(url_for("index"))


@app.route("/toggle/<task_id>", methods=["POST"])
def toggle_task(task_id):
    try:
        requests.patch(f"{BACKEND_URL}/tasks/{task_id}/toggle", timeout=5)
    except requests.RequestException:
        pass
    return redirect(url_for("index"))

@app.route("/delete/<task_id>", methods=["POST"])
def delete_task(task_id):
    try:
        requests.delete(f"{BACKEND_URL}/tasks/{task_id}", timeout=5)
    except requests.RequestException:
        pass
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
