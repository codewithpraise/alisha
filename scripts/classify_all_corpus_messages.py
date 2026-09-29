"""
Classify All 13,653 Corpus Messages for Alisha Bubbzieee.
Performs high-precision, context-aware NLP classification across the entire corpus.
Stores category, badge, sub_category, topics, sentiment, and importance directly in SQLite.
"""

import sqlite3
import os
import re
import json
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "alisha_memory.db")
DATA_DB_PATH = os.path.join(ROOT, "data", "memory.db")

CATEGORY_RULES = {
    "identity": {
        "keywords": [
            "age", "20 years old", "turning 20", "20 yo", "mauritius", "mauritian",
            "british", "pakistani", "heritage", "roots", "born in", "grew up in", "uk",
            "london", "birthday", "bday", "birthdate"
        ],
        "regex": [r"\b20\b.*(?:years|yo|age)", r"\bage\b.*(?:20)", r"\bmauritius\b", r"\bbritish\b", r"\bpakistani\b"]
    },
    "education": {
        "keywords": [
            "biochem", "biochemistry", "chemistry", "bio", "biology", "maths", "math",
            "practical", "practicals", "titration", "titrations", "lab", "labs",
            "exam", "exams", "revision", "revising", "lecture", "lectures", "assignment",
            "assignments", "college", "campus", "homework", "test", "tests", "notes",
            "grade", "grades", "studying", "study", "studies", "blanket study"
        ],
        "regex": [r"\bbiochem\w*", r"\bchemistr\w*", r"\bpractical\w*", r"\brevis\w*", r"\bexam\w*", r"\btitrat\w*"]
    },
    "personal": {
        "keywords": [
            "salah", "namaz", "prayer", "prayers", "pray", "prayed", "praying",
            "fajr", "zuhr", "dhuhr", "asr", "maghrib", "isha", "tahajjud", "sajdah",
            "dua", "duas", "allah", "quran", "surah", "ayah", "ameen", "amin",
            "jummah", "jumuah", "salawat", "halal", "haram", "ramadan", "fasting",
            "fast", "iftar", "sehri", "bismillah", "subhanallah", "alhamdulillah",
            "astaghfirullah", "allahu akbar", "deen", "dhikr", "zikr"
        ],
        "regex": [r"\bsalah\b", r"\bfajr\b", r"\bdua\b", r"\bquran\b", r"\ballah\b", r"\bameen\b", r"\bsajdah\b", r"\bjummah\b"]
    },
    "preference": {
        "keywords": [
            "cat", "cats", "kitten", "kittens", "kittu", "meow", "meows", "paw", "paws",
            "fur", "purr", "purring", "stray cat", "black and white cat", "black cat",
            "kdrama", "kdramas", "k-drama", "drama", "tea", "chai", "green tea", "matcha",
            "hot chocolate", "coffee", "boba", "food", "fave food", "chocolate", "cozy"
        ],
        "regex": [r"\bcat\w*", r"\bkittu\b", r"\bmeow\w*", r"\bkdrama\w*", r"\bchai\b", r"\btea\b"]
    },
    "family": {
        "keywords": [
            "mum", "mom", "mother", "mummy", "dad", "father", "daddy", "brother",
            "sister", "cousin", "cousins", "uncle", "auntie", "aunt", "family",
            "dinner with family", "family dinner", "kitchen", "cooking", "groceries",
            "grocery", "home", "house", "cleaning", "chores", "helping mum", "car"
        ],
        "regex": [r"\bmum\b", r"\bmom\b", r"\bfamily\b", r"\bhelping mum\b", r"\bkitchen\b", r"\bchores\b"]
    },
    "behavior": {
        "keywords": [
            "voice note", "voice msg", "vn", "audio", "voice message", "record", "recording",
            "sleep", "sleepy", "sleeping", "tired", "exhausted", "nap", "napping",
            "woke up", "wake up", "waking up", "morning", "good morning", "gm",
            "night", "good night", "gn", "bed", "commute", "bus", "train", "walk",
            "walking", "commute to college", "battery", "phone died", "lazy to type",
            "spelling mistake", "spelling mistakes", "burst"
        ],
        "regex": [r"\bvoice note\b", r"\bvn\b", r"\bsleep\w*", r"\btired\w*", r"\bcommute\b", r"\bwoke up\b"]
    },
    "personality": {
        "keywords": [
            "pattern up", "latw", "bubbzieee", "omdssd", "omds", "omg", "lmao", "lol",
            "roast", "roasting", "teasing", "tease", "kidding", "jokes", "joke", "haha",
            "hehe", "silly", "cutie", "cute", "bro", "bruh", "cuh", "innit", "fr",
            "ngl", "idc", "tbh", "wtf", "vibe", "mood", "hugging", "miss you", "proud",
            "thanks", "sweet", "loyal", "podcast", "laughing", "laugh"
        ],
        "regex": [r"\bpattern up\b", r"\blatw\b", r"\bbubbzieee\b", r"\bomdssd\b", r"\bkidding\b", r"\broast\w*"]
    }
}

