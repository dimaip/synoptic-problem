#!/usr/bin/env python3
"""Experiment E2 (version 2): does Luke's selection alone produce the Q/M style difference?

Pre-registered design (see the specification this was written from). Inside Matthew, "Q"
(double tradition) is compared with "M" (special Matthew) by common-word style. The control
is Matthew's own Markan material split by whether Luke also has it: one source, one editor,
so any difference there is produced by Luke's selection alone. Mirror tests run in Luke and
in Mark.

Loading, alignment links, the woes SUPPLEMENT, the Q list and the Luke verse classes (CL) are
reused unchanged from tools/kloppenborg_test.py: it is executed with runpy, its printed output
discarded, and its globals (TOK, VERSE, LINK, PARTNER, PAR, CL, runs, jesus_share, ...) taken
over. That script is not modified, so its committed output stays reproducible.

Version history. Version 1 (outputs kept as research_stylometry_v1.txt / .json) defined the
selection controls MK-L / MK-M by Aland's pericope parallels; they came out almost empty (2 verses
each), because Aland prints a Lukan passage beside nearly every Markan saying in Matthew. Its power
check (all Matthew sayings vs all Luke sayings) was not significant (D p = 0.053, classifier 57.5%),
largely because ~40% of those words are shared verbatim. Version 1 stopped at that gate before any
of the ten comparisons was computed. Version 2 (this script) applies a written revision of the
design: (A) selection classes defined per verse by shared (aligned) words, plus M* / L* variants;
(B) power gate = M sayings vs L sayings (text the two do not share), D p < 0.01, with the v1 check
still printed; (C) bias-corrected percentile interval for E; (D) E(1)-E(2) and E(5)-E(6) with
paired-bootstrap intervals, on which the pre-stated rule is read; (E) classifier descriptive only,
"too few chunks" when a class has fewer than 6.

numpy only.

Usage: python3 tools/research_stylometry.py <synoptic-canvas>/public/data [out.json] > tools/research_stylometry.txt
       (out.json defaults to tools/research_stylometry.json next to this script)
"""
import contextlib, io, json, os, runpy, sys, unicodedata, collections
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = sys.argv[1]
OUT_JSON = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'research_stylometry.json')

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

N_PERM, N_BOOT, N_CPERM, N_NULL = 5000, 2000, 1000, 200
SEED = 20261116
OUT = {'settings': dict(permutations=N_PERM, bootstrap=N_BOOT, classifier_permutations=N_CPERM,
                        null_splits=N_NULL, seed=SEED)}

def say(*a): print(*a, flush=True)

# ---------------------------------------------------------------- features
# Function-word prefixes from the specification, plus INJ (interjections such as ἰδού), a closed
# class that this data tags with its own prefix. COND does not occur in this data.
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

class Scope:
    """A feature vocabulary built from all sayings verses of one or more Gospels."""
    def __init__(self, books, thr, func_only=False, all_verses=False):
        self.func_only = func_only
        source = (lambda b: [k for k in VERSE if k[0] == b]) if all_verses else (lambda b: sayings(b, thr))
        cnt = collections.Counter()
        for b in books:
            for k in source(b):
                for i in tokens(k):
                    f, fn = raw_feature(i)
                    if fn or not func_only: cnt[f] += 1
        self.raw = cnt
        def pooled(f, fn):
            if cnt[f] >= 20: return f
            if fn: return 'RARE-FUNC'
            return 'V-RARE' if f.startswith('V-') else 'OTHER'
        self.map = {}
        for b in books:
            for k in source(b):
                for i in tokens(k):
                    f, fn = raw_feature(i)
                    if fn or not func_only: self.map[f] = pooled(f, fn)
        final = collections.Counter()
        for f, n in cnt.items(): final[self.map[f]] += n
        self.feats = sorted(final, key=lambda f: (-final[f], f))
        self.index = {f: j for j, f in enumerate(self.feats)}
        self.top30 = [self.index[f] for f in self.feats[:30]]

    def seq(self, verses):
        """feature indices of the tokens of a list of verses, in order."""
        out = []
        for k in verses:
            for i in tokens(k):
                f, fn = raw_feature(i)
                if self.func_only and not fn: continue
                out.append(self.index[self.map[f]])
        return out

    def counts(self, verses):
        return np.bincount(self.seq(verses), minlength=len(self.feats)).astype(float)

# ---------------------------------------------------------------- classes
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

