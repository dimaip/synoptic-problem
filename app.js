// Renders the whole page from the JSON files in content/.
// Content lives only in those files; this script handles layout and interaction.
// A missing or invalid file never breaks the page: its section says "not yet written".

const GROUP_IDS = ['P', 'I', 'C', 'D', 'Q', 'M', 'S'];
const FILES = ['meta', 'synopsis', 'chapters', 'phenomena', 'models',
  ...GROUP_IDS.map(g => `arguments/${g}`),
  'positions', 'history', 'corrections', 'research', 'assessment', 'bibliography'];

async function load(name) {
  try {
    const r = await fetch(`content/${name}.json`, { cache: 'no-cache' });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return await r.json();
  } catch (e) {
    console.warn(`content/${name}.json not loaded: ${e.message}`);
    return null;
  }
}
const RAW = Object.fromEntries((await Promise.all(FILES.map(load))).map((d, i) => [FILES[i], d]));

/* ---------- helpers ---------- */

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
const arr = x => Array.isArray(x) ? x : [];
const obj = x => (x && typeof x === 'object' && !Array.isArray(x)) ? x : null;
const num = x => { const n = Number(x); return Number.isFinite(n) ? n : null; };
const fmt = n => num(n) == null ? '' : Number(n).toLocaleString('en-GB');
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)');
// Diagrams are drawn for the width they will be shown at: a narrower drawing keeps labels legible on phones.
const NARROW = matchMedia('(max-width: 520px)').matches;

const esc = s => String(s ?? '')
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const GREEK = '\\u0370-\\u03FF\\u1F00-\\u1FFF';
const reGreek = new RegExp(`[${GREEK}](?:[${GREEK}\\u0300-\\u036F\\s·.,;:…’᾿-]*[${GREEK}])?`, 'g');

const meta = obj(RAW.meta) || {};
const synopsis = obj(RAW.synopsis);
const phenomena = obj(RAW.phenomena);
const models = obj(RAW.models);
const positions = obj(RAW.positions);
const historyData = obj(RAW.history);
const corrections = obj(RAW.corrections);
const assessment = obj(RAW.assessment);
const research = obj(RAW.research);
const EXPERIMENTS = arr(research?.items).filter(x => x && x.id);
const EXP = Object.fromEntries(EXPERIMENTS.map(x => [x.id, x]));
const BIB = arr(RAW.bibliography).filter(b => b && b.key);

const GROUP_FALLBACK = {
  P: 'Which Gospel came first?', I: 'Did Matthew and Luke write independently?',
  C: 'Signs of contact between Matthew and Luke', D: 'Which direction? Could Matthew have used Luke?',
  Q: 'What kind of thing would Q be?', M: 'How ancient authors worked', S: 'Counting'
};
const GROUPS = GROUP_IDS.map(id => {
  const g = obj(RAW[`arguments/${id}`]);
  if (!g) return { id, title: GROUP_FALLBACK[id], items: [], missing: true };
  return { ...g, id, title: g.title || GROUP_FALLBACK[id], items: arr(g.items).filter(a => a && a.id) };
});
const ALL_ARGS = GROUPS.flatMap(g => g.items);
const ARG = Object.fromEntries(ALL_ARGS.map(a => [a.id, a]));

const EXHIBITS = arr(synopsis?.exhibits).filter(e => e && e.id);
const EX = Object.fromEntries(EXHIBITS.map(e => [e.id, e]));
const exhibitsFor = id => EXHIBITS.filter(e => arr(e.usedBy).includes(id));

const argLink = id => {
  const a = ARG[id];
  if (!a && EXP[id]) return `<a href="#exp-${esc(id)}" class="arg-link exp-link" title="${esc(EXP[id].title || id)}">${esc(id)}</a>`;
  if (!a) return `<span class="arg-link missing" title="Not yet written">${esc(id)}</span>`;
  return `<a href="#arg-${esc(id)}" class="arg-link"${a ? ` title="${esc(a.title)}"` : ''}>${esc(id)}</a>`;
};

// Escape; tag Greek runs; *italic*; [[C3]] → link to an argument, [[E1]] → link to an experiment.
function rich(s) {
  if (s == null || s === '') return '';
  return esc(s)
    .replace(reGreek, m => `<span lang="grc">${m}</span>`)
    .replace(/\*([^*\n]+?)\*/g, '<em>$1</em>')
    .replace(/\[\[([A-Za-z]+\d+[a-z]?)\]\]/g, (_, id) => argLink(id));
}

/* basis markers */
const BASIS_DEFAULT = {
  read: 'Checked directly in the publication',
  abstract: 'Known from an abstract, summary or preview only',
  reported: 'Reported by another author; not checked directly',
  unchecked: 'From background knowledge; not confirmed in a source'
};
const BASIS = { ...BASIS_DEFAULT, ...(obj(meta.basisLegend) || {}) };
const BASIS_ORDER = ['read', 'abstract', 'reported', 'unchecked', ...Object.keys(BASIS).filter(k => !BASIS_DEFAULT[k])];
// Not focusable: there are hundreds of these; the legend (masthead and footer) explains them.
const basisTag = b => b ? `<span class="basis b-${esc(b)}" title="${esc(BASIS[b] || b)}">${esc(b)}</span>` : '';

/* bibliography linking: one alternation of all keys, longest first, matched on the raw text */
const slug = k => 'bib-' + String(k).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
  .replace(/&/g, ' and ').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const reEsc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const BIBKEYS = new Set(BIB.map(b => String(b.key)));
const bibRe = BIB.length
  ? new RegExp(`(?<![\\p{L}\\p{N}])(${[...BIBKEYS].sort((a, b) => b.length - a.length).map(reEsc).join('|')})(?![\\p{L}\\p{N}])`, 'gu')
  : null;

function refLinks(s) {
  if (s == null || s === '') return '';
  s = String(s);
  if (!bibRe) return rich(s);
  let out = '', last = 0;
  for (const m of s.matchAll(bibRe)) {
    out += rich(s.slice(last, m.index)) + `<a href="#${slug(m[1])}" class="bib-link">${esc(m[1])}</a>`;
    last = m.index + m[1].length;
  }
  return out + rich(s.slice(last));
}
const refSpan = (ref, basis) => (ref || basis)
  ? ` <span class="ref">${ref ? '— ' + refLinks(ref) : ''} ${basisTag(basis)}</span>` : '';

// A bibliography entry for a person named with a year, if there is one.
function keyFor(name, year) {
  if (!name) return null;
  const plain = String(name).replace(/\s*\(.*?\)\s*/g, ' ').trim();
  const last = plain.split(/\s+/).pop();
  return [plain, `${plain} ${year}`, `${last} ${year}`].find(c => BIBKEYS.has(c));
}
const nameLink = (name, year) => {
  const k = keyFor(name, year);
  return k ? `<a href="#${slug(k)}">${rich(name)}</a>` : rich(name);
};

const sectionHead = (n, title, intro) => `
  <header class="sec-head wrap-wide">
    <p class="sec-num">${n}</p>
    <h2>${esc(title)}</h2>
    ${intro ? `<p class="sec-intro">${rich(intro)}</p>` : ''}
  </header>`;
const NOT_YET = '<p class="empty">Not yet written.</p>';
const intro = id => obj(meta.intros)?.[id];

/* ---------- markers ---------- */

// Shape + colour: Mark = red square, Matthew = blue circle, Luke = ochre triangle,
// hypothetical = dashed ring, oral = small dotted ring, other text = grey diamond,
// Q side = green circle, no-Q side = rust diamond, open = neutral ring.
function shapeEl(kind, cx, cy, r) {
  const f = n => +n.toFixed(2);
  switch (kind) {
    case 'mark': { const s = r * 1.62; return `<rect x="${f(cx - s / 2)}" y="${f(cy - s / 2)}" width="${f(s)}" height="${f(s)}" fill="var(--mk)"/>`; }
    case 'matthew': return `<circle cx="${f(cx)}" cy="${f(cy)}" r="${f(r * 0.92)}" fill="var(--mt)"/>`;
    case 'luke': return `<path d="M${f(cx)} ${f(cy - r)} L${f(cx + r * 1.02)} ${f(cy + r * 0.8)} L${f(cx - r * 1.02)} ${f(cy + r * 0.8)} Z" fill="var(--lk)"/>`;
    case 'hyp': return `<circle cx="${f(cx)}" cy="${f(cy)}" r="${f(r * 0.8)}" fill="var(--bg)" stroke="var(--ink)" stroke-width="${f(Math.max(1.3, r * 0.22))}" stroke-dasharray="${f(r * 0.42)} ${f(r * 0.3)}"/>`;
    case 'oral': return `<circle cx="${f(cx)}" cy="${f(cy)}" r="${f(r * 0.6)}" fill="none" stroke="var(--muted)" stroke-width="${f(Math.max(1.4, r * 0.22))}" stroke-dasharray="0.1 ${f(r * 0.42)}" stroke-linecap="round"/>`;
    case 'other': { const s = r * 1.25; return `<rect x="${f(cx - s / 2)}" y="${f(cy - s / 2)}" width="${f(s)}" height="${f(s)}" transform="rotate(45 ${f(cx)} ${f(cy)})" fill="var(--neutral)"/>`; }
    case 'q': return `<circle cx="${f(cx)}" cy="${f(cy)}" r="${f(r * 0.86)}" fill="var(--q)"/>`;
    case 'noq': { const s = r * 1.3; return `<rect x="${f(cx - s / 2)}" y="${f(cy - s / 2)}" width="${f(s)}" height="${f(s)}" transform="rotate(45 ${f(cx)} ${f(cy)})" fill="var(--noq)"/>`; }
    default: return `<circle cx="${f(cx)}" cy="${f(cy)}" r="${f(r * 0.7)}" fill="none" stroke="var(--neutral)" stroke-width="${f(Math.max(1.6, r * 0.28))}"/>`;
  }
}
const marker = (kind, size = 14) =>
  `<svg class="mk" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" aria-hidden="true">${shapeEl(kind, size / 2, size / 2, size / 2 * 0.95)}</svg>`;
const kindTag = (kind, label, cls = '') =>
  `<span class="rtag k-${esc(kind)} ${cls}">${marker(kind, 12)}<span>${rich(label)}</span></span>`;

const GOSPEL = {
  Matt: { name: 'Matthew', cls: 'mt', kind: 'matthew', letter: 'M' },
  Mark: { name: 'Mark', cls: 'mk', kind: 'mark', letter: 'K' },
  Luke: { name: 'Luke', cls: 'lk', kind: 'luke', letter: 'L' }
};
const G_ORDER = ['Matt', 'Mark', 'Luke'];
const gosp = id => GOSPEL[id] || GOSPEL[{ Matthew: 'Matt', Mt: 'Matt', Mk: 'Mark', Lk: 'Luke' }[id]];
const gId = id => G_ORDER.find(k => GOSPEL[k] === gosp(id));

const HYP = ['2DH', 'FH', 'MPH', '2GH'];
const SIDE_KIND = { q: 'q', noq: 'noq', open: 'open' };

/* ---------- state ---------- */

const state = {
  model: new URLSearchParams(location.search).get('model') || '',
  filter: 'all',
  sort: 'order',
  open: new Set(),
  indexOpen: matchMedia('(min-width: 700px)').matches,
  bibFilter: 'all'
};
if (!HYP.includes(state.model)) state.model = '';

/* ---------- masthead ---------- */

if (meta.title) {
  $('#title').textContent = meta.title;
  document.title = meta.kicker ? `${meta.title} — ${meta.kicker}` : meta.title;
}
if (meta.kicker) $('#kicker').textContent = meta.kicker;
$('#subtitle').innerHTML = rich(meta.subtitle);
$('#lede').innerHTML = rich(meta.lede);
const legendHTML = () => `
  <span class="legend-title">How each item was checked</span>
  ${BASIS_ORDER.map(k => `<span class="legend-item">${basisTag(k)} ${esc(BASIS[k])}</span>`).join('')}`;
