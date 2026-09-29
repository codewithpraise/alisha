"""
LifeEngine — Persistent Simulated Life State for Alisha.

Maintains ongoing daily simulation continuity without contaminating the historical Fact Ledger.
Separates:
- TYPE 2: SOURCE-GROUNDED ALISHA KNOWLEDGE (stored in fact_ledger, immutable historical facts)
- TYPE 3: SIMULATED CURRENT LIFE (stored in life_events, ongoing small mundane day experiences)

Constraints:
- Mundane, plausible daily routines only.
- Never fabricates major life crises, deaths, exam results, or fake historical claims.
- Never written to fact_ledger.
"""

import json
import os
import sqlite3
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(ROOT, "alisha_memory.db")


@dataclass
class LifeEvent:
    event_id: str
    timestamp_ms: int
    simulated_day: str
    text: str
    topic_tags: List[str]
    energy: float
    people: List[str]
    source_domain: str
    simulation_generation_id: str
    status: str = "active"  # "active", "resolved", "archived"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


class LifeEngine:
    """
    Simulates ongoing mundane life events and daily state.
    Persists state into the 'life_events' table in alisha_memory.db.
    """

    DOMAINS = [
        "uni_routine",
        "commute",
        "meals",
        "family",
        "cats",
        "revision",
        "weather",
        "chores",
        "general_observation",
    ]

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_table()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_table(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS life_events (
                    event_id TEXT PRIMARY KEY,
                    timestamp_ms INTEGER NOT NULL,
                    simulated_day TEXT NOT NULL,
                    text TEXT NOT NULL,
                    topic_tags TEXT NOT NULL,
                    energy REAL NOT NULL,
                    people TEXT NOT NULL,
                    source_domain TEXT NOT NULL,
                    simulation_generation_id TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active'
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_life_events_ts ON life_events(timestamp_ms)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_life_events_status ON life_events(status)
            """)
            conn.commit()

    def get_current_routine_phase(self, hour: Optional[int] = None) -> Tuple[str, str, float]:
        """
        Returns (phase_name, description, default_energy) based on local/simulated time.
        """
        if hour is None:
            hour = datetime.now().hour

        if 0 <= hour < 5:
            return "late_night", "late night winding down / sleepy / browsing phone in bed", 0.35
        elif 5 <= hour < 9:
            return "early_morning", "morning routine / getting ready / waking up", 0.5
        elif 9 <= hour < 14:
            return "daytime_college", "daytime college / classes / revision / in library", 0.7
        elif 14 <= hour < 18:
            return "afternoon_commute", "afternoon commute / errands / heading back", 0.6
        elif 18 <= hour < 21:
            return "evening_home", "evening at home / dinner / tea / family time", 0.75
        else:
            return "night_relax", "night time relaxing / cozy / chatting with friends", 0.65

    def get_active_events(self, limit: int = 3) -> List[LifeEvent]:
        """Fetches active simulated events from SQLite."""
        events = []
        with self._get_connection() as conn:
            cur = conn.execute(
                "SELECT * FROM life_events WHERE status = 'active' ORDER BY timestamp_ms DESC LIMIT ?",
                (limit,)
            )
            for row in cur.fetchall():
                events.append(LifeEvent(
                    event_id=row["event_id"],
                    timestamp_ms=row["timestamp_ms"],
                    simulated_day=row["simulated_day"],
                    text=row["text"],
                    topic_tags=json.loads(row["topic_tags"]),
                    energy=float(row["energy"]),
                    people=json.loads(row["people"]),
                    source_domain=row["source_domain"],
                    simulation_generation_id=row["simulation_generation_id"],
                    status=row["status"],
                ))
        return events

    def add_simulated_event(
        self,
        text: str,
        source_domain: str = "general_observation",
        topic_tags: Optional[List[str]] = None,
        energy: float = 0.6,
        people: Optional[List[str]] = None,
    ) -> LifeEvent:
        """
        Adds a new simulated life event.
        STRICT GUARANTEE: Never writes to fact_ledger table.
        """
        event_id = f"sim_{uuid.uuid4().hex[:10]}"
        now_ms = int(time.time() * 1000)
        day_str = datetime.now().strftime("%A")
        tags = topic_tags or [source_domain]
        ppl = people or []

        event = LifeEvent(
            event_id=event_id,
            timestamp_ms=now_ms,
            simulated_day=day_str,
            text=text.strip(),
            topic_tags=tags,
            energy=energy,
            people=ppl,
            source_domain=source_domain,
            simulation_generation_id=f"gen_{int(time.time())}",
            status="active"
        )

        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO life_events (
                    event_id, timestamp_ms, simulated_day, text,
                    topic_tags, energy, people, source_domain,
                    simulation_generation_id, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_id,
                event.timestamp_ms,
                event.simulated_day,
                event.text,
                json.dumps(event.topic_tags),
                event.energy,
                json.dumps(event.people),
                event.source_domain,
                event.simulation_generation_id,
                event.status,
            ))
            conn.commit()

        return event

    def resolve_event(self, event_id: str):
        """Marks a simulated event as resolved/completed."""
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE life_events SET status = 'resolved' WHERE event_id = ?",
                (event_id,)
            )
            conn.commit()

    def get_simulation_prompt_block(self) -> str:
        """
        Builds a compact simulation context block for the LLM prompt.
        Explicitly demarcated as current ongoing situation, NOT historical fact.
        """
        phase, desc, energy = self.get_current_routine_phase()
        active_events = self.get_active_events(limit=2)

        lines = [
            f"[SIMULATED LIFE STATE — Current Routine: {desc}]"
        ]
        if active_events:
            for ev in active_events:
                lines.append(f"- Ongoing note: {ev.text}")

        return "\n".join(lines)


# Singleton
_engine: Optional[LifeEngine] = None

def get_life_engine() -> LifeEngine:
    global _engine
    if _engine is None:
        _engine = LifeEngine()
    return _engine
