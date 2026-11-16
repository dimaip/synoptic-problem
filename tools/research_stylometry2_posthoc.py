#!/usr/bin/env python3
"""E3, checks made AFTER the pre-specified run. Not part of the fixed design.

The fixed run (research_stylometry2.txt) scored several comparisons at exactly 50%. A classifier
that assigns every chunk to the larger group scores exactly 50% balanced accuracy, so those values
may show a failure of the instrument on unequal groups, not an absence of difference. This script
(1) prints what each classifier actually predicted in the fixed run, and (2) repeats the
comparisons with the classes weighted equally (class_weight='balanced'), everything else as fixed.

Usage: tools/.venv/bin/python tools/research_stylometry2_posthoc.py DATA > tools/research_stylometry2_posthoc.txt
"""
import os, sys, json
import numpy as np
os.environ['E3_DATA'] = sys.argv[1]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import research_stylometry2 as e3
import research_common as c
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.model_selection import StratifiedGroupKFold, LeaveOneGroupOut
from sklearn.metrics import balanced_accuracy_score
from joblib import Parallel, delayed

SEED = e3.SEED
def predict(passages, labels, kind, balanced):
    texts, y, groups, _ = e3.prepare(passages, labels, kind)
    counts = [int(np.sum(labels == lab)) for lab in (0, 1)]
    splitter = LeaveOneGroupOut() if min(counts) < 10 else StratifiedGroupKFold(n_splits=10, shuffle=True, random_state=SEED)
    pred = np.empty(len(y), dtype=int); cw = 'balanced' if balanced else None
    for train, test in splitter.split(texts, y, groups):
        vec = TfidfVectorizer(**e3.SETTINGS[kind]); x = vec.fit_transform(texts[train]); z = vec.transform(texts[test])
        model = (LinearSVC(C=1, max_iter=5000, random_state=SEED, class_weight=cw) if kind == 'char'
                 else LogisticRegression(C=1, max_iter=2000, random_state=SEED, class_weight=cw))
        model.fit(x, y[train]); pred[test] = model.predict(z)
    return y, pred

def run(name, pa, pb, kind, nperm):
    passages = pa + pb; labels = np.array([0] * len(pa) + [1] * len(pb))
    y, p0 = predict(passages, labels, kind, False); y, p1 = predict(passages, labels, kind, True)
    conf = lambda p: [[int(np.sum((y == a) & (p == b))) for b in (0, 1)] for a in (0, 1)]
    obs = balanced_accuracy_score(y, p1); rng = np.random.default_rng(SEED + 7000); null = []
    for _ in range(nperm):
        yy, pp = predict(passages, rng.permutation(labels), kind, True); null.append(balanced_accuracy_score(yy, pp))
    return dict(name=name, kind=kind, chunks=[int(np.sum(y == 0)), int(np.sum(y == 1))],
                fixed_acc=float(balanced_accuracy_score(y, p0)), fixed_confusion=conf(p0),
                weighted_acc=float(obs), weighted_confusion=conf(p1),
                weighted_p=(1 + sum(a >= obs for a in null)) / (nperm + 1))

classes = dict(matthew=c.matthew_classes(.8), luke=c.luke_classes(.8), mark=c.mark_classes(.8))
ps = {(g, k): c.passages(v) for g, cl in classes.items() for k, v in cl.items()}
P = lambda g, k: ps[(g, k)]
MK_M = P('matthew', 'MK+L') + P('matthew', 'MK-L'); MK_L = P('luke', 'MK+M') + P('luke', 'MK-M')
CONTRASTS = [
    ('G2  Matthew M* vs Luke L*', P('matthew', 'M*'), P('luke', 'L*')),
    ('1   Matthew DT vs M*', P('matthew', 'DT'), P('matthew', 'M*')),
    ('1s  Matthew DT vs M', P('matthew', 'DT'), P('matthew', 'M')),
    ('2   Matthew MK+L vs MK-L', P('matthew', 'MK+L'), P('matthew', 'MK-L')),
    ('3   Matthew Markan vs DT', MK_M, P('matthew', 'DT')),
    ('4   Matthew Markan vs M*', MK_M, P('matthew', 'M*')),
    ('5   Luke DT vs L*', P('luke', 'DT'), P('luke', 'L*')),
    ('7   Luke Markan vs DT', MK_L, P('luke', 'DT')),
    ('8   Luke Markan vs L*', MK_L, P('luke', 'L*')),
    ('9   Mark taken vs not taken by Luke', P('mark', 'taken by Lk'), P('mark', 'not taken by Lk')),
    ('10  Mark taken vs not taken by Matthew', P('mark', 'taken by Mt'), P('mark', 'not taken by Mt')),
]
NPERM = int(os.environ.get('E3_POSTHOC_PERM', '300'))
res = Parallel(n_jobs=-1)(delayed(run)(n, a, b, k, NPERM) for n, a, b in CONTRASTS for k in e3.KINDS)
print(__doc__.split('Usage')[0].strip()); print(f'\npermutations {NPERM} (passage labels), seed {SEED + 7000}; confusion = [[A as A, A as B], [B as A, B as B]]\n')
print(f"{'contrast':40s} {'instr':7s} {'chunks':9s} {'fixed acc':>9s}  {'fixed predictions':22s} {'weighted acc':>12s} {'p':>7s}  weighted predictions")
for r in res:
    print(f"{r['name']:40s} {r['kind']:7s} {str(r['chunks']):9s} {100*r['fixed_acc']:8.1f}%  {str(r['fixed_confusion']):22s} {100*r['weighted_acc']:11.1f}% {r['weighted_p']:7.4f}  {r['weighted_confusion']}")
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'research_stylometry2_posthoc.json'), 'w'), indent=1)
