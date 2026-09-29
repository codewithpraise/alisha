"""
Test: Antigravity V3 Pipeline Components
Tests all new components: Persona profiles, FactService, ResponseBehaviorPlanner,
ContextCompiler, PersonaVerifier, and AlishaContextEngine V3 routing.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPersonaProfiles(unittest.TestCase):
    def test_profiles_load(self):
        from packages.persona.loader import (
            get_profile, get_statistics, get_burst_profile, get_emoji_profile,
            get_median_length_chars, get_burst_probability, get_emoji_rate
        )
        profile = get_profile()
        self.assertIn("persona_name", profile)
        self.assertEqual(profile["persona_name"], "Alisha")

        stats = get_statistics()
        self.assertIn("corpus", stats)

        self.assertGreater(get_median_length_chars(), 0)
        self.assertGreater(get_burst_probability(), 0)
        self.assertLess(get_burst_probability(), 1)
        self.assertGreater(get_emoji_rate(), 0)
        self.assertLess(get_emoji_rate(), 1)

    def test_top_slang_non_empty(self):
        from packages.persona.loader import get_top_slang
        slang = get_top_slang()
        self.assertIsInstance(slang, list)
        self.assertGreater(len(slang), 0)

    def test_exemplars_exist(self):
        import os
        path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "persona", "exemplars", "stimulus_response_pairs.jsonl"
        )
        self.assertTrue(os.path.exists(path), "Exemplars file not found")
        with open(path, encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        self.assertGreater(len(lines), 0, "No exemplars found")


class TestFactService(unittest.TestCase):
    def setUp(self):
        from packages.facts import get_fact_service
        self.fs = get_fact_service()

    def test_seeded_facts_exist(self):
        facts = self.fs.lookup(subject="alisha")
        self.assertGreater(len(facts), 0)

    def test_studies_fact_verified(self):
        facts = self.fs.lookup(subject="alisha", predicate="studies")
        self.assertGreater(len(facts), 0)
        self.assertEqual(facts[0].status, "verified")
        self.assertGreater(facts[0].confidence, 0.9)

    def test_prompt_block_format(self):
        block = self.fs.get_fact_prompt_block("she studies biology")
        self.assertIn("VERIFIED FACTS", block)

    def test_add_fact_and_retrieve(self):
        fact_id, action = self.fs.add_fact(
            subject="alisha",
            predicate="test_predicate_unique_12345",
            value="test value xyz",
            confidence=0.7,
        )
        self.assertIn(action, ("inserted", "updated", "superseded_old"))
        facts = self.fs.lookup(subject="alisha", predicate="test_predicate_unique_12345", include_unknown=True)
        self.assertGreater(len(facts), 0)


class TestResponseBehaviorPlanner(unittest.TestCase):
    def setUp(self):
        from packages.planner import ResponseBehaviorPlanner
        self.planner = ResponseBehaviorPlanner()

    def test_plan_returns_valid_object(self):
        from packages.planner import ResponseBehaviorPlan
        plan = self.planner.plan("hey wyd", context_type="casual")
        self.assertIsInstance(plan, ResponseBehaviorPlan)

    def test_banter_mode(self):
        plan = self.planner.plan("omg bro 💀", context_type="banter")
        self.assertIn(plan.interaction_mode, ("playful", "excited", "teasing", "casual"))

    def test_affectionate_mode(self):
        plan = self.planner.plan("i miss you cutie", context_type="affection")
        self.assertIn(plan.interaction_mode, ("affectionate",))

    def test_faith_mode(self):
        plan = self.planner.plan("ameen making dua", context_type="faith")
        self.assertEqual(plan.interaction_mode, "serious")

    def test_burst_count_range(self):
        for _ in range(10):
            plan = self.planner.plan("hey", context_type="casual")
            self.assertGreaterEqual(plan.burst_count, 1)
            self.assertLessEqual(plan.burst_count, 3)

    def test_length_bounds(self):
        plan = self.planner.plan("hi", context_type="casual")
        self.assertGreater(plan.target_chars_max, plan.target_chars_min)
        self.assertGreater(plan.target_chars_soft_max, 0)

    def test_plan_to_dict(self):
        plan = self.planner.plan("test", context_type="casual")
        d = plan.to_dict()
        self.assertIn("interaction_mode", d)
        self.assertIn("speech_acts", d)

    def test_plan_to_prompt_block(self):
        plan = self.planner.plan("test", context_type="casual")
        block = plan.to_prompt_block()
        self.assertIn("RESPONSE BEHAVIOR PLAN", block)


class TestPersonaVerifier(unittest.TestCase):
    def setUp(self):
        from packages.verifier import PersonaVerifier
        self.verifier = PersonaVerifier()

    def test_good_response_passes(self):
        result = self.verifier.verify("yeah ig lmao")
        self.assertGreater(result.overall_score, 0.7)
        self.assertTrue(result.overall_pass)

    def test_single_word_passes(self):
        result = self.verifier.verify("hmm")
        self.assertTrue(result.overall_pass)

    def test_generic_assistant_fails(self):
        result = self.verifier.verify(
            "Great question! As an AI assistant I am here to help you with that."
        )
        self.assertFalse(result.overall_pass)
        self.assertLess(result.generic_suppression, 0.7)

    def test_formal_style_penalized(self):
        result = self.verifier.verify(
            "Furthermore, it is important to note that this is a comprehensive explanation."
        )
        self.assertLess(result.style_fit, 0.7)

    def test_think_block_penalized(self):
        result = self.verifier.verify("<think>let me think about this</think>yeah okay")
        self.assertLess(result.naturalness, 0.7)

    def test_select_best_candidate(self):
        candidates = [
            "Great question! As an AI I'm here to help!",  # bad
            "yeah ig lmao",  # good
            "hmm",  # good
        ]
        best = self.verifier.select_best_candidate(candidates)
        self.assertIn(best, ["yeah ig lmao", "hmm"])


class TestContextCompiler(unittest.TestCase):
    def setUp(self):
        from packages.context import ContextCompiler
        self.compiler = ContextCompiler()

    def test_compile_returns_context(self):
        from packages.context import CompiledContext
        result = self.compiler.compile("hey wyd", chat_history=[])
        self.assertIsInstance(result, CompiledContext)

    def test_messages_have_system(self):
        result = self.compiler.compile("hey wyd", chat_history=[])
        self.assertGreater(len(result.messages), 0)
        self.assertEqual(result.messages[0]["role"], "system")
        self.assertIn("Alisha", result.messages[0]["content"])

    def test_context_classification(self):
        from packages.context import classify_context
        cases = [
            ("hey how are you", "casual"),
            ("omg bro", "banter"),
            ("got a chem practical", "study"),
            ("i saw a cat", "cats"),
            ("ameen", "faith"),
            ("mum is making dinner", "home_life"),
        ]
        for msg, expected in cases:
            result = classify_context(msg)
            self.assertEqual(result, expected, f"classify_context({msg!r}): expected {expected}, got {result}")

    def test_plan_is_attached(self):
        result = self.compiler.compile("hey wyd", chat_history=[])
        self.assertIsNotNone(result.plan)
        self.assertIsNotNone(result.plan.interaction_mode)

    def test_history_injected(self):
        history = [
            {"role": "user", "content": "how was college"},
            {"role": "assistant", "content": "ugh so tired"},
        ]
        result = self.compiler.compile("same", chat_history=history)
        # Should have system + history turns + current
        self.assertGreaterEqual(len(result.messages), 3)

    def test_token_estimate_reasonable(self):
        result = self.compiler.compile("hey", chat_history=[])
        self.assertGreater(result.token_estimate, 100)
        self.assertLess(result.token_estimate, 5000)


class TestEngineV3Routing(unittest.TestCase):
    def test_engine_v3_ready(self):
        from packages.engine.context_rag import AlishaContextEngine
        engine = AlishaContextEngine()
        self.assertTrue(engine._ag_pipeline_ready, "V3 pipeline should be ready")

    def test_compiler_attached(self):
        from packages.engine.context_rag import AlishaContextEngine
        engine = AlishaContextEngine()
        self.assertIsNotNone(engine._compiler)
        self.assertIsNotNone(engine._verifier)


if __name__ == "__main__":
    unittest.main(verbosity=2)
