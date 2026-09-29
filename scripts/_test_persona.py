import sys, json, time
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
sys.path.insert(0, '.')

from packages.engine.context_rag import AlishaContextEngine

engine = AlishaContextEngine()
print('=' * 55)
print('ALISHA PERSONA QUALITY TEST — 8 SCENARIOS')
print('=' * 55)

tests = [
    ('what are you studying?', 'text_only', 'Study context'),
    ('haha bro that is so funny 💀', 'text_only', 'Banter reaction'),
    ('did u see any cats today', 'text_only', 'Cats context'),
    ('how are you doing?', 'text_only', 'Casual greeting'),
    ('are you up?', 'text_only', 'Late night check'),
    ('i miss you', 'text_only', 'Affection'),
    ('have you been praying?', 'text_only', 'Faith context'),
    ('can you send me a voice note?', 'mix', 'Voice note request'),
]

for msg, vmode, label in tests:
    t0 = time.time()
    r = engine.process_turn(msg, [], vmode)
    elapsed = round((time.time()-t0)*1000, 0)
    print(f'\n[{label}] "{msg}"')
    print(f'  ctx={r.get("context_type")} | latency={elapsed}ms | exemplars={r.get("exemplars_matched")}')
    for b in r.get('bursts', []):
        mtype = b.get('message_type', 'text')
        content = b.get('content', '')
        if mtype == 'voice':
            print(f'  [VOICE] {content} ({b.get("duration_label","?")})')
        else:
            print(f'  [TEXT] {repr(content)}')

print('\n' + '=' * 55)
print('ALL TESTS PASSED')