$('#basis-legend').innerHTML = legendHTML();

// One shared set of SVG arrowheads for the diagrams.
document.body.insertAdjacentHTML('afterbegin', `<svg class="defs" width="0" height="0" aria-hidden="true" focusable="false">
  <defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0 0 L10 5 L0 10 z" fill="var(--edge)"/></marker></defs></svg>`);

/* ---------- synopsis component ---------- */

const KIND_LABEL = {
  double: 'double tradition', triple: 'triple tradition', overlap: 'Mark–Q overlap',
  'minor-agreement': 'minor agreement', fatigue: 'editorial fatigue', primitivity: 'primitivity',
  addition: 'addition to Mark', 'dual-expression': 'dual expression', 'harder-reading': 'harder reading'
};
const kindLabel = k => KIND_LABEL[k] || String(k || '').replace(/-/g, ' ');

function agreeClass(g, three) {
  const s = [...String(g || '')].filter(c => 'MKL'.includes(c)).sort((a, b) => 'MKL'.indexOf(a) - 'MKL'.indexOf(b)).join('');
  if (s.length >= 3) return 't-all';
  if (s === 'MK') return 't-mk';
  if (s === 'KL') return 't-kl';
  if (s === 'ML') return three ? 't-ml' : 't-dt';
  return '';
}

function tokenClass(t, three, used) {
  let cls = agreeClass(t.g, three);
  if (cls) { used.add(cls); return cls; }
  const lx = agreeClass(t.gl, three);
  used.add('t-un');
  if (lx) { used.add('lx'); return `t-un lx lx-${lx.slice(2)}`; }
  return 't-un';
}

// Consecutive words of the same agreement class form one run (one box, one underline),
// so a shared phrase reads as a phrase rather than as separate boxed words.
function tokensHTML(toks, three, used) {
  const runs = [];
  for (const t of toks) {
    if (!t || t.w == null) continue;
    const cls = tokenClass(t, three, used);
    const last = runs[runs.length - 1];
    if (last && last.cls === cls && !cls.includes('lx')) last.toks.push(t);
    else runs.push({ cls, toks: [t] });
  }
  return runs.map(r => {
    const inner = r.toks.map((t, i) => esc(t.w) + (i < r.toks.length - 1 ? esc(t.post || '') + ' ' : '')).join('');
    return `<span class="tk ${r.cls}">${inner}</span>${esc(r.toks[r.toks.length - 1].post || '')}`;
  }).join(' ');
}

// Split a column into verse blocks [{v, toks, en}].
function verseBlocks(col) {
  const blocks = [];
  let cur = null;
  for (const t of arr(col.greek)) {
    if (t && t.v != null && t.w == null) { cur = { v: String(t.v), toks: [] }; blocks.push(cur); continue; }
    if (!cur) { cur = { v: null, toks: [] }; blocks.push(cur); }
    cur.toks.push(t);
  }
  const en = arr(col.english).filter(Boolean);
  const enBy = Object.fromEntries(en.filter(e => e.v != null).map(e => [String(e.v), e.t]));
  blocks.forEach(b => { b.en = b.v != null ? enBy[b.v] : undefined; });
  // English verses with no Greek block (e.g. an English-only column) still show.
  if (!blocks.length) en.forEach(e => blocks.push({ v: e.v != null ? String(e.v) : null, toks: [], en: e.t }));
  else if (blocks.every(b => b.v == null) && en.length) blocks[0].en = en.map(e => e.t).join(' ');
  // chapter for each verse (a column may cross a chapter boundary)
  let ch = num(String(col.ref || '').match(/(\d+):/)?.[1]), prev = 0;
  blocks.forEach(b => {
    if (b.v && b.v.includes(':')) { b.label = b.v; ch = num(b.v.split(':')[0]); prev = num(b.v.split(':')[1]) || 0; return; }
    const v = num(b.v);
    if (v != null && v < prev && ch != null) ch++;
    if (v != null) prev = v;
    b.label = b.v == null ? '' : (ch != null ? `${ch}:${b.v}` : b.v);
  });
  return blocks;
}

const AGREE_LABEL = {
  three: {
    't-all': 'in all three', 't-mk': 'Matthew = Mark', 't-kl': 'Mark = Luke',
    't-ml': 'Matthew = Luke, against Mark', 'lx': 'same word, different form', 't-un': 'in this Gospel only'
  },
  two: {
    't-dt': 'same word in Matthew and Luke', 't-mk': 'same word in Matthew and Mark', 't-kl': 'same word in Mark and Luke',
    'lx': 'same word, different form', 't-un': 'in this Gospel only'
  }
};

function synopsisHTML(ex, prefix) {
  const cols = arr(ex.columns).filter(c => c && gosp(c.gospel))
    .sort((a, b) => G_ORDER.indexOf(gId(a.gospel)) - G_ORDER.indexOf(gId(b.gospel)));
  if (!cols.length) return `<p class="empty">The text of this exhibit is not yet available.</p>`;
  const three = cols.length >= 3;
  const used = new Set();
  const data = cols.map(c => ({ c, G: gosp(c.gospel), blocks: verseBlocks(c) }));
  const hasEn = data.some(d => d.blocks.some(b => b.en));
  const hasGk = data.some(d => d.blocks.some(b => b.toks.length));
  const n0 = data[0].blocks.length;
  // Verse-by-verse rows only when the verses really correspond. Equal verse counts alone can be a coincidence
  // (Matt 25:14–30 and Luke 19:11–27 both have 17 verses that do not pair up), so also require that most rows
  // share wording across every column. An exhibit can force either way with "aligned": true | false.
  const sameCount = cols.length > 1 && n0 > 1 && data.every(d => d.blocks.length === n0);
  const shares = b => b.toks.some(t => t && String(t.g || '').length >= 2);
  const rowsShared = sameCount ? data[0].blocks.filter((_, i) => data.every(d => shares(d.blocks[i]))).length : 0;
  const aligned = typeof ex.aligned === 'boolean' ? ex.aligned && sameCount : sameCount && rowsShared >= 0.75 * n0;

  const block = (d, b, withLabel) => `
    <div class="syn-v">
      ${withLabel ? `<span class="syn-cell-lbl g-${d.G.cls}">${marker(d.G.kind, 10)} ${esc(d.G.name)} ${esc(b.label)}</span>` : ''}
      ${b.toks.length ? `<p class="gk" lang="grc">${b.v != null ? `<span class="vn">${esc(b.v)}</span> ` : ''}${tokensHTML(b.toks, three, used)}</p>` : ''}
      ${b.en ? `<p class="en">${!b.toks.length && b.v != null ? `<span class="vn">${esc(b.v)}</span> ` : ''}${rich(b.en)}</p>` : ''}
    </div>`;
  const head = d => `<div class="syn-head g-${d.G.cls}"><span class="syn-gname">${marker(d.G.kind, 12)} ${esc(d.G.name)}</span> <span class="syn-ref">${esc(d.c.ref)}</span></div>`;

  let grid;
  if (aligned) {
    let cells = '';
    for (let i = 0; i < n0; i++) data.forEach((d, j) => { cells += `<div class="syn-cell g-${d.G.cls}${j === data.length - 1 ? ' row-end' : ''}">${block(d, d.blocks[i], true)}</div>`; });
    grid = `<div class="syn-grid aligned" style="--n:${cols.length}">${data.map(head).join('')}${cells}</div>`;
  } else {
    grid = `<div class="syn-grid" style="--n:${cols.length}">${data.map(d => `
      <div class="syn-col g-${d.G.cls}">${head(d)}<div class="syn-cell">${d.blocks.map(b => block(d, b, false)).join('')}</div></div>`).join('')}</div>`;
  }

  const labels = three ? AGREE_LABEL.three : AGREE_LABEL.two;
  const ids = data.map(d => d.G.letter).join('');
  const lxKey = three ? 'ml' : ids === 'MK' ? 'mk' : ids === 'KL' ? 'kl' : 'dt';
  const legend = Object.keys(labels).filter(k => used.has(k)).map(k =>
    `<li><span class="tk ${k === 'lx' ? 't-un lx lx-' + lxKey : k}">${esc(labels[k])}</span></li>`).join('');
  const mode = hasEn && hasGk ? 'both' : hasEn ? 'en' : 'grc';
  const toggle = hasEn && hasGk ? `
    <div class="seg syn-mode" role="group" aria-label="Show Greek, English or both">
      <span class="seg-label">Show</span>
      <button type="button" data-synmode="both" aria-pressed="true">both</button>
      <button type="button" data-synmode="grc" aria-pressed="false">Greek</button>
      <button type="button" data-synmode="en" aria-pressed="false">English</button>
    </div>` : '';
  const allStats = arr(ex.stats).filter(s => s && (s.label || s.value));
  const isLong = s => String(s.value ?? '').length > 60;
  const stats = allStats.filter(s => !isLong(s)), statNotes = allStats.filter(isLong);
  const points = arr(ex.points).filter(Boolean);
  const usedBy = arr(ex.usedBy).filter(Boolean);
  return `
    <div class="syn" id="${esc(prefix)}-${esc(ex.id)}" data-mode="${mode}">
      <div class="syn-tools">
        ${legend ? `<ul class="syn-legend" aria-label="Key to the colouring">${legend}</ul>` : ''}
        ${toggle}
      </div>
      <div class="syn-body">${grid}</div>
      ${stats.length ? `<dl class="syn-stats">${stats.map(s => `<div><dt>${rich(s.label)}</dt><dd>${rich(s.value)}</dd></div>`).join('')}</dl>` : ''}
      ${statNotes.map(s => `<p class="syn-method"><span class="lbl">${rich(s.label)}</span> ${rich(s.value)}</p>`).join('')}
      ${points.length ? `<ul class="syn-points">${points.map(p => `<li>${rich(p)}</li>`).join('')}</ul>` : ''}
      ${usedBy.length ? `<p class="syn-used"><span class="lbl">Used in</span> ${usedBy.map(id => argLink(id) + (ARG[id] ? ` <span class="syn-used-t">${rich(ARG[id].title)}</span>` : '')).join(' · ')}</p>` : ''}
    </div>`;
}

/* ---------- 1. the problem ---------- */

function renderProblem() {
  const sides = arr(meta.sides).filter(Boolean);
  const hero = sides.length ? `
    <div class="hero wrap-wide">
      ${sides.map(s => {
        const k = SIDE_KIND[s.id] || 'open';
        const name = String(s.name || '');
        return `
        <article class="side s-${k}">
          <p class="side-label">${marker(k, 16)} ${esc(s.label || '')}</p>
          <p class="side-name${name.length > 10 ? ' long' : ''}">${rich(name)}</p>
          ${s.gloss ? `<p class="side-gloss">${rich(s.gloss)}</p>` : ''}
          <dl class="side-meta">
            ${s.heldBy ? `<div><dt>Held by</dt><dd>${refLinks(s.heldBy)}</dd></div>` : ''}
            ${s.classic ? `<div><dt>Classic statement</dt><dd>${refLinks(s.classic)}</dd></div>` : ''}
          </dl>
        </article>`;
      }).join('<div class="hero-or" aria-hidden="true">or</div>')}
    </div>` : `<div class="wrap-wide">${NOT_YET}</div>`;

  const ex = EX['john-preaching'] || EXHIBITS[0];
  const flag = ex ? `
    <div class="block wrap-wide flagship">
      <h3>${rich(ex.title)} <span class="kind">${esc(kindLabel(ex.kind))}</span></h3>
      ${ex.lede ? `<p class="exh-lede-lg">${rich(ex.lede)}</p>` : ''}
      ${synopsisHTML(ex, 'flag')}
      <p class="helper"><a href="#exhibits">More passages side by side</a> in section 2.</p>
    </div>` : '';
  $('#problem').innerHTML = sectionHead('1', 'The problem', intro('problem')) + hero + flag;
}

