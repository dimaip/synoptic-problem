#!/usr/bin/env python3
"""Build content/synopsis.json and content/chapters.json from MorphGNT SBLGNT data.

Usage (from the repo root):
  python3 tools/build_synopsis.py            # write content/synopsis.json and content/chapters.json
  python3 tools/build_synopsis.py --check    # also print every exhibit as text with agreement markers
  python3 tools/build_synopsis.py --dump Matt 3:11-12   # print numbered tokens of a passage (for writing blocks)

Inputs:  tools/exhibits.json (hand-written spec), tools/data/6?-*-morphgnt.txt (downloaded data).
The Greek text is taken only from the data files; nothing Greek is typed by hand.

Alignment (per pair of columns: Matt-Mark, Matt-Luke, Mark-Luke):
  1. Longest common subsequence on MorphGNT's normalised word-form (lower-cased), weighted so that content
     words (3) outrank articles, conjunctions, prepositions, particles, negatives and pronouns (1).
  2. Between consecutive form matches, a second LCS on lemmas over the still-unmatched tokens
     (articles excluded from this pass).
  3. A light word (article, conjunction, preposition, particle, pronoun, negative) is kept as a match only
     if a matched content word lies within three words of it in both texts; otherwise it is dropped as
     chance (exhibit option "filterIsolated": false turns this off).
  An exhibit may restrict matching to paired "blocks" of verses (tokens only match within the same block),
  and may set "align": "bag" to match by multiset (order ignored) inside each block instead of by LCS.
  Three-way consistency: if a token is matched to both other columns and those two partners are unmatched
  with each other but identical, they are linked too.
Token fields: w (word), post (trailing punctuation), g (form agreement), gl (form-or-lemma agreement).
"""
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "tools", "data")
SPEC = os.path.join(ROOT, "tools", "exhibits.json")
OUT = os.path.join(ROOT, "content", "synopsis.json")
OUT_CH = os.path.join(ROOT, "content", "chapters.json")

FILES = {"Matt": "61-Mt-morphgnt.txt", "Mark": "62-Mk-morphgnt.txt", "Luke": "63-Lk-morphgnt.txt"}
LETTER = {"Matt": "M", "Mark": "K", "Luke": "L"}
ORDER = ["Matt", "Mark", "Luke"]
NAME = {"Matt": "Matthew", "Mark": "Mark", "Luke": "Luke"}
SIGLA = "⸀⸁⸂⸃⸄⸅⟦⟧[]"
SENT_END = set(".·;")

CREDIT = ("Greek text: The Greek New Testament: SBL Edition (SBLGNT), © 2010 Society of Biblical Literature "
          "and Logos Bible Software, licensed CC BY 4.0. Lemmas and normalised forms: MorphGNT SBLGNT "
          "(morphgnt.org, J. K. Tauber et al.), licensed CC BY-SA 3.0. Alignment, statistics and English "
          "working translation generated for this site.")


# ---------------------------------------------------------------- data

def load_book(gospel):
    toks = []
    with open(os.path.join(DATA, FILES[gospel]), encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) != 7:
                continue
            bcv, pos, parse, text, word, norm, lemma = parts
            ch, v = int(bcv[2:4]), int(bcv[4:6])
            clean = "".join(c for c in text if c not in SIGLA)
            i = clean.find(word)
            if i < 0:
                raise SystemExit("cannot locate word %r in %r (%s %s)" % (word, text, gospel, bcv))
            toks.append({"ch": ch, "v": v, "w": word, "pre": clean[:i], "post": clean[i + len(word):],
                         "norm": norm.replace("(", "").replace(")", "").lower(),
                         "lemma": lemma.lower(), "pos": pos})
    by_verse = {}
    for t in toks:
        lst = by_verse.setdefault((t["ch"], t["v"]), [])
        t["i"] = len(lst) + 1
        lst.append(t)
    return toks, by_verse


def chapters(toks):
    out = {}
    for t in toks:
        out[t["ch"]] = max(out.get(t["ch"], 0), t["v"])
    return [out[c] for c in sorted(out)]