def dt_aland(thr):
    """Sensitivity (c): Matthew sayings verses in an Aland group with no Mark passage whose
    Luke passage(s) are at least half Q-list verses."""
    keep = set()
    for g in groups:
        if not g['correspondence']: continue
        ps = g['passages']
        if any(p['book'] == 'mark' for p in ps): continue
        lv = [('luke', *map(int, r.split(':'))) for p in ps if p['book'] == 'luke' for r in p['verses']]
        if not lv or sum(k in Q for k in lv) < len(lv) / 2: continue
        for p in ps:
            if p['book'] == 'matthew':
                for r in p['verses']: keep.add(('matthew', *map(int, r.split(':'))))
    s = set(sayings('matthew', thr))
    return sorted(keep & s, key=lambda k: (k[1], k[2]))

def passages(verses): return runs(verses)          # runs of consecutive verses of one class

# ---------------------------------------------------------------- statistic D
def D_many(SA, SB):
    """D for rows of count matrices SA, SB (k x F)."""
    SA = np.atleast_2d(SA); SB = np.atleast_2d(SB)
    nA = SA.sum(1, keepdims=True); nB = SB.sum(1, keepdims=True)
    p = (SA + SB) / (nA + nB)
    mask = (p * nA >= 5) & (p * nB >= 5)
    diff2 = (SA / nA - SB / nB) ** 2
    return np.where(mask, diff2 / np.where(p > 0, p, 1), 0).sum(1)

def perm_test(PA, PB, rng, n=N_PERM):
    """PA, PB: passage x feature counts. Returns D_obs, permutation mean, p, permuted Ds."""
    P = np.vstack([PA, PB]); tot = P.sum(0); a = len(PA); N = len(P)
    dobs = D_many(PA.sum(0), PB.sum(0))[0]
    M = np.zeros((n, N))
    for r in range(n): M[r, rng.permutation(N)[:a]] = 1
    SA = M @ P; dp = D_many(SA, tot - SA)
    return dobs, dp.mean(), (1 + (dp >= dobs).sum()) / (1 + n), dp

def boot_D(PA, PB, rng, n=N_BOOT):
    def resample(P):
        idx = rng.integers(0, len(P), size=(n, len(P)))
        W = np.zeros((n, len(P)))
        for r in range(n): W[r] = np.bincount(idx[r], minlength=len(P))
        return W @ P
    return D_many(resample(PA), resample(PB))

# ---------------------------------------------------------------- classifier (Burrows's Delta)
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

def classifier(passA, passB, scope, rng, nperm=N_CPERM):
    UA, UB = chunk_units(passA, scope), chunk_units(passB, scope)
    units = UA + UB; ulab = np.array([0] * len(UA) + [1] * len(UB)); U = len(units)
    cA, cB = sum(len(u) for u in UA), sum(len(u) for u in UB)
    # v2 change E: descriptive only, and not computed when a class has fewer than 6 chunks
    if len(UA) < 2 or len(UB) < 2 or cA < 6 or cB < 6: return dict(acc=None, chunksA=cA, chunksB=cB, accP=None, unitsA=len(UA), unitsB=len(UB))
    X, cu = [], []
    for ui, u in enumerate(units):
        for c in u:
            v = np.bincount(c, minlength=len(scope.feats))[scope.top30] / len(c); X.append(v); cu.append(ui)
    X = np.array(X); cu = np.array(cu); C = len(X)
    # z-scoring depends only on which unit is held out, not on labels: precompute per fold
    S = np.zeros((U, U, X.shape[1]))         # S[f, u] = sum of z-scored chunks of unit u in fold f
    NC = np.bincount(cu, minlength=U).astype(float)
    Ztest = []
    for f in range(U):
        tr = cu != f; mu = X[tr].mean(0); sd = X[tr].std(0); sd[sd == 0] = 1
        Z = (X - mu) / sd
        np.add.at(S[f], cu, Z); S[f, f] = 0
        Ztest.append(Z[cu == f])
    def bal_acc(lab):
        m1 = np.tile(lab == 1, (U, 1)).astype(float); np.fill_diagonal(m1, 0)
        m0 = np.tile(lab == 0, (U, 1)).astype(float); np.fill_diagonal(m0, 0)
        c1 = np.einsum('fu,fuk->fk', m1, S) / (m1 @ NC)[:, None]
        c0 = np.einsum('fu,fuk->fk', m0, S) / (m0 @ NC)[:, None]
        hit = np.zeros(2)
        for f in range(U):
            d0 = np.abs(Ztest[f] - c0[f]).mean(1); d1 = np.abs(Ztest[f] - c1[f]).mean(1)
            pred = (d1 < d0).astype(int); hit[lab[f]] += (pred == lab[f]).sum()
        n = np.array([(NC * (lab == 0)).sum(), (NC * (lab == 1)).sum()])
        return (hit / n).mean()
    acc = bal_acc(ulab)
    ge = sum(bal_acc(rng.permutation(ulab)) >= acc for _ in range(nperm))
    return dict(acc=acc, chunksA=cA, chunksB=cB, accP=(1 + ge) / (1 + nperm), unitsA=len(UA), unitsB=len(UB))

