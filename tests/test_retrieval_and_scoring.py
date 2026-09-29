"""
Unit tests for character n-gram similarity, score fusion, duplicate suppression,
weak relevance suppression, and style exemplar retrieval.
"""

import os
import unittest

from packages.memory.database import MemoryDatabase
from packages.memory.retriever import (
    MemoryRetriever,
    ScoreWeights,
    deterministic_text_vector,
    cosine_similarity,
    jaccard_word_similarity,
)

current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current_dir, ".."))
DB_PATH = os.path.join(root, "data", "memory.db")


class TestRetrievalAndScoring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = MemoryDatabase(DB_PATH)
        cls.retriever = MemoryRetriever(cls.db)

    def test_character_ngram_vector_determinism(self):
        t1 = "remember to pray salah"
        t2 = "remember to pray salah"
        t3 = "completely different weather today"

        v1 = deterministic_text_vector(t1)
        v2 = deterministic_text_vector(t2)
        v3 = deterministic_text_vector(t3)

        self.assertEqual(len(v1), 128)
        self.assertEqual(v1, v2, "Identical text must generate identical vector")

        sim_same = cosine_similarity(v1, v2)
        sim_diff = cosine_similarity(v1, v3)

        self.assertAlmostEqual(sim_same, 1.0, places=4)
        self.assertLess(sim_diff, 0.40)

    def test_score_fusion_and_depth(self):
        # Query matching faith / salah fact
        memories = self.retriever.search_memories("salah and prayer times", depth=5)
        self.assertGreaterEqual(len(memories), 1)
        self.assertLessEqual(len(memories), 5)

        top = memories[0]
        self.assertIn("salah", top["object"].lower())
        self.assertGreater(top["final_score"], 0.35)
        self.assertIn("source_message_id", top)
        self.assertIsNotNone(top["source_message_id"])

    def test_weak_relevance_suppression(self):
        # Query with random unrelated tokens should yield empty result (Never inject memory merely because it exists)
        memories = self.retriever.search_memories("quantum teleportation astrophysics", depth=5)
        self.assertEqual(len(memories), 0, "Weak relevance queries must retrieve nothing")

    def test_duplicate_suppression(self):
        # Search with duplicate-rich query
        w = ScoreWeights(duplication_penalty_weight=0.50, min_score_threshold=0.20)
        memories = self.retriever.search_memories("salah prayer dawah sins", depth=8, weights=w)

        # Check that no two returned memories are near-duplicates
        for i in range(len(memories)):
            for j in range(i + 1, len(memories)):
                t1 = f"{memories[i]['subject']} {memories[i]['predicate']} {memories[i]['object']}"
                t2 = f"{memories[j]['subject']} {memories[j]['predicate']} {memories[j]['object']}"
                jac = jaccard_word_similarity(t1, t2)
                self.assertLess(jac, 0.80, f"Memories {i} and {j} should not be near-duplicates")

    def test_style_exemplars_retrieval(self):
        teasing_ex = self.retriever.get_style_exemplars("teasing", limit=3)
        self.assertGreaterEqual(len(teasing_ex), 1)
        for ex in teasing_ex:
            self.assertEqual(ex["mode"], "teasing")
            self.assertIsNotNone(ex["text"])
            self.assertIsNotNone(ex["source_message_id"])

        serious_ex = self.retriever.get_style_exemplars("serious", limit=2)
        self.assertGreaterEqual(len(serious_ex), 1)
        self.assertEqual(serious_ex[0]["mode"], "serious")


if __name__ == "__main__":
    unittest.main()
