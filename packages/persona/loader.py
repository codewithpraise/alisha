"""
Fast Profile Loader for Persona Intelligence.

Loads all pre-computed persona profiles from the persona/ directory.
Caches them in memory so repeated access is O(1).
If profiles don't exist, runs the analyzer first.
"""

import json
import os
from typing import Dict, Any, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PERSONA_DIR = os.path.join(ROOT, "persona")

_CACHE: Dict[str, Any] = {}
_LOADED = False


def _load_json(filename: str) -> Any:
    path = os.path.join(PERSONA_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _ensure_loaded():
    global _LOADED
    if _LOADED:
        return

    # Check if persona dir exists and has profiles
    if not os.path.exists(PERSONA_DIR) or not os.path.exists(
        os.path.join(PERSONA_DIR, "profile.json")
    ):
        print("[PersonaLoader] Profiles not found — running analyzer...")
        try:
            from packages.persona.analyzer import run_full_analysis
            run_full_analysis()
        except Exception as e:
            print(f"[PersonaLoader] Analyzer failed: {e}")
            # Provide safe defaults
            _CACHE["profile"] = _default_profile()
            _LOADED = True
            return

    files = [
        "profile", "statistics", "lexical_profile", "emoji_profile",
        "slang_profile", "punctuation_profile", "burst_profile",
        "response_act_profile", "address_terms", "humor_profile",
        "topic_profiles", "temporal_profiles",
    ]
    for key in files:
        data = _load_json(f"{key}.json")
        if data is not None:
            _CACHE[key] = data

    _LOADED = True


def get_profile() -> Dict[str, Any]:
    _ensure_loaded()
    return _CACHE.get("profile", _default_profile())


def get_statistics() -> Dict[str, Any]:
    _ensure_loaded()
    return _CACHE.get("statistics", {})


def get_lexical_profile() -> Dict[str, Any]:
    _ensure_loaded()
    return _CACHE.get("lexical_profile", {})


def get_emoji_profile() -> Dict[str, Any]:
    _ensure_loaded()
    return _CACHE.get("emoji_profile", {
        "emoji_rate": 0.087,
        "characteristic_emojis": ["😭", "💀", "❤️", "💪🏽"],
        "standalone_rate": 0.4,
    })


def get_slang_profile() -> Dict[str, Any]:
    _ensure_loaded()
    return _CACHE.get("slang_profile", {"top_terms": [
        "yeah", "okay", "idk", "ig", "hmm", "bro", "nah", "tbh", "ngl"
    ]})


def get_burst_profile() -> Dict[str, Any]:
    _ensure_loaded()
    return _CACHE.get("burst_profile", {
        "mean_burst_size": 2.52,
        "double_text_probability": 0.54,
        "triple_text_probability": 0.29,
    })


def get_response_act_profile() -> Dict[str, Any]:
    _ensure_loaded()
    return _CACHE.get("response_act_profile", {
        "dominant_acts": ["acknowledgment", "reaction", "agreement"],
    })


def get_address_terms() -> Dict[str, Any]:
    _ensure_loaded()
    return _CACHE.get("address_terms", {
        "pet_names": ["cutie", "babycakes", "pookie"],
        "casual_address": ["bro", "cuh", "lad"],
    })


def get_humor_profile() -> Dict[str, Any]:
    _ensure_loaded()
    return _CACHE.get("humor_profile", {
        "dominant_humor_type": "teasing",
    })


def get_topic_profiles() -> Dict[str, Any]:
    _ensure_loaded()
    return _CACHE.get("topic_profiles", {})


def get_temporal_profiles() -> Dict[str, Any]:
    _ensure_loaded()
    return _CACHE.get("temporal_profiles", {})


def get_characteristic_emojis() -> list:
    return get_emoji_profile().get("characteristic_emojis", ["😭", "💀", "❤️"])


def get_top_slang() -> list:
    return get_slang_profile().get("top_terms", [])[:20]


def get_median_length_chars() -> int:
    stats = get_statistics()
    return stats.get("message_length", {}).get("chars", {}).get("median", 26)


def get_p90_length_chars() -> int:
    stats = get_statistics()
    return stats.get("message_length", {}).get("chars", {}).get("p90", 79)


def get_emoji_rate() -> float:
    return get_emoji_profile().get("emoji_rate", 0.087)


def get_burst_probability() -> float:
    return get_burst_profile().get("double_text_probability", 0.54)


def reload():
    """Force reload of all profiles from disk."""
    global _LOADED
    _CACHE.clear()
    _LOADED = False
    _ensure_loaded()


def _default_profile() -> Dict[str, Any]:
    """Safe fallback when profiles haven't been computed yet."""
    return {
        "version": "0.0.0-default",
        "persona_name": "Alisha",
        "style_summary": {
            "dominant_style": "lowercase casual British/Pakistani slang",
            "dominant_response_acts": ["acknowledgment", "reaction"],
            "top_slang": ["yeah", "okay", "idk", "ig", "hmm", "bro"],
            "top_emojis": ["😭", "💀", "❤️"],
            "message_length_class": "short",
        },
        "generation_constraints": {
            "target_length_chars": {
                "median": 26,
                "typical_high": 79,
                "soft_max": 115,
            },
            "burst_probability": 0.54,
            "emoji_probability": 0.087,
            "capitalization_probability": 0.028,
        },
    }
