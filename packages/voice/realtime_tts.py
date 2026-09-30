"""
Real-Time Authentic Voice Engine for Alisha.
Production Implementation:
Uses Qwen3-TTS 12Hz 1.7B Base with validated In-Context Learning (ICL) voice cloning.
Conditioned on Colab-validated prompt item (voice_v1/prompt_item.pt).
Falls back to Edge TTS ONLY if explicitly permitted by configuration (ALLOW_STOCK_TTS_FALLBACK=true).
"""

import asyncio
import hashlib
import os
import re
import sys
import time
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List
import torch

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GEN_VOICE_DIR = os.path.join(ROOT, "voice", "generated")
VOICE_DIR = os.path.join(ROOT, "voice")
VOICE_V1_DIR = os.path.join(ROOT, "voice_v1")
os.makedirs(GEN_VOICE_DIR, exist_ok=True)

# ── HARD RUNTIME GUARD: Refuse to run without validated prompt item ───────────
PROMPT_PATH = Path(VOICE_V1_DIR) / "prompt_item.pt"
EXPECTED_MD5 = "7beafdc198a0"

if not PROMPT_PATH.exists():
    raise RuntimeError("prompt_item.pt missing — cannot clone Alisha.")

actual_md5 = hashlib.md5(PROMPT_PATH.read_bytes()).hexdigest()[:12]
if actual_md5 != EXPECTED_MD5:
    raise RuntimeError(f"prompt_item.pt md5 mismatch: {actual_md5} != {EXPECTED_MD5}")

from qwen_tts import VoiceClonePromptItem
sys.modules["__main__"].VoiceClonePromptItem = VoiceClonePromptItem

# Configuration flags
USE_QWEN_TTS_SERVICE = os.environ.get("USE_QWEN_TTS_SERVICE", "true").lower() in ("true", "1")
ALLOW_STOCK_TTS_FALLBACK = os.environ.get("ALLOW_STOCK_TTS_FALLBACK", "false").lower() in ("true", "1")
QWEN_TTS_MODEL_PATH = os.environ.get("QWEN_TTS_MODEL_PATH", r"D:\models\Qwen3-TTS-12Hz-1.7B-Base")
VALIDATED_PROMPT_ITEM_PATH = str(PROMPT_PATH)

