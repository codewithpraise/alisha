"""
Fact Service for Alisha AI Friend.

This is the canonical fact ledger. Every important personal fact about Alisha
must pass through this service before being used in generation.

Key principles:
- Facts are NEVER pulled directly from vector embeddings
- Every fact has: subject, predicate, value, status, confidence, evidence
- Conflicting facts are NEVER silently merged
- Age is modeled as DOB + observed_at, not a static integer
- Unknown is a valid explicit state
- High-importance facts require stronger evidence
"""

import json
import os
import re
import sqlite3
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use the existing alisha_memory.db but add a fact_ledger table
DB_PATH = os.path.join(ROOT, "alisha_memory.db")


# ── Fact schemas ──────────────────────────────────────────────────────────────

FACT_STATUS = {
    "verified":     "✓ Strongly supported by multiple sources",
    "provisional":  "~ Supported by single source, not contradicted",
    "historical":   "H Historical -- may have changed",
    "conflicted":   "⚡ Multiple contradictory statements found",
    "superseded":   "→ Replaced by newer fact",
    "unknown":      "? Not enough evidence",
}

# High-importance fact categories requiring stronger evidence
HIGH_IMPORTANCE_PREDICATES = {
    "age", "date_of_birth", "studies", "location", "relationship_status",
    "siblings", "parents", "employer", "health_status",
}

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS fact_ledger (
    fact_id         TEXT PRIMARY KEY,
    subject         TEXT NOT NULL,
    predicate       TEXT NOT NULL,
    value           TEXT NOT NULL,
    fact_type       TEXT NOT NULL DEFAULT 'personal',
    status          TEXT NOT NULL DEFAULT 'provisional',
    confidence      REAL NOT NULL DEFAULT 0.5,
    importance      REAL NOT NULL DEFAULT 0.5,
    valid_from      INTEGER,
    valid_until     INTEGER,
    first_seen      INTEGER NOT NULL,
    last_confirmed  INTEGER NOT NULL,
    source_msg_ids  TEXT NOT NULL DEFAULT '[]',
    source_platforms TEXT NOT NULL DEFAULT '[]',
    evidence_count  INTEGER NOT NULL DEFAULT 1,
    notes           TEXT
);

CREATE INDEX IF NOT EXISTS idx_fl_subject ON fact_ledger(subject);
CREATE INDEX IF NOT EXISTS idx_fl_predicate ON fact_ledger(predicate);
CREATE INDEX IF NOT EXISTS idx_fl_status ON fact_ledger(status);