# ---------------------------------------------------------------- references
# Grammar (one chapter per column):  "3:7–10"  "14:1–5, 9–12"  "6:5–6a"  "6:21b"  "3:11@1–9"
#   a / b = the verse up to / after the first sentence-ending punctuation (. · ;)
#   @i–j  = words i..j of a single verse (1-based, inclusive)

def norm_dash(s):
    return s.replace("–", "-").replace("—", "-").replace(" ", "")


def verse_tokens(by_verse, ch, v, part=None):
    lst = by_verse.get((ch, v))
    if not lst:
        raise SystemExit("verse %d:%d not in data" % (ch, v))
    if part is None:
        return list(lst)
    if part.startswith("@"):
        a, _, b = part[1:].partition("-")
        a, b = int(a), int(b or a)
        return lst[a - 1:b]
    cut = next((k + 1 for k, t in enumerate(lst) if set(t["post"]) & SENT_END), len(lst))
    return lst[:cut] if part == "a" else lst[cut:]


def parse_ref(by_verse, ref):
    """Return list of tokens (in order) for a reference string."""
    out, ch = [], None
    for item in norm_dash(ref).split(","):
        if ":" in item:
            c, item = item.split(":", 1)
            ch = int(c)
        m = re.fullmatch(r"(\d+)(a|b|@\d+(?:-\d+)?)?(?:-(\d+)(a|b)?)?", item)
        if not m or ch is None:
            raise SystemExit("bad reference %r" % ref)
        v1, p1, v2, p2 = int(m.group(1)), m.group(2), m.group(3), m.group(4)
        if v2 is None:
            out += verse_tokens(by_verse, ch, v1, p1)
        else:
            for v in range(v1, int(v2) + 1):
                part = p1 if v == v1 else (p2 if v == int(v2) else None)
                out += verse_tokens(by_verse, ch, v, part)
    return out


# ---------------------------------------------------------------- alignment

# "Light" words: article, conjunction, preposition, particle, personal and relative pronoun, negative.
LIGHT_POS = {"RA", "C-", "P-", "X-", "RP", "RR"}
FUNCTION_LEMMA = {"οὐ", "μή"}


NEAR = 3


def is_light(t):
    return t["pos"] in LIGHT_POS or t["lemma"] in FUNCTION_LEMMA


def weight(t):
    """Content words weigh 3, light words 1, so a shared noun or verb outranks two shared particles."""
    return 1 if is_light(t) else 3


def lcs(a, b, w):
    """Index pairs of a maximum-weight common subsequence of a and b; w[i] = weight of a[i].
    Ties prefer the earliest diagonal."""
    n, m = len(a), len(b)
    if not n or not m:
        return []
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        ai, row, nxt, wi = a[i], dp[i], dp[i + 1], w[i]
        for j in range(m - 1, -1, -1):
            best = max(nxt[j], row[j + 1])
            if ai == b[j]:
                best = max(best, nxt[j + 1] + wi)
            row[j] = best
    pairs, i, j = [], 0, 0
    while i < n and j < m:
        if a[i] == b[j] and dp[i][j] == dp[i + 1][j + 1] + w[i]:
            pairs.append((i, j)); i += 1; j += 1
        elif dp[i + 1][j] >= dp[i][j + 1]:
            i += 1
        else:
            j += 1
    return pairs


def bag(a, b):
    used, pairs = set(), []
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            if j not in used and x == y:
                used.add(j); pairs.append((i, j)); break
    return pairs


def lemma_key(t):
    """Lemma used for the second pass; articles never match by lemma alone (ὁ/τοῦ/τῶν is not agreement)."""
    return ("article", id(t)) if t["pos"] == "RA" else t["lemma"]