/* ---------- 2. the data ---------- */

const SEG_ORDER = ['triple', 'mk-mt', 'mk-lk', 'double', 'mark-alone', 'special'];

function countsFigure(C) {
  const gos = arr(C.gospels).filter(g => g && gosp(g.id));
  const segs = arr(C.segments).filter(s => s && s.id)
    .sort((a, b) => ((SEG_ORDER.indexOf(a.id) + 1) || 99) - ((SEG_ORDER.indexOf(b.id) + 1) || 99));
  if (!gos.length || !segs.length) return NOT_YET;
  const unit = String(C.unit || 'verses');
  const inVerses = unit === 'verses';
  const val = (s, g) => num(s[gId(g.id)]) ?? num(s[g.id]);
  const rows = gos.map(g => {
    const G = gosp(g.id);
    const parts = segs.map(s => ({ s, v: val(s, g) ?? 0 }));
    const sum = parts.reduce((a, p) => a + p.v, 0);
    const verses = num(g.verses);
    // Only a count in verses can be compared with the Gospel's verse total.
    const total = inVerses ? (verses ?? sum) : sum;
    const rest = inVerses ? Math.max(0, total - sum) : 0;
    return { g, G, parts, sum, total, rest, verses, len: Math.max(total, sum) };
  });
  const max = Math.max(...rows.map(r => r.len), 1);
  const counted = s => rows.some(r => val(s, r.g) != null);
  const segCls = (s, G) => s.id === 'special' ? `cs-special g-${G.cls}` : `cs-${esc(s.id)}`;

  const bars = rows.map(r => {
    const label = `${r.G.name}: ` + r.parts.filter(p => p.v).map(p => `${p.s.label || p.s.id} ${fmt(p.v)} ${unit}`).join(', ');
    const segsHTML = r.parts.filter(p => p.v > 0).map(p => `
      <span class="cs ${segCls(p.s, r.G)}" style="flex:${p.v} 1 0" title="${esc(`${p.s.label || p.s.id}: ${fmt(p.v)} ${unit}`)}">
        <span class="cs-in"><b class="cs-n">${fmt(p.v)}</b> <span class="cs-name">${esc(p.s.short || String(p.s.label || p.s.id).replace(/\s*\(.*\)\s*$/, ''))}</span></span>
      </span>`).join('') + (r.rest ? `<span class="cs cs-rest" style="flex:${r.rest} 1 0" title="not classified: ${fmt(r.rest)} ${unit}"></span>` : '');
    return `
      <div class="cnt-row">
        <span class="cnt-name g-${r.G.cls}">${marker(r.G.kind, 12)} ${esc(r.G.name)}${!inVerses && r.verses ? `<span class="cnt-verses">${fmt(r.verses)} verses in all</span>` : ''}</span>
        <div class="cnt-track">
          <div class="cnt-bar" role="img" aria-label="${esc(label)}" style="flex:0 0 calc((100% - 4.6rem) * ${(r.len / max).toFixed(4)})">${segsHTML}</div>
          <span class="cnt-total">${fmt(r.total)}</span>
        </div>
      </div>`;
  }).join('');

  const key = segs.map(s => `<li><span class="cs-sw cs-${esc(s.id)}${s.id === 'special' ? ' cs-special-key' : ''}${counted(s) ? '' : ' cs-none'}" aria-hidden="true"></span><span><b>${esc(s.label || s.id)}</b>${counted(s) ? '' : ' <span class="cnt-nc">no count</span>'}${s.note ? ` <span class="cnt-note">${rich(s.note)}</span>` : ''}${s.verses && typeof s.verses === 'string' ? ` <span class="cnt-vs">${rich(s.verses)}</span>` : ''}</span></li>`).join('');
  const table = `
    <div class="scroll-x"><table class="data-table">
      <caption class="sr">Counts (${esc(unit)}) by kind of material</caption>
      <thead><tr><th scope="col">Material (${esc(unit)})</th>${rows.map(r => `<th scope="col" class="num">${esc(r.G.name)}</th>`).join('')}</tr></thead>
      <tbody>
        ${segs.map(s => `<tr><th scope="row">${esc(s.label || s.id)}</th>${rows.map(r => { const v = val(s, r.g); return `<td class="num">${v != null ? fmt(v) : '—'}</td>`; }).join('')}</tr>`).join('')}
        ${rows.some(r => r.rest) ? `<tr><th scope="row">Not classified</th>${rows.map(r => `<td class="num">${r.rest ? fmt(r.rest) : '—'}</td>`).join('')}</tr>` : ''}
        <tr class="tot"><th scope="row">${inVerses ? 'Total verses' : `Total ${esc(unit)} counted`}</th>${rows.map(r => `<td class="num">${fmt(r.total)}</td>`).join('')}</tr>
        ${!inVerses && rows.some(r => r.verses) ? `<tr><th scope="row">Verses in the Gospel</th>${rows.map(r => `<td class="num">${fmt(r.verses)}</td>`).join('')}</tr>` : ''}
      </tbody></table></div>`;
  return `
    <figure class="counts">
      <p class="cnt-unit">${inVerses ? 'Verses, by kind of material; bar length is the Gospel’s length' : `Counted in ${esc(unit)}, by kind of material; bar length is the ${esc(unit)} counted`}</p>
      <div class="cnt-rows">${bars}</div>
      <ul class="cnt-key">${key}</ul>
      <details class="fallback"><summary>Show the numbers as a table</summary>${table}</details>
      ${C.note || C.ref || C.basis ? `<figcaption class="caption">${rich(C.note)}${refSpan(C.ref, C.basis)}</figcaption>` : ''}
    </figure>`;
}

function termsGrid(terms) {
  terms = terms.filter(t => t && (t.term || t.definition));
  if (!terms.length) return NOT_YET;
  return `<dl class="terms">${terms.map(t => `
    <div class="term"${t.id ? ` id="term-${esc(t.id)}"` : ''}>
      <dt>${rich(t.term)}</dt>
      ${t.definition ? `<dd class="term-def">${rich(t.definition)}</dd>` : ''}
      ${t.size ? `<dd class="term-row"><span class="lbl">Size</span> ${rich(t.size)}</dd>` : ''}
      ${t.example ? `<dd class="term-row"><span class="lbl">Example</span> ${rich(t.example)}</dd>` : ''}
      ${t.matters ? `<dd class="term-matters"><span class="lbl">Why it matters</span> ${rich(t.matters)}</dd>` : ''}
      ${t.ref || t.basis ? `<dd class="src">${refLinks(t.ref)} ${basisTag(t.basis)}</dd>` : ''}
      ${t.exhibit && EX[t.exhibit] ? `<dd class="term-link"><a href="#ex-${esc(t.exhibit)}">See the text: ${rich(EX[t.exhibit].title)}</a></dd>` : ''}
    </div>`).join('')}</dl>`;
}

/* order charts */

const CHAPTERS = (() => {
  const src = obj(RAW.chapters) || obj(phenomena?.chapters) || {};
  const out = {};
  for (const g of G_ORDER) {
    const c = arr(src[g] ?? src[GOSPEL[g].name]).map(num).filter(x => x != null && x > 0);
    if (!c.length) continue;
    const cum = [0];
    c.forEach(n => cum.push(cum[cum.length - 1] + n));
    out[g] = { counts: c, cum, total: cum[cum.length - 1] };
  }
  return out;
})();

// "3:23–4:1" → { a, b } as fractions of the Gospel's length (start and end of the range).
function refPos(g, ref) {
  const C = CHAPTERS[g];
  if (!C || ref == null) return null;
  const m = String(ref).match(/(\d+):(\d+)(?:\s*[–—-]\s*(\d+)(?::(\d+))?)?/);
  if (!m) return null;
  const at = (c, v) => (C.cum[Math.min(c, C.counts.length) - 1] ?? 0) + v;
  const c1 = +m[1], v1 = +m[2];
  if (c1 < 1 || c1 > C.counts.length) return null;
  const start = at(c1, v1) - 1;
  let end = m[4] ? at(+m[3], +m[4]) : m[3] ? at(c1, +m[3]) : start + 1;
  if (end <= start) end = start + 1;
  return { a: start / C.total, b: Math.min(end, C.total) / C.total, m: ((start + end) / 2) / C.total };
}

function lisSet(vals) {
  const n = vals.length, len = Array(n).fill(1), prev = Array(n).fill(-1);
  for (let i = 0; i < n; i++) for (let j = 0; j < i; j++)
    if (vals[j] <= vals[i] && len[j] + 1 > len[i]) { len[i] = len[j] + 1; prev[i] = j; }
  let best = 0;
  for (let i = 1; i < n; i++) if (len[i] > len[best]) best = i;
  const s = new Set();
  for (let i = n ? best : -1; i >= 0; i = prev[i]) s.add(i);
  return s;
}

const AGREE = { high: 'high verbal agreement', medium: 'moderate verbal agreement', low: 'low verbal agreement' };

