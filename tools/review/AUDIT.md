# Technical audit of E1–E5

Date: 16 November 2026. Repository: `/Users/dimaip/.t3/projects/against-q`.

The arithmetic mostly survives. The strongest historical conclusions do not. E5's supposedly comparable sayings figures depend strongly on selecting different Markan material and compressing each comparison into different blocks. E4's ratio is calculated correctly but its proposed interpretation assumes an editorial policy that direct dependence does not entail. E3's descriptive accuracies reproduce, but its post hoc significance does not survive familywise correction.

Severity below applies to the specified claim, not automatically to the whole experiment: **FATAL** invalidates the advertised inference; **MATERIAL** changes a result, its uncertainty, or a consequential interpretation; **MINOR** is a reporting or robustness defect with limited effect here.

## Scope and independence

All new code, logs and results are in this audit directory. No experiment script was imported or executed. `recompute.py` independently loads the two JSON datasets, builds token/verse indices and all alignment edges, implements the supplied class definitions and woes supplement, and computes the requested figures. `check_e3.py` independently reconstructs classes, chunks, rendering and classifiers; it does not call the project functions. `check_e4_full.py` reads the literal passage-list definition using AST, then uses independent counting/alignment code. Original outputs were read for comparison. `input_hashes.json` records final-read SHA-256 hashes for the scoped inputs and both datasets. No repository edits, commits, pushes or subagents were used.

Artifacts:

- `recomputed.json`: headline counts, order sensitivities, baseline counts.
- `mustard.txt`: all three Greek texts, every matched token pair, and every Matthew token's cell.
- `diagnostics.json`: common-sample checks, filter changes, bootstrap checks, multiplicity corrections.
- `e3_checked.json`: all 66 observed fixed/weighted classifier accuracies and fold checks.
- `e4_full_checked.json`: 69 independently checked passage/variant cell records and 24 bootstrap intervals.
- `e1_full_checked.json`: E1's passage counts, sensitivity table and bootstrap gaps.
- `alignment_diagnostics.json`, `more_checks.json`, `output_checks.json`: supplementary checks.

## Independent recomputation

Percentages below use unrounded counts. All E1/S1 requested denominators reproduce exactly. E5's last public value has a rounding error.

| Quantity | Claimed | Independent result | Verdict |
|---|---:|---:|---|
| E1, Q sayings, Luke–Matthew | 41.1% of 3,145 | 1,294/3,145 = 41.1447% | Reproduced |
| E1, triple-tradition sayings, Luke–Matthew | 26.7% of 2,199 | 587/2,199 = 26.6940% | Reproduced |
| E1 difference | +14.5 points | +14.4507 points | Reproduced |
| E1 Q interval | 33.2–49.8% | 33.16–49.80% by verse-run resampling | Reproduced; interpretation qualified below |
| E1 triple interval | 20.3–33.9% | 20.27–33.91% | Reproduced |
| Luke 3:7–9 | 60/72 | 60/72 = 83.3333% | Reproduced |
| S1 eligible Mark words | 9,744 | 9,744 unique token IDs | Reproduced |
| S1 Matthew keeps | 35.4% | 3,450/9,744 = 35.4064% | Reproduced |
| S1 Luke keeps | 21.4% | 2,089/9,744 = 21.4388% | Reproduced |
| S1 both keep | 12.5% | 1,214/9,744 = 12.4590% | Reproduced |
| S1 product of marginal rates | 7.6% | 7.59072% | Reproduced; not a sufficient historical independence null |
| E4 pooled Markan words retained | 31.0% | 39/126 = 30.9524% | Reproduced |
| E4 pooled other words retained | 46.6% | 263/564 = 46.6312% | Reproduced |
| E4 pooled ratio | 0.66 | 0.6637696904 | Reproduced |
| E4 ratio interval | 0.44–1.03 | 0.4360861–1.0307826, seed 20261116 | Reproduced |
| E5 Luke–Mark, all | 0.90; 93 blocks | 0.8992519869; 93 | Reproduced |
| E5 Matthew–Mark, all | 0.85; 125 blocks | 0.8523870968; 125 | Reproduced |
| E5 double tradition, all | 0.54; 91 blocks | 0.5357753358; 91 | Reproduced |
| E5 Luke–Mark, sayings | 0.95; 22 blocks | 0.9480519481; 22 | Reproduced as implemented |
| E5 Matthew–Mark, sayings | 0.56; 34 blocks | 0.5614973262; 34 | Reproduced as implemented; stated filter gives a different answer |
| E5 double tradition, sayings | 0.45; 76 blocks | 0.4445614035; 76 | Raw result reproduced; round to **0.44**, not 0.45 |

### E4 six-passage cells

Here `a` = Matthew token matched to both Mark and Luke; `b` = matched to Mark only; `c` = matched to Luke only; `d` = matched to neither. These are alignment-defined categories, not independently demonstrated source assignments.

| Passage | a | b | c | d | a/(a+b) | c/(c+d) | Ratio | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| John, Matt 3:11–12 | 11 | 2 | 29 | 15 | 84.6% | 65.9% | 1.28 | All cells reproduce |
| Temptation, Matt 4:1–11 | 4 | 7 | 100 | 73 | 36.4% | 57.8% | 0.63 | All cells reproduce |
| Beelzebul, Matt 12:22–30 | 14 | 31 | 65 | 55 | 31.1% | 54.2% | 0.57 | All cells reproduce |
| Blasphemy, Matt 12:31–32 | 0 | 7 | 7 | 37 | 0.0% | 15.9% | 0.00 | All cells reproduce |
| Mustard, Matt 13:31–32 | 6 | 10 | 13 | 21 | 37.5% | 38.2% | 0.98 | All cells reproduce |
| Mission, Matt 10:1,7–16 | 4 | 30 | 49 | 100 | 11.8% | 32.9% | 0.36 | All cells reproduce |
| Pooled | **39** | **87** | **263** | **301** | **31.0%** | **46.6%** | **0.66** | Reproduced |

The Mark-only cells also reproduce: pooled `e=34`, `f=199`, yielding 14.5923%. All 23 passages, all three variants, and all 24 reported pooled bootstrap intervals reproduce independently. There are no repeated Matthew or Mark source tokens across the 23 passage specifications. Nine Luke tokens recur across passage specifications (Luke 11:16 in Beelzebul and Sign of Jonah); that is reuse of target material in the secondary analysis, not double-counting of the pooled Matthew denominator.

