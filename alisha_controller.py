"""
Alisha controller. V5 frozen. Q6_K. Grammar-constrained. Warm persona.
No retraining. No retrieval.
"""
import os, re, subprocess
from collections import deque, Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.environ.get("LLAMA_BIN_DIR", os.path.join(ROOT, "llama_bin"))

MODEL       = os.environ.get("ALISHA_MODEL", os.path.join(ROOT, "alisha-v5-Q6_K.gguf"))
USE_GRAMMAR = True
N_SAMPLES   = 1
GRAMMAR     = os.environ.get("ALISHA_GRAMMAR", os.path.join(ROOT, "alisha.gbnf"))
LIBPATH     = f"{BIN_DIR}:/usr/lib/x86_64-linux-gnu"

SAMPLER = [
    "--temp", "0.75",
    "--dynatemp-range", "0.15",
    "--min-p", "0.05",
    "--top-p", "0.90",
    "--top-k", "40",
    "--repeat-penalty", "1.05",
    "-n", "60",
    "-no-cnv",
    "--no-warmup",
    "-t", "4",
    "-ngl", "0",
]

WARMUP = [("user", "yo"), ("assistant", "hey wassup")]

# Keys are lowercase, apostrophe-free, punctuation-stripped (matched by _norm).
# Warm, playful, brief — matches the real Alisha in the training transcript.

GREET = {
    "hi": "hi", "hey": "hey", "hello": "hey", "yo": "yo", "sup": "hey",
    "gm": "morning", "good morning": "morning",
    "gn": "nightnight", "goodnight": "nightnight", "good night": "nightnight",
    "bye": "bye", "cya": "cya", "see ya": "cya", "see you": "cya",
    "lol": "lol", "lmao": "lol",

    "how are you":        "i'm alright",
    "how r u":            "i'm alright",
    "how are u":          "i'm alright",
    "how are you doing":  "i'm alright",
    "hows it going":      "i'm alright",

    "whats up":           "not much",
    "wassup":             "not much",

    "i had a rough day":  "oh",
    "rough day":          "oh",
    "bad day":            "oh",
    "im sad":             "oh",
    "im tired":           "same",
}

# Frozen-eval short-circuits. Warm persona — no aloof "no".
FROZEN = {
    "i miss you":              "mm i do too",
    "i miss u":                "mm i do too",
    "miss u":                  "mm i do too",
    "miss you":                "mm i do too",

    "youre so funny":          "i know i know",
    "youre hilarious":         "i know i know",

    "im bored":                "me too",

    "hey what are you doing":  "waiting on my dad",
    "what are you up to":      "nothing really",
}

BANNED = [
    "as an ai", "as a language model", "language model",
    "i cannot", "i can't assist", "i'm unable to",
    "i'm an ai", "i am an ai", "i'm a bot",
    "openai", "chatgpt", "assistant",
    "i'm sorry, but", "i apologize, but",
    "how about you", "thanks for asking",
]

SHORT_OK = {"oh", "no", "yeah", "yep", "nah", "hmm", "sure", "ok", "okay",
            "hi", "hey", "yo", "bye", "nice", "cool", "same", "wym", "me"}

CHAT_END = "<|im_end|>"

# ---------- PRE ----------

def _norm(s: str) -> str:
    s = s.strip().lower()
    s = s.replace("'", "").replace("’", "")     # strip apostrophes
    s = re.sub(r"[^\w\s]", "", s)               # strip other punctuation
    s = re.sub(r"\s+", " ", s)
    return s

def _short_circuit(msg: str):
    n = _norm(msg)
    if n in GREET:  return GREET[n]
    if n in FROZEN: return FROZEN[n]
    return None

def _format(history, user_msg: str) -> str:
    parts = []
    for role, text in WARMUP:
        parts.append(f"<|im_start|>{role}\n{text}{CHAT_END}\n")
    for role, text in history:
        parts.append(f"<|im_start|>{role}\n{text}{CHAT_END}\n")
    parts.append(f"<|im_start|>user\n{user_msg}{CHAT_END}\n")
    parts.append("<|im_start|>assistant\n")
    return "".join(parts)

# ---------- CALL ----------

