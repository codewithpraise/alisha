"""
End-to-End Test Suite for Alisha Bubbzieee.
Validates all 8 build phases systematically.
"""

import json
import os
import sys
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current_dir, ".."))
if root not in sys.path:
    sys.path.insert(0, root)

from packages.pipeline.quality_analyzer import compute_audio_metrics
from packages.personality.fingerprint import analyze_messages
from packages.memory.retriever import MemoryRetriever
from packages.inference.context_builder import ContextBuilder
from packages.inference.llm_client import LLMClient
from packages.personality.message_compositor import MessageCompositor
from packages.voice.prosody_controller import get_prosody_for_text
from packages.voice.paralinguistic_lib import get_token_metadata
from packages.voice.stream_pipeline import VoiceCallPipeline, CallState
from packages.proactive.initiation_model import evaluate_initiation
from packages.proactive.quality_gate import passes_quality_gate
from packages.evaluation.evaluator import AlishaEvaluator


class TestAlishaBubbzieeeAllPhases(unittest.TestCase):

    def test_phase_1_voice_refinery(self):
        """Phase 1: Voice dataset, manifests, quality analysis, references."""
        # 1. Check manifests exist
        train_manifest = os.path.join(root, "data", "voice_train.jsonl")
        val_manifest = os.path.join(root, "data", "voice_val.jsonl")
        quality_manifest = os.path.join(root, "data", "quality_manifest.jsonl")
        report_html = os.path.join(root, "data", "voice_report.html")

        self.assertTrue(os.path.exists(train_manifest), "voice_train.jsonl must exist")
        self.assertTrue(os.path.exists(val_manifest), "voice_val.jsonl must exist")
        self.assertTrue(os.path.exists(quality_manifest), "quality_manifest.jsonl must exist")
        self.assertTrue(os.path.exists(report_html), "voice_report.html must exist")

        # 2. Check reference clips
        neutral_ref = os.path.join(root, "data", "refs", "ref_neutral.wav")
        self.assertTrue(os.path.exists(neutral_ref), "ref_neutral.wav must exist")

        # 3. Test quality analyzer on sample
        sample_wav = os.path.join(root, "voice", "1303735758283391.wav")
        metrics = compute_audio_metrics(sample_wav)
        self.assertIn("quality_score", metrics)
        self.assertIn(metrics["classification"], ["A", "B", "C", "R"])
        self.assertGreater(metrics["duration_sec"], 0)

    def test_phase_2_friend_text_brain(self):
        """Phase 2: Behavioral fingerprint, memory database, retriever, compositor."""
        # 1. Check profile
        profile_path = os.path.join(root, "data", "friend_profile.json")
        self.assertTrue(os.path.exists(profile_path))
        with open(profile_path, "r", encoding="utf-8") as f:
            prof = json.load(f)
        self.assertIn("linguistic_metrics", prof)
        self.assertLess(prof["linguistic_metrics"]["capitalization_rate"], 0.10)

        # 2. Check database & retriever
        db_path = os.path.join(root, "data", "memory.db")
        self.assertTrue(os.path.exists(db_path))
        retriever = MemoryRetriever(db_path)
        mems = retriever.search_memories("salah prayer")
        self.assertGreater(len(mems), 0)

        # 3. Context builder & compositor
        builder = ContextBuilder(profile_path, db_path)
        prompt = builder.build_prompt("are you latw again?", [])
        self.assertIn("Alisha", prompt)
        self.assertIn("Strict Behavior Rules", prompt.title())

        compositor = MessageCompositor(prof)
        bursts = compositor.compose("Nahhh bro I was literally so busy with mum 😭\nStop making fun of me.")
        self.assertGreaterEqual(len(bursts), 1)
        # Check lowercase enforcement
        self.assertTrue(bursts[0]["content"][0].islower())

    def test_phase_3_training_artifacts(self):
        """Phase 3: Kaggle training notebook, dataset splits, GGUF converter."""
        train_chat = os.path.join(root, "data", "chat_train.jsonl")
        nb_path = os.path.join(root, "training", "kaggle_training.ipynb")
        gguf_script = os.path.join(root, "training", "convert_to_gguf.py")
        benchmark_doc = os.path.join(root, "training", "redmi_benchmark.md")

        self.assertTrue(os.path.exists(train_chat))
        self.assertTrue(os.path.exists(nb_path))
        self.assertTrue(os.path.exists(gguf_script))
        self.assertTrue(os.path.exists(benchmark_doc))

    def test_phase_4_voice_cloning_artifacts(self):
        """Phase 4: TTS benchmark, prosody controller, paralinguistics, Kaggle notebook."""
        prosody = get_prosody_for_text("bro that is hilarious 💀")
        self.assertEqual(prosody["emotion"], "amused")
        self.assertGreater(prosody["energy"], 0.7)

        token_meta = get_token_metadata("<chuckle>")
        self.assertIsNotNone(token_meta)

        tts_nb = os.path.join(root, "training", "kaggle_voice_training.ipynb")
        self.assertTrue(os.path.exists(tts_nb))

    def test_phase_5_voice_streaming_pipeline(self):
        """Phase 5: Real-time voice call pipeline state machine & interruption."""
        states_recorded = []
        pipeline = VoiceCallPipeline(on_state_change=lambda s: states_recorded.append(s))
        self.assertEqual(pipeline.state, CallState.IDLE)

        # User starts speaking
        pipeline.on_vad_speech_start()
        self.assertEqual(pipeline.state, CallState.LISTENING)

        # User finishes speaking
        pipeline.on_vad_speech_end("hello")
        self.assertEqual(pipeline.state, CallState.SPEAKING)

        # User interrupts Alisha
        pipeline.on_vad_speech_start()
        self.assertEqual(pipeline.state, CallState.LISTENING)

        # Check Android pipeline file exists
        android_audio_pkg = os.path.join(root, "apps", "android", "app", "src", "main", "java", "com", "friendos", "alishabubbzieee", "core", "voice", "AudioPipeline.kt")
        android_audio_root = os.path.join(root, "apps", "android", "AudioPipeline.kt")
        self.assertTrue(os.path.exists(android_audio_pkg) or os.path.exists(android_audio_root))

    def test_phase_6_proactive_engine(self):
        """Phase 6: Initiation model, quality gate, WorkManager."""
        profile_path = os.path.join(root, "data", "friend_profile.json")
        db_path = os.path.join(root, "data", "memory.db")

        # Test initiation evaluation at peak hour 13
        init_res = evaluate_initiation(profile_path, db_path, override_hour=13)
        self.assertIn("score", init_res)
        self.assertIn("should_initiate", init_res)

        # Test quality gate
        self.assertTrue(passes_quality_gate("bro look at this 💀"))
        self.assertFalse(passes_quality_gate("Hello there, as your AI assistant I am checking in on you."))

        # Check Android files
        worker_kt_pkg = os.path.join(root, "apps", "android", "app", "src", "main", "java", "com", "friendos", "alishabubbzieee", "core", "proactive", "ProactiveNotificationManager.kt")
        worker_kt_root = os.path.join(root, "apps", "android", "ProactiveWorker.kt")
        guide_md = os.path.join(root, "apps", "android", "MIUI_BATTERY_GUIDE.md")
        self.assertTrue(os.path.exists(worker_kt_pkg) or os.path.exists(worker_kt_root))
        self.assertTrue(os.path.exists(guide_md))

    def test_phase_7_pwa_web_app(self):
        """Phase 7: Next.js 15 App Router, Tailwind CSS, PWA Manifest, 5 Routes."""
        package_json = os.path.join(root, "apps", "web", "package.json")
        tailwind_config = os.path.join(root, "apps", "web", "tailwind.config.ts")
        layout_tsx = os.path.join(root, "apps", "web", "app", "layout.tsx")
        page_tsx = os.path.join(root, "apps", "web", "app", "page.tsx")
        chat_page = os.path.join(root, "apps", "web", "app", "chat", "page.tsx")
        call_page = os.path.join(root, "apps", "web", "app", "call", "page.tsx")
        memories_page = os.path.join(root, "apps", "web", "app", "memories", "page.tsx")
        settings_page = os.path.join(root, "apps", "web", "app", "settings", "page.tsx")
        manifest_json = os.path.join(root, "apps", "web", "public", "manifest.json")
        sw_js = os.path.join(root, "apps", "web", "public", "sw.js")
        icon_512 = os.path.join(root, "apps", "web", "public", "icons", "icon-512.svg")

        self.assertTrue(os.path.exists(package_json))
        self.assertTrue(os.path.exists(tailwind_config))
        self.assertTrue(os.path.exists(layout_tsx))
        self.assertTrue(os.path.exists(page_tsx))
        self.assertTrue(os.path.exists(chat_page))
        self.assertTrue(os.path.exists(call_page))
        self.assertTrue(os.path.exists(memories_page))
        self.assertTrue(os.path.exists(settings_page))
        self.assertTrue(os.path.exists(manifest_json))
        self.assertTrue(os.path.exists(sw_js))
        self.assertTrue(os.path.exists(icon_512))

        # Check branding in manifest
        with open(manifest_json, "r", encoding="utf-8") as f:
            man = json.load(f)
        self.assertEqual(man["name"], "alisha bubbzieee")
        self.assertEqual(man["short_name"], "alisha")


    def test_phase_8_evaluation_harness(self):
        """Phase 8: Evaluator scoring and benchmark report."""
        evaluator = AlishaEvaluator()
        res = evaluator.evaluate("innit\ni literally forgot 💀")
        self.assertGreaterEqual(res["composite_score"], 80.0)
        self.assertEqual(res["rating"], "Authentic Alisha")

        report_json = os.path.join(root, "data", "evaluation_report.json")
        self.assertTrue(os.path.exists(report_json))

    def test_phase_9_islamic_lifeos(self):
        """Phase 9: Islamic LifeOS suite, astronomical salah, dhikr, quran, duas, muhasabah, game."""
        from packages.lifeos import (
            SalahCalculator,
            DhikrEngine,
            QuranEngine,
            DuasDatabase,
            MuhasabahEngine,
            PersonalGrowthEngine,
            SignalGameEngine,
            IslamicContentRouter,
            AdaptiveNotificationScheduler
        )
        # 1. Salah
        calc = SalahCalculator(lat=24.8607, lng=67.0011, timezone_offset=5.0)
        status = calc.get_current_status()
        self.assertIn("current_prayer", status)

        # 2. Quran integrity
        quran = QuranEngine()
        catalog = quran.get_catalog()
        self.assertGreater(len(catalog), 0)
        waqiah = quran.get_surah(56)
        self.assertEqual(waqiah["surah"]["number"], 56)

        # 3. Router separation
        router = IslamicContentRouter()
        self.assertTrue(router.is_religious_query("what time is asr?"))
        self.assertFalse(router.is_religious_query("hey alisha what are you doing?"))


if __name__ == "__main__":
    unittest.main()

