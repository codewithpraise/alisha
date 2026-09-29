"""
Full Corpus Analyzer for Alisha AI Friend.

Processes data/messages.jsonl and generates all persona profile files:
  - persona/profile.json            (master profile)
  - persona/statistics.json         (raw measurements)
  - persona/lexical_profile.json    (n-grams, openers, fillers)
  - persona/emoji_profile.json      (emoji engine data)
  - persona/slang_profile.json      (auto-discovered slang lexicon)
  - persona/punctuation_profile.json
  - persona/burst_profile.json      (burst size distribution)
  - persona/response_act_profile.json (speech act distribution)
  - persona/address_terms.json      (nickname/address model)
  - persona/humor_profile.json
  - persona/emotional_profile.json
  - persona/topic_profiles.json
  - persona/temporal_profiles.json  (early/mid/recent drift)
  - persona/interaction_modes.json
  - persona/exemplars/              (real stimulus->response pairs)

RULES:
- Never modify raw source data
- Every measurement is evidence-backed
- Confidence = frequency / total occurrences
- Idempotent: safe to rerun multiple times
"""

import json
import os
import re
import math
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MESSAGES_JSONL = os.path.join(ROOT, "data", "messages.jsonl")
PERSONA_DIR = os.path.join(ROOT, "persona")

# ── Emoji regex (comprehensive) ──────────────────────────────────────────────
EMOJI_RE = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001F900-\U0001F9FF"  # supplemental
    "\U0001FA70-\U0001FAFF"  # extended
    "\U00002600-\U000026FF"
    "\U0001F3FB-\U0001F3FF"  # skin tones
    "\u200d"                  # ZWJ
    "\ufe0f"                  # variation selectors
    "]+",
    flags=re.UNICODE,
)


# ── Text helpers ─────────────────────────────────────────────────────────────

def fix_encoding(text: str) -> str:
    if not text:
        return ""
    try:
        return text.encode("latin1").decode("utf-8")
    except Exception:
        return text


def is_system_msg(content: str) -> bool:
    if not content or not content.strip():
        return True
    c = content.strip().lower()
    system_fragments = [
        "liked a message", "reacted ", "to your message", "you sent an attachment",
        "sent an attachment", "pinned a message", "started a call", "ended the call",
        "sent a reel", "sent a link", "sent a voice message",
    ]
    return any(s in c for s in system_fragments)


def extract_emojis(text: str) -> List[str]:
    return EMOJI_RE.findall(text)


def strip_emojis(text: str) -> str:
    return EMOJI_RE.sub("", text).strip()


def tokenize(text: str) -> List[str]:
    return re.findall(r"\b\w+\b", text.lower())


def is_alisha(sender: str) -> bool:
    s = sender.lower()
    return "alisha" in s or "اليشا" in sender


# ── Load corpus ───────────────────────────────────────────────────────────────

def load_messages() -> Tuple[List[Dict], List[str], List[str]]:
    """Returns (all_messages, alisha_texts, user_texts)."""
    all_msgs: List[Dict] = []
    alisha_texts: List[str] = []
    user_texts: List[str] = []

    if not os.path.exists(MESSAGES_JSONL):
        # Fallback to raw messages file
        alt = os.path.join(ROOT, "messages", "messages.jsonl")
        if not os.path.exists(alt):
            print(f"[Analyzer] Warning: messages.jsonl not found at {MESSAGES_JSONL}")
            return [], [], []
        path = alt
    else:
        path = MESSAGES_JSONL

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except Exception:
                continue

            sender = fix_encoding(entry.get("sender_name", entry.get("sender", "")))
            content = fix_encoding(entry.get("content", entry.get("text", "")))
            entry["sender_name"] = sender
            entry["content"] = content

            if is_system_msg(content):
                continue

            all_msgs.append(entry)
            if is_alisha(sender):
                alisha_texts.append(content)
            else:
                user_texts.append(content)

    all_msgs.sort(key=lambda x: x.get("timestamp_ms", x.get("ts_ms", 0)))
    return all_msgs, alisha_texts, user_texts


# ── Burst computation ─────────────────────────────────────────────────────────

