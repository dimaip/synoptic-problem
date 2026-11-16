#!/usr/bin/env python3
"""Bounded review diagnostics. Run: python3 -B tools/research_review_checks.py [DATA].
Writes only the three companion review artifacts; no review-directory dependency.
Greek: OpenGNT (CC BY-SA 4.0); parallels: Aland via Synoptic Canvas.
Manual judgements below concern correspondence, not literary dependence.
"""
import sys
sys.dont_write_bytecode = True
import os, json, random, collections, hashlib
from pathlib import Path
import numpy as np
DATA = Path(sys.argv[1]).expanduser() if len(sys.argv)>1 else Path.home()/'Documents/ChatGPT/gospel/public/data'
os.environ['E3_DATA'] = str(DATA)
import research_common as c
import research_order as o
HERE = Path(__file__).resolve().parent
# Frozen close reading: ref | class | specific Mark counterpart (if any) | reason.
JUDGEMENTS = '''4:18|ADDITION||Isaiah commission quotation has no counterpart in Mark's Nazareth account.
4:19|ADDITION||The acceptable-year quotation is absent from Mark's Nazareth account.
4:23|UNCLEAR|6:2-5|The hometown demand for miracles could recast Mark's miracles and unbelief, but the physician proverb is additional.
4:25|ADDITION||The Elijah famine example is absent from Mark's Nazareth account.
4:26|ADDITION||The widow of Zarephath example has no corresponding Markan clause.
4:27|ADDITION||The Elisha and Naaman example has no corresponding Markan clause.
5:39|ADDITION||Preference for old wine adds a conclusion absent from Mark's wineskin saying.
7:41|ADDITION||The two debtors and their amounts are absent from Mark's anointing account.
7:42|ADDITION||Forgiving two debts and asking about love are absent from Mark's anointing account.
7:45|ADDITION||The contrast between Simon's missing kiss and the woman's kisses is absent from Mark.
7:46|UNCLEAR|14:3,8|The anointing corresponds broadly, but feet versus head and Simon's omission prevent a secure clause-level identification.
7:47|ADDITION||Forgiveness in relation to love is absent from Mark's defence of the woman.
8:11|RENDERS|4:14|Identifying seed with God's word restates Mark's sower sowing the word.
8:16|RENDERS|4:21|Lighting and placing the lamp restates Mark's lamp under bed or on stand, with an added purpose clause.
11:21|UNCLEAR|3:27|The armed guardian elaborates the strong man's house, but Mark has no corresponding peaceful-guarding clause.
11:22|RENDERS|3:27|Overcoming the strong man and distributing spoils restates binding him and plundering his house.
13:25|ADDITION||The shut door and rejected petition have no counterpart in Mark's first-last saying.
17:25|ADDITION||Suffering and rejection are absent from the Markan eschatological passages printed here; Mark 8:31 is outside this bounded comparison.
17:28|ADDITION||Lot's contemporaries and their occupations are absent from the printed Markan parallels.
17:29|ADDITION||Lot leaving Sodom and the fiery destruction are absent from the printed Markan parallels.
17:32|ADDITION||The warning about Lot's wife is absent from the printed Markan parallels.
19:14|ADDITION||The citizens' embassy rejecting kingship is absent from Mark's departing-householder comparison.
19:27|ADDITION||Executing the king's enemies is absent from Mark's departing-householder comparison.
20:11|RENDERS|12:4|Sending and dishonouring another servant corresponds to Mark's second servant, with changed injuries and outcome.
20:12|UNCLEAR|12:5|The third servant corresponds in sequence, but wounding and expulsion replace killing and may conflate other servant clauses.
20:13|RENDERS|12:6|The owner's decision to send his beloved son and expectation of respect restate Mark's clause.
20:18|ADDITION||The falling and crushing stone saying adds to Mark's quoted rejected-stone text.
20:36|UNCLEAR|12:25-27|Angelic resurrection existence corresponds, but inability to die and divine sonship extend the claim substantially.
21:12|RENDERS|13:9|Arrest and delivery before synagogues, kings and governors restate Mark's persecution prediction.
21:13|RENDERS|13:9|The outcome as testimony restates Mark's testimony clause.
21:14|RENDERS|13:11|Not preparing a defence restates Mark's instruction not to premeditate speech.
21:15|UNCLEAR|13:11|Jesus' gift of irresistible wisdom may recast the Spirit's supplied speech, but speaker and emphasis change.
21:18|UNCLEAR|13:13|No hair lost may express Mark's promised salvation, but the bodily assurance is not an explicit Markan clause.
21:19|RENDERS|13:13|Gaining life through endurance restates salvation for the one enduring to the end.
21:22|UNCLEAR|13:19-20|Days of vengeance and scriptural fulfilment may explicate the tribulation, but neither clause appears explicitly in Mark.
21:24|UNCLEAR|13:19-20|Death, captivity and Jerusalem's trampling may specify Mark's tribulation, but no individual clause corresponds securely.
21:25|RENDERS|13:24-25|Signs in sun, moon and stars restate Mark's celestial portents, with additional earthly distress.
21:28|ADDITION||The instruction to raise heads because redemption approaches is absent from the printed Markan coming-of-the-Son passage.
22:21|RENDERS|14:18,20|The betrayer's hand at the table restates the betrayer eating and dipping with Jesus.
22:27|UNCLEAR|10:43-45|Jesus serving corresponds to the Son of Man serving, but the table-rank question adds a different illustration.
22:31|UNCLEAR|14:27|Satan's sifting may recast the predicted disciples' collapse, but Satan and the image are absent from Mark.
22:32|ADDITION||Jesus' intercession and Peter strengthening brothers have no counterpart in the printed Markan denial prediction.
22:68|ADDITION||The refusal to answer Jesus' hypothetical question is absent from Mark's hearing account.
23:29|ADDITION||The coming blessing of barren women is absent from Mark's journey to crucifixion.
23:31|ADDITION||The green and dry wood comparison is absent from Mark's journey to crucifixion.'''


