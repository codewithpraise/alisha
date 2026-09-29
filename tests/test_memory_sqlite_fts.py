"""
Unit tests for SQLite persistence, FTS5 retrieval, temporal updates, and provenance.
"""

import os
import shutil
import tempfile
import time
import unittest

from packages.memory.database import MemoryDatabase


class TestMemoryDatabase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_memory.db")
        self.db = MemoryDatabase(self.db_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_message_persistence_and_fts(self):
        self.db.insert_message(
            msg_id="m1",
            conversation_id="c1",
            timestamp=1000,
            sender="user",
            text="remember to pray salah on time",
            source_index=0,
        )
        self.db.insert_message(
            msg_id="m2",
            conversation_id="c1",
            timestamp=2000,
            sender="alisha",
            text="yeah honestly salah brings so much peace",
            source_index=1,
        )

        messages = self.db.get_recent_messages(limit=5)
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["id"], "m1")
        self.assertEqual(messages[1]["id"], "m2")

    def test_facts_provenance_and_fts(self):
        self.db.insert_fact(
            fact_id="f1",
            subject="Alisha",
            predicate="prays",
            obj="salah daily",
            confidence=0.99,
            importance=0.85,
            source_message_id="msg_42",
        )

        facts = self.db.get_active_facts()
        self.assertEqual(len(facts), 1)
        self.assertEqual(facts[0]["source_message_id"], "msg_42")
        self.assertEqual(facts[0]["predicate"], "prays")

        # Test FTS5 query
        fts_res = self.db.search_facts_fts("salah")
        self.assertGreaterEqual(len(fts_res), 1)
        self.assertEqual(fts_res[0]["id"], "f1")

    def test_temporal_updates_and_stale_memory_suppression(self):
        t1 = 100000
        t2 = 200000

        # Step 1: Alisha likes matcha at t1
        self.db.insert_fact(
            fact_id="f_tea_old",
            subject="Alisha",
            predicate="prefers_drink",
            obj="matcha latte",
            confidence=0.9,
            importance=0.7,
            first_seen=t1,
            last_confirmed=t1,
            valid_from=t1,
            source_message_id="msg_10",
        )

        # Active at t1 + 500
        active_early = self.db.get_active_facts(at_timestamp=t1 + 500)
        self.assertEqual(len(active_early), 1)
        self.assertEqual(active_early[0]["object"], "matcha latte")

        # Step 2: Alisha changes preference to iced karak chai at t2
        updated = self.db.update_fact_temporally(
            old_fact_id="f_tea_old",
            new_fact_id="f_tea_new",
            new_obj="iced karak chai",
            effective_timestamp=t2,
            confidence=0.95,
            importance=0.8,
            source_message_id="msg_50",
        )
        self.assertTrue(updated)

        # Step 3: Query active facts at t2 + 1000 -> Stale memory must be suppressed!
        active_now = self.db.get_active_facts(at_timestamp=t2 + 1000)
        self.assertEqual(len(active_now), 1)
        self.assertEqual(active_now[0]["id"], "f_tea_new")
        self.assertEqual(active_now[0]["object"], "iced karak chai")
        self.assertEqual(active_now[0]["source_message_id"], "msg_50")

        # Step 4: Verify historical chain is NOT destroyed
        history = self.db.get_fact_history("Alisha", "prefers_drink")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["object"], "matcha latte")
        self.assertEqual(history[0]["valid_until"], t2)  # Historical expiration recorded
        self.assertEqual(history[1]["object"], "iced karak chai")
        self.assertIsNone(history[1]["valid_until"])      # Currently active

    def test_episodes_and_style_examples(self):
        self.db.insert_episode(
            episode_id="ep1",
            start_timestamp=1000,
            end_timestamp=5000,
            summary="Late night conversation about university deadlines and exams",
            importance=0.7,
            source_start_message_id="m100",
            source_end_message_id="m140",
        )
        episodes = self.db.get_episodes(limit=2)
        self.assertEqual(len(episodes), 1)
        self.assertEqual(episodes[0]["source_start_message_id"], "m100")

        self.db.insert_style_example(
            example_id="s1",
            mode="teasing",
            text="not latw again 💀 stop making fun of my typos",
            source_message_id="m205",
            importance=0.9,
        )
        examples = self.db.get_style_examples(mode="teasing")
        self.assertEqual(len(examples), 1)
        self.assertEqual(examples[0]["mode"], "teasing")


if __name__ == "__main__":
    unittest.main()