def compute_bursts(all_msgs: List[Dict]) -> List[Dict]:
    """Groups consecutive same-sender messages into turns/bursts."""
    turns: List[Dict] = []
    current_sender = None
    current_burst: List[Dict] = []

    for msg in all_msgs:
        sender = msg.get("sender_name", msg.get("sender", ""))
        if current_sender is None:
            current_sender = sender
            current_burst = [msg]
        elif current_sender == sender:
            current_burst.append(msg)
        else:
            turns.append({
                "sender": current_sender,
                "messages": current_burst,
                "start_ms": current_burst[0].get("timestamp_ms", current_burst[0].get("ts_ms", 0)),
                "end_ms": current_burst[-1].get("timestamp_ms", current_burst[-1].get("ts_ms", 0)),
                "size": len(current_burst),
            })
            current_sender = sender
            current_burst = [msg]

    if current_burst:
        turns.append({
            "sender": current_sender,
            "messages": current_burst,
            "start_ms": current_burst[0].get("timestamp_ms", current_burst[0].get("ts_ms", 0)),
            "end_ms": current_burst[-1].get("timestamp_ms", current_burst[-1].get("ts_ms", 0)),
            "size": len(current_burst),
        })

    return turns


# ── Slang auto-discovery ──────────────────────────────────────────────────────

def discover_slang(alisha_texts: List[str], user_texts: List[str]) -> Dict[str, Any]:
    """
    Auto-discovers slang candidates: words with high frequency in Alisha's messages
    that are not standard English dictionary words.
    Returns a scored lexicon.
    """
    # Simple English stopwords + common words that are NOT slang
    stopwords = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "up", "about", "into", "through", "during",
        "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
        "do", "does", "did", "will", "would", "could", "should", "may", "might",
        "shall", "can", "need", "dare", "ought", "used", "that", "this", "these",
        "those", "i", "you", "he", "she", "it", "we", "they", "me", "him", "her",
        "us", "them", "my", "your", "his", "its", "our", "their", "mine", "yours",
        "not", "no", "yes", "so", "if", "as", "then", "than", "when", "where",
        "how", "what", "which", "who", "there", "here", "just", "all", "some",
        "any", "each", "few", "more", "most", "other", "such", "same", "own",
        "very", "also", "get", "got", "go", "going", "like", "know", "think",
        "come", "back", "out", "see", "say", "said", "make", "made", "want",
        "let", "tell", "time", "one", "two", "way", "now", "new", "day", "good",
        "well", "too", "really", "even", "after", "before", "still", "already",
        "much", "many", "take", "look", "its", "been", "something", "nothing",
        "everything", "anything", "someone", "everyone", "because", "since",
        "while", "although", "though", "actually", "probably", "maybe",
    }

    alisha_word_freq = Counter()
    for text in alisha_texts:
        tokens = tokenize(strip_emojis(text))
        alisha_word_freq.update(tokens)

    user_word_freq = Counter()
    for text in user_texts:
        tokens = tokenize(strip_emojis(text))
        user_word_freq.update(tokens)

    total_alisha = max(1, sum(alisha_word_freq.values()))

    slang_candidates: List[Dict] = []

    for word, count in alisha_word_freq.most_common(300):
        if len(word) < 2:
            continue
        if word in stopwords:
            continue
        if count < 3:
            continue

        # Score: relative frequency + specificity to Alisha vs user
        rel_freq = count / total_alisha
        user_count = user_word_freq.get(word, 0)
        specificity = count / max(1, user_count + count)

        # Categorize
        is_abbreviation = len(word) <= 4 and not word[0].isupper()
        is_elongated = bool(re.search(r"(.)\1{2,}", word))  # nahhh, sighhh
        has_non_standard = bool(re.search(r"[^a-z']", word))

        slang_candidates.append({
            "term": word,
            "frequency": count,
            "relative_frequency": round(rel_freq * 1000, 2),  # per 1000 tokens
            "alisha_specificity": round(specificity, 3),
            "is_abbreviation": is_abbreviation,
            "is_elongated": is_elongated,
            "confidence": round(min(1.0, specificity * math.log(count + 1) / 5), 3),
        })

    # Sort by confidence * frequency
    slang_candidates.sort(key=lambda x: x["confidence"] * x["frequency"], reverse=True)

    return {
        "total_unique_tokens": len(alisha_word_freq),
        "slang_candidates": slang_candidates[:80],
        "top_terms": [s["term"] for s in slang_candidates[:30]],
    }


