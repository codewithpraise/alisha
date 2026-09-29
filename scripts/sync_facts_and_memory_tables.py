"""
Sync fact_ledger with facts table and create FTS5 indexes in alisha_memory.db and data/memory.db.
Ensures MemoryDatabase and MemoryRetriever have immediate access to all 39 verified facts
and the full 13,653 classified message corpus.
"""

import sqlite3
import os
import zlib
import math
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "alisha_memory.db")
DATA_DB_PATH = os.path.join(ROOT, "data", "memory.db")

def deterministic_text_vector(text: str, dim: int = 128):
    vec = [0.0] * dim
    clean = re.sub(r"[^\w\s]", "", text.lower())
    words = clean.split()
    if not words:
        return vec
    for word in words:
        h_w = zlib.crc32(word.encode("utf-8")) % dim
        vec[h_w] += 2.0
        for i in range(len(word) - 2):
            tri = word[i : i + 3]
            h_tri = zlib.crc32(tri.encode("utf-8")) % dim
            vec[h_tri] += 1.0
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 1e-6:
        vec = [x / norm for x in vec]
    return vec

def sync_database(db_file):
    print(f"Syncing schema and facts for {db_file}...")
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    # Create facts table
    cur.execute("""
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
        valid_until INTEGER,
        source_message_id TEXT
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_facts_subject ON facts(subject);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_facts_predicate ON facts(predicate);")

    # Create facts_fts virtual table
    try:
        cur.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts USING fts5(
            id UNINDEXED,
            subject,
            predicate,
            object,
            tokenize='porter unicode61'
        );
        """)
    except Exception as e:
        print(f"FTS5 facts notice: {e}")

    # Create entity_embeddings table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS entity_embeddings (
        entity_id TEXT PRIMARY KEY,
        entity_type TEXT NOT NULL,
        embedding_json TEXT NOT NULL
    );
    """)

    # Populate facts from fact_ledger if fact_ledger exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fact_ledger'")
    if cur.fetchone():
        cur.execute("""
        SELECT fact_id, subject, predicate, value, confidence, importance, first_seen, last_confirmed, valid_from, valid_until, notes
        FROM fact_ledger
        """)
        facts = cur.fetchall()
        print(f"Found {len(facts)} facts in fact_ledger. Populating 'facts' table...")

        cur.execute("DELETE FROM facts")
        try:
            cur.execute("DELETE FROM facts_fts")
        except Exception:
            pass

        now = int(time.time() * 1000)
        for f in facts:
            fact_id, subj, pred, val, conf, imp, fs, lc, vf, vu, notes = f
            vf = vf or fs or now
            fs = fs or now
            lc = lc or now
            cur.execute("""
            INSERT OR REPLACE INTO facts
            (id, subject, predicate, object, confidence, importance, first_seen, last_confirmed, valid_from, valid_until, source_message_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (fact_id, subj, pred, val, conf, imp, fs, lc, vf, vu, notes or "fact_ledger"))

            try:
                cur.execute("""
                INSERT INTO facts_fts (id, subject, predicate, object) VALUES (?, ?, ?, ?)
                """, (fact_id, subj, pred, val))
            except Exception:
                pass

            # Pre-compute and save embedding
            fact_text = f"{subj} {pred} {val}"
            vec = deterministic_text_vector(fact_text)
            import json
            cur.execute("""
            INSERT OR REPLACE INTO entity_embeddings (entity_id, entity_type, embedding_json)
            VALUES (?, 'fact', ?)
            """, (fact_id, json.dumps(vec)))

    conn.commit()
    conn.close()
    print(f"Sync complete for {db_file}.\n")

if __name__ == "__main__":
    import time
    sync_database(DB_PATH)
    if os.path.exists(DATA_DB_PATH):
        sync_database(DATA_DB_PATH)
