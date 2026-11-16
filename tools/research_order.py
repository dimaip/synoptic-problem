#!/usr/bin/env python3
"""Pre-specified E5 passage-order experiment.

Usage: python3 -B tools/research_order.py [DATA]
Creates research_order.txt and research_order.json beside this script, exclusively:
existing outputs prevent a rerun. Shared data and existing scripts are read-only.
Gate is evaluated before any DT direction statistic. No definition is tuned.
"""
import os
import sys
from pathlib import Path
import json
import collections
import numpy as np

sys.dont_write_bytecode = True
os.environ['E3_DATA'] = str(Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else
                          Path.home() / 'Documents/ChatGPT/gospel/public/data')
import research_common as c

HERE = Path(__file__).resolve().parent
SEED = 20261116
KS = (4, 6, 8)
READING = """- `A_DT` positive with its interval above 0 for at least two of the three k: the order is kept
  locally from Matthew's side, as when Matthew gathers from a source in Luke's order. This fits the
  Two-Source view and Matthew's use of Luke, and is a difficulty for Luke's use of Matthew.
- `A_DT` negative with its interval below 0 for at least two k: the order is kept locally from
  Luke's side, as when Luke gathers from Matthew. This fits Luke's use of Matthew.
- Otherwise: inconclusive."""

# Running verse indices include all verses in the pack, even any without tokens.
POSITIONS = {}
for book in c.pack['books']:
    for position, verse in enumerate(sorted(book['verses'], key=lambda v: (v['chapter'], v['verse'])), 1):
        POSITIONS[(book['id'], verse['chapter'], verse['verse'])] = position


def blocks(a, b, eligible, minimum, gap=2, exclude_q=False):
    """Map by linked-token plurality; merge maximal forward runs after mapping."""
    mapped = []
    for verse in sorted(eligible, key=lambda v: POSITIONS[v]):
        votes = collections.Counter()
        for token in c.VERSE[verse]:
            partner = c.PARTNER[token].get(b)
            if b in c.LINK[token] and partner is not None:
                t = c.TOK[partner]
                votes[(b, t['ch'], t['v'])] += 1
        if sum(votes.values()) < minimum:
            continue
        target = min(votes, key=lambda v: (-votes[v], POSITIONS[v]))
        if exclude_q and c.CL.get(target) in ('Q', 'Q+Mark overlap'):
            continue
        mapped.append((verse, target))
    groups = []
    for source, target in mapped:
        if groups and 0 < POSITIONS[source] - POSITIONS[groups[-1][-1][0]] <= gap and \
                0 <= POSITIONS[target] - POSITIONS[groups[-1][-1][1]] <= gap:
            groups[-1].append((source, target))
        else:
            groups.append([(source, target)])
    return [dict(a=a, b=b, a_position=POSITIONS[g[0][0]], b_position=POSITIONS[g[0][1]],
                 verses=[dict(a=list(x), b=list(y)) for x, y in g],
                 jesus_share=float(np.mean([c.K['jesus_share'](x) for x, _ in g]))) for g in groups]


def positions(units):
    return np.array([[u['a_position'], u['b_position']] for u in units], dtype=int).reshape(-1, 2)


def pair_stats(x):
    """Tau-a and concordant share: ties contribute zero, denominator all pairs."""
    i, j = np.triu_indices(len(x), 1)
    signs = np.sign(x[i, 0] - x[j, 0]) * np.sign(x[i, 1] - x[j, 1])
    return (float(np.mean(signs)), float(np.mean(signs > 0))) if len(signs) else (float('nan'), float('nan'))


def descriptive(units, seed):
    x = positions(units)
    rng = np.random.default_rng(seed)
    tau, share = pair_stats(x)
    null = [pair_stats(np.column_stack((x[:, 0], rng.permutation(x[:, 1]))))[0] for _ in range(5000)]
    boots = np.array([pair_stats(x[rng.integers(len(x), size=len(x))]) for _ in range(2000)])
    return dict(blocks=len(x), tau=tau, concordant_share=share,
                permutation_p=(1 + sum(abs(t) >= abs(tau) for t in null)) / 5001,
                tau_ci=np.percentile(boots[:, 0], [2.5, 97.5]).tolist(),
                concordant_share_ci=np.percentile(boots[:, 1], [2.5, 97.5]).tolist())


def asymmetry(x, k):
    """Equal groups via array_split; stable sort resolves position ties reproducibly."""
    shares = []
    for axis in (0, 1):
        good = total = 0
        for group in np.array_split(np.argsort(x[:, axis], kind='stable'), k):
            i, j = np.triu_indices(len(group), 1)
            pairs = x[group]
            good += int(np.sum((pairs[i, 0] - pairs[j, 0]) * (pairs[i, 1] - pairs[j, 1]) > 0))
            total += len(i)
        shares.append(good / total if total else float('nan'))
    return shares[0], shares[1], shares[1] - shares[0]


def direction(units, seed):
    x = positions(units)
    rng = np.random.default_rng(seed)
    # Re-cut both orders for every bootstrap sample, including repeated blocks.
    samples = [x[rng.integers(len(x), size=len(x))] for _ in range(2000)]
    out = {}
    for k in KS:
        ca, cb, value = asymmetry(x, k)
        boot = [asymmetry(sample, k)[2] for sample in samples]
        out[str(k)] = dict(C_A=ca, C_B=cb, A=value, ci=np.percentile(boot, [2.5, 97.5]).tolist())
    return out