### E2/E3 recomputation beyond the requested headlines

All 14 E2 class-count records reproduce independently, including scripture removal. All 33 E3 fixed-run observed accuracies printed in the post hoc file, and all 33 weighted observed accuracies, reproduce exactly to numerical precision: **66/66**. This also reproduces the fixed confusion-based diagnosis, including the classifiers that predict only one class.

For the fixed E3 run, all **139 computable permutation p-values** agree with an independent recount of their saved null arrays, including the 100 negative-control splits and seven significant splits. This is an arithmetic check of saved null results, not a rerun of their fitted null classifiers. Post hoc p-values lie on the required `(b+1)/301` grid; their individual permutations are not saved and were not rerun here.

## Checked defects and exact fixes

1. **FATAL — E5 does not establish the claimed comparison of editorial habits.**

   **Claim:** `content/research.json`, E5 reading: “The plain measurement is still worth having, because it compares like with like.” E5 summary and `content/assessment.json` Direction then say double tradition is reordered about as much as Matthew reorders Mark's sayings and much more than Luke does. The same inference appears in the computed points of `content/arguments/D.json` and `I.json`.

   **Evidence:** The two Mark comparisons start with different surviving Mark verses, build blocks separately from each target's order, then filter those blocks by source-side speech. Of 177 Mark verses individually meeting 80% Jesus speech, 132 survive the Matthew mapping and 76 the Luke mapping; only 68 survive both. Numerous displaced sayings disappear from Luke's sample, including Mark 4:21, 4:24, 4:31–32, 9:42 and 10:31. The Luke mapping additionally discards targets classified as Q or Q+Mark overlap; the Matthew mapping has no corresponding exclusion. Thus alternate Lukan forms are actively removed from this Mark comparison.

   Keeping the same 68 source verses and giving each verse one unit yields **tau 0.920544 for Matthew and 0.935031 for Luke**, rather than 0.56 and 0.95. This changes both sample matching and unit granularity; it is a diagnostic, not a proposed final estimator. Separately, with each comparison's original eligible verses but no compression, sayings tau becomes **0.847675 on 132 units for Matthew and 0.936491 on 76 for Luke**. Keeping the common sayings sample but retaining target-specific gap-2 compression gives **0.866287 on 38 Matthew blocks versus 0.938462 on 40 Luke blocks**. These checks disentangle the two problems: sample selection matters and compression matters.

   The gap-2 rule on the original data produces Matthew sayings tau 0.6343 with gap 1 and 0.4954 with gap 3; Luke remains about 0.92–0.95. One block gets one vote regardless of whether it contains one verse or nine. Compression therefore changes pair weights in precisely the dimension being compared.

   **Fix:** Remove “compares like with like,” “of Matthew's kind,” and the directional use of this contrast from E5, D1, I2 and assessment until there is a matched source-unit comparison. Define common semantic/pericope units independently of observed order, compare the same retained units where possible, report omissions separately, and show sensitivity to unit construction. Retain the current figures only as descriptions of three differently selected and differently compressed datasets. The failed direction gate remains a failed gate.

2. **FATAL — E4's proposed discriminator assumes the answer about copying policy.**

   **Claim:** E4 method: “If Luke copied Matthew's text, he should have the Markan words at least as often as the others: a ratio of 1 or more.” Reading: “both figures should stand near 50%.” Assessment Direction treats the observed difference as evidence for Matthew as combiner.

   **Evidence:** Nothing in direct use entails equal token-retention probabilities for the two strata. An editor using Mark as narrative frame and Matthew for additional teaching can directly copy Matthew's additions more often than Matthew's already familiar Markan wording. Set the two retention probabilities to the observed 39/126 and 263/564: a direct-copying process then generates the very table said to count against it. No empirical or generative copying model in the scripts excludes that policy. Conversely, a common source can itself share wording with Mark. The statistic measures differential overlap, not source identity or direction.

   **Fix:** Keep the table and “inconclusive under the pre-stated rule.” Remove the unqualified predictions R≥1 and “both near 50%,” and stop treating R<1 as a calibrated direction test. To claim comparative evidential weight, specify and test copying/selection models for each historical account, including Luke's simultaneous use of Mark. Assessment must say that this is an editorial-policy question left open by the count. A soft judgement is possible, but the count does not supply the advertised discriminator.

3. **MATERIAL — E5 implements a different sayings threshold from the public description.**

   **Claim:** E5 results: “blocks at least 80% words of Jesus.”

   **Code:** `tools/research_order.py:63` averages verse-level proportions with equal verse weights, only on side A. It does not divide Jesus tokens by all tokens in the block, and it does not inspect the target block's speech percentage.

   **Evidence:** Mark 11:22–23 maps to Matt 21:21: unweighted average **66.67%**, actual token share **85%**. Mark 12:36–37 maps to Matt 22:44–45: unweighted **79.41%**, actual **84.09%**. Both blocks are incorrectly excluded under the stated word-level definition. Applying that definition gives **36 Matthew blocks and tau 0.5936508**, versus the published 34 and 0.5614973. Luke and DT counts remain 22 and 76 in this particular correction.

   **Fix:** Sum speech-token counts over the block and divide by total tokens. State explicitly whether speech qualification must hold on the source side, target side, or both; then rerun all intervals and propagated quotations. Alternatively, describe the existing estimator accurately, but do not call it 80% of words.

4. **MATERIAL — E5's small-sample percentile intervals have a concrete downward bias from duplicate draws.**

   **Code:** `tools/research_order.py:70–85` uses tau-a, keeps all sampled pairs in the denominator, and assigns zero to pairs that are copies of the same original block. A bootstrap sample therefore creates “ties” absent from the original data. For a U-statistic of this form, its empirical bootstrap expectation is `(n−1)/n` times the original statistic.

   **Evidence:** Luke–Mark sayings have **zero genuine tied pairs**, 225 concordant and six discordant pairs. Original tau is 0.94805, but the mean of the published bootstrap is **0.90558**. The stated CI is **0.80087–0.96104**. Using exactly the same draws but excluding pairs of duplicate original identities from the denominator gives **0.84475–1.00000**. For Matthew it changes 0.28516–0.76832 to **0.29433–0.79489**. This diagnostic does not solve dependence between adjacent blocks; it demonstrates the duplicate-pair effect.

   **Fix:** Use and validate an interval method appropriate to Kendall/U statistics and the chosen cluster units; distinguish genuine positional ties from resampled copies. Publish the convention and a small-n calibration. Do not attribute the uncertainty merely to “many tied pairs”: the sayings datasets have respectively one, zero and zero genuine ties.