function orderChart(kind, rows) {
  const markan = kind === 'markan';
  const axes = markan ? [['Matt', 170], ['Mark', 500], ['Luke', 830]] : [['Matt', 280], ['Luke', 720]];
  if (axes.some(([g]) => !CHAPTERS[g])) return { svg: '', ok: false };
  const W = 1000, top = 70, axisH = 620, H = top + axisH + 26;
  const X = Object.fromEntries(axes);
  const y = f => +(top + f * axisH).toFixed(1);
  let grid = '', chLabels = '';
  for (const [g, x] of axes) {
    const C = CHAPTERS[g], G = GOSPEL[g];
    grid += `<g class="oa-head">${shapeEl(G.kind, x, top - 46, 7)}<text x="${x}" y="${top - 18}" text-anchor="middle" class="oa-name g-${G.cls}">${G.name}</text></g>`;
    grid += `<line class="oa" x1="${x}" x2="${x}" y1="${top}" y2="${top + axisH}"/>`;
    const side = x < 400 ? -1 : 1;
    let lastY = -99;
    C.counts.forEach((_, i) => {
      const yy = y(C.cum[i] / C.total);
      grid += `<line class="oa-tick" x1="${x - 5}" x2="${x + 5}" y1="${yy}" y2="${yy}"/>`;
      // a chapter number is shown only where it has room; the tick is always drawn
      if (yy - lastY < (NARROW ? 21 : 16)) return;
      lastY = yy;
      chLabels += `<text class="oa-ch" x="${x + side * 10}" y="${yy + 5}" text-anchor="${side < 0 ? 'end' : 'start'}">${i + 1}</text>`;
    });
  }
  const items = rows.filter(Boolean).map((r, i) => ({
    r, i, n: r.n ?? i + 1,
    Matt: refPos('Matt', r.mt), Mark: markan ? refPos('Mark', r.mk) : null, Luke: refPos('Luke', r.lk)
  }));
  // Rows out of order relative to their base (Mark for the triple tradition, Luke for the double).
  const moved = { Matt: new Set(), Luke: new Set() };
  if (markan) {
    for (const g of ['Matt', 'Luke']) {
      const seq = items.filter(it => it.Mark && it[g]).sort((a, b) => a.Mark.m - b.Mark.m);
      const keep = lisSet(seq.map(it => it[g].m));
      seq.forEach((it, k) => { if (!keep.has(k)) moved[g].add(it.i); });
    }
  }

  const band = (g, p) => `<rect class="ob ob-${GOSPEL[g].cls}" x="${X[g] - 3.5}" y="${y(p.a)}" width="7" height="${Math.max(1.5, y(p.b) - y(p.a)).toFixed(1)}"/>`;
  const seg = (g1, p1, g2, p2, cls) => {
    const d = `M${X[g1]} ${y(p1.m)} L${X[g2]} ${y(p2.m)}`;
    return `<path class="ol-hit" d="${d}"/><path class="ol-l ${cls}" d="${d}"/>`;
  };
  let lines = '';
  for (const it of items) {
    const r = it.r;
    let inner = '';
    const desc = [];
    if (markan) {
      if (!it.Mark) continue;
      if (it.Matt) inner += seg('Mark', it.Mark, 'Matt', it.Matt, `l-mt${moved.Matt.has(it.i) ? ' moved' : ''}`);
      if (it.Luke) inner += seg('Mark', it.Mark, 'Luke', it.Luke, `l-lk${moved.Luke.has(it.i) ? ' moved' : ''}`);
      inner += [['Mark', it.Mark], ['Matt', it.Matt], ['Luke', it.Luke]].filter(x => x[1]).map(([g, p]) => band(g, p)).join('');
    } else {
      if (!it.Matt || !it.Luke) continue;
      const ag = AGREE[r.agree] ? `ag-${r.agree}` : 'ag-none';
      inner += seg('Matt', it.Matt, 'Luke', it.Luke, `l-dt ${ag}${r.overlap ? ' overlap' : ''}`);
      inner += band('Matt', it.Matt) + band('Luke', it.Luke);
    }
    if (markan) desc.push(`Mark ${r.mk}`);
    desc.push(r.mt ? `Matthew ${r.mt}` : 'not in Matthew');
    desc.push(r.lk ? `Luke ${r.lk}` : 'not in Luke');
    const notes = [];
    if (moved.Matt.has(it.i)) notes.push(markan ? 'out of Mark’s order in Matthew' : 'out of Luke’s order in Matthew');
    if (moved.Luke.has(it.i)) notes.push('out of Mark’s order in Luke');
    if (!markan && AGREE[r.agree]) notes.push(AGREE[r.agree]);
    if (!markan && r.overlap) notes.push('also has a parallel in Mark');
    if (r.exhibit && EX[r.exhibit]) notes.push('text shown in section 2');
    const label = `${it.n}. ${r.label || ''} — ${desc.join(' · ')}${notes.length ? ' (' + notes.join('; ') + ')' : ''}`;
    lines += `<g class="ol" tabindex="0" data-read="${esc(label)}" aria-label="${esc(label)}"><title>${esc(label)}</title>${inner}</g>`;
  }
  const svg = `<svg class="ochart" viewBox="0 0 ${W} ${H}" role="group" aria-label="${markan ? 'The order of Mark’s passages compared with Matthew and Luke' : 'The order of the double tradition in Matthew and Luke'}">${grid}${lines}<g class="oa-labels" aria-hidden="true">${chLabels}</g></svg>`;
  return { svg, ok: true, moved, items };
}

function orderBlock(kind, rows, title, helper) {
  rows = arr(rows).filter(Boolean);
  if (!rows.length) return '';
  const markan = kind === 'markan';
  const ch = orderChart(kind, rows);
  const list = `<ol class="ord-list">${rows.map((r, i) => {
    const flags = [];
    if (ch.ok && ch.moved.Matt.has(i)) flags.push('moved in Matthew');
    if (ch.ok && ch.moved.Luke.has(i)) flags.push('moved in Luke');
    return `<li value="${esc(r.n ?? i + 1)}"><span class="ord-lbl">${rich(r.label)}</span>
      <span class="ord-refs">${markan ? `<span class="g-mk">Mark ${esc(r.mk ?? '—')}</span> · ` : ''}<span class="g-mt">Matt ${esc(r.mt ?? '—')}</span> · <span class="g-lk">Luke ${esc(r.lk ?? '—')}</span>${!markan && AGREE[r.agree] ? ` · ${esc(AGREE[r.agree])}` : ''}${!markan && r.overlap ? ' · also in Mark' : ''}${r.exhibit && EX[r.exhibit] ? ` · <a href="#ex-${esc(r.exhibit)}">see the text</a>` : ''}</span>
      ${flags.length ? `<span class="ord-flag">${flags.join('; ')}</span>` : ''}</li>`;
  }).join('')}</ol>`;
  const key = markan
    ? `<ul class="ord-key"><li><svg width="34" height="10" aria-hidden="true"><line x1="0" x2="34" y1="5" y2="5" class="ol-l l-mt"/></svg> to Matthew</li><li><svg width="34" height="10" aria-hidden="true"><line x1="0" x2="34" y1="5" y2="5" class="ol-l l-lk"/></svg> to Luke</li><li><svg width="34" height="10" aria-hidden="true"><line x1="0" x2="34" y1="5" y2="5" class="ol-l l-mt moved"/></svg> heavy line: passage out of Mark’s order</li></ul>`
    : `<ul class="ord-key">${['high', 'medium', 'low'].filter(a => rows.some(r => r.agree === a)).map(a => `<li><svg width="34" height="10" aria-hidden="true"><line x1="0" x2="34" y1="5" y2="5" class="ol-l l-dt ag-${a}"/></svg> ${AGREE[a]}</li>`).join('')}${rows.some(r => !AGREE[r.agree]) ? `<li><svg width="34" height="10" aria-hidden="true"><line x1="0" x2="34" y1="5" y2="5" class="ol-l l-dt ag-none"/></svg> no published figure</li>` : ''}${rows.some(r => r.overlap) ? `<li><svg width="34" height="10" aria-hidden="true"><line x1="0" x2="34" y1="5" y2="5" class="ol-l l-dt ag-none overlap"/></svg> dotted: also has a parallel in Mark</li>` : ''}</ul>`;
  return `
    <figure class="order">
      <h4>${esc(title)}</h4>
      <p class="helper">${helper}</p>
      ${ch.ok ? `
        ${key}
        <p class="ord-read" aria-live="polite">Hover over or focus a line to see the passage.</p>
        <p class="helper scroll-hint">Scroll sideways to see the whole chart.</p>
        <div class="scroll-x">${ch.svg}</div>` : `<p class="empty">The chart needs the chapter lengths (content/chapters.json); the list below has the same data.</p>`}
      <details class="fallback"${ch.ok ? '' : ' open'}><summary>List the passages</summary>${list}</details>
    </figure>`;
}

function renderData() {
  const P = phenomena;
  let body = '';
  if (!P) body += `<div class="wrap-wide">${NOT_YET}</div>`;
  else {
    const C = obj(P.counts);
    body += `<div class="block wrap-wide"><h3>How much is shared</h3>${C ? countsFigure(C) : NOT_YET}</div>`;
    const terms = arr(P.terms);
    if (terms.length) body += `<div class="block wrap-wide"><h3>The terms</h3>${termsGrid(terms)}</div>`;
    const O = obj(P.order);
    if (O) {
      body += `<div class="block wrap-wide"><h3>Order</h3>
        ${O.note ? `<p class="block-intro">${rich(O.note)}${refSpan(O.ref, O.basis)}</p>` : ''}
        <div class="orders">
          ${orderBlock('markan', O.markan, 'Markan order', 'Each axis runs from the first verse of a Gospel (top) to its last, marked by chapter. Each line joins a passage in Mark to its parallel in Matthew (left) and Luke (right). Lines that run parallel keep Mark’s order; crossing lines mark a passage moved.')}
          ${orderBlock('double', O.double, 'Double tradition order', 'The same for material shared by Matthew and Luke but absent from Mark, numbered in Luke’s order. A strong common sequence points to a shared written source or to one Gospel copying the other; scattered lines to rearrangement.')}
        </div>
      </div>`;
    }
  }
  body += `<div class="block wrap-wide" id="exhibits"><h3>The texts side by side</h3>${exhibitGallery()}</div>`;
  const tk = arr(P?.takeaways).filter(Boolean);
  if (tk.length) body += `<div class="block wrap-wide"><h3>What this shows</h3><ol class="takeaways">${tk.map(t => `<li>${rich(t)}</li>`).join('')}</ol></div>`;
  $('#data').innerHTML = sectionHead('2', 'The data', P?.intro || intro('data')) + body;
}

// Each exhibit can be opened in Synoptic Canvas, which shows the whole passage in all four Gospels.
const CANVAS_URL = 'https://synoptic-canvas.vercel.app/';
const canvasLink = ex => ex && /^(mark|matthew|luke)-\d+-\d+$/.test(ex.canvas || '')
  ? `<p class="canvas-link"><a href="${CANVAS_URL}?view=1&amp;passage=${esc(ex.canvas)}&amp;lang=opengnt" target="_blank" rel="noopener">Open this passage in Synoptic Canvas</a> to read it in its full context in all four Gospels.</p>` : '';

function exhibitGallery() {
  if (!EXHIBITS.length) return NOT_YET;
  return `
    <p class="helper">Open a passage to read it in Greek and English. Colour, weight and underline mark which Gospels share each word.</p>
    <div class="exhibits">${EXHIBITS.map(ex => `
      <details class="exh" id="ex-${esc(ex.id)}">
        <summary>
          <span class="exh-top"><span class="exh-title">${rich(ex.title || ex.id)}</span>${ex.kind ? ` <span class="kind">${esc(kindLabel(ex.kind))}</span>` : ''}</span>
          <span class="exh-refs">${arr(ex.columns).filter(c => c && gosp(c.gospel)).map(c => `${esc(gosp(c.gospel).name)} ${esc(c.ref)}`).join(' // ')}</span>
          ${ex.lede ? `<span class="exh-lede">${rich(ex.lede)}</span>` : ''}
        </summary>
        <div class="exh-body">${synopsisHTML(ex, 'syn')}${canvasLink(ex)}</div>
      </details>`).join('')}
    </div>
    ${synopsis?.credit ? `<p class="credit">${rich(synopsis.credit)}</p>` : ''}`;
}

/* ---------- 3. hypotheses ---------- */

function wrapText(s, max) {
  const words = String(s).split(/\s+/); const lines = []; let cur = '';
  for (const w of words) {
    if ((cur + ' ' + w).trim().length > max && cur) { lines.push(cur); cur = w; }
    else cur = (cur + ' ' + w).trim();
  }
  if (cur) lines.push(cur);
  return lines;
}