# ---------------------------------------------------------------- one comparison
def words(pl, scope): return sum(len(scope.seq(p)) for p in pl)

BOOT = {}   # comparison id -> bias-corrected bootstrap series of E (for the paired differences)

def compare(cid, gospel, a, b, passA, passB, scope, clf=True):
    rng = np.random.default_rng(SEED)
    PA = np.array([scope.counts(p) for p in passA]); PB = np.array([scope.counts(p) for p in passB])
    r = dict(id=cid, gospel=gospel, a=a, b=b, wordsA=int(PA.sum()), wordsB=int(PB.sum()),
             passagesA=len(passA), passagesB=len(passB))
    if len(passA) < 2 or len(passB) < 2:
        r.update(D=None, permMean=None, E=None, Elo=None, Ehi=None, p=None, acc=None, chunksA=None, chunksB=None, accP=None)
        say(f'  {cid:>4} {gospel:8s} {a:>16s} vs {b:<16s}  too few passages ({len(passA)}, {len(passB)}): not computed'); return r
    dobs, pm, p, _ = perm_test(PA, PB, rng)
    # v2 change C: bias-corrected percentile interval. Bootstrap series D*, recentred on D_obs,
    # minus the permutation mean. Ebs is kept (not in JSON) for the paired differences (change D).
    Ds = boot_D(PA, PB, rng)
    Ebs = Ds - Ds.mean() + dobs - pm
    r.update(D=dobs, permMean=pm, E=dobs - pm, Elo=float(np.percentile(Ebs, 2.5)), Ehi=float(np.percentile(Ebs, 97.5)), p=p)
    BOOT[cid] = Ebs
    if clf:
        c = classifier(passA, passB, scope, rng)
        r.update(acc=c['acc'], chunksA=c['chunksA'], chunksB=c['chunksB'], accP=c['accP'])
    else: r.update(acc=None, chunksA=None, chunksB=None, accP=None)
    acc = f"acc {100*r['acc']:5.1f}% (chunks {r['chunksA']}/{r['chunksB']}, p {r['accP']:.3f})" if r['acc'] is not None else ('acc -' if not clf else f"too few chunks ({r['chunksA']}/{r['chunksB']})")
    say(f"  {cid:>4} {gospel:8s} {a:>16s} vs {b:<16s} words {r['wordsA']:5d}/{r['wordsB']:<5d} pass {len(passA):3d}/{len(passB):<3d} "
        f"D {dobs:.4f} null {pm:.4f} E {r['E']:+.4f} [{r['Elo']:+.4f}, {r['Ehi']:+.4f}] p {p:.4f}  {acc}")
    return r

def clean(o):
    if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
    if isinstance(o, list): return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)): return round(float(o), 6)
    if isinstance(o, np.integer): return int(o)
    return o

# ================================================================ run
# Set E2_SANITY_ONLY=1 to stop after the sanity checks (used only while debugging the checks).
SANITY_ONLY = os.environ.get('E2_SANITY_ONLY') == '1'

say('Experiment E2, version 2: does Luke\'s selection alone produce the Q/M style difference?')
say(f'permutations {N_PERM}, bootstrap {N_BOOT}, classifier permutations {N_CPERM}, seed {SEED}')
say('Version 2 applies a written revision of the design made AFTER version 1 stopped at its power gate and')
say('BEFORE any of the ten comparisons had been computed (version 1 output: research_stylometry_v1.txt).')
say('Changes: (A) selection classes by shared words per verse, plus M*/L*; (B) power gate = M vs L sayings;')
say('(C) bias-corrected bootstrap interval for E; (D) E(1)-E(2), E(5)-E(6) with paired-bootstrap intervals;')
say('(E) classifier descriptive only, "too few chunks" under 6 chunks in a class.\n')

