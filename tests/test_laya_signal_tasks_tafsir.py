import unittest
import sys
import os
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from packages.laya import LayaService, LayaRouter, LayaDecision, ResponseBehaviorPlan
from packages.laya.types import ResponseMode, RetrievalNeed, MemoryNeed, InteractionMode, ResponseAct
from packages.lifeos import SignalGameEngine, TaskManager, TafsirHadithEngine


class TestLayaRoutingSuite(unittest.TestCase):
    def setUp(self):
        self.laya = LayaService.get_instance()

    def test_casual_fast_routing(self):
        dec, plan = self.laya.route_turn("yo wyd lol")
        self.assertEqual(dec.response_mode, ResponseMode.FAST)
        self.assertIn(dec.retrieval_need, (RetrievalNeed.NONE, RetrievalNeed.LIGHT))
        self.assertIsInstance(plan, ResponseBehaviorPlan)
        self.assertLessEqual(plan.target_bubble_count, 2)

    def test_deep_memory_recall_routing(self):
        dec, plan = self.laya.route_turn("remember what I told you about my exam on Friday?")
        self.assertEqual(dec.response_mode, ResponseMode.DEEP)
        self.assertEqual(dec.retrieval_need, RetrievalNeed.DEEP)
        self.assertIn(dec.memory_need, (MemoryNeed.RECALL, MemoryNeed.WRITE))
        self.assertTrue(dec.historical_reference)
        self.assertGreaterEqual(plan.target_bubble_count, 1)

    def test_voice_call_routing(self):
        dec, plan = self.laya.route_turn("can you hear me?", voice_mode="always")
        self.assertEqual(dec.response_mode, ResponseMode.CALL)
        self.assertEqual(plan.target_bubble_count, 1)

    def test_memory_write_routing(self):
        dec, plan = self.laya.route_turn("actually remember that my meeting is moved to 4pm")
        self.assertEqual(dec.memory_need, MemoryNeed.WRITE)

    def test_memory_forget_routing(self):
        dec, plan = self.laya.route_turn("forget that please")
        self.assertEqual(dec.memory_need, MemoryNeed.FORGET)

    def test_confidence_gating_and_fallback(self):
        # Empty or ambiguous input falls back cleanly with high safety
        dec, plan = self.laya.route_turn("...")
        self.assertIsNotNone(dec.response_mode)
        self.assertGreaterEqual(dec.confidence, 0.5)

    def test_candidate_compliance_verification(self):
        plan = ResponseBehaviorPlan(
            mode="CASUAL",
            speech_act="GREETING",
            length_class="SHORT",
            target_word_range=(2, 10),
            target_bubble_count=1,
            slang_intensity=0.7,
            emoji_policy="OPTIONAL",
            warmth=0.5,
            teasing_intensity=0.3
        )
        res = self.laya.verify_candidate_compliance("hey wyd?", plan)
        self.assertTrue(res["compliant"])


