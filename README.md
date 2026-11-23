

# Student Management API

A RESTful CRUD API for managing student records, built with **FastAPI**, **Pydantic**, **SQLAlchemy**, and **PostgreSQL**.

## Features

- Full CRUD: create, read, update, and delete students
- Request validation with Pydantic (types, ranges, string lengths, email format)
- Sorting by `name`, `age`, `course`, or `marks` (ascending or descending)
- Proper HTTP status codes (`201`, `404`, `409`, `422`)
- PostgreSQL persistence through SQLAlchemy ORM
- Dependency injection (`Depends`) for per-request database sessions
- Secrets kept out of the code using environment variables
- Auto-generated interactive docs (Swagger UI and ReDoc)

## Tech Stack

| Layer      | Technology     |
| ---------- | -------------- |
| Framework  | FastAPI        |
| Validation | Pydantic v2    |
| ORM        | SQLAlchemy 2.x |
| Database   | PostgreSQL     |
| Driver     | psycopg (v3)   |
| Config     | python-dotenv  |

## Project Structure

```
Advance-Fastapi/
├── main.py              # FastAPI app and endpoints
├── database.py          # Engine, session, table model, get_db dependency
├── requirements.txt     # Python dependencies
├── .env                 # Local secrets (NOT committed)
├── .env.example         # Template for environment variables
├── Dockerfile           # Container recipe (work in progress)
├── docker-compose.yml   # App + database setup (work in progress)
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10 or newer
- PostgreSQL (with pgAdmin, optional) running locally
- Git

### 1. Clone the repository

```bash
git clone https://github.com/Jawad-Muzafar/Advance-Fastapi.git
cd Advance-Fastapi
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

| Shell              | Activate command                  |
| ------------------ | --------------------------------- |
| Git Bash (Windows) | `source .venv/Scripts/activate` |
| PowerShell         | `.\.venv\Scripts\Activate.ps1`  |
| Linux / macOS      | `source .venv/bin/activate`     |

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Create the database

In pgAdmin (or `psql`), create an empty database, for example `studentdb`.

### 5. Configure environment variables

Copy `.env.example` to `.env` and fill in your values:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/studentdb
```

> Never commit `.env`. It is listed in `.gitignore`.

### 6. Run the server

```bash
fastapi dev main.py
```

The tables are created automatically on startup.

Open the interactive docs at **http://127.0.0.1:8000/docs**.

## API Endpoints

| Method     | Endpoint                         | Description                      |
| ---------- | -------------------------------- | -------------------------------- |
| `POST`   | `/create_student`              | Create a new student             |
| `GET`    | `/students`                    | List all students (with sorting) |
| `GET`    | `/students/{student_id}`       | Get one student by ID            |
| `PATCH`  | `/update_student/{student_id}` | Partially update a student       |
| `DELETE` | `/delete_student/{student_id}` | Delete a student                 |

### Student model

| Field          | Type    | Rules               |
| -------------- | ------- | ------------------- |
| `student_id` | string  | Unique, primary key |
| `name`       | string  | 2 to 50 characters  |
| `age`        | integer | 16 to 30            |
| `course`     | string  | 2 to 50 characters  |
| `email`      | string  | Valid email, unique |
| `marks`      | float   | 0 to 100            |

### Examples

**Create a student**

```http
POST /create_student
```

```json
{
  "student_id": "S001",
  "name": "Jawad",
  "age": 19,
  "course": "OOP",
  "email": "jawad@example.com",
  "marks": 70
}
```

Response `201 Created`:

```json
{ "message": "Student created", "student_id": "S001" }
```

**List students sorted by marks (highest first)**

```http
GET /students?sort_by=marks&sort_order=desc
```

| Query parameter | Allowed values                           | Default  |
| --------------- | ---------------------------------------- | -------- |
| `sort_by`     | `name`, `age`, `course`, `marks` | `name` |
| `sort_order`  | `asc`, `desc`                        | `asc`  |

**Update only the marks**

```http
PATCH /update_student/S001
```

```json
{ "marks": 90 }
```

Only the fields you send are changed.

### Status codes

| Code    | Meaning                                       |
| ------- | --------------------------------------------- |
| `200` | Success                                       |
| `201` | Student created                               |
| `404` | Student not found                             |
| `409` | Student with this ID already exists           |
| `422` | Validation failed (invalid or missing fields) |

## How It Works

```
Request -> FastAPI route -> Pydantic validation -> Depends(get_db)
        -> SQLAlchemy session -> PostgreSQL -> JSON response
```

Each request receives its own database session from `get_db`, which is closed automatically when the request finishes.

## Troubleshooting

| Problem                                       | Fix                                                                 |
| --------------------------------------------- | ------------------------------------------------------------------- |
| `ModuleNotFoundError: psycopg`              | Run `python -m pip install "psycopg[binary]"` inside the venv     |
| `DATABASE_URL` is `None`                  | Check that `.env` exists, is saved, and the variable name matches |
| `password authentication failed`            | Fix the password in `.env`                                        |
| `database "..." does not exist`             | Create the database in pgAdmin; names must match exactly            |
| `relation "students_record" does not exist` | Make sure the tables were created on startup                        |
| Packages install but code cannot find them    | Deactivate conda (`conda deactivate`) and use only the `.venv`  |

## Roadmap

- [ ] Pagination (`page` and `limit`)
- [ ] `response_model` for cleaner responses
- [ ] Authentication (JWT)
- [ ] Database migrations with Alembic
- [ ] Automated tests with pytest
- [ ] Finish Docker setup

## Author

**Jawad Muzafar**
GitHub: [@Jawad-Muzafar](https://github.com/Jawad-Muzafar)

## License

This project is for learning purposes.
