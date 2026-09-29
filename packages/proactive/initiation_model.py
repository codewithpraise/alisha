"""
Proactive Initiation Engine for Alisha Bubbzieee.
Determines whether Alisha should text first based on peak hours,
unresolved threads, time elapsed, and social initiation probability.
"""

from datetime import datetime
import json
import os
import random
import sys
import time
from typing import Dict, Any, Optional

current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if root not in sys.path:
    sys.path.insert(0, root)

from packages.memory.retriever import MemoryRetriever
from packages.proactive.quality_gate import passes_quality_gate


def evaluate_initiation(
    profile_path: str,
    db_path: str,
    override_hour: Optional[int] = None,
) -> Dict[str, Any]:
    with open(profile_path, "r", encoding="utf-8") as f:
        profile = json.load(f)

    retriever = MemoryRetriever(db_path)
    state = retriever.get_friend_state()

    current_hour = override_hour if override_hour is not None else datetime.now().hour
    peak_hours = profile.get("timing_metrics", {}).get("peak_hours", [12, 13, 17, 18, 19])
    base_init_rate = profile.get("social_metrics", {}).get("initiation_rate", 0.57)

    score = 0.0
    factors = []

    # 1. Peak hour bonus
    if current_hour in peak_hours:
        score += 0.30
        factors.append(f"Peak active hour ({current_hour}:00)")

    # 2. Unresolved threads bonus
    unfinished = state.get("unfinished_threads")
    has_threads = unfinished and unfinished != "[]"
    if has_threads:
        score += 0.35
        factors.append("Active unresolved conversational thread")

    # 3. Base social initiation prior
    score += base_init_rate * 0.25
    factors.append(f"Empirical initiation prior ({base_init_rate:.2f})")

    # Normalize score 0..1
    final_score = round(min(1.0, score), 3)
    threshold = 0.50
    should_initiate = final_score >= threshold

    candidate_message = None
    style_category = "none"

    if should_initiate:
        # Pick initiation style
        styles = ["continuation", "random_share", "check_in"]
        weights = [0.45, 0.30, 0.25] if has_threads else [0.20, 0.45, 0.35]
        style_category = random.choices(styles, weights=weights)[0]

        if style_category == "continuation":
            threads = retriever.get_ongoing_threads()
            if threads:
                candidate_message = f"wait so what happened with {threads[0].lower()}"
            else:
                candidate_message = "so what happened with that thing"
        elif style_category == "random_share":
            options = [
                "bro look at this 💀",
                "okay wait listen to this",
                "i literally just remembered something",
                "bro i cannot make this up 😭",
            ]
            candidate_message = random.choice(options)
        else:  # check_in
            options = [
                "where did you disappear",
                "u alive? 🤨",
                "what are you up to rn",
                "hey cutie what's up",
            ]
            candidate_message = random.choice(options)

        # Pass through Quality Gate
        if not passes_quality_gate(candidate_message):
            should_initiate = False
            candidate_message = None

    return {
        "should_initiate": should_initiate,
        "score": final_score,
        "threshold": threshold,
        "factors": factors,
        "style_category": style_category,
        "message": candidate_message,
        "timestamp": int(time.time()),
    }
