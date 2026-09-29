"""
Style Filter for Alisha Bubbzieee.
Enforces authentic human friend tone and strips away AI assistant artifacts.
"""

import re
from typing import List


BANNED_AI_PATTERNS = [
    r"as an ai",
    r"language model",
    r"how can i (help|assist)",
    r"i'd be (happy|glad) to",
    r"is there anything else",
    r"feel free to ask",
    r"certainly!",
    r"absolutely!",
    r"i understand that you",
    r"i hope this (helps|finds you well)",
    r"let me know if you need",
    r"that's a great question",
    r"as mentioned earlier",
]


def clean_ai_artifacts(text: str) -> str:
    """Removes robotic / assistant phrases from generated text."""
    cleaned = text.strip()
    for pat in BANNED_AI_PATTERNS:
        cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE).strip()

    # Clean leading "Alisha:" or quotes
    cleaned = re.sub(r"^(alisha|iishazsr):\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip("\"' ")
    return cleaned


def enforce_alisha_style(text: str, capitalization_prob: float = 0.03) -> str:
    """
    Applies Alisha's linguistic fingerprint:
    predominantly lowercase, no forced terminal periods.
    """
    cleaned = clean_ai_artifacts(text)
    if not cleaned:
        return "💀"

    # Lowercase dominant
    lines = cleaned.split("\n")
    processed_lines = []
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        # Convert first character to lowercase unless it's an acronym
        words = line_clean.split()
        if words and len(words[0]) > 1 and words[0].isupper():
            pass  # keep acronyms like LOL or WTF
        else:
            line_clean = line_clean[0].lower() + line_clean[1:] if len(line_clean) > 0 else ""

        # Remove trailing formal period
        if line_clean.endswith(".") and not line_clean.endswith(".."):
            line_clean = line_clean[:-1]

        processed_lines.append(line_clean)

    return "\n".join(processed_lines)
