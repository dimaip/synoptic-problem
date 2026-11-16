#!/usr/bin/env python3
"""E4 pre-registered overlap count on read-only Synoptic Canvas data.

Usage: python3 tools/research_overlaps.py [DATA_DIRECTORY]
Writes only research_overlaps.txt and research_overlaps.json beside this script.
Identical forms and greedy matching reproduce kloppenborg_test.py SUPPLEMENT.
"""
import os
import sys
import json
import random
from pathlib import Path
from collections import defaultdict
import numpy as np

os.environ['E3_DATA'] = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else '~/Documents/ChatGPT/gospel/public/data')
import research_common as c

PASSAGES = [
 ('P1','John on the coming one','1:7-8','3:11-12','3:16-17'),
 ('P2','Temptation','1:12-13','4:1-11','4:1-13'),
 ('P3','Beelzebul','3:22-27','12:22-30','11:14-23'),
 ('P4','Blasphemy against the Spirit','3:28-30','12:31-32','12:10'),
 ('P5','Mustard seed','4:30-32','13:31-32','13:18-19'),
 ('P6','Mission charge','6:7-13','10:1, 7-16','10:1-12'),
 ('S1','Lamp','4:21','5:15','11:33'),
 ('S2','Hidden and revealed','4:22','10:26','12:2'),
 ('S3','Measure','4:24','7:2','6:38'),
 ('S4','To the one who has','4:25','25:29','19:26'),
 ('S5','Sign of Jonah','8:11-12','12:38-42','11:16, 29-32'),
 ('S6','Taking up the cross','8:34','10:38','14:27'),
 ('S7',"Losing one's life",'8:35','10:39','17:33'),
 ('S8','Confessing and denying','8:38','10:32-33','12:8-9'),
 ('S9','Receiving the one sent','9:37','10:40','10:16'),
 ('S10','Causes of stumbling','9:42','18:6-7','17:1-2'),
 ('S11','Salt','9:49-50','5:13','14:34-35'),
 ('S12','Divorce','10:11-12','5:32','16:18'),
 ('S13','First and last','10:31','20:16','13:30'),
 ('S14','Faith that moves','11:22-23','17:20','17:6'),
 ('S15','The Spirit will speak','13:11','10:19-20','12:11-12'),
 ('S16','Lightning and the false alarms','13:21-23','24:23-28','17:23-24, 37'),
 ('S17','Best seats','12:38-39','23:6-7','11:43'),
]
READING = '''- If Luke copied these passages from Matthew's text, he should reproduce Matthew's Markan words at
  least as often as Matthew's other words: R at or above 1.
- If Luke had the non-Markan version only (Q), he should have Matthew's non-Markan words and few of
  Matthew's Markan ones: R clearly below 1.
- R clearly below 1 (pooled primary interval wholly below 1, and below 1 in at least five of the
  six primary passages): the "unpicking" observation is a fact, and is a difficulty for Luke's use
  of Matthew. R at or above 1: the observation fails. In between: inconclusive.
- A high `Lk_Mark_only` in a passage means Luke also drew on Mark there, which every hypothesis allows.'''
CELLS = 'abcdef'
RATES = ('rMK','rNOT','R','Lk_Mark_only')
SEED = 20261116


def align(left, right):
    """Literal SUPPLEMENT algorithm; ties sort by descending (length,left,right).

    Ordered arguments are Matthew-Mark, Matthew-Luke, Mark-Luke. The original
    singleton pass checks exactly one free RIGHT counterpart, not uniqueness on
    both sides. Preserve that rule, minimum four letters, and token-ID adjacency.
    """
    kl = [c.K['formkey'](c.TOK[i]['text']) for i in left]
    kr = [c.K['formkey'](c.TOK[i]['text']) for i in right]
    candidates = []
    for a in range(len(left)):
        for b in range(len(right)):
            if kl[a] != kr[b] or (a and b and kl[a-1] == kr[b-1]):
                continue
            n = 0
            while (a+n < len(left) and b+n < len(right) and kl[a+n] == kr[b+n]
                   and left[a+n] == left[a]+n and right[b+n] == right[b]+n):
                n += 1
            if n >= 2:
                candidates.append((n,a,b))
    used_left, used_right, pairs = set(), set(), set()
    for n,a,b in sorted(candidates, reverse=True):
        if any(a+i in used_left or b+i in used_right for i in range(n)):
            continue
        for i in range(n):
            used_left.add(a+i)
            used_right.add(b+i)
            pairs.add((left[a+i],right[b+i]))
    for a in range(len(left)):
        if a in used_left or c.TOK[left[a]]['gram'] or len(kl[a]) < 4:
            continue
        free = [b for b in range(len(right)) if b not in used_right and kr[b] == kl[a]]
        if len(free) == 1:
            used_left.add(a)
            used_right.add(free[0])
            pairs.add((left[a],right[free[0]]))
    assert len(pairs) == len({x for x,y in pairs}) == len({y for x,y in pairs})
    assert all(c.K['formkey'](c.TOK[x]['text']) == c.K['formkey'](c.TOK[y]['text']) for x,y in pairs)
    return pairs


