import json, re, sys
from collections import Counter, defaultdict
import random

ALISHA_NAME = 'petiue._.mon'
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

print('Loading messages...')
all_msgs = []
with open('data/messages.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            all_msgs.append(json.loads(line))
        except:
            pass

alisha_msgs = [m for m in all_msgs if m.get('sender_name') == ALISHA_NAME]
a_texts = [m['content'] for m in alisha_msgs if m.get('content','').strip()]
print(f'Alisha messages: {len(a_texts)}')

char_lens = sorted(len(t) for t in a_texts)
word_lens = sorted(len(t.split()) for t in a_texts)
n = len(char_lens)

def pct(lst, p):
    return lst[int(len(lst)*p)]

print(f'char median={pct(char_lens,0.5)} mean={round(sum(char_lens)/n,1)}')
print(f'char p25={pct(char_lens,0.25)} p75={pct(char_lens,0.75)} p90={pct(char_lens,0.9)} p95={pct(char_lens,0.95)} max={max(char_lens)}')
print(f'word median={pct(word_lens,0.5)} mean={round(sum(word_lens)/n,1)} p90={pct(word_lens,0.9)}')

very_short = Counter([t for t in a_texts if len(t)<=12])
print('Most common short replies:')
for txt,c in very_short.most_common(25):
    print(f'  {repr(txt)}: {c}')

openers = Counter()
for t in a_texts:
    words = re.findall(r'[a-zA-Z]+', t.lower())
    if words:
        openers[words[0]] += 1
print(f'Top 20 openers: {[w for w,_ in openers.most_common(20)]}')

burst_sizes = []
curr = 0
for m in all_msgs:
    s = m.get('sender_name','')
    if s == ALISHA_NAME:
        curr += 1
    else:
        if curr > 0:
            burst_sizes.append(curr)
            curr = 0
if curr:
    burst_sizes.append(curr)
bc = Counter(burst_sizes)
total = len(burst_sizes)
print(f'Burst dist: {dict(sorted(bc.items()))}')
print(f'Mean burst: {round(sum(burst_sizes)/total,2)}')

word_re = re.compile(r"[a-zA-Z']+")
all_words = []
for t in a_texts:
    all_words.extend(word_re.findall(t.lower()))
wf = Counter(all_words)
SLANG = ['innit','yea','nah','nahhh','latw','omg','bro','ig','literally',
         'wait','okay','lol','haha','tbh','ngl','idk','cutie','ily','ofc',
         'bruh','deadass','lowkey','slay','hmm','yeah','omg']
sf = {s: wf.get(s,0) for s in SLANG}
print(f'Slang freqs: {sf}')

STOPS = {'i','you','the','a','to','and','is','it','in','of','that','this',
         'was','for','on','are','with','he','she','they','we','what','so',
         'but','not','be','have','just','do','at','or','an','im','its','my',
         'your','me','no','yes','ok','can','dont','will','had','has','about',
         'when','all','one','there','if','would','which','who','then','like'}
top_vocab = [(w,c) for w,c in wf.most_common(100) if w not in STOPS and len(w)>1 and c>=5]
print(f'Top meaningful vocab: {top_vocab[:30]}')

print(f'Messages over 60 chars: {sum(1 for t in a_texts if len(t)>60)}')
print(f'Messages over 100 chars: {sum(1 for t in a_texts if len(t)>100)}')

random.seed(42)
long_msgs = [t for t in a_texts if len(t)>80]
random.shuffle(long_msgs)
print('Sample long messages (>80 chars):')
for t in long_msgs[:15]:
    print(f'  {repr(t)}')

EMOJI_RE = re.compile(
    r'[\U0001F300-\U0001F9FF\U00010000-\U0010FFFF\u2600-\u27BF\uFE00-\uFE0F]+',
    flags=re.UNICODE
)
emoji_counter = Counter()
for t in a_texts:
    for e in EMOJI_RE.findall(t):
        emoji_counter[e] += 1
print(f'Top emojis: {[e for e,_ in emoji_counter.most_common(20)]}')
msgs_with_emoji = sum(1 for t in a_texts if EMOJI_RE.search(t))
print(f'Emoji rate: {round(msgs_with_emoji/n,3)}')

bigrams = Counter()
for t in a_texts:
    words = word_re.findall(t.lower())
    for i in range(len(words)-1):
        bigrams[f'{words[i]} {words[i+1]}'] += 1
top_bigrams = [(b,c) for b,c in bigrams.most_common(40) if c>=4]
print(f'Top bigrams: {top_bigrams[:20]}')

# Specific Alisha phrases
print('\nSearching for key phrases:')
for phrase in ['bro i cannot','omg no','innit','latw','yea ig','wait no','no way','so busy','literally','biochem','bio chem','cat','kittu','dua','ameen','salah','mum','college','exam','lab']:
    count = sum(1 for t in a_texts if phrase.lower() in t.lower())
    print(f'  "{phrase}": {count}')

print('\nDONE')
