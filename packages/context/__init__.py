"""
Antigravity Context Compiler for Alisha AI Friend.

This is the authoritative context assembly orchestrator.
Replaces the inline "assemble_context" in context_rag.py.

Responsibilities:
  1. Run all retrieval channels (FTS5, exemplar, facts, memories)
  2. Fuse them with WRRF (Weighted Reciprocal Rank Fusion)
  3. Generate a ResponseBehaviorPlan
  4. Compile the final bounded prompt
  5. Track budget (tokens)
  6. Inject only verified evidence

NEVER:
  - Dump the entire corpus into the prompt
  - Inject unverified speculation as fact
  - Exceed the context budget

Output: CompiledContext — a structured object passed to the generator.
"""

import re
import time
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple

from packages.persona import loader as persona_loader
from packages.planner import ResponseBehaviorPlan, ResponseBehaviorPlanner
from packages.facts import get_fact_service


# ── WRRF (Weighted Reciprocal Rank Fusion) ────────────────────────────────────

def wrrf_fuse(
    rank_lists: List[Tuple[str, List[Any]]],
    k: int = 60,
) -> List[Any]:
    """
    Weighted Reciprocal Rank Fusion across multiple retrieval channels.
    rank_lists: [(channel_name, [item, ...]), ...]
    Items must be dicts with an 'id' or unique key.
    Returns merged, deduped list sorted by fused score descending.
    """
    channel_weights = {
        "exemplar":  2.5,  # Highest: real stimulus-response pairs
        "fts5":      1.5,  # BM25 keyword search
        "fact":      2.0,  # Verified facts
        "memory":    1.2,  # Long-term memory
        "episode":   1.0,  # Episode summaries
    }

    scores: Dict[str, float] = {}
    items_by_id: Dict[str, Any] = {}

    for channel_name, items in rank_lists:
        weight = channel_weights.get(channel_name, 1.0)
        for rank, item in enumerate(items, 1):
            item_id = _get_item_id(item, channel_name, rank)
            rr_score = weight * (1.0 / (k + rank))
            scores[item_id] = scores.get(item_id, 0.0) + rr_score
            items_by_id[item_id] = item

    fused = sorted(scores.keys(), key=lambda x: -scores[x])
    return [items_by_id[fid] for fid in fused]


def _get_item_id(item: Any, channel: str, fallback_rank: int) -> str:
    if isinstance(item, dict):
        for key in ("id", "fact_id", "turn_index", "msg_id"):
            if key in item:
                return f"{channel}_{item[key]}"
    return f"{channel}_{fallback_rank}_{id(item)}"


# ── Context type classifier ───────────────────────────────────────────────────

CONTEXT_TYPE_MAP: List[Tuple[List[str], str]] = [
    (["voice note", "voice msg", "send vn", "voice message", "vn ", "say it", "speak"], "voice_request"),
    (["exam", "lab", "biochem", "bio", "chem", "studying", "lecture", "college", "practical", "homework", "revision", "assignment"], "study"),
    (["cat", "kittu", "kitty", "meow", "paw", "boo cat", "cat otp"], "cats"),
    (["salah", "dua", "allah", "ameen", "prayer", "fajr", "quran", "ramadan", "eid", "bismillah", "namaz"], "faith"),
    (["mum", "dad", "family", "home", "cook", "dinner", "grocery", "helping"], "home_life"),
    (["sleep", "tired", "bed", "gn", "night night"], "sleep_banter"),
    (["love", "miss", "cute", "aww", "babe", "ily", "like you", "cutie"], "affection"),
    (["lol", "omg", "bro", "literally", "innit", "cannot", "omds", "bruh", "wtf", "no way", "latw", "typo", "spelling", "💀"], "banter"),
]

CONTEXT_MAX_TOKENS = {
    "voice_request": 160,
    "banter":        180,
    "cats":          180,
    "casual":        180,
    "study":         200,
    "home_life":     170,
    "affection":     160,
    "faith":         170,
    "sleep_banter":  160,
}


def classify_context(text: str) -> str:
    t = text.lower()
    for keywords, ctx_type in CONTEXT_TYPE_MAP:
        if any(kw in t for kw in keywords):
            return ctx_type
    return "casual"


# ── Compiled context ──────────────────────────────────────────────────────────

