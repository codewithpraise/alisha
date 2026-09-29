"""
Deterministic Policy & Controller for Alisha Bubbzieee.
Runs purely in deterministic code and heuristics (zero LLM overhead, zero Laya).
Responsibilities:
- Detect explicit memory requests
- Determine retrieval depth (0 for casual greeting, 3-5 normal, 6-8 deep recall)
- Select style retrieval mode (neutral, playful, teasing, affectionate, serious, comforting, explanatory, annoyed)
- Choose response length (short fragmented messages)
- Determine whether voice is requested
- Hard-limit burst decisions to maximum 1 optional second message
- Enforce safety and anti-repetition policies
"""

import re
from typing import Dict, Any, List, Optional


class PolicyDecision:
    def __init__(
        self,
        is_explicit_memory_request: bool,
        retrieval_depth: int,
        style_mode: str,
        max_response_tokens: int,
        is_voice_requested: bool,
        permit_second_burst: bool,
    ):
        self.is_explicit_memory_request = is_explicit_memory_request
        self.retrieval_depth = retrieval_depth
        self.style_mode = style_mode
        self.max_response_tokens = max_response_tokens
        self.is_voice_requested = is_voice_requested
        self.permit_second_burst = permit_second_burst

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_explicit_memory_request": self.is_explicit_memory_request,
            "retrieval_depth": self.retrieval_depth,
            "style_mode": self.style_mode,
            "max_response_tokens": self.max_response_tokens,
            "is_voice_requested": self.is_voice_requested,
            "permit_second_burst": self.permit_second_burst,
        }


class DeterministicPolicy:
    def __init__(self):
        # Explicit memory recall patterns
        self.explicit_memory_regex = re.compile(
            r"\b(do you remember|remember when|what did (?:i|you) say|when did we|who was|where did we|tell me about the time)\b",
            re.IGNORECASE,
        )
        # Voice note inquiry patterns
        self.voice_request_regex = re.compile(
            r"\b(send a voice|voice note|send audio|vn|say it in audio|call me|speak to me)\b",
            re.IGNORECASE,
        )
        # Casual greetings that need 0 retrieval depth
        self.greeting_regex = re.compile(
            r"^(hi|hey|heyy|yo|sup|hello|salam|salaam|asalam|assalamu alaikum|assalamualaikum)[!?. ]*$",
            re.IGNORECASE,
        )

    def evaluate(
        self,
        user_input: str,
        recent_history: Optional[List[Dict[str, str]]] = None,
        is_voice_input: bool = False,
    ) -> PolicyDecision:
        clean = user_input.strip().lower()

        # 1. Explicit memory request detection & retrieval depth
        is_explicit_memory = bool(self.explicit_memory_regex.search(clean))
        is_greeting = bool(self.greeting_regex.match(clean))

        if is_greeting:
            retrieval_depth = 0
        elif is_explicit_memory:
            retrieval_depth = 6
        elif any(w in clean for w in ["why", "what", "how", "when", "tell me"]):
            retrieval_depth = 5
        else:
            retrieval_depth = 3

        # 2. Select Style Mode from 8 canonical modes
        if any(w in clean for w in ["latw", "typo", "lmao", "making fun", "stop laughing", "spell"]):
            style_mode = "teasing"
        elif any(w in clean for w in ["salah", "prayer", "deen", "allah", "sin", "dawah", "dua", "jannah", "niyyah", "quran", "namaz"]):
            style_mode = "serious"
        elif any(w in clean for w in ["cutie", "love you", "miss you", "ily", "pretty", "cute", "adore"]):
            style_mode = "affectionate"
        elif any(w in clean for w in ["stressed", "depressed", "sad", "crying", "anxious", "deadline", "hard time", "exhausted"]):
            style_mode = "comforting"
        elif any(w in clean for w in ["where were you", "why didn't you", "busy with", "what took so long", "what happened"]):
            style_mode = "explanatory"
        elif any(w in clean for w in ["annoying", "shut up", "leave me", "hate you", "go away"]):
            style_mode = "annoyed"
        elif any(w in clean for w in ["innit", "bro", "look at this", "check this", "💀", "😭", "meme", "joke"]):
            style_mode = "playful"
        else:
            style_mode = "neutral"

        # 3. Response Length
        if style_mode in ["explanatory", "serious", "comforting"] or is_explicit_memory:
            max_tokens = 90
        elif style_mode in ["teasing", "playful"]:
            max_tokens = 45
        else:
            max_tokens = 40

        # 4. Voice Request Determination
        is_voice_requested = is_voice_input or bool(self.voice_request_regex.search(clean))

        # 5. Deterministic Burst Decision (Hard-limited to max 1 optional second message)
        # Alisha naturally double-texts only when teasing, sharing a sudden reaction, or laughing
        permit_burst = style_mode in ["teasing", "playful", "affectionate"] and not is_voice_requested

        return PolicyDecision(
            is_explicit_memory_request=is_explicit_memory,
            retrieval_depth=retrieval_depth,
            style_mode=style_mode,
            max_response_tokens=max_tokens,
            is_voice_requested=is_voice_requested,
            permit_second_burst=permit_burst,
        )

    def evaluate_second_burst(self, primary_response: str, style_mode: str) -> Optional[str]:
        """
        Hard-limits burst generation.
        Returns an optional short secondary burst message (e.g. an emoji or reaction)
        only if appropriate, without letting the LLM generate runaway turns.
        """
        clean_resp = primary_response.strip().lower()

        # If primary message is already a short reaction, never burst
        if len(clean_resp) < 6:
            return None

        # Style-driven secondary burst
        if style_mode == "teasing":
            if "latw" in clean_resp or "typo" in clean_resp:
                return "stop making fun of my typos 😭"
            return "💀💀"
        elif style_mode == "playful":
            if "bro" in clean_resp and "😭" not in clean_resp:
                return "😭"
            return None
        elif style_mode == "affectionate":
            if "❤️" not in clean_resp:
                return "❤️"
            return None

        return None
