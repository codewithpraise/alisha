"""
Streaming Voice Conversation Pipeline for Alisha Bubbzieee.
Implements:
  - Low-latency streaming (chunked TTS playback before LLM finishes)
  - Interruption detection (barge-in cancellation)
  - VAD state machine (IDLE -> LISTENING -> THINKING -> SPEAKING -> INTERRUPTED)
"""

from enum import Enum
import queue
import threading
import time
from typing import Callable, Optional, Dict, Any


class CallState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    INTERRUPTED = "interrupted"


class VoiceCallPipeline:
    def __init__(
        self,
        on_state_change: Optional[Callable[[CallState], None]] = None,
        on_audio_chunk: Optional[Callable[[bytes], None]] = None,
    ):
        self.state = CallState.IDLE
        self.on_state_change = on_state_change
        self.on_audio_chunk = on_audio_chunk
        self.audio_queue = queue.Queue()
        self.is_running = False
        self._playback_thread: Optional[threading.Thread] = None
        self._interrupt_event = threading.Event()

    def set_state(self, new_state: CallState):
        self.state = new_state
        if self.on_state_change:
            self.on_state_change(new_state)

    def on_vad_speech_start(self):
        """Called when user starts speaking."""
        if self.state == CallState.SPEAKING:
            # User interrupted Alisha while she was talking!
            self.trigger_interruption()
        self.set_state(CallState.LISTENING)

    def trigger_interruption(self):
        """Immediately halts audio playback and drains buffer."""
        print("[VoicePipeline] Interruption detected! Halting TTS playback.")
        self._interrupt_event.set()
        # Drain audio queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        self.set_state(CallState.INTERRUPTED)

    def on_vad_speech_end(self, user_audio_transcript: str):
        """Called when user finishes speaking."""
        self.set_state(CallState.THINKING)
        self._interrupt_event.clear()

        # In full runtime: stream tokens from LLM -> chunk to TTS -> enqueue
        # Here we simulate the pipeline step
        self.stream_response(user_audio_transcript)

    def stream_response(self, text: str):
        self.set_state(CallState.SPEAKING)
        # Play synthesized audio chunks
        def worker():
            for i in range(3):
                if self._interrupt_event.is_set():
                    break
                # Dummy audio chunk (or real PCM bytes)
                fake_pcm = b"\x00" * 4800  # 100ms chunk
                if self.on_audio_chunk:
                    self.on_audio_chunk(fake_pcm)
                time.sleep(0.3)
            if not self._interrupt_event.is_set():
                self.set_state(CallState.LISTENING)

        self._playback_thread = threading.Thread(target=worker, daemon=True)
        self._playback_thread.start()
