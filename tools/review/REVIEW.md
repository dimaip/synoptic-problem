# Referee report: E1–E5 and the assessment

16 November 2026. Review of the working-tree versions, not a published revision.

**Recommendation: retain the counts as exploratory descriptions; withdraw the claim that these experiments justify a revised ranking of the source hypotheses.** The largest problem is not small samples. It is that the quantities measured are not the quantities the conclusions require. E1 misdescribes its comparison population; E2 never reaches its question; E3 never validates its selection control; E4 substitutes a copying model for the Farrer hypothesis without defending that model; E5 fails its direction control and then recovers directional rhetoric through a descriptive comparison.

The specialist voices below are adversarial reconstructions, not quotations from, or claims to speak for, the named scholars. Attributions to published scholarship come exclusively from the site's argument files. Their `read`, `reported` and `abstract` qualifications remain in force. No independent bibliographic verification is claimed and no additional scholarly citations have been invented. FH = Luke used Matthew; MPH = Matthew used Luke; 2SH = independent use of Mark and Q. These abbreviations denote families whose auxiliary assumptions matter.

## What was inspected and checked

Read `content/research.json`, `content/assessment.json`, the claims and statuses across C, I, D, M, S, Q and P, relevant supporting exchanges, all experiment scripts, and the associated outputs. Small checks loaded the specified local Greek and parallel data. No commentary text was fetched. The repository was kept read-only; the checks and their output are `audit.py` and `audit.json` beside this report. Imports ran with bytecode writing disabled. The published experiment entry points were not rerun into their repository output paths.

Three checks matter substantially:

1. **E1's main triple-tradition comparison contains 45 of 125 verses with no aligned Markan word: 699 of 2,199 words.** Those verses contribute only 17 Matthew agreements. They include Luke 4:25–27 and 7:41–42, 45–47. The Nazareth synopsis groups Luke 4:16–30 with Matthew 13:53–58 and Mark 6:1–6a; the anointing synopsis groups Luke 7:36–50 with Matthew 26 and Mark 14. Sharing a synopsis group does not make every saying in its Lukan version a saying taken from Mark. The displayed strings Luke 4:23–27 and 7:45–47 consequently score zero while being labelled sayings both took from Mark.
2. **E5 excludes Q-classified counterparts only from its Mark–Luke block set.** Restore them, keeping the existing mapping, minimum of three links and gap of two, and sayings tau falls from **0.948 on 22 blocks to 0.770 on 32**; all-material tau falls from 0.899 to 0.848. This does not erase Luke's greater order agreement. It does materially weaken “almost without exception,” and makes the headline depend on excluding just the material at issue.
3. **E4's directional point estimate is not produced by a single freak passage.** Leaving out each primary passage in turn gives pooled ratios from 0.551 to 0.738, all below one. That preserves a descriptive tendency. It does not validate the expectation of one, establish provenance, or turn six selected passages into a random sample.

An intentionally crude E1 sensitivity restricts the triple-tradition comparison to verses with at least one Mark link: Matthew agreement rises from 26.7% to 38.0%; requiring three gives 41.1%, essentially the Q group's 41.1%. **These are not corrected estimates.** Selecting on retained Markan wording changes the estimand and favours closely copied verses. They show that the headline is highly sensitive to what counts as genuinely Markan material. A defensible repair requires independently delimited corresponding sayings, including genuine Markan sayings that Luke paraphrases completely.

## Part 1: the attack

### E1 — Verbal agreement, like for like

**Two-Source referee.** You have not controlled form by selecting verses mostly spoken by Jesus. A narrative parable, a brief proverb, an eschatological prediction and a scriptural quotation remain different kinds of material. More seriously, your “Markan sayings” population includes sayings absent from Mark. Your Q boundary comes from a saying-by-saying source reconstruction; your triple boundary admits whole Lukan expansions within broad Aland parallels. This is asymmetrical measurement. The seven highly agreeing passages are also not inconvenient contaminants: under a written-source theory they are precisely places where both editors may have preserved wording. Removing observations because they carry the effect is not an independent robustness test.

The formula multiplying marginal retention rates in the Mark table assumes equal or adequately modelled propensities to retain words. Independence of authors does not entail independent identically distributed decisions across tokens. Both can independently preserve the same essential expression. S1 itself records that caveat. Splitting Jesus/narrator is one useful stratification, not a solution to lexical and passage heterogeneity.

