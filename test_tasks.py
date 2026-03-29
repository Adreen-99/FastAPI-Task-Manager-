# test_tasks.py — Full test suite for the Task Manager API
#
# Run with:  pytest test_tasks.py -v

import json
import pytest
from fastapi.testclient import TestClient
from main import app, DB_FILE


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clean_db(tmp_path, monkeypatch):
    """
    Runs before every test:
    - Points DB_FILE at a temp file so tests never touch the real tasks.json
    - Writes a fresh empty database into that temp file
    Temp file is deleted automatically by pytest after each test.
    """
    test_db = tmp_path / "tasks.json"
    monkeypatch.setattr("main.DB_FILE", test_db)
    test_db.write_text(json.dumps({"next_id": 1, "tasks": {}}, indent=2))
    yield


@pytest.fixture
def client():
    """A TestClient that talks to the app without a running server."""
    return TestClient(app)


@pytest.fixture
def client_with_tasks(client):
    """A client pre-loaded with three tasks of different priorities."""
    client.post("/tasks", json={"title": "Task A", "priority": "low"})
    client.post("/tasks", json={"title": "Task B", "priority": "high"})
    client.post("/tasks", json={"title": "Task C", "priority": "medium"})
    return client


# ── Health check ──────────────────────────────────────────────────────────────

def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "total_tasks" in data
    assert "by_status" in data


# ── Create task ───────────────────────────────────────────────────────────────

def test_create_task_minimal(client):
    """Only title is required — everything else uses defaults."""
    res = client.post("/tasks", json={"title": "Buy milk"})
    assert res.status_code == 201
    data = res.json()
    assert data["title"]    == "Buy milk"
    assert data["status"]   == "todo"       # always starts as todo
    assert data["priority"] == "medium"     # default priority
    assert data["id"]       == "1"
    assert "created_at" in data


def test_create_task_all_fields(client):
    """All optional fields should be stored and returned correctly."""
    res = client.post("/tasks", json={
        "title":       "Write report",
        "description": "Q1 summary",
        "priority":    "high",
        "due_date":    "2026-04-01",
    })
    assert res.status_code == 201
    data = res.json()
    assert data["description"] == "Q1 summary"
    assert data["priority"]    == "high"
    assert data["due_date"]    == "2026-04-01"


def test_create_task_missing_title(client):
    """Missing title must return 422 with a readable errors list."""
    res = client.post("/tasks", json={"priority": "high"})
    assert res.status_code == 422
    body = res.json()
    assert "errors" in body
    assert body["errors"][0]["field"] == "title"


def test_create_task_title_too_short(client):
    """Empty string title must fail validation."""
    res = client.post("/tasks", json={"title": ""})
    assert res.status_code == 422


def test_create_task_invalid_priority(client):
    """Priority must be one of: low / medium / high."""
    res = client.post("/tasks", json={"title": "Test", "priority": "urgent"})
    assert res.status_code == 422


def test_create_multiple_tasks_increments_id(client):
    """Each new task should get the next sequential ID."""
    r1 = client.post("/tasks", json={"title": "First"})
    r2 = client.post("/tasks", json={"title": "Second"})
    assert r1.json()["id"] == "1"
    assert r2.json()["id"] == "2"


# ── List tasks ────────────────────────────────────────────────────────────────

def test_list_tasks_empty(client):
    """Empty database returns an empty list, not an error."""
    res = client.get("/tasks")
    assert res.status_code == 200
    assert res.json() == {"count": 0, "tasks": []}


def test_list_tasks_returns_all(client_with_tasks):
    """All tasks are returned when no filters are applied."""
    res = client_with_tasks.get("/tasks")
    assert res.status_code == 200
    assert res.json()["count"] == 3


def test_filter_by_status(client_with_tasks):
    """?status=todo should only return todo tasks."""
    res = client_with_tasks.get("/tasks?status=todo")
    assert res.status_code == 200
    tasks = res.json()["tasks"]
    assert all(t["status"] == "todo" for t in tasks)


def test_filter_by_priority(client_with_tasks):
    """?priority=high should only return high-priority tasks."""
    res = client_with_tasks.get("/tasks?priority=high")
    assert res.status_code == 200
    tasks = res.json()["tasks"]
    assert all(t["priority"] == "high" for t in tasks)
    assert len(tasks) == 1