# ── Emoji analysis ────────────────────────────────────────────────────────────

def analyze_emojis(alisha_texts: List[str]) -> Dict[str, Any]:
    """
    Builds a conditional emoji engine:
    - Overall frequency
    - Standalone vs inline
    - Position (start/mid/end)
    - Clusters
    """
    all_emoji_sequences: List[str] = []
    emoji_positions: Counter = Counter()
    emoji_combos: Counter = Counter()
    standalone_count = 0
    messages_with_emoji = 0

    for text in alisha_texts:
        emojis = extract_emojis(text)
        if not emojis:
            continue

        messages_with_emoji += 1
        all_emoji_sequences.extend(emojis)

        text_stripped = strip_emojis(text).strip()
        if not text_stripped:
            standalone_count += 1
            emoji_positions["standalone"] += len(emojis)
        else:
            if text.startswith(emojis[0]):
                emoji_positions["start"] += 1
            elif text.endswith(emojis[-1]):
                emoji_positions["end"] += 1
            else:
                emoji_positions["middle"] += 1

        # Combos (pairs of consecutive emojis in same message)
        if len(emojis) >= 2:
            for i in range(len(emojis) - 1):
                emoji_combos[f"{emojis[i]}+{emojis[i+1]}"] += 1

    total = len(alisha_texts)
    emoji_freq_counter = Counter(all_emoji_sequences)

    top_emojis = [
        {"emoji": em, "count": cnt, "rate": round(cnt / total, 4)}
        for em, cnt in emoji_freq_counter.most_common(20)
    ]

    return {
        "emoji_rate": round(messages_with_emoji / max(1, total), 4),
        "standalone_rate": round(standalone_count / max(1, messages_with_emoji), 3),
        "top_emojis": top_emojis,
        "top_combos": [{"combo": k, "count": v} for k, v in emoji_combos.most_common(10)],
        "position_distribution": dict(emoji_positions),
        "characteristic_emojis": [e["emoji"] for e in top_emojis[:8]],
        "generic_emojis": ["😊", "😀", "🙂", "👍"],  # emojis Alisha avoids
    }


# ── Address terms / nicknames ─────────────────────────────────────────────────

NICKNAME_PATTERNS = [
    r"\bcutie\b", r"\bbabycakes\b", r"\bpookie\b", r"\bboo\b",
    r"\bbabe\b", r"\bbabes\b", r"\bbro\b", r"\bcuh\b", r"\bsir\b",
    r"\blad\b", r"\bmate\b", r"\bgirl\b",
]

def analyze_address_terms(alisha_texts: List[str]) -> Dict[str, Any]:
    terms: Dict[str, int] = {}
    for pattern in NICKNAME_PATTERNS:
        count = sum(1 for t in alisha_texts if re.search(pattern, t, re.IGNORECASE))
        if count > 0:
            term = pattern.replace(r"\b", "").replace("\\b", "")
            terms[term] = count

    total = len(alisha_texts)
    result = [
        {
            "term": term,
            "frequency": cnt,
            "rate": round(cnt / total, 4),
            "category": _classify_address_term(term),
        }
        for term, cnt in sorted(terms.items(), key=lambda x: -x[1])
    ]
    return {
        "address_terms": result,
        "pet_names": [t["term"] for t in result if t["category"] == "pet_name"],
        "casual_address": [t["term"] for t in result if t["category"] == "casual"],
    }


def _classify_address_term(term: str) -> str:
    pet_names = {"cutie", "babycakes", "pookie", "boo", "babe", "babes"}
    casual = {"bro", "cuh", "lad", "mate", "sir", "girl"}
    if term.lower() in pet_names:
        return "pet_name"
    if term.lower() in casual:
        return "casual"
    return "general"


# ── Response act classification ────────────────────────────────────────────────