**Farrer referee.** Your underlying directionless result is unsurprising: agreement in double tradition can be high and very uneven. But do not advertise the best passages as the reason the argument is “fragile,” delete them, and treat an interval crossing zero as if the remaining effect had been disproved. The trimmed difference is still positive. A non-significant estimate is not an equivalence result. Conversely, the similar 32.8% Luke–Mark and 41.1% Luke–Matthew figures are not a fitted prediction of FH. They compare different texts with different denominators and editorial opportunities. FH gives Luke both sources, and permits him to use them differently. A numerical resemblance is not corroboration unless alternatives would have made it unlikely.

**MPH referee.** Agreement is symmetric; a denominator taken from Luke is not a temporal arrow. Your Matthew-side 48.3% has already been selected for identifiable Lukan counterparts. It cannot rescue direction. Matthew's abbreviation or expansion of Luke and Luke's expansion of Mark produce different denominators. None has been modelled.

**The reading overclaims in these sentences:**

> “Because sayings are compared with sayings, the difference is not just a matter of form.”

This controls speaker, incompletely controls broad genre, and does not control subgenre, quotation or source correspondence. The audited denominator defect precedes even those qualifications.

> “At most this shows contact, not its direction.”

If “contact” means direct Matthew–Luke dependence, this has not been shown. Shared written Q predicts verbal contact through a source. If “contact” means only some literary relationship, it is true but offers no leverage between the hypotheses.

> “On the Two-Source hypothesis, both evangelists must have kept Q's wording more closely than they kept Mark's.”

“Both” and “must” are indefensible. Q's wording, length and the two marginal retention rates are unobserved. One highly conservative user, heterogeneous copying, correlated choices of essential wording and different amounts of new material can change observed Matthew–Luke agreement. The two separate retention rates cannot be recovered from this agreement fraction.

**Alternative not adequately considered:** unequal amounts of Lukan-only expansion in the denominators, finer kinds of saying, and heterogeneous word preservation under genuinely independent editing. The first is demonstrated by the code check; the others remain live explanations.

**Novelty:** a useful local implementation of the comparison attributed to Kloppenborg, not a new discovery of high or variable double-tradition agreement. C9 and S2 already give that literature, including Bergemann's wide variation. No specialist should accept a claim of a new dependence result until the populations are repaired. Whether the exact implementation is first in the literature has not been independently checked.

### E2 — A test stopped at its own check

**Two-Source referee.** A method failing to distinguish Matthew's special sayings from Luke's special sayings does not show that a published source contrast lies “near the edge” of measurability. Author contrasts and source contrasts are different effects; Jesus' speech may preserve common tradition in both authors. Your own gate changes population, genre mixture, sample size and likely effect size at once. A p threshold is not a power calculation. You have shown only that this test did not detect this contrast at these sample sizes.

**Farrer referee.** The proposed selection control is not actually “what Luke took” versus “what Luke left.” It is what an exact-form aligner links versus does not link. Luke can retain a saying with different inflections or paraphrase it beyond the link threshold. Moreover, where Luke already has Mark, he need not select from Matthew as he would select Matthew's new material. That control does not transport automatically to the double tradition. Stopping is correct; the project should stop drawing implications too.

**MPH referee.** You specify a Luke-selecting-Matthew alternative and no reciprocal Matthew-selecting-Luke alternative. In a Matthew-third model the shared Markan material in Matthew may itself reflect selection or influence from Luke. Calling it “one source and one editor” does not make that influence disappear. This design cannot fairly rank three models.

**The reading:**

> “This experiment says nothing for or against Q.”

Correct. It should govern the rest of the discussion.

> “Results of that kind therefore sit near the edge of what texts this short can show, and the 2023 study's own figure for sayings (p = 0.05) is at that edge.”

The “therefore” fails. Different features, populations and validation procedures have different power. A p-value is not a distance from the limit of an instrument. The reported larger-sample success is a sample-dependent result, not evidence that the published source signal is nearly spurious. Likewise, “the evangelist's own hand is close to invisible” should remain explicitly restricted to this failed contrast and instrument.

**Alternative not adequately considered:** the special-sayings gate may contain less of the authors' distinguishing editorial behaviour than the putative source contrast, irrespective of whether Q exists. The wider gate's success can reflect additional editorial framing or different discourse types as well as more words; changing both cannot isolate sample size.

**Novelty:** an informative engineering failure of this implementation. No source-historical result, positive or negative. The stopping rule was honoured; do not mistake that procedural virtue for evidence against other instruments.

### E3 — Stronger classifiers, same unidentified comparison

**Two-Source referee.** You have not replicated Mealand by substituting different labels, features, chunk sizes and evaluation rules. “Well short of his four in five” is not a commensurable effect-size comparison. Your balanced repeat actually finds 65.2% and 62.3% discrimination for strict M with p = 0.003 and 0.010. That may reflect form, source or both. The experiment has not measured which. Widening M to zero-linked verses within shared pericopes changes what M means; it can dilute a real source contrast with unrecognised paraphrase, mixed-source verses and editorial connectors. It is not a clean robustness test of the same target.