def count(matthew, mark, mm, ml, kl, content=False):
    """Classify source tokens; independently computed pairs need not be transitive."""
    mk = {x for x,y in mm}
    lk = {x for x,y in ml}
    mt = {y for x,y in mm}
    lk_from_mark = {x for x,y in kl}
    cells = dict.fromkeys(CELLS,0)
    for i in matthew:
        if content and c.TOK[i]['gram']:
            continue
        cells['a' if i in mk and i in lk else 'b' if i in mk else 'c' if i in lk else 'd'] += 1
    for i in mark:
        if i not in mt and not (content and c.TOK[i]['gram']):
            cells['e' if i in lk_from_mark else 'f'] += 1
    assert sum(cells[k] for k in 'abcd') == sum(not content or not c.TOK[i]['gram'] for i in matthew)
    return cells


def rates(cells):
    a,b,cc,d,e,f = [cells[k] for k in CELLS]
    mk = a/(a+b) if a+b else None
    other = cc/(cc+d) if cc+d else None
    return dict(rMK=mk, rNOT=other, R=mk/other if mk is not None and other else None,
                Lk_Mark_only=e/(e+f) if e+f else None)


def pool(records):
    """Percentile intervals of pooled ratios, 5,000 passage resamples."""
    total = {k:sum(r[k] for r in records) for k in CELLS}
    rng = random.Random(SEED)
    samples = {k:[] for k in RATES}
    for _ in range(5000):
        chosen = [rng.choice(records) for _ in records]
        values = rates({k:sum(r[k] for r in chosen) for k in CELLS})
        for k,v in values.items():
            if v is not None:
                samples[k].append(v)
    return dict(**total, **rates(total), ci95={k:np.percentile(v,[2.5,97.5]).tolist() if v else None for k,v in samples.items()},
                valid_resamples={k:len(v) for k,v in samples.items()}, passages=len(records))


