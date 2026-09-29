"""
Unit tests for LlmEngine, streaming, cancellation, deterministic mode, and metrics.
"""

import unittest
from packages.inference.llm_engine import (
    DeterministicTestLlmEngine,
    LocalSimulatedLlmEngine,
    GenerationRequest,
)


class TestLlmEngineAndStreaming(unittest.TestCase):
    def test_streaming_callback(self):
        engine = DeterministicTestLlmEngine(canned_response="bro that is hilarious 💀")
        collected_tokens = []

        req = GenerationRequest(prompt="User: look at this meme\nAlisha:")
        res = engine.generate(req, on_token=lambda t: collected_tokens.append(t))

        self.assertFalse(res.is_cancelled)
        self.assertEqual(res.text, "bro that is hilarious 💀")
        self.assertEqual("".join(collected_tokens), "bro that is hilarious 💀")
        self.assertGreater(res.generated_tokens, 0)
        self.assertGreaterEqual(res.time_to_first_token_ms, 0.0)
        self.assertGreater(res.tokens_per_sec, 0.0)

    def test_cancellation_mid_stream(self):
        engine = DeterministicTestLlmEngine(canned_response="one two three four five six seven eight")
        collected = []

        def cancel_after_two(token: str):
            collected.append(token)
            if len(collected) >= 2:
                engine.cancel()

        req = GenerationRequest(prompt="User: hi\nAlisha:")
        res = engine.generate(req, on_token=cancel_after_two)

        self.assertTrue(res.is_cancelled)
        self.assertLess(res.generated_tokens, 8)

    def test_deterministic_mode_vs_sampling(self):
        engine = LocalSimulatedLlmEngine()

        req_det = GenerationRequest(prompt="User: hi\nAlisha:", deterministic_test_mode=True)
        res1 = engine.generate(req_det)
        res2 = engine.generate(req_det)

        self.assertEqual(res1.text, res2.text, "Deterministic mode must produce identical output")
        self.assertEqual(res1.text, "innit\ni was literally so busy with mum 😭")

    def test_regeneration(self):
        engine = LocalSimulatedLlmEngine()
        req = GenerationRequest(prompt="User: are you busy?\nAlisha:")

        # Generate original
        res_orig = engine.generate(req)
        # Regenerate with same prompt
        res_regen = engine.generate(req)

        self.assertIsNotNone(res_orig.text)
        self.assertIsNotNone(res_regen.text)
        self.assertFalse(res_orig.is_cancelled)
        self.assertFalse(res_regen.is_cancelled)


if __name__ == "__main__":
    unittest.main()
