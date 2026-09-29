"""
Training Data Preparation for Qwen3.5-2B QLoRA Fine-Tuning.
Extracts clean, anti-assistant conversational pairs from messages/messages.jsonl
into ShareGPT format JSONL files for training on Kaggle.
"""

import json
import os
import random
import sys
from typing import List, Dict, Any

current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current_dir, ".."))
if root not in sys.path:
    sys.path.insert(0, root)

from packages.personality.fingerprint import fix_instagram_encoding, is_system_or_reaction


ANTI_ASSISTANT_REJECTIONS = [
    {
        "prompt": "you free?",
        "rejected": "Certainly! I am completely free and available to assist you with whatever you need. How can I help today?",
        "chosen": "yea",
    },
    {
        "prompt": "did you do that thing",
        "rejected": "I have processed your request. Please let me know if there is anything else you require.",
        "chosen": "nahhh\ni literally forgot 💀",
    },
    {
        "prompt": "why are you latw",
        "rejected": "I apologize sincerely for my delay. I encountered unforeseen circumstances.",
        "chosen": "not latw 😭\nstop making fun of my typos",
    },
    {
        "prompt": "where were you",
        "rejected": "I apologize for being away. I was attending to personal obligations.",
        "chosen": "was busy with mum errr",
    },
    {
        "prompt": "what song is that",
        "rejected": "That appears to be a song by Katy Perry titled 'Hot N Cold'. It was released in 2008.",
        "chosen": "hot and cold situation innit\nstill stuck in my head",
    },
]


def prepare_datasets(
    messages_path: str, output_dir: str, seed: int = 42
) -> Dict[str, Any]:
    os.makedirs(output_dir, exist_ok=True)

    with open(messages_path, "r", encoding="utf-8") as f:
        raw_lines = [json.loads(line) for line in f if line.strip()]

    raw_lines.sort(key=lambda x: x.get("timestamp_ms", 0))

    turns = []
    current_sender = None
    current_messages = []

    for item in raw_lines:
        sender = fix_instagram_encoding(item.get("sender_name", ""))
        content = fix_instagram_encoding(item.get("content", ""))

        if is_system_or_reaction(content):
            continue

        role = "alisha" if (sender == "اليشا" or "alisha" in sender.lower()) else "user"

        if current_sender is None:
            current_sender = role
            current_messages = [content]
        elif current_sender == role:
            current_messages.append(content)
        else:
            turns.append({"role": current_sender, "text": "\n".join(current_messages)})
            current_sender = role
            current_messages = [content]

    if current_messages:
        turns.append({"role": current_sender, "text": "\n".join(current_messages)})

    # Build pairs: user turn -> alisha turn
    conversation_samples = []
    for i in range(len(turns) - 1):
        if turns[i]["role"] == "user" and turns[i + 1]["role"] == "alisha":
            user_text = turns[i]["text"]
            alisha_text = turns[i + 1]["text"]

            # Context window of previous turn if available
            context_prefix = ""
            if i >= 2:
                prev_u = turns[i - 2]["text"]
                prev_a = turns[i - 1]["text"]
                context_prefix = f"Friend: {prev_u}\nAlisha: {prev_a}\n"

            sample = {
                "conversations": [
                    {
                        "from": "system",
                        "value": "You are Alisha (@iishazsr). Text naturally in lowercase, casual slang (innit, bro, ig), short fragments, and authentic emojis (💀, 😭, ❤️). Never sound like an AI assistant.",
                    },
                    {
                        "from": "human",
                        "value": (context_prefix + f"Friend: {user_text}").strip(),
                    },
                    {
                        "from": "gpt",
                        "value": alisha_text,
                    },
                ]
            }
            conversation_samples.append(sample)

    # Append anti-assistant examples
    for aa in ANTI_ASSISTANT_REJECTIONS:
        conversation_samples.append({
            "conversations": [
                {
                    "from": "system",
                    "value": "You are Alisha (@iishazsr). Text naturally in lowercase, casual slang (innit, bro, ig), short fragments, and authentic emojis (💀, 😭, ❤️). Never sound like an AI assistant.",
                },
                {"from": "human", "value": f"Friend: {aa['prompt']}"},
                {"from": "gpt", "value": aa["chosen"]},
            ]
        })

    rng = random.Random(seed)
    rng.shuffle(conversation_samples)

    n_total = len(conversation_samples)
    n_train = int(n_total * 0.80)
    n_val = int(n_total * 0.10)

    train_data = conversation_samples[:n_train]
    val_data = conversation_samples[n_train:n_train + n_val]
    test_data = conversation_samples[n_train + n_val:]

    def write_jsonl(path: str, data: List[Dict[str, Any]]):
        with open(path, "w", encoding="utf-8") as f:
            for d in data:
                f.write(json.dumps(d, ensure_ascii=False) + "\n")

    train_path = os.path.join(output_dir, "chat_train.jsonl")
    val_path = os.path.join(output_dir, "chat_val.jsonl")
    test_path = os.path.join(output_dir, "chat_test.jsonl")

    write_jsonl(train_path, train_data)
    write_jsonl(val_path, val_data)
    write_jsonl(test_path, test_data)

    print(f"Chat training dataset generated:")
    print(f"  Total pairs: {n_total}")
    print(f"  Train (80%): {len(train_data)} -> {train_path}")
    print(f"  Val   (10%): {len(val_data)} -> {val_path}")
    print(f"  Test  (10%): {len(test_data)} -> {test_path}")

    return {
        "total": n_total,
        "train": train_path,
        "val": val_path,
        "test": test_path,
    }


if __name__ == "__main__":
    msg_file = os.path.join(root, "messages", "messages.jsonl")
    out_dir = os.path.join(root, "data")
    prepare_datasets(msg_file, out_dir)
