"""
Context Builder for Alisha Bubbzieee.
Constructs strict system prompts, injects retrieved memories, relationship state,
conversation history, and style instructions.
"""

import json
import os
import sys
from typing import Dict, Any, List

current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if root not in sys.path:
    sys.path.insert(0, root)

from packages.memory.retriever import MemoryRetriever


class ContextBuilder:
    def __init__(self, profile_path: str, db_path: str):
        with open(profile_path, "r", encoding="utf-8") as f:
            self.profile = json.load(f)
        self.retriever = MemoryRetriever(db_path)

    def build_prompt(
        self,
        current_user_message: str,
        recent_history: List[Dict[str, str]],
    ) -> str:
        """
        Assembles full prompt for Qwen3.5-2B / local LLM.
        """
        # 1. Retrieve relevant memories
        memories = self.retriever.search_memories(current_user_message, top_k=4)
        memories_text = "\n".join(
            f"- [{m['type'].upper()}] {m['content']}" for m in memories
        ) if memories else "- No specific memory retrieved."

        # 2. Ongoing threads & friend state
        state = self.retriever.get_friend_state()
        unfinished = state.get("unfinished_threads", "[]")

        # 3. System Persona & Behavioral Directives
        system_prompt = f"""You are Alisha ({self.profile.get('handle', '@iishazsr')}).
You are texting your close friend. This is an intimate, real Instagram/iMessage chat.

STRICT BEHAVIOR RULES (CRITICAL):
- Never, EVER act like an AI, assistant, or bot. No helpfulness cliches, no "I hope this helps", no "How can I assist you".
- Write primarily in lowercase. Rare capitalization.
- Keep replies SHORT. Median message length is 15-20 characters. Avoid long essays.
- You speak British/Pakistani casual English: use natural slang like "innit", "bro", "ig", "nahhh", "yea", "latw".
- Emojis you naturally use: 💀, 😭, 💪🏽, 🤨. Single emojis or words like "💀" or "nahhh" are completely valid full replies.
- Fragment thoughts across multiple short lines.
- You tease affectionately, share laughs, and remember faith/deen discussions (salah, dawah) and inside jokes.

RELEVANT MEMORIES ABOUT YOU & FRIEND:
{memories_text}

RELATIONSHIP STATE:
- Current mood: {state.get('recent_emotional_context', 'warm and teasing')}
- Energy level: {state.get('energy', 0.6)}
- Open threads: {unfinished}
"""

        # 4. History formatting
        formatted_history = []
        for turn in recent_history[-8:]:
            role_tag = "Friend" if turn["role"] == "user" else "Alisha"
            formatted_history.append(f"{role_tag}: {turn['content']}")

        formatted_history.append(f"Friend: {current_user_message}")
        formatted_history.append("Alisha:")

        full_prompt = f"{system_prompt}\n\nCONVERSATION HISTORY:\n" + "\n".join(formatted_history)
        return full_prompt
