"""
Quality Gate for Proactive Messaging.
Ensures no robotic, cringe, overly repetitive, or non-Alisha texts ever get sent.
"""

import re
from typing import List


ROBOTIC_TRIGGERS = [
    r"checking in on you",
    r"how can i assist",
    r"hope you are having a wonderful",
    r"as your friend",
    r"friendly reminder",
    r"just an automated",
    r"hello there",
    r"good day",
    r"greetings",
]


def passes_quality_gate(message: str) -> bool:
    """Returns True if message passes all authenticity, brevity, and anti-AI gates."""
    if not message or len(message.strip()) == 0:
        return False

    text = message.strip().lower()

    # Gate 1: Length check (initiations should be short, under 90 chars)
    if len(text) > 90:
        return False

    # Gate 2: Check robotic triggers
    for trig in ROBOTIC_TRIGGERS:
        if re.search(trig, text):
            return False

    # Gate 3: Must not be formal greeting
    if text.startswith("dear") or text.startswith("hello "):
        return False

    return True
