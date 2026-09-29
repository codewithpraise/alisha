"""
Benchmark Evaluation Runner for Alisha Bubbzieee.
Tests the simulation and inference engine on the held-out test split.
Outputs data/evaluation_report.json.
"""

import json
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if root not in sys.path:
    sys.path.insert(0, root)

from packages.inference.context_builder import ContextBuilder
from packages.inference.llm_client import LLMClient
from packages.personality.message_compositor import MessageCompositor
from packages.evaluation.evaluator import AlishaEvaluator


def run_evaluation(num_samples: int = 25):
    test_file = os.path.join(root, "data", "chat_test.jsonl")
    profile_path = os.path.join(root, "data", "friend_profile.json")
    db_path = os.path.join(root, "data", "memory.db")
    out_report = os.path.join(root, "data", "evaluation_report.json")

    with open(profile_path, "r", encoding="utf-8") as f:
        profile = json.load(f)

    builder = ContextBuilder(profile_path, db_path)
    llm = LLMClient()
    compositor = MessageCompositor(profile)
    evaluator = AlishaEvaluator()

    with open(test_file, "r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f if line.strip()]

    sample_lines = lines[:num_samples]
    scores = []
    detailed_results = []

    print(f"Running evaluation on {len(sample_lines)} held-out conversation pairs...")

    for idx, item in enumerate(sample_lines, 1):
        convs = item.get("conversations", [])
        user_turn = convs[1]["value"]
        real_alisha = convs[2]["value"]

        # Clean prompt
        user_msg = user_turn.split("Friend:")[-1].strip()
        prompt = builder.build_prompt(user_msg, [])
        raw_ai = llm.generate(prompt)
        bursts = compositor.compose(raw_ai)
        formatted_ai = "\n".join(b["content"] for b in bursts)

        res = evaluator.evaluate(formatted_ai, real_alisha)
        scores.append(res["composite_score"])
        detailed_results.append({
            "test_index": idx,
            "user_prompt": user_msg,
            "real_alisha": real_alisha,
            "generated_alisha": formatted_ai,
            "metrics": res,
        })

    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
    summary = {
        "total_evaluated": len(sample_lines),
        "average_composite_score": avg_score,
        "max_score": max(scores) if scores else 0.0,
        "min_score": min(scores) if scores else 0.0,
        "passing_rate": f"{sum(1 for s in scores if s >= 75) / len(scores) * 100:.1f}%",
        "detailed_results": detailed_results,
    }

    with open(out_report, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n=== EVALUATION REPORT SUMMARY ===")
    print(f"Total Evaluated:        {summary['total_evaluated']}")
    print(f"Average Composite Score: {summary['average_composite_score']} / 100")
    print(f"Authenticity Pass Rate: {summary['passing_rate']}")
    print(f"Report saved to:        {out_report}")
    print("=================================\n")


if __name__ == "__main__":
    run_evaluation()