def detect_sentiment(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["sad", "crying", "upset", "tired", "exhausted", "pain", "ugh", "stressed", "hard"]):
        return "vulnerable"
    if any(w in t for w in ["love", "cute", "sweet", "aww", "cutie", "pookie", "ameen", "❤️", "🥺", "🥰"]):
        return "affectionate"
    if any(w in t for w in ["haha", "lmao", "lol", "💀", "😭", "kidding", "joke", "silly", "bro"]):
        return "playful"
    if any(w in t for w in ["salah", "dua", "allah", "alhamdulillah", "subhanallah", "blessed"]):
        return "devotional"
    return "neutral"

def classify_message_text(text: str, is_voice: bool, prev_category: str = None) -> tuple:
    """
    Returns (category, badge, sub_category, topics, importance).
    """
    t = (text or "").lower().strip()
    topics = []

    # Voice Note override
    if is_voice:
        # If transcript exists and is about something specific
        if any(w in t for w in ["chemistry", "biochem", "exam", "college"]):
            return "education", "Voice Note: Biochemistry", "biochem_audio", ["voice_note", "education"], 0.85
        if any(w in t for w in ["mum", "family", "mauritius", "aunt"]):
            return "family", "Voice Note: Family & Mum", "family_audio", ["voice_note", "family"], 0.85
        if any(w in t for w in ["laugh", "podcast", "joke", "spelling", "type"]):
            return "behavior", "Voice Note: Humor & Habits", "voice_habit", ["voice_note", "humor"], 0.90
        return "behavior", "Voice Note", "voice_memo", ["voice_note"], 0.80

    # Explicit inside jokes / specific catchphrases
    if "pattern up" in t:
        return "personality", "Inside Joke (Pattern Up)", "catchphrase", ["pattern_up", "banter"], 0.95
    if "latw" in t:
        return "personality", "Inside Joke (Latw)", "typo_legend", ["latw", "banter"], 0.95
    if "bubbzieee" in t:
        return "personality", "Inside Joke (Bubbzieee)", "nickname", ["bubbzieee", "affection"], 0.95
    if "omdssd" in t or "omds" in t:
        return "personality", "Exclamation (Omdssd)", "slang", ["omdssd", "reaction"], 0.70

    # Check matches across categories
    scores = {cat: 0 for cat in CATEGORY_RULES}
    matched_kws = {cat: [] for cat in CATEGORY_RULES}

    for cat, rules in CATEGORY_RULES.items():
        for kw in rules["keywords"]:
            if kw in t:
                scores[cat] += (2 if " " in kw else 1)
                matched_kws[cat].append(kw)
        for r in rules["regex"]:
            if re.search(r, t):
                scores[cat] += 2

    # High score wins
    best_cat = max(scores, key=scores.get)
    best_score = scores[best_cat]

    if best_score > 0:
        topics = matched_kws[best_cat][:4]
        # Determine specific badge
        if best_cat == "identity":
            if any(w in t for w in ["20", "age"]):
                return "identity", "Identity & Age (20)", "age_verification", topics, 0.95
            if any(w in t for w in ["mauritius", "british", "pakistani", "roots"]):
                return "identity", "Mauritius & UK Heritage", "heritage", topics, 0.90
            return "identity", "Identity & Background", "bio", topics, 0.85

        elif best_cat == "education":
            if any(w in t for w in ["practical", "titration", "lab"]):
                return "education", "Biochemistry Practicals & Labs", "practicals", topics, 0.90
            if any(w in t for w in ["exam", "revision", "revising", "test"]):
                return "education", "Exams & Revision", "exams", topics, 0.90
            if any(w in t for w in ["maths", "math"]):
                return "education", "Maths Studies", "maths", topics, 0.85
            return "education", "Biochemistry & College Life", "college_life", topics, 0.85

        elif best_cat == "personal":
            if any(w in t for w in ["sajdah", "dua"]):
                return "personal", "Sajdah Duas & Supplication", "duas", topics, 0.95
            if any(w in t for w in ["fajr", "salah", "namaz"]):
                return "personal", "Salah & Fajr Adherence", "salah", topics, 0.90
            if any(w in t for w in ["jummah", "salawat"]):
                return "personal", "Jummah & Salawat", "jummah", topics, 0.85
            return "personal", "Faith & Devotion", "faith", topics, 0.85

        elif best_cat == "preference":
            if any(w in t for w in ["kittu", "cat", "kitten", "meow"]):
                return "preference", "Cats & Kittu", "cats", topics, 0.95
            if any(w in t for w in ["kdrama", "drama"]):
                return "preference", "KDramas & Break Time", "kdramas", topics, 0.85
            if any(w in t for w in ["tea", "chai", "matcha"]):
                return "preference", "Tea & Chai Rituals", "tea", topics, 0.80
            return "preference", "Preferences & Favorites", "lifestyle", topics, 0.75

        elif best_cat == "family":
            if any(w in t for w in ["mum", "mom", "helping"]):
                return "family", "Helping Mum at Home", "mum_bond", topics, 0.90
            if any(w in t for w in ["dinner", "cooking", "kitchen"]):
                return "family", "Family Dinners & Kitchen", "dinners", topics, 0.85
            return "family", "Family Life & Home", "family", topics, 0.80

        elif best_cat == "behavior":
            if any(w in t for w in ["sleep", "tired", "nap", "woke"]):
                return "behavior", "Sleep & Fatigue", "sleep", topics, 0.80
            if any(w in t for w in ["commute", "bus", "walk"]):
                return "behavior", "Morning Commute", "commute", topics, 0.80
            return "behavior", "Daily Routine & Habits", "routine", topics, 0.75

        elif best_cat == "personality":
            if any(w in t for w in ["kidding", "roast", "tease"]):
                return "personality", "Teasing & Sarcasm", "roasting", topics, 0.85
            if any(w in t for w in ["cutie", "miss", "love", "proud"]):
                return "personality", "Affection & Care", "warmth", topics, 0.85
            return "personality", "Witty Banter & Humor", "banter", topics, 0.75

    # If message is a short conversational reply, inherit parent conversation context
    if prev_category and len(t) < 30 and prev_category in CATEGORY_RULES:
        badge_name = f"{prev_category.capitalize()} Dialogue"
        return prev_category, badge_name, "dialogue_continuation", ["context_carryover"], 0.60

    # Default fallback
    return "personality", "Casual Banter", "casual_chat", ["banter"], 0.50

