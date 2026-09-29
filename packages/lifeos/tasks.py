"""
Daily Tasks & Focus Execution Engine
Enforces a mandatory 'One-Liner Execution Path' for every task to prevent distraction
and preserve razor-sharp focus throughout the day.
"""

import sqlite3
from datetime import datetime, date
from typing import List, Dict, Any, Optional


DEFAULT_TASKS = [
    {
        "id": "task_1",
        "title": "Review Organic Chemistry Reaction Mechanisms",
        "one_liner": "Open notebook page 28, draw 4 nucleophilic substitution mechanisms once without looking, close tab.",
        "priority": "high",
        "completed": False,
        "est_minutes": 25,
        "created_at": datetime.now().isoformat()
    },
    {
        "id": "task_2",
        "title": "Daily 15-Minute Quran & Tafsir Study",
        "one_liner": "Open Surah Al-Mulk, read 10 ayat with classical Hanafi commentary, extract one action rule.",
        "priority": "high",
        "completed": False,
        "est_minutes": 15,
        "created_at": datetime.now().isoformat()
    },
    {
        "id": "task_3",
        "title": "Physical Exercise & Mobility",
        "one_liner": "30 pushups, 40 squats, 5 min hamstring stretches before Maghrib without looking at phone.",
        "priority": "medium",
        "completed": False,
        "est_minutes": 20,
        "created_at": datetime.now().isoformat()
    }
]


class TaskManager:
    """Manages daily tasks and distraction-shield execution rules."""

    def __init__(self, db_path: str = "alisha_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS daily_tasks (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        one_liner TEXT NOT NULL,
                        priority TEXT DEFAULT 'medium',
                        completed INTEGER DEFAULT 0,
                        est_minutes INTEGER DEFAULT 15,
                        created_date TEXT,
                        updated_at TEXT
                    )
                """)
                conn.commit()

                # Seed default tasks if empty
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM daily_tasks")
                if cur.fetchone()[0] == 0:
                    today_str = date.today().isoformat()
                    for t in DEFAULT_TASKS:
                        cur.execute(
                            "INSERT INTO daily_tasks (id, title, one_liner, priority, completed, est_minutes, created_date, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (t["id"], t["title"], t["one_liner"], t["priority"], int(t["completed"]), t["est_minutes"], today_str, t["created_at"])
                        )
                    conn.commit()
        except Exception:
            pass

    def get_tasks(self, task_date: Optional[str] = None) -> List[Dict[str, Any]]:
        target_date = task_date or date.today().isoformat()
        tasks = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT id, title, one_liner, priority, completed, est_minutes FROM daily_tasks ORDER BY completed ASC, id DESC")
                for row in cur.fetchall():
                    tasks.append({
                        "id": row[0],
                        "title": row[1],
                        "one_liner": row[2],
                        "priority": row[3],
                        "completed": bool(row[4]),
                        "est_minutes": row[5]
                    })
        except Exception:
            tasks = list(DEFAULT_TASKS)
        return tasks

    def get_tasks_for_date(self, task_date: Optional[str] = None) -> Dict[str, Any]:
        tasks = self.get_tasks(task_date)
        total = len(tasks)
        completed = sum(1 for t in tasks if t.get("completed"))
        return {
            "tasks": tasks,
            "summary": {
                "total": total,
                "completed": completed,
                "pending": total - completed,
                "est_minutes_total": sum(t.get("est_minutes", 15) for t in tasks),
                "completion_rate": int((completed / total) * 100) if total > 0 else 0
            }
        }

    def add_task(self, title: str, one_liner: str, category: str = "general", priority: str = "medium", est_minutes: int = 15, task_date: Optional[str] = None, estimated_mins: Optional[int] = None) -> Dict[str, Any]:
        task_id = f"task_{int(datetime.now().timestamp() * 1000)}"
        today_str = task_date or date.today().isoformat()
        now_str = datetime.now().isoformat()
        actual_mins = estimated_mins if estimated_mins is not None else est_minutes

        clean_title = title.strip()
        clean_one_liner = one_liner.strip() or "Execute step with full presence and zero tab-switching."

        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO daily_tasks (id, title, one_liner, priority, completed, est_minutes, created_date, updated_at) VALUES (?, ?, ?, ?, 0, ?, ?, ?)",
                    (task_id, clean_title, clean_one_liner, priority, est_minutes, today_str, now_str)
                )
                conn.commit()
        except Exception:
            pass

        return {
            "id": task_id,
            "title": clean_title,
            "one_liner": clean_one_liner,
            "category": category,
            "priority": priority,
            "completed": False,
            "est_minutes": est_minutes
        }

    def toggle_task(self, task_id: Any) -> Dict[str, Any]:
        str_id = str(task_id)
        now_str = datetime.now().isoformat()
        new_status = False
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT completed FROM daily_tasks WHERE id = ?", (str_id,))
                row = cur.fetchone()
                if row:
                    new_status = not bool(row[0])
                    cur.execute(
                        "UPDATE daily_tasks SET completed = ?, updated_at = ? WHERE id = ?",
                        (int(new_status), now_str, str_id)
                    )
                    conn.commit()
        except Exception:
            pass

        return {"id": str_id, "completed": new_status}

    def delete_task(self, task_id: Any) -> bool:
        str_id = str(task_id)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM daily_tasks WHERE id = ?", (str_id,))
                conn.commit()
                return True
        except Exception:
            return False
