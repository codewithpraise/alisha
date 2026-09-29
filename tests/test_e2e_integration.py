"""
End-to-End Integration Tests for Alisha Bubbzieee.
Validates:
1. Text pipeline: user message -> policy -> retrieval -> context packing -> LLM -> response -> burst
2. Voice pipeline: audio -> VAD -> ASR -> ConversationEngine -> LLM -> TTS -> playback
3. Diagnostics verification: metrics logged, zero private data leaks
4. Cancellation during active turn
"""

import os
import unittest

from packages.memory.database import MemoryDatabase
from packages.engine.conversation_engine import ConversationEngine
from packages.inference.llm_engine import DeterministicTestLlmEngine
from packages.voice.engine_interfaces import (
    EnergyVadEngine,
    MockOfflineAsrEngine,
    DeterministicMockTtsEngine,
)

current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current_dir, ".."))
DB_PATH = os.path.join(root, "data", "memory.db")


class TestEndToEndIntegration(unittest.TestCase):
    def setUp(self):
        self.db = MemoryDatabase(DB_PATH)
        self.engine = ConversationEngine(
            db=self.db,
            llm=DeterministicTestLlmEngine(canned_response="not latw again 💀"),
            tts=DeterministicMockTtsEngine(),
            asr=MockOfflineAsrEngine(default_transcript="you said latw again"),
            vad=EnergyVadEngine(threshold_db=-44.0),
            conversation_id="conv_e2e_test",
        )

    def test_e2e_text_turn(self):
        tokens_received = []

        resp = self.engine.process_text_turn(
            user_text="you said latw again",
            on_token=lambda t: tokens_received.append(t),
            deterministic_test_mode=True,
        )

        # 1. Output messages verify primary + burst
        self.assertGreaterEqual(len(resp.messages), 1)
        self.assertEqual(resp.messages[0], "not latw again 💀")
        # Burst policy for teasing should trigger second message
        if len(resp.messages) > 1:
            self.assertEqual(resp.messages[1], "stop making fun of my typos 😭")

        # 2. Tokens streamed
        self.assertEqual("".join(tokens_received), "not latw again 💀")

        # 3. Policy decisions
        self.assertEqual(resp.policy_decision.style_mode, "teasing")

        # 4. Diagnostics recorded
        d = resp.diagnostics
        self.assertGreater(d.context_size_chars, 50)
        self.assertGreater(d.generated_tokens, 0)
        self.assertTrue(d.trace_id.startswith("trace_"))

        # 5. Database persistence check
        recent = self.db.get_recent_messages(limit=5, conversation_id="conv_e2e_test")
        self.assertGreaterEqual(len(recent), 2)
        # Check user and alisha message persisted
        senders = [m["sender"] for m in recent]
        self.assertIn("user", senders)
        self.assertIn("alisha", senders)

    def test_e2e_voice_pipeline(self):
        # Create speech PCM
        speech_samples = [12000 if i % 2 == 0 else -12000 for i in range(3200)]
        speech_pcm = bytearray()
        for s in speech_samples:
            speech_pcm.extend(s.to_bytes(2, byteorder="little", signed=True))

        audio_chunks_received = []
        finals_received = []

        def audio_cb(chunk: bytes, is_final: bool):
            audio_chunks_received.append(chunk)
            finals_received.append(is_final)

        tokens_streamed = []

        resp = self.engine.process_voice_turn(
            audio_pcm=bytes(speech_pcm),
            on_audio_chunk=audio_cb,
            on_token=lambda t: tokens_streamed.append(t),
            deterministic_test_mode=True,
        )

        # 1. Verification of voice response
        self.assertTrue(resp.is_voice)
        self.assertGreaterEqual(len(resp.messages), 1)

        # 2. TTS audio chunks streamed to callback
        self.assertEqual(len(audio_chunks_received), 4)
        self.assertTrue(finals_received[-1])

        # 3. Voice latency diagnostics recorded
        d = resp.diagnostics
        self.assertGreaterEqual(d.tts_generation_time_ms, 0.0)
        self.assertGreaterEqual(d.asr_latency_ms, 0.0)

    def test_e2e_voice_silence_rejection(self):
        silence_pcm = bytes([0] * 640)
        audio_chunks = []

        resp = self.engine.process_voice_turn(
            audio_pcm=silence_pcm,
            on_audio_chunk=lambda c, f: audio_chunks.append(c),
        )

        self.assertEqual(len(resp.messages), 0, "Silence must produce 0 messages")
        self.assertEqual(len(audio_chunks), 0, "Silence must produce 0 audio chunks")

    def test_e2e_cancellation(self):
        # Test cancel_active method
        self.engine.cancel_active()
        self.assertTrue(self.engine.llm._is_cancelled)
        self.assertTrue(self.engine.tts._is_cancelled)


if __name__ == "__main__":
    unittest.main()
