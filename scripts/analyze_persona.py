import sqlite3
import json

con = sqlite3.connect('alisha_memory.db')
cur = con.cursor()

print("--- SEARCHING STUDY / BIOCHEM / COLLEGE ---")
terms = ['biochem', 'study', 'studying', 'college', 'exam', 'uni', 'degree', 'major', 'class', 'classes', 'lecture', 'biology', 'chemistry']
for t in terms:
    cur.execute("SELECT id, sender, content FROM messages WHERE sender = 'alisha' AND LOWER(content) LIKE ? LIMIT 4", (f'%{t}%',))
    rows = cur.fetchall()
    if rows:
        print(f"\n[Term: {t}]")
        for r in rows:
            print(f"  #{r[0]}: {r[2]}")

print("\n--- SAMPLE ALISHA CASUAL/FUN BURSTS ---")
cur.execute("SELECT id, content FROM messages WHERE sender = 'alisha' AND LENGTH(content) > 3 AND LENGTH(content) < 80 ORDER BY RANDOM() LIMIT 20")
for r in cur.fetchall():
    print(f"  #{r[0]}: {r[1]}")

con.close()
