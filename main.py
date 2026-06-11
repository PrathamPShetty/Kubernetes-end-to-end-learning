import os
import json
import redis
import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Task Manager API")

# Read config from environment (injected via ConfigMap & Secret)
DB_HOST = os.getenv("DB_HOST", "postgres-service")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "taskdb")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "secret")
REDIS_HOST = os.getenv("REDIS_HOST", "redis-service")
APP_ENV = os.getenv("APP_ENV", "development")


def get_db():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )


def get_redis():
    return redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)


class Task(BaseModel):
    title: str
    description: str = ""


@app.on_event("startup")
def startup():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT DEFAULT '',
            done BOOLEAN DEFAULT FALSE
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


# --- Health checks (used by K8s liveness & readiness probes) ---

@app.get("/healthz")
def liveness():
    return {"status": "alive"}


@app.get("/readyz")
def readiness():
    try:
        conn = get_db()
        conn.close()
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="DB not ready")


# --- API endpoints ---

@app.get("/")
def home():
    return {"service": "task-manager", "env": APP_ENV, "version": "v1"}


@app.get("/tasks")
def list_tasks():
    # Check Redis cache first
    r = get_redis()
    cached = r.get("tasks")
    if cached:
        return json.loads(cached)

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, description, done FROM tasks ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    tasks = [{"id": r[0], "title": r[1], "description": r[2], "done": r[3]} for r in rows]

    # Cache for 30 seconds
    r.set("tasks", json.dumps(tasks), ex=30)
    return tasks


@app.post("/tasks", status_code=201)
def create_task(task: Task):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (title, description) VALUES (%s, %s) RETURNING id",
        (task.title, task.description)
    )
    task_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    # Invalidate cache
    get_redis().delete("tasks")
    return {"id": task_id, "title": task.title}


@app.put("/tasks/{task_id}/done")
def mark_done(task_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET done = TRUE WHERE id = %s", (task_id,))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    conn.commit()
    cur.close()
    conn.close()

    get_redis().delete("tasks")
    return {"id": task_id, "done": True}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    conn.commit()
    cur.close()
    conn.close()

    get_redis().delete("tasks")
    return {"deleted": task_id}