# Authentic Voice Corpus: 100% genuine recordings of Alisha (@iishazsr)
AUTHENTIC_ALISHA_RECORDINGS = [
    {
        "id": "ref_uni_travel",
        "audio_path": "/voice_v1/reference.wav",
        "transcript": "that's good, im okay. i'm just getting ready for uni tomorrow. don't wanna go, it's so jarring ugh, cuz it's like two to three umm hour travel",
        "duration_sec": 4.0,
        "duration_label": "0:04",
        "keywords": ["uni", "travel", "tomorrow", "ready", "jarring", "okay", "good", "hour", "hours", "college", "study", "exam", "tired"]
    },
    {
        "id": "alisha_vn_forget_sound",
        "audio_path": "/voice/1211480357481077.wav",
        "transcript": "no but i'm pretty sure if i was to stop sending voice messages you would forget how i sound",
        "duration_sec": 53.5,
        "duration_label": "0:53",
        "keywords": ["forget", "sound", "stop", "messages", "voice message", "voice note", "how i sound", "remember", "hear", "voice"]
    },
    {
        "id": "alisha_vn_remember_voices",
        "audio_path": "/voice/1242969967588294.wav",
        "transcript": "so like whoever has sent you voice messages in the past, you still remember how they sounded",
        "duration_sec": 4.0,
        "duration_label": "0:04",
        "keywords": ["remember", "past", "whoever", "sent", "how they sounded", "sounded", "listen", "audio"]
    },
    {
        "id": "alisha_vn_sweet_voice",
        "audio_path": "/voice/1247080237633732.wav",
        "transcript": "lmao just if their voice was sweet",
        "duration_sec": 5.5,
        "duration_label": "0:05",
        "keywords": ["sweet", "sweet voice", "lmao", "cute", "soft", "honey", "pretty"]
    },
    {
        "id": "alisha_vn_miss_voice",
        "audio_path": "/voice/1511834979942376.wav",
        "transcript": "my voice missed you too",
        "duration_sec": 25.6,
        "duration_label": "0:25",
        "keywords": ["missed", "miss", "miss you", "miss your voice", "missing", "aww", "cutie"]
    },
    {
        "id": "alisha_vn_fall_in_love",
        "audio_path": "/voice/1870167123674999.wav",
        "transcript": "you'll fall in love with my voice",
        "duration_sec": 55.5,
        "duration_label": "0:55",
        "keywords": ["love", "fall in love", "like my voice", "love your voice", "in love", "tease"]
    },
    {
        "id": "alisha_vn_typos_spelling",
        "audio_path": "/voice/1465028061962602.wav",
        "transcript": "omdssd i was thinking to just send voice messages as well because im making a lot of spelling mistakes and its taking time to erase and retype",
        "duration_sec": 4.0,
        "duration_label": "0:04",
        "keywords": ["spelling", "typo", "typos", "erase", "retype", "mistakes", "mistake", "omdssd", "send vn", "typing"]
    },
    {
        "id": "alisha_vn_get_voice_msg",
        "audio_path": "/voice/780868518105469.wav",
        "transcript": "mm no but you can get a voice message",
        "duration_sec": 9.6,
        "duration_label": "0:09",
        "keywords": ["get a voice message", "can you send", "voice note please", "send voice", "send audio", "voice message"]
    },
    {
        "id": "alisha_vn_send_when_can",
        "audio_path": "/voice/1449866003269008.wav",
        "transcript": "suresure ill send you a voice message about it when i can",
        "duration_sec": 5.2,
        "duration_label": "0:05",
        "keywords": ["suresure", "sure", "ill send", "when i can", "tell me", "story"]
    },
    {
        "id": "alisha_vn_voice_innit",
        "audio_path": "/voice/2106340333237368.wav",
        "transcript": "their voice is their voice innit",
        "duration_sec": 39.0,
        "duration_label": "0:39",
        "keywords": ["innit", "accent", "their voice", "british", "talk", "accent"]
    },
    {
        "id": "alisha_vn_mauritius_auntie",
        "audio_path": "/voice/807974821750413.wav",
        "transcript": "I had an auntie back in mauritius that started a rumour saying I was talking to a man most of the time I spent there...",
        "duration_sec": 51.7,
        "duration_label": "0:51",
        "keywords": ["mauritius", "auntie", "rumour", "island", "family", "roots", "heritage"]
    },
    {
        "id": "alisha_vn_send_later_long",
        "audio_path": "/voice/823834583912959.wav",
        "transcript": "later i'll just send a voice message since it might be long",
        "duration_sec": 25.6,
        "duration_label": "0:25",
        "keywords": ["long", "explain", "later", "story", "what happened"]
    },
    {
        "id": "alisha_vn_whats_to_miss",
        "audio_path": "/voice/1499224784558091.wav",
        "transcript": "what's there to miss about my voice 😭",
        "duration_sec": 13.0,
        "duration_label": "0:13",
        "keywords": ["miss about my voice", "why do you miss", "miss you", "soothing"]
    }
]

# Neural TTS selection: emergency fallback only
PRIMARY_VOICE = "en-GB-MaisieNeural"
FALLBACK_VOICE = "en-GB-SoniaNeural"


def match_authentic_voice(query: str, context_type: str = "casual") -> Optional[Dict[str, Any]]:
    """
    Returns None to ensure every turn dynamically synthesizes genuine speech
    for the specific text generated by Groq.
    """
    return None


