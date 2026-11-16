#!/usr/bin/env python3
"""E3 fixed sequence-classifier experiment.

Usage: tools/.venv/bin/python tools/research_stylometry2.py DATA [--step1-only]
Outputs are tools/research_stylometry2.{txt,json}; stdout is also printed.
After --step1-only, use --resume-step2 to reuse saved gates without rerunning them.
Step 2 is guarded by an exclusive marker: never rerun it against an existing marker.
Short passages merge exactly as in E2. Their original passage IDs are retained;
merged units are conservative CV groups. Permutations shuffle ORIGINAL passage
labels and then rebuild E2 chunks, rather than shuffling merged-unit labels.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
import sys, json, platform, time, unicodedata
from pathlib import Path
import numpy as np
import scipy, sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.model_selection import StratifiedGroupKFold, LeaveOneGroupOut
from sklearn.metrics import balanced_accuracy_score
from joblib import Parallel, delayed
os.environ['E3_DATA'] = sys.argv[1]
import research_common as c
# Rendering is deterministic and label-independent; cache strings, never fitted features.
RENDERED = {kind: {} for kind in ['char', 'masked', 'tags']}
for token_id in c.TOK:
    form = ''.join(ch for ch in c.strip(c.TOK[token_id]['text']) if not unicodedata.category(ch).startswith('P'))
    feature, function = c.raw_feature(token_id)
    RENDERED['char'][token_id] = form
    RENDERED['masked'][token_id] = form if function else feature
    RENDERED['tags'][token_id] = feature

HERE = Path(__file__).resolve().parent
SEED = 20261116
KINDS = ['char', 'masked', 'tags']
SETTINGS = dict(char=dict(analyzer='char', ngram_range=(3,5), max_features=6000,
                         min_df=2, sublinear_tf=True, lowercase=False, token_pattern=None),
                masked=dict(analyzer='char', ngram_range=(3,5), max_features=6000,
                         min_df=2, sublinear_tf=True, lowercase=False, token_pattern=None),
                tags=dict(analyzer='word', ngram_range=(1,4), max_features=3000,
                         min_df=2, sublinear_tf=True, lowercase=False, token_pattern=r'(?u)\b\w+\b'))

class TokenScope:
    """Retain original passage membership through the unchanged E2 chunker."""
    def __init__(self, passage_ids):
        self.passage_ids = passage_ids
    def seq(self, verses):
        return [(i, self.passage_ids[k]) for k in verses for i in c.tokens(k)]


def prepare(passages, labels, kind):
    texts, y, groups, membership = [], [], [], []
    for label in (0, 1):
        selected = [p for p, lab in zip(passages, labels) if lab == label]
        pid = {k: j for j, p in enumerate(passages) for k in p}
        units = c.chunk_units(selected, TokenScope(pid))
        for unit in units:
            group = len(membership)
            membership.append(sorted({p for chunk in unit for _, p in chunk}))
            for chunk in unit:
                rendered = [RENDERED[kind][i] for i, _ in chunk]
                texts.append(' '.join(rendered)); y.append(label); groups.append(group)
    return np.array(texts), np.array(y), np.array(groups), membership


def accuracy(texts, y, groups, passage_counts):
    if min(passage_counts) < 2 or min(np.bincount(y, minlength=2)) == 0:
        return None, 'too few passages'
    # Merging only joins passages: holding a whole merged unit out cannot leak an original passage.
    group_counts = [len(set(groups[y == lab])) for lab in (0, 1)]
    if min(group_counts) < 2:
        return None, 'too few independent merged groups for training both classes'
    if min(passage_counts) < 10:
        splitter = LeaveOneGroupOut()
    else:
        splitter = StratifiedGroupKFold(n_splits=10, shuffle=True, random_state=SEED)
    pred = np.empty(len(y), dtype=int)
    for train, test in splitter.split(texts, y, groups):
        assert not set(groups[train]) & set(groups[test])
        vec = TfidfVectorizer(**SETTINGS[CURRENT_KIND])
        try:
            x = vec.fit_transform(texts[train]); z = vec.transform(texts[test])
        except ValueError as e:
            return None, str(e)
        model = LinearSVC(C=1,max_iter=5000,random_state=SEED) if CURRENT_KIND == 'char' else LogisticRegression(C=1,max_iter=2000,random_state=SEED)
        model.fit(x, y[train]); pred[test] = model.predict(z)
    return float(balanced_accuracy_score(y, pred)), None


def score(passages, labels, kind):
    global CURRENT_KIND
    CURRENT_KIND = kind
    texts, y, groups, members = prepare(passages, labels, kind)
    counts = [int(np.sum(labels == lab)) for lab in (0,1)]
    acc, gap = accuracy(texts, y, groups, counts)
    return acc, gap, dict(chunks=[int(np.sum(y == lab)) for lab in (0,1)], passages=counts,
                          merged_groups=[len(set(groups[y == lab])) for lab in (0,1)])


def contrast(pa, pb, kind, nperm=500, seed=SEED, initial_labels=None):
    passages = pa + pb
    labels = np.array([0]*len(pa)+[1]*len(pb)) if initial_labels is None else initial_labels
    observed, gap, counts = score(passages, labels, kind)
    result = dict(instrument=kind, accuracy=observed, gap=gap, **counts)
    if observed is None:
        result['p'] = None; return result
    rng = np.random.default_rng(seed)
    null = []
    for _ in range(nperm):
        a, g, _ = score(passages, rng.permutation(labels), kind)
        if a is None:
            result.update(p=None, gap='Permutation unavailable: '+g, permutation_accuracies=null)
            return result
        null.append(a)
    result.update(p=(1+sum(a >= observed for a in null))/(nperm+1), permutation_accuracies=null)
    return result


def negative(pa, index):
    rng = np.random.default_rng(SEED+1000+index)
    order = rng.permutation(len(pa)); split = len(pa)//2
    result = contrast([pa[j] for j in order[:split]], [pa[j] for j in order[split:]], 'tags', 200, SEED+2000+index)
    result['split'] = index
    return result


def matched(pa, pb, kind, n, draw):
    global CURRENT_KIND
    CURRENT_KIND = kind
    texts, y, groups, members = prepare(pa+pb, np.array([0]*len(pa)+[1]*len(pb)), kind)
    rng = np.random.default_rng(SEED+3000+draw)
    ix = np.concatenate([rng.choice(np.flatnonzero(y == label), n, replace=False) for label in (0,1)])
    counts = [len({p for g in set(groups[ix][y[ix] == lab]) for p in members[g]}) for lab in (0,1)]
    a, gap = accuracy(texts[ix], y[ix], groups[ix], counts)
    return a, gap


def main():
    out = dict(settings=dict(seed=SEED, permutations=500, negative_splits=100, negative_permutations=200,
                matched_draws=100, vectorizers=SETTINGS, learners=dict(char='LinearSVC(C=1,max_iter=5000,random_state=seed)',
                masked='LogisticRegression(C=1,max_iter=2000,random_state=seed)', tags='LogisticRegression(C=1,max_iter=2000,random_state=seed)')),
                versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,sklearn=sklearn.__version__),
                gates={},controls={},comparisons=[],matched={},differences={})
    def emit(label, value):
        print(label, json.dumps(value, ensure_ascii=False), flush=True)
    def save():
        (HERE/'research_stylometry2.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
    out['implementation_corrections'] = ['Validity attempt stopped before results: fold selection incorrectly also used merged-group counts; corrected to use original passage counts only. Worker data path made environment-based for process-safe loading. Deterministic token rendering cached; no fitted features cached.']
    emit('Implementation corrections',out['implementation_corrections'])
    print('E3: design fixed before this run. No settings or thresholds tuned.', flush=True)
    emit('Versions',out['versions']); emit('Settings',out['settings'])
    print("October style.py lines 61-65 copied: analyzer='word' if word else 'char'; ngram_range=(1,4) for pos_sequence_lr else (3,5); max_features=3000 for pos_sequence_lr else 6000; min_df=2; sublinear_tf=True; lowercase=False; token_pattern=r'(?u)\\b\\w+\\b' if word else None; LinearSVC(C=1,max_iter=5000,random_state=seed) or LogisticRegression(C=1,max_iter=2000,random_state=seed). Defaults unchanged.",flush=True)
    print('Seeds: CV/learners/permutations 20261116; negative split 20262116+i, negative permutation 20263116+i; matched draw 20264116+i; initial leakage-label shuffle 20265116.',flush=True)
    print('G2 is not blind: added after E2 post-stop wider-group separation p=0.0048.',flush=True)
    print('E2 short-passage merges unchanged. Original passage labels permuted before rechunking. Merged units held together; leave-one-merged-unit-out when original class passages <10. No rare pooling for tags: raw E2 function lemma/coarse feature as specified. Word tokenizer splits V-PI and multiword lemmas exactly as October settings require.',flush=True)
    print('Matched spread: subsample percentiles, NOT a confidence interval. Data read-only.',flush=True)
    classes = dict(matthew=c.matthew_classes(.8),luke=c.luke_classes(.8),mark=c.mark_classes(.8))
    ps = {(g,k):c.passages(v) for g, cl in classes.items() for k,v in cl.items()}
    counts = [dict(gospel=g,cls=k,verses=len(v),words=sum(len(c.tokens(x)) for x in v),passages=len(ps[g,k])) for g,cl in classes.items() for k,v in cl.items()]
    prior = json.loads((HERE/'research_stylometry.json').read_text())['class_counts']
    key = lambda x:(x['gospel'],x['cls'])
    equal = sorted(counts,key=key) == sorted(prior,key=key)
    out['class_count_check'] = dict(equal=equal,actual=counts,expected=prior)
    emit('Class count check',out['class_count_check']); assert equal
    P = lambda g,k: ps.get((g,k),[])
    if '--resume-step2' in sys.argv:
        out = json.loads((HERE/'research_stylometry2.json').read_text())
        passed = out['passed']
        out['execution_notes'] = ['Step 1 completed first. A reservation marker stopped its process before any Step 2 contrast. Step 2 resumed once with independent contrasts scheduled in parallel; no statistical definitions changed.']
        emit('Execution notes', out['execution_notes'])
    else:
        jobs = []
        for kind in KINDS:
            jobs.extend([('G1',kind,P('matthew','M'),P('luke','L')),('G2',kind,P('matthew','M*'),P('luke','L*'))])
        # Processes perform independent numerical jobs; no delegated agents.
        results = Parallel(n_jobs=6)(delayed(contrast)(pa,pb,kind) for _,kind,pa,pb in jobs)
        for (gate,kind,_,_),r in zip(jobs,results):
            out['gates'].setdefault(kind,{})[gate]=r
            emit(gate,{k:v for k,v in r.items() if k!='permutation_accuracies'})
        save()
        pa,pb=P('matthew','M*'),P('luke','L*')
        shuffled=np.random.default_rng(SEED+4000).permutation(np.array([0]*len(pa)+[1]*len(pb)))
        out['controls']['leakage_seed']=SEED+4000
        leakage = Parallel(n_jobs=3)(delayed(contrast)(pa,pb,kind,500,SEED,shuffled) for kind in KINDS)
        out['controls']['leakage']=leakage
        for r in leakage: emit('Leakage',{k:v for k,v in r.items() if k!='permutation_accuracies'})
        save()
        negative_results=[]
        for start in range(0,100,6):
            negative_results.extend(Parallel(n_jobs=6)(delayed(negative)(pa,i) for i in range(start,min(start+6,100))))
            print(f'Negative control completed {len(negative_results)}/100',flush=True)
        valid=[r['p'] for r in negative_results if r['p'] is not None]
        out['controls']['negative']=dict(splits=negative_results,computable=len(valid),share_p_under_05=sum(p<.05 for p in valid)/len(valid) if valid else None)
        emit('Negative control',{k:v for k,v in out['controls']['negative'].items() if k!='splits'})
        passed=[k for k in KINDS if out['gates'][k]['G2']['accuracy'] is not None and out['gates'][k]['G2']['accuracy']>=.65 and out['gates'][k]['G2']['p'] is not None and out['gates'][k]['G2']['p']<.01]
        out['passed']=passed; emit('Passed',passed); save()
    if not passed:
        out['status']='E3 void'; print('E3 void',flush=True); save(); return
    if '--step1-only' in sys.argv:
        out['status']='Step 1 complete'; save(); return
    with (HERE/'research_stylometry2.step2.lock').open('x') as f:
        f.write('Step 2 started once '+time.ctime()+'\n')
    definitions=[]
    for g,offset,special,plus,minus in [('matthew',0,'M*','MK+L','MK-L'),('luke',4,'L*','MK+M','MK-M')]:
        dt,sp,pl,mi=P(g,'DT'),P(g,special),P(g,plus),P(g,minus)
        definitions.extend([(offset+1,g,'DT vs '+special,dt,sp),(offset+2,g,plus+' vs '+minus,pl,mi),(offset+3,g,'Markan vs DT',pl+mi,dt),(offset+4,g,'Markan vs '+special,pl+mi,sp)])
    definitions.extend([('1-secondary','matthew','DT vs M',P('matthew','DT'),P('matthew','M')),(9,'mark','taken vs not taken by Luke',P('mark','taken by Lk'),P('mark','not taken by Lk')),(10,'mark','taken vs not taken by Matthew',P('mark','taken by Mt'),P('mark','not taken by Mt'))])
    jobs = []
    for cid,g,label,a,b in definitions:
        for kind in passed:
            if cid == 6 and min(score(a+b,np.array([0]*len(a)+[1]*len(b)),kind)[2]['chunks']) < 6:
                _,_,cnt=score(a+b,np.array([0]*len(a)+[1]*len(b)),kind)
                r=dict(instrument=kind,accuracy=None,p=None,gap='too few',**cnt,id=cid,gospel=g,contrast=label)
                out['comparisons'].append(r); emit('Comparison',r)
            else:
                jobs.append((cid,g,label,a,b,kind))
    results = Parallel(n_jobs=6, return_as='generator')(
        delayed(contrast)(a,b,kind) for cid,g,label,a,b,kind in jobs)
    for (cid,g,label,a,b,kind),r in zip(jobs,results):
        r.update(id=cid,gospel=g,contrast=label); out['comparisons'].append(r)
        emit('Comparison',{k:v for k,v in r.items() if k!='permutation_accuracies'}); save()
    for g,ids,special,plus,minus in [('matthew',range(1,5),'M*','MK+L','MK-L'),('luke',range(5,9),'L*','MK+M','MK-M')]:
        chunk_counts=[sum(len(u) for u in c.chunk_units(P(g,cl),TokenScope({k:j for j,p in enumerate(P(g,cl)) for k in p}))) for cl in ['DT',special,plus,minus]]
        if g=='luke' and chunk_counts[-1]<6:
            out['matched'][g]=dict(gap='MK-M has fewer than 6 chunks'); continue
        n=min(chunk_counts)
        for kind in passed:
            series={}
            for cid in ids:
                _,_,_,a,b=next(d for d in definitions if d[0]==cid)
                draws=Parallel(n_jobs=6)(delayed(matched)(a,b,kind,n,i) for i in range(100))
                values=[v for v,gap in draws]
                summary=dict(n=n,values=values,gaps=[gap for v,gap in draws])
                if all(v is not None for v in values):
                    summary.update(mean=float(np.mean(values)),percentiles=np.percentile(values,[2.5,97.5]).tolist())
                series[str(cid)]=summary; emit('Matched',dict(instrument=kind,id=cid,**{k:v for k,v in summary.items() if k not in ['values','gaps']}))
            out['matched'].setdefault(g,{})[kind]=series
            aa,bb=series[str(min(ids))]['values'],series[str(min(ids)+1)]['values']
            if all(v is not None for v in aa+bb):
                diff=np.array(aa)-np.array(bb)
                r=dict(mean=float(diff.mean()),percentiles=np.percentile(diff,[2.5,97.5]).tolist(),values=diff.tolist())
                out['differences'].setdefault(g,{})[kind]=r; emit('Difference',dict(gospel=g,instrument=kind,mean=r['mean'],percentiles=r['percentiles']))
            save()
    out['status']='complete'; save()

if __name__ == '__main__':
    class Tee:
        def __init__(self, stream, file): self.stream,self.file=stream,file
        def write(self, text): self.stream.write(text); self.file.write(text)
        def flush(self): self.stream.flush(); self.file.flush()
    with (HERE/'research_stylometry2.txt').open('a' if '--resume-step2' in sys.argv else 'w') as log:
        sys.stdout=Tee(sys.stdout,log)
        try:
            main()
        finally:
            sys.stdout = sys.stdout.stream
