#!/usr/bin/env python3
"""A first run of the like-for-like test John Kloppenborg proposed in his response to
Mark Goodacre's "Too Good to Be Q" (Marcan Priority without Q, 2015, pp. 242-243):

  Do Matthew and Luke agree with each other as closely in Mark's sayings strings,
  where both are known to copy Mark, as they do in the double tradition's sayings?

Data (not included here): the Synoptic Canvas project's public/data directory, which holds
  opengnt.json  OpenGNT 3.3 Greek text with lemmas, morphology, speech tagging and a word
                alignment of every Aland parallel (CC BY-SA 4.0); a link joins words with the
                same inflected form, ignoring accents
  net.json      Aland's parallel groups (github.com/cbop-dev/aland-gospel-synopsis)

Limits. OpenGNT is close to, but is not, the Nestle-Aland text. The alignment is automatic;
section 0 checks it against published counts. The extent of Q (QLIST) follows Kloppenborg,
Excavating Q (2000), p. 100, as reproduced at earlychristianwritings.com/q-contents.html:
the items he prints without brackets, at whole-verse precision. Section E repeats the test
without any Q list. Luke's woes (11:39-52) are only cross-referenced to Matthew 23 in the
Aland data, so they are aligned here by the same rule (SUPPLEMENT). Only identical inflected forms count as agreement, which is
stricter than Carlston and Norlin. The second half of Kloppenborg's proposal, a comparison
with ancient authors who used two sources, is not attempted.

Usage: python3 tools/kloppenborg_test.py <synoptic-canvas>/public/data > tools/kloppenborg_test.txt
"""
import json, re, sys, random, collections

D = sys.argv[1]
pack = json.load(open(f'{D}/opengnt.json'))
groups = json.load(open(f'{D}/net.json'))['groups']
align = pack['greekAlignment']['groups']

TOK = {}                       # id -> token record
VERSE = collections.defaultdict(list)   # (book, ch, v) -> [ids]
for b in pack['books']:
    for v in b['verses']:
        for t in v.get('greekTokens', []):
            kinds = {a['kind'] for a in v.get('annotations', []) if a['start'] < t['end'] and a['end'] > t['start']}
            TOK[t['id']] = dict(book=b['id'], ch=v['chapter'], v=v['verse'], text=v['text'][t['start']:t['end']],
                                jesus='jesus' in kinds, speech=bool(kinds & {'jesus', 'speech'}),
                                scripture='scripture' in kinds, gram=bool(re.match(r'(T-|CONJ|PREP|PRT|P-|R-|D-)', t['morphology'])))
            VERSE[(b['id'], v['chapter'], v['verse'])].append(t['id'])

# token -> set of books it is linked to (identical form) in any group
LINK = collections.defaultdict(set)
PARTNER = collections.defaultdict(dict)   # token -> {book: partner id}
for gid, a in align.items():
    for link in a['links']:
        for x in link:
            for y in link:
                if x != y:
                    LINK[x].add(TOK[y]['book']); PARTNER[x][TOK[y]['book']] = y

# Passages the Aland data set lists only as cross-references, so the canvas has no alignment
# for them. Aligned here by the same rule (identical forms): longest common runs first, then
# single content words that have exactly one free counterpart.
SUPPLEMENT = [('11:39-44, 46-52', '23:4, 6-7, 13, 23, 25-36')]      # the woes
import unicodedata
def formkey(t): return ''.join(c for c in unicodedata.normalize('NFD', t.lower()) if not unicodedata.combining(c) and c.isalpha()).replace('ς', 'σ')
def _ids(book, spec):
    out = []
    for part in spec.split(';'):
        ch, rest = part.strip().split(':')
        for r in rest.split(','):
            a, _, b = r.strip().partition('-')
            for v in range(int(a), int(b or a) + 1): out += VERSE[(book, int(ch), v)]
    return out