say('== 1. Morphology tag inventory (prefix before the first hyphen), Matthew+Mark+Luke ==')
inv = collections.Counter(MORPH[i].split('-')[0] for i in TOK if TOK[i]['book'] != 'john')
say('  ' + ', '.join(f'{p} {n}' for p, n in inv.most_common()))
say('  Function-word prefixes used: ' + ' '.join(sorted(FUNC_PREFIX)) + '.')
say('  Added beyond the specification: INJ (interjections, a closed class with its own prefix here).')
say('  COND does not occur (conditionals are tagged CONJ). HEB and ARAM (indeclinable foreign words) -> OTHER.')
say('  Verb class = V- + tense letter + mood letter, the "2" of second tenses ignored (V-2AAI-3S -> V-AI).')
say('  Rare pooling: function lemmas under 20 -> RARE-FUNC; verb classes under 20 -> V-RARE; other coarse under 20 -> OTHER.')
say('  Link counts (mk, lk, lkQ, mt) use all tokens of the verse; scripture tokens are dropped only from features.\n')

THR = 0.8
SC = {g: Scope([g], THR) for g in ('matthew', 'luke', 'mark')}
for g, s in SC.items(): say(f'  vocabulary {g:8s}: {len(s.feats)} features after pooling; top 30: {" ".join(s.feats[:30])}')
MC, LC, KC = matthew_classes(THR), luke_classes(THR), mark_classes(THR)
PS = {('matthew', c): passages(v) for c, v in MC.items()}
PS.update({('luke', c): passages(v) for c, v in LC.items()})
PS.update({('mark', c): passages(v) for c, v in KC.items()})

say('\n== 2. Class counts (sayings verses >= 80% words of Jesus; words exclude scripture) ==')
say('  Matthew: DT lkQ>=2 & mk<3; MK+L mk>=3 & lk>=2; MK-L mk>=3 & lk==0; M mk==lk==0 & no Aland Mk/Lk parallel;')
say('           M* mk==lk==0 (any Aland status; superset of M). Luke mirror with mt; DT = CL "Q" (checked first);')
say('           L* mk==mt==0 and not DT. Mark: taken = >=2 tokens linked, not taken = 0 linked.')
counts = []
for g, order, cl in (('matthew', ['DT', 'MK+L', 'MK-L', 'M', 'M*'], MC), ('luke', ['DT', 'MK+M', 'MK-M', 'L', 'L*'], LC),
                     ('mark', ['taken by Lk', 'not taken by Lk', 'taken by Mt', 'not taken by Mt'], KC)):
    for c in order:
        pl = PS.get((g, c), []); n = words(pl, SC[g])
        counts.append(dict(gospel=g, cls=c, verses=len(cl.get(c, [])), words=n, passages=len(pl)))
        say(f'  {g:8s} {c:16s} verses {len(cl.get(c, [])):4d}  words {n:5d}  passages {len(pl):3d}')
ovl = sum(1 for k in LC.get('MK+M', []) if CL[k] == 'Q+Mark overlap')
say(f'  (Luke MK+M includes {ovl} verses that kloppenborg_test.py classes as "Q+Mark overlap".)')
OUT['class_counts'] = counts

# ---------------------------------------------------------------- sanity checks
say('\n== 3. Sanity checks ==')
rng = np.random.default_rng(SEED)
Mp = PS[('matthew', 'M')]; PM = np.array([SC['matthew'].counts(p) for p in Mp])
ps = []
for _ in range(N_NULL):
    perm = rng.permutation(len(Mp)); h = len(Mp) // 2
    ps.append(perm_test(PM[perm[:h]], PM[perm[h:]], rng)[2])
ps = np.array(ps); share = float((ps < .05).mean())
say(f'  Null check: M passages ({len(Mp)}) split at random in two halves {N_NULL} times; share of p < 0.05 = {100*share:.1f}%  (mean p {ps.mean():.3f})')