**Farrer referee.** The gate shows that these classifiers can distinguish selected populations, not that they identify an author's compositional hand. The “masked” and “forms” instruments still see kinds of discourse through syntax, function words and grammatical sequences. They are not source-specific instruments. Worse, the decisive selection control has only 11 chunks on one side. Its failure to separate groups does not establish that selection is weak or that the observed Q/M contrast exceeds it. The design does not provide the counterfactual it promised.

**MPH referee.** A stylistic contrast inside Matthew fits Matthew retaining Luke in some passages and writing or taking other material elsewhere. It also fits Matthew absorbing his source's idiom into his own. C5, D4 and S2 already record that reversibility, including Poirier's vocabulary-adoption warning. There is no reciprocal, calibrated model here that justifies a direction preference.

**The reading overclaims:**

> “What can be said is that the difference between Q and special Matthew is small.”

What can be said is that these classifiers achieve these accuracies on these populations. Classification accuracy is not an intrinsic scale of source difference, especially across unequal sample sizes and different validation designs. The corpus is too small to certify a small upper bound.

> “So the stylometric case for Q in Matthew rests on a modest difference that form or selection could each account for, and the case in Luke was not reproduced.”

The second clause is acceptable as a result of this implementation. The first turns untested explanations into measured explanations and generalises from a local exploratory analysis to “the stylometric case.” Form is unmodelled; the selection control is explicitly unreadable. A plausible explanation has not thereby accounted quantitatively for the signal.

**Implementation and inference defects:**

- Repairing majority-class collapse with balanced training is sensible, and disclosed. The headline run is nevertheless exploratory. The repeat has **33** comparisons, not 30 (eleven contrasts × three instruments); some are controls, but the reporting family should be specified. The instruments are correlated, not three replications.
- The minimum repeat-run p is 1/301. Near 0.05 its Monte Carlo standard error is approximately 0.013. Rounded boundary values cannot bear fine interpretive distinctions. Repeated fold partitions and honest effect intervals are more valuable here than another isolated small p.
- Holding a whole constructed unit out prevents that unit's chunks leaking across train and test. It does not establish independence of different verse-runs from the same story, discourse or doublet. Permuting original run labels is appropriate only under the corresponding exchangeability assumption. Their being adjacent Greek passages is not a guarantee of exchangeability.
- “Where [Letters] finds a difference and the two style-only tools do not, the difference is one of content” in the limits is also too categorical. A significant/non-significant contrast is not itself a significant difference between instruments; feature sensitivity and power can differ.

**Alternative not adequately considered:** dilution from the wide-M definition and classification driven by intradiscourse grammar. Both can explain the change from strict to wide M without adjudicating source history. A single fold seed and few independent long passages add substantial instability.

**Novelty:** new exploratory numbers for this corpus and code. No replication or refutation of the cited studies; no established estimate of how much selection explains. Common expectations on every hypothesis—genre distinctions, source carryover, editorial assimilation—can produce the observed classifier behaviour. The exact accuracy pattern is not trivially guaranteed, but it is not a hypothesis likelihood either.

### E4 — Did Luke strip Mark's words out of Matthew?

**Two-Source referee.** You have converted an argument about recognisable phrases, settings and source combination into a census of identical tokens. A third of “Markan words” surviving says little about whether Luke retains the diagnostically Markan elements at issue: common connective or necessary wording may survive on every model. Q and Mark need not have been verbally disjoint. Calling Matthew's unmatched words “other” is appropriate; silently treating them as Q or as a second source is not. The six selected passages differ radically in scale, narrative/speech composition and extant Markan coverage. An interval over six units describes instability within that chosen list, not uncertainty over the source hypotheses.

A Two-Source advocate can accept the tendency and still reject your “both half right” settlement of M1. You have not audited the phrase-level claims in Andrejevs and Sloan's table reported there. Nor have you tested Olson's reverse objection: how exactly Matthew would have combined a Luke-like Q with Mark.

**Farrer referee.** Your null is invented:

> “If Luke copied Matthew's text, he should have the Markan words at least as often as the others: a ratio of 1 or more.”

Why? Luke has Mark as well as Matthew. Novel material, a fuller explanation or a more useful formulation can be attractive precisely because it differs from material he already knows. Selection can act on content, grammar and narrative function without identifying historical provenance token by token. M1's own rejoinder reports Poirier's answer that Luke preferred Matthew's improvements, and I2 gives Goodacre's different literary roles for the two sources. You cannot test the actual hypothesis by assuming those replies away. A pre-stated prediction is not necessarily a justified prediction.

