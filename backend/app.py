import os
from datetime import datetime

from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import Flask, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "taskdb")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[DB_NAME]
tasks_collection = db["tasks"]


def serialize_task(task):
    return {
        "id": str(task["_id"]),
        "title": task["title"],
        "done": task.get("done", False),
        "created_at": task.get("created_at"),
    }


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = [serialize_task(t) for t in tasks_collection.find()]
    return jsonify(tasks), 200


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    if not title:
        return jsonify({"error": "title is required"}), 400

    task = {
        "title": title,
        "done": False,
        "created_at": datetime.utcnow().isoformat(),
    }
    result = tasks_collection.insert_one(task)
    task["_id"] = result.inserted_id
    return jsonify(serialize_task(task)), 201


@app.route("/tasks/<task_id>", methods=["GET"])
def get_task(task_id):
    try:
        task = tasks_collection.find_one({"_id": ObjectId(task_id)})
    except InvalidId:
        return jsonify({"error": "invalid id"}), 400

    if not task:
        return jsonify({"error": "not found"}), 404
    return jsonify(serialize_task(task)), 200


@app.route("/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    try:
        result = tasks_collection.delete_one({"_id": ObjectId(task_id)})
    except InvalidId:
        return jsonify({"error": "invalid id"}), 400

    if result.deleted_count == 0:
        return jsonify({"error": "not found"}), 404
    return jsonify({"deleted": task_id}), 200

@app.route("/tasks/<task_id>/toggle", methods=["PATCH"])
def toggle_task(task_id):
    try:
        task = tasks_collection.find_one({"_id": ObjectId(task_id)})
    except InvalidId:
        return jsonify({"error": "invalid id"}), 400
    if not task:
        return jsonify({"error": "not found"}), 404
    new_status = not task.get("done", False)
    tasks_collection.update_one({"_id": ObjectId(task_id)}, {"$set": {"done": new_status}})
    task["done"] = new_status
    return jsonify(serialize_task(task)), 200
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