5. **MATERIAL — E1's intervals are composition sensitivity under an untested cluster assumption, not established historical uncertainty.**

   **Claim:** The E1 reading says the gap “could be as small as 3.9 points or as large as 24.9.”

   **Evidence:** The code resamples **50 Q runs and 50 triple runs** independently, with runs split at chapter boundaries, speech-threshold failures and class changes. An extended discourse can supply multiple resampling units. For example, the Q woes in Aland 194 occupy multiple runs; the Pounds in Aland 266 and the eschatological material in Aland 235/296 also span multiple runs. These are not demonstrably independent passages. The bootstrap holds text, annotations, alignment, class definitions and the selected Q list fixed. Its “share ≤0” is not a permutation p-value.

   An independent, deliberately coarser chapter-cluster sensitivity, resampling 13 Q and 15 triple chapter units, yields an interval around **+0.61 to +27.40 points** (4,000 draws, seed 1), compared with +3.9 to +24.9. Chapters are not claimed to be the correct historical units; the result demonstrates the dependence on clustering. The already published no-Q-list sensitivity crosses zero too.

   **Fix:** Call these conditional resampling/composition intervals. Use predeclared discourse or pericope clusters, including a treatment of overlapping Aland presentations, and report cluster sensitivity. Avoid reading the endpoints as calibrated bounds on a historical effect. Existing limits concede text, Q-list and threshold sensitivity, but not the fragmented-cluster assumption.

6. **MATERIAL — E1/S1 do not establish historical dependence, and one E1 statement is mathematically too strong.**

   **Claims:** E1: “On the Two-Source hypothesis, both evangelists must have kept Q's wording more closely than they kept Mark's.” Assessment Contact: counts of editing Mark “point the same way” toward contact.

   **Evidence:** A proportion of Luke's words matching Matthew is not either evangelist's retention probability from Q. It depends on the lost source's length, additions, omissions, and which words each selects. The numerator and denominator do not identify two copying rates. Even an independent model can yield 41.1% agreement with Matthew's Q-retention fraction below his 55.4% Mark figure: a 1,000-word source, expected retention of 500 words by Matthew and 822 by Luke, and 1,000-word resulting texts has expected shared source overlap 411 words. Matthew's source-word fraction is then 50%, not above 55.4%.

   S1's 7.6% is the product of global marginal rates. Historical independence does not require identical selection probabilities for every Mark token. Shared preferences for indispensable names, plot details, formulas and grammatical constructions produce positively correlated retention even when the editors act independently conditional on word type. Splitting speech from narration does not remove variation within those strata. The public table note already concedes this; the assessment still assigns the pattern evidential direction without a conditioned null or likelihood comparison.

   **Fix:** Replace “both must” with a statement that a common-source account must explain the observed pairwise agreement. Keep S1 descriptive unless a conditioned retention model is tested. Do not present its product-of-marginals excess as an independent estimate of contact. The E1 point estimate remains valid for its stated sample.

7. **MATERIAL — E3's post hoc significance is unadjusted, and the multiplicity count is wrong.**

   **Claim:** E3 limits: “Thirty figures were computed.” Reading treats strict Q–M separation at p=.003 and .010 as an observed style signal.

   **Evidence:** `research_stylometry2_posthoc.py` runs **11 contrasts × 3 instruments = 33 tests**, not 30. The table displays ten contrasts and leaves out the Mark-by-Matthew contrast, whose three weighted accuracies are still exactly 50%. With all 33 as the family, the smallest possible reported p, 1/301, becomes **0.10963** under Bonferroni and Holm. **No test survives familywise 5% correction.** Even excluding the three gate tests leaves 30 substantive tests, so the minimum Bonferroni p is 0.09967.

   This does not mean all multiplicity procedures erase every exploratory signal: Benjamini–Hochberg across 33 leaves eight q-values below .05. In particular strict Q–M masked has q=.02193 and forms q=.04111. Those are exploratory FDR results, not confirmation of a source. The raw strict masked/form p-values have Holm-adjusted values **.10963 and .27907** respectively.

   **Fix:** State “33 tests computed, 30 shown” or show all 33. Report the chosen family and adjusted values, specify the error criterion, and mark the table as exploratory. Do not select a smaller family after inspecting the results. With only 300 permutations, the p-value resolution is itself too coarse for stringent 33-test familywise claims. The existing limits concede multiplicity but undercount it and do not show its consequence.

8. **MATERIAL — E3 prevents literal chunk leakage, but its “passage” groups are not independent pericopes.**

   **Evidence checked:** All chunks belonging to an original class-defined verse-run stay together in CV. Independent assertions found no shared token IDs or original run IDs between train and test. TF–IDF vocabulary selection, document-frequency filtering and IDF fitting happen on training data only. Deterministic token rendering uses no fitted test information. The permutation shuffles original run labels and rebuilds chunks, as the script says; it does not simply permute chunk labels.

   **Remaining defect:** `research_common.py:100` defines a passage as a consecutive run of verses **within one selected class**. A single discourse/pericope can be fragmented into different original runs, even different classes; holding out one run does not hold out the discourse. Multiple such fragments can occur in different CV folds, and independent permutation treats them as exchangeable units. The audit finds actual within-pericope CV splits, not merely a possibility. In strict Q-versus-M, fold 1 trains on Matt 24:41 while testing Matt 24:38–39, inside the same contiguous passage in Aland 235. Original runs remain separate, but the discourse is not held out. This is dependence/topic leakage at the pericope level, not same-token leakage; its numerical inflation of accuracy has not been estimated here. See `group_checks.json`.

   Chunk construction is also class-dependent: short, possibly distant passages merge with the next selected passage before n-grams are made. New sequence features cross artificial passage joins. Under cross-Gospel gate permutations the sorting key ignores book and builds artificial mixed-Gospel sequences: the first G2 label permutation at seed 20261116 produces 30 merged groups containing both Matthew and Luke passages. Rebuilding preprocessing within each permutation is better than fixing label-dependent chunks, but it does not turn these joins into authentic Greek sequences or pericopes.

   **Fix:** Define independent discourse/pericope group IDs before class assignment and use them for CV and permutation, including all related fragments. Prevent n-grams across noncontiguous passage joins, or represent each fragment separately while aggregating predictions. Describe current units as verse-runs and merged groups. Re-evaluate gate and contrasts after that redesign. The current reading acknowledges form/topic confounding but not these group boundaries.

