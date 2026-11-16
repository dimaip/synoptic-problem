#!/usr/bin/env python3
"""Bounded apparatus-screened phrase audit.
Run: PYTHONDONTWRITEBYTECODE=1 python3 tools/research_minor_agreements.py [data-dir]
Writes only the adjacent .txt and .json. No supplemental realignment is used.
"""
import os
import sys
import json
import re
import hashlib
from pathlib import Path
from collections import defaultdict, Counter
sys.dont_write_bytecode = True
os.environ['E3_DATA'] = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else '~/Documents/ChatGPT/gospel/public/data')
import research_common as c

# Frozen verbatim verse lists from RESEARCH-E4.md, in Mark / Matthew / Luke order.
EXCLUSIONS = [
('1:7-8','3:11-12','3:16-17'),('1:12-13','4:1-11','4:1-13'),
('3:22-27','12:22-30','11:14-23'),('3:28-30','12:31-32','12:10'),
('4:30-32','13:31-32','13:18-19'),('6:7-13','10:1,7-16','10:1-12'),
('4:21','5:15','11:33'),('4:22','10:26','12:2'),('4:24','7:2','6:38'),
('4:25','25:29','19:26'),('8:11-12','12:38-42','11:16,29-32'),
('8:34','10:38','14:27'),('8:35','10:39','17:33'),('8:38','10:32-33','12:8-9'),
('9:37','10:40','10:16'),('9:42','18:6-7','17:1-2'),('9:49-50','5:13','14:34-35'),
('10:11-12','5:32','16:18'),('10:31','20:16','13:30'),('11:22-23','17:20','17:6'),
('13:11','10:19-20','12:11-12'),('13:21-23','24:23-28','17:23-24,37'),
('12:38-39','23:6-7','11:43')]
EXCLUDED = {v for row in EXCLUSIONS for book,spec in zip(('mark','matthew','luke'),row) for v in c.K['span'](book,spec)}
APP = Path.home()/'Documents/ChatGPT/gospel/public/na28/chapters'
key = c.K['formkey']


def refs(ids):
    return ', '.join(dict.fromkeys(f"{c.TOK[i]['ch']}:{c.TOK[i]['v']}" for i in ids))


def screen(ids):
    """Literal normalized substring matches; omission/addition signs at verse scope.

    Include entries anchored earlier whose structured unit range covers the verse.
    Omission/addition units are located in the printed NA28 token stream; repeated
    candidate forms conservatively match every position with that form.
    """
    hits = []
    for book,ch,v in sorted({(c.TOK[i]['book'],c.TOK[i]['ch'],c.TOK[i]['v']) for i in ids}):
        data = apparatus[(book,ch)]
        forms = {key(c.TOK[i]['text']) for i in ids if (c.TOK[i]['book'],c.TOK[i]['ch'],c.TOK[i]['v']) == (book,ch,v)}
        spanning = {u['entryId'] for u in data['units'] if u.get('range',{}).get('verse',u['verse']) <= v <= u.get('range',{}).get('verseEnd',u['verse'])}
        for entry in data['apparatus']:
            if entry['verse'] != v and entry['id'] not in spanning:
                continue
            text = ''.join(r['t'] for r in entry['runs'])
            matched = sorted(f for f in forms if f and f in key(text))
            positions = {n for verse in data['text'] if verse['verse']==v
                         for n,t in enumerate(verse['tokens']) if t['k']=='word' and key(t['t']) in forms}
            signs = False
            for unit in data['units']:
                if unit['entryId'] != entry['id'] or unit['kind'] not in ('omission','insertion'):
                    continue
                lemma = unit['lemma']
                start_v = int(lemma['verseId'][-3:])
                end_v = int(lemma.get('toVerseId',lemma['verseId'])[-3:])
                if not start_v <= v <= end_v:
                    continue
                lo = lemma['from'] if v==start_v else 0
                hi = lemma['to'] if v==end_v else 100000
                if unit['kind']=='insertion':
                    # A sign occupies a token slot between printed words.
                    signs |= any(abs(pos-lo)<=2 for pos in positions)
                else:
                    signs |= any(lo<=pos<=hi for pos in positions)
            if matched or signs:
                hits.append(dict(book=book,chapter=ch,verse=v,entry=entry['id'],text=text,matched_forms=matched,localized_omission_addition=signs))
    return hits


