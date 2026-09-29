import sys, json
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
sys.path.insert(0, '.')

from packages.engine.context_rag import AlishaContextEngine

engine = AlishaContextEngine()
print('Engine loaded OK')

# Test 1: study context
r = engine.process_turn('what are you studying?', [], 'text_only')
print(f'\n[Test 1] Studying question:')
print(f'  context_type: {r.get("context_type")}')
print(f'  exemplars: {r.get("exemplars_matched")}')
print(f'  diag: {r.get("diagnostics")}')
for b in r.get('bursts', []):
    print(f'  [{b["message_type"]}]: {repr(b["content"])}')

# Test 2: banter context
r2 = engine.process_turn('bro that is insane 💀', [], 'text_only')
print(f'\n[Test 2] Banter:')
print(f'  context_type: {r2.get("context_type")}')
for b in r2.get('bursts', []):
    print(f'  [{b["message_type"]}]: {repr(b["content"])}')

# Test 3: cat context
r3 = engine.process_turn('omg did you see any cats today', [], 'text_only')
print(f'\n[Test 3] Cats:')
print(f'  context_type: {r3.get("context_type")}')
for b in r3.get('bursts', []):
    print(f'  [{b["message_type"]}]: {repr(b["content"])}')

# Test 4: casual
r4 = engine.process_turn('how are you?', [], 'text_only')
print(f'\n[Test 4] Casual:')
print(f'  context_type: {r4.get("context_type")}')
for b in r4.get('bursts', []):
    print(f'  [{b["message_type"]}]: {repr(b["content"])}')

print('\nDONE')
