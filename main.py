# main.py - Task Manager API
# Run: uvicorn main:app --reload
# Docs: http://127.0.0.1:8000/docs

import json
from pathlib import Path
from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from model import Priority, Status, TaskCreate, TaskUpdate

app = FastAPI(
    title="Task Manager API",
    version="1.0.0",
    description="REST API for managing tasks. Data stored in tasks.json.",
)

DB_FILE = Path("tasks.json")

def read_db() -> dict:
    """Load tasks.json. Creates it automatically on first run."""
    if not DB_FILE.exists():
        write_db({"next_id": 1, "tasks": {}})
    return json.loads(DB_FILE.read_text())

def write_db(data: dict) -> None:
    """Save data to tasks.json, formatted for readability."""
    DB_FILE.write_text(json.dumps(data, indent=2, default=str))

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Return a clean error message instead of FastAPI's default verbose 422."""
    errors = [
        {
            "field":   "->".join(str(part) for part in err["loc"][1:]),
            "message": err["msg"],
        }
        for err in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"error": "Validation failed", "errors": errors})

@app.get("/tasks", tags=["Tasks"], summary="List all tasks")
def list_tasks(status: Optional[Status] = None, priority: Optional[Priority] = None):
    """Return all tasks. Filter with ?status=todo or ?priority=high."""
    db    = read_db()
    tasks = list(db["tasks"].values())
    if status:
        tasks = [t for t in tasks if t["status"] == status.value]
    if priority:
        tasks = [t for t in tasks if t["priority"] == priority.value]
    return {"count": len(tasks), "tasks": tasks}

@app.post("/tasks", tags=["Tasks"], status_code=201, summary="Create a new task")
def create_task(task: TaskCreate):
    """Create a task. Required: title. Optional: description, priority, due_date."""
    db      = read_db()
    task_id = str(db["next_id"])
    new_task = {
        "id":          task_id,
        "title":       task.title,
        "description": task.description,
        "priority":    task.priority.value,
        "status":      Status.todo.value,
        "due_date":    str(task.due_date) if task.due_date else None,
        "created_at":  str(date.today()),
    }
    db["tasks"][task_id] = new_task
    db["next_id"] += 1
    write_db(db)
    return new_task

@app.get("/tasks/{task_id}", tags=["Tasks"], summary="Get a single task")
def get_task(task_id: int):
    """Return a single task by its numeric ID."""
    db   = read_db()
    task = db["tasks"].get(str(task_id))
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task

@app.patch("/tasks/{task_id}", tags=["Tasks"], summary="Update a task")
def update_task(task_id: int, updates: TaskUpdate):
    """Partially update a task. Only fields you send will change."""
    db   = read_db()
    task = db["tasks"].get(str(task_id))
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    for field, value in updates.model_dump(exclude_unset=True).items():
        if hasattr(value, "value"):
            task[field] = value.value
        elif isinstance(value, date):
            task[field] = str(value)
        else:
            task[field] = value
    write_db(db)
    return task

@app.delete("/tasks/{task_id}", tags=["Tasks"], status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    """Delete a single task. Returns 204 No Content."""
    db = read_db()
    if str(task_id) not in db["tasks"]:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    del db["tasks"][str(task_id)]
    write_db(db)

@app.delete("/tasks", tags=["Tasks"], status_code=204, summary="Delete all tasks")
def delete_all_tasks():
    """Wipe every task. Cannot be undone."""
    db = read_db()
    db["tasks"] = {}
    write_db(db)

@app.get("/health", tags=["Meta"], summary="Health check")
def health():
    """Confirm the API is running and show task counts."""
    db    = read_db()
    tasks = list(db["tasks"].values())
    return {
        "status":      "ok",
        "total_tasks": len(tasks),
        "by_status": {
            "todo":        sum(1 for t in tasks if t["status"] == "todo"),
            "in_progress": sum(1 for t in tasks if t["status"] == "in_progress"),
            "done":        sum(1 for t in tasks if t["status"] == "done"),
        },
    }