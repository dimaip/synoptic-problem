#!/usr/bin/env python3
"""Frozen hide-Mark literal recovery calibration. Writes only its .json and .txt.
Usage: python3 -B tools/research_hide_mark.py [DATA_DIRECTORY]
"""
import os
import sys
sys.dont_write_bytecode = True
os.environ['E3_DATA'] = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else '~/Documents/ChatGPT/gospel/public/data')
import json
import hashlib
from pathlib import Path
from collections import defaultdict
import numpy as np
import research_common as c

SEED = 20261116
B = 2000
STRATA = ['all', 'Jesus', 'other speech', 'narrator', 'Jesus short', 'Jesus long', 'Jesus outside sayings verses']


def labels(book):
    """Full-Gospel, same-chapter consecutive >=80%-Jesus verses; length in all words."""
    short = {}
    sayings = [k for k in c.VERSE if k[0] == book and c.K['jesus_share'](k) >= .8]
    for run in c.runs(sayings):
        size = sum(len(c.VERSE[k]) for k in run)
        for k in run:
            short[k] = size < 40
    result = {}
    for k in c.VERSE:
        if k[0] != book:
            continue
        for i in c.VERSE[k]:
            t = c.TOK[i]
            s = {'all', 'Jesus' if t['jesus'] else 'other speech' if t['speech'] else 'narrator'}
            if t['jesus']:
                s.add('Jesus short' if short.get(k) is True else 'Jesus long' if short.get(k) is False else 'Jesus outside sayings verses')
            result[i] = s
    return result


def extract(ml_links, minimum):
    """Accept pairs in diagonal consecutive-token runs. Receives no Mark tokens or links."""
    pairs = set(ml_links)
    accepted = set()
    for m, l in sorted(pairs):
        if (m - 1, l - 1) in pairs:
            continue
        run = []
        while (m + len(run), l + len(run)) in pairs:
            run.append((m + len(run), l + len(run)))
        if len(run) >= minimum:
            accepted.update(run)
    return accepted


def summarize(rows, draws):
    a = np.array(rows, dtype=int)
    sums = a.sum(axis=0)
    bs = a[draws].sum(axis=1)
    result = dict(zip(['recovered_Mark', 'Mark_words', 'matched_pseudo', 'pseudo_words'], map(int, sums)))
    for name, hit, den in [('recall', 0, 1), ('precision', 2, 3)]:
        valid = bs[:, den] > 0
        result[name] = float(sums[hit] / sums[den]) if sums[den] else None
        result[name + '_ci95'] = np.quantile(bs[valid, hit] / bs[valid, den], [.025, .975]).tolist() if valid.any() else None
        result[name + '_valid_resamples'] = int(valid.sum())
    return result