def main(log, output):
    def emit(label, value):
        line = label + ': ' + json.dumps(value, ensure_ascii=False, allow_nan=False)
        print(line, flush=True)
        log.write(line + '\n'); log.flush()

    result = dict(settings=dict(seed=SEED, bootstrap=2000, permutations=5000, simulations=500,
                  k=list(KS), permutation='two-sided absolute tau, plus-one correction',
                  interval='percentile 2.5 and 97.5', ties='zero numerator; all pairs denominator',
                  grouping='array_split; stable positional sort', sayings='unweighted mean of A-verse Jesus shares >= 0.8'),
                  implementation_corrections=[], part2=None, sensitivities=None)
    emit('Settings', result['settings'])
    mark = [v for v in c.VERSE if v[0] == 'mark']
    dt = [v for v in c.VERSE if v[0] == 'luke' and c.CL.get(v) == 'Q']
    sets = {'DT': blocks('luke', 'matthew', dt, 2),
            'MK-MT': blocks('mark', 'matthew', mark, 3),
            'MK-LK': blocks('mark', 'luke', mark, 3, exclude_q=True)}
    result['block_sets'] = sets
    for name, units in sets.items():
        emit('Counts ' + name, dict(blocks=len(units), verses=sum(len(u['verses']) for u in units)))
    for n, unit in enumerate(sets['DT'], 1):
        emit(f'DT block {n} Luke -> Matthew', unit['verses'])

    # Evaluate the known-answer gate first; do not compute DT direction yet.
    gate = direction(sets['MK-MT'], SEED + 1)
    passed = sum(v['A'] > 0 and v['ci'][0] > 0 for v in gate.values()) >= 2
    result['gate'] = dict(values=gate, passed=passed)
    emit('MK-MT gate', result['gate'])
    result['mark_luke_check'] = direction(sets['MK-LK'], SEED + 2)
    emit('MK-LK informational', result['mark_luke_check'])
    rng = np.random.default_rng(SEED + 3)
    n = len(sets['DT'])
    synthetic = {str(k): [] for k in KS}
    for _ in range(500):
        discourse = rng.integers(5, size=n)
        order = np.argsort(discourse, kind='stable')
        editor = np.empty(n, dtype=int); editor[order] = np.arange(n)
        x = np.column_stack((np.arange(n), editor))
        for k in KS:
            synthetic[str(k)].append(asymmetry(x, k)[2])
    result['synthetic_check'] = {k: dict(share_positive=float(np.mean(np.array(v) > 0)), values=v) for k, v in synthetic.items()}
    emit('Synthetic share A > 0', {k: v['share_positive'] for k, v in result['synthetic_check'].items()})
    result['part1'] = {}
    for j, (name, units) in enumerate(sets.items()):
        result['part1'][name] = {}
        for offset, (label, subset) in enumerate((('all', units), ('sayings', [u for u in units if u['jesus_share'] >= .8]))):
            r = descriptive(subset, SEED + 10 + j * 2 + offset)
            result['part1'][name][label] = r
            emit('Part 1 ' + name + ' ' + label, r)
    emit('Pre-stated reading', READING)
    if not passed:
        result['status'] = 'direction test void'
        emit('Status', result['status'])
    else:
        result['part2'] = direction(sets['DT'], SEED + 20)
        emit('Part 2 DT', result['part2'])
        positive = sum(v['A'] > 0 and v['ci'][0] > 0 for v in result['part2'].values()) >= 2
        negative = sum(v['A'] < 0 and v['ci'][1] < 0 for v in result['part2'].values()) >= 2
        result['status'] = 'positive' if positive else 'negative' if negative else 'inconclusive'
        result['sensitivities'] = {}
        auto = [v for v in c.VERSE if v[0] == 'luke' and 'matthew' in c.PAR[v] and 'mark' not in c.PAR[v]]
        for j, (label, units) in enumerate((('a_m3', blocks('luke', 'matthew', dt, 3)),
                                          ('b_gap1', blocks('luke', 'matthew', dt, 2, gap=1)),
                                          ('c_no_Q_list', blocks('luke', 'matthew', auto, 2)))):
            r = dict(blocks=units, values=direction(units, SEED + 30 + j))
            result['sensitivities'][label] = r
            emit('Sensitivity ' + label, dict(blocks=len(units), values=r['values']))
    result['limitations'] = ['Automatic identical-form token alignment, including inherited woes supplement; PARTNER retains one partner per target Gospel.',
                             'Bootstrap repeated blocks and genuine positional ties count as tied pairs; percentile intervals are not tie-corrected.',
                             'Block construction preserves within-block order by definition; only between-block pairs are tested.']
    emit('Limitations', result['limitations'])
    emit('Implementation corrections', result['implementation_corrections'])
    json.dump(result, output, ensure_ascii=False, indent=2, allow_nan=False)
    output.write('\n')


if __name__ == '__main__':
    # Both paths must be absent before reserving outputs; never overwrite earlier runs.
    paths = [HERE / 'research_order.txt', HERE / 'research_order.json']
    if any(p.exists() for p in paths):
        raise SystemExit('Existing E5 output: refusing to rerun.')
    with paths[0].open('x') as log, paths[1].open('x') as output:
        main(log, output)