SC_ML = Scope(['matthew', 'luke'], THR)
say('  Version 1 check, failed (kept for the record; not a gate in version 2): all Matthew sayings vs all Luke sayings')
power_v1 = compare('PWR1', 'Mt/Lk', 'Mt all sayings', 'Lk all sayings', runs(sayings('matthew', THR)), runs(sayings('luke', THR)), SC_ML)
say('  Version 2 power gate: M (Matthew) sayings vs L (Luke) sayings, joint Matthew+Luke vocabulary; gate D p < 0.01')
power = compare('PWR2', 'Mt/Lk', 'Mt M', 'Lk L', PS[('matthew', 'M')], PS[('luke', 'L')], SC_ML)
ok = power['p'] < 0.01
acc_s = f'{100*power["acc"]:.1f}% (classifier p {power["accP"]:.3f})' if power['acc'] is not None else 'too few chunks'
say(f'  Power gate {"PASSED" if ok else "FAILED"}: D p = {power["p"]:.4f}; classifier balanced accuracy (not a gate) = {acc_s}')
say('  Informational check (not a gate): MK+L in Matthew vs MK+M in Luke, both editing the same Markan sayings')
power_info = compare('PWR3', 'Mt/Lk', 'Mt MK+L', 'Lk MK+M', PS[('matthew', 'MK+L')], PS[('luke', 'MK+M')], SC_ML)
OUT['sanity'] = dict(null_check=dict(splits=N_NULL, share_p_below_05=share, mean_p=float(ps.mean()), passages=len(Mp)),
                     power_check_v1_failed=power_v1, power_check=power, power_passed=bool(ok),
                     power_check_informational=power_info)
if not ok:
    # Post hoc diagnostics. NOT part of the pre-specified design: run after the gate failed, to see
    # whether the instrument is broken or whether sayings are simply too alike for it.
    say('\n== 3b. Post hoc diagnostics (not pre-specified; run after the gate failed) ==')
    SC_ALL = Scope(['matthew', 'luke'], THR, all_verses=True)
    narr = lambda b: [k for k in VERSE if k[0] == b and K['jesus_share'](k) < 0.2]
    OUT['post_hoc'] = [
        compare('POST1', 'Mt', 'Mt sayings', 'Mt narrative', runs(sayings('matthew', THR)), runs(narr('matthew')), SC_ALL),
        compare('POST2', 'Mt/Lk', 'Mt narrative', 'Lk narrative', runs(narr('matthew')), runs(narr('luke')), SC_ALL),
        compare('POST3', 'Mt/Lk', 'Mt M*', 'Lk L*', PS[('matthew', 'M*')], PS[('luke', 'L*')], SC_ML)]
    say('  The instrument cannot see style: experiment void.'); json.dump(clean(OUT), open(OUT_JSON, 'w'), indent=1, ensure_ascii=False); sys.exit()
if SANITY_ONLY:
    say('  (E2_SANITY_ONLY set: stopping before the comparisons.)'); sys.exit()

# ---------------------------------------------------------------- comparisons
say('\n== 4. Comparisons ==')
say('  E = D - mean(permutation D). 95% interval: bias-corrected percentile interval (approximate): 2,000 bootstrap')
say('  resamples of passages within each group give D*; interval = percentiles 2.5/97.5 of D* - mean(D*) + D_obs,')
say('  minus the permutation mean. p = permutation p for D (primary). acc = leave-one-passage-out balanced')
say('  accuracy, Burrows\'s Delta (descriptive only).')
def P(g, *cs): return [p for c in cs for p in PS.get((g, c), [])]
spec = [
    (1, 'matthew', 'DT', 'M', P('matthew', 'DT'), P('matthew', 'M')),
    (2, 'matthew', 'MK+L', 'MK-L', P('matthew', 'MK+L'), P('matthew', 'MK-L')),
    (3, 'matthew', 'MK+L|MK-L', 'DT', P('matthew', 'MK+L', 'MK-L'), P('matthew', 'DT')),
    (4, 'matthew', 'MK+L|MK-L', 'M', P('matthew', 'MK+L', 'MK-L'), P('matthew', 'M')),
    (5, 'luke', 'DT', 'L', P('luke', 'DT'), P('luke', 'L')),
    (6, 'luke', 'MK+M', 'MK-M', P('luke', 'MK+M'), P('luke', 'MK-M')),
    (7, 'luke', 'MK+M|MK-M', 'DT', P('luke', 'MK+M', 'MK-M'), P('luke', 'DT')),
    (8, 'luke', 'MK+M|MK-M', 'L', P('luke', 'MK+M', 'MK-M'), P('luke', 'L')),
    (9, 'mark', 'taken by Lk', 'not taken by Lk', P('mark', 'taken by Lk'), P('mark', 'not taken by Lk')),
    (10, 'mark', 'taken by Mt', 'not taken by Mt', P('mark', 'taken by Mt'), P('mark', 'not taken by Mt')),
]
OUT['comparisons'] = [compare(i, g, a, b, pa, pb, SC[g]) for i, g, a, b, pa, pb in spec]
say('  Secondary variants (M* for comparison 1, L* for comparison 5):')
OUT['variants'] = [compare('1*', 'matthew', 'DT', 'M*', P('matthew', 'DT'), P('matthew', 'M*'), SC['matthew']),
                   compare('5*', 'luke', 'DT', 'L*', P('luke', 'DT'), P('luke', 'L*'), SC['luke'])]