def main():
    mlabel, klabel = labels('matthew'), labels('mark')
    candidates = []
    for g in c.groups:
        books = {p['book'] for p in g['passages']}
        if not g['correspondence'] or not {'mark', 'matthew', 'luke'} <= books:
            continue
        verses = defaultdict(set)
        primary = set()
        for p in g['passages']:
            for ref in p['verses']:
                ch, v = map(int, ref.split(':'))
                k = (p['book'], ch, v)
                verses[p['book']].add(k)
                if p['book'] == 'mark' and p.get('primary', False):
                    primary.add(k)
        if any(c.CL.get(k) in {'Q', 'Q+Mark overlap'} for k in verses['luke']):
            continue
        candidates.append((g, verses, primary))
    owner = {}
    for j, (_, vs, primary) in enumerate(candidates):
        for k in vs['mark']:
            if k not in owner or (k in primary and k not in candidates[owner[k]][2]):
                owner[k] = j
    episodes = []
    for j, (g, vs, _) in enumerate(candidates):
        kv = sorted(k for k in vs['mark'] if owner[k] == j and c.VERSE[k])
        if not kv:
            continue
        ids = {b: {i for k in vs[b] for i in c.VERSE[k]} for b in ('matthew', 'luke')}
        # Project only Matthew/Luke before extraction; Mark is revealed below for scoring.
        links = c.pack['greekAlignment']['groups'].get(g['id'], {}).get('links', [])
        ml = []
        for link in links:
            ms = [i for i in link if i in ids['matthew']]
            ls = [i for i in link if i in ids['luke']]
            ml.extend((m, l) for m in ms for l in ls)
        pseudo = {minimum: extract(ml, minimum) for minimum in (2, 1)}
        episodes.append((g['id'], kv, links, pseudo))
    draws = np.random.default_rng(SEED).integers(0, len(episodes), size=(B, len(episodes)))
    output = {'seed': SEED, 'bootstrap_resamples': B, 'episodes': len(episodes), 'variants': {}, 'methods': [
        'Eligible correspondence groups exclude every group containing a Q or Q+Mark-overlap Luke verse (shared CL). Mark verses assigned primary eligible group, otherwise first; empty groups omitted.',
        'Extraction uses group-restricted Matthew-Luke links only, with original integer token adjacency on both sides. Pseudo-source is unique Matthew token occurrences per episode. No SUPPLEMENT extraction.',
        'Recall requires the very same three-way link in that episode and assigned Mark verses. Other pairwise links and alternative locations do not count.',
        'Precision uses Matthew annotation proxies, explicitly authorized: numerator matched pseudo tokens / all pseudo tokens with that Matthew stratum. Recall uses Mark strata. These are different strata populations.',
        'Sayings runs computed across each entire Gospel before episode selection, same chapter, consecutive verse numbers, >=80% Jesus tokens per verse; 40-word threshold counts all words. Jesus tokens outside those verses reported separately.',
        'Secondary removes scripture tokens on all three sides AFTER extraction; preserves frozen runs, strata and episodes, never bridges deleted words.',
        '95% percentile bootstrap: 2000 episode resamples, same seeded draws throughout; undefined denominators omitted with valid counts.',
        'Whole-Mark denominator includes every token in all 16 chapters of this OpenGNT dataset; outside-episode words unrecovered. Whole precision equals selected-episode precision.',
        'Alternative exact-form locations and uncertainty flags are diagnostics, never additional recovery credit. Three-way means aligned correspondence, not historical certainty.'
    ]}
    for minimum, variant in [(2, 'main'), (1, 'B')]:
        output['variants'][variant] = {}
        for no_scripture in (False, True):
            rows = {s: [] for s in STRATA}
            records = []
            recovered_all = set()
            for gid, kv, links, pseudo in episodes:
                mark = {i for k in kv for i in c.VERSE[k] if not no_scripture or not c.TOK[i]['scripture']}
                pairs = {(m, l) for m, l in pseudo[minimum] if not no_scripture or not (c.TOK[m]['scripture'] or c.TOK[l]['scripture'])}
                ps = {m for m, l in pairs}
                recovered, matched = set(), set()
                for link in links:
                    for m, l in pairs:
                        if m in link and l in link:
                            ks = mark.intersection(link)
                            if ks:
                                recovered.update(ks)
                                matched.add(m)
                assert recovered <= mark and matched <= ps
                recovered_all.update(recovered)
                for s in STRATA:
                    ks = {i for i in mark if s in klabel[i]}
                    ms = {i for i in ps if s in mlabel[i]}
                    rows[s].append([len(ks & recovered), len(ks), len(ms & matched), len(ms)])
                # Count uncredited pseudo words that have an identical form somewhere in this episode.
                forms = {c.K['formkey'](c.TOK[i]['text']) for i in mark}
                alt = sum(c.K['formkey'](c.TOK[i]['text']) in forms for i in ps - matched)
                uncertain = set(c.pack['greekAlignment']['groups'].get(gid, {}).get('uncertain', []))
                records.append({'id': gid, 'Mark_verses': [f'{k[1]}:{k[2]}' for k in kv], 'Mark_words': len(mark), 'pseudo_words': len(ps), 'recovered_Mark': len(recovered), 'matched_pseudo': len(matched), 'extra_shared_words': len(ps - matched), 'alternative_form_locations_uncredited': alt, 'uncertain_Mark_tokens': len(mark & uncertain), 'verses_no_recovered_word': sum(not (set(c.VERSE[k]) & recovered) for k in kv), 'recall': len(recovered)/len(mark) if mark else None, 'precision': len(matched)/len(ps) if ps else None, 'pseudo_token_ids': sorted(ps), 'recovered_Mark_token_ids': sorted(recovered)})
            whole = {i for k in c.VERSE if k[0] == 'mark' for i in c.VERSE[k] if not no_scripture or not c.TOK[i]['scripture']}
            dist = {}
            for metric in ('recall', 'precision'):
                xs = [r[metric] for r in records if r[metric] is not None]
                dist[metric + '_quartiles'] = np.quantile(xs, [.25, .5, .75]).tolist()
                dist[metric + '_defined_episodes'] = len(xs)
            dist.update(zero_recall_episodes=sum(r['recall'] == 0 for r in records), no_pseudo_source_episodes=sum(not r['pseudo_words'] for r in records), Mark_verses=len(owner), verses_no_recovered_word=sum(r['verses_no_recovered_word'] for r in records))
            dist['share_verses_no_recovered_word'] = dist['verses_no_recovered_word']/sum(len(r['Mark_verses']) for r in records)
            output['variants'][variant]['no_scripture' if no_scripture else 'primary'] = {'strata': {s: summarize(rows[s], draws) for s in STRATA}, 'whole_Mark': {'words': len(whole), 'recovered': len(recovered_all), 'recall': len(recovered_all)/len(whole)}, 'distribution': dist, 'episodes': records}
    comparison = {}
    for book, verses, other in [('luke', [k for k in c.VERSE if k[0] == 'luke' and c.CL[k] == 'Q' and c.K['jesus_share'](k) >= .8], 'matthew'), ('matthew', [k for k in c.K['mat'] if c.K['MC'][k] == 'Q'], 'luke')]:
        h, n = c.K['rate'](verses, other)
        comparison[book] = {'matched': h, 'words': n, 'percent': 100*h/n, 'matches_published_1dp': round(100*h/n, 1) == (41.1 if book == 'luke' else 48.3)}
    output['double_tradition'] = comparison
    output['inputs_sha256'] = {name: hashlib.sha256((Path(c.DATA)/name).read_bytes()).hexdigest() for name in ('net.json', 'opengnt.json')}
    output['limits'] = ['Literal identical-form intersection misses paraphrase, inflection changes, reordered matches, and independent alignment misses; not a reconstruction-method performance estimate.', 'Broad Aland episodes need not delimit actual source use; Q exclusion and primary assignment restrict coverage. Existing alignments were originally computed with Mark visible: computational projection is not a newly blinded alignment.', 'Alternative identical locations are not adjudicated; speech/scripture annotations and text edition affect counts. Bootstrap describes episode resampling, not uncertainty in text, alignment, source boundaries or historical dependence.', 'Pseudo-source Matthew tokens can recur across episodes; Mark tokens never do. Precision strata use Matthew proxies and need not agree with Mark speaker or run-length labels. No inference ranking Synoptic hypotheses.']
    here = Path(__file__).resolve().parent
    (here/'research_hide_mark.json').write_text(json.dumps(output, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    lines = ['Hide Mark calibration', f'Episodes: {len(episodes)}; seed {SEED}; bootstrap {B}', *output['methods']]
    for variant, sensitivities in output['variants'].items():
        for sensitivity, result in sensitivities.items():
            lines += ['', variant+' / '+sensitivity]
            for s, r in result['strata'].items():
                lines.append(s+': '+json.dumps(r))
            lines += ['Whole Mark: '+json.dumps(result['whole_Mark']), 'Episode distribution: '+json.dumps(result['distribution'])]
    lines += ['', 'Double tradition: '+json.dumps(comparison), '', 'Limits:', *output['limits'], '', 'Changes: created only research_hide_mark.py, .txt and .json. OpenGNT 3.3 / Synoptic Canvas automatic alignment; OpenGNT CC BY-SA 4.0.']
    report = '\n'.join(lines)+'\n'
    (here/'research_hide_mark.txt').write_text(report)
    print(report)


if __name__ == '__main__':
    main()
