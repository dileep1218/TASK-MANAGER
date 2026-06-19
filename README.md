# Task Manager API

A task management application built in Python, evolved from a simple CRUD script into a properly layered application with object-oriented design, a REST API, and an automated test suite.

This project demonstrates clean architecture (separation between data, business logic, and API layers), input validation, custom error handling, and test-driven verification — not just "it runs," but "it's verified to work."

## Features

- Create, read, update, and delete tasks
- Filter tasks by status (`pending` / `done`)
- Input validation (no empty titles, valid priority levels, valid date formats)
- Custom exceptions for meaningful error messages (`TaskNotFoundError`, `InvalidTaskDataError`)
- REST API built with FastAPI, including interactive auto-generated docs
- 32 automated tests covering both business logic and API endpoints
- Two interfaces on top of the same core logic: a command-line app and a web API

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| API Framework | FastAPI |
| Validation | Pydantic |
| Database | SQLite |
| Testing | pytest, httpx (FastAPI TestClient) |
| Server | Uvicorn |

## Architecture

The project is organized into clear, separated layers, so each piece has a single responsibility:

```
main.py / app.py   →  Entry points (CLI and API) — handle user/HTTP interaction only
task_manager.py    →  Business logic layer — the rules of the application
database.py        →  Persistence layer — all SQL lives here, nowhere else
task.py            →  Domain model — the Task object and its validation rules
schemas.py         →  API request/response contracts (Pydantic models)
exceptions.py       →  Custom exceptions used across all layers
```

This separation means the same `TaskManager` logic powers both the CLI (`main.py`) and the API (`app.py`) without duplication, and the storage engine could be swapped without touching business logic.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/tasks` | List all tasks (optional `?status=pending` or `?status=done` filter) |
| `POST` | `/tasks` | Create a new task |
| `GET` | `/tasks/{id}` | Get a single task by ID |
| `PUT` | `/tasks/{id}` | Update a task |
| `PATCH` | `/tasks/{id}/done` | Mark a task as done |
| `DELETE` | `/tasks/{id}` | Delete a task |

Once running, interactive documentation is available at `http://localhost:8000/docs`.

## Getting Started

**1. Clone the repository**
```bash
git clone https://github.com/dileep1218/TASK-MANAGER.git
cd TASK-MANAGER
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3a. Run the API**
```bash
uvicorn app:app --reload
```
The API will be available at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

**3b. Or run the command-line version**
```bash
python main.py
```

## Running Tests

```bash
pytest
```

This runs the full suite of 32 tests — covering the business logic layer (`TaskManager`) directly, and the API layer through real HTTP requests via FastAPI's TestClient. Each test runs against an isolated, temporary database, so nothing interferes with your actual data.

## Example Request

Creating a task:
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Write report", "priority": "high", "due_date": "2026-06-30"}'
```

Response:
```json
{
  "id": 1,
  "title": "Write report",
  "description": "",
  "priority": "high",
  "status": "pending",
  "due_date": "2026-06-30",
  "created_at": "2026-06-18T05:27:35.734746"
}
```

## What I Learned / Why This Design

This project started as a basic procedural script with everything in one file. I rebuilt it to practice:
- Translating procedural code into proper OOP design
- Separating concerns so logic isn't tangled with storage or presentation
- Writing input validation and custom exceptions instead of letting errors fail silently or crash
- Building a REST API on top of existing business logic without duplicating it
- Writing tests that actually verify behavior, including edge cases like invalid input and missing records

## Possible Future Improvements

- Add user authentication so tasks are scoped per user
- Switch from SQLite to PostgreSQL for production use
- Add pagination for the task list endpoint
- Deploy the API (e.g. Render, Railway) for a live demo link
