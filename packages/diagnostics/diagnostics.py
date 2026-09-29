"""
Local Developer Diagnostics for Alisha Bubbzieee.
Tracks performance telemetry:
- model_load_time_ms
- prompt_tokens
- generated_tokens
- time_to_first_token_ms
- tokens_per_sec
- retrieval_count
- retrieval_latency_ms
- context_size_chars
- tts_first_audio_latency_ms
- tts_generation_time_ms
- asr_latency_ms

Privacy & Security Guarantees:
- Stored exclusively in local memory (circular buffer of 50 records)
- Zero external uploads / zero telemetry network calls
- Never records raw conversational text or private information
- Uses opaque random IDs in debug logs
"""

import time
from typing import Dict, Any, List, Optional


class ExecutionDiagnostics:
    def __init__(
        self,
        trace_id: str,
        model_load_time_ms: float = 0.0,
        prompt_tokens: int = 0,
        generated_tokens: int = 0,
        time_to_first_token_ms: float = 0.0,
        tokens_per_sec: float = 0.0,
        retrieval_count: int = 0,
        retrieval_latency_ms: float = 0.0,
        context_size_chars: int = 0,
        tts_first_audio_latency_ms: float = 0.0,
        tts_generation_time_ms: float = 0.0,
        asr_latency_ms: float = 0.0,
        timestamp: Optional[float] = None,
    ):
        self.trace_id = trace_id
        self.model_load_time_ms = model_load_time_ms
        self.prompt_tokens = prompt_tokens
        self.generated_tokens = generated_tokens
        self.time_to_first_token_ms = time_to_first_token_ms
        self.tokens_per_sec = tokens_per_sec
        self.retrieval_count = retrieval_count
        self.retrieval_latency_ms = retrieval_latency_ms
        self.context_size_chars = context_size_chars
        self.tts_first_audio_latency_ms = tts_first_audio_latency_ms
        self.tts_generation_time_ms = tts_generation_time_ms
        self.asr_latency_ms = asr_latency_ms
        self.timestamp = timestamp or time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "model_load_time_ms": round(self.model_load_time_ms, 2),
            "prompt_tokens": self.prompt_tokens,
            "generated_tokens": self.generated_tokens,
            "time_to_first_token_ms": round(self.time_to_first_token_ms, 2),
            "tokens_per_sec": round(self.tokens_per_sec, 2),
            "retrieval_count": self.retrieval_count,
            "retrieval_latency_ms": round(self.retrieval_latency_ms, 2),
            "context_size_chars": self.context_size_chars,
            "tts_first_audio_latency_ms": round(self.tts_first_audio_latency_ms, 2),
            "tts_generation_time_ms": round(self.tts_generation_time_ms, 2),
            "asr_latency_ms": round(self.asr_latency_ms, 2),
            "timestamp": int(self.timestamp * 1000),
        }


class DiagnosticsCollector:
    _instance: Optional["DiagnosticsCollector"] = None

    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self._history: List[ExecutionDiagnostics] = []
        self._latest: Optional[ExecutionDiagnostics] = None

    @classmethod
    def get_instance(cls) -> "DiagnosticsCollector":
        if cls._instance is None:
            cls._instance = DiagnosticsCollector()
        return cls._instance

    def record(self, diag: ExecutionDiagnostics):
        self._latest = diag
        self._history.append(diag)
        if len(self._history) > self.max_history:
            self._history.pop(0)

    def get_latest(self) -> Optional[Dict[str, Any]]:
        return self._latest.to_dict() if self._latest else None

    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        return [d.to_dict() for d in reversed(self._history[-limit:])]

    def get_summary_averages(self) -> Dict[str, float]:
        if not self._history:
            return {
                "avg_ttft_ms": 0.0,
                "avg_tokens_per_sec": 0.0,
                "avg_retrieval_latency_ms": 0.0,
                "avg_tts_latency_ms": 0.0,
                "avg_asr_latency_ms": 0.0,
                "sample_count": 0,
            }

        n = len(self._history)
        return {
            "avg_ttft_ms": round(sum(d.time_to_first_token_ms for d in self._history) / n, 2),
            "avg_tokens_per_sec": round(sum(d.tokens_per_sec for d in self._history) / n, 2),
            "avg_retrieval_latency_ms": round(sum(d.retrieval_latency_ms for d in self._history) / n, 2),
            "avg_tts_latency_ms": round(sum(d.tts_generation_time_ms for d in self._history) / n, 2),
            "avg_asr_latency_ms": round(sum(d.asr_latency_ms for d in self._history) / n, 2),
            "sample_count": n,
        }
