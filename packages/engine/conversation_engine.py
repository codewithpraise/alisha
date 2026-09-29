"""
Local ConversationEngine for Alisha Bubbzieee.
Orchestrates:
  User (Text or Voice -> VAD -> ASR)
  -> DeterministicPolicy
  -> SQLite / FTS5 / Style Retriever
  -> ContextPacker
  -> Local LLM Generator (LlmEngine)
  -> Optional Burst Decision (hard-limited to max 2 messages)
  -> TTS (TtsEngine) -> Audio

Guarantees:
- LLM is NOT responsible for memory management
- Controller performs deterministic routing
- 100% offline, zero network telemetry, zero private data logging
- Configurable and completely swappable components
"""

import os
import random
import sys
import time
import uuid
from typing import Callable, Dict, Any, List, Optional

from packages.memory.database import MemoryDatabase
from packages.memory.retriever import MemoryRetriever, ScoreWeights
from packages.policy.deterministic_policy import DeterministicPolicy, PolicyDecision
from packages.inference.context_packer import ContextPacker
from packages.inference.llm_engine import LlmEngine, GenerationRequest, LocalSimulatedLlmEngine
from packages.voice.engine_interfaces import (
    VadEngine,
    AsrEngine,
    TtsEngine,
    AudioChunkCallback,
    EnergyVadEngine,
    WhisperAsrEngine,
    DeterministicMockTtsEngine,
)
from packages.diagnostics.diagnostics import DiagnosticsCollector, ExecutionDiagnostics


class EngineResponse:
    def __init__(
        self,
        messages: List[str],
        policy_decision: PolicyDecision,
        diagnostics: ExecutionDiagnostics,
        is_voice: bool = False,
    ):
        self.messages = messages
        self.policy_decision = policy_decision
        self.diagnostics = diagnostics
        self.is_voice = is_voice

    def to_dict(self) -> Dict[str, Any]:
        return {
            "messages": self.messages,
            "policy": self.policy_decision.to_dict(),
            "diagnostics": self.diagnostics.to_dict(),
            "is_voice": self.is_voice,
        }