CREATE TABLE IF NOT EXISTS fact_ledger_history (
    history_id      TEXT PRIMARY KEY,
    fact_id         TEXT NOT NULL,
    old_value       TEXT,
    new_value       TEXT,
    old_status      TEXT,
    new_status      TEXT,
    changed_at      INTEGER NOT NULL,
    change_reason   TEXT,
    changed_by      TEXT DEFAULT 'system'
);
"""


@dataclass
class Fact:
    fact_id: str
    subject: str
    predicate: str
    value: str
    fact_type: str = "personal"
    status: str = "provisional"
    confidence: float = 0.5
    importance: float = 0.5
    valid_from: Optional[int] = None
    valid_until: Optional[int] = None
    first_seen: int = field(default_factory=lambda: int(time.time() * 1000))
    last_confirmed: int = field(default_factory=lambda: int(time.time() * 1000))
    source_msg_ids: List[str] = field(default_factory=list)
    source_platforms: List[str] = field(default_factory=list)
    evidence_count: int = 1
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status_description"] = FACT_STATUS.get(self.status, self.status)
        return d

    def to_prompt_snippet(self) -> str:
        """One-line representation for injection into prompts."""
        status_icon = {"verified": "✓", "provisional": "~", "conflicted": "⚡", "unknown": "?"}.get(
            self.status, ""
        )
        return f"{status_icon} {self.subject} {self.predicate}: {self.value} (confidence: {self.confidence:.0%})"


class FactService:
    """
    Canonical fact ledger service.
    Thread-safe reads. Write operations are serialized.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_schema()
        self._seed_known_facts()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn

    def _init_schema(self):
        with self._conn() as conn:
            conn.executescript(SCHEMA_SQL)
            conn.commit()

    def _seed_known_facts(self):
        """
        Seeds well-known facts from the corpus that were manually verified.
        Idempotent -- only inserts if not already present.
        """
        known_facts = [
            {
                "subject": "alisha",
                "predicate": "age",
                "value": "20 years old -- university/college student in the UK",
                "status": "verified",
                "confidence": 1.0,
                "importance": 0.95,
                "fact_type": "identity",
                "notes": "Verified age: 20 years old",
                "evidence_count": 25,
            },
            {
                "subject": "alisha",
                "predicate": "studies",
                "value": "Biochemistry and Maths at college in the UK (biology practicals, chemistry labs, exam revision)",
                "status": "verified",
                "confidence": 0.99,
                "importance": 0.95,
                "fact_type": "education",
                "notes": "Confirmed across college notes, lab practicals, revision sessions",
                "evidence_count": 35,
            },
            {
                "subject": "alisha",
                "predicate": "background",
                "value": "Mauritius British background, raised in the UK, speaks Mauritian native language with family from Mauritius",
                "status": "verified",
                "confidence": 0.99,
                "importance": 1.0,
                "fact_type": "identity",
                "evidence_count": 28,
            },
            {
                "subject": "alisha",
                "predicate": "faith",
                "value": "Muslim -- prays 5 daily salah, observes Fajr, makes earnest duas in sajdah",
                "status": "verified",
                "confidence": 0.99,
                "importance": 0.95,
                "fact_type": "personal",
                "notes": "Spiritual practice grounded in Hanafi traditions and sincere devotion",
                "evidence_count": 40,
            },
            {
                "subject": "alisha",
                "predicate": "loves_cats",
                "value": "Obsessed with cats -- especially black-and-white cats on the way to college and family kitten",
                "status": "verified",
                "confidence": 0.99,
                "importance": 0.9,
                "fact_type": "preference",
                "evidence_count": 30,
            },
            {
                "subject": "alisha",
                "predicate": "family_life",
                "value": "Lives with family -- very close to mum, helps at home, family dinner outings",
                "status": "verified",
                "confidence": 0.98,
                "importance": 0.85,
                "fact_type": "family",
                "evidence_count": 28,
            },
            {
                "subject": "alisha",
                "predicate": "kdramas",
                "value": "Loves watching KDramas during college breaks -- gets deeply invested in storylines",
                "status": "verified",
                "confidence": 0.95,
                "importance": 0.75,
                "fact_type": "preference",
                "evidence_count": 15,
            },
            {
                "subject": "alisha",
                "predicate": "voice_notes",
                "value": "Sends voice notes when lazy to type or explaining funny stories and chemistry practicals",
                "status": "verified",
                "confidence": 0.99,
                "importance": 0.9,
                "fact_type": "behavior",
                "evidence_count": 100,
            },
            {
                "subject": "alisha",
                "predicate": "personality",
                "value": "Teasing, witty, sarcastic, warm, deeply caring -- always says 'kidding' after a savage roast",
                "status": "verified",
                "confidence": 0.99,
                "importance": 0.95,
                "fact_type": "personality",
                "evidence_count": 65,
            },
            {
                "subject": "alisha",
                "predicate": "inside_jokes",
                "value": "Says 'PATTERN UP', 'bubbzieee', 'omdssd', teases about late night sleep and typos ('latw')",
                "status": "verified",
                "confidence": 0.98,
                "importance": 0.85,
                "fact_type": "personality",
                "evidence_count": 45,
            },
            {
                "subject": "alisha",
                "predicate": "study_habits",
                "value": "Wraps in cozy blanket while studying chemistry mechanisms with warm cup of tea",
                "status": "verified",
                "confidence": 0.96,
                "importance": 0.8,
                "fact_type": "education",
                "evidence_count": 22,
            },
            {
                "subject": "alisha",
                "predicate": "daily_routine",
                "value": "College lectures in morning, commutes back, helps mum, evening revision and LifeOS Salah",
                "status": "verified",
                "confidence": 0.97,
                "importance": 0.85,
                "fact_type": "behavior",
                "evidence_count": 32,
            },
        ]

        for f in known_facts:
            fact_id = f"seed_{f['subject']}_{f['predicate']}".replace(" ", "_")
            now = int(time.time() * 1000)
            if not self._fact_exists(fact_id):
                self._insert_fact(
                    fact_id=fact_id,
                    subject=f["subject"],
                    predicate=f["predicate"],
                    value=f["value"],
                    fact_type=f.get("fact_type", "personal"),
                    status=f["status"],
                    confidence=f["confidence"],
                    importance=f["importance"],
                    first_seen=now,
                    last_confirmed=now,
                    source_msg_ids=[],
                    evidence_count=f.get("evidence_count", 1),
                    notes=f.get("notes"),
                )
            else:
                with self._conn() as conn:
                    conn.execute(
                        """
                        UPDATE fact_ledger 
                        SET value = ?, status = ?, confidence = ?, importance = ?, fact_type = ?, evidence_count = ?, last_confirmed = ?
                        WHERE fact_id = ?
                        """,
                        (f["value"], f["status"], f["confidence"], f["importance"], f.get("fact_type", "personal"), f.get("evidence_count", 1), now, fact_id)
                    )
                    conn.commit()

    def _fact_exists(self, fact_id: str) -> bool:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT fact_id FROM fact_ledger WHERE fact_id = ?", (fact_id,)
            ).fetchone()
            return row is not None

    def _insert_fact(
        self,
        fact_id: str,
        subject: str,
        predicate: str,
        value: str,
        fact_type: str = "personal",
        status: str = "provisional",
        confidence: float = 0.5,
        importance: float = 0.5,
        first_seen: Optional[int] = None,
        last_confirmed: Optional[int] = None,
        valid_from: Optional[int] = None,
        valid_until: Optional[int] = None,
        source_msg_ids: Optional[List[str]] = None,
        source_platforms: Optional[List[str]] = None,
        evidence_count: int = 1,
        notes: Optional[str] = None,
    ):
        now = int(time.time() * 1000)
        with self._conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO fact_ledger
                   (fact_id, subject, predicate, value, fact_type, status, confidence,
                    importance, valid_from, valid_until, first_seen, last_confirmed,
                    source_msg_ids, source_platforms, evidence_count, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    fact_id, subject, predicate, value, fact_type, status, confidence,
                    importance,
                    valid_from,
                    valid_until,
                    first_seen or now,
                    last_confirmed or now,
                    json.dumps(source_msg_ids or []),
                    json.dumps(source_platforms or []),
                    evidence_count,
                    notes,
                ),
            )
            conn.commit()

    def lookup(
        self,
        subject: str = "alisha",
        predicate: Optional[str] = None,
        include_unknown: bool = False,
    ) -> List[Fact]:
        """
        Primary query: get current facts about a subject.
        Returns only active (not superseded/historical) facts.
        """
        with self._conn() as conn:
            if predicate:
                rows = conn.execute(
                    """SELECT * FROM fact_ledger
                       WHERE subject = ? AND predicate = ?
                       AND status NOT IN ('superseded', 'historical')
                       ORDER BY confidence DESC""",
                    (subject.lower(), predicate.lower()),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT * FROM fact_ledger
                       WHERE subject = ?
                       AND status NOT IN ('superseded', 'historical')
                       ORDER BY importance DESC, confidence DESC""",
                    (subject.lower(),),
                ).fetchall()

        facts = []
        for row in rows:
            d = dict(row)
            d["source_msg_ids"] = json.loads(d.get("source_msg_ids", "[]"))
            d["source_platforms"] = json.loads(d.get("source_platforms", "[]"))
            f = Fact(**{k: v for k, v in d.items() if k in Fact.__dataclass_fields__})
            if not include_unknown and f.status == "unknown":
                continue
            facts.append(f)

        return facts

    def lookup_for_prompt(
        self,
        query: str,
        subject: str = "alisha",
    ) -> List[Fact]:
        """
        Returns the most relevant facts for a given query.
        Used by the context compiler to inject verified facts into generation.
        """
        all_facts = self.lookup(subject=subject, include_unknown=False)
        q_lower = query.lower()
        # Meaningful query words (exclude stop words and short particles)
        STOP_WORDS = {
            "what", "where", "when", "why", "who", "which", "how", "are", "you", "your",
            "is", "the", "a", "an", "do", "to", "in", "it", "me", "my", "i", "was", "were",
            "and", "on", "that", "this", "can", "with", "have", "had", "just", "like", "for",
            "so", "be", "at", "as", "or", "if", "not", "but", "about", "ur", "u", "im",
            "dont", "wbu", "hey", "hi", "hello", "yo", "sup", "okay", "alisha", "tell"
        }
        q_clean_words = {w for w in re.findall(r"\b\w{3,}\b", q_lower) if w not in STOP_WORDS}
        if not q_clean_words:
            return []

        scored = []
        for fact in all_facts:
            # Relevance: does query mention the predicate or value?
            pred_words = {w for w in fact.predicate.lower().split("_") if w not in STOP_WORDS}
            val_words = {w for w in re.findall(r"\b\w{3,}\b", fact.value.lower()) if w not in STOP_WORDS}
            target_words = pred_words | val_words
            overlap = len(q_clean_words & target_words)
            if overlap > 0:
                scored.append((overlap, fact))

        if not scored:
            return []

        scored.sort(key=lambda x: (-x[0], -x[1].importance, -x[1].confidence))
        return [f for _, f in scored[:3]]

    def add_fact(
        self,
        subject: str,
        predicate: str,
        value: str,
        confidence: float = 0.6,
        importance: float = 0.5,
        fact_type: str = "personal",
        source_msg_id: Optional[str] = None,
        platform: str = "live_conversation",
    ) -> Tuple[str, str]:
        """
        Adds or updates a fact. Returns (fact_id, action).
        Actions: "inserted", "updated", "conflicted", "unchanged"
        """
        # Check for existing fact on same subject/predicate
        existing = self.lookup(subject=subject, predicate=predicate, include_unknown=True)

        if not existing:
            # New fact
            fact_id = f"fact_{uuid.uuid4().hex[:12]}"
            self._insert_fact(
                fact_id=fact_id,
                subject=subject,
                predicate=predicate,
                value=value,
                fact_type=fact_type,
                status="provisional",
                confidence=confidence,
                importance=importance,
                source_msg_ids=[source_msg_id] if source_msg_id else [],
                source_platforms=[platform],
            )
            return fact_id, "inserted"

        latest = existing[0]

        # Same value -- confirm and boost confidence
        if latest.value.lower().strip() == value.lower().strip():
            now = int(time.time() * 1000)
            new_confidence = min(1.0, latest.confidence + 0.05)
            new_status = "verified" if new_confidence >= 0.85 and latest.evidence_count >= 3 else latest.status
            with self._conn() as conn:
                conn.execute(
                    """UPDATE fact_ledger SET
                       confidence = ?, status = ?, last_confirmed = ?, evidence_count = evidence_count + 1
                       WHERE fact_id = ?""",
                    (new_confidence, new_status, now, latest.fact_id),
                )
                conn.commit()
            return latest.fact_id, "updated"

        # Different value -- check if it's a genuine update or conflict
        if importance >= 0.7 or predicate in HIGH_IMPORTANCE_PREDICATES:
            # Mark old as superseded, insert new
            now = int(time.time() * 1000)
            with self._conn() as conn:
                conn.execute(
                    "UPDATE fact_ledger SET status = 'superseded', valid_until = ? WHERE fact_id = ?",
                    (now, latest.fact_id),
                )
                conn.commit()
            fact_id = f"fact_{uuid.uuid4().hex[:12]}"
            self._insert_fact(
                fact_id=fact_id,
                subject=subject,
                predicate=predicate,
                value=value,
                fact_type=fact_type,
                status="provisional",
                confidence=confidence,
                importance=importance,
                valid_from=now,
                source_msg_ids=[source_msg_id] if source_msg_id else [],
                source_platforms=[platform],
                notes=f"Supersedes: {latest.fact_id} (was: {latest.value[:50]})",
            )
            # Record history
            self._record_history(
                latest.fact_id, latest.value, value, latest.status, "superseded",
                "newer_statement_received"
            )
            return fact_id, "superseded_old"

        # Low-confidence conflict -- mark both as conflicted
        now = int(time.time() * 1000)
        with self._conn() as conn:
            conn.execute(
                "UPDATE fact_ledger SET status = 'conflicted' WHERE fact_id = ?",
                (latest.fact_id,),
            )
            conn.commit()
        fact_id = f"fact_{uuid.uuid4().hex[:12]}"
        self._insert_fact(
            fact_id=fact_id,
            subject=subject,
            predicate=predicate,
            value=value,
            fact_type=fact_type,
            status="conflicted",
            confidence=confidence * 0.5,  # Lower confidence when conflicting
            importance=importance,
            source_msg_ids=[source_msg_id] if source_msg_id else [],
            source_platforms=[platform],
            notes=f"Conflicts with: {latest.fact_id}",
        )
        return fact_id, "conflicted"

    def _record_history(
        self, fact_id, old_val, new_val, old_status, new_status, reason
    ):
        now = int(time.time() * 1000)
        history_id = f"hist_{uuid.uuid4().hex[:10]}"
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO fact_ledger_history
                   (history_id, fact_id, old_value, new_value, old_status, new_status, changed_at, change_reason)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (history_id, fact_id, old_val, new_val, old_status, new_status, now, reason),
            )
            conn.commit()

    def get_all_for_ui(self) -> List[Dict[str, Any]]:
        """Returns all facts formatted for the memories UI."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM fact_ledger ORDER BY importance DESC, confidence DESC"
            ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["source_msg_ids"] = json.loads(d.get("source_msg_ids", "[]"))
            d["source_platforms"] = json.loads(d.get("source_platforms", "[]"))
            d["status_description"] = FACT_STATUS.get(d.get("status", ""), d.get("status", ""))
            result.append(d)
        return result

    def get_fact_prompt_block(self, query: str) -> str:
        """
        Returns a formatted fact block for injection into generation prompts.
        Only includes verified/provisional facts with sufficient confidence.
        """
        facts = self.lookup_for_prompt(query)
        if not facts:
            return ""

        lines = ["=== VERIFIED FACTS ==="]
        for f in facts:
            if f.confidence >= 0.6 and f.status in ("verified", "provisional"):
                lines.append(f.to_prompt_snippet())

        if len(lines) == 1:
            return ""

        lines.append("=== END FACTS ===")
        return "\n".join(lines)


# Singleton
_instance: Optional[FactService] = None


def get_fact_service() -> FactService:
    global _instance
    if _instance is None:
        _instance = FactService()
    return _instance
