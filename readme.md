#  FastAPI Task Manager API

A simple and scalable **Task Management API** built with **FastAPI**, designed to demonstrate clean architecture, RESTful principles, and modern Python backend development.

---

##  Overview

This project is a backend API for managing tasks. It allows users to create, read, update, and delete tasks efficiently using FastAPI.

It is designed as a **learning project** and a **portfolio-ready backend service** showcasing:

* API development with FastAPI
* Clean project structure
* Dependency management using virtual environments
* RESTful API design

---

##  Features

*  Create tasks
*  Retrieve all tasks
*  Get a single task by ID
*  Update tasks
*  Delete tasks
*  Fast performance with FastAPI
*  Automatic API docs (Swagger & ReDoc)

---

##  Tech Stack

* **Python 3.8+**
* **FastAPI**
* **Uvicorn** (ASGI server)
* **Pydantic** (data validation)

---

##  Project Structure

```
FastAPI-Task-Manager/
│── main.py          # Entry point of the application
│── models.py        # Data models (if applicable)
│── routes/          # API route definitions
│── venv/            # Virtual environment (ignored in production)
│── requirements.txt # Dependencies
```

---

##  Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/Adreen-99/FastAPI-Task-Manager-.git
cd FastAPI-Task-Manager-
```

### 2. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

##  Running the Application

```bash
python -m uvicorn main:app --reload
```

App will be available at:

 http://127.0.0.1:8000

---

##  API Documentation

FastAPI automatically generates interactive docs:

* UI:
   http://127.0.0.1:8000/docs

* ReDoc:
   http://127.0.0.1:8000/redoc

---

##  Example Endpoints

| Method | Endpoint      | Description       |
| ------ | ------------- | ----------------- |
| GET    | `/tasks`      | Get all tasks     |
| POST   | `/tasks`      | Create a task     |
| GET    | `/tasks/{id}` | Get a single task |
| PUT    | `/tasks/{id}` | Update a task     |
| DELETE | `/tasks/{id}` | Delete a task     |

---

##  Testing the API

You can test the API using:

* Swagger UI (`/docs`)
* Postman
* Curl

---

##  Common Issues

### 1. ModuleNotFoundError (FastAPI not found)

Make sure your virtual environment is activated:

```bash
source venv/bin/activate
```

### 2. Wrong Python Environment

Always run:

```bash
python -m uvicorn main:app --reload
```

---

##  Future Improvements

* Add database integration (PostgreSQL / SQLite)
* User authentication (JWT)
* Task categories & priorities
* Deployment (Docker + Cloud)
* Unit and integration tests

---

##  Contributing

Contributions are welcome!

1. Fork the repo
2. Create a new branch
3. Commit your changes
4. Push and open a Pull Request

---

##  License

This project is open-source and available under the **MIT License**.

---

##  Author

**Adreen Githinji**

* GitHub: https://github.com/Adreen-99

---

