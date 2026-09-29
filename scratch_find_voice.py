import sqlite3

con = sqlite3.connect("alisha_memory.db")
cur = con.cursor()
cur.execute("SELECT id, sender, content, media_path, duration_sec FROM messages WHERE is_voice = 1")
rows = cur.fetchall()
print(f"Total voice messages: {len(rows)}")
for r in rows:
    c = (r[2] or "").lower()
    if "uni" in c or "jarring" in c or "ready" in c or "travel" in c:
        print("MATCH:", r)

con.close()
