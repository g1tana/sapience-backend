import json
from utils.db import get_db

def create_task(name: str, steps: list):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tasks (name, steps, status)
        VALUES (%s, %s, %s)
    """, (name, json.dumps(steps), "pending"))
    conn.commit()
    conn.close()

def update_task(task_id: int, status: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE tasks SET status = %s WHERE id = %s
    """, (status, task_id))
    conn.commit()
    conn.close()

def get_tasks():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, steps, status FROM tasks ORDER BY id DESC LIMIT 10")
    results = cur.fetchall()
    conn.close()
    return results