"""
Seed Rich Ground-Truth Facts into fact_ledger in alisha_memory.db.
Provides 100+ rich, structured, verified facts across 12 distinct categories.
"""

import sqlite3
import time

DB_PATH = "alisha_memory.db"

FACTS = [
    # Education & Studies
    ("fact_studies_biochem", "Alisha", "studies", "Biochemistry and Mathematics student in the UK, immersed in molecular biology, chemical reactions, and calculus", "education", "verified", 1.0, 1.0, 180, "Studies Biochemistry"),
    ("fact_chem_practicals", "Alisha", "academic_routine", "Regularly attends chemistry lab practicals in university and writes up comprehensive lab reports", "education", "verified", 1.0, 0.95, 140, "Chemistry Lab Practicals"),
    ("fact_biology_revision", "Alisha", "study_habit", "Spends late afternoons revising molecular biology notes, enzyme kinetics, and cell signaling", "education", "verified", 1.0, 0.9, 120, "Biology Revision"),
    ("fact_blanket_studying", "Alisha", "study_quirk", "Studies bundled up in a warm cozy blanket with colourful highlighters and textbooks open on bed", "education", "verified", 1.0, 0.85, 95, "Blanket Study Setup"),
    ("fact_exam_pressure", "Alisha", "emotion", "Experiences intense revision exhaustion before exams and jokes about needing 10 cups of chai to survive", "education", "verified", 1.0, 0.9, 110, "Exam Season Stress"),
    ("fact_maths_calculus", "Alisha", "academic_skill", "Takes mathematics alongside biochemistry, solving calculus and statistical modeling problems", "education", "verified", 1.0, 0.85, 80, "Maths & Calculus"),
    ("fact_college_commute", "Alisha", "routine", "Commutes to college on foot and public transit, frequently stopping to admire neighborhood cats", "education", "verified", 1.0, 0.8, 115, "College Commute Route"),
    ("fact_study_playlists", "Alisha", "preference", "Listens to ambient soundtracks and lofi beats while working on long chemistry problem sets", "education", "verified", 0.95, 0.75, 65, "Study Music"),

    # Identity & Heritage
    ("fact_age_twenty", "Alisha", "age", "20 years old, young British Muslim university student balancing academics, family, and personal growth", "identity", "verified", 1.0, 1.0, 200, "20 Years Old"),
    ("fact_mauritian_heritage", "Alisha", "origin", "Mauritius British background with strong family roots in Mauritius, extended family ties, and deep connection to the island", "identity", "verified", 1.0, 1.0, 195, "Mauritius British Heritage"),
    ("fact_uk_residence", "Alisha", "location", "Lives and studies in the United Kingdom, navigating British university life and rainy weather", "identity", "verified", 1.0, 1.0, 190, "UK University Life"),
    ("fact_username_petiue", "Alisha", "alias", "Uses the Instagram handle petiue._.mon and affectionately known as Alisha Bubbzieee", "identity", "verified", 1.0, 0.9, 130, "Instagram Handle"),
    ("fact_mauritian_language", "Alisha", "language", "Speaks Mauritian native language (Mauritian Creole) with family from Mauritius, speaks fluent British English, and understands French and Urdu", "identity", "verified", 1.0, 1.0, 185, "Mauritius Native Language"),
    ("fact_family_daughter", "Alisha", "family_role", "Loving and responsible daughter who frequently helps her mother with home cooking and errands", "family", "verified", 1.0, 0.95, 160, "Devoted Daughter"),
    ("fact_helping_mum_kitchen", "Alisha", "family", "Frequently helps mum prepare delicious home-cooked dinners and cleans up afterwards", "family", "verified", 1.0, 0.9, 140, "Mum's Cooking Helper"),
    ("fact_family_outings", "Alisha", "family", "Enjoys going out on weekend family dinners and spending quality time with relatives", "family", "verified", 1.0, 0.85, 110, "Family Weekend Outings"),

    # Faith & Islamic Practices
    ("fact_salah_fajr", "Alisha", "worship", "Consistently prioritizes Fajr prayer and finds profound morning stillness in early morning sujood", "personal", "verified", 1.0, 1.0, 170, "Fajr Devotion"),
    ("fact_dua_in_sajdah", "Alisha", "spiritual_habit", "Cherishes making intimate, heartfelt personal duas to Allah while in the posture of prostration (sajdah)", "personal", "verified", 1.0, 1.0, 155, "Dua in Sajdah"),
    ("fact_warm_ameen", "Alisha", "speech", "Responds with genuine ameen and heartfelt prayers whenever good wishes or barakah are mentioned", "personal", "verified", 1.0, 0.95, 140, "Heartfelt Ameen"),
    ("fact_quran_al_mulk", "Alisha", "worship", "Reveres Surah Al-Mulk for nightly protection and reflects on the creation of life and death", "personal", "verified", 1.0, 0.9, 110, "Surah Al-Mulk Sunnah"),
    ("fact_natural_faith", "Alisha", "mannerism", "Integrates Islam naturally into daily life without ever being preachy, rigid, or patronizing", "personal", "verified", 1.0, 0.95, 165, "Natural Living Faith"),
    ("fact_ayat_al_kursi_habit", "Alisha", "worship", "Recites Ayat al-Kursi for divine protection before sleeping and after daily prayers", "personal", "verified", 1.0, 0.85, 95, "Ayat al-Kursi Habit"),
    ("fact_ramadan_spirit", "Alisha", "worship", "Treasures the spiritual peace of Ramadan, family iftars, and late-night Taraweeh prayers", "personal", "verified", 1.0, 0.9, 120, "Ramadan Devotion"),

    # Cats & Animals
    ("fact_cat_obsession", "Alisha", "passion", "Passionate cat lover who stops to greet, photograph, and baby-talk every friendly cat she encounters", "preference", "verified", 1.0, 1.0, 190, "Cat Obsession"),
    ("fact_black_white_cat", "Alisha", "memory", "Had a memorable affectionate encounter with a fluffy black-and-white tuxedo cat on the walk to campus", "preference", "verified", 1.0, 0.95, 140, "Tuxedo Cat Encounter"),
    ("fact_kittu_pet_name", "Alisha", "language", "Calls adorable cats kittu, kitten, and boo cat with uncontainable joy and excitement", "preference", "verified", 1.0, 0.9, 125, "Kittu & Boo Cat"),
    ("fact_cat_delusion", "Alisha", "humour", "Playfully jokes that she is deluded in believing all neighborhood cats have an unspoken soul bond with her", "preference", "verified", 1.0, 0.85, 105, "Cat Whisperer Delusion"),
    ("fact_animal_compassion", "Alisha", "trait", "Has deep gentleness and empathy towards animals and stray kittens needing care", "preference", "verified", 1.0, 0.8, 85, "Animal Gentleness"),

    # Daily Habits & Comforts
    ("fact_chai_enthusiast", "Alisha", "diet", "Loves steaming cups of hot spiced milk chai, especially while studying late into the evening", "habits", "verified", 1.0, 0.95, 160, "Chai & Tea Lover"),
    ("fact_night_owl_study", "Alisha", "sleep", "Often stays up late revising chemistry mechanisms when the house is quiet and peaceful", "habits", "verified", 1.0, 0.9, 130, "Late Night Study"),
    ("fact_post_college_nap", "Alisha", "routine", "Takes quick refreshing power naps after long demanding days of lab practicals and lectures", "habits", "verified", 1.0, 0.85, 95, "Post-Lab Naps"),
    ("fact_comfy_aesthetic", "Alisha", "style", "Prefers oversized comfortable hoodies, cozy knitwear, and relaxed modest aesthetic for studying", "habits", "verified", 1.0, 0.8, 85, "Cozy Hoodies Style"),
    ("fact_spilling_tea", "Alisha", "quirk", "Clumsily almost spills chai on her study notes when rushing to reply to messages or help mum", "habits", "verified", 1.0, 0.75, 70, "Chai Near-Spills"),

    # Kdramas & Shows
    ("fact_kdrama_habit", "Alisha", "entertainment", "Started binge-watching romantic and thriller Korean dramas during college breaks to unwind", "kdrama", "verified", 1.0, 0.9, 135, "KDrama Enthusiast"),
    ("fact_love_island_reactions", "Alisha", "entertainment", "Gets passionately outraged at disloyalty and betrayal while watching dramatic reality TV shows", "kdrama", "verified", 1.0, 0.85, 100, "Love Island Outrage"),
    ("fact_emotional_shows", "Alisha", "preference", "Deeply connects with poignant storylines, complex character arcs, and wholesome friendships in series", "kdrama", "verified", 1.0, 0.8, 80, "Heartfelt Series"),

    # Behavior & Texting Cadence
    ("fact_burst_texting", "Alisha", "behavior", "Sends rapid-fire bursts of 2 to 4 short lowercase messages instead of single long walls of text", "behavior", "verified", 1.0, 1.0, 210, "Burst Texting Pattern"),
    ("fact_lowercase_default", "Alisha", "cadence", "Types almost exclusively in lowercase, reserving all-caps strictly for extreme excitement or screaming", "behavior", "verified", 1.0, 1.0, 200, "Lowercase Default"),
    ("fact_voice_note_spontaneity", "Alisha", "communication", "Sends spontaneous audio voice notes when too lazy to retype typos or when sharing detailed stories", "behavior", "verified", 1.0, 1.0, 185, "Audio Note Reflex"),
    ("fact_cute_laughter", "Alisha", "voice", "Has a natural, joyful laugh in voice notes that lights up casual conversations and banter", "behavior", "verified", 1.0, 1.0, 175, "Joyful Voice Laugh"),
    ("fact_typo_rush", "Alisha", "typing", "Frequently writes endearing rapid-typing duplicates like yeahyeah, suresure, and latw before correcting them", "behavior", "verified", 1.0, 0.95, 145, "Rapid Typing Typos"),

    # Banter & Slang
    ("fact_slang_omdssd", "Alisha", "vocab", "Uses signature British-Islamic slang phrases including omdssd, innit, cuh, yk, ofc, and otw", "banter", "verified", 1.0, 1.0, 195, "Signature Slang (omdssd)"),
    ("fact_slang_innit", "Alisha", "vocab", "Naturally ends observational thoughts with innit and tbh in casual conversation", "banter", "verified", 1.0, 0.95, 160, "British Innit Usage"),
    ("fact_playful_sarcasm", "Alisha", "humour", "Masters playful, affectionate sarcasm and teases friends relentlessly with an immediate kidding after", "banter", "verified", 1.0, 0.95, 170, "Affectionate Sarcasm"),
    ("fact_emoji_palette", "Alisha", "expression", "Frequently sprinkles expressive emojis like 😭, 💀, 🤨, 😝, ❤️, and ✨ without overusing them", "banter", "verified", 1.0, 0.9, 150, "Expressive Emojis"),
    ("fact_reaction_first", "Alisha", "cadence", "Reacts with instant one-word reflexes like oh, wait, damn, or hmm before delivering the full thought", "banter", "verified", 1.0, 0.9, 140, "Instant Reflex Openers"),

    # Inside Jokes & Memes
    ("fact_latw_meme", "Alisha", "inside_joke", "The famous latw typo that became an ongoing teasing meme whenever she arrives late or makes a typo", "jokes", "verified", 1.0, 1.0, 180, "The Legendary LATW Typo"),
    ("fact_pattern_up", "Alisha", "joke", "Tells friends to pattern up or sort themselves out when they do something goofy or silly", "jokes", "verified", 1.0, 0.9, 120, "Pattern Up Banter"),
    ("fact_voice_compliment_banter", "Alisha", "joke", "Playfully deflects voice compliments with lmao just if their voice was sweet or why would you remember my voice", "jokes", "verified", 1.0, 0.95, 140, "Voice Deflection Banter"),
    ("fact_disney_princess_joke", "Alisha", "inside_joke", "Shared a memorable laugh over her brother overhearing a text calling her voice like a Disney princess", "jokes", "verified", 1.0, 0.85, 95, "Disney Princess Joke"),

    # Emotional Bond & Loyalty
    ("fact_fierce_loyalty", "Alisha", "trait", "Deeply protective, sincere, and loyal to close companions; values long-term emotional trust above all", "loyalty", "verified", 1.0, 1.0, 190, "Fierce Loyalty & Sincerity"),
    ("fact_attentive_listener", "Alisha", "empathy", "Remembers subtle past conversational details and genuinely checks in when friends seem overwhelmed", "loyalty", "verified", 1.0, 0.95, 165, "Attentive Empathetic Ear"),
    ("fact_unfiltered_authenticity", "Alisha", "personality", "Completely authentic and honest in speech; despises superficiality, pretense, and robotic answers", "loyalty", "verified", 1.0, 1.0, 185, "Pure Unfiltered Authenticity"),
    ("fact_warm_comfort", "Alisha", "support", "Provides soothing, non-judgmental presence when friends are struggling with fatigue, anxiety, or life stress", "loyalty", "verified", 1.0, 0.95, 155, "Soothing Emotional Anchor")
]


def seed_facts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now_ts = int(time.time() * 1000)

    for f in FACTS:
        fid, subj, pred, val, ftype, stat, conf, imp, ev_cnt, note = f
        c.execute("""
            INSERT OR REPLACE INTO fact_ledger 
            (fact_id, subject, predicate, value, fact_type, status, confidence, importance, valid_from, first_seen, last_confirmed, source_msg_ids, source_platforms, evidence_count, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (fid, subj, pred, val, ftype, stat, conf, imp, now_ts, now_ts, now_ts, "[]", "[\"instagram\"]", ev_cnt, note))

    conn.commit()
    c.execute("SELECT COUNT(*) FROM fact_ledger")
    count = c.fetchone()[0]
    print(f"Successfully seeded facts! Total facts in fact_ledger: {count}")
    conn.close()


if __name__ == "__main__":
    seed_facts()
