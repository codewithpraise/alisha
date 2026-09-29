"""
Unit tests for ContextPacker and DeterministicPolicy.
"""

import unittest
from packages.policy.deterministic_policy import DeterministicPolicy
from packages.inference.context_packer import ContextPacker


class TestContextPackerAndPolicy(unittest.TestCase):
    def setUp(self):
        self.policy = DeterministicPolicy()
        self.packer = ContextPacker()

    def test_policy_routing_greetings(self):
        dec = self.policy.evaluate("heyy", is_voice_input=False)
        self.assertEqual(dec.retrieval_depth, 0, "Greetings must skip retrieval")
        self.assertEqual(dec.style_mode, "neutral")
        self.assertFalse(dec.is_voice_requested)

    def test_policy_routing_teasing(self):
        dec = self.policy.evaluate("you said latw again lmao", is_voice_input=False)
        self.assertEqual(dec.style_mode, "teasing")
        self.assertTrue(dec.permit_second_burst)
        self.assertLessEqual(dec.max_response_tokens, 50)

    def test_policy_routing_deen(self):
        dec = self.policy.evaluate("are you praying salah on time?", is_voice_input=False)
        self.assertEqual(dec.style_mode, "serious")
        self.assertGreater(dec.retrieval_depth, 0)

    def test_policy_burst_hard_limit(self):
        burst2 = self.policy.evaluate_second_burst("not latw again 💀", "teasing")
        self.assertEqual(burst2, "stop making fun of my typos 😭")

        # Extremely short reaction should not trigger a second burst
        short_burst = self.policy.evaluate_second_burst("💀", "teasing")
        self.assertIsNone(short_burst)

        # Neutral should never burst
        neutral_burst = self.policy.evaluate_second_burst("yeah i think so", "neutral")
        self.assertIsNone(neutral_burst)

    def test_context_packer_structure(self):
        recent_msgs = [
            {"sender": "user", "text": "hey what are you doing"},
            {"sender": "alisha", "text": "nothing much just at home"},
        ]
        facts = [
            {"subject": "Alisha", "predicate": "discusses_faith", "object": "praying salah daily"}
        ]
        episode = {"summary": "Talked about exams and revision"}
        exemplars = [
            {"text": "bro that is actually hilarious 😭"},
            {"text": "innit 💀"},
        ]

        packed = self.packer.pack(
            recent_messages=recent_msgs,
            relevant_facts=facts,
            episode_memory=episode,
            style_exemplars=exemplars,
            current_user_input="did you pray yet?",
            max_context_budget_tokens=1024,
        )

        p = packed.prompt
        # Verify structure
        self.assertIn("<|im_start|>system", p)
        self.assertIn("Relevant Context:\n- Alisha discusses_faith: praying salah daily", p)
        self.assertIn("Past Shared Event:\n- Talked about exams and revision", p)
        self.assertIn('Authentic Style Exemplars:\n- "bro that is actually hilarious 😭"', p)
        self.assertIn("<|im_start|>Friend\ndid you pray yet?<|im_end|>", p)
        self.assertIn("<|im_start|>Alisha\n", p)
        self.assertEqual(packed.injected_fact_count, 1)
        self.assertEqual(packed.injected_exemplar_count, 2)
        self.assertTrue(packed.has_episode)

    def test_context_packer_budget_truncation(self):
        # Create huge history
        long_msgs = [{"sender": "user", "text": f"message number {i} " * 20} for i in range(50)]
        packed = self.packer.pack(
            recent_messages=long_msgs,
            relevant_facts=[],
            episode_memory=None,
            style_exemplars=[],
            current_user_input="test",
            max_context_budget_tokens=250,
        )
        self.assertLessEqual(packed.prompt_tokens_estimate, 300)


if __name__ == "__main__":
    unittest.main()