for lspec, mspec in SUPPLEMENT:
    L = _ids('luke', lspec); M = _ids('matthew', mspec); kl = [formkey(TOK[i]['text']) for i in L]; km = [formkey(TOK[i]['text']) for i in M]
    cands = []
    for a in range(len(L)):
        for b in range(len(M)):
            if kl[a] != km[b] or (a and b and kl[a - 1] == km[b - 1]): continue
            n = 0
            while a + n < len(L) and b + n < len(M) and kl[a + n] == km[b + n] and L[a + n] == L[a] + n and M[b + n] == M[b] + n: n += 1
            if n >= 2: cands.append((n, a, b))
    ua, ub, pairs = set(), set(), []
    for n, a, b in sorted(cands, reverse=True):
        if any(a + i in ua or b + i in ub for i in range(n)): continue
        for i in range(n): ua.add(a + i); ub.add(b + i); pairs.append((L[a + i], M[b + i]))
    for a in range(len(L)):
        if a in ua or TOK[L[a]]['gram'] or len(kl[a]) < 4: continue
        free = [b for b in range(len(M)) if b not in ub and km[b] == kl[a]]
        if len(free) == 1: ua.add(a); ub.add(free[0]); pairs.append((L[a], M[free[0]]))
    for l, m in pairs:
        LINK[l].add('matthew'); LINK[m].add('luke'); PARTNER[l]['matthew'] = m; PARTNER[m]['luke'] = l
SUPP = {('luke', TOK[i]['ch'], TOK[i]['v']) for lspec, _ in SUPPLEMENT for i in _ids('luke', lspec)}

# verse -> books with a passage in a shared Aland group
PAR = collections.defaultdict(set)
for g in groups:
    if not g['correspondence']: continue
    books = {p['book'] for p in g['passages']}
    for p in g['passages']:
        for ref in p['verses']:
            c, v = ref.split(':'); PAR[(p['book'], int(c), int(v))] |= books - {p['book']}
for k in SUPP: PAR[k].add('matthew')

def span(book, spec):
    """'3:7-9, 16-17; 6:20-49' -> list of verse keys."""
    out = []
    for part in spec.split(';'):
        ch, rest = part.strip().split(':')
        for r in rest.split(','):
            a, _, b = r.strip().partition('-')
            for v in range(int(a), int(b or a) + 1):
                if (book, int(ch), v) in VERSE: out.append((book, int(ch), v))
    return out

def rate(verses, other, only=None):
    """words in `verses` identical with an aligned word in `other` / all words."""
    ids = [i for k in verses for i in VERSE[k] if only is None or only(TOK[i])]
    hit = sum(1 for i in ids if other in LINK[i])
    return hit, len(ids)

def pct(h, n): return f'{h:5d}/{n:<5d} {100*h/n:5.1f}%' if n else '    0/0        -  '

def boot(units, other, only=None, B=4000, seed=1):
    """95% interval, resampling units (pericopes or runs of verses)."""
    rnd = random.Random(seed); per = [rate(u, other, only) for u in units]; per = [p for p in per if p[1]]
    if len(per) < 2: return (float('nan'),) * 2
    xs = []
    for _ in range(B):
        s = [rnd.choice(per) for _ in per]; xs.append(100 * sum(h for h, _ in s) / sum(n for _, n in s))
    xs.sort(); return xs[int(.025 * B)], xs[int(.975 * B)]

def longest(verses, other):
    """longest unbroken run of consecutive identical words (both sides consecutive)."""
    ids = [i for k in verses for i in VERSE[k]]; best = cur = 0; prev = None
    for i in ids:
        p = PARTNER[i].get(other)
        cur = cur + 1 if (p is not None and prev is not None and p == prev + 1) else (1 if p is not None else 0)
        prev = p; best = max(best, cur)
    return best

print('== 0. Check against published counts ==')
h, n = rate(span('luke', '3:7-9'), 'matthew'); print(f'Luke 3:7-9 identical with Matthew: {pct(h, n)}   (Kloppenborg: 61 of 72, 85%)')
h, n = rate(span('luke', '16:13'), 'matthew'); print(f'Luke 16:13:                        {pct(h, n)}   (Morgenthaler/Kloppenborg: 98%)')
h, n = rate(span('luke', '11:24-26'), 'matthew'); print(f'Luke 11:24-26:                     {pct(h, n)}   (93%)')
h, n = rate(span('luke', '10:13-15'), 'matthew'); print(f'Luke 10:13-15:                     {pct(h, n)}   (90%)')
h, n = rate(span('luke', '13:34-35'), 'matthew'); print(f'Luke 13:34-35:                     {pct(h, n)}   (85%)')

print('\n== A. The passages Kloppenborg names ==')
Q_STR = {'Luke 3:7-9, 16-17': '3:7-9, 16-17', 'Luke 6:20-49': '6:20-49', 'Luke 7:24-35': '7:24-35',
         'Luke 12:2-12': '12:2-12', 'Luke 12:22-34': '12:22-34'}