def clean_text_for_speech(text: str) -> str:
    """Prepares text for natural speech by expanding Alisha's slang and stripping emojis."""
    t = text

    # Alisha's specific slang → natural spoken form
    replacements = [
        (r"\blatw\b", "late"),
        (r"\brn\b", "right now"),
        (r"\btbh\b", "to be honest"),
        (r"\bngl\b", "not gonna lie"),
        (r"\bidk\b", "I don't know"),
        (r"\bimo\b", "in my opinion"),
        (r"\big\b", "I guess"),
        (r"\bomg\b", "oh my god"),
        (r"\bomdssd\b", "oh my days"),
        (r"\bomds\b", "oh my days"),
        (r"\binnit\b", "innit"),
        (r"\bwbu\b", "what about you"),
        (r"\bidc\b", "I don't care"),
        (r"\bofc\b", "of course"),
        (r"\bnah\b", "nah"),
        (r"\byea\b", "yeah"),
        (r"\bsmh\b", "shaking my head"),
        (r"\bbruh\b", "bruh"),
        (r"\byk\b", "you know"),
        (r"\bwanna\b", "wanna"),
        (r"\bgonna\b", "gonna"),
        (r"\bgotta\b", "gotta"),
        (r"\bcuh\b", "cuz"),
        (r"\bima\b", "I'm gonna"),
        (r"\botw\b", "on the way"),
        (r"\bicl\b", "I can't lie"),
        (r"\byeahyeah\b", "yeah yeah"),
        (r"\bohkay\b", "okay"),
        (r"\balrightalright\b", "alright alright"),
        (r"\bbro\b", "bro"),
        (r"\bpls\b", "please"),
        (r"\bthnx\b", "thanks"),
        (r"\bty\b", "thank you"),
        (r"\bnp\b", "no problem"),
        (r"\bwdym\b", "what do you mean"),
        (r"\bwym\b", "what you mean"),
    ]

    for pattern, replacement in replacements:
        t = re.sub(pattern, replacement, t, flags=re.IGNORECASE)

    # Strip emojis that shouldn't be read aloud
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"
        "\U0001FA70-\U0001FAFF"
        "\U00002600-\U000026FF"
        "]+",
        flags=re.UNICODE
    )
    t = emoji_pattern.sub("", t).strip()
    t = re.sub(r"\s+", " ", t).strip()

    return t or "hey cutie"


class Qwen3TTSVoiceEngine:
    """
    Singleton production voice cloning engine using Qwen3-TTS 12Hz 1.7B Base.
    Keeps model warm in memory and caches canonical ICL prompt.
    """
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.model = None
        self.canonical_prompt = None
        self._init_lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> "Qwen3TTSVoiceEngine":
        with cls._lock:
            if cls._instance is None:
                cls._instance = Qwen3TTSVoiceEngine()
            return cls._instance

    def _ensure_initialized(self):
        with self._init_lock:
            if self.model is not None and self.canonical_prompt is not None:
                return

            print(f"[Qwen3TTS] Initializing Qwen3-TTS Base model from: {QWEN_TTS_MODEL_PATH}")
            import torch
            from qwen_tts import Qwen3TTSModel, VoiceClonePromptItem

            # Set torch threads for optimal CPU performance
            num_cores = max(1, (os.cpu_count() or 4) - 1)
            torch.set_num_threads(num_cores)

            self.model = Qwen3TTSModel.from_pretrained(
                QWEN_TTS_MODEL_PATH,
                dtype=torch.bfloat16
            )

            print(f"[Qwen3TTS] Loading validated prompt item from: {VALIDATED_PROMPT_ITEM_PATH}")
            loaded_item = torch.load(VALIDATED_PROMPT_ITEM_PATH, map_location="cpu", weights_only=False)
            if not isinstance(loaded_item, list):
                self.canonical_prompt = [loaded_item]
            else:
                self.canonical_prompt = loaded_item

            pi = self.canonical_prompt[0]
            assert pi.icl_mode is True, "prompt_item must have icl_mode=True"
            assert pi.x_vector_only_mode is False, "prompt_item must have x_vector_only_mode=False"
            assert pi.ref_code.shape == (150, 16), f"ref_code shape {pi.ref_code.shape} != (150, 16)"
            assert pi.ref_spk_embedding.shape == (2048,), f"ref_spk_embedding shape {pi.ref_spk_embedding.shape} != (2048,)"
            print(f"[Qwen3TTS] Validated prompt item ready: icl_mode={pi.icl_mode}, ref_code={list(pi.ref_code.shape)}, ref_spk={list(pi.ref_spk_embedding.shape)}")

    def synthesize(self, text: str, speed: float = 1.0) -> Optional[str]:
        import soundfile as sf

        clean_text = clean_text_for_speech(text)
        print(f"[RealTimeTTS] TTS_TEXT_RAW: {text}")
        print(f"[RealTimeTTS] TTS_TEXT_NORMALIZED: {clean_text}")

        # Unique audio cache key based on clean text and model
        text_hash = hashlib.md5(f"qwen3_12hz_{clean_text}".encode("utf-8")).hexdigest()[:16]
        out_filename = f"alisha_qwen_{text_hash}.wav"
        out_path = os.path.join(GEN_VOICE_DIR, out_filename)

        if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
            return f"/voice/generated/{out_filename}"

        self._ensure_initialized()

        # Calculate tight max_new_tokens budget (12.5 codec frames per second)
        word_count = len(clean_text.split())
        token_budget = max(40, min(180, int(word_count * 15)))

        t0 = time.time()
        wavs, fs = self.model.generate_voice_clone(
            text=clean_text,
            voice_clone_prompt=self.canonical_prompt,
            do_sample=True,
            top_k=50,
            top_p=1.0,
            temperature=0.9,
            repetition_penalty=1.05,
            max_new_tokens=token_budget
        )
        dur_s = time.time() - t0
        wav = wavs[0]
        sf.write(out_path, wav, fs)
        audio_dur = len(wav) / fs
        print(f"[RealTimeTTS] Synthesized {audio_dur:.2f}s audio in {dur_s:.2f}s -> {out_filename}")

        return f"/voice/generated/{out_filename}"


