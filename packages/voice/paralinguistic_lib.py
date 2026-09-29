"""
Paralinguistic Audio Library for Alisha Bubbzieee.
Manages non-verbal human vocalizations (sighs, chuckles, throat clear, laughter)
extracted from natural audio clips to insert dynamically into voice synthesis.
"""

import os
from typing import Dict, Any, List, Optional


PARALINGUISTIC_TOKENS = {
    "<sigh>": {
        "description": "Soft thoughtful sigh",
        "duration_sec": 0.85,
        "sample_file": "voice/1125435969717032.wav",
        "context": "when thinking about work or tiredness",
    },
    "<chuckle>": {
        "description": "Short burst laugh / heh",
        "duration_sec": 0.62,
        "sample_file": "voice/1168958751922864.wav",
        "context": "when reacting to jokes or skull emoji",
    },
    "<hesitation>": {
        "description": "errr / thinking vocalization",
        "duration_sec": 0.74,
        "sample_file": "voice/1242969967588294.wav",
        "context": "before answering a question",
    },
    "<breath_in>": {
        "description": "Audible intake of breath before speaking",
        "duration_sec": 0.45,
        "sample_file": "voice/1278103253999696.wav",
        "context": "at start of sentence",
    },
}


def get_token_for_context(emotion: str) -> Optional[str]:
    """Returns appropriate paralinguistic token for emotional context."""
    if emotion == "amused":
        return "<chuckle>"
    elif emotion == "relaxed" or emotion == "tired":
        return "<sigh>"
    elif emotion == "eager":
        return "<breath_in>"
    return None


def get_token_metadata(token: str) -> Optional[Dict[str, Any]]:
    return PARALINGUISTIC_TOKENS.get(token)
