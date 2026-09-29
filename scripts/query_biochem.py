import sqlite3

con = sqlite3.connect('alisha_memory.db')
cur = con.cursor()

print("=== CHECKING ALISHA STUDY / BIOCHEM / EXAMS ===")
query = """
SELECT id, sender, content 
FROM messages 
WHERE sender = 'alisha' 
  AND (
    LOWER(content) LIKE '%biochem%' 
    OR LOWER(content) LIKE '%study%' 
    OR LOWER(content) LIKE '%exam%' 
    OR LOWER(content) LIKE '%college%'
    OR LOWER(content) LIKE '%lecture%'
    OR LOWER(content) LIKE '%lab%'
    OR LOWER(content) LIKE '%class%'
  )
LIMIT 25
"""
cur.execute(query)
for r in cur.fetchall():
    print(f"[{r[0]}] {r[2]}")

print("\n=== CHECKING MEMORIES / INSIDE JOKES / NICKNAMES ===")
query2 = """
SELECT id, sender, content 
FROM messages 
WHERE sender = 'alisha' 
  AND (
    LOWER(content) LIKE '%cutie%' 
    OR LOWER(content) LIKE '%latw%' 
    OR LOWER(content) LIKE '%innit%'
    OR LOWER(content) LIKE '%bored%'
    OR LOWER(content) LIKE '%food%'
    OR LOWER(content) LIKE '%tea%'
    OR LOWER(content) LIKE '%chai%'
  )
LIMIT 20
"""
cur.execute(query2)
for r in cur.fetchall():
    print(f"[{r[0]}] {r[2]}")

con.close()
