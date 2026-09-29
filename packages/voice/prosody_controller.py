"""
Prosody Controller for Alisha Bubbzieee Voice Synthesis.
Translates message text, emojis, and emotional state into acoustic synthesis parameters:
emotion, energy, speaking rate (speed), and delivery mode for Qwen3-TTS.
"""

from typing import Dict, Any


EMOTION_MAP = {
    "💀": {"emotion": "amused", "energy": 0.8, "speed": 1.12, "delivery": "casual"},
    "😭": {"emotion": "playful_dramatic", "energy": 0.75, "speed": 1.05, "delivery": "expressive"},
    "❤️": {"emotion": "warm", "energy": 0.5, "speed": 0.95, "delivery": "intimate"},
    "💪🏽": {"emotion": "supportive", "energy": 0.85, "speed": 1.02, "delivery": "upbeat"},
    "🤨": {"emotion": "skeptical_teasing", "energy": 0.6, "speed": 0.92, "delivery": "deadpan"},
    "😜": {"emotion": "teasing", "energy": 0.8, "speed": 1.1, "delivery": "playful"},
    "default": {"emotion": "neutral_casual", "energy": 0.62, "speed": 1.0, "delivery": "casual"},
}


def get_prosody_for_text(text: str) -> Dict[str, Any]:
    """
    Analyzes text and returns the optimal TTS parameters.
    """
    t = text.lower()

    # Check for emojis
    for emoji, config in EMOTION_MAP.items():
        if emoji != "default" and emoji in text:
            return config

    # Text keyword heuristics
    if any(w in t for w in ["nahhh", "bro", "innit", "lol", "lmao", "latw"]):
        return {"emotion": "amused", "energy": 0.78, "speed": 1.08, "delivery": "casual"}
    if any(w in t for w in ["cutie", "love", "ameen", "dua", "allah", "bless"]):
        return {"emotion": "warm", "energy": 0.52, "speed": 0.94, "delivery": "intimate"}
    if any(w in t for w in ["wait", "listen", "literally", "okay so"]):
        return {"emotion": "eager", "energy": 0.82, "speed": 1.15, "delivery": "expressive"}
    if any(w in t for w in ["tired", "sleep", "errr", "busy"]):
        return {"emotion": "relaxed", "energy": 0.45, "speed": 0.92, "delivery": "casual"}

    return dict(EMOTION_MAP["default"])
