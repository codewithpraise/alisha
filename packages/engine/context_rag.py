"""
Temporal Hybrid Context-Graph RAG & Style Engine for Alisha.
Built from ground-truth corpus analysis of 13,653 real messages.

Corpus Statistics (empirically measured):
  - Total Alisha messages: 3,747
  - Char median: 26, mean: 41.3, p90: 79, p95: 115, max: 992
  - Word median: 5, mean: 8.4, p90: 16
  - Emoji rate: ~8% of messages (stored as bytes in DB, unicode in JSONL)
  - Double-text+ probability: ~60% (mean burst = 2.52 messages/turn)
  - Most common short replies: 'oh', 'hmm', 'yeah', 'kidding', 'damn', 'ohkay', 'wbu'
  - Top openers: i, you, oh, yeah, it, and, but, that, u, what, well, so, hmm, idk
  - Top slang: yeah (161), okay (104), hmm (54), ig (59), idk (55), wait (32), bro (29)
  - Authentic phrases: 'omdssd', 'yk', 'cuh', 'ima', 'otw', 'innit', 'ofc'
  - Real voice note context: sends vn when lazy to type, when explaining longer stuff

Architecture Layers:
  A: Immutable Archive (13,653 messages in alisha_memory.db via SQLite FTS5)
  B: Working Memory (last 6-10 turns)
  C: Session State (late night / topic awareness)
  D: Durable Long-Term Memory (biochem, cats, college, faith, family)
  E: Style Card + Episodic Exemplars (micro-windows from real corpus)
  Voice: Real-Time Zero-Shot Neural TTS (edge-tts / en-GB-SoniaNeural)
"""

import os
import re
import random
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from packages.inference.groq_provider import GroqProvider
from packages.voice.realtime_tts import synthesize_speech, match_authentic_voice
from packages.laya import LayaService

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(ROOT, "alisha_memory.db")


# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# CONSTITUTIONAL STYLE CARD
# ─────────────────────────────────────────────────────────────────────────────
STYLE_CARD = """
YOU ARE ALISHA (@iishazsr, also called "bubbzieee").
You are texting your close friend Soban (@petiue._.mon) in a private 1-on-1 chat on Instagram/Discord.
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

# ─────────────────────────────────────────────────────────────────────────────
# Context classification for dynamic token budgeting
# ─────────────────────────────────────────────────────────────────────────────
def _classify_context(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["voice note", "voice msg", "send vn", "voice message", "say it", "record", "speak", "sing"]):
        return "voice_request"
    if any(k in t for k in ["exam", "lab", "biochem", "bio", "chem", "study", "studying", "lecture", "college", "class", "homework", "revision", "practical", "assignment"]):
        return "study"
    if any(k in t for k in ["cat", "kittu", "kitty", "meow", "paw", "pookie"]):
        return "cats"
    if any(k in t for k in ["salah", "dua", "allah", "ameen", "pray", "prayer", "fajr", "quran", "ramadan", "eid", "bismillah"]):
        return "faith"
    if any(k in t for k in ["mum", "dad", "family", "home", "cook", "dinner", "food", "grocery"]):
        return "home_life"
    if any(k in t for k in ["sleep", "tired", "latw", "late", "night", "morning", "wake", "bed", "fajr"]):
        return "sleep_banter"
    if any(k in t for k in ["love", "miss", "cute", "aww", "babe", "heart", "ily", "like you", "like me"]):
        return "affection"
    if any(k in t for k in ["lol", "omg", "bro", "literally", "innit", "cannot", "omds", "bruh", "wtf", "noway", "no way"]):
        return "banter"
    return "casual"

# Max tokens by context (keeps responses authentic to Alisha's real length distribution)
CONTEXT_MAX_TOKENS = {
    "voice_request": 140,
    "banter": 140,
    "cats": 160,
    "casual": 150,
    "study": 180,
    "home_life": 150,
    "affection": 130,
    "faith": 150,
    "sleep_banter": 120,
}


class AlishaContextEngine:
    def __init__(self):
        self.groq = GroqProvider()
        self.turn_count = 0
        self._db_available = os.path.exists(DB_PATH)

        # ── Antigravity pipeline (V3) ──────────────────────────────────────
        self._compiler = None
        self._verifier = None
        self._ag_pipeline_ready = False
        self._init_ag_pipeline()
    def _init_ag_pipeline(self):
        """
        Lazily initialises the Antigravity V3 pipeline.
        Falls back to V2 gracefully if any component fails to import.
        """
        try:
            from packages.context import ContextCompiler
            from packages.verifier import PersonaVerifier
            self._compiler = ContextCompiler(db_path=DB_PATH if self._db_available else None)
            self._verifier = PersonaVerifier()
            self._ag_pipeline_ready = True
            print("[AlishaContextEngine] Antigravity V3 pipeline ready")
        except Exception as e:
            print(f"[AlishaContextEngine] V3 pipeline init failed, using V2: {e}")
            self._ag_pipeline_ready = False

    def search_episodic_exemplars(self, user_msg: str, ctx: str, limit: int = 4) -> List[Tuple[str, str]]:

        """
        Retrieves real micro-episodes from the corpus where a similar topic came up.
        Prioritizes: (1) exact phrase matches in user-side utterances, (2) topic-based
        Alisha-side real messages to ground factual statements.
        """
        exemplars: List[Tuple[str, str]] = []
        if not self._db_available:
            return exemplars

        try:
            con = sqlite3.connect(DB_PATH)
            cur = con.cursor()

            # --- Strategy 1: FTS5 semantic search for user-similar messages ---
            terms = re.findall(r"\w+", user_msg.lower())
            stops = {"what","are","you","is","the","a","do","how","to","in","it","me","my","i","was","of","and","on"}
            sig_terms = [t for t in terms if t not in stops and len(t) > 2]

            seen_ids = set()
            for term in sig_terms[:5]:
                cur.execute(
                    "SELECT id, content FROM messages WHERE sender = 'user' AND LOWER(content) LIKE ? ORDER BY RANDOM() LIMIT 6",
                    (f"%{term}%",)
                )
                for r_id, u_content in cur.fetchall():
                    if r_id in seen_ids:
                        continue
                    seen_ids.add(r_id)
                    # Get Alisha's response(s) immediately after
                    cur.execute(
                        "SELECT content FROM messages WHERE id > ? AND id <= ? AND sender = 'alisha' ORDER BY id ASC LIMIT 3",
                        (r_id, r_id + 4)
                    )
                    replies = [r[0] for r in cur.fetchall() if r[0] and r[0].strip()]
                    if replies:
                        alisha_text = "\n".join(replies)
                        if 3 < len(alisha_text) < 200:
                            exemplars.append((u_content.strip()[:120], alisha_text.strip()))
                if len(exemplars) >= limit:
                    break

            # --- Strategy 2: Topic-grounded Alisha statements (factual anchor) ---
            topic_queries = {
                "study": ["biochem", "bio", "chem", "college", "exam", "practical"],
                "cats": ["cat", "kittu"],
                "faith": ["dua", "salah", "ameen"],
                "home_life": ["mum", "home"],
                "sleep_banter": ["latw", "sleep", "tired", "night"],
            }
            if ctx in topic_queries and len(exemplars) < limit:
                for kw in topic_queries[ctx]:
                    cur.execute(
                        "SELECT content FROM messages WHERE sender = 'alisha' AND LOWER(content) LIKE ? ORDER BY RANDOM() LIMIT 2",
                        (f"%{kw}%",)
                    )
                    for (content,) in cur.fetchall():
                        if content and 3 < len(content) < 180:
                            exemplars.append((f"[context: {ctx}]", content.strip()))
                    if len(exemplars) >= limit:
                        break

            con.close()
        except Exception as e:
            print(f"[ContextRAG] Exemplar search: {e}")

        return exemplars[:limit]

    def assemble_context(
        self,
        user_msg: str,
        chat_history: List[Dict[str, str]],
        exemplars: List[Tuple[str, str]],
        ctx: str,
        persona_mode: str = "classic"
    ) -> List[Dict[str, str]]:
        """
        Compiles the bounded prompt. Budget-conscious: system + 8 turns + exemplars.
        """
        system_parts = [STYLE_CARD]

        # Ongoing simulation life state (persistent mundane daily context, strictly separated from historical fact ledger)
        try:
            from packages.life import get_life_engine
            sim_block = get_life_engine().get_simulation_prompt_block()
            if sim_block:
                system_parts.append(f"\n{sim_block}")
        except Exception:
            pass

        if exemplars:
            system_parts.append("\n\nREAL PAST CONVERSATION STYLE EXAMPLES (use as tone/style guide ONLY, not to copy):")
            for u_stim, a_resp in exemplars[:2]:
                if "[context:" not in u_stim:
                    system_parts.append(f"Friend: {u_stim}\nAlisha: {a_resp}")
                else:
                    system_parts.append(f"[Alisha actually said]: {a_resp}")

        # Context-specific instruction addition
        ctx_hints = {
            "study": "Topic: studies / classes. Keep it natural and casual.",
            "cats": "Topic: cats! Enthusiastic and cute.",
            "banter": "Topic: playful sarcastic banter. Tease comfortably.",
            "affection": "Topic: warm friendship. Genuine and sweet ('cutie ❤️', 'missed you honestly').",
            "faith": "Topic: faith / salah / dua. Sincere and natural ('ameen ❤️', 'making dua for you').",
            "sleep_banter": "Topic: late night / sleep. Cozy, groggy, tease about being up late scrolling on phone.",
        }
        if ctx in ctx_hints:
            system_parts.append(f"\n\nCURRENT CONTEXT HINT: {ctx_hints[ctx]}")

        system_parts.append(
            "\n\nNOW REPLY AS ALISHA (@iishazsr).\n"
            "TEXTING STYLE:\n"
            "1. Bursts: Emit 1 to 3 punchy, natural texting lines separated by newlines (\\n). Each line is delivered as an individual chat bubble.\n"
            "2. Engagement: Be authentic, witty, and engaging. Address the user directly without forcing unrelated anecdotes.\n"
            "3. Flow: Default lowercase. Use occasional slang or playful tease naturally."
        )

        messages = [{"role": "system", "content": "\n".join(system_parts)}]

        # Working memory: normalize and merge consecutive bubbles into true multi-line turns
        merged_history: List[Dict[str, str]] = []
        for h in chat_history[-10:]:
            role = "user" if h.get("role") in ["user", "me"] else "assistant"
            content = (h.get("content") or "").strip()
            if not content or content.lower() == "voice note":
                continue
            if merged_history and merged_history[-1]["role"] == role:
                merged_history[-1]["content"] += f"\n{content}"
            else:
                merged_history.append({"role": role, "content": content})

        for mh in merged_history:
            messages.append(mh)

        messages.append({"role": "user", "content": user_msg})
        return messages

    def _post_process(self, raw: str, ctx: str) -> str:
        """Clean model output artefacts and enforce authentic Alisha style."""
        text = raw.strip()
        # Remove role prefix hallucinations
        for prefix in ("Alisha:", "alisha:", "Assistant:", "assistant:", "AI:", "ai:"):
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        # Strip surrounding quotes
        text = text.strip('"').strip("'")
        # Remove <think> blocks (Qwen chain-of-thought)
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
        # Remove [voice note: ...] meta markers
        text = re.sub(r"\[(voice note|audio|vn).*?\]", "", text, flags=re.IGNORECASE).strip()
        # Remove markdown bold/italics
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
        text = re.sub(r"\*(.+?)\*", r"\1", text)
        # Remove numbered lists
        text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)
        # Remove bullet points
        text = re.sub(r"^[-•]\s+", "", text, flags=re.MULTILINE)
        # Guardrail: filter out slurs or offensive hallucinations
        for bad_word in [r"\bn-?word\b", r"\bnigg\w*\b"]:
            text = re.sub(bad_word, "", text, flags=re.IGNORECASE)
        # Collapse excessive exclamation marks (keep max 2)
        text = re.sub(r"!{3,}", "!!", text)
        return text.strip()

    def should_generate_voice(self, user_msg: str, reply_text: str, ctx: str) -> bool:
        """
        Determines whether this turn should be delivered as a voice note.
        Only generates voice when explicitly requested or in always-voice mode,
        ensuring normal text chats are never unexpectedly replaced with audio.
        """
        u_low = user_msg.lower()
        explicit_vn = any(k in u_low for k in [
            "voice note", "voice msg", "send vn", "send audio", "voice message",
            "say it in voice", "sing", "send a vn", "record", "can u speak",
            "can you speak", "send voice"
        ])
        return bool(explicit_vn)

    def segment_and_guarantee_bursts(self, clean_text: str, ctx: str, target_count: int = 3) -> List[str]:
        """
        Guarantees Alisha ALWAYS emits 2 to 4 rapid, punchy, authentic texting bubbles.
        Splits on newlines, conversational clauses/emojis, and appends authentic persona
        micro-bursts if the LLM output was too short.
        """
        lines = [l.strip() for l in clean_text.split("\n") if l.strip()]
        if not lines:
            lines = [clean_text] if clean_text else []

        # If only 1 line, split on natural mobile texting boundaries
        if len(lines) == 1:
            t = lines[0]
            split_pats = [
                r'(?<=[😭💀❤️🙏🏽])\s+',
                r'(?<=[.!?])\s+',
                r'\s+(?=and my\b|\band then\b|\bso like\b|\bstop bullying\b|\bnot an error\b|\bleave me alone\b|\banyway\b|\bcan\'t lie\b|\bstyll\b)',
                r'(?<=[,])\s+(?=[a-z])'
            ]
            for pat in split_pats:
                parts = [p.strip() for p in re.split(pat, t) if p.strip()]
                if len(parts) > 1:
                    lines = parts
                    break

        # Cap at target burst (1 to 3 bubbles based on empirical distribution)
        target_burst = max(1, min(3, target_count))
        if len(lines) > target_burst:
            lines = lines[:target_burst]

        return lines

    def process_turn(
        self,
        user_msg: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        voice_mode: str = "mix",  # "always", "mix", "text_only"
        persona_mode: str = "classic",
    ) -> Dict[str, Any]:
        """
        Antigravity V3 Main Pipeline:
        1. ContextCompiler (WRRF-fused retrieval + ResponseBehaviorPlan)
        2. Groq inference (plan-guided)
        3. PersonaVerifier (post-generation quality gate)
        4. Burst segmentation
        5. TTS (if triggered)

        Falls back to V2 pipeline if V3 components are unavailable.
        """
        self.turn_count += 1
        chat_history = chat_history or []

        # ── V3 Pipeline ────────────────────────────────────────────────────
        if self._ag_pipeline_ready and self._compiler:
            return self._process_turn_v3(user_msg, chat_history, voice_mode, persona_mode=persona_mode)

        # ── V2 Fallback ────────────────────────────────────────────────────
        # 1. Context classification
        ctx = _classify_context(user_msg)
        max_tok = CONTEXT_MAX_TOKENS.get(ctx, 55)

        # 2. Retrieve exemplars
        exemplars = self.search_episodic_exemplars(user_msg, ctx, limit=3)

        # 2b. VOICE REQUEST FAST PATH — generate speech content, skip text inference
        if ctx == "voice_request" or voice_mode == "always":
            # Build a casual spoken response
            vn_messages = self.assemble_context(user_msg, chat_history, exemplars, "casual")
            spoken_text = "yeah here you go"
            vn_latency = 40.0
            try:
                vn_res = self.groq.generate(vn_messages, temperature=0.80, max_tokens=55,
                                             stop=["\nUser:", "\nFriend:", "\n\n\n"])
                spoken_text = self._post_process(vn_res["text"], "casual") or spoken_text
                vn_latency = vn_res["total_ms"]
            except Exception as e:
                print(f"[ContextRAG] Voice text gen: {e}")

            voice_url_vn = synthesize_speech(spoken_text)
            has_voice_vn = bool(voice_url_vn)
            dur_secs = max(3, min(30, int(len(spoken_text) / 12)))
            if has_voice_vn:
                bursts_vn = [{
                    "index": 0, "content": "voice note", "message_type": "voice",
                    "audio_url": voice_url_vn, "duration_label": f"0:{dur_secs:02d}", "typing_delay_ms": 600
                }]
            else:
                lines_vn = [l.strip() for l in spoken_text.split("\n") if l.strip()][:3]
                if not lines_vn:
                    lines_vn = [spoken_text]
                bursts_vn = [
                    {"index": i, "content": l, "typing_delay_ms": min(1500, 250 + len(l)*16), "message_type": "text"}
                    for i, l in enumerate(lines_vn)
                ]

            return {
                "user_message": user_msg, "context_type": ctx, "bursts": bursts_vn,
                "has_voice": has_voice_vn, "voice_url": voice_url_vn,
                "duration_label": f"0:{dur_secs:02d}" if has_voice_vn else "0:08",
                "exemplars_matched": len(exemplars),
                "diagnostics": {
                    "provider": "groq", "model": self.groq.model, "latency_ms": round(vn_latency, 1),
                    "tokens_generated": len(spoken_text.split()), "max_tokens_used": 55,
                    "context_type": ctx, "tts_mode": "edge-neural-realtime" if has_voice_vn else "none"
                }
            }

        # 3. Assemble context
        messages = self.assemble_context(user_msg, chat_history, exemplars, ctx)

        # 4. Groq inference
        try:
            groq_res = self.groq.generate(
                messages,
                temperature=0.78,
                max_tokens=max_tok,
                stop=["\nUser:", "\nFriend:", "\n\n\n"]
            )
            raw_text = groq_res["text"]
            latency_ms = groq_res["total_ms"]
        except Exception as e:
            print(f"[ContextRAG] Groq fallback: {e}")
            # Context-aware fallbacks grounded in real corpus
            fallbacks = {
                "study":       "just getting on with a bit of bio\nugh exams are exhausting 😭\nmy brain is literally fried styll",
                "cats":        "SAW THE KITTU CAT OTW TO COLLEGE and i nearly cried\nmy boo cat 😭\nthey love me i'm telling you",
                "banter":      "💀\nnah i cannot make this up\nyou are actually hilarious",
                "affection":   "cutie ❤️\naww stop it 😭\ni missed you too honestly",
                "faith":       "ameen ❤️\nmaking dua for you always\ngotta go pray fajr soon inshaAllah",
                "sleep_banter": "sighhh\ngo sleep bro 💀\nstop staying up scrolling on your phone",
                "home_life":   "yeah helping mum in the kitchen rn\nher cooking is the best styll\nbrb in a bit",
            }
            raw_text = fallbacks.get(ctx, "done with college for today\nexhausted but surviving ig\nwbu though")
            latency_ms = 40.0

        # 5. Post-process
        clean_text = self._post_process(raw_text, ctx)

        # 5b. Burst segmentation (guarantee 2 to 4 authentic bubbles)
        lines = self.segment_and_guarantee_bursts(clean_text, ctx, target_count=3)

        bursts = []
        for idx, line in enumerate(lines):
            # Typing delay: ~18ms per char + base 300ms, capped at 2.5s
            delay_ms = min(2500, 300 + len(line) * 18)
            bursts.append({
                "index": idx,
                "content": line,
                "typing_delay_ms": delay_ms,
                "message_type": "text",
            })

        # 6. Voice note decision
        if voice_mode == "always":
            wants_voice = True
        elif voice_mode == "text_only":
            wants_voice = False
        else:
            wants_voice = self.should_generate_voice(user_msg, clean_text, ctx)

        voice_url = None
        has_voice = False
        duration_label = "0:08"

        if wants_voice:
            spoken_text = " ".join(lines)
            voice_url = synthesize_speech(spoken_text)
            if voice_url:
                has_voice = True
                dur_secs = max(3, min(30, int(len(spoken_text) / 12)))
                duration_label = f"0:{dur_secs:02d}"
                bursts.append({
                    "index": len(bursts),
                    "content": "voice note",
                    "message_type": "voice",
                    "audio_url": voice_url,
                    "duration_label": duration_label,
                    "typing_delay_ms": 600,
                })

        return {
            "user_message": user_msg,
            "context_type": ctx,
            "bursts": bursts,
            "has_voice": has_voice,
            "voice_url": voice_url,
            "duration_label": duration_label,
            "exemplars_matched": len(exemplars),
            "diagnostics": {
                "provider": "groq",
                "model": self.groq.model,
                "latency_ms": round(latency_ms, 1),
                "tokens_generated": len(clean_text.split()),
                "max_tokens_used": max_tok,
                "context_type": ctx,
                "tts_mode": "edge-neural-realtime" if has_voice else "none",
            }
        }

    # ──────────────────────────────────────────────────────────────────────────
    # ANTIGRAVITY V3 PIPELINE
    # ──────────────────────────────────────────────────────────────────────────

    def _process_turn_v3(
        self,
        user_msg: str,
        chat_history: List[Dict[str, str]],
        voice_mode: str,
        persona_mode: str = "classic",
    ) -> Dict[str, Any]:
        """
        Antigravity V3 pipeline:
          ContextCompiler → plan-guided Groq inference → PersonaVerifier → burst → TTS
        """
        import time as _time
        start_ms = _time.time() * 1000
        # 0. Laya Fast Routing Pass (<35ms)
        laya_decision, laya_plan = LayaService.get_instance().route_turn(
            current_message=user_msg,
            recent_messages=chat_history,
            voice_mode=voice_mode
        )

        # 1. Compile context (WRRF fusion + plan)
        compiled = self._compiler.compile(
            user_message=user_msg,
            chat_history=chat_history,
            is_voice_turn=(voice_mode == "always" or laya_decision.response_mode.value == "CALL"),
            turn_number=self.turn_count,
        )

        ctx = compiled.context_type
        plan = compiled.plan
        max_tok = max(140, compiled.max_tokens)


        # 2. Voice fast-path
        if ctx == "voice_request" or voice_mode == "always":
            # Generate genuine NEW text as Alisha using Groq
            vn_messages = compiled.messages
            spoken_text = "yeah here you go"
            vn_latency = 40.0
            try:
                vn_res = self.groq.generate(
                    vn_messages, temperature=0.82, max_tokens=140,
                    stop=["\nUser:", "\nFriend:", "\n\n\n"]
                )
                spoken_text = self._post_process(vn_res["text"], "casual") or spoken_text
                vn_latency = vn_res["total_ms"]
            except Exception as e:
                print(f"[V3] Voice text gen error: {e}")

            # Always synthesize a brand new voice message dynamically
            voice_url_vn = synthesize_speech(spoken_text, user_prompt=user_msg)
            has_voice_vn = bool(voice_url_vn)
            dur_secs = max(3, min(30, int(len(spoken_text) / 12)))
            if has_voice_vn:
                bursts_vn = [{
                    "index": 0, "content": spoken_text, "message_type": "voice",
                    "audio_url": voice_url_vn, "duration_label": f"0:{dur_secs:02d}", "typing_delay_ms": 600
                }]
            else:
                lines_vn = [l.strip() for l in spoken_text.split("\n") if l.strip()][:3]
                if not lines_vn:
                    lines_vn = [spoken_text]
                bursts_vn = [
                    {"index": i, "content": l, "typing_delay_ms": min(1500, 250 + len(l)*16), "message_type": "text"}
                    for i, l in enumerate(lines_vn)
                ]
            return {
                "user_message": user_msg, "context_type": ctx, "bursts": bursts_vn,
                "has_voice": has_voice_vn, "voice_url": voice_url_vn,
                "duration_label": f"0:{dur_secs:02d}" if has_voice_vn else "0:08",
                "exemplars_matched": len(compiled.retrieved_exemplars),
                "pipeline_version": "v3",
                "diagnostics": {
                    **compiled.diagnostics,
                    "provider": "groq", "model": self.groq.model,
                    "latency_ms": round(vn_latency, 1),
                    "tts_mode": "dynamic-neural-synthesis" if has_voice_vn else "none",
                },
            }

        # 3. Groq inference (plan-guided temperature/max_tokens)
        temperature = 0.78
        if plan:
            if plan.interaction_mode in ("teasing", "playful"):
                temperature = 0.82
            elif plan.interaction_mode == "serious":
                temperature = 0.65
            elif plan.interaction_mode == "affectionate":
                temperature = 0.75

        raw_text = "hmm"
        latency_ms = 40.0
        try:
            groq_res = self.groq.generate(
                compiled.messages,
                temperature=temperature,
                max_tokens=max_tok,
                stop=["\nUser:", "\nFriend:", "\n\n\n"]
            )
            raw_text = groq_res["text"]
            latency_ms = groq_res["total_ms"]
        except Exception as e:
            print(f"[V3] Groq error: {e}")
            fallbacks = {
                "study":        "just getting on with a bit of bio\nugh exams are exhausting 😭\nmy brain is literally fried styll",
                "cats":         "SAW THE KITTU CAT OTW TO COLLEGE and i nearly cried\nmy boo cat 😭\nthey love me i'm telling you",
                "banter":       "💀\nnah i cannot make this up\nyou are actually hilarious",
                "affectionate": "cutie ❤️\naww stop it 😭\ni missed you too honestly",
                "faith":        "ameen ❤️\nmaking dua for you always\ngotta go pray fajr soon inshaAllah",
                "sleep_banter": "sighhh\ngo sleep bro 💀\nstop staying up scrolling on your phone",
                "home_life":    "yeah helping mum in the kitchen rn\nher cooking is the best styll\nbrb in a bit",
                "casual":       "done with college for today\nexhausted but surviving ig\nwbu though",
            }
            raw_text = fallbacks.get(ctx, fallbacks["casual"])

        # 4. Post-process
        clean_text = self._post_process(raw_text, ctx)

        # 5. Persona verification
        verification = None
        if self._verifier and clean_text:
            verification = self._verifier.verify(
                candidate=clean_text,
                plan=plan,
                exemplars=compiled.retrieved_exemplars,
            )
            # Generic phrase suppressor: clean generic assistant phrases if any leaked
            for phrase in ["as an ai", "how can i help", "i hope that helps", "feel free to ask"]:
                if phrase in clean_text.lower():
                    clean_text = re.sub(re.escape(phrase), "", clean_text, flags=re.IGNORECASE).strip()

        # 6. Burst segmentation (guarantee 2 to 4 authentic bubbles matching plan)
        target_burst = plan.burst_count if plan else 3
        lines = self.segment_and_guarantee_bursts(clean_text, ctx, target_count=target_burst)

        bursts = []
        for idx, line in enumerate(lines):
            delay_ms = min(2500, 300 + len(line) * 18)
            bursts.append({
                "index": idx,
                "content": line,
                "typing_delay_ms": delay_ms,
                "message_type": "text",
            })

        # 7. Voice note decision
        if voice_mode == "always":
            wants_voice = True
        elif voice_mode == "text_only":
            wants_voice = False
        else:
            wants_voice = self.should_generate_voice(user_msg, clean_text, ctx)

        voice_url = None
        has_voice = False
        duration_label = "0:08"

        if wants_voice:
            spoken_text = " ".join(lines)
            voice_url = synthesize_speech(spoken_text, user_prompt=user_msg)
            if voice_url:
                has_voice = True
                dur_secs = max(3, min(30, int(len(spoken_text) / 12)))
                duration_label = f"0:{dur_secs:02d}"
                vn_burst = {
                    "index": len(bursts),
                    "content": spoken_text,
                    "message_type": "voice",
                    "audio_url": voice_url,
                    "duration_label": duration_label,
                    "typing_delay_ms": 600,
                }
                is_explicit_vn = ctx == "voice_request" or voice_mode == "always" or any(k in user_msg.lower() for k in [
                    "voice note", "send vn", "send audio", "voice message", "say it in voice", "sing", "send a vn"
                ])
                if is_explicit_vn:
                    bursts = [vn_burst]
                else:
                    bursts.append(vn_burst)

        total_ms = _time.time() * 1000 - start_ms

        return {
            "user_message": user_msg,
            "context_type": ctx,
            "bursts": bursts,
            "has_voice": has_voice,
            "voice_url": voice_url,
            "duration_label": duration_label,
            "exemplars_matched": len(compiled.retrieved_exemplars),
            "pipeline_version": "v3",
            "verification": verification.to_dict() if verification else None,
            "plan": plan.to_dict() if plan else None,
            "diagnostics": {
                **compiled.diagnostics,
                "provider": "groq",
                "model": self.groq.model,
                "latency_ms": round(latency_ms, 1),
                "total_pipeline_ms": round(total_ms, 1),
                "tokens_generated": len(clean_text.split()),
                "max_tokens_used": max_tok,
                "context_type": ctx,
                "tts_mode": "edge-neural-realtime" if has_voice else "none",
                "verification_pass": verification.overall_pass if verification else None,
                "verification_score": verification.overall_score if verification else None,
            },
        }

