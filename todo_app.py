from pathlib import Path
import json
from datetime import datetime, date

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
                return normalize_tasks(data)
    except (json.JSONDecodeError, OSError):
        pass

    return []


def save_tasks(tasks):
    with TASKS_FILE.open("w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=2)


def normalize_tasks(tasks):
    normalized = []

    for task in tasks:
        if not isinstance(task, dict):
            continue

        normalized.append(
            {
                "title": task.get("title", "").strip(),
                "completed": bool(task.get("completed", False)),
                "created_at": task.get("created_at"),
                "completed_at": task.get("completed_at"),
            }
        )

    return normalized


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


def build_monthly_chart(tasks):
    today = date.today()
    current_year = today.year
    current_month = today.month
    end_year = 2030
    months = []
    counts = {}

    year = current_year
    month = current_month
    while year < end_year or (year == end_year and month <= 12):
        key = f"{year:04d}-{month:02d}"
        counts[key] = 0
        months.append(
            {
                "key": key,
                "label": datetime(year, month, 1).strftime("%b %Y"),
                "count": 0,
            }
        )

        month += 1
        if month == 13:
            month = 1
            year += 1

    for task in tasks:
        completed_at = task.get("completed_at")
        if not completed_at:
            continue

        month_key = completed_at[:7]
        if month_key in counts:
            counts[month_key] += 1

    max_count = 0
    for month in months:
        month["count"] = counts[month["key"]]
        max_count = max(max_count, month["count"])

    for month in months:
        if max_count:
            month["height"] = max(12, int((month["count"] / max_count) * 100))
        else:
            month["height"] = 12

    return {"months": months, "max_count": max_count}


@app.route("/", methods=["GET"])
def index():
    tasks = load_tasks()
    summary = build_summary(tasks)
    chart = build_monthly_chart(tasks)
    return render_template("index.html", tasks=tasks, summary=summary, chart=chart)


@app.route("/tasks", methods=["POST"])
def add_task():
    tasks = load_tasks()
    task_name = request.form.get("title", "").strip()

    if task_name:
        tasks.append(
            {
                "title": task_name,
                "completed": False,
                "created_at": datetime.now().isoformat(),
                "completed_at": None,
            }
        )
        save_tasks(tasks)

    return redirect(url_for("index"))


@app.route("/tasks/<int:task_index>/complete", methods=["POST"])
def complete_task(task_index):
    tasks = load_tasks()

    if 0 <= task_index < len(tasks):
        tasks[task_index]["completed"] = True
        tasks[task_index]["completed_at"] = datetime.now().isoformat()
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