async def _synthesize_async(text: str, voice: str = PRIMARY_VOICE, speed: float = 1.0) -> str:
    """Emergency stock fallback using Edge TTS."""
    import edge_tts

    clean_text = clean_text_for_speech(text)

    cache_key = f"{voice}_{speed:.2f}_{clean_text}"
    file_hash = hashlib.md5(cache_key.encode("utf-8")).hexdigest()[:16]
    out_filename = f"alisha_{file_hash}.mp3"
    out_path = os.path.join(GEN_VOICE_DIR, out_filename)

    if os.path.exists(out_path) and os.path.getsize(out_path) > 500:
        return f"/voice/generated/{out_filename}"

    base_rate_delta = 14
    rate_percent = int(base_rate_delta + (speed - 1.0) * 100)
    rate_str = f"{rate_percent:+d}%"

    for v in [voice, FALLBACK_VOICE]:
        try:
            communicate = edge_tts.Communicate(
                text=clean_text,
                voice=v,
                rate=rate_str,
                pitch="+4Hz"
            )
            await communicate.save(out_path)
            if os.path.exists(out_path) and os.path.getsize(out_path) > 500:
                return f"/voice/generated/{out_filename}"
        except Exception:
            continue

    return f"/voice/generated/{out_filename}"


def synthesize_speech(text: str, voice: str = PRIMARY_VOICE, speed: float = 1.0, user_prompt: str = "") -> Optional[str]:
    """
    Dynamically synthesizes new speech for Alisha's generated text response.
    Primary path: Official Qwen3-TTS 12Hz Base with authentic voice clone prompt.
    Fallback policy: Stock Edge TTS allowed ONLY when ALLOW_STOCK_TTS_FALLBACK=true.
    """
    if not text or not text.strip():
        text = "hey cutie"

    if USE_QWEN_TTS_SERVICE:
        try:
            engine = Qwen3TTSVoiceEngine.get_instance()
            return engine.synthesize(text, speed=speed)
        except Exception as e:
            print(f"[RealTimeTTS Qwen Error] {e}")
            if not ALLOW_STOCK_TTS_FALLBACK:
                # Per Phase 35: Never silently fall back to stock Edge TTS unless explicitly allowed
                raise RuntimeError(
                    f"Qwen3-TTS generation failed and ALLOW_STOCK_TTS_FALLBACK=false. Error: {e}"
                )
            print("[RealTimeTTS] Falling back to emergency stock TTS due to explicit ALLOW_STOCK_TTS_FALLBACK=true")

    # Stock fallback (only reachable if ALLOW_STOCK_TTS_FALLBACK=true or USE_QWEN_TTS_SERVICE=false)
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        url = loop.run_until_complete(_synthesize_async(text, voice, speed))
        loop.close()
        return url
    except Exception as e:
        print(f"[RealTimeTTS Stock Fallback Error] {e}")
        return "/voice/1242969967588294.wav"