class ConversationEngine:
    def __init__(
        self,
        db: MemoryDatabase,
        retriever: Optional[MemoryRetriever] = None,
        policy: Optional[DeterministicPolicy] = None,
        packer: Optional[ContextPacker] = None,
        llm: Optional[LlmEngine] = None,
        tts: Optional[TtsEngine] = None,
        asr: Optional[AsrEngine] = None,
        vad: Optional[VadEngine] = None,
        diagnostics: Optional[DiagnosticsCollector] = None,
        conversation_id: str = "conv_default",
    ):
        self.db = db
        self.retriever = retriever or MemoryRetriever(db)
        self.policy = policy or DeterministicPolicy()
        self.packer = packer or ContextPacker()
        self.llm = llm or LocalSimulatedLlmEngine()
        self.tts = tts or DeterministicMockTtsEngine()
        self.asr = asr or WhisperAsrEngine()
        self.vad = vad or EnergyVadEngine()
        self.diagnostics = diagnostics or DiagnosticsCollector.get_instance()
        self.conversation_id = conversation_id

    def cancel_active(self):
        """Immediately halts active LLM generation or TTS playback."""
        self.llm.cancel()
        self.tts.cancel()

    def process_text_turn(
        self,
        user_text: str,
        on_token: Optional[Callable[[str], None]] = None,
        deterministic_test_mode: bool = False,
        is_voice_turn: bool = False,
    ) -> EngineResponse:
        trace_id = f"trace_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        now_ms = int(start_time * 1000)

        # 1. Store incoming user message in SQLite
        user_msg_id = f"msg_{uuid.uuid4().hex[:10]}"
        self.db.insert_message(
            msg_id=user_msg_id,
            conversation_id=self.conversation_id,
            timestamp=now_ms,
            sender="user",
            text=user_text,
            source_index=int(now_ms % 100000),
        )

        # 2. Deterministic Routing Policy
        policy_decision = self.policy.evaluate(
            user_input=user_text,
            is_voice_input=is_voice_turn,
        )

        # 3. Retrieve Evidence (Memories & Style Exemplars)
        t_ret_start = time.time()
        retrieved_facts = []
        if policy_decision.retrieval_depth > 0:
            retrieved_facts = self.retriever.search_memories(
                query=user_text,
                depth=policy_decision.retrieval_depth,
            )
        retrieval_latency_ms = (time.time() - t_ret_start) * 1000

        # Retrieve real style exemplars for the selected style mode
        style_exemplars = self.retriever.get_style_exemplars(
            mode=policy_decision.style_mode,
            limit=2,
            topic_query=user_text,
        )

        # Recent conversation history from SQLite
        recent_msgs = self.db.get_recent_messages(limit=6, conversation_id=self.conversation_id)

        # 4. Context Packing
        packed = self.packer.pack(
            recent_messages=recent_msgs,
            relevant_facts=retrieved_facts,
            episode_memory=None,
            style_exemplars=style_exemplars,
            current_user_input=user_text,
        )

        # 5. Local LLM Generator
        gen_req = GenerationRequest(
            prompt=packed.prompt,
            max_tokens=policy_decision.max_response_tokens,
            deterministic_test_mode=deterministic_test_mode,
        )
        gen_res = self.llm.generate(gen_req, on_token=on_token)

        primary_text = gen_res.text.strip()
        if not primary_text:
            primary_text = "yea ig"

        output_messages = [primary_text]

        # 6. Deterministic Burst Decision (Hard-limited to max 1 optional second message)
        if policy_decision.permit_second_burst:
            burst2 = self.policy.evaluate_second_burst(primary_text, policy_decision.style_mode)
            if burst2:
                output_messages.append(burst2)

        # Store assistant response(s) in SQLite
        for i, out_msg in enumerate(output_messages):
            asst_msg_id = f"msg_asst_{uuid.uuid4().hex[:8]}_{i}"
            self.db.insert_message(
                msg_id=asst_msg_id,
                conversation_id=self.conversation_id,
                timestamp=int(time.time() * 1000),
                sender="alisha",
                text=out_msg,
                source_index=int(now_ms % 100000) + i + 1,
            )

        # 7. Collect Execution Diagnostics
        total_time_ms = (time.time() - start_time) * 1000
        diag = ExecutionDiagnostics(
            trace_id=trace_id,
            model_load_time_ms=0.0,
            prompt_tokens=gen_res.prompt_tokens,
            generated_tokens=gen_res.generated_tokens,
            time_to_first_token_ms=gen_res.time_to_first_token_ms,
            tokens_per_sec=gen_res.tokens_per_sec,
            retrieval_count=len(retrieved_facts),
            retrieval_latency_ms=retrieval_latency_ms,
            context_size_chars=len(packed.prompt),
            tts_first_audio_latency_ms=0.0,
            tts_generation_time_ms=0.0,
            asr_latency_ms=0.0,
        )
        self.diagnostics.record(diag)

        return EngineResponse(
            messages=output_messages,
            policy_decision=policy_decision,
            diagnostics=diag,
            is_voice=policy_decision.is_voice_requested,
        )

    def process_voice_turn(
        self,
        audio_pcm: bytes,
        on_audio_chunk: AudioChunkCallback,
        on_token: Optional[Callable[[str], None]] = None,
        deterministic_test_mode: bool = False,
    ) -> EngineResponse:
        """
        End-to-End Voice pipeline:
        audio -> VAD -> ASR -> ConversationEngine -> LLM -> TTS -> audio chunk playback
        """
        # 1. VAD Speech Detection
        has_speech = self.vad.process_pcm(audio_pcm)
        if not has_speech:
            # Silence / no speech detected
            diag = ExecutionDiagnostics(trace_id=f"vad_silence_{uuid.uuid4().hex[:6]}")
            return EngineResponse(
                messages=[],
                policy_decision=PolicyDecision(False, 0, "neutral", 0, True, False),
                diagnostics=diag,
                is_voice=True,
            )

        # 2. ASR Transcription
        t_asr_start = time.time()
        transcript = self.asr.transcribe(audio_pcm)
        asr_latency_ms = (time.time() - t_asr_start) * 1000

        if not transcript.strip():
            transcript = "hey"

        # 3. Text pipeline
        response = self.process_text_turn(
            user_text=transcript,
            on_token=on_token,
            deterministic_test_mode=deterministic_test_mode,
            is_voice_turn=True,
        )
        response.is_voice = True

        # 4. TTS Streaming Synthesis
        t_tts_start = time.time()
        first_audio_received = False
        tts_first_latency_ms = 0.0

        def chunk_interceptor(chunk: bytes, is_final: bool):
            nonlocal first_audio_received, tts_first_latency_ms
            if not first_audio_received:
                first_audio_received = True
                tts_first_latency_ms = (time.time() - t_tts_start) * 1000
            on_audio_chunk(chunk, is_final)

        full_speech_text = " ".join(response.messages)
        self.tts.synthesize(full_speech_text, callback=chunk_interceptor)
        tts_total_ms = (time.time() - t_tts_start) * 1000

        # Update diagnostics with voice latencies
        response.diagnostics.asr_latency_ms = asr_latency_ms
        response.diagnostics.tts_first_audio_latency_ms = tts_first_latency_ms
        response.diagnostics.tts_generation_time_ms = tts_total_ms
        self.diagnostics.record(response.diagnostics)

        return response