**MPH referee.** A Matthew-third account fits mixing Mark and Luke, but the ratio does not show that Matthew mixed them. You never measure the topology of actual alternation between Mark-exclusive and Luke-exclusive phrases or test the competing Luke-third topology. E4 explicitly cannot distinguish MPH from 2SH. This is not a new positive MPH result just because its point estimate points away from an oversimplified FH.

**The reading overclaims:**

> “If Luke were simply copying Matthew's text at the rate he copies it in the double tradition, both figures should stand near 50%.”

“Simply” hides all the disputed assumptions: uniform copying rate, comparable opportunities, comparable text kinds and comparable alignment. Ordinary FH does not impose them. Calling the expectation “simple” does not make it neutral.

> “So the count leans against Luke's use of Matthew on this point without reaching the bar set for it.”

The problem is not principally that the interval reaches 1.03 rather than 0.99. Even an interval wholly below one would reject the specified retention model, not FH. Conversely, an interval crossing one is not proof of no tendency. The observed tendency is real in the selected sample and remains below one in every leave-one-out count; its historical meaning remains uncalibrated.

**Alternative the interpretation fails to test:** selective copying of Matthew's distinctive content alongside continued use or memory of Mark, without “unpicking” Markan tokens. It is mentioned as a specialist reply in M1 but never made an operational alternative here.

The 31% ≈ 35% and 47% ≈ 53% baseline resemblance is especially weak. Overlaps use the new greedy pairwise aligner; baselines use raw Canvas links. The ordinary-triple baseline excludes verses with linked Q-classified Lukan counterparts. The double-tradition baseline positively selects for shared Luke words. Those are unlike populations defined partly through the measured outcome. Their resemblance to overlap subgroups cannot demonstrate two-source switching. Three independent pairwise alignments also need not identify one transitive three-way word correspondence. The Canvas check's 238/250 recall conceals 62 extra edges among 300 proposed edges; these are disagreements with another algorithm, not proven errors or proven correct matches.

The temptation also exposes coarse counting: of eleven Matthew–Mark matched tokens, only one is speech-tagged; of 173 unmatched tokens, 74 are speech-tagged. Pooling narrative and quoted dialogue creates unequal opportunities before any source theory is invoked. Content-word and Scripture sensitivities help but do not match those opportunities.

**Novelty:** a reproducible token summary of an old disputed pattern. The mustard-seed equality is a useful constraint on an absolute token-avoidance formulation, already challenged by the retained Markan wording cited in M1/C3. No new demonstration of deliberate stripping, conflation direction or two separate sources in Luke.

### E5 — Order, with a failed direction gate

**Two-Source referee.** Relative order between Matthew and Luke is not distance from Q's order. Q is unobserved; neither or both users may have moved material. Saying the pair's tau resembles Matthew–Mark tau does not identify Matthew as the mover. You do not know the original sequence and cannot supply it by analogy. The count is also not fully like-for-like: speech is defined on the source side, thresholds differ, the Mark–Luke comparison removes Q counterparts and the three comparisons retain different sayings.

**Farrer referee.** You correctly say the direction measure failed. Then you use another number from the same exercise to do the work the validated measure could not do. A symmetric statistic cannot tell gathering from scattering. “Luke treats Mark as a narrative frame and Matthew as a supplementary teaching source” is not an emergency concession invented to save this result; it is already in I2/M1. Requantifying the order problem does not create a new independent problem. Your headline of near-perfect conservatism also excludes some of Luke's departures by classifying their counterparts as Q. I2's own evidence explicitly names Luke moving Mark's mustard seed. Restore the excluded counterparts and the observed sayings tau is 0.77, not 0.95.

**MPH referee.** I welcome a number for a familiar distinction, but it is not my directional argument. My argument concerns the feasibility and motivation of gathering, actual shared sequences and contextual seams; D1 records it. Matching a third, symmetric tau does not establish that Matthew gathered Luke. The simulation demonstrates recovery of its own five-bucket stable-sort mechanism, not recovery of ancient editorial direction.

**The reading:**

> “On direction this experiment says nothing.”

Correct as a statement about the failed test.

> “The plain measurement is still worth having, because it compares like with like.”

Worth having, yes; like-for-like, no. Blocks are made by merging forward runs **using the observed orders**, and their speech classification depends on the mean Jesus-share of verses on one side. Reordering, gaps, omissions and narrative adjacency therefore affect which observations survive and how many independent blocks they count as. This is a conditional summary of constructed units, not a common metric on an invariant sample.

> “That fits Matthew as the rearranger, which is the Two-Source view and equally the view that Matthew used Luke.”