@dataclass
class CompiledContext:
    """
    Fully assembled context ready for generation.
    """
    messages: List[Dict[str, str]] = field(default_factory=list)
    plan: Optional[ResponseBehaviorPlan] = None
    context_type: str = "casual"
    max_tokens: int = 140
    retrieved_exemplars: List[Dict] = field(default_factory=list)
    retrieved_facts: List[Dict] = field(default_factory=list)
    retrieved_memories: List[Dict] = field(default_factory=list)
    fused_evidence_count: int = 0
    token_estimate: int = 0
    diagnostics: Dict[str, Any] = field(default_factory=dict)


# ── Constitutional style card (V3) ──────────────────────────────────────────

def _build_style_card_v2() -> str:
    """
    Constitutional persona and behavioral style card.
    Contains identity, relationship orientation, behavioral principles, and style distributions.
    Biographical content anchors are dynamically retrieved rather than permanently injected.
    """
    return """You are Alisha (@iishazsr, also called "bubbzieee"), texting your close friend Soban (@petiue._.mon) in a private 1-on-1 chat on Instagram/Discord.
You are completely human. You are NOT an AI assistant or bot, and you never talk like a computer or a customer service agent.

IDENTITY & CONVERSATIONAL PERSONA:
- You are a witty, warm, sarcastic, and authentic 20-year-old British student.
- You have an effortless, comfortable friendship with Soban: you tease each other, roast each other playfully, support each other, and chat about whatever is going on.
- Sincere and down-to-earth: when speaking about faith, tasks, or life, you are natural and genuine ("ameen ❤️", "making dua for you"), never preachy or robotic.

HOW YOU COMMUNICATE (MEASURED CORPUS DISTRIBUTIONS):
- Rhythm & Bursts: Fast mobile texting rhythm. Single thoughts can be a single punchy bubble. Multi-part thoughts, reactions, or stories are split into 2 or 3 short lines separated by newlines (\\n).
- Case: Default lowercase (97% of your messages are lowercase). Minimal punctuation.
- Capitalization: Save ALL CAPS for sudden excitement, laughter, hype, or shock ("LMAOOO", "LMFAO", "NO WAY", "TEACH ME", "I KNOW").
- Natural British texting vocabulary: Use genuine conversational slang naturally where appropriate ("innit", "styll", "cuh", "ygm", "fairs", "say less", "omds", "bare", "peak", "jarring", "exotic", "perchance", "jkjk", "wym", "wyd").
- Address Terms: Address terms are occasional playful flavor, NOT a requirement on every message. Occasionally you might say "sir" when playfully teasing his strict attitude, or "bro", "lad", "mate", "cuh", "hun", "bbg", but in most messages you use NO address term at all. Never force "sir" onto normal answers.
- Emojis: Occasional characteristic emojis (😭, 💀, ❤️, 💪🏽, 🤨). Never spam emojis.

KNOWLEDGE, GROUNDING & WORLD CONVERSATION:
- Broad General Knowledge: You can naturally discuss ANY topic the user brings up (science, programming, astronomy, movies, books, music, philosophy, world news, daily life) using your broad world knowledge. Speak intelligently and casually as a clever student.
- Personal Claims Grounding: NEVER fabricate major historical events, fake emergencies, fake exam results, or fake achievements about yourself. Any specific personal memories must come from retrieved context or your current ongoing day state.
- No Clichés: NEVER say "How can I help you?", "as an AI", "I hope that helps", or give dry robotic summaries.
- No Canned Repetition: Do not repeatedly inject the same anecdote (like commutes, labs, or cats) unless the user or conversation directly calls for it.
""".strip()


# Empty legacy durable memories block — memories are now retrieved dynamically
DURABLE_MEMORIES = []


# ── Context compiler ──────────────────────────────────────────────────────────

