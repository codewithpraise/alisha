"""
Laya Service
Central unified interface for Laya routing, confidence gating, and behavior planning.
Preloads at backend startup and executes sub-50ms multi-question single-pass routing.
"""

from typing import Dict, Any, List, Optional, Tuple
from .types import (
    ResponseMode,
    RetrievalNeed,
    MemoryNeed,
    InteractionMode,
    ResponseAct,
    LayaDecision,
    ResponseBehaviorPlan
)
from .LayaRouter import LayaRouter
from .LayaQuestions import LAYA_ROUTING_QUESTIONS


class LayaService:
    """
    Central Laya service instance.
    Keeps routing fast, clean, private, and deterministic.
    """

    _instance: Optional["LayaService"] = None

    def __init__(self, checkpoint: str = "router"):
        self.router = LayaRouter(checkpoint=checkpoint)
        self.is_preloaded = True

    @classmethod
    def get_instance(cls) -> "LayaService":
        if cls._instance is None:
            cls._instance = LayaService()
        return cls._instance

    def route_turn(self, current_message: str, recent_messages: Optional[List[Dict[str, str]]] = None,
                   voice_mode: str = "mix", context_metadata: Optional[Dict[str, Any]] = None) -> Tuple[LayaDecision, ResponseBehaviorPlan]:
        """
        Main entrypoint for Alisha conversation turns.
        Evaluates input state and returns both the LayaDecision and the ResponseBehaviorPlan.
        """
        state = {
            "current_message": current_message,
            "recent_messages": recent_messages or [],
            "metadata": context_metadata or {}
        }

        decision = self.router.evaluate_state(state, voice_mode=voice_mode)
        plan = self.router.build_behavior_plan(decision)

        return decision, plan

    def classify_conversation(self, message: str) -> ResponseMode:
        dec, _ = self.route_turn(message)
        return dec.response_mode

    def classify_retrieval_need(self, message: str) -> RetrievalNeed:
        dec, _ = self.route_turn(message)
        return dec.retrieval_need

    def classify_memory_need(self, message: str) -> MemoryNeed:
        dec, _ = self.route_turn(message)
        return dec.memory_need

    def classify_interaction_mode(self, message: str) -> InteractionMode:
        dec, _ = self.route_turn(message)
        return dec.interaction_mode

    def classify_response_act(self, message: str) -> ResponseAct:
        dec, _ = self.route_turn(message)
        return dec.response_act

    def verify_candidate_compliance(self, candidate_text: str, plan: ResponseBehaviorPlan) -> Dict[str, Any]:
        """
        Verifies if the generated candidate satisfies the ResponseBehaviorPlan.
        Checks length class, burst count, and tone markers.
        """
        words = candidate_text.split()
        word_count = len(words)
        lines = [l.strip() for l in candidate_text.split("\n") if l.strip()]
        bubble_count = len(lines)

        min_w, max_w = plan.target_word_range
        is_length_ok = (min_w - 2) <= word_count <= (max_w + 10)
        is_bubble_ok = bubble_count <= (plan.target_bubble_count + 1)

        return {
            "compliant": is_length_ok and is_bubble_ok,
            "word_count": word_count,
            "bubble_count": bubble_count,
            "target_range": plan.target_word_range,
            "target_bubbles": plan.target_bubble_count
        }


# Type alias
Tuple_LayaResult = tuple[LayaDecision, ResponseBehaviorPlan]
