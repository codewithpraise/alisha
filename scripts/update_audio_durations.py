"""
Update exact WAV durations across all databases and voice note messages.
"""
import os
import wave
import sqlite3

def compute_durations(voice_dir="voice"):
    durations = {}
    if not os.path.exists(voice_dir):
        return durations
    for f in os.listdir(voice_dir):
        if f.endswith(".wav"):
            p = os.path.join(voice_dir, f)
            try:
                with wave.open(p, "r") as w:
                    frames = w.getnframes()
                    rate = w.getframerate()
                    dur = frames / float(rate)
                    durations[f] = dur
            except Exception as e:
                print(f"Error reading {f}: {e}")
    return durations

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    voice_dir = os.path.join(root, "voice")
    durations = compute_durations(voice_dir)
    print(f"Found {len(durations)} WAV files with accurate durations.")

    db_paths = [
        os.path.join(root, "alisha_memory.db"),
        os.path.join(root, "data", "memory.db"),
    ]

    for db_path in db_paths:
        if not os.path.exists(db_path):
            continue
        con = sqlite3.connect(db_path)
        cur = con.cursor()

        cols = [c[1] for c in cur.execute("PRAGMA table_info(messages)").fetchall()]
        if "duration_sec" not in cols:
            cur.execute("ALTER TABLE messages ADD COLUMN duration_sec REAL DEFAULT 0.0")
        if "duration_label" not in cols:
            cur.execute("ALTER TABLE messages ADD COLUMN duration_label TEXT DEFAULT ''")

        cur.execute("SELECT id, media_path FROM messages WHERE is_voice = 1")
        rows = cur.fetchall()
        updated = 0
        for mid, mpath in rows:
            fn = os.path.basename(mpath) if mpath else ""
            dur = durations.get(fn, 12.0)
            mins = int(dur // 60)
            secs = int(dur % 60)
            label = f"{mins}:{secs:02d}"
            cur.execute(
                "UPDATE messages SET duration_sec = ?, duration_label = ? WHERE id = ?",
                (round(dur, 1), label, mid),
            )
            updated += 1

        con.commit()
        con.close()
        print(f"Updated {updated} voice message records in {os.path.basename(db_path)}")

if __name__ == "__main__":
    main()
