"""
Laya Type Definitions
Structured decision schemas and ResponseBehaviorPlan for Alisha AI.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple


class ResponseMode(str, Enum):
    FAST = "FAST"
    DEEP = "DEEP"
    CALL = "CALL"


class RetrievalNeed(str, Enum):
    NONE = "NONE"
    LIGHT = "LIGHT"
    DEEP = "DEEP"


class MemoryNeed(str, Enum):
    NONE = "NONE"
    RECALL = "RECALL"
    WRITE = "WRITE"
    UPDATE = "UPDATE"
    FORGET = "FORGET"


class InteractionMode(str, Enum):
    CASUAL = "CASUAL"
    PLAYFUL = "PLAYFUL"
    TEASING = "TEASING"
    AFFECTIONATE = "AFFECTIONATE"
    SUPPORTIVE = "SUPPORTIVE"
    SERIOUS = "SERIOUS"
    EXCITED = "EXCITED"
    LOW_ENERGY = "LOW_ENERGY"
    FIRM = "FIRM"
    FAREWELL = "FAREWELL"


class ResponseAct(str, Enum):
    GREETING = "GREETING"
    REACTION = "REACTION"
    ANSWER = "ANSWER"
    QUESTION = "QUESTION"
    FOLLOW_UP = "FOLLOW_UP"
    TEASE = "TEASE"
    PLAYFUL_INSULT = "PLAYFUL_INSULT"
    AFFECTION = "AFFECTION"
    REASSURANCE = "REASSURANCE"
    COMFORT = "COMFORT"
    ENCOURAGEMENT = "ENCOURAGEMENT"
    HUMOR = "HUMOR"
    EXPLANATION = "EXPLANATION"
    CORRECTION = "CORRECTION"
    ACKNOWLEDGMENT = "ACKNOWLEDGMENT"
    SURPRISE = "SURPRISE"
    EXCITEMENT = "EXCITEMENT"
    TOPIC_SHIFT = "TOPIC_SHIFT"
    FAREWELL = "FAREWELL"


@dataclass
class LayaDecision:
    response_mode: ResponseMode
    retrieval_need: RetrievalNeed
    memory_need: MemoryNeed
    interaction_mode: InteractionMode
    response_act: ResponseAct
    historical_reference: bool
    confidence: float
    raw_decision: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResponseBehaviorPlan:
    mode: str  # e.g. "PLAYFUL", "SUPPORTIVE", "FAST"
    speech_act: str  # e.g. "TEASE", "ANSWER", "REACTION"
    length_class: str  # "VERY_SHORT", "SHORT", "MEDIUM"
    target_word_range: Tuple[int, int]
    target_bubble_count: int
    slang_intensity: float
    emoji_policy: str  # "OPTIONAL", "REQUIRED_ONE", "NONE"
    warmth: float
    teasing_intensity: float
    relevant_facts: List[str] = field(default_factory=list)
    relevant_memories: List[str] = field(default_factory=list)
    historical_examples: List[str] = field(default_factory=list)
    guidance_notes: str = ""