It is compatible with that view. It is equally compatible with FH's source-role distinction unless comparative predictions establish otherwise. Compatibility is not directional evidence. Nor does 2SH require Matthew to have done all the rearranging.

**Alternative not operationalised:** different treatment of a narrative frame and a supplementary source. The write-up mentions it, but supplies no fitted benchmark or out-of-sample prediction against which to call it costly.

**Further technical issues:** the Luke–Mark point score is sensitive to eligibility as demonstrated above. The bootstrap samples already formed blocks and never re-estimates their construction, so its intervals omit mapping and segmentation uncertainty. Duplicated draws are ties with zero numerator but remain in the tau-a denominator: for fixed empirical blocks the bootstrap mean is mechanically attenuated by (n−1)/n. For the 22-block Luke–Mark sayings sample this makes its expected bootstrap centre about 0.905 for an observed 0.948. That does not invalidate every interval, but it demands calibration before using interval overlap as an equivalence claim. The broad intervals on 0.45 and 0.56 do not establish “about the same” without a prespecified equivalence margin. Sensitivities in the script sit behind the failed gate and are left null, although descriptive sensitivity analysis need not have been stopped with the direction test.

**Novelty:** new numbers for the familiar order problem, already set out in I2 and D1; I6/S1 also report Tripp's order study as significant but non-decisive. The asymmetry statistic is a new failed instrument. Retained relative sequence is expected on all three written-source models; the exact tau ranking requires editorial assumptions and is not guaranteed on each.

## The assessment: has it over-updated?

**Yes—its stated update is larger than the experiments warrant.** This is a judgement about the argumentative warrant in the present files, not a reconstruction of the author's previous numerical probabilities. There is no documented prior, likelihood model or accounting of correlated evidence from which to calculate an actual update.

### Verdict and odds

Markan priority is defended mainly by P2–P4 and survives these experiments. None of the new tests independently establishes Matthew–Luke dependence, chooses a direction, or excludes a written Q. A personal preference for contact can still be defended from C1–C6 and the published statistical literature; it must confront their counterarguments and cannot acquire experimental authority from E1–E5.

The odds are **arithmetically coherent**. For example, contact probability 0.63 and conditional Luke-used-Matthew probability 0.60 give 0.378 FH-family, 0.370 independent-family and 0.252 MPH-family. That captures the three verbal odds. There is no arithmetic scandal here. There is an evidential one: none of the experiments supplies either probability or their precision. “Judgements, not calculations” acknowledges subjectivity but does not explain why 3:2 rather than 1:1 or 2:1 is warranted.

The three-way partition also needs to be labelled as broad families, conditional on Markan priority. The verdict favours contact **plus other tradition**, while the odds call the categories three “separate accounts” and contrast them with the Two-Source hypothesis. Pure FH, contact plus a written common source, oral supplementation and earlier editions do not have the same predictions. Pooling them under “Luke's use of Matthew” then invoking the economy of pure FH gives an elastic target an undeserved advantage. Conversely, contact need not eliminate a Q-like shared source. C8's own status says economy is a last step, not evidence; the Contact step instead elevates “a lost document should be posited only when direct use has been excluded” into a premise. That is one side's methodological rule, not a result of the experiments.

### The Direction step

It is reasonable to keep direction open. It is not reasonable to write that the margin “has narrowed” on the experimental warrant offered. E4 and E5 are closely related to the pre-existing order/conflation debate in M1, I2 and D1, and share data, alignment, source boundaries and editorial assumptions. They are not two independent votes.

E4 records preferential agreement with non-Markan wording but does not justify its FH expectation. E5 records relative reordering but fails its direction control and filters the Luke–Mark comparison. The sentence “Both fit Matthew as the writer who combined and rearranged” upgrades compatibility to a historical diagnosis. Its placement in Direction makes it evidential despite the caveats in Research. A legitimate update would be: the site now has local measurements of two old observations, whose comparative explanatory force remains disputed. No experimental change in odds is warranted yet.

A Two-Source referee would additionally object that the Contact step counts difficulties for Q cumulatively while treating arguments for independence mainly as tastes about Luke. I1's narrowed omissions concern specific editorial interests; C6 explicitly records that the early Q narrative/Mark-reordering correlation is predicted on both hypotheses. A Farrer referee would object that E4/E5 merely restate known requirements of Luke-third under a uniform-editor straw man. An MPH referee would object that the remaining conditional 3:2 preference for Luke-third rests on C5's expressly reversible language and C4's contested seams, while D4/S1's published directional arguments get no explicit comparative weighting. None can extract a calibrated ranking from these counts.

### Inconsistencies and asymmetries with the argument sections

