import sqlite3, json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("MESSAGES_SRC", os.path.join(ROOT, "data", "messages.jsonl") if os.path.exists(os.path.join(ROOT, "data", "messages.jsonl")) else os.path.join(ROOT, "messages", "messages.jsonl"))
DB  = os.environ.get("MEMORY_DB", os.path.join(ROOT, "alisha_memory.db"))

SCHEMA = """
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    ts_ms INTEGER,
    content TEXT NOT NULL,
    source TEXT,
    session TEXT
);
CREATE VIRTUAL TABLE messages_fts USING fts5(
    content,
    content='messages',
    content_rowid='id',
    tokenize='unicode61'
);
CREATE TRIGGER messages_ai AFTER INSERT ON messages BEGIN
    INSERT INTO messages_fts(rowid, content) VALUES (new.id, new.content);
END;
CREATE TRIGGER messages_ad AFTER DELETE ON messages BEGIN
    INSERT INTO messages_fts(messages_fts, rowid, content) VALUES('delete', old.id, old.content);
END;
CREATE TRIGGER messages_au AFTER UPDATE ON messages BEGIN
    INSERT INTO messages_fts(messages_fts, rowid, content) VALUES('delete', old.id, old.content);
    INSERT INTO messages_fts(rowid, content) VALUES (new.id, new.content);
END;
"""

SENDER_KEYS  = ("sender", "from", "role", "author", "who")
TS_KEYS      = ("ts_ms", "timestamp", "ts", "time", "date")
CONTENT_KEYS = ("content", "text", "message", "body", "msg")
SOURCE_KEYS  = ("source", "src", "platform")
SESSION_KEYS = ("session", "conv", "thread", "channel")

def _pick(d, keys, default=None):
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return default

def build():
    if os.path.exists(DB):
        os.remove(DB)
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.executescript(SCHEMA)

    n = skipped = 0
    with open(SRC, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                skipped += 1
                continue
            content = _pick(r, CONTENT_KEYS)
            if not content:
                if r.get("audio_files"):
                    content = "[voice note]"
                elif r.get("reactions"):
                    content = "[reaction]"
                elif r.get("share"):
                    content = "[shared post]"
                else:
                    content = "[media]"
            cur.execute(
                "INSERT INTO messages(sender,ts_ms,content,source,session) VALUES (?,?,?,?,?)",
                (_pick(r, SENDER_KEYS),
                 _pick(r, TS_KEYS, 0),
                 str(content),
                 _pick(r, SOURCE_KEYS),
                 _pick(r, SESSION_KEYS)),
            )
            n += 1

    con.commit()
    cur.execute("INSERT INTO messages_fts(messages_fts) VALUES('rebuild')")
    con.commit()

    total = cur.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    fts_n = cur.execute("SELECT COUNT(*) FROM messages_fts").fetchone()[0]
    con.close()
    print(f"inserted  : {n}")
    print(f"skipped   : {skipped}")
    print(f"messages  : {total}")
    print(f"fts rows  : {fts_n}")
    print(f"db        : {DB}  ({os.path.getsize(DB)/1e6:.1f} MB)")

if __name__ == "__main__":
    with open(SRC, "r", encoding="utf-8") as f:
        first = json.loads(f.readline())
    print("first record keys:", sorted(first.keys()))
    print("first record     :", {k: (str(v)[:60]) for k, v in first.items()})
    print("-" * 60)
    build()
