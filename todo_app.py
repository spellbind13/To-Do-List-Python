from pathlib import Path
import json

from flask import Flask, redirect, render_template, request, url_for


BASE_DIR = Path(__file__).resolve().parent
TASKS_FILE = BASE_DIR / "tasks.json"

app = Flask(__name__)


def load_tasks():
    if not TASKS_FILE.exists():
        return []

    try:
        with TASKS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
    except (json.JSONDecodeError, OSError):
        pass

    return []


def save_tasks(tasks):
    with TASKS_FILE.open("w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=2)


def build_summary(tasks):
    total = len(tasks)
    completed = sum(task.get("completed", False) for task in tasks)
    remaining = total - completed
    completion_rate = int((completed / total) * 100) if total else 0

    return {
        "total": total,
        "completed": completed,
        "remaining": remaining,
        "completion_rate": completion_rate,
    }


@app.route("/", methods=["GET"])
def index():
    tasks = load_tasks()
    summary = build_summary(tasks)
    return render_template("index.html", tasks=tasks, summary=summary)


@app.route("/tasks", methods=["POST"])
def add_task():
    tasks = load_tasks()
    task_name = request.form.get("title", "").strip()

    if task_name:
        tasks.append({"title": task_name, "completed": False})
        save_tasks(tasks)

    return redirect(url_for("index"))


@app.route("/tasks/<int:task_index>/complete", methods=["POST"])
def complete_task(task_index):
    tasks = load_tasks()

    if 0 <= task_index < len(tasks):
        tasks[task_index]["completed"] = True
        save_tasks(tasks)

    return redirect(url_for("index"))


@app.route("/tasks/<int:task_index>/delete", methods=["POST"])
def delete_task(task_index):
    tasks = load_tasks()

    if 0 <= task_index < len(tasks):
        tasks.pop(task_index)
        save_tasks(tasks)

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
@app.route("/tasks/<int:task_index>/delete", methods=["POST"])
def delete_task(task_index):
    tasks = load_tasks()

    if 0 <= task_index < len(tasks):
        tasks.pop(task_index)
        save_tasks(tasks)

    return redirect(url_for("index"))

