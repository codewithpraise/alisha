"""
Persona Verifier for Alisha AI Friend.

After generation, evaluates candidates against:
- Corpus-measured style metrics (deterministic)
- Response act match
- Length distribution fit
- Emoji profile fit
- Generic-assistant suppressor
- Relationship appropriateness

Returns structured scores. Does NOT rely solely on an LLM judge.
"""

import re
import math
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

from packages.persona import loader as persona_loader
from packages.planner import ResponseBehaviorPlan


# ── Generic assistant phrases to detect and penalize ─────────────────────────

GENERIC_ASSISTANT_PHRASES = [
    "how can i help",
    "how may i assist",
    "as an ai",
    "i'm here to help",
    "i hope that helps",
    "great question",
    "that's a great",
    "certainly!",
    "absolutely!",
    "of course!",
    "i understand how you feel",
    "i appreciate your",
    "thank you for sharing",
    "i'm sorry to hear",
    "feel free to ask",
    "let me know if you",
    "i'd be happy to",
    "furthermore",
    "in conclusion",
    "to summarize",
    "in addition",
    "it's important to note",
    "there are several",
    "based on my training",
    "my knowledge cutoff",
]

EMOJI_RE = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001F900-\U0001F9FF"
    "\U0001FA70-\U0001FAFF"
    "\U00002600-\U000026FF"
    "]+",
    flags=re.UNICODE,
)


@dataclass
class VerificationResult:
    """Structured verification scores. All 0.0–1.0 where 1.0 is best."""

    # Core scores
    context_fit: float = 1.0        # Does this make sense in context?
    style_fit: float = 1.0          # Does this sound like Alisha?
    length_fit: float = 1.0         # Is the length appropriate?
    emoji_fit: float = 1.0          # Is emoji use appropriate?
    slang_fit: float = 1.0          # Is slang level appropriate?
    response_act_fit: float = 1.0   # Is the speech act correct?
    relationship_fit: float = 1.0   # Is the relational tone correct?
    naturalness: float = 1.0        # Does it feel like a real text?
    fact_safety: float = 1.0        # No invented facts?
    copying_risk: float = 0.0       # High = copied verbatim from exemplar (bad)
    generic_suppression: float = 1.0 # 1.0 = no generic phrases detected

    # Pass/fail
    overall_pass: bool = True

    # Failure reasons (for debug)
    failure_reasons: List[str] = None

    def __post_init__(self):
        if self.failure_reasons is None:
            self.failure_reasons = []

    @property
    def overall_score(self) -> float:
        weights = {
            "style_fit": 0.20,
            "length_fit": 0.15,
            "response_act_fit": 0.15,
            "naturalness": 0.15,
            "generic_suppression": 0.15,
            "emoji_fit": 0.08,
            "slang_fit": 0.07,
            "relationship_fit": 0.05,
        }
        score = sum(
            getattr(self, k, 1.0) * w
            for k, w in weights.items()
        )
        return round(score, 3)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["overall_score"] = self.overall_score
        return d


