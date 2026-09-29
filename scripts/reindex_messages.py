import json
import sqlite3
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSONL_PATH = os.path.join(ROOT, "data", "messages.jsonl")
DB_PATH = os.path.join(ROOT, "alisha_memory.db")
VOICE_DIR = os.path.join(ROOT, "voice")

voice_files = set(f for f in os.listdir(VOICE_DIR) if f.endswith(".wav")) if os.path.exists(VOICE_DIR) else set()

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

# Drop and recreate messages table with clean columns
cur.execute("DROP TABLE IF EXISTS messages_fts")
cur.execute("DROP TABLE IF EXISTS messages")

cur.execute("""
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    ts_ms INTEGER,
    content TEXT,
    is_voice INTEGER DEFAULT 0,
    media_path TEXT,
    session INTEGER
)
""")

voice_idx = 0
voice_list = sorted(list(voice_files))

rows = []
if os.path.exists(JSONL_PATH):
    with open(JSONL_PATH, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            d = json.loads(line)
            role = d.get("_speaker_role", "")
            sender = "alisha" if "alisha" in role or "assistant" in role else "user"
            ts_ms = d.get("timestamp_ms", 0)
            content = d.get("content", "") or ""
            is_voice = 1 if ("voice" in content.lower() or "audio" in content.lower() or ".wav" in content.lower() or d.get("audio_file")) else 0
            media_path = ""
            if is_voice:
                if voice_list:
                    media_path = f"voice/{voice_list[voice_idx % len(voice_list)]}"
                    voice_idx += 1
                else:
                    media_path = "voice/1303735758283391.wav"
            
            session = d.get("conversation_session", 1)
            rows.append((sender, ts_ms, content, is_voice, media_path, session))

cur.executemany("""
INSERT INTO messages (sender, ts_ms, content, is_voice, media_path, session)
VALUES (?, ?, ?, ?, ?, ?)
""", rows)

con.commit()

# Create FTS5 search index
cur.execute("""
CREATE VIRTUAL TABLE messages_fts USING fts5(
    content,
    sender UNINDEXED,
    id UNINDEXED
)
""")

cur.execute("""
INSERT INTO messages_fts (rowid, content, sender, id)
SELECT id, content, sender, id FROM messages
""")

con.commit()

# Verify count
cur.execute("SELECT COUNT(*), SUM(is_voice) FROM messages")
tot, v_tot = cur.fetchone()
print(f"Indexed {tot} messages, {v_tot} voice notes into {DB_PATH}")
con.close()