9. **MATERIAL — E4's aligner and the public “identical word” definitions are not equivalent.**

   **Claim:** E4 method: “words match when their forms are identical, longest common runs first”; table note defines Markan words as words identical in form with a word in Mark's parallel. E1 method says “letter for letter” and “at the same place.”

   **Evidence:** After greedy runs of length ≥2, the aligner accepts isolated matches only when the left token is not in a narrow grammar class, its normalized form has at least four letters, and exactly one free right counterpart exists. It can reject an identical word solely for being a short/function word, and accepts some repeated copulas in unrelated clauses. Normalization also removes punctuation, case and accents. These are aligner choices, not mere identical-form equality. See the manual mustard audit below.

   Direction matters. Reversing each alignment pair changes mustard cells from **(6,10,13,21)** to **(6,10,12,22)** and the ratio from **0.98077** to **1.0625**. The claim “five of six under 1” then becomes **four of six**. The pooled ratio remains essentially unchanged, **0.66353**, so this does not reverse the pooled conclusion. It does show that the six-passage sign count is partly a tie-breaking artifact.

   **Fix:** Publish the full matching rule and name the categories “matched by this aligner.” Validate disputed isolated matches against passage-local human alignments, and report orientation sensitivity. Use normalised-form terminology instead of “letter for letter” or “same place.” A wholly new matching rule requires new reported results, not relabelling the old counts as hand-verified textual correspondence.

10. **MATERIAL — E4's B1/B2 numbers reproduce, but they are selected baselines under another aligner.**

   **Evidence:** B1 selects Matthew verses with at least three raw-canvas Mark links, a Luke Aland parallel, and no linked Luke verse classified Q or Q+Mark overlap. It gives **352 verses**, cells **(1125,2086,223,2834)**, rates **35.0358% and 7.2947%**. B2 selects verses with at least two raw-canvas links to Luke Q and fewer than three Mark links. It gives **157 verses**, cells **(0,1,1520,1372)**; reported `rNOT` is **1520/2892 = 52.5588%**. It is technically not all Matthew words: one Mark-linked token is excluded from that denominator. All-token retention is **1520/2893 = 52.5406%**; both round to 52.6%.

   These baselines use raw canvas links, whereas E4's six primary passages use the new greedy pair aligner. The latter is documented as having 300 Matthew–Luke matches where the canvas has 250, with only 238 shared: 62 new and 12 missed. B2 also selects verses for containing positive Q matches, while B1 expressly excludes such matches. Their different “other-word” rates are therefore conditioned by selection; they are not matched reference distributions for historical copying policies. The raw baseline deliberately omits the supplemental woes edges.

   **Fix:** State B1/B2 selection and denominators. Harmonize alignment and selection scope before comparing rates; provide uncertainties or matched controls. Treat the existing rates as scale illustrations only. Remove the claim that these rates establish which author combined sources. In particular “31% against 35%” has not been tested for equivalence.

11. **MINOR — PARTNER discards valid alternative links and depends on JSON iteration order.**

   **Code:** `kloppenborg_test.py:51` overwrites `PARTNER[x][book]` on every link. It is inherited by E2/E3 Matthew Q classification and E5 verse mapping.

   **Evidence:** There are **32 token-to-Matthew entries, 16 token-to-Luke entries and six token-to-Mark entries** with multiple actual partners in the independent union graph. Retaining the first rather than last partner changes the all-material Mark–Matthew result from **125 blocks, .8523871**, to **128 blocks, .8491634**. The six requested sayings/all headline results otherwise keep their rounded values in this first-versus-last check. This is not a demonstrated large numerical failure of these headlines.

   **Fix:** Retain partner sets and establish a deterministic, passage-local vote rule with unique source-token weighting. Publish a sensitivity for ambiguous links. Do not arbitrarily select a partner by serialization order. LINK's set union is fine for binary retention counts and avoids counting repeated Aland edges twice; the lossy PARTNER dictionary is a separate issue.

12. **MINOR — E5's block construction and statistic need the actual rules, not the simplified description.**

   **Evidence:** `research_order.py:48` applies the minimum to the **sum of votes across all target verses**, not the winning target. Luke 11:41 maps to Matt 23:34 on a 1–1 tie with Matt 23:36; a retained DT mapping may have only one word in its chosen target. Mark 13:10 maps to Matt 24:14 on two votes, with a third vote at Matt 10:18. Earlier target verse wins ties. Blocks allow a gap of two verse positions on either side, and allow repeated target verse positions; they are not strictly consecutive verses advancing on both sides. Blocks are positioned by their first mapped verse. The Mark–Luke Q exclusion and source-side speech qualification are not in the public unit definition.

   The statistic is **tau-a = (concordant−discordant)/all pairs**, not the share of same-order pairs. For DT sayings, same-order share is .7221053 while tau-a is .4445614. Tau zero means balanced concordance/discordance, not no same-order pairs.

   **Fix:** Give these rules explicitly, label tau-a, and explain zero as no net order association. If the intent is at least two/three words in the chosen target, change the test to the winning vote count and rerun. Separate selection from block construction in the public description. The actual block rule permits source steps of one or two verse positions and target steps of zero, one or two; a target need not advance, a verse may be skipped, and only the first mapped position represents the block. The two/three-word threshold is on votes over all candidate target verses, not necessarily on the winning verse. Luke 11:41 passes on two singleton votes to Matt 23:34 and 23:36, then maps to the former. These details should be stated rather than implying consecutive one-to-one verse runs.