1. **Q's existence versus recoverability.** Q3 expressly says that unreliable reconstruction does not show that Q did not exist; its known-Mark comparison makes that point. The verdict's “a single lost document that can be recovered word by word probably never existed” bundles existence with a standard of recoverability. Literally it rejects their conjunction; rhetorically it reads as evidence against existence. The No recoverable Q step appropriately criticises precision, then slides to the identity of the lost source. Separate the two questions.
2. **Failed direction versus directional uptake.** E5 says it says nothing on direction; Direction cites it as leaning toward Matthew's combining and rearranging. D1 distinguishes the failed direction test from the descriptive count, but that distinction is not respected in the update.
3. **Luke's conservatism versus omitted counterinstances.** I2's pre-existing evidence gives Markan sayings Luke abbreviates and relocates, including the mustard seed. E5's near-perfect score omits Q-classified counterpart locations and is then restated in I2 and the assessment as Luke's general procedure. This is a qualification lost in transmission, not new evidence that answers those counterinstances.
4. **Possible confounding versus measured explanation.** E3 says its selection control cannot answer the question. S2's status says the difference is “of a size that form or Luke's selection could each produce.” Those magnitudes were not established. Its `contra` sentence that E2 could not distinguish Matthew's sayings from Luke's “at all” also erases the restricted failed gate and the successful wider post-hoc gate.
5. **A contested economy rule becomes an axiom.** C8 describes genuine disagreement about parsimony; Contact's third reason assumes direct use must be excluded before a common source may be inferred. This is not an experimental conclusion and stacks the comparison.
6. **A conditional direction becomes an unconditional consequence.** The closing says that without Q “Luke becomes Matthew's first interpreter.” On MPH the interpretive direction is reversed. The site's substantial probability for MPH makes the unconditional wording untenable. And “Whichever way the contact ran, Luke also had sayings ... not ... through Matthew” is substantive under FH but automatic under MPH; it cannot establish an additional common source on both.
7. **Multiple possible textual solutions are treated as an extra defect without comparison.** C1/C2 record Kloppenborg's explicit symmetry: anomalies do not collapse either hypothesis. The assessment repeatedly treats competing solutions to Matt 26:68 as uniquely damaging while allowing contact models multiple source, memory and redaction explanations. The single agreement may still carry weight; the diversity of defences does not itself supply a likelihood ratio.

The Q3 and C8 problems need conceptual revision. The E5 and S2 problems are direct failures to preserve the experiments' own limits in the assessment/argument summaries.

### The three sentences I would change first

**1. E1, reading[0]:**

> “Because sayings are compared with sayings, the difference is not just a matter of form.”

**Replace with:** “This whole-verse count differs between the two lists, but the Markan group includes Lukan additions and the kinds of saying are not matched, so the count does not isolate a difference in copying.”

This is the most urgent measurement correction: the label currently promises a control the code does not implement.

**2. Assessment, Direction:**

> “Both fit Matthew as the writer who combined and rearranged.”

**Replace with:** “E4 and E5 quantify familiar disputed patterns: E4 does not test a justified prediction of Luke's use of Matthew, and E5 supplies no validated result about direction.”

This removes the unsupported experimental update while leaving the published arguments for each direction available.

**3. Assessment, verdict:**

> “Matthew and Luke were probably not independent of each other, and a single lost document that can be recovered word by word probably never existed.”

**Replace with:** “I tentatively favour direct dependence between Matthew and Luke; that judgement neither excludes a shared written source nor establishes how much of one could be recovered.”

If the author prefers to retain numerical odds, label them explicitly as personal judgements over broad model families and state that E1–E5 do not calibrate them. The least misleading current choice is to omit their apparent precision.

## Part 2: cheap further work

Ranked by expected value. These are bounded specifications, not promises of decisive source identification. Every proposal uses only the listed data and is comfortably below an hour of compute. Manual judgements are stated separately. Predictions are conditional editorial predictions where necessary; none is misrepresented as a theorem of a whole hypothesis.

### 1. Apparatus-screened minor-agreement phrase audit

**Question:** Is there a residue of secure, distinctive shared innovation outside the disputed overlaps, rather than a large count of common tokens?

**Exact measurement:** Freeze exclusions for the 23 E4 passages and Scripture-tagged spans. In the remaining genuine triple-tradition episodes, enumerate unique maximal contiguous Matthew–Luke runs of at least two identical normalised forms. Require at least one shared lemma absent from the entire corresponding Markan episode; flag rather than accept cases supported only by an uncertain/competing alignment. Deduplicate repeated Aland presentations and doublets. Report counts by phrase length, lexical rarity in non-overlap speech/narrative and episode, with the actual phrases. For every candidate, inspect the local NA28 units and report a conservative count after excluding any phrase whose agreement depends on an apparatus-listed disputed unit. Freeze a top-ten list for manual contextual checking before making an inference. Do not invent a p-value from token independence.