MK_STR = {'Luke 8:5-8, 10-18 (Mark 4:3-9, 11-25)': '8:5-8, 10-18', 'Luke 21:8-36 (Mark 13:5-37)': '21:8-36'}
print('Share of Luke\'s words identical with Matthew\'s:')
tq = [0, 0]; tm = [0, 0]
for name, s in Q_STR.items():
    h, n = rate(span('luke', s), 'matthew'); tq[0] += h; tq[1] += n; print(f'  Q string    {name:42s} {pct(h, n)}  longest run {longest(span("luke", s), "matthew")}')
for name, s in MK_STR.items():
    vs = span('luke', s); h, n = rate(vs, 'matthew'); tm[0] += h; tm[1] += n
    hk, _ = rate(vs, 'mark'); print(f'  Mark string {name:42s} {pct(h, n)}  longest run {longest(vs, "matthew")}   (identical with Mark: {100*hk/n:.1f}%)')
print(f'  Q strings together    {pct(*tq)}\n  Mark strings together {pct(*tm)}')

print('\nSame passages, from Mark\'s side (share of Mark\'s words kept unchanged):')
for name, s in {'Mark 4:3-9, 11-25': '4:3-9, 11-25', 'Mark 13:5-37': '13:5-37'}.items():
    ids = [i for k in span('mark', s) for i in VERSE[k]]; n = len(ids)
    m = sum('matthew' in LINK[i] for i in ids); l = sum('luke' in LINK[i] for i in ids); both = sum({'matthew', 'luke'} <= LINK[i] for i in ids)
    print(f'  {name:20s} words {n}: Matthew keeps {100*m/n:.1f}%, Luke keeps {100*l/n:.1f}%, both keep {100*both/n:.1f}% (independence would give {100*m*l/n/n:.1f}%)')

# ---- B. every saying of Jesus, by verse ----
QLIST = ('3:7-9, 16-17; 4:1-13; 6:20-23, 27-33, 35-49; 7:1-2, 6-10, 18-19, 22-28, 31-35; 9:57-60; 10:2-16, 21-24; '
         '11:2-4, 9-20, 23-26, 29-35, 39-44, 46-52; 12:2-12, 22-31, 33-34, 39-40, 42-46, 49, 51-56, 58-59; '
         '13:18-21, 24, 26-30, 34-35; 14:11, 16-24, 26-27, 34-35; 15:4-7; 16:13, 16-18; '
         '17:1-4, 6, 23-24, 26-27, 30, 33-35, 37; 19:12-13, 15-26; 22:28-30')
Q = set(span('luke', QLIST))

def jesus_share(k):
    ids = VERSE[k]; return sum(TOK[i]['jesus'] for i in ids) / len(ids)

luke = [k for k in VERSE if k[0] == 'luke']
def cls(k):
    mk_words = sum('mark' in LINK[i] for i in VERSE[k])
    if k in Q: return 'Q+Mark overlap' if ('mark' in PAR[k] and mk_words >= 3) else 'Q'
    if {'matthew', 'mark'} <= PAR[k]: return 'triple'
    if 'matthew' in PAR[k]: return 'double, not in Q list'
    return 'other'
CL = {k: cls(k) for k in luke}

def runs(keys):
    """group consecutive verses into runs."""
    out = []
    for k in sorted(keys, key=lambda k: (k[1], k[2])):
        if out and out[-1][-1][1] == k[1] and out[-1][-1][2] == k[2] - 1: out[-1].append(k)
        else: out.append([k])
    return out

print('\n== B. All of Luke, verses that are at least 80% words of Jesus ==')
print('Share of Luke\'s words identical with Matthew\'s, with a 95% interval from resampling runs of verses:')
say = [k for k in luke if jesus_share(k) >= .8]
allruns = runs(say)                      # runs of consecutive sayings verses, any class
runlen = {k: len(r) for r in allruns for k in r}
for label, test in [('all sayings verses', lambda k: True), ('in strings of 5+ verses', lambda k: runlen[k] >= 5), ('isolated, strings of 1-4', lambda k: runlen[k] < 5)]:
    print(f'  -- {label}')
    for c in ['Q', 'triple', 'Q+Mark overlap']:
        ks = [k for k in say if CL[k] == c and test(k)]
        h, n = rate(ks, 'matthew'); lo, hi = boot(runs(ks), 'matthew')
        hc, nc = rate(ks, 'matthew', only=lambda t: not t['gram'])
        hk, _ = rate(ks, 'mark')
        print(f'     {c:16s} verses {len(ks):4d}  {pct(h, n)}  [{lo:4.1f}, {hi:4.1f}]   content words only {100*hc/nc:4.1f}%   identical with Mark {100*hk/n:4.1f}%')