def main():
    # Raw canvas edges: do not accidentally include loader SUPPLEMENT edges.
    canvas = defaultdict(set)
    group_pairs = {}
    group_tokens_by_id = {}
    for group in c.groups:
        group_tokens_by_id[group['id']] = {i for passage in group['passages'] for ref in passage['verses']
            for i in c.VERSE[(passage['book'], *map(int, ref.split(':')))]}
    for gid,group in c.pack['greekAlignment']['groups'].items():
        edges = defaultdict(set)
        for link in group['links']:
            for x in link:
                for y in link:
                    if c.TOK[x]['book'] != c.TOK[y]['book']:
                        canvas[x].add(y)
                        edges[(c.TOK[x]['book'],c.TOK[y]['book'])].add((x,y))
        group_pairs[gid] = edges
    output = dict(seed=SEED, bootstrap_resamples=5000, data=os.environ['E3_DATA'], passages=[], pooled={}, aligner_check=[], baselines={}, changes=['Fixed canvas-check denominator to include all tokens printed in a group, including unlinked tokens; experiment counts unchanged.'])
    variants = {'all':[], 'content':[], 'no_scripture':[]}
    for pid,name,ks,ms,ls in PASSAGES:
        seq = {book:c.K['_ids'](book,spec) for book,spec in [('mark',ks),('matthew',ms),('luke',ls)]}
        assert all(seq.values())
        rec = dict(id=pid,name=name,mark=ks,matthew=ms,luke=ls)
        for variant in variants:
            selected = {b:[i for i in ids if variant != 'no_scripture' or not c.TOK[i]['scripture']] for b,ids in seq.items()}
            m,k,l = [selected[b] for b in ('matthew','mark','luke')]
            mm,ml,kl = align(m,k),align(m,l),align(k,l)
            cells = count(m,k,mm,ml,kl,variant=='content')
            variants[variant].append(cells)
            rec[variant] = dict(**cells,**rates(cells))
            if variant == 'all':
                # A qualifying group must contain restricted edges for all three pairs.
                for gid,edges in group_pairs.items():
                    cm = {(x,y) for x,y in edges[('matthew','mark')] if x in seq['matthew'] and y in seq['mark']}
                    cl = {(x,y) for x,y in edges[('matthew','luke')] if x in seq['matthew'] and y in seq['luke']}
                    ck = {(x,y) for x,y in edges[('mark','luke')] if x in seq['mark'] and y in seq['luke']}
                    if cm and cl and ck:
                        check = dict(id=pid,group=gid)
                        for label,ours,theirs in [('Matthew-Mark',mm,cm),('Matthew-Luke',ml,cl)]:
                            # Restrict our edges to tokens actually printed in this group.
                            group_tokens = group_tokens_by_id[gid]
                            restricted = {(x,y) for x,y in ours if x in group_tokens and y in group_tokens}
                            check[label] = dict(agree=len(restricted & theirs),ours=len(restricted),canvas=len(theirs))
                        output['aligner_check'].append(check)
        output['passages'].append(rec)
    for variant,records in variants.items():
        output['pooled'][variant] = dict(primary=pool(records[:6]),secondary=pool(records))
    # Baselines select whole Matthew verses, then count every Matthew token.
    for label in ('B1','B2'):
        chosen=[]
        total=dict.fromkeys('abcd',0)
        for verse,ids in c.VERSE.items():
            if verse[0] != 'matthew':
                continue
            mk=sum(any(c.TOK[j]['book']=='mark' for j in canvas[i]) for i in ids)
            lclasses=[c.CL.get(('luke',c.TOK[j]['ch'],c.TOK[j]['v'])) for i in ids for j in canvas[i] if c.TOK[j]['book']=='luke']
            lq=sum(any(c.TOK[j]['book']=='luke' and c.CL.get(('luke',c.TOK[j]['ch'],c.TOK[j]['v']))=='Q' for j in canvas[i]) for i in ids)
            include = (mk>=3 and 'luke' in c.PAR[verse] and not any(cl in ('Q','Q+Mark overlap') for cl in lclasses)) if label=='B1' else (lq>=2 and mk<3)
            if not include:
                continue
            chosen.append(f'{verse[1]}:{verse[2]}')
            for i in ids:
                books={c.TOK[j]['book'] for j in canvas[i]}
                total['a' if {'mark','luke'}<=books else 'b' if 'mark' in books else 'c' if 'luke' in books else 'd']+=1
        result=dict(verses=len(chosen), verse_refs=chosen, **total)
        values=rates(dict(**total,e=0,f=0))
        result.update({k:values[k] for k in ('rMK','rNOT','R')} if label=='B1' else dict(rNOT=values['rNOT']))
        output['baselines'][label]=result
    primary=output['pooled']['all']['primary']
    below=sum(r['all']['R'] is not None and r['all']['R']<1 for r in output['passages'][:6])
    output['reading_result'] = ('the "unpicking" observation is a fact, and is a difficulty for Luke\'s use of Matthew' if primary['ci95']['R'][1]<1 and below>=5 else 'the observation fails' if primary['R']>=1 else 'inconclusive')
    output['primary_passages_R_below_1']=below
    output['aligner_check_summary'] = {}
    for label in ('Matthew-Mark','Matthew-Luke'):
        # Union token pairs over eligible groups, so repeated Aland presentations count once.
        ours, theirs = set(), set()
        for check in output['aligner_check']:
            record = next(r for r in output['passages'] if r['id'] == check['id'])
            left = c.K['_ids']('matthew',record['matthew'])
            book = 'mark' if label == 'Matthew-Mark' else 'luke'
            right = c.K['_ids'](book,record[book])
            printed = group_tokens_by_id[check['group']]
            ours |= {(x,y) for x,y in align(left,right) if x in printed and y in printed}
            theirs |= {(x,y) for x,y in group_pairs[check['group']][('matthew',book)] if x in left and y in right}
        output['aligner_check_summary'][label] = dict(agree=len(ours & theirs),ours=len(ours),canvas=len(theirs))
    output['methods'] = ['Exact SUPPLEMENT rules; arguments Matthew-Mark, Matthew-Luke, Mark-Luke.', 'Content sensitivity filters counted source tokens after full alignment, using T-, CONJ, PREP, PRT, P-, R-, D-.', 'No-scripture sensitivity removes scripture-tagged tokens from all three sequences before re-aligning; token-ID adjacency still required.', 'Canvas check requires at least one edge in each of three passage-restricted pairs within a single group; agreement is exact token-pair intersection.', 'Baseline uses raw canvas edges, not SUPPLEMENT additions; CL and PAR from shared loader.', 'Undefined ratios are null; intervals omit undefined resamples and report valid counts.', 'Six passages make the primary interval rough. Automatic identical-form alignment misses inflection changes and synonyms; independent pairs need not be transitive.']
    here=Path(__file__).resolve().parent
    (here/'research_overlaps.json').write_text(json.dumps(output,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    lines=['E4: Mark-Q overlaps', 'This list was written from the standard lists of overlap texts before any count was made.', 'id | passage | Mark | Matthew | Luke']
    lines += [' | '.join(p) for p in PASSAGES]
    lines += ['', 'Pre-stated reading (unchanged)',READING,'','Methods']+output['methods']
    lines += ['Seed: '+str(SEED)+'; 5,000 passage bootstrap resamples; 95% percentile intervals.','Changes / bug fixes: '+ '; '.join(output['changes']),'', 'Per-passage records (rates are proportions)']
    lines += [json.dumps(r,ensure_ascii=False) for r in output['passages']]
    for key in ('pooled','aligner_check','aligner_check_summary','baselines','reading_result','primary_passages_R_below_1'):
        lines += ['',key,json.dumps(output[key],ensure_ascii=False,indent=2)]
    report='\n'.join(lines)+'\n'
    (here/'research_overlaps.txt').write_text(report)
    print(report)

if __name__=='__main__':
    main()
