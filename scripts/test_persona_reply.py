import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from packages.engine.context_rag import AlishaContextEngine

engine = AlishaContextEngine()

queries = [
    "what u studying",
    "im bored rn",
    "you're always latw",
    "can you send me a voice message"
]

for q in queries:
    res = engine.process_turn(q)
    print(f"\nUser: {q}")
    for b in res["bursts"]:
        if b["message_type"] == "voice":
            print(f"  [Alisha Voice Note]: {b.get('audio_url')} ({b.get('duration_label')})")
        else:
            print(f"  Alisha: {b['content']}")