**Predictions:** FH and MPH allow secure shared innovations through direct copying, without specifying direction. A restrictive 2SH with independent editing of a fixed Mark predicts no extra direct-transmission channel; a substantial residue of unusual phrases creates a burden for coincidence/common tradition or textual explanations. A flexible 2SH can still explain individual cases. Distinguishing these is the point of presenting secure phrases, not an automatic rejection count.

**Known-answer check:** Verify that long three-way Mark-derived phrases are not mislabelled as innovations; inspect the supplied mocking-question case as a pipeline check, never as an independent discovery. Use the printed apparatus, keeping explicit and inferred witnesses distinct.

**How it misleads:** absence from Mark is not proof of invention by Matthew or Luke; shared formulae, oral tradition and scribal harmonisation remain possible. NA28's selective apparatus is not an exhaustive manuscript collation. Compute takes minutes; checking the bounded list takes human reading.

### 2. Hide Mark: source-recovery calibration stratified within speech

**Question:** How much of an actual extant source can this corpus recover from its two users, and does sayings subgenre change the answer enough to matter for Q3?

**Exact measurement:** Without consulting Mark during extraction, take identical aligned Matthew–Luke runs of two or more tokens within frozen triple-tradition episodes as a deliberately minimal pseudo-source. Reveal Mark only for scoring. Measure source-token recall, precision against the corresponding Markan tokens, omitted episodes, and extra shared wording absent from Mark. Report all speech, narrative, short speech units below 40 words and longer speech units separately; exclude Scripture in a predeclared secondary run. Distinguish certain three-way token correspondences from alternative matching locations. This is a literal reconstruction baseline, not an attempted reproduction of the IQP's full critical method.

**Predictions:** All three Markan-priority hypotheses accept that Mark was a real source despite whatever recovery loss occurs. Poor recovery is therefore a known-answer counterexample to “unrecoverable, therefore nonexistent.” FH/MPH may additionally transmit innovations absent from Mark; 2SH can also generate shared innovations through independent editing or other tradition. This experiment calibrates the existence/reconstruction inference, not the three-way ranking.

**Known-answer check:** Mark itself provides the answer. Stratification directly addresses the sayings-versus-narrative objection to the Weaks analogy recorded in Q3.

**How it misleads:** an intersection baseline is intentionally conservative; its failure cannot estimate the performance of every reconstruction method. Markan narrative is not a substitute for Q; report the within-speech strata rather than extrapolate a single loss percentage. Computational work takes minutes.

### 3. Phrase-switch costs for the two extant-source directions

**Question:** Does one direction require substantially more fine-grained source switching in the passages used to argue about “unpicking”?

**Exact measurement:** Freeze E4's six primary passages and a same-sized set of ordinary triple-tradition controls before counting. For Luke-third, mark exact runs of at least three words available from Matthew, Mark, both or neither; repeat for Matthew-third using Luke and Mark. A dynamic program minimises source switches over admissible assignments, keeping common runs ambiguous and newly composed words neutral. Report switches per 100 copied words, median run length and the share of switches within a printed punctuation-delimited clause. Show every case contributing a within-clause switch. Repeat a predeclared two-word threshold sensitivity; never infer provenance from singleton connective words.

**Predictions:** The block-copying FH described in M1 predicts that Luke-third will not require exceptional fine-grained switching relative to its controls. MPH's simpler-conflation claim predicts a lower burden for Matthew-third. Under 2SH, Matthew's missing Q prevents an equivalent full cost from being observed: the Matthew-third result is a Luke-as-Q proxy and must be labelled as such, not evidence that Q had Luke's exact wording.

**Known-answer check:** Construct a few passages from the existing source tokens using known block joins and known short alternating runs; require the optimiser to recover their minimum costs, with unambiguous anchors separating source runs.

**How it misleads:** a low minimum is a feasibility bound, not a reconstruction of the author's actual process; paraphrase, memory and altered wording hide switches. A more flexible copying model will always look cheaper unless both directions have identical rules. This adds sequential structure that E4's bag of tokens does not measure; no hypothesis receives an invented Q text. Compute takes seconds or minutes.

### 4. A bounded, direction-blind fatigue audit

**Question:** Do the site's strongest fatigue examples survive one criterion applied in both directions, calibrated against Mark?

**Exact measurement:** Freeze the DT cases actually cited in C4/D4 and an equal number of P4 Markan controls. Before revealing the model labels, give each case a binary checklist: an initial source-detail change, a later retained detail, a demonstrable incompatibility introduced by the initial change, and an explanation that removes it without changing the proposed source. Score each directed reading separately. Publish the Greek evidence and disagreements; count only cases passing all three fatigue requirements. No automated search for ever more favourable cases.

