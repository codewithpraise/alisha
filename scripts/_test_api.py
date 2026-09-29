import urllib.request, json, sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

payload = json.dumps({'message': 'what are you studying?', 'history': [], 'voice_mode': 'text_only'}).encode()
req = urllib.request.Request('http://localhost:8000/api/chat', data=payload, 
      headers={'Content-Type': 'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=30) as r:
    data = json.loads(r.read())

print('Context type:', data.get('context_type'))
print('Exemplars matched:', data.get('exemplars_matched'))
print('Diagnostics:', json.dumps(data.get('diagnostics'), indent=2))
print('Bursts:')
for b in data.get('bursts', []):
    mtype = b.get('message_type')
    content = b.get('content')
    print(f'  [{mtype}] {repr(content)}')