function diagram(dg, W = 360) {
  dg = obj(dg);
  const nodes = arr(dg?.nodes).filter(n => n && n.id != null).map((n, i) => ({ ...n, id: String(n.id), idx: i, parents: [], children: [] }));
  if (!nodes.length) return '';
  const byId = Object.fromEntries(nodes.map(n => [n.id, n]));
  const edges = arr(dg.edges).map(e => Array.isArray(e)
    ? { a: String(e[0]), b: String(e[1]), style: obj(e[2])?.style }
    : obj(e) && { a: String(e.from ?? e.a), b: String(e.to ?? e.b), style: e.style })
    .filter(e => e && byId[e.a] && byId[e.b] && e.a !== e.b);
  edges.forEach(e => { byId[e.a].children.push(e.b); byId[e.b].parents.push(e.a); });

  // longest-path layering (cycle-safe), then pull sources down to just above their first child
  const memo = {};
  const depth = (id, seen = new Set()) => {
    if (id in memo) return memo[id];
    if (seen.has(id)) return 0;
    seen.add(id);
    const p = byId[id].parents;
    const d = p.length ? 1 + Math.max(...p.map(x => depth(x, seen))) : 0;
    seen.delete(id);
    return (memo[id] = d);
  };
  nodes.forEach(n => { n.layer = depth(n.id); });
  nodes.filter(n => !n.parents.length && n.children.length).forEach(n => {
    n.layer = Math.max(0, Math.min(...n.children.map(c => byId[c].layer)) - 1);
  });
  const used = [...new Set(nodes.map(n => n.layer))].sort((a, b) => a - b);
  nodes.forEach(n => { n.layer = used.indexOf(n.layer); });
  const layers = used.map(() => []);
  nodes.forEach(n => layers[n.layer].push(n));

  // An edge that skips layers gets a dummy point in each layer it crosses. The dummy takes a slot
  // in that layer like a node, so the edge runs down its own lane beside the labels, not through them.
  edges.forEach((e, k) => {
    const p = byId[e.a], c = byId[e.b];
    e.chain = [p];
    for (let l = p.layer + 1; l < c.layer; l++) {
      const d = { id: `_d${k}_${l}`, dummy: true, layer: l, idx: 1000 + k, parents: [], children: [] };
      layers[l].push(d); byId[d.id] = d; e.chain.push(d);
    }
    e.chain.push(c);
  });
  const up = n => n._up || [], down = n => n._down || [];
  edges.forEach(e => e.chain.forEach((n, i) => {
    if (i) (n._up = n._up || []).push(e.chain[i - 1]);
    if (i < e.chain.length - 1) (n._down = n._down || []).push(e.chain[i + 1]);
  }));
  layers.forEach(l => l.sort((a, b) => a.idx - b.idx).forEach((n, i) => { n.ord = i; }));
  const bary = (n, rel) => { const xs = rel(n).map(m => m.ord); return xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : n.ord; };
  const sweep = (list, rel) => list.forEach(layer => {
    layer.forEach(n => { n.key = bary(n, rel) + n.idx * 1e-4; });
    layer.sort((a, b) => a.key - b.key).forEach((n, i) => { n.ord = i; });
  });
  for (let it = 0; it < 3; it++) {
    sweep(layers.slice(1), up);
    sweep([...layers].reverse().slice(1), down);
  }

  const pad = 4, lh = 15, R = 8, gap = W < 320 ? 14 : 22, DW = 16, MINW = W < 320 ? 44 : 58;
  const charW = 7.3, subW = 6.4;
  layers.forEach(layer => {
    const real = layer.filter(n => !n.dummy);
    const free = W - pad * 2 - (layer.length - real.length) * (DW + gap) - real.length * gap;
    const maxChars = Math.max(8, Math.min(18, Math.floor(free / Math.max(1, real.length) / charW)));
    real.forEach(n => {
      n.lines = wrapText(String(n.label ?? n.id).replace(/\*/g, ''), maxChars);
      n.sub = [n.kind === 'hyp' ? 'hypothetical' : '', n.date].filter(Boolean).join(' · ');
      n.w = Math.max(MINW, ...n.lines.map(l => l.length * charW), n.sub.length * subW);
    });
    layer.filter(n => n.dummy).forEach(n => { n.w = DW; n.lines = []; n.sub = ''; });
  });
  // x: start packed and centred, then pull each node towards its neighbours while keeping order and spacing
  const place = (layer, want) => {
    const n = layer.length;
    const xs = layer.map((m, i) => want[i]);
    for (let i = 1; i < n; i++) xs[i] = Math.max(xs[i], xs[i - 1] + (layer[i - 1].w + layer[i].w) / 2 + gap);
    const over = xs[n - 1] + layer[n - 1].w / 2 - (W - pad);
    if (over > 0) xs[n - 1] -= over;
    for (let i = n - 2; i >= 0; i--) xs[i] = Math.min(xs[i], xs[i + 1] - (layer[i].w + layer[i + 1].w) / 2 - gap);
    xs[0] = Math.max(xs[0], pad + layer[0].w / 2);
    for (let i = 1; i < n; i++) xs[i] = Math.max(xs[i], xs[i - 1] + (layer[i - 1].w + layer[i].w) / 2 + gap);
    layer.forEach((m, i) => { m.x = xs[i]; });
  };
  layers.forEach(layer => {
    const total = layer.reduce((a, n) => a + n.w, 0) + gap * (layer.length - 1);
    let x = (W - total) / 2;
    layer.forEach(n => { n.x = x + n.w / 2; x += n.w + gap; });
  });
  const mean = xs => xs.reduce((a, b) => a + b, 0) / xs.length;
  for (let it = 0; it < 6; it++) {
    const order = it % 2 ? [...layers].reverse() : layers;
    const rel = it % 2 ? down : up;
    order.forEach(layer => place(layer, layer.map(n => rel(n).length ? mean(rel(n).map(m => m.x)) : n.x)));
  }
  // centre the whole drawing
  const lo = Math.min(...layers.flat().map(n => n.x - n.w / 2)), hi = Math.max(...layers.flat().map(n => n.x + n.w / 2));
  const shift = (W - (hi - lo)) / 2 - lo;
  layers.flat().forEach(n => { n.x = +(n.x + shift).toFixed(1); });

  let y = 16;
  layers.forEach(layer => {
    const real = layer.filter(n => !n.dummy);
    const h = Math.max(...real.map(n => n.lines.length * lh + (n.sub ? lh - 2 : 0)));
    layer.forEach(n => { n.y = y; n.bottom = y + R + 8 + h; });
    y += R * 2 + h + 40;
  });
  const H = y - 28;

  // spread the ends of several edges leaving or entering one node, so the arrowheads do not pile up
  const outs = {}, ins = {};
  edges.forEach(e => {
    const p = e.chain[0], c = e.chain[e.chain.length - 1];
    (outs[p.id] = outs[p.id] || []).push(e); (ins[c.id] = ins[c.id] || []).push(e);
  });
  Object.values(outs).forEach(list => list.sort((a, b) => a.chain[1].x - b.chain[1].x)
    .forEach((e, k) => { e.dx1 = (k - (list.length - 1) / 2) * 7; }));
  // incoming arrows fan out round the top of the node, each pointing at its centre
  Object.values(ins).forEach(list => list.sort((a, b) => a.chain[a.chain.length - 2].x - b.chain[b.chain.length - 2].x)
    .forEach((e, k) => { e.ang = list.length > 1 ? (-1 + 2 * k / (list.length - 1)) * Math.min(48, 18 * (list.length - 1)) * Math.PI / 180 : 0; }));

  const f1 = n => +n.toFixed(1);
  let es = '';
  edges.forEach(e => {
    const p = byId[e.a], c = byId[e.b];
    const cls = `st-edge${e.style === 'dashed' ? ' st-dashed' : ''}`;
    let d;
    if (c.layer <= p.layer) {
      // a back edge (only in a cyclic diagram): bow out to the side
      const x1 = p.x, y1 = p.bottom, x2 = c.x, y2 = c.y - R - 4;
      const bow = (Math.sign(x1 - W / 2) || 1) * W * 0.2;
      d = `M${x1} ${y1} C${x1 + bow} ${y1 + 40}, ${x2 + bow} ${y2 - 50}, ${x2} ${y2}`;
    } else {
      const pts = [[p.x + e.dx1, p.bottom]];
      e.chain.slice(1, -1).forEach(m => { pts.push([m.x, m.y - R - 2]); pts.push([m.x, m.bottom]); });
      const sx = Math.sin(e.ang), cy = Math.cos(e.ang), rr = R + 5;
      pts.push([c.x + sx * rr, c.y - cy * rr]);
      d = `M${f1(pts[0][0])} ${f1(pts[0][1])}`;
      for (let i = 1; i < pts.length; i++) {
        const [x1, y1] = pts[i - 1], [x2, y2] = pts[i];
        const last = i === pts.length - 1;
        if (x1 === x2 && !last) { d += ` L${f1(x2)} ${f1(y2)}`; continue; }
        const my = (y1 + y2) / 2, k = Math.min(26, (y2 - y1) * 0.55);
        const c2 = last ? [x2 + sx * k, y2 - cy * k] : [x2, my];
        d += ` C${f1(x1)} ${f1(my)}, ${f1(c2[0])} ${f1(c2[1])}, ${f1(x2)} ${f1(y2)}`;
      }
    }
    es += `<path d="${d}" class="${cls}" marker-end="url(#arrow)"/>`;
  });
  const ns = nodes.map(n => {
    const tip = [String(n.label ?? n.id).replace(/\*/g, ''), n.sub, n.note].filter(Boolean).join(' — ');
    const text = n.lines.map((l, i) => `<tspan x="${n.x.toFixed(1)}" dy="${i ? lh : 0}">${esc(l)}</tspan>`).join('');
    return `<g class="st-node k-${esc(n.kind || 'other')}"><title>${esc(tip)}</title>
      ${shapeEl(n.kind || 'other', n.x, n.y, R)}
      <text class="st-label${n.kind === 'hyp' ? ' st-hyp' : ''}" x="${n.x.toFixed(1)}" y="${n.y + R + 15}" text-anchor="middle">${text}</text>
      ${n.sub ? `<text class="st-date" x="${n.x.toFixed(1)}" y="${n.y + R + 15 + n.lines.length * lh - 1}" text-anchor="middle">${esc(n.sub)}</text>` : ''}
    </g>`;
  }).join('');
  const notes = nodes.filter(n => n.note);
  const aria = 'Diagram: ' + edges.map(e => `${byId[e.a].label ?? e.a} → ${byId[e.b].label ?? e.b}${e.style === 'dashed' ? ' (dashed)' : ''}`).join('; ');
  return `<svg class="stemma" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(aria)}">${es}${ns}</svg>
    ${notes.length ? `<ul class="st-notes">${notes.map(n => `<li>${marker(n.kind || 'other', 10)} <b>${rich(n.label ?? n.id)}:</b> ${rich(n.note)}</li>`).join('')}</ul>` : ''}`;
}

const holdersList = hs => {
  hs = arr(hs).filter(h => h && h.name);
  if (!hs.length) return '<p class="empty">None listed.</p>';
  return `<ul class="holders">${[...hs].sort((a, b) => (num(a.year) ?? 9999) - (num(b.year) ?? 9999)).map(h => `
    <li><span class="h-year">${esc(h.year ?? '')}</span><span class="h-body"><span class="h-name">${nameLink(h.name, h.year)}</span> ${basisTag(h.basis)}${h.note ? `<span class="h-note">${rich(h.note)}</span>` : ''}</span></li>`).join('')}
  </ul>`;
};
const bulletList = xs => { xs = arr(xs).filter(Boolean); return xs.length ? `<ul>${xs.map(t => `<li>${rich(t)}</li>`).join('')}</ul>` : '<p class="empty">None listed.</p>'; };

const NODE_KEY = [['mark', 'Mark'], ['matthew', 'Matthew'], ['luke', 'Luke'], ['hyp', 'hypothetical document'], ['oral', 'oral tradition or special material'], ['other', 'another text']];