13. **MINOR — The post hoc run changes Monte Carlo settings as well as class weights; “forms” are split by the tokenizer.**

   **Evidence:** For observed scores, the learners, folds, vectorizer settings, rendering and chunk preparation are unchanged; all 33 fixed scores reproduced through the independent post hoc reconstruction. The only learner change is `class_weight='balanced'`. But fixed nulls use **500 permutations, seed 20261116**; post hoc nulls use **300, seed 20268116**. Post hoc does not repeat the matched-size analysis or the controls. Thus “everything else as fixed” is true about the observed classifier comparison, not the entire experiment.

   Also, the forms instrument uses `(?u)\b\w+\b`; `V-AI V-PI` becomes `V, AI, V, PI`. The advertised 1–4 “tags” are 1–4 tokenizer pieces, not 1–4 original grammatical features. The fixed script discloses this, the public method does not.

   **Fix:** Say “same observed-score pipeline with class balancing; new 300-permutation null with the stated seed.” Qualify the forms description or preserve atomic tags in a new declared design. Do not describe a tokenizer change as part of the weights-only rerun.

14. **MINOR — E4's “content words only” sensitivity retains a set of function-word categories.**

   **Evidence:** The filter excludes only `T-, CONJ, PREP, PRT, P-, R-, D-`; among the primary Matthew tokens it still retains **15 ADV, four F, two INJ, two I and one X** tokens that E2/E3 themselves classify as function words. Alignment is done on full text before the source-token filter. The number .77 reproduces, but the label is broader than the operation.

   **Fix:** Name the actual filter or define one shared content/function classification and recompute. State that this variant filters counted source tokens after alignment, unlike the scripture-removal variant, which realigns filtered sequences.

15. **MINOR — Numeric transcription and supporting-output omissions.**

   The complete mismatch ledger below gives exact locations and corrections. These are small compared with the inference failures, but a reproducible publication should not double-round its headline statistic or claim an unarchived experiment is checkable from the supplied outputs.

16. **MINOR — PARTNER silently discards real alternative edges and changes block construction.**

   **Code/evidence:** `kloppenborg_test.py:45–51` overwrites the target token whenever another alignment link for the same Gospel is encountered. In the independently loaded graph there are six tokens with multiple Mark partners, 32 with multiple Matthew partners and 16 with multiple Luke partners (counts by target Gospel across the pack, after supplementation). Choosing the first rather than last partner changes Mark–Matthew from **125 blocks, tau .852387** to **128 blocks, tau .849163**. The reported sayings taus do not change in this tested first/last sensitivity. The graph also contains 2,726 directed token edges repeated in multiple alignment presentations; the headline rate counters correctly deduplicate those through sets rather than counting them repeatedly.

   **Fix:** Retain all partner edges and their parallel-group context. Use an explicit stable policy for verse mapping, counting a source token at most once per candidate verse, and report ambiguity sensitivity. Do not rely on JSON group iteration order. This is a verified robustness defect with a small observed headline impact, not an explanation for E1's reproduced rates.

## Numeric and claim-to-output ledger

This checks the empirical numbers in E1–E5 and every `basis: computed` point in C/S/M/I/D against the corresponding `.txt` files, with JSON used for unrounded values. References, dates, verse numbers, settings explicitly described as choices, and numbers attributed to outside published scholarship are not treated as this project's empirical results.

### Every located numerical mismatch or unsupported project figure

| Public file / location | Quoted text or value | Stored/recomputed value | Exact fix |
|---|---|---|---|
| `content/research.json`, E5 results[0], line 804 | “+0.009, +0.011 and +0.033” | .0084611317, .0104838710, .0327868852 | At three decimals: **+.008, +.010, +.033**; avoid intermediate rounding |
| `content/research.json`, E5 results[3], line 807 | “double tradition 0.45 on 76 blocks” | .4445614035 | **.44** at two decimals |
| `content/research.json`, E5 table row “Matthew and Luke, double tradition”, line 845 | “0.45” | .4445614035 | **.44** |
| `content/arguments/D.json`, D1 computed evidence, line 33 | “0.45 in sayings” | .4445614035 | **.44** |
| `content/arguments/I.json`, I2 computed evidence, line 151 | “at 0.45” | .4445614035 | **.44** |
| `content/research.json`, E3 limits[0], line 647 | “Thirty figures were computed” | 33 rows in post hoc `.txt`/`.json` | **33 computed; 30 displayed**, including an explicit account of the omitted row |
| `content/research.json`, E5 results[3] and table | “at least 80% words of Jesus”; “34”; “0.56” | Actual implemented unweighted filter: 34/.5614973; stated word-weighted filter: **36/.5936508** | Fix filter then publish **36/.59** and recomputed intervals, or accurately relabel the implemented filter |
| `content/research.json`, E2 reading[1], line 508 | “October 2026 … five kinds of classifier … 52.9% to 57.1%, against a pass mark of 65%” | These project-trial results are absent from all supplied experiment outputs; no October classifier source/output was found in the specified repo | Archive the source, settings, samples and output, or remove this empirical range. **No corrected value can be established here.** |

Other definitional mismatches are recorded in defects 9, 10, 12–14. They do not change the currently stored arithmetic. In particular the B2 all-token denominator correction still rounds to 52.6%.

### Values checked and found consistent