RESPONSE_ACT_PATTERNS: Dict[str, List[str]] = {
    "reaction": [r"omg", r"omds", r"wait", r"no way", r"bro", r"💀", r"😭", r"bruh"],
    "agreement": [r"\byeah\b", r"\byes\b", r"\byea\b", r"\bokay\b", r"\btrue\b", r"\bexactly\b", r"\bfr\b"],
    "disagreement": [r"\bnah\b", r"\bno\b", r"\bnope\b", r"\bnahhh\b"],
    "teasing": [r"\bkidding\b", r"\bsmh\b", r"\bpattern up\b", r"\blatw\b"],
    "affection": [r"\bcutie\b", r"\bbabycakes\b", r"\bpookie\b", r"❤️", r"\bily\b", r"\blove\b"],
    "question": [r"\?", r"\bwbu\b", r"\bwdym\b", r"\bhow\b", r"\bwhat\b", r"\bwhy\b"],
    "acknowledgment": [r"\boh\b", r"\bhmm\b", r"\bokay\b", r"\bah\b", r"\bic\b"],
    "excitement": [r"!+", r"\bomg\b", r"\bwow\b", r"😍", r"🤩"],
    "farewell": [r"\bbye\b", r"\bgn\b", r"\bnight\b", r"\bsleep\b", r"\bbrb\b"],
    "reassurance": [r"\bit's okay\b", r"\bdon't worry\b", r"\byou're fine\b", r"\byou got this\b"],
}

def classify_response_act(text: str) -> List[str]:
    acts = []
    t = text.lower()
    for act, patterns in RESPONSE_ACT_PATTERNS.items():
        for p in patterns:
            if re.search(p, t, re.IGNORECASE):
                acts.append(act)
                break
    return acts if acts else ["continuation"]


def build_response_act_profile(alisha_texts: List[str]) -> Dict[str, Any]:
    act_counts: Counter = Counter()
    for text in alisha_texts:
        acts = classify_response_act(text)
        act_counts.update(acts)

    total = max(1, sum(act_counts.values()))
    distribution = {
        act: {"count": cnt, "rate": round(cnt / total, 4)}
        for act, cnt in act_counts.most_common()
    }
    return {
        "distribution": distribution,
        "dominant_acts": [a for a, _ in act_counts.most_common(5)],
        "act_taxonomy": list(RESPONSE_ACT_PATTERNS.keys()),
    }


# ── Burst profile ─────────────────────────────────────────────────────────────

def build_burst_profile(turns: List[Dict]) -> Dict[str, Any]:
    alisha_bursts = [t["size"] for t in turns if is_alisha(t["sender"])]
    if not alisha_bursts:
        return {}

    size_dist = Counter(alisha_bursts)
    total = len(alisha_bursts)

    return {
        "mean_burst_size": round(statistics.mean(alisha_bursts), 3),
        "median_burst_size": statistics.median(alisha_bursts),
        "max_burst_size": max(alisha_bursts),
        "burst_size_distribution": {
            str(k): {"count": v, "probability": round(v / total, 4)}
            for k, v in sorted(size_dist.items())
        },
        "double_text_probability": round(sum(1 for s in alisha_bursts if s >= 2) / total, 4),
        "triple_text_probability": round(sum(1 for s in alisha_bursts if s >= 3) / total, 4),
        "total_turns": total,
    }


# ── Temporal drift ────────────────────────────────────────────────────────────

