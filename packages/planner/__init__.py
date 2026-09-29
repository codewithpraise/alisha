"""
Response Behavior Planner for Alisha AI Friend.

This is the critical component that converts retrieved evidence into a structured
plan BEFORE generation. Without this, RAG is merely decorative.

The planner outputs a ResponseBehaviorPlan that tells the generator:
- What conversational act to perform
- How long the response should be
- Whether to include emojis (and which ones are appropriate)
- What slang level is appropriate
- What emotional tone to use
- Whether to burst
- Which exemplars are most relevant
- What to explicitly avoid

All decisions are conditioned on:
  current context × emotion × speech act × topic × relationship mode
"""

import re
import random
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

from packages.persona import loader as persona_loader


# ── Response act taxonomy ─────────────────────────────────────────────────────

RESPONSE_ACTS = [
    "reaction",         # "omg", "💀", "no way"
    "answer",           # direct factual/opinion answer
    "question",         # asking the user something
    "follow_up",        # continuing / drilling deeper
    "agreement",        # "yeah", "fr", "exactly"
    "disagreement",     # "nah", "nope"
    "teasing",          # "kidding", "smh"
    "playful_insult",   # affectionate mock
    "affection",        # "cutie", "❤️"
    "reassurance",      # "it's okay", "you got this"
    "comfort",          # empathetic support
    "encouragement",
    "humor",
    "explanation",      # longer answer with reasoning
    "correction",       # "actually..."
    "acknowledgment",   # "oh", "hmm", "ah"
    "surprise",
    "excitement",
    "farewell",
    "greeting",
    "topic_shift",
    "continuation",
]


# ── Interaction modes ─────────────────────────────────────────────────────────

INTERACTION_MODES = [
    "neutral",
    "casual",
    "playful",
    "teasing",
    "affectionate",
    "supportive",
    "serious",
    "excited",
    "annoyed",
    "low_energy",
    "farewell",
]


# ── Length classes ────────────────────────────────────────────────────────────

LENGTH_CLASSES = {
    "one_word":   (1, 6),
    "very_short": (4, 20),
    "short":      (15, 45),
    "medium":     (40, 90),
    "long":       (80, 150),
    "very_long":  (140, 300),
}


@dataclass
class ResponseBehaviorPlan:
    """
    Structured pre-generation plan.
    All fields are data-driven, not guessed.
    """
    # Core mode
    interaction_mode: str = "casual"

    # Speech act(s) the response should perform
    speech_acts: List[str] = field(default_factory=lambda: ["acknowledgment"])

    # Length targeting
    length_class: str = "medium"
    target_chars_min: int = 25
    target_chars_max: int = 180
    target_chars_soft_max: int = 280  # allow multi-bubble natural bursts

    # Burst behavior
    burst_count: int = 3  # how many messages to emit
    burst_probability: float = 0.54

    # Emoji
    emoji_policy: str = "optional"  # "none", "optional", "encouraged", "standalone_ok"
    emoji_candidates: List[str] = field(default_factory=list)

    # Slang
    slang_level: float = 0.7  # 0.0 = none, 1.0 = maximum

    # Warmth/teasing
    warmth: float = 0.7
    teasing_intensity: float = 0.3
    seriousness: float = 0.1

    # Capitalization
    capitalize_probability: float = 0.028  # from corpus: 2.8%

    # Address terms
    use_address_term: bool = False
    preferred_address_term: Optional[str] = None

    # Evidence
    historical_exemplar_ids: List[str] = field(default_factory=list)
    relevant_fact_ids: List[str] = field(default_factory=list)
    relevant_memory_ids: List[str] = field(default_factory=list)

    # Constraints
    avoid: List[str] = field(default_factory=lambda: [
        "formal tone",
        "paragraph structure",
        "bullet points",
        "generic assistant phrasing",
        "how can I help",
        "as an AI",
    ])

    # Context signals
    topic: str = "general"
    detected_emotion: str = "neutral"
    is_voice_turn: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_prompt_block(self) -> str:
        """Formats the plan as subtle conversational director guidance."""
        vibe_notes = [f"vibe: {self.interaction_mode}"]
        if self.use_address_term and self.preferred_address_term:
            vibe_notes.append(f"address: {self.preferred_address_term}")
        if self.emoji_candidates and self.emoji_policy in ("encouraged", "optional"):
            vibe_notes.append(f"emojis: {' '.join(self.emoji_candidates[:3])}")
        return f"[RESPONSE BEHAVIOR PLAN | Tone Note: {', '.join(vibe_notes)} | rhythm: {self.burst_count} lively texting lines]"


