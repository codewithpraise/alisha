"""
SQLite + FTS5 Memory Storage for Alisha Bubbzieee.
Implements:
- Structured entities: messages, facts, episodes, relationships, style_examples
- FTS5 virtual tables for BM25 lexical search
- Provenance enforcement (source_message_id)
- Temporal fact updates (valid_from, valid_until) without destroying historical records
- Stale memory suppression
"""

import json
import os
import sqlite3
import time
from typing import List, Dict, Any, Optional


SCHEMA_SQL = """
-- 1. Messages table
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    sender TEXT NOT NULL,
    text TEXT NOT NULL,
    source_index INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_ts ON messages(timestamp);

-- FTS5 for messages
CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
    id UNINDEXED,
    text,
    tokenize='porter unicode61'
);

-- 2. Structured Facts with Provenance & Temporal validity
CREATE TABLE IF NOT EXISTS facts (
    id TEXT PRIMARY KEY,
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object TEXT NOT NULL,
    confidence REAL NOT NULL DEFAULT 1.0,
    importance REAL NOT NULL DEFAULT 0.5,
    first_seen INTEGER NOT NULL,
    last_confirmed INTEGER NOT NULL,
    valid_from INTEGER NOT NULL,
    valid_until INTEGER,               -- NULL means currently active
    source_message_id TEXT             -- Provenance link
);
CREATE INDEX IF NOT EXISTS idx_facts_subject ON facts(subject);
CREATE INDEX IF NOT EXISTS idx_facts_validity ON facts(valid_from, valid_until);

-- FTS5 for facts
CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts USING fts5(
    id UNINDEXED,
    subject,
    predicate,
    object,
    tokenize='porter unicode61'
);

-- 3. Episode Memory
CREATE TABLE IF NOT EXISTS episodes (
    id TEXT PRIMARY KEY,
    start_timestamp INTEGER NOT NULL,
    end_timestamp INTEGER NOT NULL,
    summary TEXT NOT NULL,
    importance REAL NOT NULL DEFAULT 0.5,
    confidence REAL NOT NULL DEFAULT 1.0,
    source_start_message_id TEXT,
    source_end_message_id TEXT
);
CREATE INDEX IF NOT EXISTS idx_episodes_ts ON episodes(start_timestamp);

-- FTS5 for episodes
CREATE VIRTUAL TABLE IF NOT EXISTS episodes_fts USING fts5(
    id UNINDEXED,
    summary,
    tokenize='porter unicode61'
);

-- 4. Relationships
CREATE TABLE IF NOT EXISTS relationships (
    id TEXT PRIMARY KEY,
    subject TEXT NOT NULL,
    relation TEXT NOT NULL,
    object TEXT NOT NULL,
    confidence REAL NOT NULL DEFAULT 1.0,
    first_seen INTEGER NOT NULL,
    last_confirmed INTEGER NOT NULL,
    source_message_id TEXT
);
CREATE INDEX IF NOT EXISTS idx_rel_subject ON relationships(subject);

-- 5. Style Examples (Real Historical Exemplars)
CREATE TABLE IF NOT EXISTS style_examples (
    id TEXT PRIMARY KEY,
    mode TEXT NOT NULL,                -- neutral, playful, teasing, affectionate, serious, comforting, explanatory, annoyed
    text TEXT NOT NULL,
    source_message_id TEXT,
    confidence REAL NOT NULL DEFAULT 1.0,
    importance REAL NOT NULL DEFAULT 0.5
);
CREATE INDEX IF NOT EXISTS idx_style_mode ON style_examples(mode);

-- FTS5 for style examples
CREATE VIRTUAL TABLE IF NOT EXISTS style_examples_fts USING fts5(
    id UNINDEXED,
    text,
    tokenize='porter unicode61'
);

-- 6. Compact local vector embeddings for memories/facts
CREATE TABLE IF NOT EXISTS entity_embeddings (
    entity_id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    vector_json TEXT NOT NULL
);
"""


class MemoryDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_database(self):
        with self.get_connection() as conn:
            statements = [
                """CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT,
                    timestamp INTEGER,
                    sender TEXT,
                    text TEXT,
                    source_index INTEGER
                );""",
                "CREATE INDEX IF NOT EXISTS idx_messages_ts ON messages(timestamp);",
                """CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
                    id UNINDEXED,
                    text,
                    tokenize='porter unicode61'
                );""",
                """CREATE TABLE IF NOT EXISTS facts (
                    id TEXT PRIMARY KEY,
                    subject TEXT NOT NULL,
                    predicate TEXT NOT NULL,
                    object TEXT NOT NULL,
                    confidence REAL NOT NULL DEFAULT 1.0,
                    importance REAL NOT NULL DEFAULT 0.5,
                    first_seen INTEGER NOT NULL,
                    last_confirmed INTEGER NOT NULL,
                    valid_from INTEGER NOT NULL,
                    valid_until INTEGER,
                    source_message_id TEXT
                );""",
                "CREATE INDEX IF NOT EXISTS idx_facts_subject ON facts(subject);",
                "CREATE INDEX IF NOT EXISTS idx_facts_validity ON facts(valid_from, valid_until);",
                """CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts USING fts5(
                    id UNINDEXED,
                    subject,
                    predicate,
                    object,
                    tokenize='porter unicode61'
                );""",
                """CREATE TABLE IF NOT EXISTS episodes (
                    id TEXT PRIMARY KEY,
                    start_timestamp INTEGER NOT NULL,
                    end_timestamp INTEGER NOT NULL,
                    summary TEXT NOT NULL,
                    importance REAL NOT NULL DEFAULT 0.5,
                    confidence REAL NOT NULL DEFAULT 1.0,
                    source_start_message_id TEXT,
                    source_end_message_id TEXT
                );""",
                "CREATE INDEX IF NOT EXISTS idx_episodes_ts ON episodes(start_timestamp);",
                """CREATE VIRTUAL TABLE IF NOT EXISTS episodes_fts USING fts5(
                    id UNINDEXED,
                    summary,
                    tokenize='porter unicode61'
                );""",
                """CREATE TABLE IF NOT EXISTS relationships (
                    id TEXT PRIMARY KEY,
                    subject TEXT NOT NULL,
                    relation TEXT NOT NULL,
                    object TEXT NOT NULL,
                    confidence REAL NOT NULL DEFAULT 1.0,
                    first_seen INTEGER NOT NULL,
                    last_confirmed INTEGER NOT NULL,
                    source_message_id TEXT
                );""",
                "CREATE INDEX IF NOT EXISTS idx_rel_subject ON relationships(subject);",
                """CREATE TABLE IF NOT EXISTS style_examples (
                    id TEXT PRIMARY KEY,
                    mode TEXT NOT NULL,
                    text TEXT NOT NULL,
                    source_message_id TEXT,
                    confidence REAL NOT NULL DEFAULT 1.0,
                    importance REAL NOT NULL DEFAULT 0.5
                );""",
                "CREATE INDEX IF NOT EXISTS idx_style_mode ON style_examples(mode);",
                """CREATE VIRTUAL TABLE IF NOT EXISTS style_examples_fts USING fts5(
                    id UNINDEXED,
                    text,
                    tokenize='porter unicode61'
                );""",
                """CREATE TABLE IF NOT EXISTS entity_embeddings (
                    entity_id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    vector_json TEXT NOT NULL
                );"""
            ]
            for stmt in statements:
                try:
                    conn.execute(stmt)
                except Exception:
                    pass

            # Safe index creation for conversation_id if column exists
            try:
                cur = conn.execute("PRAGMA table_info(messages)")
                cols = [r["name"] for r in cur.fetchall()]
                if "conversation_id" in cols:
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id);")
            except Exception:
                pass
            conn.commit()

    # ---------------- Messages ----------------
    def insert_message(
        self,
        msg_id: str,
        conversation_id: str,
        timestamp: int,
        sender: str,
        text: str,
        source_index: int,
    ):
        with self.get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO messages 
                   (id, conversation_id, timestamp, sender, text, source_index)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (msg_id, conversation_id, timestamp, sender, text, source_index),
            )
            # FTS5 insert or replace
            conn.execute("DELETE FROM messages_fts WHERE id = ?", (msg_id,))
            conn.execute(
                "INSERT INTO messages_fts (id, text) VALUES (?, ?)",
                (msg_id, text),
            )
            conn.commit()

    def get_recent_messages(self, limit: int = 10, conversation_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            if conversation_id:
                cursor = conn.execute(
                    "SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp DESC LIMIT ?",
                    (conversation_id, limit),
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM messages ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                )
            rows = cursor.fetchall()
            messages = [dict(r) for r in reversed(rows)]
            return messages

    # ---------------- Facts with Temporal Versioning & Provenance ----------------
    def insert_fact(
        self,
        fact_id: str,
        subject: str,
        predicate: str,
        obj: str,
        confidence: float = 1.0,
        importance: float = 0.5,
        first_seen: Optional[int] = None,
        last_confirmed: Optional[int] = None,
        valid_from: Optional[int] = None,
        valid_until: Optional[int] = None,
        source_message_id: Optional[str] = None,
    ):
        now = int(time.time() * 1000)
        fs = first_seen if first_seen is not None else now
        lc = last_confirmed if last_confirmed is not None else now
        vf = valid_from if valid_from is not None else now

        with self.get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO facts
                   (id, subject, predicate, object, confidence, importance, first_seen, last_confirmed, valid_from, valid_until, source_message_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (fact_id, subject, predicate, obj, confidence, importance, fs, lc, vf, valid_until, source_message_id),
            )
            conn.execute("DELETE FROM facts_fts WHERE id = ?", (fact_id,))
            conn.execute(
                "INSERT INTO facts_fts (id, subject, predicate, object) VALUES (?, ?, ?, ?)",
                (fact_id, subject, predicate, obj),
            )
            conn.commit()

    def update_fact_temporally(
        self,
        old_fact_id: str,
        new_fact_id: str,
        new_obj: str,
        effective_timestamp: int,
        confidence: float = 1.0,
        importance: float = 0.5,
        source_message_id: Optional[str] = None,
    ) -> bool:
        """
        Implements temporal fact update without destroying historical records.
        Sets old_fact.valid_until = effective_timestamp.
        Inserts new_fact with valid_from = effective_timestamp.
        """
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM facts WHERE id = ?", (old_fact_id,))
            old_row = cursor.fetchone()
            if not old_row:
                return False

            # 1. Expire old fact
            conn.execute(
                "UPDATE facts SET valid_until = ?, last_confirmed = ? WHERE id = ?",
                (effective_timestamp, effective_timestamp, old_fact_id),
            )

            # 2. Insert new fact
            subj = old_row["subject"]
            pred = old_row["predicate"]
            conn.execute(
                """INSERT INTO facts
                   (id, subject, predicate, object, confidence, importance, first_seen, last_confirmed, valid_from, valid_until, source_message_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?)""",
                (new_fact_id, subj, pred, new_obj, confidence, importance, effective_timestamp, effective_timestamp, effective_timestamp, source_message_id),
            )
            conn.execute(
                "INSERT INTO facts_fts (id, subject, predicate, object) VALUES (?, ?, ?, ?)",
                (new_fact_id, subj, pred, new_obj),
            )
            conn.commit()
            return True

    def get_active_facts(self, subject: Optional[str] = None, at_timestamp: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Suppresses stale memories: returns only facts where valid_from <= at_timestamp
        and (valid_until IS NULL OR valid_until > at_timestamp).
        """
        now = at_timestamp if at_timestamp is not None else int(time.time() * 1000)
        with self.get_connection() as conn:
            query = """
                SELECT * FROM facts 
                WHERE valid_from <= ? AND (valid_until IS NULL OR valid_until > ?)
            """
            params: List[Any] = [now, now]
            if subject:
                query += " AND subject = ?"
                params.append(subject)
            query += " ORDER BY importance DESC, last_confirmed DESC"

            cursor = conn.execute(query, params)
            return [dict(r) for r in cursor.fetchall()]

    def get_fact_history(self, subject: str, predicate: str) -> List[Dict[str, Any]]:
        """
        Returns full historical chain of a fact's updates across time.
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM facts WHERE subject = ? AND predicate = ? ORDER BY valid_from ASC",
                (subject, predicate),
            )
            return [dict(r) for r in cursor.fetchall()]

    # ---------------- Episodes ----------------
    def insert_episode(
        self,
        episode_id: str,
        start_timestamp: int,
        end_timestamp: int,
        summary: str,
        importance: float = 0.5,
        confidence: float = 1.0,
        source_start_message_id: Optional[str] = None,
        source_end_message_id: Optional[str] = None,
    ):
        with self.get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO episodes
                   (id, start_timestamp, end_timestamp, summary, importance, confidence, source_start_message_id, source_end_message_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (episode_id, start_timestamp, end_timestamp, summary, importance, confidence, source_start_message_id, source_end_message_id),
            )
            conn.execute("DELETE FROM episodes_fts WHERE id = ?", (episode_id,))
            conn.execute(
                "INSERT INTO episodes_fts (id, summary) VALUES (?, ?)",
                (episode_id, summary),
            )
            conn.commit()

    def get_episodes(self, limit: int = 5) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM episodes ORDER BY start_timestamp DESC LIMIT ?",
                (limit,),
            )
            return [dict(r) for r in cursor.fetchall()]

    # ---------------- Relationships ----------------
    def insert_relationship(
        self,
        rel_id: str,
        subject: str,
        relation: str,
        obj: str,
        confidence: float = 1.0,
        first_seen: Optional[int] = None,
        last_confirmed: Optional[int] = None,
        source_message_id: Optional[str] = None,
    ):
        now = int(time.time() * 1000)
        fs = first_seen if first_seen is not None else now
        lc = last_confirmed if last_confirmed is not None else now
        with self.get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO relationships
                   (id, subject, relation, object, confidence, first_seen, last_confirmed, source_message_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (rel_id, subject, relation, obj, confidence, fs, lc, source_message_id),
            )
            conn.commit()

    def get_relationships(self, subject: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            if subject:
                cursor = conn.execute("SELECT * FROM relationships WHERE subject = ?", (subject,))
            else:
                cursor = conn.execute("SELECT * FROM relationships")
            return [dict(r) for r in cursor.fetchall()]

    # ---------------- Style Examples (Exemplars) ----------------
    def insert_style_example(
        self,
        example_id: str,
        mode: str,
        text: str,
        source_message_id: Optional[str] = None,
        confidence: float = 1.0,
        importance: float = 0.5,
    ):
        with self.get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO style_examples
                   (id, mode, text, source_message_id, confidence, importance)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (example_id, mode.lower(), text, source_message_id, confidence, importance),
            )
            conn.execute("DELETE FROM style_examples_fts WHERE id = ?", (example_id,))
            conn.execute(
                "INSERT INTO style_examples_fts (id, text) VALUES (?, ?)",
                (example_id, text),
            )
            conn.commit()

    def get_style_examples(self, mode: Optional[str] = None, limit: int = 4) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            if mode:
                cursor = conn.execute(
                    "SELECT * FROM style_examples WHERE mode = ? ORDER BY importance DESC, confidence DESC LIMIT ?",
                    (mode.lower(), limit),
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM style_examples ORDER BY importance DESC, confidence DESC LIMIT ?",
                    (limit,),
                )
            return [dict(r) for r in cursor.fetchall()]

    # ---------------- Embeddings ----------------
    def save_embedding(self, entity_id: str, entity_type: str, vector: List[float]):
        with self.get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO entity_embeddings (entity_id, entity_type, vector_json) VALUES (?, ?, ?)",
                (entity_id, entity_type, json.dumps(vector)),
            )
            conn.commit()

    def get_embedding(self, entity_id: str) -> Optional[List[float]]:
        with self.get_connection() as conn:
            try:
                cursor = conn.execute("SELECT vector_json FROM entity_embeddings WHERE entity_id = ?", (entity_id,))
                row = cursor.fetchone()
                if row and row["vector_json"]:
                    return json.loads(row["vector_json"])
            except Exception:
                pass
            try:
                cursor = conn.execute("SELECT embedding_json FROM entity_embeddings WHERE entity_id = ?", (entity_id,))
                row = cursor.fetchone()
                if row and row["embedding_json"]:
                    return json.loads(row["embedding_json"])
            except Exception:
                pass
            return None

    # ---------------- FTS5 Search ----------------
    def search_facts_fts(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Executes BM25 search over facts_fts.
        """
        clean = "".join(c if c.isalnum() or c.isspace() else " " for c in query).strip()
        if not clean:
            return []
        
        # Format words for FTS5 prefix match: word*
        tokens = [f'"{w}"*' for w in clean.split() if len(w) >= 2]
        if not tokens:
            return []
        fts_query = " OR ".join(tokens)

        with self.get_connection() as conn:
            sql = """
                SELECT f.*, bm25(facts_fts) as bm25_rank
                FROM facts_fts
                JOIN facts f ON facts_fts.id = f.id
                WHERE facts_fts MATCH ?
                ORDER BY bm25_rank ASC
                LIMIT ?
            """
            try:
                cursor = conn.execute(sql, (fts_query, limit))
                return [dict(r) for r in cursor.fetchall()]
            except Exception:
                return []