function renderHypotheses() {
  const M = models;
  if (!M) { $('#hypotheses').innerHTML = sectionHead('3', 'Hypotheses') + `<div class="wrap-wide">${NOT_YET}</div>`; return; }
  const items = arr(M.items).filter(m => m && m.id);
  const others = arr(M.others).filter(m => m && (m.id || m.name));
  const key = `<p class="legend-row" aria-label="Key to the diagrams">${NODE_KEY.map(([k, l]) => kindTag(k, l, k === 'hyp' ? 'k-hyp-i' : '')).join(' ')}
    <span class="rtag"><svg width="30" height="10" aria-hidden="true"><path d="M1 5 H26" class="st-edge" marker-end="url(#arrow)"/></svg><span>source, used by</span></span>
    <span class="rtag"><svg width="30" height="10" aria-hidden="true"><path d="M1 5 H26" class="st-edge st-dashed" marker-end="url(#arrow)"/></svg><span>secondary or optional source</span></span></p>`;
  $('#hypotheses').innerHTML = sectionHead('3', 'Hypotheses', M.intro) + `
    <div class="wrap-wide">
      ${key}
      ${items.length ? `<div class="models">
        ${items.map(m => `
          <article class="model" data-model-card="${esc(m.id)}">
            <header class="model-head">
              <span class="model-letter">${esc(m.id)}</span>
              <div class="model-names">
                <h3>${rich(m.name || m.id)}</h3>
                ${m.title ? `<p class="model-sub">${rich(m.title)}</p>` : ''}
              </div>
              ${HYP.includes(m.id) ? `<button type="button" class="trace-btn" data-model-select="${esc(m.id)}" aria-pressed="false">Trace ${esc(m.id)}</button>` : ''}
            </header>
            <p class="model-short">${rich(m.short)}</p>
            <div class="model-stemma">${diagram(m.diagram, NARROW ? 310 : 360)}</div>
            <div class="model-explains"><h4>What it explains</h4>${bulletList(m.explains)}</div>
            <div class="model-costs"><h4>What it costs</h4>${bulletList(m.costs)}</div>
            <div class="model-holders"><h4>Who holds it</h4>${holdersList(m.holders)}</div>
            <div class="model-variants">${arr(m.variants).filter(Boolean).map(v => `<aside class="variant-note"><h4>${rich(v.title)}</h4><p>${rich(v.text)}</p></aside>`).join('')}</div>
          </article>`).join('')}
      </div>` : NOT_YET}
      ${others.length ? `
        <h3 class="sub">Other proposals</h3>
        ${M.othersIntro ? `<p class="block-intro others-intro">${rich(M.othersIntro)}</p>` : ''}
        <div class="others">
          ${others.map(m => {
            const hs = arr(m.holders).filter(h => h && h.name).sort((a, b) => (num(a.year) ?? 9999) - (num(b.year) ?? 9999));
            return `
            <article class="other-model">
              <header class="model-head sm">${m.id ? `<span class="model-letter sm">${esc(m.id)}</span>` : ''}<h3>${rich(m.name || m.id)}</h3></header>
              ${m.short ? `<p class="model-short">${rich(m.short)}</p>` : ''}
              ${m.diagram ? `<div class="model-stemma">${diagram(m.diagram, NARROW ? 290 : 300)}</div>` : ''}
              ${hs.length ? `<p class="o-holders"><span class="lbl">Held by</span> ${hs.map((h, i) => `${nameLink(h.name, h.year)}${h.year ? ` <span class="h-year">${esc(h.year)}</span>` : ''}<span class="nw"> ${basisTag(h.basis)}${i < hs.length - 1 ? ';' : ''}</span>`).join(' ')}</p>` : ''}
              ${m.standing ? `<p class="o-standing"><span class="lbl">Where it stands</span> ${rich(m.standing)}</p>` : ''}
            </article>`;
          }).join('')}
        </div>` : ''}
    </div>`;
}

/* ---------- 4. arguments ---------- */

const FAVOURS = {
  'mark-first': { label: 'favours Markan priority', kind: 'mark' },
  'matthew-first': { label: 'favours Matthean priority', kind: 'matthew' },
  independence: { label: 'favours Q', kind: 'q' },
  'luke-used-matthew': { label: 'favours Luke’s use of Matthew', kind: 'noq' },
  'matthew-used-luke': { label: 'favours Matthew’s use of Luke', kind: 'noq' },
  contact: { label: 'favours Matthew–Luke contact', kind: 'noq' },
  open: { label: 'cuts both ways', kind: 'open' }
};
const favoursTag = f => { const F = FAVOURS[f] || (f ? { label: `favours ${f}`, kind: 'open' } : null); return F ? kindTag(F.kind, F.label) : ''; };

const BEAR = {
  supports: { sym: '+', label: 'supports' },
  strains: { sym: '−', label: 'strains' },
  neutral: { sym: '·', label: 'neutral for' },
  unrated: { sym: '?', label: 'not rated for' }
};
const bearOf = (a, m) => BEAR[obj(a.bearsOn)?.[m]] && obj(a.bearsOn)[m] !== 'unrated' ? obj(a.bearsOn)[m] : 'unrated';
const bearTag = (b, m) => `<span class="bear bear-${b}"><span class="bear-sym" aria-hidden="true">${BEAR[b].sym}</span>${BEAR[b].label}${m ? ' ' + esc(m) : ''}</span>`;

const point = p => {
  if (!p) return '';
  if (typeof p === 'string') return `<li>${rich(p)}</li>`;
  return `<li>${rich(p.text)}${refSpan(p.ref, p.basis)}</li>`;
};
const points = xs => arr(xs).filter(Boolean);

// A strip plot: one row per group, one dot per item, placed by percentage. Plain HTML so it
// reflows with the page; dots that would collide are stacked.
function figureHTML(f) {
  if (!f || f.type !== 'strips') return '';
  const rows = arr(f.rows).filter(Boolean);
  const from = Number(f.band?.from);
  const rowHTML = r => {
    const placed = [];
    const dots = arr(r.items).slice().sort((x, y) => x[0] - y[0]).map(([p, ref, w]) => {
      let lane = 0;
      while (placed.some(q => q.lane === lane && Math.abs(q.p - p) < 3.2)) lane++;
      placed.push({ p, lane });
      return { p, ref, w, lane };
    });
    const lanes = Math.max(0, ...dots.map(d => d.lane)) + 1;
    return `<div class="strip-row tone-${esc(r.tone || 'n')}">
      <p class="strip-label">${rich(r.label)}</p>
      <div class="strip-track" style="height:${lanes * 13 + 32}px">
        ${Number.isFinite(from) ? `<span class="strip-band" style="left:${from}%"></span>` : ''}
        ${r.pooled != null ? `<span class="strip-pool" style="left:${Number(r.pooled)}%"><span>${esc(r.pooledLabel || '')}</span></span>` : ''}
        ${dots.map(d => `<span class="strip-dot" style="left:${d.p}%;bottom:${5 + d.lane * 13}px" title="${esc(d.ref)}: ${Math.round(d.p)}%, ${esc(d.w)} words"></span>`).join('')}
      </div>
    </div>`;
  };
  return `<figure class="strips">
    <figcaption>${rich(f.title)}</figcaption>
    ${rows.map(rowHTML).join('')}
    <div class="strip-axis" aria-hidden="true">${[0, 20, 40, 60, 80, 100].map(t => `<span style="left:${t}%">${t}%</span>`).join('')}</div>
    ${f.note ? `<p class="strip-note">${rich(f.note)}</p>` : ''}
    <details class="strip-table"><summary>The figures</summary>
      <table><thead><tr><th>Passage</th><th>Group</th><th>Identical</th><th>Words</th></tr></thead><tbody>
      ${rows.map(r => arr(r.items).map(([p, ref, w]) => `<tr><td>${esc(ref)}</td><td>${esc(String(r.label).split(':')[0])}</td><td>${Math.round(p)}%</td><td>${esc(w)}</td></tr>`).join('')).join('')}
      </tbody></table>
    </details>
  </figure>`;
}

function argItem(a) {
  const open = state.open.has(a.id);
  const bear = state.model ? bearOf(a, state.model) : null;
  const ev = points(a.evidence);
  const exs = exhibitsFor(a.id);
  const pro = points(a.pro), contra = points(a.contra), rej = points(a.rejoinder);
  const see = arr(a.seeAlso).filter(Boolean);
  return `
  <li class="arg${open ? ' open' : ''}${bear ? ' has-bear bear-row-' + bear : ''}" id="arg-${esc(a.id)}">
    <button type="button" class="arg-head" aria-expanded="${open}" aria-controls="argb-${esc(a.id)}" data-arg="${esc(a.id)}">
      <span class="arg-id">${esc(a.id)}</span>
      <span class="arg-main">
        <span class="arg-title">${rich(a.title || a.id)}</span>
        ${a.claim ? `<span class="arg-claim">${rich(a.claim)}</span>` : ''}
      </span>
      <span class="arg-tags">
        ${favoursTag(a.favours)}
        ${bear ? bearTag(bear, state.model) : ''}
      </span>
      <span class="arg-chev" aria-hidden="true"></span>
    </button>
    <div class="arg-body" id="argb-${esc(a.id)}" ${open ? '' : 'hidden'}>
      ${ev.length || exs.length || a.figure ? `<div class="evidence"><h4>The evidence</h4>
        ${ev.length ? `<ul>${ev.map(point).join('')}</ul>` : ''}
        ${a.figure ? figureHTML(a.figure) : ''}
        ${exs.length ? `<p class="ev-ex">${exs.map(x => `<a href="#ex-${esc(x.id)}" class="ex-link">See the Greek: ${rich(x.title || x.id)}</a>`).join('<br>')}</p>` : ''}
      </div>` : ''}
      <div class="procon">
        <div class="pro"><h4>For</h4>${pro.length ? `<ul>${pro.map(point).join('')}</ul>` : '<p class="empty">None listed.</p>'}</div>
        <div class="contra"><h4>Against</h4>${contra.length ? `<ul>${contra.map(point).join('')}</ul>` : '<p class="empty">None listed.</p>'}</div>
      </div>
      ${rej.length ? `<div class="rejoinder"><h4>Rejoinder</h4><ul>${rej.map(point).join('')}</ul></div>` : ''}
      ${a.status ? `<p class="status"><span class="lbl">Where it stands</span> ${rich(a.status)}</p>` : ''}
      <p class="bears-all"><span class="lbl">Bearing on the hypotheses</span> ${HYP.map(m => bearTag(bearOf(a, m), m)).join(' ')}</p>
      ${see.length ? `<p class="see-also"><span class="lbl">See also</span> ${see.map(id => `<span class="see-i">${argLink(id)}${ARG[id] ? ` <span class="see-t">${rich(ARG[id].title)}</span>` : ''}</span>`).join('<span class="see-sep" aria-hidden="true">·</span>')}</p>` : ''}
    </div>
  </li>`;
}

// Re-rendering the section must not drop keyboard focus: put it back on the same control or argument.
function renderArguments() {
  const a = document.activeElement;
  const sel = a && $('#arguments').contains(a)
    ? ['data-filter', 'data-sort', 'data-expand', 'data-arg'].map(k => a.hasAttribute(k) ? `[${k}="${a.getAttribute(k)}"]` : '').find(Boolean)
    : null;
  drawArguments();
  if (sel) $(sel, $('#arguments'))?.focus({ preventScroll: true });
}

