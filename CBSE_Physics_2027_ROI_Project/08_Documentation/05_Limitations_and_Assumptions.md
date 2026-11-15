# Limitations and assumptions

Everything in this document is a reason to trust the report *less* than a casual reading
suggests. It is deliberately complete.

## 1. What CBSE does not publish, and this project cannot invent

CBSE publishes **unit** marks (16/17/18/12/7) and question papers. It does **not** publish
chapter-level marks. Every chapter-level number in this project is therefore an estimate
constrained to sum to an official total. The unit cells are verified; the split *within* a
cell between its chapters is inferred.

## 2. The missing question-level database

No original board paper could be retrieved (see `03_Source_Register_and_Provenance.md`).
Consequences:

* no count of questions per chapter per set, only the publisher's annual counts;
* no duplicate detection across sets;
* no compartment or supplementary evidence at all;
* no verification of MTG's own inclusion rules.

The schema and extraction procedure ship in `03_Research_Data/` so the database can be added
later without changing the model.

## 3. Circularity in the constraint check

Because the reconciled vector is *raked* to the official unit cells, "it reproduces every cell
exactly" is true by construction, not an empirical finding. It is a statement that the model
is consistent with the official constraint, not that it is correct. The gross deviation
(before raking) is reported separately so the reader can see how far the raw evidence was
moved.

## 4. Expert judgement enters in four places

| Parameter | Value | Why it cannot be measured here |
|---|---|---|
| Hours to strong readiness per chapter | 6–19 h | No dataset of student study time exists; could be measured in the app |
| Chapter difficulty index (drives `r0`) | 0.35–0.72 | Requires item-level response data |
| Readiness targets (`r1`) | 0.45–0.95 by scenario | Definitional, but the values are chosen |
| Deletion shares | 0–15% | Weighs removed content against the historical evidence; no published weights |

Each is varied in the sensitivity analysis; the ranking's sensitivity to hours is the largest
single vulnerability and is stated in the report rather than buried.

## 5. Evidence asymmetries

* Stream C (the official sample paper) is a **single instance** carrying 25% weight. One paper
  is a weak estimate of a distribution, and its topic mix may reflect one setter's preferences.
* Stream A and B both come from the same publisher and are correlated. Treating them as
  independent evidence overstates the amount of independent information (the weights
  0.40/0.35/0.25 do not correct for this).
* The 2022 session was split into two terms with reduced syllabi; treating each as a half
  paper is a modelling choice, not a fact.

## 6. Internal choice is modelled, not observed

`f(r) = r + 0.157(1 − r)` assumes a student facing two alternatives has prepared exactly one of
them with probability 0.5 and gains 50% of the remaining gap. Reality is heterogeneous: some
students prepare both (no gain), some neither (no gain). The aggregate is plausible; the
per-student prediction is not.

## 7. Deletion adjustment renormalises

Removing content and rescaling to 70 implies that marks freed by deletion are redistributed to
the remaining content pro rata. CBSE could instead redistribute them to specific units. The
observable effect (Unit IX −11.9%) is published; the assumption is not hidden.

## 8. Thresholds are conventions

Tier boundaries (10% of tier leader), near-tie labelling (5%), grade cut-offs (74/64),
confidence weights (0.45/0.25/0.30) and the ROI-per-hour floor (1.5 h) are conventions chosen
for interpretability. Different conventions move individual ranks, not the top tier.

## 9. The application is not validated on students

The adaptive selector, readiness estimator, scheduler and calibration statistics are verified
by 53 logic assertions and 30 DOM/behaviour assertions. That is software correctness, not
pedagogical validity. No student cohort was available. The 84-item bank is small: after roughly
six sessions the app begins to repeat items, and its readiness estimates then depend on
recalled answers.

## 10. Copyright and reproduction

No CBSE question text and no MTG content is reproduced. The sample paper is used as *metadata*
(section, marks, chapter) and the answer attribution is a factual mapping. The app's questions
are original. If a future maintainer adds real past-paper text, they must clear rights first.

## 11. Scope exclusions

The 30-mark practical examination, the 2027 sample paper (not yet published), and any change
CBSE makes after 15 November 2026 are outside the model. If the syllabus changes, the
reconciliation must be recomputed from `official_unit_weightage.csv`.
