"""
Muhasabah & Character Engine
Mercy-oriented self-reflection, private lapse recovery, and Akhlaq cultivation.
No shame mechanics or streak-destruction penalties. Focuses on rapid recovery,
trigger mitigation, tawbah, and character development.
"""

import sqlite3
import json
from datetime import datetime, date
from typing import List, Dict, Any, Optional

AKHLAQ_TRAITS = [
    {"id": "anger_control", "name": "Anger Control", "description": "Pausing before reacting when agitated, making wudu or changing posture."},
    {"id": "guarding_speech", "name": "Guarding Speech", "description": "Refraining from backbiting (gheebah), sarcasm, or idle gossip."},
    {"id": "truthfulness", "name": "Truthfulness", "description": "Strict honesty in speech, commitments, and internal self-honesty."},
    {"id": "patience", "name": "Patience (Sabr)", "description": "Remaining dignified through delays, hardships, and unexpected friction."},
    {"id": "keeping_promises", "name": "Fulfilling Pledges", "description": "Honoring word, meeting deadlines, keeping trusts intact."},
    {"id": "gratitude", "name": "Gratitude (Shukr)", "description": "Acknowledging blessings internally and voicing appreciation to people."},
    {"id": "lowering_ego", "name": "Humility (Tawadu')", "description": "Letting go of the need to always prove oneself right."},
    {"id": "forgiveness", "name": "Forgiveness ('Afw)", "description": "Pardoning small slights and not harboring silent resentment."}
]

class MuhasabahEngine:
    """Handles private lapse reflection, tawbah recovery flow, and Akhlaq logs."""

    def __init__(self, db_path: str = "alisha_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS muhasabah_lapses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT,
                    category TEXT,
                    trigger_context TEXT,
                    action_taken TEXT,
                    repair_plan TEXT,
                    tawbah_completed INTEGER DEFAULT 1,
                    reflection_note TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS akhlaq_reflections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT,
                    trait_id TEXT,
                    observed_behavior TEXT,
                    score_intent INTEGER,
                    growth_note TEXT
                )
            """)
            conn.commit()

    def get_akhlaq_traits(self) -> List[Dict[str, Any]]:
        return AKHLAQ_TRAITS

    def record_lapse_recovery(self, category: str, trigger: str, repair: str, notes: str = "") -> Dict[str, Any]:
        """
        Mercy-oriented recording: focuses on immediate recovery and trigger avoidance.
        """
        now_str = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO muhasabah_lapses (created_at, category, trigger_context, action_taken, repair_plan, tawbah_completed, reflection_note)
                VALUES (?, ?, ?, ?, ?, 1, ?)
            """, (now_str, category, trigger, "Recognized, stopped, and made Istighfar", repair, notes))
            conn.commit()
            lapse_id = cursor.lastrowid

        return {
            "id": lapse_id,
            "success": True,
            "status": "recovered",
            "message": "You slipped. Return now. Continue from here.",
            "guidance": "Prophetic principle: 'Follow an evil deed with a good one to wipe it out' (Jami' at-Tirmidhi 1987).",
            "mercy_reminder": "Prophetic principle: 'Follow an evil deed with a good one to wipe it out' (Jami' at-Tirmidhi 1987)."
        }

    record_lapse = record_lapse_recovery

    def record_akhlaq_reflection(self, trait_id: str, behavior: str, growth_note: str = "") -> Dict[str, Any]:
        now_str = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO akhlaq_reflections (created_at, trait_id, observed_behavior, score_intent, growth_note)
                VALUES (?, ?, ?, 1, ?)
            """, (now_str, trait_id, behavior, growth_note))
            conn.commit()
            ref_id = cursor.lastrowid

        return {
            "id": ref_id,
            "success": True,
            "trait_id": trait_id,
            "recorded_at": now_str
        }

    def get_recent_entries(self, limit: int = 10) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM muhasabah_lapses ORDER BY id DESC LIMIT ?", (limit,))
            lapses = [dict(row) for row in cursor.fetchall()]

            cursor.execute("SELECT * FROM akhlaq_reflections ORDER BY id DESC LIMIT ?", (limit,))
            reflections = [dict(row) for row in cursor.fetchall()]

        return {
            "lapses": lapses,
            "reflections": reflections,
            "akhlaq": reflections,
            "recovery_message": "Mercy is expansive. Focus on the next upright action."
        }
