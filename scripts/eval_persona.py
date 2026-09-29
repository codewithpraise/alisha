#!/usr/bin/env python3
"""
scripts/eval_persona.py — Multi-turn Persona Benchmark & Distribution Comparison
Evaluates Generated Distribution against Ground Truth Corpus Distribution.
"""

import sys
import os
import json
import re
import math
from typing import Dict, Any, List, Tuple

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from packages.engine.context_rag import AlishaContextEngine
from packages.persona.loader import (
    get_profile,
    get_burst_profile,
    get_emoji_profile,
    get_address_terms,
    get_response_act_profile,
)

BENCHMARK_PROMPTS = [
    ("greeting", "hey alisha"),
    ("casual", "how was your day today?"),
    ("emotional", "feeling kinda drained and stressed today tbh"),
    ("family", "how's your family doing?"),
    ("studies", "got so much revision to do for exams"),
    ("cats", "saw the cutest stray cat sitting on a wall today"),
    ("faith", "make dua for my exams coming up"),
    ("banter", "you type with two thumbs and still take 5 minutes to reply"),
    ("affection", "miss you cutie ❤️"),
    ("sleep", "why are you still awake scrolling on your phone?"),
    ("food", "what did you have for dinner?"),
    ("weather", "it's literally freezing outside today"),
    ("plans", "any plans for the weekend?"),
    ("general_world", "explain quantum computing in simple terms"),
    ("general_world_2", "what makes the sky blue during sunset?"),
    ("spontaneous", "tell me something completely random"),
    ("daily_checkin", "what did you do today?"),
    ("simulation_continuity", "did you end up getting anything to eat?"),
]