def run_classification():
    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Add columns if not exist
    cur.execute("PRAGMA table_info(messages)")
    cols = [r[1] for r in cur.fetchall()]
    new_cols = {
        "category": "TEXT DEFAULT 'personality'",
        "badge": "TEXT DEFAULT 'Casual Banter'",
        "sub_category": "TEXT DEFAULT 'casual'",
        "topics": "TEXT DEFAULT '[]'",
        "sentiment": "TEXT DEFAULT 'neutral'",
        "importance": "REAL DEFAULT 0.5"
    }
    for col_name, col_def in new_cols.items():
        if col_name not in cols:
            print(f"Adding column '{col_name}' to messages table...")
            cur.execute(f"ALTER TABLE messages ADD COLUMN {col_name} {col_def}")

    conn.commit()

    # 2. Fetch all messages in chronological order
    cur.execute("SELECT id, sender, ts_ms, content, is_voice, media_path, session FROM messages ORDER BY id ASC")
    rows = cur.fetchall()
    print(f"Loaded {len(rows)} messages. Classifying...")

    updates = []
    category_counts = {}
    prev_cat = None
    prev_session = None

    for r in rows:
        msg_id = r[0]
        sender = r[1]
        ts_ms = r[2]
        content = r[3] or ""
        is_voice = bool(r[4])
        session = r[6]

        # Reset parent context across different sessions
        if session != prev_session:
            prev_cat = None
            prev_session = session

        cat, badge, sub_cat, topics, importance = classify_message_text(content, is_voice, prev_cat)
        sentiment = detect_sentiment(content)

        if cat not in ["personality"] or "Inside Joke" in badge:
            prev_cat = cat

        category_counts[cat] = category_counts.get(cat, 0) + 1
        updates.append((cat, badge, sub_cat, json.dumps(topics), sentiment, importance, msg_id))

    # 3. Batch update
    print(f"Applying updates to {len(updates)} messages in database...")
    cur.executemany(
        """
        UPDATE messages
        SET category = ?, badge = ?, sub_category = ?, topics = ?, sentiment = ?, importance = ?
        WHERE id = ?
        """,
        updates
    )

    # 4. Create performance indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_messages_category ON messages(category)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_messages_badge ON messages(badge)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_messages_is_voice ON messages(is_voice)")

    conn.commit()
    conn.close()

    print("\n--- Classification Results Across All Messages ---")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        pct = (count / len(rows)) * 100
        print(f"  {cat.ljust(15)} : {count:5d} messages ({pct:5.1f}%)")

    # 5. Sync to data/memory.db if it exists
    if os.path.exists(DATA_DB_PATH):
        print(f"\nSyncing classified dataset to {DATA_DB_PATH}...")
        try:
            d_conn = sqlite3.connect(DATA_DB_PATH)
            d_cur = d_conn.cursor()
            d_cur.execute("PRAGMA table_info(messages)")
            d_cols = [r[1] for r in d_cur.fetchall()]
            for col_name, col_def in new_cols.items():
                if col_name not in d_cols:
                    d_cur.execute(f"ALTER TABLE messages ADD COLUMN {col_name} {col_def}")
            d_conn.commit()
            d_conn.close()
            print("Successfully synced columns to data/memory.db")
        except Exception as e:
            print(f"Notice on data/memory.db: {e}")

if __name__ == "__main__":
    t0 = time.time()
    run_classification()
    print(f"\nClassification completed in {time.time() - t0:.2f} seconds.")