def measure(keys):
    h,n = c.K['rate'](keys,'matthew')
    return dict(verses=len(keys), hits=h, words=n, rate=100*h/n)


def chapter_interval(q,t):
    units=[]
    for keys in (q,t):
        chapters=collections.defaultdict(list)
        for k in keys: chapters[k[1]].append(k)
        units.append([c.K['rate'](v,'matthew') for v in chapters.values()])
    rng=random.Random(1); ds=[]
    for _ in range(4000):
        rates=[]
        for per in units:
            sample=[rng.choice(per) for _ in per]
            rates.append(100*sum(h for h,n in sample)/sum(n for h,n in sample))
        ds.append(rates[0]-rates[1])
    ds.sort()
    return [ds[100],ds[3900]]


def strings(keys):
    pairs=[c.K['rate'](r,'matthew') for r in c.runs(keys)]
    pairs=[(h,n) for h,n in pairs if n>=40]
    return dict(total=len(pairs), at70=sum(h/n>=.7 for h,n in pairs), at50=sum(h/n>=.5 for h,n in pairs))


def construct(mapped, gap=None):
    """Own units: singleton verses or published forward-gap rule, first positions."""
    groups=[]
    for a,b in mapped:
        if gap is not None and groups and 0<o.POSITIONS[a]-o.POSITIONS[groups[-1][-1][0]]<=gap and 0<=o.POSITIONS[b]-o.POSITIONS[groups[-1][-1][1]]<=gap:
            groups[-1].append((a,b))
        else: groups.append([(a,b)])
    return groups


def describe(units):
    x=np.array([(o.POSITIONS[g[0][0]],o.POSITIONS[g[0][1]]) for g in units])
    return dict(units=len(units),tau=o.pair_stats(x)[0])


def saying_units(units, weighted=False):
    if weighted:
        return [g for g in units if sum(c.TOK[i]['jesus'] for a,b in g for i in c.VERSE[a])/sum(len(c.VERSE[a]) for a,b in g)>=.8]
    return [g for g in units if np.mean([c.K['jesus_share'](a) for a,b in g])>=.8]