print('\n== C. Distribution: how many sayings strings reach high agreement ==')
for c in ['Q', 'triple']:
    rs = [r for r in runs([k for k in say if CL[k] == c]) if sum(len(VERSE[k]) for k in r) >= 40]
    xs = sorted((100 * rate(r, 'matthew')[0] / rate(r, 'matthew')[1], r) for r in rs)
    hi = [x for x in xs if x[0] >= 70]
    print(f'  {c:7s} strings of 40+ words: {len(xs)}; median {xs[len(xs)//2][0]:.0f}%; at 70% or more: {len(hi)}; at 50% or more: {sum(x[0]>=50 for x in xs)}')
    for p, r in xs[-4:]: print(f'        top: Luke {r[0][1]}:{r[0][2]}-{r[-1][2]}  {p:.0f}%')

print('\n== D. Narrative for comparison (verses under 20% words of Jesus) ==')
nar = [k for k in luke if jesus_share(k) < .2]
for c in ['Q', 'triple']:
    ks = [k for k in nar if CL[k] == c]; h, n = rate(ks, 'matthew'); print(f'     {c:16s} verses {len(ks):4d}  {pct(h, n)}')

json.dump({'classes': {f'{k[1]}:{k[2]}': CL[k] for k in luke}}, open(sys.argv[2], 'w')) if len(sys.argv) > 2 else None

# ---- E. robustness ----
def diff_boot(qs, ts, other='matthew', B=6000, seed=7):
    rnd = random.Random(seed); pq = [rate(u, other) for u in runs(qs)]; pt = [rate(u, other) for u in runs(ts)]
    def r(per):
        s = [rnd.choice(per) for _ in per]; return 100 * sum(h for h, _ in s) / sum(n for _, n in s)
    ds = sorted(r(pq) - r(pt) for _ in range(B))
    return ds[int(.025 * B)], ds[int(.975 * B)], sum(d <= 0 for d in ds) / B

QRUNS = runs([k for k in luke if CL[k] == 'Q' and jesus_share(k) >= .8])
print('\n== E. Robustness: Q minus triple, sayings of Jesus, points of Luke-Matthew agreement ==')
def variant(label, keep):
    qs = [k for k in luke if CL[k] == 'Q' and keep(k)]; ts = [k for k in luke if CL[k] == 'triple' and keep(k)]
    hq, nq = rate(qs, 'matthew'); ht, nt = rate(ts, 'matthew'); lo, hi, p = diff_boot(qs, ts)
    print(f'  {label:52s} Q {100*hq/nq:4.1f}% ({nq:4d} w)  triple {100*ht/nt:4.1f}% ({nt:4d} w)  diff {100*hq/nq-100*ht/nt:+5.1f} [{lo:+5.1f}, {hi:+5.1f}]  share of resamples <= 0: {p:.3f}')
variant('verses >= 80% Jesus (main)', lambda k: jesus_share(k) >= .8)
variant('verses 100% Jesus', lambda k: jesus_share(k) == 1)
variant('verses >= 50% Jesus', lambda k: jesus_share(k) >= .5)
variant('>= 80%, without Luke 21 (possible special source)', lambda k: jesus_share(k) >= .8 and k[1] != 21)
variant('>= 80%, without Luke 22-24 (passion)', lambda k: jesus_share(k) >= .8 and k[1] < 22)
variant('>= 80%, Q without the Sermon (Luke 6)', lambda k: jesus_share(k) >= .8 and k[1] != 6)
variant('>= 80%, Q without its 7 strings at 70%+', lambda k: jesus_share(k) >= .8 and not (CL[k] == 'Q' and any(k in r and rate(r, 'matthew')[0] / rate(r, 'matthew')[1] >= .7 and sum(len(VERSE[x]) for x in r) >= 40 for r in QRUNS)))

