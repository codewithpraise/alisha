"""
Memory Seeder for Alisha Bubbzieee.
Processes messages/messages.jsonl to initialize data/memory.db with schema,
past message history, and synthesized episodic, semantic, relational, and ongoing memories.
"""

import json
import os
import re
import sqlite3
import sys
import time
from typing import List, Dict, Any

current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if root not in sys.path:
    sys.path.insert(0, root)

from packages.personality.fingerprint import fix_instagram_encoding, is_system_or_reaction
from packages.memory.retriever import text_to_dense_vector



def init_database(db_path: str, schema_path: str):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def seed_database_from_messages(
    messages_path: str, db_path: str, schema_path: str
) -> Dict[str, int]:
    init_database(db_path, schema_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Clear existing
    cursor.execute("DELETE FROM memories")
    cursor.execute("DELETE FROM messages")
    cursor.execute("DELETE FROM conversations")
    cursor.execute("DELETE FROM friend_state")

    # Load messages
    with open(messages_path, "r", encoding="utf-8") as f:
        raw_lines = [json.loads(line) for line in f if line.strip()]

    raw_lines.sort(key=lambda x: x.get("timestamp_ms", 0))

    conversations = []
    current_conv_id = f"conv_{int(time.time())}_0"
    current_conv_msgs = []
    last_ts = 0

    valid_messages = []
    for idx, raw in enumerate(raw_lines):
        content = fix_instagram_encoding(raw.get("content", ""))
        sender = fix_instagram_encoding(raw.get("sender_name", ""))
        ts = raw.get("timestamp_ms", 0)

        if is_system_or_reaction(content):
            continue

        role = "alisha" if (sender == "اليشا" or "alisha" in sender.lower()) else "user"

        # Session gap > 4 hours implies a new conversation
        if last_ts > 0 and (ts - last_ts) > (4 * 3600 * 1000):
            conv_id = f"conv_{len(conversations)}"
            conversations.append({
                "id": conv_id,
                "started_at": current_conv_msgs[0]["timestamp"] if current_conv_msgs else last_ts,
                "ended_at": last_ts,
                "turn_count": len(current_conv_msgs),
            })
            current_conv_id = f"conv_{len(conversations)}"
            current_conv_msgs = []

        msg_id = f"msg_{idx}"
        msg_obj = {
            "id": msg_id,
            "conversation_id": current_conv_id,
            "role": role,
            "content": content,
            "timestamp": ts,
            "message_type": "text",
        }
        current_conv_msgs.append(msg_obj)
        valid_messages.append(msg_obj)
        last_ts = ts

    if current_conv_msgs:
        conv_id = f"conv_{len(conversations)}"
        conversations.append({
            "id": conv_id,
            "started_at": current_conv_msgs[0]["timestamp"],
            "ended_at": last_ts,
            "turn_count": len(current_conv_msgs),
        })

    # Insert conversations
    for c in conversations:
        cursor.execute(
            "INSERT OR REPLACE INTO conversations (id, started_at, ended_at, turn_count) VALUES (?, ?, ?, ?)",
            (c["id"], c["started_at"], c["ended_at"], c["turn_count"]),
        )

    # Insert messages
    for m in valid_messages:
        cursor.execute(
            "INSERT OR REPLACE INTO messages (id, conversation_id, role, content, timestamp, message_type) VALUES (?, ?, ?, ?, ?, ?)",
            (m["id"], m["conversation_id"], m["role"], m["content"], m["timestamp"], m["message_type"]),
        )

    # Synthesize core memories (episodic, semantic, relational, ongoing)
    cur_time = int(time.time())
    preloaded_memories = [
        # Episodic
        {
            "id": "mem_ep_01",
            "type": "episodic",
            "content": "Talked about staying away from sins, doing dawah, praying salah on time, and dhikr. Alisha reacted with hearts.",
            "source": "real_conversation",
            "confidence": 1.0,
            "keywords": "deen, salah, dawah, sins, heart, prayer",
        },
        {
            "id": "mem_ep_02",
            "type": "episodic",
            "content": "Joked about being late ('latw') and forgetting about things. Alisha sent a voice note laughing about it.",
            "source": "real_conversation",
            "confidence": 0.98,
            "keywords": "late, latw, voice note, forgot, laugh",
        },
        {
            "id": "mem_ep_03",
            "type": "episodic",
            "content": "Listened to songs together and talked about 'hot and cold situation innit' like Katy Perry.",
            "source": "real_conversation",
            "confidence": 0.95,
            "keywords": "song, hot and cold, music, innit",
        },
        {
            "id": "mem_ep_04",
            "type": "episodic",
            "content": "Deep conversation about holding on to feelings, caring for each other, and praying for each other's rizq and jannat-ul-firdous.",
            "source": "real_conversation",
            "confidence": 0.99,
            "keywords": "feelings, dua, rizq, jannah, care",
        },
        # Semantic
        {
            "id": "mem_sem_01",
            "type": "semantic",
            "content": "Alisha writes predominantly in lowercase, rarely capitalizes, and prefers sending rapid short bursts instead of paragraphs.",
            "source": "inference",
            "confidence": 1.0,
            "keywords": "style, typing, lowercase, bursts",
        },
        {
            "id": "mem_sem_02",
            "type": "semantic",
            "content": "Alisha uses voice notes whenever she wants to tell a longer funny story or elaborate on something.",
            "source": "inference",
            "confidence": 0.95,
            "keywords": "voice note, audio, story",
        },
        {
            "id": "mem_sem_03",
            "type": "semantic",
            "content": "Top expressive emojis are 😭, 💪🏽, 💀, 🤨, and heart reactions.",
            "source": "real_conversation",
            "confidence": 0.98,
            "keywords": "emojis, reactions, skull, cry",
        },
        # Relational
        {
            "id": "mem_rel_01",
            "type": "relational",
            "content": "Playful, affectionate teasing dynamic. Uses words like 'bro', 'innit', 'cutie', 'ig'.",
            "source": "real_conversation",
            "confidence": 1.0,
            "keywords": "teasing, affection, bro, cutie, dynamic",
        },
        # Ongoing threads
        {
            "id": "mem_ong_01",
            "type": "ongoing",
            "content": "Checking in on studies and how her day went.",
            "source": "inference",
            "confidence": 0.90,
            "keywords": "studies, check-in, day",
        },
        {
            "id": "mem_ong_02",
            "type": "ongoing",
            "content": "Follow up on the thing she was busy with earlier.",
            "source": "inference",
            "confidence": 0.88,
            "keywords": "busy, follow-up, update",
        },
    ]

    for mem in preloaded_memories:
        emb = text_to_dense_vector(mem["content"] + " " + mem["keywords"])
        cursor.execute(
            """INSERT OR REPLACE INTO memories 
               (id, content, type, source, confidence, created_at, last_accessed, access_count, keywords, embedding)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                mem["id"],
                mem["content"],
                mem["type"],
                mem["source"],
                mem["confidence"],
                cur_time,
                cur_time,
                0,
                mem["keywords"],
                json.dumps(emb),
            ),
        )

    # Initialize friend_state
    cursor.execute(
        """INSERT OR REPLACE INTO friend_state 
           (id, conversation_state, current_topic, unfinished_threads, recent_emotional_context, initiation_probability, teasing_level, energy, verbosity, last_updated)
           VALUES (1, 'active', 'reconnection', '["how her day is going", "studies update"]', 'warm and playfully teasing', 0.57, 0.55, 0.65, 0.35, ?)""",
        (cur_time,),
    )

    conn.commit()
    conn.close()

    print(f"Database seeded successfully: {len(valid_messages)} messages, {len(conversations)} conversations, {len(preloaded_memories)} memories.")
    return {
        "messages": len(valid_messages),
        "conversations": len(conversations),
        "memories": len(preloaded_memories),
    }


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    msg_path = os.path.join(root, "messages", "messages.jsonl")
    db_path = os.path.join(root, "data", "memory.db")
    schema_path = os.path.join(root, "packages", "memory", "schema.sql")

    seed_database_from_messages(msg_path, db_path, schema_path)
