from flask import Flask, jsonify, request

app = Flask(__name__)


# In-memory mock database
tasks = [
    {
        "id": 1,
        "title": "Configure NetLab VM",
        "priority": "high",
        "completed": True,
        "due_date": "2026-09-01"
    },
    {
        "id": 2,
        "title": "Implement Centralized Error Handlers",
        "priority": "medium",
        "completed": False,
        "due_date": "2026-09-15"
    },
    {
        "id": 3,
        "title": "Design SQLite Schema",
        "priority": "low",
        "completed": False,
        "due_date": "2026-09-22"
    }
]


ALLOWED_PRIORITIES = {"low", "medium", "high"}


# -------------------------
# Centralized Error Handlers
# -------------------------

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Resource not found",
        "status": 404
    }), 404


@app.errorhandler(400)
def bad_request(e):
    return jsonify({
        "error": "Bad Request",
        "status": 400
    }), 400


# -------------------------
# GET all tasks
# -------------------------

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    priority_filter = request.args.get("priority")

    if priority_filter:
        filtered = [
            task for task in tasks
            if task["priority"].lower() == priority_filter.lower()
        ]

        return jsonify({
            "count": len(filtered),
            "data": filtered
        }), 200

    return jsonify({
        "count": len(tasks),
        "data": tasks
    }), 200


# -------------------------
# GET single task
# -------------------------

@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = next(
        (task for task in tasks if task["id"] == task_id),
        None
    )

    if not task:
        return jsonify({
            "error": f"Task {task_id} not found",
            "status": 404
        }), 404

    return jsonify({
        "data": task
    }), 200


# -------------------------
# POST create task
# -------------------------

@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Missing JSON request body",
            "status": 400
        }), 400

    # Required fields
    if "title" not in data or "priority" not in data:
        return jsonify({
            "error": "Missing required fields: 'title' and 'priority'",
            "status": 400
        }), 400

    # Validate title
    if not isinstance(data["title"], str) or not data["title"].strip():
        return jsonify({
            "error": "'title' must be a non-empty string",
            "status": 422
        }), 422

    # Validate priority
    if (
        not isinstance(data["priority"], str)
        or data["priority"].lower() not in ALLOWED_PRIORITIES
    ):
        return jsonify({
            "error": "'priority' must be one of low, medium, or high",
            "status": 422
        }), 422

    # Validate completed if supplied
    if "completed" in data and not isinstance(data["completed"], bool):
        return jsonify({
            "error": "'completed' must be true or false",
            "status": 422
        }), 422

    # Validate due_date if supplied
    if "due_date" in data and not isinstance(data["due_date"], str):
        return jsonify({
            "error": "'due_date' must be a string",
            "status": 422
        }), 422

    new_id = max(
        [task["id"] for task in tasks],
        default=0
    ) + 1

    new_task = {
        "id": new_id,
        "title": data["title"].strip(),
        "priority": data["priority"].lower(),
        "completed": data.get("completed", False),
        "due_date": data.get("due_date", "N/A")
    }

    tasks.append(new_task)

    return jsonify({
        "message": "Task created",
        "data": new_task
    }), 201


# -------------------------
# PUT update task
# -------------------------

@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = next(
        (task for task in tasks if task["id"] == task_id),
        None
    )

    if not task:
        return jsonify({
            "error": f"Task {task_id} not found",
            "status": 404
        }), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({
            "error": "Missing JSON request body",
            "status": 400
        }), 400

    if "title" in data:
        if not isinstance(data["title"], str) or not data["title"].strip():
            return jsonify({
                "error": "'title' cannot be empty",
                "status": 422
            }), 422

        task["title"] = data["title"].strip()

    if "priority" in data:
        if (
            not isinstance(data["priority"], str)
            or data["priority"].lower() not in ALLOWED_PRIORITIES
        ):
            return jsonify({
                "error": "'priority' must be one of low, medium, or high",
                "status": 422
            }), 422

        task["priority"] = data["priority"].lower()

    if "completed" in data:
        if not isinstance(data["completed"], bool):
            return jsonify({
                "error": "'completed' must be true or false",
                "status": 422
            }), 422

        task["completed"] = data["completed"]

    if "due_date" in data:
        if not isinstance(data["due_date"], str):
            return jsonify({
                "error": "'due_date' must be a string",
                "status": 422
            }), 422

        task["due_date"] = data["due_date"]

    return jsonify({
        "message": "Task updated",
        "data": task
    }), 200


# -------------------------
# DELETE task
# -------------------------

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    global tasks

    task = next(
        (task for task in tasks if task["id"] == task_id),
        None
    )

    if not task:
        return jsonify({
            "error": f"Task {task_id} not found",
            "status": 404
        }), 404

    tasks = [
        task for task in tasks
        if task["id"] != task_id
    ]

    return jsonify({
        "message": f"Task {task_id} deleted successfully"
    }), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