# auto-classified double tradition (Aland: Matthew parallel, no Mark parallel), ignoring the Q list
auto_q = [k for k in luke if jesus_share(k) >= .8 and 'matthew' in PAR[k] and 'mark' not in PAR[k]]
auto_t = [k for k in luke if jesus_share(k) >= .8 and {'matthew', 'mark'} <= PAR[k]]
hq, nq = rate(auto_q, 'matthew'); ht, nt = rate(auto_t, 'matthew'); lo, hi, p = diff_boot(auto_q, auto_t)
print(f"  {'Aland parallels alone, no Q list (overlaps in triple)':52s} Q {100*hq/nq:4.1f}% ({nq:4d} w)  triple {100*ht/nt:4.1f}% ({nt:4d} w)  diff {100*hq/nq-100*ht/nt:+5.1f} [{lo:+5.1f}, {hi:+5.1f}]  share of resamples <= 0: {p:.3f}")

print('\n== F. Each hypothesis read against Luke\'s and Matthew\'s known copying of Mark\'s sayings ==')
say_t = [k for k in luke if CL[k] == 'triple' and jesus_share(k) >= .8]; say_q = [k for k in luke if CL[k] == 'Q' and jesus_share(k) >= .8]
lm = rate(say_t, 'mark'); lmt = rate(say_t, 'matthew'); lq = rate(say_q, 'matthew')
print(f"  Luke, Markan sayings: identical with Mark {pct(*lm)}; identical with Matthew {pct(*lmt)}")
print(f"  Luke, Q sayings:      identical with Matthew {pct(*lq)}")
# Matthew side: verses that are sayings of Jesus, classed by their Lukan partners
mat = [k for k in VERSE if k[0] == 'matthew' and jesus_share(k) >= .8]
def mclass(k):
    partners = collections.Counter()
    for i in VERSE[k]:
        p = PARTNER[i].get('luke')
        if p is not None: t = TOK[p]; partners[CL[('luke', t['ch'], t['v'])]] += 1
    mk = sum('mark' in LINK[i] for i in VERSE[k])
    if partners['Q'] >= 2 and mk < 3: return 'Q'
    if {'luke', 'mark'} <= PAR[k] and mk >= 1 and partners['Q'] == 0: return 'triple'
    if 'mark' in PAR[k] and 'luke' not in PAR[k]: return 'mark-only'
    return 'other'
MC = {k: mclass(k) for k in mat}
for c in ['Q', 'triple', 'mark-only']:
    ks = [k for k in mat if MC[k] == c]; a = rate(ks, 'luke'); b = rate(ks, 'mark')
    print(f"  Matthew, {c:9s} sayings verses {len(ks):4d}: identical with Luke {pct(*a)}; identical with Mark {pct(*b)}")

print('\n== G. Three kinds of text, all of Luke (word level) ==')
for c in ['Q', 'triple']:
    ids = [i for k in luke if CL[k] == c for i in VERSE[k]]
    for lab, f in [('words of Jesus', lambda t: t['jesus']), ('other speech', lambda t: t['speech'] and not t['jesus']), ('narrator', lambda t: not t['speech'])]:
        sel = [i for i in ids if f(TOK[i])]; h = sum('matthew' in LINK[i] for i in sel)
        print(f"  {c:7s} {lab:15s} {pct(h, len(sel))}")

print('\n== H. Mark\'s words in the triple tradition: who keeps them ==')
mark3 = [k for k in VERSE if k[0] == 'mark' and {'matthew', 'luke'} <= PAR[k]]
for lab, f in [('all words', lambda t: True), ('words of Jesus', lambda t: t['jesus']), ('narrator', lambda t: not t['speech'])]:
    ids = [i for k in mark3 for i in VERSE[k] if f(TOK[i])]; n = len(ids)
    m = sum('matthew' in LINK[i] for i in ids); l = sum('luke' in LINK[i] for i in ids); b = sum({'matthew', 'luke'} <= LINK[i] for i in ids)
    print(f'  {lab:15s} {n:5d} words: Matthew keeps {100*m/n:4.1f}%, Luke keeps {100*l/n:4.1f}%, both keep {100*b/n:4.1f}%; independent choices would give {100*m*l/n/n:4.1f}%')

if len(sys.argv) > 3:   # optional: per-string figures as JSON, for charting
    out = []
    for c in ['Q', 'triple']:
        for r in runs([k for k in say if CL[k] == c]):
            h, n = rate(r, 'matthew')
            if n >= 40: out.append({'cls': c, 'ref': f'Luke {r[0][1]}:{r[0][2]}' + (f'-{r[-1][2]}' if len(r) > 1 else ''), 'words': n, 'pct': round(100 * h / n, 1)})
    json.dump(out, open(sys.argv[3], 'w'))