def test_filter_by_status_and_priority(client):
    """Both filters applied together must satisfy both conditions."""
    client.post("/tasks", json={"title": "A", "priority": "high"})
    client.post("/tasks", json={"title": "B", "priority": "low"})
    client.patch("/tasks/1", json={"status": "done"})

    res   = client.get("/tasks?status=todo&priority=low")
    tasks = res.json()["tasks"]
    assert len(tasks) == 1
    assert tasks[0]["title"] == "B"


def test_filter_invalid_status(client):
    """An unrecognised status value must return 422."""
    res = client.get("/tasks?status=finished")
    assert res.status_code == 422


# ── Get single task ───────────────────────────────────────────────────────────

def test_get_task(client):
    """Should return the correct task for a valid ID."""
    client.post("/tasks", json={"title": "Find me"})
    res = client.get("/tasks/1")
    assert res.status_code == 200
    assert res.json()["title"] == "Find me"


def test_get_task_not_found(client):
    """Non-existent task ID must return 404."""
    res = client.get("/tasks/999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


# ── Update task ───────────────────────────────────────────────────────────────

def test_update_status(client):
    """PATCH status updates only the status — other fields stay unchanged."""
    client.post("/tasks", json={"title": "Do laundry"})
    res = client.patch("/tasks/1", json={"status": "done"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "done"
    assert data["title"]  == "Do laundry"   # unchanged


def test_update_multiple_fields(client):
    """Multiple fields can be updated in a single PATCH."""
    client.post("/tasks", json={"title": "Old title", "priority": "low"})
    res = client.patch("/tasks/1", json={"title": "New title", "priority": "high"})
    assert res.status_code == 200
    data = res.json()
    assert data["title"]    == "New title"
    assert data["priority"] == "high"


def test_update_preserves_other_fields(client):
    """Fields not included in PATCH must not be touched."""
    client.post("/tasks", json={
        "title":       "Important task",
        "description": "Keep this",
        "priority":    "high",
    })
    client.patch("/tasks/1", json={"status": "in_progress"})
    res  = client.get("/tasks/1")
    data = res.json()
    assert data["description"] == "Keep this"    # untouched
    assert data["priority"]    == "high"         # untouched
    assert data["status"]      == "in_progress"  # updated


def test_update_not_found(client):
    """PATCH on a non-existent task must return 404."""
    res = client.patch("/tasks/999", json={"status": "done"})
    assert res.status_code == 404


def test_update_invalid_status(client):
    """Invalid status value in PATCH must return 422."""
    client.post("/tasks", json={"title": "Test"})
    res = client.patch("/tasks/1", json={"status": "maybe"})
    assert res.status_code == 422


# ── Delete task ───────────────────────────────────────────────────────────────

def test_delete_task(client):
    """Deleted task should not be retrievable — GET returns 404."""
    client.post("/tasks", json={"title": "Delete me"})
    res = client.delete("/tasks/1")
    assert res.status_code == 204
    assert client.get("/tasks/1").status_code == 404


def test_delete_task_not_found(client):
    """Deleting a non-existent task must return 404."""
    res = client.delete("/tasks/999")
    assert res.status_code == 404


def test_delete_does_not_affect_other_tasks(client):
    """Deleting one task must leave all others intact."""
    client.post("/tasks", json={"title": "Keep me"})
    client.post("/tasks", json={"title": "Delete me"})
    client.delete("/tasks/2")

    res = client.get("/tasks")
    assert res.json()["count"] == 1
    assert res.json()["tasks"][0]["title"] == "Keep me"


def test_delete_all_tasks(client_with_tasks):
    """DELETE /tasks must wipe every task."""
    assert client_with_tasks.get("/tasks").json()["count"] == 3
    res = client_with_tasks.delete("/tasks")
    assert res.status_code == 204
    assert client_with_tasks.get("/tasks").json()["count"] == 0


# ── Persistence ───────────────────────────────────────────────────────────────

def test_data_persists_to_json(tmp_path, monkeypatch):
    """
    Tasks written via the API should be saved to tasks.json on disk.
    Confirms that write_db() is actually writing to the file.
    """
    test_db = tmp_path / "tasks.json"
    monkeypatch.setattr("main.DB_FILE", test_db)
    test_db.write_text(json.dumps({"next_id": 1, "tasks": {}}, indent=2))

    client = TestClient(app)
    client.post("/tasks", json={"title": "Persisted task"})

    saved = json.loads(test_db.read_text())
    assert "1" in saved["tasks"]
    assert saved["tasks"]["1"]["title"] == "Persisted task"