"""
Groq API Provider for Alisha AI Friend.
Uses OpenAI-compatible endpoint with ultra-low latency (450+ tok/s).
Primary model: qwen/qwen3.8-27b
Secondary fallback: openai/gpt-oss-120b / openai/gpt-oss-20b
Explicit reasoning_effort: "none" for natural, uninhibited texting persona.
"""
import os
import json
import time
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional, Callable


def _load_env_file():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env_path = os.path.join(root, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip('"').strip("'")
                    if k not in os.environ:
                        os.environ[k] = v


_load_env_file()


class GroqProvider:
    DEFAULT_MODEL = "qwen/qwen3.8-27b"
    FALLBACK_MODEL = "llama-3.1-8b-instant"  # Fast Groq-native fallback
    ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        _load_env_file()
        self.api_key = api_key or os.environ.get("GROQ_API_KEY", "")
        self.model = model or os.environ.get("GROQ_MODEL", self.DEFAULT_MODEL)
        self.reasoning_effort = os.environ.get("GROQ_REASONING_EFFORT", "none")

    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key.startswith("gsk_"))

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.72,
        max_tokens: int = 80,
        stop: Optional[List[str]] = None,
        on_token: Optional[Callable[[str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Execute chat completion on Groq with low latency.
        """
        if not self.is_available():
            raise ValueError("Groq API key not configured in .env")

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": on_token is not None,
        }
        # Disable chain-of-thought tokens for authentic natural text
        if self.reasoning_effort:
            payload["reasoning_effort"] = self.reasoning_effort

        if stop:
            payload["stop"] = stop

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "AlishaApp/2.0",
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.ENDPOINT, data=data_bytes, headers=headers, method="POST")

        start_time = time.time()
        try:
            if on_token is not None:
                accumulated = []
                ttft_ms = 0.0
                with urllib.request.urlopen(req, timeout=12.0) as resp:
                    for line in resp:
                        decoded = line.decode("utf-8").strip()
                        if not decoded.startswith("data: "):
                            continue
                        chunk_raw = decoded[6:]
                        if chunk_raw == "[DONE]":
                            break
                        try:
                            chunk = json.loads(chunk_raw)
                            delta = chunk["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                if not accumulated:
                                    ttft_ms = (time.time() - start_time) * 1000
                                accumulated.append(content)
                                on_token(content)
                        except Exception:
                            continue

                total_time = (time.time() - start_time) * 1000
                full_text = "".join(accumulated).strip()
                return {
                    "text": full_text,
                    "model": self.model,
                    "ttft_ms": ttft_ms or total_time,
                    "total_ms": total_time,
                }
            else:
                with urllib.request.urlopen(req, timeout=10.0) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                    total_time = (time.time() - start_time) * 1000
                    full_text = result["choices"][0]["message"]["content"].strip()
                    return {
                        "text": full_text,
                        "model": self.model,
                        "ttft_ms": total_time,
                        "total_ms": total_time,
                    }

        except urllib.error.HTTPError as e:
            # Handle rate limits with exponential backoff retry
            if e.code == 429:
                retry_after = 2.0
                try:
                    h_val = e.headers.get("Retry-After")
                    if h_val:
                        retry_after = max(1.0, float(h_val))
                except Exception:
                    pass
                print(f"[GroqProvider] Rate limit (429) on {self.model}, waiting {retry_after}s before retry...")
                time.sleep(retry_after)
                return self.generate(messages, temperature, max_tokens, stop, on_token)
            raise e
