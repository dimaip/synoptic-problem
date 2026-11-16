<img src="assets/icon.svg" width="64" height="64" alt="">

# Was There a Q? — the Synoptic Problem

A small static explainer site on the Synoptic Problem: did Matthew and Luke
independently use Mark and a lost sayings source, Q, or did one of them read
the other?

It sets out the problem and the two broad answers, the data (how much the
Gospels share, the order of their material, and the Greek texts side by side,
marked by which Gospels share each word), four main hypotheses and eight minor
ones with diagrams, the arguments grouped by question (each with its evidence,
the case for and against, the rejoinder and where it stands, plus a hypothesis
selector that shows how each argument bears on a chosen hypothesis), who holds
which position, claims to retire, an assessment that takes a position, and a bibliography.
It is a sibling of [*Angry or Compassionate? Mark 1:41*](https://dimaip.github.io/mark-1-41/)
and follows its layout and conventions.

## Files

```
index.html          page shell: masthead, section bar with the hypothesis picker, empty sections
styles.css          all styles (light and dark, phone layout, print)
app.js              renders every section from content/ at load time; no framework, no build step
content/
  meta.json         title, lede, the two answers at the top, section intros, basis legend, credits
  phenomena.json    counts, terms, order tables (Markan and double tradition), takeaways
  synopsis.json     the Greek exhibits            (generated: see below)
  chapters.json     verses per chapter, for the order charts (generated: see below)
  models.json       the four main hypotheses, othersIntro and the other proposals, with diagram data
  arguments/        one file per group, loaded in this order: P, I, C, D, Q, M, S
  positions.json    who stands where, in period groups
  history.json      how the question developed (timeline)
  corrections.json  claims to retire
  assessment.json   the site's own assessment (optional: until it exists the section says "Not yet written")
  bibliography.json every work cited: key, citation, optional url, basis
tools/
  build_synopsis.py builds content/synopsis.json and content/chapters.json
  exhibits.json     hand-written specification of each exhibit (passages, title, lede, points, usedBy)
  data/             MorphGNT SBLGNT data for Matthew, Mark and Luke (unmodified; see tools/data/README)
  kloppenborg_test.py   counts of verbal agreement behind the "computed" points in arguments C9 and S1;
                        needs the public/data folder of Synoptic Canvas (synoptic-canvas.vercel.app)
  kloppenborg_test.txt  its output, as cited on the page
assets/icon.svg     repository icon
```

## Editing the content

Fix a date, add a reference or change wording in `content/`; the page is
rendered from these files at load time, so no layout code needs to change.

- Text fields accept plain text, `*italic*`, Greek (tagged automatically for
  the Greek font) and `[[C3]]`, which becomes a link that opens argument C3.
  A link to an argument that does not exist yet is shown greyed out, not broken.
- Bibliography entries are linked automatically wherever a reference contains
  an entry's `key` (e.g. `Goodacre 2002, ch. 8`). The longest key wins, so
  `Goodacre 2002a` never links to `Goodacre 2002`; keys with `&`, `et al.`,
  diacritics or letter suffixes work as written. Each entry's anchor is
  `#bib-` plus the key in lower case with accents removed, `&` as `and` and
  other punctuation as hyphens (`Müller & Omerzu 2018` → `#bib-muller-and-omerzu-2018`).
- Every item can carry a `basis` (`read`, `abstract`, `reported`, `unchecked`),
  shown as a small marker and explained in the legend at the top and bottom
  of the page.
- A missing or invalid file does not break the page: its section shows
  "Not yet written".

Links: `#arg-C3` opens an argument, `#ex-john-preaching` opens an exhibit,
`#bib-goodacre-2002` jumps to a bibliography entry, and `?model=FH` traces a
hypothesis through the arguments.

## Regenerating the Greek synopsis

`content/synopsis.json` and `content/chapters.json` are generated; do not edit
them by hand. To change an exhibit, edit `tools/exhibits.json` and run, from
the repository root:

    python3 tools/build_synopsis.py            # rewrite content/synopsis.json and content/chapters.json
    python3 tools/build_synopsis.py --check    # also print each exhibit as text with its agreement marks
    python3 tools/build_synopsis.py --dump Matt 3:11-12   # numbered tokens of a passage, for writing blocks

The script needs only Python 3. It takes the Greek text and lemmas from the
MorphGNT files in `tools/data/`, aligns the parallel columns word by word, and
marks each word with the Gospels that share its exact form (`g`) and its
lemma (`gl`). How it aligns and counts is described at the top of the script
and summarised on the page under "How counted". An exhibit may set
`"aligned": true` or `false` to force or prevent verse-by-verse rows; by
default rows are aligned only when the columns have the same number of verses
and most rows share wording.

## Running locally

No build step. Serve the folder with any static server, for example:

    python3 -m http.server 8000

then open http://localhost:8000. (Opening `index.html` directly from disk
will not work, because the page fetches the files in `content/`.)

## Credits and licences

- Greek text: *The Greek New Testament: SBL Edition* (SBLGNT), © 2010 Society
  of Biblical Literature and Logos Bible Software, licensed
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Lemmas, normalised forms and parsing: [MorphGNT SBLGNT](https://github.com/morphgnt/sblgnt)
  (James K. Tauber and contributors), licensed
  [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/). The data
  files in `tools/data/` are unmodified copies; `content/synopsis.json`, which
  is derived from them, is shared under the same licence.
- English renderings of the Greek are working translations made for this page.
- Web font: Gentium Book Plus (SIL Open Font License), loaded from Google Fonts.