def align_block(A, B, mode, filter_isolated=True):
    """A, B: lists of tokens. Returns (form_pairs, lemma_pairs) as lists of (ia, ib)."""
    fa = [t["norm"] for t in A]
    fb = [t["norm"] for t in B]
    wa = [weight(t) for t in A]
    if mode == "bag":
        form = bag(fa, fb)
        ua = [i for i in range(len(A)) if i not in {p[0] for p in form}]
        ub = [j for j in range(len(B)) if j not in {p[1] for p in form}]
        lem = [(ua[x], ub[y]) for x, y in bag([lemma_key(A[i]) for i in ua], [lemma_key(B[j]) for j in ub])]
        return form, lem
    form = lcs(fa, fb, wa)
    lem = []
    anchors = [(-1, -1)] + form + [(len(A), len(B))]
    for (a0, b0), (a1, b1) in zip(anchors, anchors[1:]):
        ga, gb = list(range(a0 + 1, a1)), list(range(b0 + 1, b1))
        if ga and gb:
            for x, y in lcs([lemma_key(A[i]) for i in ga], [lemma_key(B[j]) for j in gb], [wa[i] for i in ga]):
                lem.append((ga[x], gb[y]))
    if filter_isolated:
        # A light word (article, conjunction, preposition, particle, negative, pronoun) counts only if a
        # matched content word lies within NEAR words of it in both texts; otherwise it is treated as chance.
        allp = set(form) | set(lem)
        content = [(i, j) for (i, j) in allp if not is_light(A[i])]
        drop = {(i, j) for (i, j) in allp if is_light(A[i])
                and not any(abs(i2 - i) <= NEAR and abs(j2 - j) <= NEAR for (i2, j2) in content)}
        form = [p for p in form if p not in drop]
        lem = [p for p in lem if p not in drop]
    return form, lem


def align_exhibit(ex, cols, blocks, mode):
    """cols: {gospel: [tokens]}. Sets t['g'], t['gl'] on every token."""
    gos = [g for g in ORDER if g in cols]
    pos = {g: {id(t): k for k, t in enumerate(cols[g])} for g in gos}
    # match[(g1,g2)][kind] = {index in g1: index in g2}
    match = {}
    for x in range(len(gos)):
        for y in range(x + 1, len(gos)):
            g1, g2 = gos[x], gos[y]
            F, Lm = {}, {}
            for blk in blocks:
                if blk.get(g1) is None or blk.get(g2) is None:
                    continue
                A, B = blk[g1], blk[g2]
                f, l = align_block(A, B, blk.get("_mode", mode), ex.get("filterIsolated", True))
                for i, j in f:
                    F[pos[g1][id(A[i])]] = pos[g2][id(B[j])]
                for i, j in l:
                    Lm[pos[g1][id(A[i])]] = pos[g2][id(B[j])]
            match[(g1, g2)] = {"form": F, "lemma": Lm}
            match[(g2, g1)] = {"form": {v: k for k, v in F.items()}, "lemma": {v: k for k, v in Lm.items()}}
    # three-way closure
    if len(gos) == 3:
        for kind, key in (("form", "norm"), ("lemma", "lemma")):
            for g in gos:
                o1, o2 = [h for h in gos if h != g]
                both = lambda a, b, k: match[(a, b)]["form"].get(k, match[(a, b)]["lemma"].get(k)) \
                    if kind == "lemma" else match[(a, b)]["form"].get(k)
                for k in range(len(cols[g])):
                    p, q = both(g, o1, k), both(g, o2, k)
                    if p is None or q is None:
                        continue
                    if both(o1, o2, p) is None and both(o2, o1, q) is None and \
                            cols[o1][p][key] == cols[o2][q][key]:
                        match[(o1, o2)][kind][p] = q
                        match[(o2, o1)][kind][q] = p
    for g in gos:
        for k, t in enumerate(cols[g]):
            fs = [h for h in gos if h != g and k in match[(g, h)]["form"]]
            ls = [h for h in gos if h != g and (k in match[(g, h)]["form"] or k in match[(g, h)]["lemma"])]
            t["g"] = "".join(LETTER[h] for h in ORDER if h == g or h in fs) if fs else ""
            t["gl"] = "".join(LETTER[h] for h in ORDER if h == g or h in ls) if ls else ""


# ---------------------------------------------------------------- stats

def fmt_pct(n, d):
    return "%d%%" % round(100.0 * n / d) if d else "–"


