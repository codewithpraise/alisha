"""
Comprehensive Unit & Integration Test Suite for LifeOS Engines.
Validates:
1. Astronomical Fiqh & Salah Calculations (Hanafi vs Shafi'i Asr, Solar Boundaries, Awqat Makruha)
2. Dhikr Progression & Adaptive Targets
3. Canonical Quran Integrity & Surah Catalog
4. Evidence-Grounded Authentic Duas Database
5. Muhasabah Mercy-Oriented Recovery Flow & Akhlaq Tracking
6. Personal Growth Adaptive Energy Levels
7. SIGNAL Cognitive Game & Asynchronous Alisha Challenge
8. Islamic Content Router & Strict Knowledge Isolation
9. Adaptive Notification Scheduler & Throttling Engine
"""

import unittest
import os
import sys
import tempfile
import sqlite3

current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current_dir, ".."))
if root not in sys.path:
    sys.path.insert(0, root)

from packages.lifeos import (
    SalahCalculator,
    DhikrEngine,
    QuranEngine,
    DuasDatabase,
    MuhasabahEngine,
    PersonalGrowthEngine,
    SignalGameEngine,
    IslamicContentRouter,
    AdaptiveNotificationScheduler,
)


class TestSalahCalculator(unittest.TestCase):
    def setUp(self):
        # Test coordinates: Karachi (24.8607, 67.0011, TZ=5.0)
        self.calc_hanafi = SalahCalculator(lat=24.8607, lng=67.0011, timezone_offset=5.0, madhhab="hanafi", method="karachi")
        self.calc_shafii = SalahCalculator(lat=24.8607, lng=67.0011, timezone_offset=5.0, madhhab="shafii", method="karachi")

    def test_prayer_schedule_keys(self):
        times = self.calc_hanafi.calculate_prayer_times()
        expected_keys = ["fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha", "midnight", "last_third"]
        for k in expected_keys:
            self.assertIn(k, times)
            self.assertRegex(times[k], r"^\d{2}:\d{2}$")

    def test_hanafi_vs_shafii_asr(self):
        times_h = self.calc_hanafi.calculate_prayer_times()
        times_s = self.calc_shafii.calculate_prayer_times()
        # Hanafi Asr (2x shadow) must be later than Shafi'i Asr (1x shadow)
        h_hour, h_min = map(int, times_h["asr"].split(":"))
        s_hour, s_min = map(int, times_s["asr"].split(":"))
        self.assertGreaterEqual(h_hour * 60 + h_min, s_hour * 60 + s_min)

    def test_prohibited_solar_windows(self):
        status = self.calc_hanafi.get_current_status()
        self.assertIn("prohibited_windows", status)
        pw = status["prohibited_windows"]
        self.assertIn("sunrise_prohibited", pw)
        self.assertIn("zenith_prohibited", pw)
        self.assertIn("sunset_prohibited", pw)

    def test_current_status_structure(self):
        status = self.calc_hanafi.get_current_status()
        self.assertIn("current_prayer", status)
        self.assertIn("state", status)
        self.assertIn("remaining_formatted", status)
        self.assertIn("next_prayer", status)
        self.assertIn("schedule", status)


class TestDhikrEngine(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.engine = DhikrEngine(db_path=self.temp_db.name)

    def tearDown(self):
        try:
            if os.path.exists(self.temp_db.name):
                os.remove(self.temp_db.name)
        except Exception:
            pass

    def test_get_daily_list(self):
        adhkar = self.engine.get_daily_adhkar()
        self.assertGreaterEqual(len(adhkar), 4)
        ids = [a["id"] for a in adhkar]
        self.assertIn("subhanallah", ids)
        self.assertIn("istighfar", ids)

    def test_increment_and_adaptive_goal(self):
        initial = self.engine.get_daily_adhkar()[0]
        initial_count = initial["count"]
        res = self.engine.increment_count(initial["id"], delta=5)
        self.assertEqual(res["new_count"], initial_count + 5)

        adaptive = self.engine.get_adaptive_recommendation(initial["id"])
        self.assertIn("recommended_target", adaptive)
        self.assertIn("consistency_score", adaptive)


class TestQuranEngine(unittest.TestCase):
    def setUp(self):
        self.engine = QuranEngine()

    def test_catalog_structure(self):
        catalog = self.engine.get_catalog()
        self.assertGreater(len(catalog), 0)
        surah_1 = next(s for s in catalog if s["number"] == 1)
        self.assertEqual(surah_1["name_en"], "Al-Fatihah")
        self.assertEqual(surah_1["verses"], 7)

    def test_surah_al_waqiah_retrieval(self):
        data = self.engine.get_surah(56)
        self.assertEqual(data["surah"]["number"], 56)
        self.assertGreater(len(data["verses"]), 0)
        # Verify first verse Arabic text preservation
        first_verse = data["verses"][0]
        self.assertIn("الْوَاقِعَةُ", first_verse["ar"])

    def test_special_virtues_and_firdaus_path(self):
        virtues = self.engine.get_special_virtues()
        self.assertIn("waqiah_wealth", virtues)
        # Verify classification distinction for Waqi'ah
        self.assertIn("Da'if", virtues["waqiah_wealth"]["classification"])

        firdaus = self.engine.get_firdaus_path()
        self.assertEqual(len(firdaus), 6)


class TestDuasDatabase(unittest.TestCase):
    def setUp(self):
        self.db = DuasDatabase()

    def test_get_all_and_filter(self):
        all_duas = self.db.get_all()
        self.assertGreater(len(all_duas), 0)

        knowledge_duas = self.db.get_all(category="knowledge")
        self.assertTrue(all(d["category"] == "knowledge" for d in knowledge_duas))

    def test_search_duas(self):
        results = self.db.search("knowledge")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["id"], "dua_knowledge")

    def test_authenticity_field_presence(self):
        all_duas = self.db.get_all()
        for d in all_duas:
            self.assertIn("authenticity_grade", d)
            self.assertIn("source_reference", d)


