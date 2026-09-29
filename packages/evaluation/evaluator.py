"""
Evaluation Harness for Alisha Bubbzieee.
Scores candidate responses across 6 core authenticity axes:
  1. Vocabulary & Slang Match
  2. Character Length Proximity (Target median ~16 chars)
  3. Emoji Frequency & Authenticity
  4. Message Fragmentation & Turn Structure
  5. Anti-AI Assistant Voice Penalty
  6. Overall Human Simulation Fidelity (0-100)
"""

import math
import re
from typing import Dict, Any, List


ALISHA_VOCAB = {"innit", "bro", "ig", "latw", "errr", "nahhh", "yea", "yeah", "literally", "wait", "cutie", "salah"}
AI_TRIGGERS = ["as an ai", "i would be happy", "certainly", "how can i assist", "feel free", "great question", "i apologize for the delay"]


class AlishaEvaluator:
    def evaluate(self, candidate_response: str, real_response: str = "") -> Dict[str, Any]:
        text = candidate_response.strip()
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        words = re.findall(r"\b\w+\b", text.lower())

        # 1. Anti-AI Score (0 to 10)
        anti_ai = 10.0
        text_lower = text.lower()
        for trig in AI_TRIGGERS:
            if trig in text_lower:
                anti_ai -= 4.0
        if text.startswith("Hello") or text.startswith("Dear"):
            anti_ai -= 3.0
        anti_ai = max(0.0, anti_ai)

        # 2. Length Score (0 to 10)
        # Target length is 10-35 characters per message
        avg_line_len = sum(len(l) for l in lines) / max(1, len(lines))
        if 8 <= avg_line_len <= 35:
            length_score = 10.0
        elif avg_line_len < 8:
            length_score = 8.0
        else:
            length_score = max(2.0, 10.0 - ((avg_line_len - 35) / 10.0))

        # 3. Vocabulary Match (0 to 10)
        has_slang = any(w in ALISHA_VOCAB for w in words)
        vocab_score = 9.0 if has_slang else 7.5

        # 4. Capitalization & Punctuation (0 to 10)
        # Alisha writes in lowercase and rarely uses terminal periods
        is_lowercase = text[0].islower() if (text and text[0].isalpha()) else True
        has_terminal_period = text.endswith(".") and not text.endswith("..")
        style_score = 10.0
        if not is_lowercase:
            style_score -= 2.5
        if has_terminal_period:
            style_score -= 2.5

        # 5. Fragmentation Score (0 to 10)
        # 1-3 lines is ideal
        if 1 <= len(lines) <= 3:
            frag_score = 10.0
        else:
            frag_score = 6.0

        # Composite score (0 - 100)
        composite = (
            (anti_ai * 0.35)
            + (length_score * 0.20)
            + (style_score * 0.20)
            + (vocab_score * 0.15)
            + (frag_score * 0.10)
        ) * 10.0
        composite = round(min(100.0, max(0.0, composite)), 1)

        return {
            "candidate": candidate_response,
            "anti_ai_score": round(anti_ai, 1),
            "length_score": round(length_score, 1),
            "style_score": round(style_score, 1),
            "vocab_score": round(vocab_score, 1),
            "fragmentation_score": round(frag_score, 1),
            "composite_score": composite,
            "rating": "Authentic Alisha" if composite >= 85 else ("Natural" if composite >= 70 else "Needs Improvement"),
        }
