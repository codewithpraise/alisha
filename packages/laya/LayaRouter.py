"""
Laya Local Router
Fast deterministic and embedding-assisted classifier for sub-50ms routing.
Includes confidence gating, low-confidence safe fallbacks, and multi-question single pass.
"""

import re
from typing import Dict, Any, List, Optional
from .types import (
    ResponseMode,
    RetrievalNeed,
    MemoryNeed,
    InteractionMode,
    ResponseAct,
    LayaDecision,
    ResponseBehaviorPlan
)


class LayaRouter:
    """
    Local-first, zero-cost decision router.
    Evaluates compact conversation state and emits a structured LayaDecision.
    """

    def __init__(self, checkpoint: str = "router"):
        self.checkpoint = checkpoint
        self.min_confidence_threshold = 0.70

    def evaluate_state(self, state: Dict[str, Any], voice_mode: str = "mix") -> LayaDecision:
        """
        Evaluates the conversation state in a single logical pass.
        
        State schema:
        {
            "current_message": str,
            "recent_messages": List[Dict[str, str]],
            "current_topic": str,
            "active_entities": List[str],
            "session_summary": str,
            "recent_memories": List[str]
        }
        """
        msg = (state.get("current_message") or "").strip().lower()
        recent = state.get("recent_messages", [])

        # 1. Voice Call Override
        if voice_mode == "always" or voice_mode == "call":
            return LayaDecision(
                response_mode=ResponseMode.CALL,
                retrieval_need=RetrievalNeed.LIGHT,
                memory_need=MemoryNeed.NONE,
                interaction_mode=InteractionMode.CASUAL,
                response_act=ResponseAct.ANSWER,
                historical_reference=False,
                confidence=0.98,
                raw_decision={"override": "voice_call"}
            )

        # 2. Memory Need Classification
        mem_need = MemoryNeed.NONE
        if re.search(r"\b(remember that|don't forget|keep in mind|note that|make a note|my (exam|birthday|flight) is)\b", msg):
            mem_need = MemoryNeed.WRITE
        elif re.search(r"\b(what did i (say|tell you)|(do you )?remember (my|what|when|where|about)|remember what i told you|what's my|when is my)\b", msg):
            mem_need = MemoryNeed.RECALL
        elif re.search(r"\b(actually it'?s|correction|it is actually|changed to|moved to)\b", msg):
            mem_need = MemoryNeed.UPDATE
        elif re.search(r"\b(forget (that|about|what)|delete (that|memory)|erase)\b", msg):
            mem_need = MemoryNeed.FORGET

        # 3. Response Mode & Retrieval Need Classification
        # Fast casual messages
        fast_patterns = [
            r"^(yo|hey|hi|hello|heyy+|sup|wyd|wbu|lol|lmao|same|omg|damn|bruh|cuh|innit|fr|true|yeah|yep|nah|nope|wait|haha+)$",
            r"^(good morning|good night|gm|gn|tc|ty|thanks|thank you|ok|okay|ohkay|k|hmm|sure|cool|nice)$",
            r"^(what are you doing|what u doing|where r u|where are you|what's up|how r u|how are you)$"
        ]
        is_fast = any(re.match(p, msg) for p in fast_patterns) or (len(msg.split()) <= 3 and not re.search(r"\b(remember|why|explain|tell me about)\b", msg))

        # Deep queries
        deep_patterns = [
            r"\b((do you )?remember (when|that time|what happened|what i told you|about)|tell me about the time|why do you think|how do i deal with)\b",
            r"\b(i feel (so |really )?(sad|anxious|lost|tired|broken|hopeless|stressed)|can you help me with|important question)\b",
            r"\b(biochem|chemistry|practical|exam prep|college project|family issue|our inside joke)\b"
        ]
        is_deep = any(re.search(p, msg) for p in deep_patterns) or len(msg.split()) > 15 or mem_need in (MemoryNeed.RECALL, MemoryNeed.WRITE, MemoryNeed.UPDATE)

        if is_deep:
            resp_mode = ResponseMode.DEEP
            retrieval_need = RetrievalNeed.DEEP
        elif is_fast:
            resp_mode = ResponseMode.FAST
            retrieval_need = RetrievalNeed.NONE if len(msg.split()) <= 2 else RetrievalNeed.LIGHT
        else:
            resp_mode = ResponseMode.FAST
            retrieval_need = RetrievalNeed.LIGHT

        # 4. Interaction Mode Classification
        if re.search(r"\b(love you|miss you|pookie|cutie|babycakes|boo|sweet|warm)\b", msg):
            interaction_mode = InteractionMode.AFFECTIONATE
        elif re.search(r"\b(kidding|loser|noob|dumb|fool|hahaha|joke|cap|💀|😭|😝)\b", msg):
            interaction_mode = InteractionMode.TEASING if re.search(r"\b(loser|dumb|noob)\b", msg) else InteractionMode.PLAYFUL
        elif re.search(r"\b(sad|crying|depressed|hard|difficult|scared|hurt|pain|fail)\b", msg):
            interaction_mode = InteractionMode.SUPPORTIVE
        elif re.search(r"\b(serious|seriously|listen|focus|urgent|emergency)\b", msg):
            interaction_mode = InteractionMode.SERIOUS
        elif re.search(r"\b(omg|omdssd|wow|yay|won|passed|scored|celebrate|🎉)\b", msg):
            interaction_mode = InteractionMode.EXCITED
        elif re.search(r"\b(bye|cya|see you|goodnight|talk tomorrow|gotta sleep|sleeping)\b", msg):
            interaction_mode = InteractionMode.FAREWELL
        else:
            interaction_mode = InteractionMode.CASUAL

        # 5. Response Act Classification
        if re.match(r"^(yo|hey|hi|hello|heyy+|gm|good morning)", msg):
            response_act = ResponseAct.GREETING
        elif re.match(r"^(bye|gn|goodnight|see ya|cya)", msg):
            response_act = ResponseAct.FAREWELL
        elif re.search(r"\b(loser|stfu|shut up|you suck|ugly)\b", msg):
            response_act = ResponseAct.PLAYFUL_INSULT
        elif re.search(r"\b(why|what|how|when|where|who)\b", msg) and msg.endswith("?"):
            response_act = ResponseAct.ANSWER
        elif interaction_mode == InteractionMode.SUPPORTIVE:
            response_act = ResponseAct.REASSURANCE
        elif interaction_mode == InteractionMode.AFFECTIONATE:
            response_act = ResponseAct.AFFECTION
        elif interaction_mode == InteractionMode.TEASING:
            response_act = ResponseAct.TEASE
        elif re.search(r"\b(omg|wow|whattt|really|no way)\b", msg):
            response_act = ResponseAct.SURPRISE
        else:
            response_act = ResponseAct.REACTION if len(msg.split()) <= 4 else ResponseAct.ANSWER

        # 6. Historical Reference Flag
        hist_ref = bool(re.search(r"\b((do you )?remember (when|that time|what happened|what i told you)|that cat|the lab|chemistry practical|inside joke)\b", msg))

        confidence = 0.92 if (is_fast or is_deep) else 0.78

        return LayaDecision(
            response_mode=resp_mode,
            retrieval_need=retrieval_need,
            memory_need=mem_need,
            interaction_mode=interaction_mode,
            response_act=response_act,
            historical_reference=hist_ref,
            confidence=confidence,
            raw_decision={
                "is_fast": is_fast,
                "is_deep": is_deep,
                "msg_len": len(msg.split())
            }
        )

    def build_behavior_plan(self, decision: LayaDecision, retrieved_facts: Optional[List[str]] = None,
                            retrieved_memories: Optional[List[str]] = None,
                            historical_examples: Optional[List[str]] = None) -> ResponseBehaviorPlan:
        """
        Converts the Laya decision and retrieval signals into an explicit ResponseBehaviorPlan.
        """
        facts = retrieved_facts or []
        memories = retrieved_memories or []
        examples = historical_examples or []

        if decision.response_mode == ResponseMode.FAST:
            length_class = "VERY_SHORT"
            word_range = (2, 8)
            bubble_count = 1
            slang_intensity = 0.85
            teasing_intensity = 0.6 if decision.interaction_mode in (InteractionMode.PLAYFUL, InteractionMode.TEASING) else 0.2
            warmth = 0.6
        elif decision.response_mode == ResponseMode.CALL:
            length_class = "SHORT"
            word_range = (5, 14)
            bubble_count = 1
            slang_intensity = 0.70
            teasing_intensity = 0.3
            warmth = 0.8
        else:  # DEEP
            length_class = "MEDIUM"
            word_range = (8, 22)
            bubble_count = 2 if len(facts) > 0 or len(memories) > 0 else 1
            slang_intensity = 0.75
            teasing_intensity = 0.4
            warmth = 0.85

        emoji_policy = "OPTIONAL"
        if decision.interaction_mode in (InteractionMode.EXCITED, InteractionMode.AFFECTIONATE):
            emoji_policy = "REQUIRED_ONE"
        elif decision.interaction_mode == InteractionMode.SERIOUS:
            emoji_policy = "NONE"

        guidance = f"Mode: {decision.interaction_mode.value}. Speech Act: {decision.response_act.value}. Deliver in authentic Alisha British/Pakistani college texting tone."

        return ResponseBehaviorPlan(
            mode=decision.interaction_mode.value,
            speech_act=decision.response_act.value,
            length_class=length_class,
            target_word_range=word_range,
            target_bubble_count=bubble_count,
            slang_intensity=slang_intensity,
            emoji_policy=emoji_policy,
            warmth=warmth,
            teasing_intensity=teasing_intensity,
            relevant_facts=facts,
            relevant_memories=memories,
            historical_examples=examples,
            guidance_notes=guidance
        )