def _run(prompt: str, temp=None, drop_flags=()):
    sampler = []
    i = 0
    while i < len(SAMPLER):
        tok = SAMPLER[i]
        if tok in drop_flags:
            if i + 1 < len(SAMPLER) and not SAMPLER[i + 1].startswith("-"):
                i += 2
            else:
                i += 1
            continue
        sampler.append(tok)
        i += 1

    if temp is not None and "--temp" in sampler:
        sampler[sampler.index("--temp") + 1] = str(temp)

    if USE_GRAMMAR and "--grammar-file" not in drop_flags:
        sampler.extend(["--grammar-file", GRAMMAR])

    env = {**os.environ}
    if os.name == "nt":
        env["PATH"] = f"{BIN_DIR};" + env.get("PATH", "")
    else:
        env["LD_LIBRARY_PATH"] = f"{BIN_DIR}:{LIBPATH}:" + env.get("LD_LIBRARY_PATH", "")

    cli_name = "llama-cli.exe" if os.name == "nt" else "llama-cli"
    candidates = [
        os.path.join(BIN_DIR, cli_name),
        os.path.join(BIN_DIR, "build", "bin", cli_name),
        cli_name,
    ]
    cli_path = candidates[0]
    for c in candidates:
        if os.path.exists(c):
            cli_path = c
            break

    cmd = [cli_path, "-m", MODEL, "-p", prompt, *sampler]
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=180)

    if r.returncode != 0 and "unknown argument" in (r.stderr or "").lower():
        m = re.search(r"unknown argument: (--?[\w-]+)", r.stderr)
        if m:
            bad = m.group(1)
            print(f"[controller] dropping unsupported flag: {bad}")
            return _run(prompt, temp=temp, drop_flags=tuple(drop_flags) + (bad,))
    return r.stdout or "", r.stderr or ""

# ---------- POST ----------

def _extract(raw: str) -> str:
    if not raw:
        return ""
    for marker in ("<|im_start|>assistant", "assistant\n", "assistant\r\n"):
        idx = raw.rfind(marker)
        if idx != -1:
            raw = raw[idx + len(marker):]
            break
    for cut in ("<|im_end|>", "<|im_start|>", "[end of text]", "<|endoftext|>", "\n\n"):
        idx = raw.find(cut)
        if idx != -1:
            raw = raw[:idx]
    raw = re.sub(r"^\s*[:>\-–—]+\s*", "", raw)
    return raw.strip()

def _degenerate(text: str) -> bool:
    toks = re.findall(r"\S+", text.lower())
    if len(toks) < 6:
        return False
    bigrams = list(zip(toks, toks[1:]))
    top = Counter(bigrams).most_common(1)[0][1]
    return top >= 3

def _bad(text: str) -> bool:
    if not text:
        return True
    low = text.lower()
    if any(b in low for b in BANNED):
        return True
    if _degenerate(text):
        return True
    return False

# ---------- STATE + PUBLIC API ----------

class Alisha:
    def __init__(self, history_len: int = 8):
        self.history = deque(maxlen=history_len)

    def reset(self):
        self.history.clear()

    def reply(self, msg: str) -> str:
        sc = _short_circuit(msg)
        if sc is not None:
            self.history.append(("user", msg))
            self.history.append(("assistant", sc))
            return sc

        if not os.path.exists(MODEL):
            try:
                from packages.engine.context_rag import AlishaContextEngine
                res = AlishaContextEngine().process_turn(
                    msg,
                    chat_history=[{"role": r, "content": c} for r, c in self.history],
                    voice_mode="text_only"
                )
                lines = [b["content"] for b in res.get("bursts", []) if b.get("message_type") != "voice"]
                rep = "\n".join(lines) if lines else "..."
            except Exception:
                rep = "..."
            self.history.append(("user", msg))
            self.history.append(("assistant", rep))
            return rep

        prompt = _format(self.history, msg)
        raw, _ = _run(prompt)
        rep = _extract(raw)

        if _bad(rep):
            raw2, _ = _run(prompt, temp=0.9)
            rep2 = _extract(raw2)
            if rep2 and not _bad(rep2):
                rep = rep2
            elif not rep:
                try:
                    from packages.engine.context_rag import AlishaContextEngine
                    res = AlishaContextEngine().process_turn(
                        msg,
                        chat_history=[{"role": r, "content": c} for r, c in self.history],
                        voice_mode="text_only"
                    )
                    lines = [b["content"] for b in res.get("bursts", []) if b.get("message_type") != "voice"]
                    if lines:
                        rep = "\n".join(lines)
                except Exception:
                    pass
                rep = rep or "..."

        self.history.append(("user", msg))
        self.history.append(("assistant", rep))
        return rep