- **E1:** all five alignment checks; 540/1,325 and 193/723; the 3,145/2,199 word totals; 41.1/26.7; both individual intervals; gap +14.5 and +3.9–24.9; 27/15 strings, medians 35/30 and seven/one above 70%; all eight sensitivity-table rows and denominators; the seven-string removal 34.0% of 2,674 and gap +7.3; Aland-only 37.7% of 2,209 versus 31.3% of 3,643; all six speech/narration percentages; 32.8%, 55.4%, 48.3%; all S1 table counts and percentages. Minor-looking differences obtained by subtracting rounded percentages, such as 41.1−26.7=14.4 versus the printed 14.5, are **not errors**: unrounded arithmetic gives 14.4507.
- **E2:** 52 Matthew features; 5,000 permutations; 2/2 sparse control verses in v1; .053 and 57.5%; special groups 1,596/2,169 words and 16/29 runs; .5343→.53 and 53.1%; .9106→.91; post-stop .0002/87.6%, .0002/75.9%, .0048/67.5%; wider groups 3,797/3,117 words; 200 splits and 3.5%; all eight rows of the displayed class-count table. The unarchived October range is the exception above. E2's code genuinely exits before the ten planned comparisons when its gate fails; both saved runs stop there.
- **E3:** all 30 displayed weighted accuracies, chunk counts and p-values match the post hoc `.txt`; all fixed headline accuracies match; fixed gates 76.1/74.3/68.8; shuffled scores about 45–54%; seven of 100 negative splits; matched 11 chunks/side; differences +13.8,+9.4,−.7 and their stated broad ranges; all rounded prose ranges correspond to the outputs. The matched ranges are explicitly subsampling spreads, not confidence intervals. The 33-versus-30 count is the numerical exception. “Cannot tell apart,” “not at all,” and “difference is small” are stronger than these inconclusive tests establish; use “did not detect a difference in this run.”
- **E4:** every displayed primary row; pooled figures and all quoted interval pairs; 17 added sayings/23 total; five ratios below 1 in the specified orientation; 238/250 and 300/250 canvas-check figures; 35.0/7.3 and 52.6 baselines; 14.6% and 8.8–23.3 Mark-only overlap. All agree with stored outputs. The percentages do not by themselves establish direct use of Mark: identical formulaic words can agree without identifying their transmission path.
- **E5:** all six block counts, all six raw taus, all six intervals, failed gate, 500 simulations and .898/1/1 rounded as 90–100%. The correct rounding exceptions are above. DT direction really is absent (`part2: null`), and sensitivity analyses behind the failed gate were not run. The reported bootstrap convention, not arithmetic corruption, causes the interval concerns.
- **Computed argument points:** C3's 31/47, C9's entire E1 quotation, M1's E4 quotation, S1's 9,744/35/21/12.5/7.6 and strata figures, and S2's E2/E3 ranges agree with their `.txt` sources. D1 and I2 have the .45 rounding mismatch and the E5 comparability defect. No further empirical numeric mismatch was found in these computed points.
- **Assessment:** its 14-point, 33% and 41% E1 paraphrases and E4 “nearly a third” are compatible with outputs. Its odds are explicitly labelled judgements, not calculations. The approximate arithmetic is internally possible: dependence around .625 and conditional Luke→Matthew around .60 gives .375/.375/.25 across Farrer/Two-Source/Matthew-uses-Luke. The experiments do not estimate these probabilities. The material issue is the Direction/Contact evidential interpretation, not an arithmetical odds contradiction.

## Statistical assessment by experiment

| Experiment | Strongest objection to the inference | Consequence | Already conceded? |
|---|---|---|---|
| E1 | No identified common-source model links pairwise agreement to two individual retention rates; the historical independence benchmark is missing. Runs are not established independent discourse clusters. Removing the seven high-agreement runs is outcome-selected trimming, useful as a contribution analysis, not an independent confirmation. | Fatal to proving contact or “both must copy Q more closely”; weakens interval interpretation. Does not invalidate the descriptive 14.45-point gap. | Missing outside benchmark, alternative Q list, small sample, alignment and fragility are conceded. Cluster dependence and the “both must” error are not. |
| S1 within E1 | Product of marginal retention rates assumes homogeneous/unconditioned choices. Independence conditional on token characteristics can produce the observed positive aggregate association. | Fatal to using the 7.6% benchmark as a historical independence test. | The table note explicitly concedes shared editorial preferences. Assessment uses the count more strongly than that concession permits. |
| E2 | Failure to reject a difference between small M/L sets does not establish that source signals are absent or undetectable. Cross-author separation is not a validated necessary condition for every within-author source task. | Weakens broad statements about stylometry. Stopping under its declared gate is appropriate; the experiment supplies no result for or against Q. | Feature limitation, small/unequal passages, redesign and post-stop status are conceded. |
| E3 | Exploratory multiplicity, class/genre confounding, fragmented discourse groups, and small/unequal training sets prevent interpreting raw accuracy as a clean measure of source-style effect size. Different studies' accuracy percentages are not comparable effect sizes. | No confirmed Q/M style result under familywise testing; no demonstrated equivalence from nonsignificance. Descriptive accuracies remain reproducible. | Most topic/form/multiplicity/small-sample limitations are conceded. Exact multiplicity consequence and discourse grouping are not. |
| E4 | R is a valid descriptive retention-risk ratio, but R=1 is not an established prediction of direct use. Six purposively selected, heterogeneous passages are not a random sample of independently generated overlap passages. | Fatal to the proposed historical discriminator; bootstrap is a composition sensitivity, not a calibrated likelihood comparison. | Six-unit roughness, alignment and exact-form limits are conceded. The copying-policy premise and baseline-conditioning problem are not. |
| E5 | Different surviving source samples, explicit Lukan Q exclusion, and target-dependent compression confound the sayings contrast. A nondirectional order magnitude cannot recover the direction that the gated test failed to identify. | Fatal to “like with like” and its directional use in assessment. | Failed gate, 22/34/76 blocks and Luke's omissions are conceded. Their measured impact and the filter error are not. |

### E4 ratio and six-passage bootstrap

The pooled ratio is the ratio of two token-weighted retention rates. It is **not** a mean of six ratios and need not be; as a descriptive statistic it answers the stated aggregate question. The unweighted mean of passage ratios here is .63763, compared with pooled .66377. Neither is automatically the historical likelihood ratio between hypotheses. A passage-stratified analysis or predeclared common weighting would better separate within-passage contrast from changes in passage composition.

All 5,000 primary passage bootstrap draws are defined; no undefined-resample filtering changes this primary interval. Repeated words inside a passage are correctly kept clustered by passage. But n=6, purposive passage choice and the very unequal Markan denominators (7–45) leave little basis for claiming nominal 95% coverage over a historical population.

Enumerating **all 6^6 = 46,656** ordered resamples of these six passage records gives the exact empirical-bootstrap interval **.44203–1.04429**, and 3.2858% of resamples at or above one. The stored random approximation .43609–1.03078 is legitimate Monte Carlo variation and is not a bug. Neither interval meets the declared bar. Leave-one-out pooled point ratios range **.55064–.73776**; the point direction is not solely one passage. This robustness of the point is compatible with an inconclusive interval and does not validate the historical null.

E4's “Luke also has 14.6% … so in places he drew on Mark directly” also overstates what those cells establish. The mustard Mark–Luke-only matches include a reporting verb and the formula “of God”; exact-form presence is compatible with direct Mark use but does not independently identify a source. Replace “so” with “consistent with,” leaving the historical case for Mark use to the separate evidence.