def main():
    global apparatus
    apparatus = {}
    for book in ('matthew','luke'):
        for ch in range(1,29 if book=='matthew' else 25):
            apparatus[(book,ch)] = json.loads((APP/book/f'{ch}.json').read_text())
    episodes, excluded = [], []
    for g in c.groups:
        books = {p['book'] for p in g['passages']}
        if not g['correspondence'] or not {'mark','matthew','luke'} <= books:
            continue
        verses = {(p['book'],*map(int,r.split(':'))) for p in g['passages'] for r in p['verses'] if p['book'] in ('mark','matthew','luke')}
        reasons = []
        if any(c.CL.get(v) in ('Q','Q+Mark overlap') for v in verses if v[0]=='luke'): reasons.append('Luke Q / Q+Mark overlap')
        if verses & EXCLUDED: reasons.append('E4 verse intersection (any of three books)')
        if reasons:
            excluded.append(dict(id=g['id'],reasons=reasons)); continue
        seq = {b:sorted({i for v in verses if v[0]==b for i in c.VERSE[v] if not c.TOK[i]['scripture']}) for b in ('mark','matthew','luke')}
        episodes.append((g,seq))
    frequency = Counter()
    for i in {i for _,s in episodes for ids in s.values() for i in ids}:
        frequency[('speech' if c.TOK[i]['speech'] else 'narrative',c.LEMMA[i])] += 1
    multi, single, controls = {}, {}, []
    for g,seq in episodes:
        a = c.pack['greekAlignment']['groups'].get(g['id'],{'links':[]})
        edges = defaultdict(set)
        for link in a['links']:
            for x in link:
                edges[x].update(y for y in link if c.TOK[y]['book'] != c.TOK[x]['book'])
        mklemmas = {c.LEMMA[i] for i in seq['mark']}
        luke = set(seq['luke'])
        # Keep all possible supplied paths, never silently pick a competing partner.
        pairs = {(m,l) for m in seq['matthew'] if not any(c.TOK[j]['book']=='mark' for j in edges[m]) for l in edges[m] if l in luke and not any(c.TOK[j]['book']=='mark' for j in edges[l]) and key(c.TOK[m]['text'])==key(c.TOK[l]['text'])}
        paths = []
        for m,l in sorted(pairs):
            if (m-1,l-1) in pairs: continue
            n=1
            while (m+n,l+n) in pairs: n+=1
            paths.append((list(range(m,m+n)),list(range(l,l+n))))
        def record(ms,ls):
            absent = sorted({c.LEMMA[i] for i in ms if c.LEMMA[i] not in mklemmas})
            hits = screen(ms+ls)
            uncertain = set(a.get('uncertain',[]))
            return dict(matthew=refs(ms),luke=refs(ls),mark=refs(seq['mark']),phrase=' '.join(c.TOK[i]['text'] for i in ms),matthew_ids=ms,luke_ids=ls,length=len(ms),content_words=sum(not c.TOK[i]['gram'] for i in ms),absent_lemmas=absent,speech_or_narrative='/'.join(sorted({'speech' if c.TOK[i]['speech'] else 'narrative' for i in ms+ls})),alignment_flag=bool(uncertain.intersection(ms+ls)) or any(len([j for j in edges[i] if c.TOK[j]['book'] in ('luke','matthew')])>1 for i in ms+ls),apparatus_touched=bool(hits),apparatus=hits,episodes=[g['id']],lemma_frequency=[dict(lemma=c.LEMMA[i],stratum='speech' if c.TOK[i]['speech'] else 'narrative',occurrences=frequency[('speech' if c.TOK[i]['speech'] else 'narrative',c.LEMMA[i])]) for i in ms if not c.TOK[i]['gram']])
        for ms,ls in paths:
            if len(ms)<2 or not any(c.LEMMA[i] not in mklemmas for i in ms): continue
            k=tuple(ms)
            if k in multi:
                multi[k]['episodes'].append(g['id'])
                multi[k].setdefault('alternative_presentations',[]).append(record(ms,ls))
                multi[k]['apparatus_touched'] |= bool(screen(ms+ls))
            else: multi[k]=record(ms,ls)
        for m,l in sorted(pairs):
            if c.TOK[m]['gram'] or c.LEMMA[m] in mklemmas: continue
            if m in single: single[m]['episodes'].append(g['id'])
            else: single[m]=record([m],[l])
        # Long three-way aligned contiguous phrases: deterministic negative controls.
        triple = {(m,l,k) for m in seq['matthew'] for l in edges[m] if l in luke for k in edges[m] if k in set(seq['mark']) and k in edges[l]}
        for m,l,k in sorted(triple):
            if (m-1,l-1,k-1) in triple: continue
            n=1
            while (m+n,l+n,k+n) in triple: n+=1
            if n>=5: controls.append(dict(episode=g['id'],length=n,matthew_ids=list(range(m,m+n)),matthew=refs(range(m,m+n)),luke=refs(range(l,l+n)),mark=refs(range(k,k+n)),phrase=' '.join(c.TOK[i]['text'] for i in range(m,m+n))))
    candidates = sorted(multi.values(),key=lambda r:(-r['content_words'],-r['length'],r['matthew_ids']))
    checks=[]
    for r in sorted(controls,key=lambda r:(-r['length'],r['matthew_ids'])):
        if any(t['episode']==r['episode'] for t in checks): continue
        r['listed_as_candidate']=any(set(r['matthew_ids']) & set(t['matthew_ids']) for t in candidates)
        assert not r['listed_as_candidate']
        checks.append(r)
        if len(checks)==3: break
    assert len(checks)==3
    known=[r for r in candidates if '26:68' in r['matthew'] and '22:64' in r['luke']]
    stats=lambda rows:dict(before=len(rows),after_apparatus=sum(not r['apparatus_touched'] for r in rows),alignment_flagged=sum(r['alignment_flag'] for r in rows))
    out=dict(methods=['Frozen E4 exclusions: drop entire group intersecting any listed verse in any Synoptic book.','Raw per-group greekAlignment only; no SUPPLEMENT. Both partners must lack Mark links. Original token-ID adjacency prevents bridging removed Scripture.','Single-word looser count includes qualifying words inside multiword runs, deduplicated by Matthew ID.','Apparatus: accent-insensitive substring search including function words; omission/addition units intersect matching printed NA28 token positions (insertion signs within two token slots), including spanning units. No witness interpretation.','Sort: descending content words, then length, then Matthew token IDs. First ten frozen for contextual review, not independently validated discoveries.','Lemma frequency: unique non-Scripture tokens in examined episodes, all three books, stratified by speech/narrative.','OpenGNT 3.3 (CC BY-SA 4.0); apparatus NA28, Deutsche Bibelgesellschaft. Editions differ.'],exclusions=EXCLUSIONS,excluded_episodes=excluded,episodes_examined=len(episodes),multiword=stats(candidates),looser_singleword=stats(list(single.values())),episodes_with_candidates=len({g for r in candidates for g in r['episodes']}),counts_by_length=dict(Counter(r['length'] for r in candidates)),counts_by_episode={g['id']:dict(before=sum(g['id'] in r['episodes'] for r in candidates),after_apparatus=sum(g['id'] in r['episodes'] and not r['apparatus_touched'] for r in candidates)) for g,s in episodes},known_answer=dict(passed=any(key('τίς ἐστιν ὁ παίσας σε') in key(r['phrase']) for r in known),records=known),negative_controls=checks,candidates=candidates,looser_singleword_candidates=list(single.values()),changes=['Created this audit and its two output files; no existing files edited.'],limitations=['Absence from Mark does not establish innovation. Formulae, oral tradition and scribal harmonisation remain possible.','Automatic alignment may miss or misplace agreements; alignment flags are retained, not accepted as secure.','Apparatus absence is not textual security: NA28 is selective, not a full collation. Repeated-form localization and substring matches can overflag.','Whole-verse Aland boundaries can be thematic; fixed whole-group exclusions discard additional material.'])
    out['input_sha256']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(os.environ['E3_DATA'])/'opengnt.json',Path(os.environ['E3_DATA'])/'net.json',Path(c.__file__),Path(c.HERE)/'kloppenborg_test.py']}
    out['apparatus_sha256']={str(APP/b/f'{ch}.json'):hashlib.sha256((APP/b/f'{ch}.json').read_bytes()).hexdigest() for b,ch in apparatus}
    here=Path(__file__).resolve().parent
    (here/'research_minor_agreements.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    lines=['Apparatus-screened minor-agreement phrase audit',*out['methods'],'',json.dumps({k:out[k] for k in ('episodes_examined','episodes_with_candidates','multiword','looser_singleword','counts_by_length','counts_by_episode','known_answer','negative_controls')},ensure_ascii=False,indent=2),'','Matthew | Luke | Mark passage | Greek phrase | absent lemmas | speech/narrative | apparatus touched | content words | length | alignment flagged']
    for r in candidates:
        lines.append(' | '.join(str(r[k]) for k in ('matthew','luke','mark','phrase','absent_lemmas','speech_or_narrative','apparatus_touched','content_words','length','alignment_flag')))
        lines.extend('  Apparatus '+json.dumps(h,ensure_ascii=False) for h in r['apparatus'])
    lines+=['','Looser single-word count (includes words within multiword phrases)']+[json.dumps(r,ensure_ascii=False) for r in single.values()]+['','Limitations',*out['limitations'],'','Changes',*out['changes']]
    (here/'research_minor_agreements.txt').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:out[k] for k in ('episodes_examined','episodes_with_candidates','multiword','looser_singleword')},indent=2))
    print('Known answer:',out['known_answer']['passed'])
    for r in candidates[:10]: print(r['matthew'],r['luke'],r['phrase'],r['apparatus_touched'])

if __name__=='__main__': main()