class TestMuhasabahEngine(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.engine = MuhasabahEngine(db_path=self.temp_db.name)

    def tearDown(self):
        try:
            if os.path.exists(self.temp_db.name):
                os.remove(self.temp_db.name)
        except Exception:
            pass

    def test_record_lapse_mercy_response(self):
        res = self.engine.record_lapse(
            category="distraction",
            trigger="Late night mindless scrolling",
            repair="Put phone away, made wudu, recited Surah Al-Mulk",
            notes="Felt tired after work"
        )
        self.assertTrue(res["success"])
        self.assertIn("mercy_reminder", res)

    def test_record_and_get_akhlaq(self):
        res = self.engine.record_akhlaq_reflection(
            trait_id="anger_control",
            behavior="Held silence during a heated meeting rather than reacting"
        )
        self.assertTrue(res["success"])

        entries = self.engine.get_recent_entries()
        self.assertIn("akhlaq", entries)
        self.assertGreaterEqual(len(entries["akhlaq"]), 1)


class TestPersonalGrowthEngine(unittest.TestCase):
    def setUp(self):
        self.engine = PersonalGrowthEngine()

    def test_generate_daily_plans(self):
        for mode in ["low", "normal", "high"]:
            plan = self.engine.generate_daily_plan(energy_level=mode)
            self.assertEqual(plan["energy_level"], mode)
            self.assertIn("quote", plan)
            self.assertIn("focus", plan)
            self.assertIn("worship", plan)

    def test_weekly_review(self):
        review = self.engine.generate_weekly_review()
        self.assertIn("framework", review)
        self.assertIn("questions", review)


class TestSignalGameEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SignalGameEngine()

    def test_generate_round(self):
        r1 = self.engine.generate_round(level=1)
        self.assertEqual(r1["level"], 1)
        self.assertGreaterEqual(len(r1["sequence"]), 3)
        self.assertFalse(r1["has_distractor"])

        r5 = self.engine.generate_round(level=5)
        self.assertEqual(r5["level"], 5)
        self.assertTrue(r5["has_distractor"])

    def test_evaluate_submission(self):
        seq = ["amber_pulse", "emerald_flash", "sapphire_glow"]
        res = self.engine.evaluate_submission(
            level=2,
            user_inputs=seq,
            expected_seq=seq,
            elapsed_ms=3000,
            combo=2
        )
        self.assertTrue(res["correct"])
        self.assertGreater(res["score_earned"], 0)

    def test_simulate_alisha_challenge(self):
        sim = self.engine.simulate_alisha_challenge(player_score=850)
        self.assertIn("alisha_score", sim)
        self.assertIn("outcome", sim)
        self.assertIn("chat_response", sim)



class TestIslamicContentRouter(unittest.TestCase):
    def setUp(self):
        self.router = IslamicContentRouter()

    def test_classification_of_religious_queries(self):
        self.assertTrue(self.router.is_religious_query("what time is asr prayer today?"))
        self.assertTrue(self.router.is_religious_query("can you show me surah al waqiah"))
        self.assertTrue(self.router.is_religious_query("is music halal or haram"))
        self.assertTrue(self.router.is_religious_query("what is the dua for anxiety"))

    def test_classification_of_casual_queries(self):
        self.assertFalse(self.router.is_religious_query("hey alisha what are you doing today?"))
        self.assertFalse(self.router.is_religious_query("tell me a story about when we visited the cafe"))
        self.assertFalse(self.router.is_religious_query("play some lofi music for me"))

    def test_route_fiqh_question(self):
        routed = self.router.route_query("is eating during fast valid by mistake?")
        self.assertEqual(routed["type"], "fiqh_boundary")
        self.assertIn("LifeOS", routed["message"])


class TestAdaptiveNotificationScheduler(unittest.TestCase):
    def setUp(self):
        self.scheduler = AdaptiveNotificationScheduler()

    def test_compute_schedule_with_salah_times(self):
        salah_schedule = {
            "fajr": "05:12",
            "sunrise": "06:28",
            "dhuhr": "12:24",
            "asr": "16:42",
            "maghrib": "18:19",
            "isha": "19:35",
            "midnight": "23:45"
        }
        schedule = self.scheduler.compute_daily_schedule(salah_schedule=salah_schedule, fatigue_score=0.1)
        self.assertGreaterEqual(len(schedule), 2)
        categories = [n.category for n in schedule]
        self.assertIn("salah", categories)

    def test_fatigue_dampening(self):
        history_fatigued = [{"status": "ignored"}] * 8 + [{"status": "opened"}] * 2
        fatigue = self.scheduler.evaluate_fatigue(history_fatigued)
        self.assertGreaterEqual(fatigue, 0.7)

        salah_schedule = {
            "fajr": "05:12",
            "sunrise": "06:28",
            "dhuhr": "12:24",
            "asr": "16:42",
            "maghrib": "18:19",
            "isha": "19:35",
            "midnight": "23:45"
        }
        # With high fatigue, optional items like game challenges are dropped
        schedule = self.scheduler.compute_daily_schedule(salah_schedule=salah_schedule, fatigue_score=fatigue)
        categories = [n.category for n in schedule]
        self.assertNotIn("game", categories)


if __name__ == "__main__":
    unittest.main(verbosity=2)