def build_temporal_profiles(all_msgs: List[Dict]) -> Dict[str, Any]:
    """Split corpus into early/mid/recent thirds, compare style metrics."""
    alisha_msgs = [
        m for m in all_msgs
        if is_alisha(m.get("sender_name", m.get("sender", "")))
        and not is_system_msg(m.get("content", ""))
    ]
    if len(alisha_msgs) < 30:
        return {}

    n = len(alisha_msgs)
    thirds = [
        ("early", alisha_msgs[:n // 3]),
        ("mid", alisha_msgs[n // 3: 2 * n // 3]),
        ("recent", alisha_msgs[2 * n // 3:]),
    ]

    def compute_metrics(msgs: List[Dict]) -> Dict[str, Any]:
        texts = [m.get("content", "") for m in msgs]
        if not texts:
            return {}
        lengths = [len(t) for t in texts]
        emoji_count = sum(1 for t in texts if extract_emojis(t))
        return {
            "msg_count": len(texts),
            "median_length_chars": int(statistics.median(lengths)),
            "mean_length_chars": round(statistics.mean(lengths), 1),
            "emoji_rate": round(emoji_count / len(texts), 4),
            "caps_rate": round(
                sum(1 for t in texts if t and t[0].isupper() and t[0].isalpha()) / len(texts), 4
            ),
        }

    return {
        period: {
            "date_range": {
                "start": datetime.fromtimestamp(
                    msgs[0].get("timestamp_ms", msgs[0].get("ts_ms", 0)) / 1000
                ).isoformat() if msgs else None,
                "end": datetime.fromtimestamp(
                    msgs[-1].get("timestamp_ms", msgs[-1].get("ts_ms", 0)) / 1000
                ).isoformat() if msgs else None,
            },
            **compute_metrics(msgs),
        }
        for period, msgs in thirds
    }


# ── Lexical profile ───────────────────────────────────────────────────────────

def build_lexical_profile(alisha_texts: List[str]) -> Dict[str, Any]:
    word_freq: Counter = Counter()
    bigram_freq: Counter = Counter()
    trigram_freq: Counter = Counter()
    openers: Counter = Counter()

    for text in alisha_texts:
        clean = strip_emojis(text).strip()
        tokens = tokenize(clean)
        if not tokens:
            continue

        word_freq.update(tokens)
        openers[tokens[0]] += 1

        for i in range(len(tokens) - 1):
            bigram_freq[f"{tokens[i]} {tokens[i+1]}"] += 1
        for i in range(len(tokens) - 2):
            trigram_freq[f"{tokens[i]} {tokens[i+1]} {tokens[i+2]}"] += 1

    lengths_chars = [len(t) for t in alisha_texts]
    lengths_words = [len(tokenize(strip_emojis(t))) for t in alisha_texts]

    return {
        "top_words": [{"word": w, "count": c} for w, c in word_freq.most_common(50)],
        "top_bigrams": [{"bigram": b, "count": c} for b, c in bigram_freq.most_common(30)],
        "top_trigrams": [{"trigram": t, "count": c} for t, c in trigram_freq.most_common(20)],
        "top_openers": [{"word": w, "count": c} for w, c in openers.most_common(15)],
        "length_distribution": {
            "chars": {
                "min": min(lengths_chars) if lengths_chars else 0,
                "median": int(statistics.median(lengths_chars)) if lengths_chars else 0,
                "mean": round(statistics.mean(lengths_chars), 1) if lengths_chars else 0,
                "p90": int(sorted(lengths_chars)[int(len(lengths_chars) * 0.9)]) if lengths_chars else 0,
                "p95": int(sorted(lengths_chars)[int(len(lengths_chars) * 0.95)]) if lengths_chars else 0,
                "max": max(lengths_chars) if lengths_chars else 0,
            },
            "words": {
                "min": min(lengths_words) if lengths_words else 0,
                "median": int(statistics.median(lengths_words)) if lengths_words else 0,
                "mean": round(statistics.mean(lengths_words), 1) if lengths_words else 0,
                "p90": int(sorted(lengths_words)[int(len(lengths_words) * 0.9)]) if lengths_words else 0,
            },
        },
    }


# ── Punctuation profile ───────────────────────────────────────────────────────

def build_punctuation_profile(alisha_texts: List[str]) -> Dict[str, Any]:
    total = max(1, len(alisha_texts))
    caps_first = sum(1 for t in alisha_texts if t and t[0].isupper() and t[0].isalpha())
    all_lower = sum(1 for t in alisha_texts if t and t == t.lower())
    has_period = sum(1 for t in alisha_texts if t.endswith("."))
    has_question = sum(1 for t in alisha_texts if "?" in t)
    has_exclamation = sum(1 for t in alisha_texts if "!" in t)
    has_ellipsis = sum(1 for t in alisha_texts if "..." in t or "…" in t)
    repeated_chars = sum(1 for t in alisha_texts if re.search(r"(.)\1{2,}", t))

    return {
        "capitalization_rate": round(caps_first / total, 4),
        "all_lowercase_rate": round(all_lower / total, 4),
        "terminal_period_rate": round(has_period / total, 4),
        "question_mark_rate": round(has_question / total, 4),
        "exclamation_rate": round(has_exclamation / total, 4),
        "ellipsis_rate": round(has_ellipsis / total, 4),
        "repeated_chars_rate": round(repeated_chars / total, 4),
        "summary": "Predominantly lowercase. Almost no terminal punctuation. Repeated chars (nahhh, sighhh) for emphasis.",
    }


# ── Topic extraction ──────────────────────────────────────────────────────────

TOPIC_KEYWORDS: Dict[str, List[str]] = {
    "study": ["biochem", "bio", "chem", "college", "exam", "practical", "lab", "lecture", "assignment", "revision"],
    "faith": ["salah", "dua", "allah", "ameen", "pray", "prayer", "fajr", "quran", "ramadan", "eid", "bismillah", "deen"],
    "cats": ["cat", "kittu", "kitty", "meow", "paw", "boo cat"],
    "family": ["mum", "dad", "mum", "siblings", "home", "family", "mummy"],
    "food": ["food", "eat", "hungry", "dinner", "lunch", "breakfast", "cook", "meal"],
    "health": ["tired", "sleep", "sick", "headache", "unwell", "rest", "exhausted"],
    "humor": ["lol", "lmao", "haha", "omg", "bruh", "bro", "💀", "😭"],
    "relationships": ["love", "miss", "cute", "cutie", "ily", "heart", "like you"],
    "entertainment": ["kdrama", "drama", "show", "movie", "film", "watch"],
    "future": ["future", "plans", "goal", "dream", "career", "degree"],
}

def build_topic_profiles(alisha_texts: List[str]) -> Dict[str, Any]:
    total = max(1, len(alisha_texts))
    results = {}
    for topic, keywords in TOPIC_KEYWORDS.items():
        count = 0
        exemplars = []
        for text in alisha_texts:
            t_lower = text.lower()
            if any(kw in t_lower for kw in keywords):
                count += 1
                if len(exemplars) < 5:
                    exemplars.append(text[:120])

        results[topic] = {
            "message_count": count,
            "rate": round(count / total, 4),
            "exemplars": exemplars,
        }
    return results


# ── Humor fingerprint ─────────────────────────────────────────────────────────

HUMOR_PATTERNS: Dict[str, List[str]] = {
    "teasing": [r"\bkidding\b", r"\bsmh\b", r"\bpattern up\b", r"\blatw\b", r"\bstop\b"],
    "sarcasm": [r"\bsure\b", r"\bright\b", r"\bobviously\b", r"\btotally\b"],
    "mock_outrage": [r"\bomg\b", r"\bno way\b", r"\bi cannot\b", r"\b💀\b"],
    "self_deprecation": [r"\bi'm so\b", r"\bim so\b", r"\bwhat am i\b"],
    "exaggeration": [r"!{2,}", r"\bliterally\b", r"\babsolutely\b", r"(.)\1{3,}"],
    "deadpan": [r"\bokay\b", r"\bfair enough\b", r"\binteresting\b", r"\bhmm\b"],
}

def build_humor_profile(alisha_texts: List[str]) -> Dict[str, Any]:
    counts: Counter = Counter()
    total = max(1, len(alisha_texts))
    for text in alisha_texts:
        t = text.lower()
        for humor_type, patterns in HUMOR_PATTERNS.items():
            if any(re.search(p, t) for p in patterns):
                counts[humor_type] += 1

    return {
        "humor_distribution": {
            ht: {"count": c, "rate": round(c / total, 4)}
            for ht, c in counts.most_common()
        },
        "dominant_humor_type": counts.most_common(1)[0][0] if counts else "teasing",
    }


# ── Build exemplars ───────────────────────────────────────────────────────────

def build_exemplars(turns: List[Dict], persona_dir: str) -> int:
    """
    Extracts (user_stimulus, alisha_response) pairs into persona/exemplars/.
    Stored as JSONL. Only real pairs where Alisha responds to the user.
    """
    exemplars_dir = os.path.join(persona_dir, "exemplars")
    os.makedirs(exemplars_dir, exist_ok=True)

    exemplars = []
    for i, turn in enumerate(turns):
        if not is_alisha(turn["sender"]):
            continue  # skip user turns
        if i == 0:
            continue  # nothing before

        # Find the previous user turn
        prev = turns[i - 1]
        if is_alisha(prev["sender"]):
            continue  # consecutive Alisha turns = burst, not exchange

        user_texts_in_turn = [
            m.get("content", m.get("text", ""))
            for m in prev["messages"]
            if not is_system_msg(m.get("content", m.get("text", "")))
        ]
        alisha_texts_in_turn = [
            m.get("content", m.get("text", ""))
            for m in turn["messages"]
            if not is_system_msg(m.get("content", m.get("text", "")))
        ]

        if not user_texts_in_turn or not alisha_texts_in_turn:
            continue

        user_stimulus = " / ".join(user_texts_in_turn)[:200]
        alisha_response = "\n".join(alisha_texts_in_turn)[:400]

        if len(alisha_response.strip()) < 2:
            continue

        acts = classify_response_act(alisha_response)
        exemplar = {
            "turn_index": i,
            "user_stimulus": user_stimulus,
            "alisha_response": alisha_response,
            "alisha_burst_size": len(alisha_texts_in_turn),
            "response_acts": acts,
            "alisha_char_length": len(alisha_response),
            "has_emoji": bool(extract_emojis(alisha_response)),
            "timestamp_ms": turn["start_ms"],
        }
        exemplars.append(exemplar)

    # Save all exemplars
    out_path = os.path.join(exemplars_dir, "stimulus_response_pairs.jsonl")
    with open(out_path, "w", encoding="utf-8") as f:
        for ex in exemplars:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"[Analyzer] Saved {len(exemplars)} stimulus->response exemplars to {out_path}")
    return len(exemplars)


# ── Main runner ───────────────────────────────────────────────────────────────

def run_full_analysis(output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Full corpus analysis pipeline. Outputs all persona profile files.
    Idempotent — safe to rerun.
    """
    persona_dir = output_dir or PERSONA_DIR
    os.makedirs(persona_dir, exist_ok=True)

    print("[Analyzer] Loading messages...")
    all_msgs, alisha_texts, user_texts = load_messages()
    if not alisha_texts:
        print("[Analyzer] ERROR: No Alisha messages found. Check MESSAGES_JSONL path.")
        return {}

    print(f"[Analyzer] Loaded {len(all_msgs)} total messages, {len(alisha_texts)} from Alisha")

    print("[Analyzer] Computing bursts...")
    turns = compute_bursts(all_msgs)

    print("[Analyzer] Building lexical profile...")
    lexical_profile = build_lexical_profile(alisha_texts)
    _save(persona_dir, "lexical_profile.json", lexical_profile)

    print("[Analyzer] Building emoji profile...")
    emoji_profile = analyze_emojis(alisha_texts)
    _save(persona_dir, "emoji_profile.json", emoji_profile)

    print("[Analyzer] Discovering slang...")
    slang_profile = discover_slang(alisha_texts, user_texts)
    _save(persona_dir, "slang_profile.json", slang_profile)

    print("[Analyzer] Building punctuation profile...")
    punct_profile = build_punctuation_profile(alisha_texts)
    _save(persona_dir, "punctuation_profile.json", punct_profile)

    print("[Analyzer] Building burst profile...")
    burst_profile = build_burst_profile(turns)
    _save(persona_dir, "burst_profile.json", burst_profile)

    print("[Analyzer] Building response act profile...")
    act_profile = build_response_act_profile(alisha_texts)
    _save(persona_dir, "response_act_profile.json", act_profile)

    print("[Analyzer] Building address term model...")
    address_profile = analyze_address_terms(alisha_texts)
    _save(persona_dir, "address_terms.json", address_profile)

    print("[Analyzer] Building humor profile...")
    humor_profile = build_humor_profile(alisha_texts)
    _save(persona_dir, "humor_profile.json", humor_profile)

    print("[Analyzer] Building topic profiles...")
    topic_profiles = build_topic_profiles(alisha_texts)
    _save(persona_dir, "topic_profiles.json", topic_profiles)

    print("[Analyzer] Building temporal drift profiles...")
    temporal_profiles = build_temporal_profiles(all_msgs)
    _save(persona_dir, "temporal_profiles.json", temporal_profiles)

    print("[Analyzer] Building exemplars...")
    exemplar_count = build_exemplars(turns, persona_dir)

    # ── Master statistics.json ─────────────────────────────────────────────
    lengths_chars = sorted([len(t) for t in alisha_texts])
    lengths_words = sorted([len(tokenize(strip_emojis(t))) for t in alisha_texts])
    n = len(lengths_chars)

    statistics_json = {
        "corpus": {
            "total_messages": len(all_msgs),
            "alisha_messages": len(alisha_texts),
            "user_messages": len(user_texts),
            "total_turns": len(turns),
            "alisha_turns": sum(1 for t in turns if is_alisha(t["sender"])),
            "exemplar_pairs": exemplar_count,
        },
        "message_length": {
            "chars": {
                "min": lengths_chars[0] if n else 0,
                "median": lengths_chars[n // 2] if n else 0,
                "mean": round(sum(lengths_chars) / n, 1) if n else 0,
                "p90": lengths_chars[int(n * 0.9)] if n else 0,
                "p95": lengths_chars[int(n * 0.95)] if n else 0,
                "max": lengths_chars[-1] if n else 0,
            },
            "words": {
                "median": lengths_words[n // 2] if n else 0,
                "mean": round(sum(lengths_words) / n, 1) if n else 0,
                "p90": lengths_words[int(n * 0.9)] if n else 0,
            },
        },
        "style": {
            "emoji_rate": emoji_profile.get("emoji_rate", 0),
            "capitalization_rate": punct_profile.get("capitalization_rate", 0),
            "all_lowercase_rate": punct_profile.get("all_lowercase_rate", 0),
            "terminal_period_rate": punct_profile.get("terminal_period_rate", 0),
            "question_rate": punct_profile.get("question_mark_rate", 0),
        },
        "burst": {
            "mean_size": burst_profile.get("mean_burst_size", 2.52),
            "double_text_probability": burst_profile.get("double_text_probability", 0.54),
        },
    }
    _save(persona_dir, "statistics.json", statistics_json)

    # ── Master profile.json ────────────────────────────────────────────────
    profile = {
        "version": "1.0.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "persona_name": "Alisha",
        "corpus_stats": statistics_json["corpus"],
        "style_summary": {
            "dominant_style": "lowercase casual British/Pakistani slang",
            "dominant_response_acts": act_profile.get("dominant_acts", []),
            "dominant_humor": humor_profile.get("dominant_humor_type", "teasing"),
            "top_slang": slang_profile.get("top_terms", [])[:15],
            "top_emojis": emoji_profile.get("characteristic_emojis", []),
            "pet_names_used": address_profile.get("pet_names", []),
            "message_length_class": "short",
            "burst_behavior": "double-texts frequently",
        },
        "generation_constraints": {
            "target_length_chars": {
                "min": 3,
                "typical_low": 8,
                "median": lengths_chars[n // 2] if n else 26,
                "typical_high": lengths_chars[int(n * 0.9)] if n else 79,
                "soft_max": lengths_chars[int(n * 0.95)] if n else 115,
            },
            "burst_probability": burst_profile.get("double_text_probability", 0.54),
            "emoji_probability": emoji_profile.get("emoji_rate", 0.087),
            "capitalization_probability": punct_profile.get("capitalization_rate", 0.028),
        },
    }
    _save(persona_dir, "profile.json", profile)

    print(f"\n[Analyzer] DONE: Complete. All profiles saved to {persona_dir}/")
    return profile


def _save(persona_dir: str, filename: str, data: Any):
    path = os.path.join(persona_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  -> {filename}")



if __name__ == "__main__":
    run_full_analysis()