def per_col(gos, fn):
    vals = [(g, fn(g)) for g in gos]
    if len({v for _, v in vals}) == 1:
        return "%d in each column" % vals[0][1]
    return " · ".join("%s %d" % (NAME[g], v) for g, v in vals)


def make_stats(ex, cols, method_note):
    gos = [g for g in ORDER if g in cols]
    n = {g: len(cols[g]) for g in gos}
    stats = [{"label": "Words per column", "value": " · ".join("%s %d" % (NAME[g], n[g]) for g in gos)}]
    counts = {"words": n}
    if len(gos) == 2:
        a, b = gos
        same = sum(1 for t in cols[a] if t["g"])
        lem = sum(1 for t in cols[a] if t["gl"])
        stats.append({"label": "Words identical in form",
                      "value": "%d — %s of %s, %s of %s" % (same, fmt_pct(same, n[a]), NAME[a], fmt_pct(same, n[b]), NAME[b])})
        stats.append({"label": "Same word, any form (lemma)",
                      "value": "%d — %s of %s, %s of %s" % (lem, fmt_pct(lem, n[a]), NAME[a], fmt_pct(lem, n[b]), NAME[b])})
        counts.update({"identical": same, "lemma": lem})
    else:
        cnt = {}
        for kind, fld in (("form", "g"), ("lemma", "gl")):
            cnt[kind] = {g: {c: sum(1 for t in cols[g] if t[fld] == c) for c in ("MKL", "MK", "KL", "ML", "")}
                         for g in gos}
        c = cnt["form"]
        stats.append({"label": "All three identical (MKL)", "value": per_col(gos, lambda g: c[g]["MKL"])})
        stats.append({"label": "Matthew and Mark only (MK)", "value": per_col(["Matt", "Mark"], lambda g: c[g]["MK"])})
        stats.append({"label": "Mark and Luke only (KL)", "value": per_col(["Mark", "Luke"], lambda g: c[g]["KL"])})
        stats.append({"label": "Matthew and Luke against Mark (ML)",
                      "value": per_col(["Matt", "Luke"], lambda g: c[g]["ML"])})
        cl = cnt["lemma"]
        stats.append({"label": "ML by lemma (Mark lacks the word in any form)",
                      "value": per_col(["Matt", "Luke"], lambda g: cl[g]["ML"])})
        stats.append({"label": "Words in no other column", "value": " · ".join("%s %d" % (NAME[g], c[g][""]) for g in gos)})
        counts.update({k: {g: {(cc or "unique"): v for cc, v in d.items()} for g, d in cnt[k].items()}
                       for k in cnt})
    stats.append({"label": "How counted", "value": method_note})
    return stats, counts


# ---------------------------------------------------------------- build

def method_text(ex):
    base = ("Every word counts, articles and καί included; forms compared after MorphGNT normalisation "
            "(accents, movable ν, elision). An article, conjunction, preposition, particle, pronoun or "
            "negative counts as shared only when a shared content word stands within three words of it in both texts")
    if ex.get("align") == "bag":
        how = "; words matched regardless of order within paired verse groups, because the order differs"
    else:
        how = ("; words matched in sequence (longest common subsequence, content words weighted above "
               "function words)")
        if ex.get("blocks"):
            how += " within paired verse groups"
    note = ex.get("alignNote")
    return base + how + "." + (" " + note if note else "")


