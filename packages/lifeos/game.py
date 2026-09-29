"""
SIGNAL Cognitive Game Engine
Deterministic, offline-first 60-120 second adaptive mental agility challenge.
Trains and evaluates:
1. Working Memory (MEMORY mode) - Sequence recall & reconstruction.
2. Response Inhibition & Selective Attention (FOCUS mode) - Go/No-Go & 2-back distractors.
3. Cognitive Flexibility (SWITCH mode) - Dynamic rule-switching under time pressure.
Includes adaptive difficulty, date-seeded Daily Challenges, and asynchronous Friend Challenges.
"""

import random
import time
from datetime import date
from typing import Dict, Any, List, Optional


class SignalGameEngine:
    """Local deterministic cognitive game engine."""

    SYMBOLS = ["amber_pulse", "emerald_flash", "sapphire_glow", "ruby_flare"]
    COLORS = ["amber", "emerald", "sapphire", "ruby"]
    SHAPES = ["circle", "triangle", "square", "diamond"]

    def __init__(self):
        self.symbols = list(self.SYMBOLS)

    def generate_round(self, level: int = 1, seed: Optional[int] = None, mode: str = "memory") -> Dict[str, Any]:
        """
        Generates a round tailored to the requested mode:
        - memory: sequence reconstruction with increasing length.
        - focus: Go/No-Go inhibition stream with target rule and distractors.
        - switch: Rule-switching challenge where target definition shifts.
        """
        rng = random.Random(seed if seed is not None else int(time.time() * 1000) % 100000)
        mode_lower = mode.lower()

        if mode_lower == "focus":
            # Focus / Go-No-Go Mode
            stream_len = min(12, 5 + level)
            stream = [rng.choice(self.symbols) for _ in range(stream_len)]
            target_symbol = rng.choice(self.symbols)
            rule_desc = f"Tap only on [{target_symbol.replace('_', ' ').title()}]. Inhibit/ignore all other signals."
            expected_targets = [s for s in stream if s == target_symbol]
            time_limit_ms = max(8000, 20000 - (level * 1000))

            return {
                "level": level,
                "mode": "focus",
                "target_rule": rule_desc,
                "target_symbol": target_symbol,
                "stream": stream,
                "stream_length": stream_len,
                "expected": expected_targets,
                "time_limit_ms": time_limit_ms,
                "base_points": 120 * level
            }

        elif mode_lower == "switch":
            # Switch / Cognitive Flexibility Mode
            rules = [
                {"id": "rule_direct", "desc": "Tap the matching symbol in direct order"},
                {"id": "rule_invert", "desc": "Tap the inverted/opposite symbol"},
                {"id": "rule_color_only", "desc": "Match by color tone only"},
                {"id": "rule_reverse", "desc": "Tap the sequence in REVERSE order"}
            ]
            active_rule = rules[(level - 1) % len(rules)]
            seq_len = min(7, 3 + (level // 2))
            sequence = [rng.choice(self.symbols) for _ in range(seq_len)]
            time_limit_ms = max(10000, 22000 - (level * 1200))

            expected = list(reversed(sequence)) if active_rule["id"] == "rule_reverse" else sequence

            return {
                "level": level,
                "mode": "switch",
                "active_rule": active_rule["desc"],
                "rule_id": active_rule["id"],
                "sequence": sequence,
                "sequence_length": seq_len,
                "expected": expected,
                "time_limit_ms": time_limit_ms,
                "base_points": 150 * level
            }

        else:
            # Memory Mode (Default)
            seq_len = min(8, 2 + max(1, level))
            sequence = [rng.choice(self.symbols) for _ in range(seq_len)]
            time_limit_ms = max(12000, 25000 - (level * 1500))

            has_distractor = level >= 4
            distractor = rng.choice(self.symbols) if has_distractor else None
            inhibit_rule = f"Inhibition Rule: Ignore {distractor.replace('_', ' ').title()}" if has_distractor else None

            return {
                "level": level,
                "mode": "memory",
                "sequence": sequence,
                "sequence_length": seq_len,
                "has_distractor": has_distractor,
                "distractor": distractor,
                "inhibit_rule": inhibit_rule,
                "expected": sequence,
                "time_limit_ms": time_limit_ms,
                "base_points": 100 * level,
                "speed_bonus_max": 50 * level
            }

    def evaluate_submission(self, level: int = 1, user_inputs: Optional[List[str]] = None,
                            expected_seq: Optional[List[str]] = None, elapsed_ms: int = 5000,
                            combo: int = 0, inputs: Optional[List[str]] = None,
                            expected: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Evaluates correctness, calculates score with combo multipliers, reaction speed,
        and computes adaptive difficulty action (increase, maintain, or ease).
        """
        actual_inputs = user_inputs if user_inputs is not None else (inputs or [])
        actual_expected = expected_seq if expected_seq is not None else (expected or [])

        correct = (actual_inputs == actual_expected)
        
        # Calculate accuracy & metrics
        total_items = max(1, len(actual_expected))
        matches = sum(1 for a, b in zip(actual_inputs, actual_expected) if a == b)
        accuracy = (matches / total_items) if correct else max(0.0, (matches / total_items) * 0.8)

        # Adaptive Difficulty Logic
        if correct and elapsed_ms < 3000:
            adaptive_action = "increase"
            next_level = level + 1
        elif correct:
            adaptive_action = "maintain"
            next_level = level + 1
        elif accuracy >= 0.5:
            adaptive_action = "maintain"
            next_level = max(1, level)
        else:
            adaptive_action = "ease"
            next_level = max(1, level - 1)

        if not correct:
            return {
                "correct": False,
                "success": False,
                "score_earned": 0,
                "combo": 0,
                "next_level": next_level,
                "adaptive_action": adaptive_action,
                "accuracy_pct": int(accuracy * 100),
                "reaction_time_ms": elapsed_ms,
                "message": "Signal interrupted. Resetting focus."
            }

        base = 100 * level
        speed_bonus = max(0, int((15000 - elapsed_ms) / 100))
        combo_mult = 1.0 + (combo * 0.15)
        total_round_score = int((base + speed_bonus) * combo_mult)

        return {
            "correct": True,
            "success": True,
            "score_earned": total_round_score,
            "combo": combo + 1,
            "speed_bonus": speed_bonus,
            "multiplier": round(combo_mult, 2),
            "next_level": next_level,
            "adaptive_action": adaptive_action,
            "accuracy_pct": 100,
            "reaction_time_ms": elapsed_ms,
            "message": "Clean signal locked!"
        }

    def get_daily_challenge(self, target_date: Optional[date] = None) -> Dict[str, Any]:
        """Returns deterministic 7-level daily challenge seeded by calendar date."""
        d = target_date or date.today()
        seed = d.toordinal()
        rng = random.Random(seed)

        seed_id = f"daily_{d.isoformat()}"
        rounds = []
        for lvl in range(1, 8):
            mode = "memory" if lvl <= 3 else ("focus" if lvl <= 5 else "switch")
            rounds.append(self.generate_round(level=lvl, seed=seed + lvl, mode=mode))

        return {
            "seed_id": seed_id,
            "date": d.isoformat(),
            "target_score": 6500,
            "total_levels": 7,
            "rounds_preview": len(rounds),
            "rounds": rounds
        }

    def create_friend_challenge(self, score: int, level: int = 5, mode: str = "memory") -> Dict[str, Any]:
        """Creates an asynchronous challenge payload that friends can attempt."""
        challenge_id = f"sig_{int(time.time())}_{score}"
        return {
            "challenge_id": challenge_id,
            "score_to_beat": score,
            "level": level,
            "mode": mode,
            "share_code": f"SIGNAL-{score}-{level}",
            "share_text": f"Can you beat my SIGNAL score of {score:,} in {mode.upper()} mode?"
        }

    def simulate_alisha_challenge(self, player_score: int = 0, user_score: Optional[int] = None,
                                 score: Optional[int] = None) -> Dict[str, Any]:
        """
        Asynchronous challenge response from Alisha friend mode.
        Playful, characteristic responses that match her persona without modifying game logic.
        """
        target_score = score if score is not None else (user_score if user_score is not None else player_score)
        target = int(target_score * random.uniform(0.88, 1.12))
        if target > target_score:
            msg = random.choice([
                f"lmao i got {target:,} 😭 try harder bby",
                f"{target:,}!! told u my reflexes r insaneee",
                f"wait i actually beat u haha {target:,} 💅"
            ])
            outcome = "alisha_ahead"
        else:
            msg = random.choice([
                f"HOW did u get {target_score:,} wtff 😭😭",
                f"okay okay u win this round... rematch rn",
                f"my thumb literally slipped!! u got lucky 😤"
            ])
            outcome = "player_ahead"

        return {
            "alisha_score": target,
            "outcome": outcome,
            "chat_response": msg,
            "mode": "async_challenge"
        }