def main():
    out={}; lines=[]
    def emit(label,value):
        out[label]=value; lines.append(label+': '+json.dumps(value,ensure_ascii=False))
    emit('Methods',dict(run_gap_interval='6000 draws, random.Random(7), exact diff_boot', chapter_gap_interval='4000 draws, random.Random(1), sorted indices 100 and 3900; independent chapter samples for Q and triple', order='PARTNER last-link mapping; minimum total votes across targets; plurality, earliest target tie-break; tau-a; gap2 source step 1-2 and target step 0-2; first pair positions', limitations=['Mark-link filter selects on agreement with Mark and overstates triple rate', 'Manual correspondence judgements, UNCLEAR retained as a sensitivity', 'Intervals measure composition under assumed clusters', 'Strata are crude stratifications, not a fitted model']))
    emit('Provenance',dict(data=str(DATA),sha256={name:hashlib.sha256((DATA/name).read_bytes()).hexdigest() for name in ('opengnt.json','net.json')},greek='OpenGNT CC BY-SA 4.0',judgement='Manual bounded correspondence judgements, not source assignments'))
    say=[k for k in c.VERSE if k[0]=='luke' and c.K['jesus_share'](k)>=.8]
    q=[k for k in say if c.CL[k]=='Q']; t=[k for k in say if c.CL[k]=='triple']
    emit('A1 Q fixed',measure(q))
    for minimum in range(4): emit(f'A1 triple fixed class and speech; minimum Mark-linked tokens={minimum}',measure([k for k in t if c.nlinked(k,'mark')>=minimum]))
    lines.append('A1 This filter selects on agreement with Mark and so overstates the triple rate.')
    rows=[]
    for line in JUDGEMENTS.splitlines():
        ref,cls,mref,reason=line.split('|'); k=('luke',*map(int,ref.split(':')))
        parallels=[]
        for g in c.groups:
            if any(p['book']=='luke' and ref in p['verses'] for p in g['passages']):
                for p in g['passages']:
                    if p['book']=='mark':
                        parallels.append(dict(group=g['id'],primary=p.get('primary',False),reference=p['reference'],greek=[dict(ref=r,text=' '.join(c.TOK[i]['text'] for i in c.VERSE[('mark',*map(int,r.split(':')))])) for r in p['verses']]))
        parallels.sort(key=lambda p:not p['primary'])
        rows.append(dict(luke_ref=ref,classification=cls,mark_ref=mref or None,reason=reason,luke_greek=' '.join(c.TOK[i]['text'] for i in c.VERSE[k]),mark_passages=parallels,source_url='https://synoptic-canvas.vercel.app/?verse=luke-'+ref.replace(':','-')))
    assert {('luke',*map(int,r['luke_ref'].split(':'))) for r in rows}=={k for k in t if c.nlinked(k,'mark')==0}
    (HERE/'research_e1_verses.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    emit('A2 judgement counts',dict(collections.Counter(r['classification'] for r in rows)))
    for r in rows: lines.append('A2 '+json.dumps(r,ensure_ascii=False))
    emit('A3 Q fixed strings',strings(q))
    for label,excluded in [('published',()),('exclude ADDITION',('ADDITION',)),('exclude ADDITION and UNCLEAR',('ADDITION','UNCLEAR'))]:
        drop={('luke',*map(int,r['luke_ref'].split(':'))) for r in rows if r['classification'] in excluded}
        ks=[k for k in t if k not in drop]
        emit('A3 '+label,dict(**measure(ks),gap=measure(q)['rate']-measure(ks)['rate'],run_ci=c.K['diff_boot'](q,ks)[:2],chapter_cluster_sensitivity_ci=chapter_interval(q,ks),strings=strings(ks)))
    lines += ['A3 Intervals: 95% composition resampling; runs 6000 draws seed 7, exactly diff_boot; chapters 4000 draws seed 1, same percentile indices; independently resample Q and triple. Chapters are a cluster sensitivity. Text, alignment, classes and Q list held fixed.', 'A4 Independent retention from 1000 source words: Matthew 500/1000=50%; Luke 822/1000=82.2%; expected overlap 1000*0.500*0.822=411 words.', 'A4 With each resulting text 1000 words, agreement=411/1000=41.1%, while Matthew retention 50% is below his 55.4% Mark figure.']
    mark=[k for k in c.VERSE if k[0]=='mark']; maps={}
    # Mapping is reused exactly; gap=0 exposes uncompressed singleton source verses.
    for name,b,exclude in [('MT','matthew',False),('LK','luke',True),('LK-inclusive','luke',False)]:
        maps[name]=[(tuple(u['verses'][0]['a']),tuple(u['verses'][0]['b'])) for u in o.blocks('mark',b,mark,3,gap=0,exclude_q=exclude)]
    for policy,lk in [('published Q exclusion','LK'),('include all Luke classes','LK-inclusive')]:
        eligible={name:{a for a,b in maps[name] if c.K['jesus_share'](a)>=.8} for name in ('MT',lk)}
        common=eligible['MT']&eligible[lk]
        for name in ('MT',lk):
            for scope,keep,gap in [('B1 common verse sample',common,None),('B2 own eligible verse sample',eligible[name],None),('B2 common verse sample published gap2',common,2)]:
                units=construct([(a,b) for a,b in maps[name] if a in keep],gap)
                emit(f'{scope}; {policy}; {name}; token-weighted >=80% Jesus; minimum3 links',describe(units))
    for name in ('MT','LK','LK-inclusive'):
        units=construct(maps[name],2)
        for scope,subset in [('all',units),('published unweighted sayings',saying_units(units)),('token-weighted sayings',saying_units(units,True))]:
            emit(f'B3 fixed published mapping and gap2; {name}; {scope}',describe(subset))
    dt=[k for k in c.VERSE if k[0]=='luke' and c.CL.get(k)=='Q']
    dtmap=[(tuple(u['verses'][0]['a']),tuple(u['verses'][0]['b'])) for u in o.blocks('luke','matthew',dt,2,gap=0)]
    for j,(name,mapped) in enumerate([('DT',dtmap),('MT',maps['MT']),('LK',maps['LK'])]):
        units=saying_units(construct(mapped,2)); x=np.array([(o.POSITIONS[g[0][0]],o.POSITIONS[g[0][1]]) for g in units]); n=len(x)
        rng=np.random.default_rng(20261116+11+j*2)
        for _ in range(5000): rng.permutation(x[:,1])
        raw=[]; corrected=[]; a,b=np.triu_indices(n,1)
        for _ in range(2000):
            ix=rng.integers(n,size=n); z=x[ix]
            signs=np.sign(z[a,0]-z[b,0])*np.sign(z[a,1]-z[b,1])
            raw.append(float(signs.mean())); corrected.append(float(signs.sum()/np.sum(ix[a]!=ix[b])))
        emit(f'B4 {name} fixed published sayings blocks and same draws; denominator change only',dict(**describe(units),published_ci=np.percentile(raw,[2.5,97.5]).tolist(),exclude_duplicate_identity_pairs_ci=np.percentile(corrected,[2.5,97.5]).tolist(),seed=20261116+11+j*2,draws=2000))
    ids=[i for k in mark if {'matthew','luke'}<=c.PAR[k] for i in c.VERSE[k]]
    assert len(ids)==9744
    emit('C fixed 9744 Mark tokens; observed and unstratified',dict(words=len(ids),observed=100*sum({'matthew','luke'}<=c.LINK[i] for i in ids)/len(ids),unstratified=100*sum('matthew' in c.LINK[i] for i in ids)*sum('luke' in c.LINK[i] for i in ids)/len(ids)**2))
    for name,key in [('lemma',lambda i:c.LEMMA[i]),('verse',lambda i:(c.TOK[i]['ch'],c.TOK[i]['v'])),('lemma within speech kind',lambda i:(c.LEMMA[i],'Jesus' if c.TOK[i]['jesus'] else 'other speech' if c.TOK[i]['speech'] else 'narrator'))]:
        strata=collections.defaultdict(list)
        for i in ids:strata[key(i)].append(i)
        expected=sum(sum('matthew' in c.LINK[i] for i in s)*sum('luke' in c.LINK[i] for i in s)/len(s) for s in strata.values())/len(ids)*100
        emit('C fixed tokens; independence within '+name,dict(strata=len(strata),expected_percent=expected))
    lines.append('C These are crude stratifications, not a fitted model. Expected joint share = sum_s(m_s*l_s/n_s)/9744.')
    report='\n'.join(lines)+'\n'
    (HERE/'research_review_checks.txt').write_text(report)
    (HERE/'research_review_checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(report,end='')

if __name__=='__main__': main()