# ---------------------------------------------------------------- paired differences (change D)
say('\n== 5. Differences of excess distance (change D) ==')
say('  Interval: percentiles 2.5/97.5 of E*_a[i] - E*_b[i] over the 2,000 bias-corrected bootstrap draws (independent samples).')
C = {r['id']: r for r in OUT['comparisons']}
def diff(a, b):
    if C[a]['E'] is None or C[b]['E'] is None:
        say(f'  E({a}) - E({b}): not computable (a comparison was not computed)'); return dict(a=a, b=b, value=None, lo=None, hi=None)
    d = BOOT[a] - BOOT[b]; v = C[a]['E'] - C[b]['E']
    lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
    say(f'  E({a}) - E({b}) = {v:+.4f}  [{lo:+.4f}, {hi:+.4f}]  interval excludes zero on the positive side: {"yes" if lo > 0 else "no"}')
    return dict(a=a, b=b, value=v, lo=lo, hi=hi, excludes_zero_positive=bool(lo > 0))
OUT['diff_1_2'] = diff(1, 2)
OUT['diff_5_6'] = diff(5, 6)

# ---------------------------------------------------------------- sensitivities
say('\n== 6. Sensitivities, comparisons 1 and 2 ==')
sens = []
say(' (a) function-word features only, no coarse classes')
SCf = Scope(['matthew'], THR, func_only=True)
sens.append(dict(variant='a', **compare('1a', 'matthew', 'DT', 'M', P('matthew', 'DT'), P('matthew', 'M'), SCf)))
sens.append(dict(variant='a', **compare('2a', 'matthew', 'MK+L', 'MK-L', P('matthew', 'MK+L'), P('matthew', 'MK-L'), SCf)))
say(' (b) sayings threshold 100% instead of 80%')
SCb = Scope(['matthew'], 1.0); MCb = matthew_classes(1.0); PB_ = {c: passages(v) for c, v in MCb.items()}
for c in ['DT', 'MK+L', 'MK-L', 'M']: say(f'      class {c:5s} verses {len(MCb.get(c, [])):4d} passages {len(PB_.get(c, [])):3d}')
sens.append(dict(variant='b', **compare('1b', 'matthew', 'DT', 'M', PB_.get('DT', []), PB_.get('M', []), SCb)))
sens.append(dict(variant='b', **compare('2b', 'matthew', 'MK+L', 'MK-L', PB_.get('MK+L', []), PB_.get('MK-L', []), SCb)))
say(' (c) DT = Matthew sayings verses in an Aland group with no Mark passage and a Luke passage at least half Q-list verses')
dtc = dt_aland(THR); pdc = passages(dtc)
say(f'      DT(c) verses {len(dtc)} passages {len(pdc)}; overlap with main DT: {len(set(dtc) & set(MC["DT"]))} verses; overlap with M: {len(set(dtc) & set(MC.get("M", [])))}')
sens.append(dict(variant='c', **compare('1c', 'matthew', 'DT(c)', 'M', pdc, P('matthew', 'M'), SC['matthew'])))
say('      comparison 2 does not involve DT, so (c) leaves it unchanged (see 4.)')
OUT['sensitivities'] = sens

# ---------------------------------------------------------------- pre-stated reading inputs
say('\n== 7. Inputs to the pre-stated reading ==')
for i in (1, 2, 3, 4, 5, 6, 7, 8):
    r = C[i]
    say(f"  E({i}) = {r['E']:+.4f}  [{r['Elo']:+.4f}, {r['Ehi']:+.4f}]" if r['E'] is not None else f'  E({i}) not computed')
say('  Rule (v1, read on the v2 difference): E(1)-E(2) interval excludes zero on the positive side = the Q/M difference')
say('  exceeds what selection alone gives; otherwise it does not.')
OUT['reading'] = dict(diff_1_2_excludes_zero_positive=OUT['diff_1_2'].get('excludes_zero_positive'),
                      diff_5_6_excludes_zero_positive=OUT['diff_5_6'].get('excludes_zero_positive'))

json.dump(clean(OUT), open(OUT_JSON, 'w'), indent=1, ensure_ascii=False)
say(f'\nJSON written: {os.path.basename(OUT_JSON)}')
