"""Unchanged E2 loader, features, classes and chunk definitions for E3.

DATA is supplied via E3_DATA by research_stylometry2.py (defaults to the specified read-only dataset).
"""
import contextlib, io, json, os, runpy, sys, unicodedata, collections
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get('E3_DATA', os.path.expanduser('~/Documents/ChatGPT/gospel/public/data'))

# ---------------------------------------------------------------- shared loader (reused)
_argv = sys.argv
sys.argv = [os.path.join(HERE, 'kloppenborg_test.py'), DATA]
with contextlib.redirect_stdout(io.StringIO()):
    K = runpy.run_path(os.path.join(HERE, 'kloppenborg_test.py'))
sys.argv = _argv
TOK, VERSE, LINK, PARTNER, PAR, CL = K['TOK'], K['VERSE'], K['LINK'], K['PARTNER'], K['PAR'], K['CL']
runs, Q, pack, groups = K['runs'], K['Q'], K['pack'], K['groups']

# lemma and Robinson morphology are not kept in TOK; read them from the same pack
MORPH, LEMMA = {}, {}
for b in pack['books']:
    for v in b['verses']:
        for t in v.get('greekTokens', []):
            MORPH[t['id']] = t['morphology']; LEMMA[t['id']] = t['lemma']


FUNC_PREFIX = {'T', 'CONJ', 'PREP', 'PRT', 'COND', 'ADV', 'P', 'R', 'D', 'C', 'X', 'I', 'Q', 'K', 'F', 'S', 'INJ'}

def strip(s): return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if not unicodedata.combining(c))

def raw_feature(i):
    """(feature, is_function_word) before rare pooling."""
    m = MORPH[i]; pre = m.split('-')[0]
    if pre in FUNC_PREFIX: return strip(LEMMA[i]), True
    if pre == 'N': return 'N', False
    if pre == 'A': return 'A', False
    if pre == 'V':                       # V-[2]TVM...: tense letter + mood letter
        body = m.split('-')[1].lstrip('2'); return f'V-{body[0]}{body[2]}', False
    return 'OTHER', False                # HEB, ARAM

def tokens(k):
    """token ids of a verse, scripture quotations dropped."""
    return [i for i in VERSE[k] if not TOK[i]['scripture']]

def sayings(book, thr):
    return [k for k in VERSE if k[0] == book and K['jesus_share'](k) >= thr]


def nlinked(k, book): return sum(book in LINK[i] for i in VERSE[k])

def lkQ(k):
    n = 0
    for i in VERSE[k]:
        p = PARTNER[i].get('luke')
        if p is not None and CL.get(('luke', TOK[p]['ch'], TOK[p]['v'])) == 'Q': n += 1
    return n

def matthew_classes(thr):
    """Version 2 (change A): selection by shared words at the verse level. DT, MK+L, MK-L, M are
    mutually exclusive (DT needs mk < 3, the Markan classes mk >= 3, M mk == 0 and lk == 0).
    M* (mk == 0 and lk == 0, any Aland status) is a superset of M, used only as a secondary
    partner in comparison 1; it cannot overlap DT (DT needs lk >= 2)."""
    out = collections.defaultdict(list)
    for k in sayings('matthew', thr):
        mk, lk, lq = nlinked(k, 'mark'), nlinked(k, 'luke'), lkQ(k)
        if mk == 0 and lk == 0: out['M*'].append(k)
        if lq >= 2 and mk < 3: c = 'DT'
        elif mk >= 3 and lk >= 2: c = 'MK+L'
        elif mk >= 3 and lk == 0: c = 'MK-L'
        elif not ({'mark', 'luke'} & PAR[k]) and mk == 0 and lk == 0: c = 'M'
        else: continue
        out[c].append(k)
    return out

def luke_classes(thr):
    """Mirror. DT = CL 'Q' takes precedence (checked first); MK+M / MK-M by shared words only
    (v2 drops v1's exclusion of 'Q+Mark overlap' verses, as the Matthew side drops lkQ == 0).
    L* = mk == 0 and mt == 0, excluding verses already in DT so that DT vs L* stays disjoint."""
    out = collections.defaultdict(list)
    for k in sayings('luke', thr):
        mk, mt = nlinked(k, 'mark'), nlinked(k, 'matthew')
        if CL[k] != 'Q' and mk == 0 and mt == 0: out['L*'].append(k)
        if CL[k] == 'Q': c = 'DT'
        elif mk >= 3 and mt >= 2: c = 'MK+M'
        elif mk >= 3 and mt == 0: c = 'MK-M'
        elif not ({'mark', 'matthew'} & PAR[k]) and mk == 0 and mt == 0: c = 'L'
        else: continue
        out[c].append(k)
    return out

def mark_classes(thr):
    out = collections.defaultdict(list)
    for k in sayings('mark', thr):
        for other, tag in (('luke', 'Lk'), ('matthew', 'Mt')):
            n = nlinked(k, other)
            if n >= 2: out[f'taken by {tag}'].append(k)
            elif n == 0: out[f'not taken by {tag}'].append(k)
    return out


def passages(verses): return runs(verses)          # runs of consecutive verses of one class


def chunk_units(pass_list, scope):
    """Merge passages shorter than 60 tokens into the next passage of the same side (a short
    last one joins the previous unit), then cut each unit into ~100-token chunks (a leftover
    under 60 tokens joins the previous chunk). Returns list of units, each a list of chunks
    (each chunk a list of feature indices)."""
    seqs = [scope.seq(p) for p in sorted(pass_list, key=lambda p: (p[0][1], p[0][2]))]
    units, carry = [], []
    for s in seqs:
        carry = carry + s
        if len(carry) >= 60: units.append(carry); carry = []
    if carry:
        if units: units[-1] = units[-1] + carry
        else: units.append(carry)
    out = []
    for u in units:
        ch = [u[j:j + 100] for j in range(0, len(u), 100)]
        if len(ch) > 1 and len(ch[-1]) < 60:
            last = ch.pop(); ch[-1] = ch[-1] + last
        out.append(ch)
    return out