def compute_js_divergence(p: Dict[str, float], q: Dict[str, float]) -> float:
    """Computes Jensen-Shannon divergence between two discrete probability distributions."""
    all_keys = set(p.keys()) | set(q.keys())
    m = {}
    for k in all_keys:
        m[k] = 0.5 * (p.get(k, 0.0) + q.get(k, 0.0))

    def kl(dist, ref):
        val = 0.0
        for k in all_keys:
            d_val = dist.get(k, 0.0)
            r_val = ref.get(k, 0.0)
            if d_val > 1e-9 and r_val > 1e-9:
                val += d_val * math.log2(d_val / r_val)
        return val

    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def run_evaluation() -> Dict[str, Any]:
    print("=" * 60)
    print("ALISHA AI FRIEND — MULTI-TURN PERSONA BENCHMARK")
    print("=" * 60)

    # 1. Ground Truth from Authentic Corpus
    burst_gt = get_burst_profile()
    gt_burst_dist = {
        str(k): v["probability"]
        for k, v in burst_gt.get("burst_size_distribution", {}).items()
        if int(k) <= 4
    }
    # Normalize gt_burst_dist over 1..4
    total_p = sum(gt_burst_dist.values()) or 1.0
    gt_burst_dist = {k: v / total_p for k, v in gt_burst_dist.items()}

    emoji_gt = get_emoji_profile()
    gt_emoji_rate = emoji_gt.get("emoji_rate", 0.087)

    addr_gt = get_address_terms()
    gt_sir_rate = 0.0083  # 0.83%
    gt_total_addr_rate = 0.02

    # 2. Run Multi-turn Benchmark
    ce = AlishaContextEngine()
    history = []
    generated_bubbles = []
    generated_turns = []
    bubble_counts = []
    has_emoji_count = 0
    sir_count = 0
    all_addr_count = 0
    all_text_chars = []
    lowercase_bubbles = 0
    total_bubbles = 0
    forced_biochem_on_unrelated = 0

    print(f"\nRunning {len(BENCHMARK_PROMPTS)} benchmark turns...")
    for idx, (cat, prompt) in enumerate(BENCHMARK_PROMPTS):
        res = ce.process_turn(prompt, chat_history=history)
        bursts = [b["content"] for b in res["bursts"]]
        generated_turns.append({"cat": cat, "prompt": prompt, "bursts": bursts})

        # Append to history
        for b in bursts:
            generated_bubbles.append(b)
            total_bubbles += 1
            all_text_chars.append(len(b))
            if b.islower():
                lowercase_bubbles += 1

            # Emoji detection
            if any(char in b for char in "😭💀❤️💪🏽🤨😍"):
                has_emoji_count += 1

            # Address term detection
            b_lower = b.lower()
            if re.search(r"\bsir\b", b_lower):
                sir_count += 1
                all_addr_count += 1
            elif any(re.search(rf"\b{w}\b", b_lower) for w in ["lad", "mate", "bro", "hun", "bbg", "cuh"]):
                all_addr_count += 1

            # Defect check: did general world knowledge or greeting force biochem/commute?
            if cat in ("greeting", "general_world", "general_world_2", "spontaneous"):
                if any(w in b_lower for w in ["biochem", "practical", "freezing train", "2 hour"]):
                    forced_biochem_on_unrelated += 1

        bubble_counts.append(len(bursts))

        # Feed assistant turn back into conversation history
        for b in bursts:
            history.append({"role": "assistant", "content": b})
        history.append({"role": "user", "content": prompt})

        print(f"[{idx+1:02d}/{len(BENCHMARK_PROMPTS):02d}] ({cat}) Q: {prompt[:30]:<30} -> {len(bursts)} bubbles: {bursts}")

    # 3. Calculate Generated Metrics
    gen_burst_dist = {}
    for c in bubble_counts:
        key = str(min(c, 4))
        gen_burst_dist[key] = gen_burst_dist.get(key, 0) + 1
    total_turns = len(bubble_counts)
    gen_burst_dist = {k: v / total_turns for k, v in gen_burst_dist.items()}

    js_burst = compute_js_divergence(gt_burst_dist, gen_burst_dist)
    gen_emoji_rate = round(has_emoji_count / max(1, total_bubbles), 4)
    gen_sir_rate = round(sir_count / max(1, total_bubbles), 4)
    gen_addr_rate = round(all_addr_count / max(1, total_bubbles), 4)
    gen_lowercase_rate = round(lowercase_bubbles / max(1, total_bubbles), 4)
    mean_bubble_length = round(sum(all_text_chars) / max(1, total_bubbles), 1)

    print("\n" + "=" * 60)
    print("DISTRIBUTION COMPARISON REPORT")
    print("=" * 60)
    print(f"Total Turns Evaluated: {total_turns}")
    print(f"Total Bubbles Generated: {total_bubbles}")
    print(f"Mean Bubble Length: {mean_bubble_length} chars (Corpus Median: 17 chars)")
    print(f"Lowercase Bubble Rate: {gen_lowercase_rate*100:.1f}% (Corpus: 97.2%)")
    print()
    print("BURST SIZE DISTRIBUTION:")
    for b in ["1", "2", "3", "4"]:
        print(f"  {b} Bubble(s): Generated = {gen_burst_dist.get(b, 0.0)*100:5.1f}% | Real Corpus = {gt_burst_dist.get(b, 0.0)*100:5.1f}%")
    print(f"  Jensen-Shannon Divergence: {js_burst:.4f} (Target: < 0.25)")
    print()
    print("STYLE & ADDRESS TERM BEHAVIOR:")
    print(f"  'sir' Address Rate: {gen_sir_rate*100:.2f}% (Real Corpus: {gt_sir_rate*100:.2f}%)")
    print(f"  All Address Terms Rate: {gen_addr_rate*100:.2f}% (Real Corpus: {gt_total_addr_rate*100:.2f}%)")
    print(f"  Emoji Rate: {gen_emoji_rate*100:.1f}% (Real Corpus: {gt_emoji_rate*100:.1f}%)")
    print()
    print("DEFECT & REPETITION METRICS:")
    print(f"  Forced Biochem/Commute on Unrelated Queries: {forced_biochem_on_unrelated} / {total_bubbles} bubbles")
    print(f"  Persona Collapse Status: {'RESOLVED' if forced_biochem_on_unrelated == 0 and gen_sir_rate < 0.08 else 'FAILED'}")
    print("=" * 60)

    report = {
        "total_turns": total_turns,
        "total_bubbles": total_bubbles,
        "mean_bubble_length": mean_bubble_length,
        "lowercase_rate": gen_lowercase_rate,
        "js_burst_divergence": round(js_burst, 4),
        "gen_burst_distribution": gen_burst_dist,
        "gt_burst_distribution": gt_burst_dist,
        "gen_sir_rate": gen_sir_rate,
        "gt_sir_rate": gt_sir_rate,
        "gen_emoji_rate": gen_emoji_rate,
        "gt_emoji_rate": gt_emoji_rate,
        "forced_biochem_on_unrelated": forced_biochem_on_unrelated,
        "persona_collapse_resolved": bool(forced_biochem_on_unrelated == 0 and gen_sir_rate < 0.08)
    }

    report_path = os.path.join(ROOT, "docs", "debug", "eval_persona_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Saved benchmark report to {report_path}")

    return report


if __name__ == "__main__":
    run_evaluation()