class PersonaVerifier:
    """
    Evaluates generated candidates against the persona profile.
    Uses deterministic style features + plan matching.
    Does NOT call the LLM for evaluation (cost + latency).
    """

    # Minimum acceptable scores
    PASS_THRESHOLDS = {
        "length_fit": 0.2,
        "generic_suppression": 0.6,
        "naturalness": 0.4,
        "style_fit": 0.3,
    }

    def __init__(self):
        self._loaded = False

    def _lazy_load(self):
        if not self._loaded:
            self._emoji_prof = persona_loader.get_emoji_profile()
            self._burst_prof = persona_loader.get_burst_profile()
            self._profile = persona_loader.get_profile()
            self._loaded = True

    def verify(
        self,
        candidate: str,
        plan: Optional[ResponseBehaviorPlan] = None,
        exemplars: Optional[List[Dict]] = None,
        facts: Optional[List[Dict]] = None,
    ) -> VerificationResult:
        """
        Full verification of a single candidate response.
        """
        self._lazy_load()

        result = VerificationResult()
        reasons = []

        if not candidate or not candidate.strip():
            result.overall_pass = False
            result.failure_reasons = ["empty_response"]
            return result

        text = candidate.strip()
        text_lower = text.lower()

        # ── 1. Generic assistant suppressor ──────────────────────────────
        generic_hits = [
            phrase for phrase in GENERIC_ASSISTANT_PHRASES
            if phrase in text_lower
        ]
        if generic_hits:
            penalty = min(1.0, len(generic_hits) * 0.4)
            result.generic_suppression = max(0.0, 1.0 - penalty)
            reasons.append(f"generic_phrases_detected: {generic_hits[:3]}")

        # ── 2. Length fit ─────────────────────────────────────────────────
        char_len = len(text)
        if plan:
            min_len = plan.target_chars_min
            max_len = plan.target_chars_soft_max
        else:
            min_len = 3
            max_len = 280

        if char_len < min_len:
            # Very short — may still be valid (single emoji, one word)
            result.length_fit = 0.8 if char_len > 0 else 0.0
        elif char_len > max_len * 2:
            # Way too long
            penalty = min(0.5, (char_len - max_len) / max_len)
            result.length_fit = max(0.4, 1.0 - penalty)
            reasons.append(f"response_too_long: {char_len} chars (soft_max {max_len})")
        elif char_len > max_len:
            # Slightly long — totally fine for lively texting
            result.length_fit = 0.9
        else:
            result.length_fit = 1.0

        # ── 3. Emoji fit ──────────────────────────────────────────────────
        found_emojis = EMOJI_RE.findall(text)
        corpus_emoji_rate = self._emoji_prof.get("emoji_rate", 0.087)
        characteristic_emojis = set(self._emoji_prof.get("characteristic_emojis", []))

        if plan:
            if plan.emoji_policy == "none" and found_emojis:
                result.emoji_fit = 0.7  # Mild penalty — not catastrophic
                reasons.append("emoji_used_when_policy_none")
            elif plan.emoji_policy in ["encouraged", "optional"] and not found_emojis:
                # Fine — emoji is always optional
                result.emoji_fit = 0.9
            elif found_emojis:
                # Check if emojis used are characteristic to Alisha
                alien_emojis = [e for e in found_emojis if e not in characteristic_emojis]
                if alien_emojis and len(alien_emojis) == len(found_emojis):
                    result.emoji_fit = 0.6
                    reasons.append(f"non_characteristic_emojis: {alien_emojis[:3]}")
        else:
            # Just check rate sanity
            if len(found_emojis) > 5:
                result.emoji_fit = 0.6
                reasons.append("excessive_emoji_count")

        # ── 4. Style fit (capitalization, punctuation, assistant phrases) ──
        style_score = 1.0

        # Too many capitals (Alisha caps rate = 2.8%)
        alpha_chars = [c for c in text if c.isalpha()]
        if alpha_chars:
            caps_rate = sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
            if caps_rate > 0.3:
                penalty = (caps_rate - 0.3) * 0.7
                style_score -= min(0.4, penalty)
                reasons.append(f"too_many_capitals: {caps_rate:.2%}")

        # Formal connectors (very un-Alisha)
        formal_connectors = ["furthermore", "however,", "in conclusion", "therefore", "consequently"]
        if any(c in text_lower for c in formal_connectors):
            style_score -= 0.4
            reasons.append("formal_connectors_detected")

        # Markdown (bold, bullets, headers)
        if re.search(r"\*\*|^[-*]\s|\n#{1,6}\s", text, re.MULTILINE):
            style_score -= 0.3
            reasons.append("markdown_detected")

        # Numbered lists
        if re.search(r"^\d+\.\s", text, re.MULTILINE):
            style_score -= 0.3
            reasons.append("numbered_list_detected")

        result.style_fit = max(0.0, min(1.0, style_score))

        # ── 5. Response act fit ───────────────────────────────────────────
        if plan and plan.speech_acts:
            # Simple heuristic check: does the response perform the planned act?
            act_score = 1.0
            for act in plan.speech_acts:
                if not self._response_performs_act(text_lower, act):
                    act_score -= 0.15
            result.response_act_fit = max(0.4, min(1.0, act_score))
        # else: assume 1.0

        # ── 6. Naturalness ────────────────────────────────────────────────
        naturalness = 1.0

        # Too long for a casual chat = unnatural
        if char_len > 300:
            naturalness -= 0.3
            reasons.append("response_unusually_long")

        # Role prefix leaked into response
        for prefix in ["alisha:", "assistant:", "ai:", "me:"]:
            if text_lower.startswith(prefix):
                naturalness -= 0.5
                reasons.append(f"role_prefix_leaked: {prefix}")
                break

        # Think blocks (Qwen CoT leaked)
        if "<think>" in text or "</think>" in text:
            naturalness -= 0.6
            reasons.append("think_block_leaked")

        result.naturalness = max(0.0, min(1.0, naturalness))

        # ── 7. Copying risk ───────────────────────────────────────────────
        if exemplars:
            max_sim = 0.0
            for ex in exemplars[:5]:
                ex_response = ex.get("alisha_response", "")
                if ex_response:
                    sim = self._text_similarity(text, ex_response)
                    max_sim = max(max_sim, sim)

            result.copying_risk = round(max_sim, 3)
            if max_sim > 0.85:
                reasons.append(f"high_copying_risk: {max_sim:.2f}")

        # ── 8. Relationship fit ───────────────────────────────────────────
        result.relationship_fit = 1.0  # Default OK; deeper checks would need context

        # ── Overall pass/fail ─────────────────────────────────────────────
        failures = []
        for attr, threshold in self.PASS_THRESHOLDS.items():
            val = getattr(result, attr, 1.0)
            if val < threshold:
                failures.append(f"{attr}={val:.2f} < {threshold}")

        result.overall_pass = len(failures) == 0
        result.failure_reasons = reasons + failures

        return result

    def select_best_candidate(
        self,
        candidates: List[str],
        plan: Optional[ResponseBehaviorPlan] = None,
        exemplars: Optional[List[Dict]] = None,
    ) -> str:
        """
        Scores multiple candidates and returns the best one.
        Falls back to first candidate if all fail.
        """
        if not candidates:
            return "hmm"
        if len(candidates) == 1:
            return candidates[0]

        scored = []
        for candidate in candidates:
            result = self.verify(candidate, plan=plan, exemplars=exemplars)
            scored.append((result.overall_score, result.overall_pass, candidate))

        # Prefer passing candidates with highest score
        passing = [(s, c) for s, ok, c in scored if ok]
        if passing:
            passing.sort(key=lambda x: -x[0])
            return passing[0][1]

        # All failed — return highest scoring
        scored.sort(key=lambda x: -x[0])
        return scored[0][2]

    def _response_performs_act(self, text_lower: str, act: str) -> bool:
        ACT_SIGNALS = {
            "reaction": [r"\bomg\b", r"\bwait\b", r"\bno way\b", r"💀", r"😭", r"\bbruh\b"],
            "agreement": [r"\byeah\b", r"\byea\b", r"\bokay\b", r"\bfr\b", r"\btrue\b"],
            "disagreement": [r"\bnah\b", r"\bnope\b", r"\bno\b"],
            "teasing": [r"\bkidding\b", r"\bsmh\b", r"\blatw\b"],
            "affection": [r"\bcutie\b", r"\bbabycakes\b", r"❤️"],
            "question": [r"\?", r"\bwbu\b", r"\bhow\b"],
            "acknowledgment": [r"\boh\b", r"\bhmm\b", r"\bah\b", r"\bic\b"],
            "farewell": [r"\bbye\b", r"\bgn\b", r"\bnight\b"],
            "comfort": [r"it.s okay", r"you.re fine", r"don.t worry"],
        }
        signals = ACT_SIGNALS.get(act, [])
        if not signals:
            return True  # Can't verify this act
        return any(re.search(p, text_lower) for p in signals)

    def _text_similarity(self, a: str, b: str) -> float:
        """Simple word-overlap similarity (Jaccard)."""
        words_a = set(re.findall(r"\b\w{3,}\b", a.lower()))
        words_b = set(re.findall(r"\b\w{3,}\b", b.lower()))
        if not words_a or not words_b:
            return 0.0
        return len(words_a & words_b) / len(words_a | words_b)
