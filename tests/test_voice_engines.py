"""
Unit tests for replaceable local voice engines: VAD, ASR, TTS.
"""

import os
import unittest
from packages.voice.engine_interfaces import (
    EnergyVadEngine,
    MockOfflineAsrEngine,
    DeterministicMockTtsEngine,
    LocalWavTtsEngine,
)

current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current_dir, ".."))
VOICE_DIR = os.path.join(root, "voice")


class TestVoiceEngines(unittest.TestCase):
    def test_vad_silence_vs_speech(self):
        vad = EnergyVadEngine(threshold_db=-44.0)

        # 1. Total silence (0s)
        silence_pcm = bytes([0] * 640)
        self.assertFalse(vad.process_pcm(silence_pcm))

        # 2. Simulated loud speech (amplitude ~10000)
        speech_samples = [10000 if i % 2 == 0 else -10000 for i in range(320)]
        speech_pcm = bytearray()
        for s in speech_samples:
            speech_pcm.extend(s.to_bytes(2, byteorder="little", signed=True))

        self.assertTrue(vad.process_pcm(bytes(speech_pcm)))

    def test_asr_transcription(self):
        asr = MockOfflineAsrEngine(default_transcript="did you pray salah yet?")
        dummy_pcm = bytes([120] * 16000)
        text = asr.transcribe(dummy_pcm)
        self.assertEqual(text, "did you pray salah yet?")

    def test_tts_streaming_callback(self):
        tts = DeterministicMockTtsEngine()
        chunks_received = []
        finals = []

        def on_chunk(chunk: bytes, is_final: bool):
            chunks_received.append(chunk)
            finals.append(is_final)

        tts.synthesize("not latw again 💀", callback=on_chunk)

        self.assertEqual(len(chunks_received), 4)
        self.assertFalse(finals[0])
        self.assertTrue(finals[-1])

    def test_tts_cancellation(self):
        tts = DeterministicMockTtsEngine()
        chunks_received = []

        def on_chunk(chunk: bytes, is_final: bool):
            chunks_received.append(chunk)
            if len(chunks_received) >= 2:
                tts.cancel()

        tts.synthesize("some long message", callback=on_chunk)
        self.assertLess(len(chunks_received), 4)

    def test_local_wav_tts(self):
        tts = LocalWavTtsEngine(voice_dir=VOICE_DIR)
        chunks = []

        def on_chunk(chunk: bytes, is_final: bool):
            chunks.append(chunk)

        tts.synthesize("test", callback=on_chunk)
        self.assertGreaterEqual(len(chunks), 1)


if __name__ == "__main__":
    unittest.main()
