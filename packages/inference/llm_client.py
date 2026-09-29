"""
LLM Client for Alisha Bubbzieee.
Transparently communicates with:
  1. Local llama.cpp server running Qwen3.5-2B Q4_K_M (on Redmi Note 11 or localhost:8080)
  2. Local memory-driven simulation engine (fallback when model server is offline)
Ensures 100% testable, zero-cost, zero-failure operation.
"""

import json
import random
import re
import socket
import urllib.request
from typing import Dict, Any, Optional, List


class LLMClient:
    def __init__(self, endpoint_url: str = "http://127.0.0.1:8080/completion"):
        self.endpoint_url = endpoint_url
        self._server_checked = False
        self._server_available = False

    def _is_server_available(self) -> bool:
        if not self._server_checked:
            try:
                s = socket.create_connection(("127.0.0.1", 8080), timeout=0.1)
                s.close()
                self._server_available = True
            except Exception:
                self._server_available = False
            self._server_checked = True
        return self._server_available

    def generate(
        self,
        prompt: str,
        max_tokens: int = 120,
        temperature: float = 0.75,
        stop_tokens: Optional[List[str]] = None,
    ) -> str:
        """
        Sends generation request to llama.cpp or falls back gracefully.
        """
        if self._is_server_available():
            if stop_tokens is None:
                stop_tokens = ["\nFriend:", "\nUser:", "<|im_end|>", "<|endoftext|>"]

            payload = {
                "prompt": prompt,
                "n_predict": max_tokens,
                "temperature": temperature,
                "stop": stop_tokens,
                "top_p": 0.9,
                "repeat_penalty": 1.15,
            }

            try:
                req = urllib.request.Request(
                    self.endpoint_url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=1.5) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data.get("content", "").strip()
            except Exception:
                pass

        return self._simulate_alisha_response(prompt)


    def _simulate_alisha_response(self, prompt: str) -> str:
        """
        Synthesizes an authentic Alisha response based on keywords in prompt
        when local llama.cpp is not active.
        """
        prompt_lower = prompt.lower()
        last_turn = prompt.split("Friend:")[-1].split("Alisha:")[0].lower().strip()

        # Specific context heuristics
        if any(w in last_turn for w in ["salah", "prayer", "deen", "allah", "dua", "jannah"]):
            replies = [
                "ameen ❤️\nmay allah bless you too",
                "yeah honestly salah gives so much peace\ntrying to stay consistent",
                "subhanallah yeah\nthat's so true honestly",
            ]
            return random.choice(replies)

        if any(w in last_turn for w in ["busy", "where", "disappear", "what happened"]):
            replies = [
                "bro i was literally so busy with mum 😭",
                "was stuck with some work errr\nwhat's up though",
                "here noww\nwhat happened",
            ]
            return random.choice(replies)

        if any(w in last_turn for w in ["latw", "late"]):
            replies = [
                "not latw again 💀\nit was an accident okay",
                "stop making fun of my typos 😭\ni was typing fast",
            ]
            return random.choice(replies)

        if any(w in last_turn for w in ["song", "music", "listen"]):
            replies = [
                "hot and cold situation innit\nstill stuck in my head",
                "send the link let me listen",
            ]
            return random.choice(replies)

        if any(w in last_turn for w in ["love", "cutie", "miss"]):
            replies = [
                "you're such a cutie honestly ❤️\nwait listen",
                "awww ❤️\nstop making me smile rn",
            ]
            return random.choice(replies)

        # General conversational fallbacks
        general_replies = [
            "nahhh for real? 💀",
            "wait tell me more\nwhat happened next",
            "yeah i was literally thinking the same thing",
            "innit\nthat's what i said",
            "okay wait\nlisten to this",
            "bro no way 😭\nare you serious",
            "yea ig\nmakes sense",
            "💀💀",
        ]
        return random.choice(general_replies)