The synthetic direction check in E5 likewise has limited reach: it reports the sign on a construction made to represent stable gathering into five discourses, not recovery of a significant interval or operating characteristics for real Gospel editing. Its success cannot rescue the failed real-world gate.

## Required changes before publication

1. **Withdraw or redesign E5's evidential use of the sayings contrast.** Fix speech weighting, use matched independent units, report omissions and recompute calibrated uncertainty. Correct the propagated .45 and gate rounding errors.
2. **Recast E4 as descriptive unless a copying-policy model is supplied.** Publish the actual matching rules, check isolated matches, harmonize baselines, and preserve the declared inconclusive decision in assessment as well as in the experiment.
3. **Make E3's exploratory status operational.** Show all 33 results, report multiplicity-adjusted values, preserve discourse groups, and replace nondetection/effect-size claims with statements justified by these small tests. Archive missing trial output if the October range stays.

## What could not be checked

- The alleged October experiment's 52.9–57.1% range, its five classifiers, and the assertion that October settings were copied unchanged: its source/output is absent from the supplied experiment set, and no `style.py` was found in the specified repo or the local Gospel project's file inventory.
- The chronology of preregistration, “before any count” or “run once” assertions. Code comments, reservation files and logs disclose intentions and execution notes but are not independent timestamped registrations. No standalone original E2 design/revision or executable v1 source was present beside the supplied outputs. I did not infer dishonesty from that absence.
- The accuracy of external published counts, source reconstructions, citations or earlier scholars' classifiers. This audit checks local computations, not the underlying scholarly literature or NA28 readings.
- A complete human gold-standard alignment. One short passage was inspected token by token; that does not validate all automatic or supplemental alignments.
- A fresh refit of every fixed/post hoc permuted classifier or every E2 Monte Carlo run. E3's 66 observed scores were independently refitted, fixed null p-value arithmetic was checked from saved arrays, E4's cells and intervals were fully recomputed, and E1's listed count/sensitivity results were independently recalculated. The saved post hoc null models/individual null accuracies are unavailable.
- Calibration of nominal confidence coverage or historical-model probabilities. No supplied generative model permits it. The audit makes no replacement numerical odds estimate.


## Appendix: mustard seed, inspected token by token

**Verdict:** the cells **a=6, b=10, c=13, d=21 are correct for this algorithm**. I do not certify them as the uniquely correct human alignment or as counts of all words identical in form. The three texts and every pair are printed below, so the distinction is checkable.

The six `a` tokens are Matthew's seed phrase and the four-token birds-of-heaven phrase. The ten `b` tokens are the comparative/superlative wording, the vegetables phrase, `καὶ γίνεται`, and the infinitive `κατασκηνοῦν`. The thirteen `c` tokens include the kingdom opening, the taking-man phrase, tree, the final branch phrase, and a dubious isolated copula.

Two checked issues are especially clear. Matthew token 7592 `ὥστε` has the identical form at Mark token 20669 but is not matched because isolated conjunctions are excluded. Matthew token 7578 `ἐστιν` belongs to “which is smaller,” yet is matched to Luke token 41004, the opening “is like a grain”; the Matthew copula corresponding to “becomes a tree” (7588) stays unmatched. This is the singleton rule choosing the first free left occurrence, not a semantic correspondence. Reversing the pair removes one Matthew–Luke copula match and changes c from 13 to 12. Changed inflections such as Mark/Matthew `κατασκηνοῦν` versus Luke `κατεσκήνωσεν` are correctly excluded under an exact-form rule.

