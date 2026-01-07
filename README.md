# FastAPI Data Drive Backend - Complete Guide

## Requirements
- Python 3.10
- Postgres
- Docker

## Local Deployment

### Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Create a docker container with Postgres database

```
docker run -d --name db-container-dr -p 5400:5432 -e POSTGRES_DB=dataroom_db -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres postgres:14
```

### Create database migraiton

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply database migrations

```bash
alembic upgrade head
```

### Revert a migration

```bash
alembic downgrade -1
```

### Start the server

```bash
uvicorn main:app --reload
```

The backend docs (Swagger) will be available at `http://127.0.0.1:8000/api/docs`

## Running Tests

### Run all tests
```bash
python -m pytest tests/
```

