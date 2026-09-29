import sqlite3, sys, re
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
con = sqlite3.connect('alisha_memory.db')
cur = con.cursor()

# Sample varied alisha messages
print('=== ALISHA DB SAMPLES (short to medium) ===')
cur.execute("SELECT content FROM messages WHERE sender='alisha' AND length(content) BETWEEN 5 AND 50 ORDER BY RANDOM() LIMIT 50")
for row in cur.fetchall():
    print(f'  {repr(row[0])}')

print('\n=== ALISHA DB SAMPLES (medium-long, 50-150 chars) ===')
cur.execute("SELECT content FROM messages WHERE sender='alisha' AND length(content) BETWEEN 50 AND 150 ORDER BY RANDOM() LIMIT 30")
for row in cur.fetchall():
    print(f'  {repr(row[0])}')

print('\n=== STUDY/COLLEGE RELATED ===')
cur.execute("SELECT content FROM messages WHERE sender='alisha' AND (LOWER(content) LIKE '%college%' OR LOWER(content) LIKE '%exam%' OR LOWER(content) LIKE '%lab%' OR LOWER(content) LIKE '%biochem%' OR LOWER(content) LIKE '%bio%' OR LOWER(content) LIKE '%chem%') LIMIT 30")
for row in cur.fetchall():
    print(f'  {repr(row[0])}')

print('\n=== CAT REFERENCES ===')
cur.execute("SELECT content FROM messages WHERE sender='alisha' AND LOWER(content) LIKE '%cat%' LIMIT 20")
for row in cur.fetchall():
    print(f'  {repr(row[0])}')

print('\n=== FAITH/DUA REFERENCES ===')
cur.execute("SELECT content FROM messages WHERE sender='alisha' AND (LOWER(content) LIKE '%dua%' OR LOWER(content) LIKE '%ameen%' OR LOWER(content) LIKE '%allah%' OR LOWER(content) LIKE '%salah%') LIMIT 20")
for row in cur.fetchall():
    print(f'  {repr(row[0])}')

print('\n=== AFFECTION/WARMTH ===')
cur.execute("SELECT content FROM messages WHERE sender='alisha' AND (LOWER(content) LIKE '%cutie%' OR LOWER(content) LIKE '%love%' OR LOWER(content) LIKE '%miss%' OR LOWER(content) LIKE '%heart%') LIMIT 20")
for row in cur.fetchall():
    print(f'  {repr(row[0])}')

con.close()
print('DONE')
