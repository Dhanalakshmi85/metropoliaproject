from flask import Flask, render_template, request, redirect
import json
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "data/sample_tasks.json"

# --------- Load & Save --------- #
def load_tasks():
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except:
        return []

def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=4)


# --------- HOME PAGE --------- #
@app.route("/", methods=["GET", "POST"])
def home():
    tasks = load_tasks()
    today = datetime.today().date()

    # urgent reminders (AI assist)
    reminders = []
    for t in tasks:
        try:
            deadline = datetime.strptime(t["deadline"], "%Y-%m-%d").date()
        except ValueError:
            continue  # skip invalid dates

        days_left = (deadline - today).days
        if days_left <= 1:
            reminders.append({
                "task": t["task"],
                "deadline": t["deadline"],
                "days_left": days_left
            })

    # add new task
    if request.method == "POST":
        new_task = {
            "task": request.form["task"],
            "deadline": request.form["deadline"],
            "hours_needed": int(request.form["hours"])
        }
        tasks.append(new_task)
        save_tasks(tasks)
        return redirect("/")

    return render_template("index.html", tasks=tasks, reminders=reminders)


# --------- WEEKLY AI PLAN --------- #
@app.route("/plan", methods=["POST"])
def plan():
    tasks = load_tasks()
    python_hours = int(request.form["python"])
    finnish_hours = int(request.form["finnish"])

    week = [
        {"name": "Monday", "python": python_hours, "finnish": finnish_hours},
        {"name": "Tuesday", "python": python_hours, "finnish": finnish_hours},
        {"name": "Wednesday", "python": python_hours, "finnish": finnish_hours},
        {"name": "Thursday", "python": python_hours, "finnish": finnish_hours},
        {"name": "Friday", "python": python_hours, "finnish": finnish_hours},
        {"name": "Saturday", "python": python_hours, "finnish": finnish_hours},
        {"name": "Sunday", "python": 0, "finnish": 0}  # rest
    ]

    # AI Priority Sorting
    today = datetime.today()
    schedule = []
    for t in tasks:
        try:
            deadline = datetime.strptime(t["deadline"], "%Y-%m-%d")
        except:
            continue

        days_left = (deadline - today).days

        if days_left <= 1:
            priority = "🔴 URGENT"
        elif days_left <= 3:
            priority = "🟠 High"
        else:
            priority = "🟢 Normal"

        schedule.append({
            "task": t["task"],
            "deadline": t["deadline"],
            "priority": priority
        })

    return render_template("results.html", plan=schedule, week=week)


# --------- RUN --------- #
if __name__ == "__main__":
    app.run(debug=True, port=5001)