function drawArguments() {
  const m = state.model;
  const rank = { supports: 0, neutral: 1, unrated: 2, strains: 3 };
  const model = arr(models?.items).find(x => x && x.id === m);

  let tally = '';
  if (m) {
    const c = { supports: 0, strains: 0, neutral: 0, unrated: 0 };
    ALL_ARGS.forEach(a => c[bearOf(a, m)]++);
    tally = `<p class="tally"><span><b>${esc(m)}</b>${model ? `: ${rich(model.name || '')}${model.title ? ` — ${rich(model.title)}` : ''}.` : ''}</span>
      <span class="tally-n">${bearTag('supports', '')} ${c.supports}</span>
      <span class="tally-n">${bearTag('strains', '')} ${c.strains}</span>
      <span class="tally-n">${bearTag('neutral', '')} ${c.neutral}</span>
      ${c.unrated ? `<span class="tally-n">${bearTag('unrated', '')} ${c.unrated}</span>` : ''}
      <span class="helper">of ${ALL_ARGS.length} arguments</span></p>`;
  }

  const controls = `
    <div class="arg-controls">
      ${m ? `
        <div class="seg" role="group" aria-label="Filter by bearing on ${esc(m)}">
          <span class="seg-label">Show</span>
          ${['all', 'supports', 'strains', 'neutral'].map(f => `<button type="button" data-filter="${f}" aria-pressed="${state.filter === f}">${f}</button>`).join('')}
        </div>
        <div class="seg" role="group" aria-label="Order">
          <span class="seg-label">Order</span>
          <button type="button" data-sort="order" aria-pressed="${state.sort === 'order'}">as argued</button>
          <button type="button" data-sort="supports" aria-pressed="${state.sort === 'supports'}">supports first</button>
          <button type="button" data-sort="strains" aria-pressed="${state.sort === 'strains'}">strains first</button>
        </div>` : `<p class="helper">Pick a hypothesis in the bar above (2DH, FH, MPH or 2GH) to see how each argument bears on it.</p>`}
      <div class="seg">
        <button type="button" data-expand="all">expand all</button>
        <button type="button" data-expand="none">collapse all</button>
      </div>
    </div>`;

  // compact index: every group and every argument, as jump links
  const indexOpen = state.indexOpen;
  const jump = `<details class="ajump"${indexOpen ? ' open' : ''}>
    <summary><span class="aj-sum">Index of the ${ALL_ARGS.length} arguments</span></summary>
    <nav aria-label="Index of arguments"><div class="aj-cols">${GROUPS.map(g => `
      <div class="aj-group">
        <a class="aj-gt" href="#group-${g.id}"><span class="aj-gid">${g.id}</span> ${rich(g.title)}</a>
        ${g.items.length ? `<ol>${g.items.map(a => {
          const b = m ? bearOf(a, m) : null;
          return `<li><a href="#arg-${esc(a.id)}"><span class="aj-id">${esc(a.id)}</span><span class="aj-t">${rich(a.title || a.id)}</span>${b ? `<span class="aj-b bear-${b}" title="${esc(BEAR[b].label)} ${esc(m)}">${BEAR[b].sym}</span>` : ''}</a></li>`;
        }).join('')}</ol>` : '<p class="empty">Not yet written.</p>'}
      </div>`).join('')}</div></nav>
  </details>`;

  const groups = GROUPS.map(g => {
    let items = [...g.items];
    if (m && state.filter !== 'all') items = items.filter(a => bearOf(a, m) === state.filter);
    if (m && state.sort !== 'order') {
      const dir = state.sort === 'supports' ? 1 : -1;
      items.sort((a, b) => dir * (rank[bearOf(a, m)] - rank[bearOf(b, m)]));
    }
    return `
      <section class="agroup" id="group-${g.id}">
        <header class="agroup-head">
          <h3><span class="agroup-id">${g.id}</span> ${rich(g.title)}</h3>
          ${g.question ? `<p>${rich(g.question)}</p>` : ''}
        </header>
        ${g.missing || !g.items.length ? NOT_YET
          : items.length ? `<ol class="args">${items.map(argItem).join('')}</ol>`
          : `<p class="empty">No arguments in this group match the filter.</p>`}
      </section>`;
  }).join('');

  $('#arguments').innerHTML = sectionHead('4', 'Arguments', intro('arguments')) + `
    <div class="wrap-wide">${jump}${tally}${controls}${groups}</div>`;
}

/* ---------- 5. who stands where ---------- */

function renderPositions() {
  const H = historyData, P = positions;
  const hist = arr(H?.items).filter(Boolean);
  const timeline = hist.length ? `
    <div class="block wrap-wide">
      <h3>How the question developed</h3>
      ${H.intro ? `<p class="block-intro">${rich(H.intro)}</p>` : ''}
      <ol class="hist">${hist.map(h => `
        <li><span class="hist-year">${esc(h.year ?? '')}</span>
          <span class="hist-body"><span class="hist-who">${nameLink(h.who, h.year)}</span> ${rich(h.what)}${refSpan(h.ref, h.basis)}</span></li>`).join('')}
      </ol>
    </div>` : '';

  const groups = arr(P?.groups).filter(g => g && arr(g.items).length);
  const entry = i => `<span class="p-name">${nameLink(i.name, i.year)}</span>${i.hyp ? ` <span class="hyp-tag">${esc(i.hyp)}</span>` : ''} ${basisTag(i.basis)}${i.note ? `<span class="p-note">${rich(i.note)}</span>` : ''}`;
  const pos = groups.length ? `
    <div class="block wrap-wide">
      <h3>Who stands where</h3>
      <div class="pos-key" aria-hidden="true">${kindTag('q', 'Q: Matthew and Luke independent')} ${kindTag('open', 'open, hybrid or other')} ${kindTag('noq', 'no Q: one used the other')}</div>
      <div class="pos-grid">
        ${groups.map(g => {
          const items = arr(g.items).filter(i => i && i.name).sort((a, b) => (num(a.year) ?? 9999) - (num(b.year) ?? 9999));
          const n = s => items.filter(i => (SIDE_KIND[i.side] || 'open') === s).length;
          const bar = ['q', 'open', 'noq'].map(s => n(s) ? `<span class="pb pb-${s}" style="flex:${n(s)}" title="${s === 'q' ? 'Q' : s === 'noq' ? 'no Q' : 'open'}: ${n(s)}">${n(s)}</span>` : '').join('');
          return `
          <section class="pos">
            <h4 class="pos-title">${rich(g.title)}</h4>
            <div class="pos-bar" role="img" aria-label="${n('q')} for Q, ${n('open')} open, ${n('noq')} against Q, of ${items.length}">${bar}</div>
            <div class="pos-cols" aria-hidden="true"><span>${marker('q', 11)} Q</span><span>year</span><span>${marker('noq', 11)} no Q</span></div>
            <ol class="pos-rows">
              ${items.map(i => {
                const s = SIDE_KIND[i.side] || 'open';
                return `
                <li class="prow side-${s}">
                  <span class="pc pc-q">${s === 'q' ? entry(i) : ''}</span>
                  <span class="pc pc-year">${esc(i.year ?? '')}</span>
                  <span class="pc pc-noq">${s === 'noq' ? entry(i) : ''}</span>
                  ${s === 'open' ? `<span class="pc pc-open">${marker('open', 10)} ${entry(i)} <span class="p-open">open</span></span>` : ''}
                  <span class="sr">${s === 'q' ? 'for Q' : s === 'noq' ? 'against Q' : 'open'}</span>
                </li>`;
              }).join('')}
            </ol>
          </section>`;
        }).join('')}
      </div>
    </div>` : `<div class="block wrap-wide">${NOT_YET}</div>`;
  $('#positions').innerHTML = sectionHead('5', 'Who stands where', P?.intro || intro('positions')) + timeline + pos;
}

/* ---------- 6–9. corrections, experiments, assessment, bibliography ---------- */

function renderCorrections() {
  const C = corrections;
  const items = arr(C?.items).filter(Boolean);
  $('#corrections').innerHTML = sectionHead('6', C?.title || 'Claims to retire', C?.intro || intro('corrections')) + `
    <div class="wrap-wide">${items.length ? `
      <ol class="corrections">${items.map(c => `
        <li>
          <p class="c-claim"><span class="lbl">Often said</span> ${rich(c.claim)}</p>
          <p class="c-fact"><span class="lbl">In fact</span> ${rich(c.fact)}${refSpan(c.ref, c.basis)}</p>
        </li>`).join('')}
      </ol>` : NOT_YET}
    </div>`;
}

// Experiments: each one a sub-section with the result always visible and the long detail folded.
function tableHTML(t) {
  if (!obj(t)) return '';
  const head = arr(t.head), rows = arr(t.rows).filter(Array.isArray);
  if (!rows.length) return '';
  return `<figure class="exp-table">
    ${t.caption ? `<figcaption>${rich(t.caption)}</figcaption>` : ''}
    <div class="scroll-x" tabindex="0" role="region" aria-label="${esc(t.caption || 'Table')}">
      <table>
        ${head.length ? `<thead><tr>${head.map(h => `<th scope="col">${rich(h)}</th>`).join('')}</tr></thead>` : ''}
        <tbody>${rows.map(r => `<tr>${r.map((c, i) => i === 0 ? `<th scope="row">${rich(c)}</th>` : `<td>${rich(c)}</td>`).join('')}</tr>`).join('')}</tbody>
      </table>
    </div>
    ${t.note ? `<p class="exp-table-note">${rich(t.note)}</p>` : ''}
  </figure>`;
}
const paras = xs => arr(xs).filter(Boolean).map(p => `<p>${rich(p)}</p>`).join('');
const fileLink = f => /^[\w./-]+$/.test(f) ? `<a href="${esc(f)}"><code>${esc(f)}</code></a>` : `<code>${esc(f)}</code>`;

function experimentHTML(x) {
  const bears = arr(x.bearsOn).filter(Boolean);
  const method = points(x.method), results = points(x.results), limits = points(x.limits), files = arr(x.files).filter(Boolean);
  const tables = (Array.isArray(x.table) ? x.table : [x.table]).map(tableHTML).join('');
  return `
  <article class="exp" id="exp-${esc(x.id)}">
    <header class="exp-head">
      <span class="exp-id">${esc(x.id)}</span>
      <div class="exp-main">
        <h3 class="exp-title">${rich(x.title || x.id)}</h3>
        ${x.question ? `<p class="exp-q">${rich(x.question)}</p>` : ''}
        <p class="exp-meta">
          ${x.date ? `<span><span class="lbl">Run</span> ${esc(x.date)}</span>` : ''}
          ${bears.length ? `<span><span class="lbl">Bears on</span> ${bears.map(id => argLink(id)).join(', ')}</span>` : ''}
          ${basisTag(x.basis)}
        </p>
      </div>
    </header>
    <div class="exp-body">
      ${x.summary ? `<p class="exp-summary">${rich(x.summary)}</p>` : ''}
      ${arr(x.why).length ? `<div class="exp-part"><h4>Why</h4>${paras(x.why)}</div>` : ''}
      ${method.length ? `<div class="exp-part"><h4>What was done</h4>${paras(method.map(m => typeof m === 'string' ? m : m.text))}</div>` : ''}
      ${results.length ? `<div class="exp-part evidence"><h4>Results</h4><ul>${results.map(point).join('')}</ul></div>` : ''}
      ${x.figure ? figureHTML(x.figure) : ''}
      ${tables}
      ${arr(x.reading).length ? `<div class="exp-part status exp-reading"><h4>What can be drawn from it</h4>${paras(x.reading)}</div>` : ''}
      ${limits.length ? `<details class="exp-more"><summary>Limits</summary><ul>${limits.map(point).join('')}</ul></details>` : ''}
      ${files.length ? `<details class="exp-more"><summary>For specialists: the calculations</summary><ul>${files.map(f => `<li>${fileLink(String(f))}</li>`).join('')}</ul></details>` : ''}
    </div>
  </article>`;
}

function renderResearch() {
  const R = research;
  const planned = arr(R?.planned).filter(Boolean);
  $('#research').innerHTML = sectionHead('7', R?.title || 'Experiments', R?.intro || intro('research')) + `
    <div class="wrap-wide">
      ${EXPERIMENTS.length ? EXPERIMENTS.map(experimentHTML).join('') : NOT_YET}
      ${planned.length ? `<div class="exp-planned">
        <h3>Not yet run</h3>
        <ul>${planned.map(p => `<li><span class="exp-p-title">${rich(p.title)}</span>${p.status ? ` <span class="kind">${esc(p.status)}</span>` : ''}${p.text ? ` <span class="exp-p-text">${rich(p.text)}</span>` : ''}</li>`).join('')}</ul>
      </div>` : ''}
    </div>`;
}

