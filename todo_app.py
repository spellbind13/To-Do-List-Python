from pathlib import Path
import json
from datetime import datetime, date
import calendar

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

        title = task.get("title", "").strip()
        if not title:
            continue

        due_date = task.get("due_date")
        due_label = format_due_date(due_date) if due_date else None

        normalized.append(
            {
                "title": title,
                "completed": bool(task.get("completed", False)),
                "created_at": task.get("created_at"),
                "completed_at": task.get("completed_at"),
                "due_date": due_date,
                "due_label": due_label,
            }
        )

    return sort_tasks(normalized)


def sort_tasks(tasks):
    def sort_key(task):
        due_date = task.get("due_date") or "9999-12-31"
        return (task.get("completed", False), due_date, task.get("title", "").lower())

    return sorted(tasks, key=sort_key)


def format_due_date(due_date):
    try:
        return datetime.strptime(due_date, "%Y-%m-%d").strftime("%b %d, %Y")
    except (TypeError, ValueError):
        return None


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
    due_map = {}

    year = current_year
    month = current_month
    while year < end_year or (year == end_year and month <= 12):
        key = f"{year:04d}-{month:02d}"
        due_map[key] = {}
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
        due_date = task.get("due_date")
        if not due_date:
            continue

        month_key = due_date[:7]
        if month_key in due_map:
            day_key = due_date[8:10]
            due_map[month_key].setdefault(day_key, []).append(
                {
                    "title": task.get("title", ""),
                    "completed": task.get("completed", False),
                }
            )

    for month in months:
        year_value, month_value = map(int, month["key"].split("-"))
        days_in_month = calendar.monthrange(year_value, month_value)[1]
        first_weekday, _ = calendar.monthrange(year_value, month_value)
        month["start_offset"] = first_weekday
        month["days"] = []
        month["count"] = 0

        for day_number in range(1, days_in_month + 1):
            day_key = f"{day_number:02d}"
            day_tasks = due_map[month["key"]].get(day_key, [])
            month["count"] += len(day_tasks)
            month["days"].append(
                {
                    "day": day_number,
                    "count": len(day_tasks),
                    "tasks": day_tasks,
                }
            )

    return {"months": months}


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
    due_date = request.form.get("due_date", "").strip() or None

    if task_name:
        tasks.append(
            {
                "title": task_name,
                "completed": False,
                "created_at": datetime.now().isoformat(),
                "completed_at": None,
                "due_date": due_date,
                "due_label": format_due_date(due_date) if due_date else None,
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