class TestSignalCognitiveGameSuite(unittest.TestCase):
    def setUp(self):
        self.game = SignalGameEngine()

    def test_memory_mode_sequence_generation(self):
        round_1 = self.game.generate_round(level=1, mode="memory")
        self.assertEqual(round_1["mode"], "memory")
        self.assertIn("sequence", round_1)
        self.assertEqual(len(round_1["sequence"]), 3)

    def test_focus_mode_go_no_go(self):
        round_focus = self.game.generate_round(level=3, mode="focus")
        self.assertEqual(round_focus["mode"], "focus")
        self.assertIn("target_rule", round_focus)
        self.assertIn("stream", round_focus)

    def test_switch_mode_dynamic_rules(self):
        round_switch = self.game.generate_round(level=4, mode="switch")
        self.assertEqual(round_switch["mode"], "switch")
        self.assertIn("active_rule", round_switch)

    def test_adaptive_difficulty_progression(self):
        # High accuracy + fast reaction -> level up
        sub_fast = self.game.evaluate_submission(
            level=3,
            user_inputs=["circle", "triangle", "square"],
            expected=["circle", "triangle", "square"],
            elapsed_ms=1200,
            combo=4
        )
        self.assertTrue(sub_fast["correct"])
        self.assertGreater(sub_fast["next_level"], 3)
        self.assertIn(sub_fast["adaptive_action"], ("increase", "maintain"))

        # Low accuracy -> reduce/maintain
        sub_err = self.game.evaluate_submission(
            level=3,
            user_inputs=["circle", "wrong", "wrong"],
            expected=["circle", "triangle", "square"],
            elapsed_ms=4500,
            combo=0
        )
        self.assertFalse(sub_err["correct"])
        self.assertLessEqual(sub_err["next_level"], 3)

    def test_daily_challenge_date_determinism(self):
        daily_today_1 = self.game.get_daily_challenge(date(2026, 9, 28))
        daily_today_2 = self.game.get_daily_challenge(date(2026, 9, 28))
        daily_tomorrow = self.game.get_daily_challenge(date(2026, 9, 29))
        self.assertEqual(daily_today_1["seed_id"], daily_today_2["seed_id"])
        self.assertEqual(daily_today_1["rounds_preview"], daily_today_2["rounds_preview"])
        self.assertNotEqual(daily_today_1["seed_id"], daily_tomorrow["seed_id"])


class TestDailyFocusTasksSuite(unittest.TestCase):
    def setUp(self):
        self.task_mgr = TaskManager("test_tasks_temp.db")

    def test_task_creation_with_mandatory_one_liner(self):
        task = self.task_mgr.add_task(
            title="Complete Physics Chapter 4 Problem Set",
            one_liner="Open textbook page 112, solve questions 1-5 on paper without looking at solutions.",
            category="study",
            priority="high",
            est_minutes=30
        )
        self.assertIn("id", task)
        self.assertEqual(task["title"], "Complete Physics Chapter 4 Problem Set")
        self.assertEqual(task["one_liner"], "Open textbook page 112, solve questions 1-5 on paper without looking at solutions.")

    def test_task_toggle_and_stats(self):
        task = self.task_mgr.add_task(
            title="Review Biology Notes",
            one_liner="Read 3 index cards on cell mitosis.",
            priority="medium",
            est_minutes=10
        )
        t_id = task["id"]
        res = self.task_mgr.toggle_task(t_id)
        self.assertTrue(res["completed"])

        overview = self.task_mgr.get_tasks_for_date()
        self.assertGreaterEqual(overview["summary"]["completed"], 1)

    def test_task_deletion(self):
        task = self.task_mgr.add_task(
            title="Temporary Scratch Task",
            one_liner="Do something quick."
        )
        t_id = task["id"]
        deleted = self.task_mgr.delete_task(t_id)
        self.assertTrue(deleted)


class TestClassicalHanafiTafsirHadithSuite(unittest.TestCase):
    def setUp(self):
        self.engine = TafsirHadithEngine()

    def test_daily_ayah_scholar_depth(self):
        bundle = self.engine.get_daily_bundle(day_offset=0)
        ayah = bundle["daily_ayah"]
        self.assertIn("arabic", ayah)
        self.assertIn("translation", ayah)
        self.assertIn("hanafi_tafsir", ayah)
        self.assertIn("contemporary_relevance", ayah)
        self.assertIn("actionable_steps", ayah)
        self.assertGreater(len(ayah["actionable_steps"]), 0)

    def test_daily_hadith_scholar_commentary(self):
        bundle = self.engine.get_daily_bundle(day_offset=0)
        hadith = bundle["daily_hadith"]
        self.assertIn("arabic", hadith)
        self.assertIn("translation", hadith)
        self.assertIn("scholar_commentary", hadith)
        self.assertIn("why_it_matters_today", hadith)
        self.assertIn("practical_implementation", hadith)
        self.assertGreater(len(hadith["practical_implementation"]), 0)


if __name__ == "__main__":
    unittest.main()