function renderAssessment() {
  const S = assessment;
  if (!S) { $('#assessment').innerHTML = sectionHead('8', 'Assessment') + `<div class="wrap-wide">${NOT_YET}</div>`; return; }
  const steps = arr(S.steps).filter(Boolean), cols = arr(S.columns).filter(Boolean), closing = arr(S.closing).filter(Boolean);
  $('#assessment').innerHTML = `
    <div class="wrap-wide">
      <article class="assess">
        <p class="sec-num">8</p>
        ${S.label ? `<p class="assess-label">${esc(S.label)}</p>` : ''}
        <h2>${esc(S.title || 'Assessment')}</h2>
        ${S.verdict ? `<p class="assess-verdict">${rich(S.verdict)}</p>` : ''}
        ${S.odds ? `<p class="assess-odds">${rich(S.odds)}</p>` : ''}
        ${steps.length ? `<ol class="assess-steps">${steps.map(s => `
          <li class="tone-${esc(s.tone || 'none')}"><span class="st-when">${rich(s.when)}${s.tone ? `<span class="st-tone">${esc(s.tone)}</span>` : ''}</span><span class="st-text">${rich(s.text)}</span></li>`).join('')}
        </ol>` : ''}
        ${cols.length ? `<div class="assess-cols" style="--cols:${Math.min(cols.length, 3)}">${cols.map(c => `
          <div><h3>${rich(c.title)}</h3>${bulletList(c.items)}</div>`).join('')}</div>` : ''}
        ${closing.length || S.closingTitle ? `<div class="assess-close">
          ${S.closingTitle ? `<h3>${esc(S.closingTitle)}</h3>` : ''}
          ${closing.map(p => `<p>${rich(p)}</p>`).join('')}
        </div>` : ''}
      </article>
    </div>`;
}

function renderBibliography() {
  const sorted = [...BIB].sort((a, b) => String(a.key).localeCompare(String(b.key), 'en', { sensitivity: 'base', numeric: true }));
  const n = k => sorted.filter(b => (b.basis || 'none') === k).length;
  const kinds = [...BASIS_ORDER, 'none'].filter(k => n(k));
  const SUM = { read: 'read', abstract: 'abstract only', reported: 'reported', unchecked: 'unchecked', none: 'not marked' };
  const summary = `<p class="bib-sum">${fmt(sorted.length)} works: ${kinds.map(k => `${fmt(n(k))} ${esc(SUM[k] || k)}`).join(', ')}</p>`;
  const filter = `<div class="seg bib-filter" role="group" aria-label="Show works by how they were checked">
      <span class="seg-label">Show</span>
      ${['all', ...kinds].map(k => `<button type="button" data-bibf="${esc(k)}" aria-pressed="${k === 'all'}">${esc(k === 'all' ? 'all' : SUM[k] || k)}</button>`).join('')}
    </div>`;
  $('#bibliography').innerHTML = sectionHead('9', 'Bibliography', intro('bibliography')) + `
    <div class="wrap-wide">${sorted.length ? `
      <div class="bib-head">${summary}${filter}</div>
      <ol class="bib" data-f="all">${sorted.map(b => `
        <li id="${slug(b.key)}" data-basis="${esc(b.basis || 'none')}">
          <span class="bib-key">${esc(b.key)}</span>
          <span class="bib-cite">${rich(b.cite)} ${b.url && /^https?:\/\//.test(b.url) ? `<a class="bib-url" href="${esc(b.url)}" rel="noopener" target="_blank">link</a>` : ''} ${basisTag(b.basis)}</span>
        </li>`).join('')}
      </ol>` : NOT_YET}
    </div>`;
}

function renderFooter() {
  const credits = [...arr(meta.credits)].filter(Boolean);
  // the synopsis credit repeats the SBLGNT/MorphGNT licence; show it only if the editor's credits do not
  if (synopsis?.credit && !credits.some(c => /SBL/.test(c))) credits.push(synopsis.credit);
  const companion = s => rich(s).replace(/companion page on Mark 1:41/, m => `<a href="https://dimaip.github.io/mark-1-41/">${m}</a>`);
  $('#footer').innerHTML = `
    <div class="legend" id="basis-legend-foot">${legendHTML()}</div>
    <div class="credits">${credits.map(c => `<p class="credit">${companion(c)}</p>`).join('')}</div>
    <p class="to-top"><a href="#top">Back to top ↑</a></p>`;
}

/* ---------- interaction ---------- */

function applyModel() {
  $$('.model-picker button').forEach(b => b.setAttribute('aria-checked', String(b.dataset.model === state.model)));
  $$('[data-model-card]').forEach(c => c.classList.toggle('selected', c.dataset.modelCard === state.model));
  $$('[data-model-select]').forEach(b => {
    const on = b.dataset.modelSelect === state.model;
    b.setAttribute('aria-pressed', String(on));
    b.textContent = on ? `Tracing ${b.dataset.modelSelect}` : `Trace ${b.dataset.modelSelect}`;
  });
  document.body.dataset.model = state.model;
  const u = new URL(location.href);
  state.model ? u.searchParams.set('model', state.model) : u.searchParams.delete('model');
  history.replaceState(history.state, '', u);
  safe('arguments', '4', 'Arguments', renderArguments);
}

function setModel(m) {
  state.model = m;
  if (!m) { state.filter = 'all'; state.sort = 'order'; }
  applyModel();
}

function flash(el) {
  if (!el) return;
  el.classList.remove('flash'); void el.offsetWidth; el.classList.add('flash');
}
const scrollTo = el => el?.scrollIntoView({ behavior: reduceMotion.matches ? 'auto' : 'smooth', block: 'start' });

function openArg(id, scroll = true) {
  if (!ARG[id]) return false;
  state.open.add(id);
  if (state.model && state.filter !== 'all' && bearOf(ARG[id], state.model) !== state.filter) state.filter = 'all';
  renderArguments();
  const el = document.getElementById('arg-' + id);
  if (scroll) { scrollTo(el); flash(el); }
  return true;
}
function openExperiment(id, scroll = true) {
  const el = document.getElementById('exp-' + id);
  if (!el) return false;
  if (scroll) { scrollTo(el); flash(el); }
  return true;
}
function openExhibit(id, scroll = true) {
  const el = document.getElementById('ex-' + id);
  if (!el) return false;
  el.open = true;
  if (scroll) { scrollTo(el); flash(el); }
  return true;
}
function followHash(scroll = true) {
  const h = decodeURIComponent(location.hash.slice(1));
  if (!h) return;
  if (h.startsWith('arg-') && openArg(h.slice(4), scroll)) return;
  if (h.startsWith('ex-') && openExhibit(h.slice(3), scroll)) return;
  if (h.startsWith('exp-') && openExperiment(h.slice(4), scroll)) return;
  const t = document.getElementById(h);
  if (t && scroll) t.scrollIntoView();
}

document.addEventListener('click', e => {
  const pick = e.target.closest('.model-picker button');
  if (pick) return setModel(pick.dataset.model);
  const sel = e.target.closest('[data-model-select]');
  if (sel) return setModel(state.model === sel.dataset.modelSelect ? '' : sel.dataset.modelSelect);

  const head = e.target.closest('.arg-head');
  if (head && !e.target.closest('a')) {
    const id = head.dataset.arg;
    const li = head.parentElement, body = li.querySelector('.arg-body');
    const open = !state.open.has(id);
    open ? state.open.add(id) : state.open.delete(id);
    li.classList.toggle('open', open);
    head.setAttribute('aria-expanded', String(open));
    body.hidden = !open;
    return;
  }
  const f = e.target.closest('[data-filter]');
  if (f) { state.filter = f.dataset.filter; return renderArguments(); }
  const s = e.target.closest('[data-sort]');
  if (s) { state.sort = s.dataset.sort; return renderArguments(); }
  const x = e.target.closest('[data-expand]');
  if (x) {
    state.open = x.dataset.expand === 'all' ? new Set(ALL_ARGS.map(a => a.id)) : new Set();
    return renderArguments();
  }
  const bf = e.target.closest('[data-bibf]');
  if (bf) { setBibFilter(bf.dataset.bibf); return; }
  const sm = e.target.closest('[data-synmode]');
  if (sm) {
    const syn = sm.closest('.syn');
    syn.dataset.mode = sm.dataset.synmode;
    $$('[data-synmode]', syn).forEach(b => b.setAttribute('aria-pressed', String(b === sm)));
    return;
  }
  const a = e.target.closest('a[href^="#"]');
  if (a) {
    const id = decodeURIComponent(a.getAttribute('href').slice(1));
    if ((id.startsWith('arg-') && ARG[id.slice(4)]) || ((id.startsWith('ex-') || id.startsWith('exp-')) && document.getElementById(id))) {
      e.preventDefault();
      history.pushState(null, '', '#' + id);
      followHash();
      return;
    }
    if (id.startsWith('bib-')) setBibFilter('all');
    flash(document.getElementById(id));
  }
});

function setBibFilter(k) {
  const list = $('ol.bib');
  if (!list) return;
  list.dataset.f = k;
  $$('[data-bibf]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.bibf === k)));
}
document.addEventListener('toggle', e => { if (e.target.classList?.contains('ajump')) state.indexOpen = e.target.open; }, true);
addEventListener('hashchange', () => followHash());
addEventListener('popstate', () => followHash());

// order charts: highlight a line on hover or focus
function setLine(g) {
  const fig = g?.closest('.order') || null;
  $$('.ochart.hl').forEach(s => { if (!fig || !fig.contains(s)) s.classList.remove('hl'); });
  $$('.ol.on').forEach(x => { if (x !== g) x.classList.remove('on'); });
  if (!g) return;
  g.classList.add('on');
  g.ownerSVGElement.classList.add('hl');
  const out = $('.ord-read', fig);
  if (out) out.textContent = g.dataset.read;
}
document.addEventListener('mouseover', e => { const g = e.target.closest?.('.ol'); if (g) setLine(g); });
document.addEventListener('mouseout', e => { if (e.target.closest?.('.ol') && !e.relatedTarget?.closest?.('.ol')) setLine(null); });
document.addEventListener('focusin', e => { const g = e.target.closest?.('.ol'); if (g) setLine(g); });
document.addEventListener('focusout', e => { if (e.target.closest?.('.ol')) setLine(null); });

// keyboard arrows within the hypothesis radiogroup
$('.model-picker').addEventListener('keydown', e => {
  if (!['ArrowLeft', 'ArrowRight'].includes(e.key)) return;
  const btns = $$('.model-picker button');
  const i = btns.findIndex(b => b.dataset.model === state.model);
  const n = btns[(i + (e.key === 'ArrowRight' ? 1 : -1) + btns.length) % btns.length];
  setModel(n.dataset.model); n.focus(); e.preventDefault();
});

// print: open everything, then restore
let printClosed = [];
addEventListener('beforeprint', () => { printClosed = $$('details:not([open])'); printClosed.forEach(d => { d.open = true; }); });
addEventListener('afterprint', () => { printClosed.forEach(d => { d.open = false; }); printClosed = []; });

// highlight the current section in the bar
const links = $$('.bar-links a');
const io = new IntersectionObserver(entries => {
  entries.forEach(en => {
    if (en.isIntersecting) links.forEach(l => l.classList.toggle('current', l.getAttribute('href') === '#' + en.target.id));
  });
}, { rootMargin: '-45% 0px -50% 0px' });

/* ---------- boot ---------- */

function safe(id, n, title, fn) {
  try { fn(); } catch (err) {
    console.error(`Section ${id}:`, err);
    $('#' + id).innerHTML = sectionHead(n, title) + `<div class="wrap-wide"><p class="empty">This section could not be displayed.</p></div>`;
  }
}

safe('problem', '1', 'The problem', renderProblem);
safe('data', '2', 'The data', renderData);
safe('hypotheses', '3', 'Hypotheses', renderHypotheses);
safe('positions', '5', 'Who stands where', renderPositions);
safe('corrections', '6', 'Claims to retire', renderCorrections);
safe('research', '7', 'Experiments', renderResearch);
safe('assessment', '8', 'Assessment', renderAssessment);
safe('bibliography', '9', 'Bibliography', renderBibliography);
try { renderFooter(); } catch (err) { console.error(err); }
applyModel();
$$('main > section').forEach(s => io.observe(s));
followHash();
// The web font can shift the long page after the first jump; settle on an experiment once it has loaded.
if (location.hash.startsWith('#exp-')) document.fonts?.ready.then(() => document.getElementById(decodeURIComponent(location.hash.slice(1)))?.scrollIntoView());