Greek text is OpenGNT, CC BY-SA 4.0. [Read the passage with parallels](https://synoptic-canvas.vercel.app/?verse=mark-4-30).

```text
OpenGNT Greek text, CC BY-SA 4.0. [Synopsis](https://synoptic-canvas.vercel.app/?verse=mark-4-30)
('mark', 4, 30): Καὶ ἔλεγεν· Πῶς ὁμοιώσωμεν τὴν βασιλείαν τοῦ Θεοῦ ἢ ἐν τίνι αὐτὴν παραβολῇ θῶμεν;
('mark', 4, 31): ὡς κόκκῳ σινάπεως, ὃς ὅταν σπαρῇ ἐπὶ τῆς γῆς, μικρότερον ὂν πάντων τῶν σπερμάτων τῶν ἐπὶ τῆς γῆς,
('mark', 4, 32): καὶ ὅταν σπαρῇ, ἀναβαίνει καὶ γίνεται μεῖζον πάντων τῶν λαχάνων καὶ ποιεῖ κλάδους μεγάλους, ὥστε δύνασθαι ὑπὸ τὴν σκιὰν αὐτοῦ τὰ πετεινὰ τοῦ οὐρανοῦ κατασκηνοῦν.
('matthew', 13, 31): Ἄλλην παραβολὴν παρέθηκεν αὐτοῖς λέγων· Ὁμοία ἐστὶν ἡ βασιλεία τῶν οὐρανῶν κόκκῳ σινάπεως, ὃν λαβὼν ἄνθρωπος ἔσπειρεν ἐν τῷ ἀγρῷ αὐτοῦ·
('matthew', 13, 32): ὃ μικρότερον μέν ἐστιν πάντων τῶν σπερμάτων, ὅταν δὲ αὐξηθῇ μεῖζον τῶν λαχάνων ἐστὶν καὶ γίνεται δένδρον, ὥστε ἐλθεῖν τὰ πετεινὰ τοῦ οὐρανοῦ καὶ κατασκηνοῦν ἐν τοῖς κλάδοις αὐτοῦ.
('luke', 13, 18): Ἔλεγεν οὖν· Τίνι ὁμοία ἐστὶν ἡ βασιλεία τοῦ Θεοῦ καὶ τίνι ὁμοιώσω αὐτήν;
('luke', 13, 19): ὁμοία ἐστὶν κόκκῳ σινάπεως, ὃν λαβὼν ἄνθρωπος ἔβαλεν εἰς κῆπον ἑαυτοῦ, καὶ ηὔξησεν καὶ ἐγένετο εἰς δένδρον, καὶ τὰ πετεινὰ τοῦ οὐρανοῦ κατεσκήνωσεν ἐν τοῖς κλάδοις αὐτοῦ.

Matthew-Mark
7565 ('matthew', 13, 31) κόκκῳ = 20638 ('mark', 4, 31) κόκκῳ
7566 ('matthew', 13, 31) σινάπεως, = 20639 ('mark', 4, 31) σινάπεως,
7576 ('matthew', 13, 32) μικρότερον = 20646 ('mark', 4, 31) μικρότερον
7579 ('matthew', 13, 32) πάντων = 20648 ('mark', 4, 31) πάντων
7580 ('matthew', 13, 32) τῶν = 20649 ('mark', 4, 31) τῶν
7581 ('matthew', 13, 32) σπερμάτων, = 20650 ('mark', 4, 31) σπερμάτων
7585 ('matthew', 13, 32) μεῖζον = 20661 ('mark', 4, 32) μεῖζον
7586 ('matthew', 13, 32) τῶν = 20663 ('mark', 4, 32) τῶν
7587 ('matthew', 13, 32) λαχάνων = 20664 ('mark', 4, 32) λαχάνων
7589 ('matthew', 13, 32) καὶ = 20659 ('mark', 4, 32) καὶ
7590 ('matthew', 13, 32) γίνεται = 20660 ('mark', 4, 32) γίνεται
7594 ('matthew', 13, 32) τὰ = 20675 ('mark', 4, 32) τὰ
7595 ('matthew', 13, 32) πετεινὰ = 20676 ('mark', 4, 32) πετεινὰ
7596 ('matthew', 13, 32) τοῦ = 20677 ('mark', 4, 32) τοῦ
7597 ('matthew', 13, 32) οὐρανοῦ = 20678 ('mark', 4, 32) οὐρανοῦ
7599 ('matthew', 13, 32) κατασκηνοῦν = 20679 ('mark', 4, 32) κατασκηνοῦν.

Matthew-Luke
7559 ('matthew', 13, 31) Ὁμοία = 40993 ('luke', 13, 18) ὁμοία
7560 ('matthew', 13, 31) ἐστὶν = 40994 ('luke', 13, 18) ἐστὶν
7561 ('matthew', 13, 31) ἡ = 40995 ('luke', 13, 18) ἡ
7562 ('matthew', 13, 31) βασιλεία = 40996 ('luke', 13, 18) βασιλεία
7565 ('matthew', 13, 31) κόκκῳ = 41005 ('luke', 13, 19) κόκκῳ
7566 ('matthew', 13, 31) σινάπεως, = 41006 ('luke', 13, 19) σινάπεως,
7567 ('matthew', 13, 31) ὃν = 41007 ('luke', 13, 19) ὃν
7568 ('matthew', 13, 31) λαβὼν = 41008 ('luke', 13, 19) λαβὼν
7569 ('matthew', 13, 31) ἄνθρωπος = 41009 ('luke', 13, 19) ἄνθρωπος
7578 ('matthew', 13, 32) ἐστιν = 41004 ('luke', 13, 19) ἐστὶν
7591 ('matthew', 13, 32) δένδρον, = 41019 ('luke', 13, 19) δένδρον,
7594 ('matthew', 13, 32) τὰ = 41021 ('luke', 13, 19) τὰ
7595 ('matthew', 13, 32) πετεινὰ = 41022 ('luke', 13, 19) πετεινὰ
7596 ('matthew', 13, 32) τοῦ = 41023 ('luke', 13, 19) τοῦ
7597 ('matthew', 13, 32) οὐρανοῦ = 41024 ('luke', 13, 19) οὐρανοῦ
7600 ('matthew', 13, 32) ἐν = 41026 ('luke', 13, 19) ἐν
7601 ('matthew', 13, 32) τοῖς = 41027 ('luke', 13, 19) τοῖς
7602 ('matthew', 13, 32) κλάδοις = 41028 ('luke', 13, 19) κλάδοις
7603 ('matthew', 13, 32) αὐτοῦ. = 41029 ('luke', 13, 19) αὐτοῦ.

Mark-Luke
20624 ('mark', 4, 30) ἔλεγεν· = 40990 ('luke', 13, 18) Ἔλεγεν
20629 ('mark', 4, 30) τοῦ = 40997 ('luke', 13, 18) τοῦ
20630 ('mark', 4, 30) Θεοῦ = 40998 ('luke', 13, 18) Θεοῦ
20638 ('mark', 4, 31) κόκκῳ = 41005 ('luke', 13, 19) κόκκῳ
20639 ('mark', 4, 31) σινάπεως, = 41006 ('luke', 13, 19) σινάπεως,
20675 ('mark', 4, 32) τὰ = 41021 ('luke', 13, 19) τὰ
20676 ('mark', 4, 32) πετεινὰ = 41022 ('luke', 13, 19) πετεινὰ
20677 ('mark', 4, 32) τοῦ = 41023 ('luke', 13, 19) τοῦ
20678 ('mark', 4, 32) οὐρανοῦ = 41024 ('luke', 13, 19) οὐρανοῦ

Matthew token cells:
7554 Ἄλλην: d
7555 παραβολὴν: d
7556 παρέθηκεν: d
7557 αὐτοῖς: d
7558 λέγων·: d
7559 Ὁμοία: c
7560 ἐστὶν: c
7561 ἡ: c
7562 βασιλεία: c
7563 τῶν: d
7564 οὐρανῶν: d
7565 κόκκῳ: a
7566 σινάπεως,: a
7567 ὃν: c
7568 λαβὼν: c
7569 ἄνθρωπος: c
7570 ἔσπειρεν: d
7571 ἐν: d
7572 τῷ: d
7573 ἀγρῷ: d
7574 αὐτοῦ·: d
7575 ὃ: d
7576 μικρότερον: b
7577 μέν: d
7578 ἐστιν: c
7579 πάντων: b
7580 τῶν: b
7581 σπερμάτων,: b
7582 ὅταν: d
7583 δὲ: d
7584 αὐξηθῇ: d
7585 μεῖζον: b
7586 τῶν: b
7587 λαχάνων: b
7588 ἐστὶν: d
7589 καὶ: b
7590 γίνεται: b
7591 δένδρον,: c
7592 ὥστε: d
7593 ἐλθεῖν: d
7594 τὰ: a
7595 πετεινὰ: a
7596 τοῦ: a
7597 οὐρανοῦ: a
7598 καὶ: d
7599 κατασκηνοῦν: b
7600 ἐν: c
7601 τοῖς: c
7602 κλάδοις: c
7603 αὐτοῦ.: c
```