def build_exhibit(ex, books):
    cols = {}
    out_cols = []
    for c in ex["columns"]:
        g = c["gospel"]
        _, by_verse = books[g]
        toks = [dict(t) for t in parse_ref(by_verse, c["ref"])]
        cols[g] = toks
    # blocks: list of {gospel: ref or null}; default = one block of everything
    blocks = []
    for b in ex.get("blocks") or [{g: c["ref"] for g, c in ((c["gospel"], c) for c in ex["columns"])}]:
        blk = {}
        for g in cols:
            if b.get(g):
                ids = {(t["ch"], t["v"], t["i"]) for t in parse_ref(books[g][1], b[g])}
                blk[g] = [t for t in cols[g] if (t["ch"], t["v"], t["i"]) in ids]
                if len(blk[g]) != len(ids):
                    raise SystemExit("%s: block %r lies outside the column" % (ex["id"], b[g]))
            else:
                blk[g] = None
        if b.get("align"):
            blk["_mode"] = b["align"]
        blocks.append(blk)
    align_exhibit(ex, cols, blocks, ex.get("align", "lcs"))
    for c in ex["columns"]:
        g = c["gospel"]
        greek, last = [], None
        for t in cols[g]:
            if (t["ch"], t["v"]) != last:
                if last is not None and t["v"] != last[1] + 1:
                    greek.append({"gap": True})
                greek.append({"v": str(t["v"])})
                last = (t["ch"], t["v"])
            greek.append({"w": t["w"], "post": t["post"], "g": t["g"], "gl": t["gl"]})
        verses = [x["v"] for x in greek if "v" in x]
        eng = c.get("english", {})
        missing = [v for v in verses if v not in eng]
        extra = [v for v in eng if v not in verses]
        if missing or extra:
            raise SystemExit("%s %s: English missing for %s, extra %s" % (ex["id"], g, missing, extra))
        out_cols.append({"gospel": g, "ref": c["ref"], "greek": greek,
                         "english": [{"v": v, "t": eng[v]} for v in verses]})
    stats, counts = make_stats(ex, cols, method_text(ex))
    res = {"id": ex["id"], "title": ex["title"], "kind": ex["kind"], "lede": ex["lede"],
           "columns": out_cols, "stats": stats, "counts": counts,
           "points": ex["points"], "usedBy": ex["usedBy"]}
    return res, cols


def show(res, cols):
    print("=" * 100)
    print("%s  [%s]  %s" % (res["id"], res["kind"], res["title"]))
    for c in res["columns"]:
        g = c["gospel"]
        print("-- %s %s" % (g, c["ref"]))
        line = []
        for x in c["greek"]:
            if "v" in x:
                line.append("\n  (%s)" % x["v"])
            elif "gap" in x:
                line.append("\n  [...]")
            else:
                tag = "[%s]" % x["g"] if x["g"] else ("{%s}" % x["gl"] if x["gl"] else "")
                line.append(x["w"] + tag + x["post"])
        print(" ".join(line))
        for e in c["english"]:
            print("   %s %s" % (e["v"], e["t"]))
    for s in res["stats"]:
        print("   * %s: %s" % (s["label"], s["value"]))


def main(argv):
    books = {g: load_book(g) for g in ORDER}
    if "--dump" in argv:
        k = argv.index("--dump")
        g, ref = argv[k + 1], argv[k + 2]
        for t in parse_ref(books[g][1], ref):
            print("%d:%d@%d\t%s%s\t%s" % (t["ch"], t["v"], t["i"], t["w"], t["post"], t["lemma"]))
        return
    with open(SPEC, encoding="utf-8") as f:
        spec = json.load(f)
    exhibits = []
    for ex in spec["exhibits"]:
        res, cols = build_exhibit(ex, books)
        for g, toks in cols.items():
            for t in toks:
                if t["pre"]:
                    print("warning: %s %s %d:%d leading punctuation %r dropped" %
                          (ex["id"], g, t["ch"], t["v"], t["pre"]), file=sys.stderr)
        exhibits.append(res)
        if "--check" in argv:
            show(res, cols)
    out = {"credit": CREDIT, "exhibits": exhibits}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    text = json.dumps(out, ensure_ascii=False, indent=2)
    # put each Greek token / English verse object on one line to keep the file readable and small
    text = re.sub(r"\{\n\s+(\"(?:v|w|gap)\": [^\n]*?(?:,\n\s+\"[a-z]+\": [^\n]*?)*)\n\s+\}",
                  lambda m: "{ " + re.sub(r",\n\s+", ", ", m.group(1)) + " }", text)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    with open(OUT_CH, "w", encoding="utf-8") as f:
        json.dump({g: chapters(books[g][0]) for g in ORDER}, f, ensure_ascii=False)
        f.write("\n")
    print("wrote %s (%d exhibits) and %s" % (os.path.relpath(OUT, ROOT), len(exhibits), os.path.relpath(OUT_CH, ROOT)),
          file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