**Predictions:** All three models predict Mark-to-user fatigue in the accepted P4 controls. The strong asymmetric FH claim predicts secure Matthew-to-Luke DT cases with no reciprocal residue. MPH predicts the reverse asymmetry, or that alleged Lukan fatigue is inherited and repaired by Matthew. 2SH allows either evangelist's fatigue against Q, so a seam alone does not discriminate it from direct dependence.

**Known-answer check:** P4 establishes the target behaviour under shared Markan priority; failure on those examples invalidates the audit instrument, not Markan priority.

**How it misleads:** fatigue judgements remain interpretive; shared-Q wording is unobserved. Blinding hides labels, not a knowledgeable reader's recognition of passages. Compute is negligible; the real cost is a bounded human close reading. Do not turn this into a whole-corpus fatigue hunt.

## Ranked improvements to the existing experiments

1. **Repair E1's source correspondence before adding statistics.** Freeze genuinely corresponding Markan sayings by clause or independently delimited unit; retain genuine paraphrases and omissions, exclude Lukan-only additions. Match short proverb/extended speech/narrative parable and Scripture status, and publish the inclusions. Do not adopt my link-threshold sensitivity as the answer: it selects on the outcome. Report both source-word retention and target-word agreement so that expansion cannot silently become rewriting.
2. **Replace E4's arbitrary null with matched editorial controls.** Use one aligner for overlaps and baselines; match speech/narrative, length and local Mark coverage. Define what a content-selecting FH would predict without conditioning the baseline on observed Matthew–Luke agreement. Report paired retention differences alongside ratios, all six cases and leave-one-out values; enumerate all 6^6 ordered passage resamples if an exact empirical bootstrap is desired. That removes Monte Carlo noise, not selection bias or the need for a justified model.
3. **Make E5 descriptive comparisons comparable.** Apply identical overlap policies to Mark–Matthew and Mark–Luke; report retained and relocated versions rather than silently deleting Q counterparts. Run gap/minimum-link sensitivities despite the failed direction gate. Use fixed independently specified pericopes as the primary units, show alternative mappings and handle bootstrap duplicate ties with a calibrated interval method. Test differences or equivalence margins directly; overlap of separate intervals establishes neither.
4. **Give E3 one properly powered, blocked primary endpoint.** Fix balanced training in advance, genuine episode/discourse holdouts, one style feature family and one definition of special material. Calibrate known Mark-source separation and artificial known-size perturbations at the same 11-chunk constraint. Report repeated-fold variability and a detectable-effect bound before interpreting a null. Keep the other results exploratory; more classifiers and more permutations do not create more independent Greek text.
5. **Replace E1/S1's product-of-global-rates null with conditional retention models.** Condition at least on passage, lemma/frequency, speech and grammatical role, with whole-phrase clustering. The simple audit's expected joint retention moves from 7.6% to 8.6% under lemma strata and 9.3% under verse strata, versus 12.5% observed. Those are separate crude stratifications, not a fitted combined model and not a disappearance of the residual. Use held-out passages to check calibration, then report residual dependence without equating it with direct use.

## Attractive rabbit holes

- **Reconstruct Q, then train a classifier to prove that Q has a distinct style:** circular labels plus an invented training text. Source reconstruction is the thing being tested.
- **Add neural embeddings, larger classifiers or dozens of feature menus:** the limiting resources are independent passages and a valid counterfactual, not computational sophistication. It multiplies researcher choices and can learn topics better than sources.
- **A full automatic fatigue census:** semantic inconsistency and literary repair need close reading. A token detector will mostly find changes of number, agent or setting that are perfectly coherent. Keep the bounded audit above.
- **Whole-apparatus dependency or stemma reconstruction:** the apparatus is selective, readings interact and harmonisation may postdate composition. Candidate-specific exclusion checks are cheap; reconstructing ancestral Gospel texts is a different research programme.
- **Recover a total ancient editorial cost from tau or scroll-travel distance:** no surviving writing-session trace calibrates that cost, and forward/reverse transformations can have the same permutation. A small optimiser can bound a specified procedure; it cannot turn that procedure into an ancient fact.
- **The missing ancient two-copyist benchmark:** potentially valuable, but Josephus, Plutarch and their sources are not supplied as structured texts in this data set. It does not meet this task's data-only constraint and should not be dressed up as a cheap local computation.

The valuable next work is sharper control of what was counted and a small number of auditable cases. The current experiments warrant methodological caution and better measurements; they do not warrant experimental odds on the Synoptic Problem.