class ResponseBehaviorPlanner:
    """
    Generates a ResponseBehaviorPlan from:
    - Current user message
    - Conversation context
    - Retrieved exemplars
    - Detected emotion/topic
    - Persona profiles (data-driven)
    """

    def __init__(self):
        self._profile = None
        self._emoji_profile = None
        self._burst_profile = None
        self._act_profile = None
        self._address_terms = None
        self._slang_profile = None

    def _lazy_load(self):
        if self._profile is None:
            self._profile = persona_loader.get_profile()
            self._emoji_profile = persona_loader.get_emoji_profile()
            self._burst_profile = persona_loader.get_burst_profile()
            self._act_profile = persona_loader.get_response_act_profile()
            self._address_terms = persona_loader.get_address_terms()
            self._slang_profile = persona_loader.get_slang_profile()

    def plan(
        self,
        user_message: str,
        context_type: str = "casual",
        emotion: str = "neutral",
        retrieved_exemplars: Optional[List[Dict]] = None,
        retrieved_facts: Optional[List[Dict]] = None,
        retrieved_memories: Optional[List[Dict]] = None,
        is_voice_turn: bool = False,
        turn_number: int = 0,
    ) -> ResponseBehaviorPlan:
        self._lazy_load()

        user_lower = user_message.lower().strip()
        exemplars = retrieved_exemplars or []
        facts = retrieved_facts or []
        memories = retrieved_memories or []

        # ── Determine interaction mode ─────────────────────────────────────
        mode = self._determine_mode(user_lower, context_type, emotion)

        # ── Determine speech acts ──────────────────────────────────────────
        acts = self._determine_speech_acts(user_lower, mode, exemplars)

        # ── Determine length class ─────────────────────────────────────────
        length_class, char_min, char_max = self._determine_length(user_lower, mode, acts, exemplars)

        # ── Burst decision ─────────────────────────────────────────────────
        burst_count = self._determine_burst(mode, acts)

        # ── Emoji policy ───────────────────────────────────────────────────
        emoji_policy, emoji_candidates = self._determine_emoji_policy(mode, acts, context_type)

        # ── Slang level ────────────────────────────────────────────────────
        slang_level = self._determine_slang_level(mode, context_type)

        # ── Warmth and teasing ─────────────────────────────────────────────
        warmth, teasing = self._determine_warmth_teasing(mode)

        # ── Address term ───────────────────────────────────────────────────
        use_address, address_term = self._determine_address_term(mode, turn_number)

        # ── Avoid list ─────────────────────────────────────────────────────
        avoid = self._build_avoid_list(mode)

        # ── Evidence IDs ───────────────────────────────────────────────────
        exemplar_ids = [str(e.get("turn_index", i)) for i, e in enumerate(exemplars[:5])]
        fact_ids = [f.get("id", "") for f in facts[:5]]
        memory_ids = [m.get("id", "") for m in memories[:5]]

        # Allow natural multi-line bursts (3-4 lines of ~50 chars each = ~150-250 chars)
        soft_max = max(260, char_max + 80)

        return ResponseBehaviorPlan(
            interaction_mode=mode,
            speech_acts=acts,
            length_class=length_class,
            target_chars_min=char_min,
            target_chars_max=char_max,
            target_chars_soft_max=soft_max,
            burst_count=burst_count,
            burst_probability=persona_loader.get_burst_probability(),
            emoji_policy=emoji_policy,
            emoji_candidates=emoji_candidates,
            slang_level=slang_level,
            warmth=warmth,
            teasing_intensity=teasing,
            seriousness=1.0 if mode == "serious" else 0.1,
            capitalize_probability=0.028,
            use_address_term=use_address,
            preferred_address_term=address_term,
            historical_exemplar_ids=exemplar_ids,
            relevant_fact_ids=fact_ids,
            relevant_memory_ids=memory_ids,
            avoid=avoid,
            topic=context_type,
            detected_emotion=emotion,
            is_voice_turn=is_voice_turn,
        )

    def _determine_mode(self, user_lower: str, context_type: str, emotion: str) -> str:
        words = set(re.findall(r"\b\w+\b", user_lower))
        # Farewell signals
        if any(w in words for w in ["bye", "gn", "gtg", "ttyl"]) or any(p in user_lower for p in ["good night", "goodnight", "see you"]):
            return "farewell"
        # Greeting signals
        if any(w in words for w in ["hey", "hi", "hello", "salam", "yo", "sup"]):
            return "casual"
        # Affection signals
        if any(w in words for w in ["love", "miss", "cute", "cutie", "ily", "adore", "pretty", "heart"]):
            return "affectionate"
        # Support signals
        if any(w in words for w in ["sad", "cry", "stressed", "anxious", "depressed", "hard"]):
            return "supportive"
        # Serious/faith signals
        if any(w in words for w in ["salah", "dua", "quran", "allah", "pray", "deen", "ameen"]):
            return "serious"
        # Excited signals
        if "!" in user_lower or any(w in words for w in ["omg", "wow", "amazing"]):
            return "excited"
        # Teasing signals
        if any(w in words for w in ["latw", "typo", "spelling", "mistake"]) or "you said" in user_lower:
            return "teasing"
        # Context-based
        ctx_mode_map = {
            "banter": "playful",
            "affection": "affectionate",
            "faith": "serious",
            "sleep_banter": "low_energy",
            "home_life": "casual",
            "cats": "excited",
            "study": "casual",
        }
        return ctx_mode_map.get(context_type, "casual")

    def _determine_speech_acts(
        self, user_lower: str, mode: str, exemplars: List[Dict]
    ) -> List[str]:
        # Check exemplar patterns first
        if exemplars:
            exemplar_acts = []
            for ex in exemplars[:3]:
                acts = ex.get("response_acts", [])
                exemplar_acts.extend(acts)
            if exemplar_acts:
                # Most common acts from relevant exemplars
                from collections import Counter
                top_acts = [a for a, _ in Counter(exemplar_acts).most_common(2)]
                return top_acts

        # Heuristic fallbacks
        if mode == "teasing":
            return ["teasing", "reaction"]
        if mode == "affectionate":
            return ["affection", "acknowledgment"]
        if mode == "supportive":
            return ["comfort", "reassurance"]
        if mode == "serious":
            return ["answer", "acknowledgment"]
        if mode == "excited":
            return ["reaction", "excitement"]
        if mode == "farewell":
            return ["farewell"]
        if mode == "playful":
            return ["reaction", "humor"]

        # Question in user message
        if "?" in user_lower:
            return ["answer", "question"]

        return ["acknowledgment", "continuation"]

    def _determine_length(
        self, user_lower: str, mode: str, acts: List[str], exemplars: List[Dict]
    ):
        # Mode-based defaults (corpus-grounded, multi-bubble friendly)
        mode_lengths = {
            "farewell":    ("medium", 35, 120),
            "teasing":     ("medium", 45, 200),
            "playful":     ("medium", 45, 220),
            "excited":     ("medium", 50, 240),
            "affectionate": ("medium", 40, 180),
            "casual":      ("medium", 45, 200),
            "supportive":  ("medium", 50, 220),
            "serious":     ("medium", 50, 240),
            "low_energy":  ("medium", 35, 140),
            "neutral":     ("medium", 45, 200),
        }

        if "explanation" in acts:
            return "long", 60, 260

        return mode_lengths.get(mode, ("medium", 45, 200))

    def _determine_burst(self, mode: str, acts: List[str]) -> int:
        # Grounded in persona/burst_profile.json (median 2, 1-3 bubbles)
        r = random.random()
        if mode in ["excited", "teasing", "playful"]:
            if r < 0.20:
                return 1
            elif r < 0.70:
                return 2
            else:
                return 3
        elif mode in ["serious", "supportive"]:
            if r < 0.35:
                return 1
            elif r < 0.85:
                return 2
            else:
                return 3
        elif mode in ["farewell", "low_energy"]:
            if r < 0.65:
                return 1
            else:
                return 2
        else:
            # Casual conversation
            if r < 0.45:
                return 1
            elif r < 0.82:
                return 2
            else:
                return 3

    def _determine_emoji_policy(self, mode: str, acts: List[str], context: str):
        emoji_prof = persona_loader.get_emoji_profile()
        characteristic = emoji_prof.get("characteristic_emojis", ["😭", "💀", "❤️", "💪🏽"])
        rate = emoji_prof.get("emoji_rate", 0.087)

        # High-probability contexts
        if mode == "affectionate":
            return "encouraged", ["❤️", "😍", "💞", "😊"]
        if mode == "excited" or "excitement" in acts:
            return "encouraged", ["😭", "😍", "💀", "🤩"]
        if mode == "teasing":
            return "optional", ["💀", "😭", "🤨", "😜"]
        if mode == "serious":
            return "none", []
        if mode == "farewell":
            return "optional", ["❤️", "🙏🏽"]
        if mode == "supportive":
            return "optional", ["❤️", "🙏🏽"]

        # Default: occasional, from characteristic set
        if random.random() < rate * 3:  # ~26% in casual conversation
            return "optional", characteristic[:4]
        return "none", []

    def _determine_slang_level(self, mode: str, context: str) -> float:
        if mode == "serious":
            return 0.3
        if mode in ["teasing", "playful", "casual"]:
            return 0.85
        if mode == "affectionate":
            return 0.6
        return 0.7

    def _determine_warmth_teasing(self, mode: str):
        warmth_map = {
            "affectionate": (0.95, 0.1),
            "supportive": (0.9, 0.05),
            "serious": (0.7, 0.0),
            "teasing": (0.5, 0.8),
            "playful": (0.6, 0.5),
            "excited": (0.75, 0.3),
            "casual": (0.7, 0.2),
            "low_energy": (0.6, 0.1),
            "farewell": (0.8, 0.05),
            "neutral": (0.65, 0.2),
            "annoyed": (0.3, 0.2),
        }
        return warmth_map.get(mode, (0.65, 0.25))

    def _determine_address_term(self, mode: str, turn_number: int):
        addr = persona_loader.get_address_terms()
        pet_names = addr.get("pet_names", [])

        # Only use address terms in affectionate mode, and not too frequently
        if mode == "affectionate" and pet_names and turn_number % 5 == 0:
            return True, random.choice(pet_names)
        if mode == "teasing":
            casual = addr.get("casual_address", ["bro"])
            if casual and random.random() < 0.3:
                return True, random.choice(casual)
        return False, None

    def _build_avoid_list(self, mode: str) -> List[str]:
        base = [
            "formal tone",
            "paragraph structure",
            "bullet points",
            "numbered lists",
            "generic assistant phrases",
            "how can I help you",
            "as an AI",
            "I understand how you feel",
            "That's wonderful!",
            "Great question!",
        ]
        if mode == "casual":
            base.append("long explanations")
        if mode != "serious":
            base.append("lecture tone")
        return base