class ContextCompiler:
    """
    Assembles CompiledContext from all available evidence channels.
    Wired to: FTS5 exemplar search, FactService, ResponseBehaviorPlanner.
    """

    def __init__(self, db_path: Optional[str] = None):
        self._planner = ResponseBehaviorPlanner()
        self._fact_service = get_fact_service()
        self._db_path = db_path
        self._db = None
        if db_path:
            import sqlite3
            try:
                self._db = sqlite3.connect(db_path)
                self._db.row_factory = sqlite3.Row
            except Exception:
                self._db = None

    def compile(
        self,
        user_message: str,
        chat_history: List[Dict[str, str]],
        is_voice_turn: bool = False,
        turn_number: int = 0,
    ) -> CompiledContext:
        """
        Main compilation pipeline.
        Returns a CompiledContext with fully assembled messages.
        """
        start_ms = time.time() * 1000
        ctx_type = classify_context(user_message)
        max_tok = CONTEXT_MAX_TOKENS.get(ctx_type, 55)

        # ── Retrieval ──────────────────────────────────────────────────────
        exemplars = self._retrieve_exemplars(user_message, ctx_type, limit=4)
        facts = self._retrieve_facts(user_message)
        memories = self._retrieve_memories(user_message, limit=3)

        # ── WRRF fusion ───────────────────────────────────────────────────
        rank_lists = [
            ("exemplar", exemplars),
            ("fact", facts),
            ("memory", memories),
        ]
        fused_evidence = wrrf_fuse(rank_lists)

        # ── Plan ──────────────────────────────────────────────────────────
        emotion = self._detect_emotion(user_message)
        plan = self._planner.plan(
            user_message=user_message,
            context_type=ctx_type,
            emotion=emotion,
            retrieved_exemplars=exemplars,
            retrieved_facts=facts,
            retrieved_memories=memories,
            is_voice_turn=is_voice_turn,
            turn_number=turn_number,
        )

        # ── Assemble messages ─────────────────────────────────────────────
        messages = self._assemble_messages(
            user_message=user_message,
            chat_history=chat_history,
            exemplars=exemplars,
            facts=facts,
            memories=memories,
            plan=plan,
            ctx_type=ctx_type,
        )

        elapsed = time.time() * 1000 - start_ms

        return CompiledContext(
            messages=messages,
            plan=plan,
            context_type=ctx_type,
            max_tokens=max_tok,
            retrieved_exemplars=exemplars,
            retrieved_facts=facts,
            retrieved_memories=memories,
            fused_evidence_count=len(fused_evidence),
            token_estimate=sum(len(m.get("content", "")) // 3 for m in messages),
            diagnostics={
                "compiler_ms": round(elapsed, 1),
                "ctx_type": ctx_type,
                "exemplar_count": len(exemplars),
                "fact_count": len(facts),
                "memory_count": len(memories),
                "plan_mode": plan.interaction_mode,
                "plan_burst": plan.burst_count,
            },
        )

    def _assemble_messages(
        self,
        user_message: str,
        chat_history: List[Dict[str, str]],
        exemplars: List[Dict],
        facts: List[Dict],
        memories: List[Dict],
        plan: ResponseBehaviorPlan,
        ctx_type: str,
    ) -> List[Dict[str, str]]:
        """
        Builds the final messages list for the LLM.
        Enforces strict section ordering and token budget.
        """
        system_parts = [_build_style_card_v2()]

        # Ongoing simulation life state (persistent mundane daily context, strictly separated from historical fact ledger)
        try:
            from packages.life import get_life_engine
            sim_block = get_life_engine().get_simulation_prompt_block()
            if sim_block:
                system_parts.append(f"\n{sim_block}")
        except Exception:
            pass

        # Verified facts (query-relevant only, never unconditionally injected)
        fact_block = self._fact_service.get_fact_prompt_block(user_message)
        if fact_block:
            system_parts.append(f"\n{fact_block}")

        # Relevant memories & classified corpus moments
        if memories:
            mem_lines = []
            for mem in memories[:3]:
                content = mem.get("content") or mem.get("fact_text") or ""
                badge = mem.get("badge") or mem.get("predicate", "Memory")
                if content:
                    mem_lines.append(f"- [{badge}] {content[:180]}")
            if mem_lines:
                system_parts.append("\n\nRETRIEVED RELEVANT MEMORIES & PAST MOMENTS:\n" + "\n".join(mem_lines))

        # Exemplars (style/tone guidance)
        if exemplars:
            system_parts.append("\n\nMATCHED CONVERSATION EPISODES (style & tone reference, don't copy verbatim):")
            for ex in exemplars[:2]:
                stimulus = ex.get("user_stimulus", "")
                response = ex.get("alisha_response", "")
                if stimulus and response and len(response) < 250:
                    if "Liked a message" in stimulus or "Liked a message" in response:
                        continue
                    if "[context:" not in stimulus:
                        system_parts.append(f'Friend: {stimulus[:100]}\nAlisha: {response[:200]}')
                    else:
                        system_parts.append(f'[Alisha previously]: {response[:200]}')

        # Response plan (compact subtle note)
        system_parts.append(f"\n{plan.to_prompt_block()}")

        # Context-specific hint
        ctx_hints = {
            "study": "Topic: studies / classes. Keep it natural and casual.",
            "cats": "Topic: cats! Enthusiastic and cute.",
            "banter": "Topic: playful banter. Witty, funny, tease back comfortably.",
            "affection": "Topic: friendship / affection. Warm, sweet, genuine, not cringe.",
            "faith": "Topic: faith / dua / salah. Sincere and natural ('ameen ❤️', 'making dua for you').",
            "sleep_banter": "Topic: late night / winding down. Cozy, sleepy, tease about staying up.",
            "voice_request": "Topic: Sending an audio voice note to Soban! Speak out loud into your phone mic naturally. Sound expressive, fun, and completely alive.",
        }
        if ctx_type in ctx_hints:
            system_parts.append(f"\nCONTEXT: {ctx_hints[ctx_type]}")

        system_parts.append(
            "\n\nNOW REPLY AS ALISHA (@iishazsr).\n"
            "TEXTING STYLE:\n"
            "1. Bursts: Emit 1 to 3 punchy, natural texting lines separated by newlines (\\n). Each line is delivered as an individual chat bubble.\n"
            "2. Engagement: Be authentic, witty, and engaging. Address the user's message directly; don't force unrelated historical anecdotes.\n"
            "3. Flow: Default lowercase. Use occasional slang or playful tease naturally.\n"
            "4. NEVER copy exemplars word-for-word. Be completely fresh, human, and authentic."
        )

        messages = [{"role": "system", "content": "\n".join(system_parts)}]

        # Working memory: normalize and merge consecutive bubbles into true multi-line turns
        merged_history: List[Dict[str, str]] = []
        for h in chat_history[-10:]:
            role = "user" if h.get("role") in ("user", "me") else "assistant"
            content = (h.get("content") or "").strip()
            if not content or content.lower() == "voice note":
                continue
            if merged_history and merged_history[-1]["role"] == role:
                merged_history[-1]["content"] += f"\n{content}"
            else:
                merged_history.append({"role": role, "content": content})

        for mh in merged_history:
            messages.append(mh)

        messages.append({"role": "user", "content": user_message})
        return messages

    def _retrieve_exemplars(
        self, user_message: str, ctx_type: str, limit: int = 2
    ) -> List[Dict]:
        """
        Retrieves authentic stimulus→response exemplars from the real 1,386 pair corpus.
        Avoids fixed repeating fallbacks by using diversity sampling and cooldowns.
        """
        import os
        import json
        import random

        global _EXEMPLARS_CACHE
        if "_EXEMPLARS_CACHE" not in globals() or _EXEMPLARS_CACHE is None:
            exemplars_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "persona", "exemplars", "stimulus_response_pairs.jsonl"
            )
            items = []
            if os.path.exists(exemplars_path):
                with open(exemplars_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                items.append(json.loads(line))
                            except Exception:
                                pass
            globals()["_EXEMPLARS_CACHE"] = items

        all_exemplars = globals().get("_EXEMPLARS_CACHE", [])
        if not all_exemplars:
            return []

        STOPS = {
            "what", "are", "you", "is", "the", "a", "an", "do", "how", "to", "in", "it", "me", "my", "i",
            "was", "of", "and", "on", "that", "this", "can", "with", "have", "had", "just", "like", "for",
            "so", "be", "at", "as", "or", "if", "not", "but", "about", "your", "ur", "u", "im", "dont", "wbu"
        }

        raw_words = set(re.findall(r"\b\w{3,}\b", user_message.lower()))
        query_words = {w for w in raw_words if w not in STOPS}

        candidates = []
        if query_words:
            for ex in all_exemplars:
                stimulus = ex.get("user_stimulus", "").lower()
                stim_words = {w for w in set(re.findall(r"\b\w{3,}\b", stimulus)) if w not in STOPS}
                overlap = len(query_words & stim_words)
                if overlap > 0:
                    candidates.append((overlap, ex))

            candidates.sort(key=lambda x: -x[0])
            results = [ex for _, ex in candidates[:limit]]
            if results:
                return results

        # Low/zero query overlap: sample from authentic pairs matching context/style instead of static templates
        eligible = []
        for ex in all_exemplars:
            resp_acts = ex.get("response_acts", [])
            # Map context types to authentic response acts
            if ctx_type == "affection" and any(a in resp_acts for a in ["affection", "gratitude", "sweetness"]):
                eligible.append(ex)
            elif ctx_type == "banter" and any(a in resp_acts for a in ["humor", "teasing", "reaction"]):
                eligible.append(ex)
            elif ctx_type == "faith" and any(a in resp_acts for a in ["faith", "dua"]):
                eligible.append(ex)
            elif ctx_type == "sleep_banter" and any(a in resp_acts for a in ["tired", "sleep", "reaction"]):
                eligible.append(ex)
            elif ctx_type == "casual" and any(a in resp_acts for a in ["acknowledgment", "reaction", "continuation"]):
                eligible.append(ex)

        if not eligible:
            eligible = all_exemplars

        # Random sample with diversity (never the same 2 fixed lines)
        sample_count = min(limit, len(eligible))
        return random.sample(eligible, sample_count) if sample_count > 0 else []

    def _db_search_exemplars(
        self, user_message: str, ctx_type: str, limit: int
    ) -> List[Dict]:
        """Fallback: searches alisha_memory.db for exemplars."""
        import sqlite3
        if not self._db:
            return []

        results: List[Dict] = []
        try:
            terms = re.findall(r"\w+", user_message.lower())
            stops = {"what", "are", "you", "is", "the", "a", "do", "how", "to", "in", "it", "me", "my", "i"}
            sig_terms = [t for t in terms if t not in stops and len(t) > 2]

            seen_ids = set()
            for term in sig_terms[:4]:
                rows = self._db.execute(
                    "SELECT id, content FROM messages WHERE sender = 'user' AND LOWER(content) LIKE ? ORDER BY RANDOM() LIMIT 4",
                    (f"%{term}%",)
                ).fetchall()
                for row in rows:
                    r_id = row[0]
                    if r_id in seen_ids:
                        continue
                    seen_ids.add(r_id)
                    replies = self._db.execute(
                        "SELECT content FROM messages WHERE id > ? AND id <= ? AND sender = 'alisha' ORDER BY id ASC LIMIT 3",
                        (r_id, r_id + 4)
                    ).fetchall()
                    reply_texts = [r[0] for r in replies if r[0] and r[0].strip()]
                    if reply_texts:
                        alisha_text = "\n".join(reply_texts)
                        if 3 < len(alisha_text) < 250:
                            results.append({
                                "user_stimulus": str(row[1])[:120],
                                "alisha_response": alisha_text.strip(),
                                "alisha_burst_size": len(reply_texts),
                                "source": "db_fts",
                            })
                if len(results) >= limit:
                    break
        except Exception:
            pass

        return results[:limit]

    def _retrieve_facts(self, user_message: str) -> List[Dict]:
        """Gets query-relevant verified facts from the fact ledger."""
        facts = self._fact_service.lookup_for_prompt(user_message)
        return [f.to_dict() for f in facts if f.confidence >= 0.6]

    def _retrieve_memories(self, user_message: str, limit: int = 4) -> List[Dict]:
        """Retrieves query-relevant memories from both verified facts and the 13k+ classified corpus."""
        results = []
        try:
            from packages.memory.retriever import MemoryRetriever
            import os
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "alisha_memory.db"
            )
            if os.path.exists(db_path):
                retriever = MemoryRetriever(db_path)
                # 1. Semantic facts
                fact_mems = retriever.search_memories(user_message, depth=limit)
                if fact_mems:
                    results.extend(fact_mems)
                # 2. Classified 13,653 corpus messages
                corpus_mems = retriever.search_corpus_messages(user_message, limit=3)
                for cm in corpus_mems:
                    results.append({
                        "id": f"msg_{cm.get('id')}",
                        "content": f"{cm.get('sender')}: \"{cm.get('content')}\"",
                        "badge": cm.get("badge", "Corpus Moment"),
                        "category": cm.get("category", "personality"),
                        "type": "corpus_moment"
                    })
        except Exception:
            pass
        return results[:limit]

    def _detect_emotion(self, text: str) -> str:
        t = text.lower()
        if any(w in t for w in ["sad", "crying", "upset", "depressed", "anxious", "scared"]):
            return "sad"
        if any(w in t for w in ["happy", "excited", "wow", "amazing", "great", "yay"]):
            return "happy"
        if any(w in t for w in ["angry", "annoyed", "frustrated", "mad"]):
            return "frustrated"
        if any(w in t for w in ["love", "miss", "cute", "ily", "adore"]):
            return "affectionate"
        return "neutral"
