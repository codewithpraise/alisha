"""
Message Compositor for Alisha Bubbzieee.
Splits raw LLM output into realistic multiple chat bursts,
calculates realistic human typing delays, and handles voice-note thresholds.
"""

import math
import random
import re
from typing import List, Dict, Any

from packages.inference.style_filter import enforce_alisha_style


class MessageCompositor:
    def __init__(self, profile: Dict[str, Any]):
        self.profile = profile
        self.metrics = profile.get("linguistic_metrics", {})
        self.double_text_prob = self.metrics.get("double_text_probability", 0.53)
        self.vn_threshold = profile.get("social_metrics", {}).get(
            "voice_note_preference_threshold_chars", 80
        )

    def compose(self, raw_text: str) -> List[Dict[str, Any]]:
        """
        Transforms raw text into a sequence of fragmented messages with typing delays.
        """
        styled = enforce_alisha_style(raw_text)
        if not styled:
            styled = "💀"

        # Check if Alisha would have preferred sending a voice note
        is_voice_note = len(styled) >= self.vn_threshold and random.random() < 0.65

        # Split into fragments
        raw_lines = [l.strip() for l in styled.split("\n") if l.strip()]
        fragments: List[str] = []

        for line in raw_lines:
            # If line is longer than 50 chars, split on natural break words
            if len(line) > 50 and any(w in line for w in [" wait ", " also ", " but ", " and then ", " like "]):
                parts = re.split(r"(?=\b(?:wait|also|and then|like)\b)", line)
                for p in parts:
                    if p.strip():
                        fragments.append(p.strip())
            else:
                fragments.append(line)

        # Enforce burst size (1 to 3 messages)
        if len(fragments) == 1 and random.random() < self.double_text_prob:
            # Occasionally split on comma or append typical Alisha reaction
            words = fragments[0].split()
            if len(words) >= 6:
                mid = len(words) // 2
                f1 = " ".join(words[:mid])
                f2 = " ".join(words[mid:])
                fragments = [f1, f2]
            elif random.random() < 0.35:
                top_emojis = self.metrics.get("top_emojis", ["💀", "😭"])
                fragments.append(random.choice(top_emojis))

        # Build message objects with realistic typing delays
        composed_messages = []
        for i, frag in enumerate(fragments):
            char_len = len(frag)
            # Simulated typing: ~35ms per character + base hesitation
            typing_delay_ms = int(max(600, min(3200, 450 + char_len * 38 + random.randint(100, 300))))
            
            composed_messages.append({
                "index": i,
                "content": frag,
                "typing_delay_ms": typing_delay_ms,
                "message_type": "voice" if (is_voice_note and i == 0) else "text",
                "audio_url": "/voice/1303735758283391.wav" if is_voice_note else None,
            })

        return composed_messages
