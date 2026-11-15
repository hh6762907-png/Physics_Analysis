# Adversarial audit

**Purpose.** To attack this project as a hostile reviewer would, before anyone else does. Each
entry states the challenge, the evidence, what was done about it, and what risk remains. No
entry is resolved by assertion alone.

---

## A1. "Reproducing the official unit cells is circular." — **Serious**

*Challenge.* The exposure vector is raked to 16/17/18/12/7, so the check "it matches every
cell" is guaranteed by construction. Presenting it as validation is misleading.

*Response.* Accepted. The report now describes the check as consistency with a constraint, not
as empirical corroboration, and publishes the pre-raking deviations so the size of the
adjustment is visible (`unit_weightage_constraint_check.csv`: `reconciled_deviation`).

*Residual.* The chapter-level split inside each cell still rests on MTG and the sample paper.
There is no way to test it without CBSE chapter-level marks, which do not exist publicly.

## A2. "Hours dominate the answer, so this is a study-time ranking, not a marks ranking." — **Serious**

*Challenge.* Sensitivity variant `hours_hard_chapters_x1_35` moves Chapter 7 from 12 to 1.

*Response.* Accepted and stated in the report, the Markdown edition and the app's About page.
The incremental ROI is reported alongside exposure so a reader can see the two components.

*Residual.* Unresolved by design. Hours are the one input the application can eventually
replace with measured study time; until then, tier-level conclusions are the defensible ones.

## A3. "The evidence weights 0.40/0.35/0.25 are arbitrary." — **Moderate**

*Response.* They are conventions, disclosed as such, and varied in the sensitivity analysis
(`weights_mtg_heavy`, equal weights, SQP-heavy). Stream C is official but single-instance,
which is why it does not dominate.

*Residual.* No data-driven weighting is possible: there is no ground truth of chapter marks.

## A4. "Two of your three streams come from the same publisher and are correlated." — **Serious**

*Response.* Stated in the limitations: treating A and B as independent overstates the
independent information. The weights do not correct for it.

*Residual.* A correlation-aware weighting would need per-year per-set data, which the
photographs do not support.

## A5. "The choice parameter 0.157 is invented." — **Moderate**

*Response.* The share (22/70) is verified from the official paper. The 50% split is an
assumption, tested at 0 and 0.75 in sensitivity; the top tier is unaffected, mid-ranks move.

*Residual.* Heterogeneous student behaviour is not modelled.

## A6. "Deletion shares are guesses." — **Moderate**

*Response.* They are declared expert estimates, applied once, renormalised, and varied by
0.5×/1.5×. Their effect is reported (Unit IX −11.9%).

*Residual.* A better estimate would require knowing the deleted content's historical weight,
which the MTG pages do not break out at that granularity.

## A7. "The confidence score and grade thresholds are arbitrary numbers." — **Moderate**

*Response.* Disclosed in the methodology; the score is a summary of three declared components,
not a measurement. Ranks are not reordered by it — it is used for tie-breaking only.

*Residual.* Cosmetic authority risk: a 0–100 score looks more precise than it is. The report
prints the grade next to it and warns against reading it as probability of success.

## A8. "Monte Carlo with subjective distributions is theatre." — **Serious-ish**

*Challenge.* Assuming normal/triangular distributions the analyst chose is not evidence.

*Response.* The report calls them uncertainty statements and prints the assumptions. The
sensitivity analysis — which is distribution-free — carries the robustness argument; Monte
Carlo is supporting, not primary. Sum checks (P(top 3) = 3.0, P(top 5) = 5.0) verify arithmetic
only.

*Residual.* Readers who treat "86%" as a probability of a 2027 outcome will over-read it. The
report says explicitly that it is not a predictive accuracy score.

## A9. "One official paper is not evidence of a distribution." — **Serious**

*Response.* Stated. Stream C is capped at 25% and varied down to 0 in sensitivity.

*Residual.* The 2027 paper may differ from the 2026-27 sample paper.

## A10. "The app's 'adaptive' engine is marketing." — **Moderate**

*Response.* The algorithm is published, deterministic and tested; the coverage-first rule is
justified (a diagnostic that ignores 9 chapters cannot personalise); the bank is small and the
repeats are disclosed.

*Residual.* No student validation. The engine cannot be said to improve outcomes.

## A11. "Self-marked written answers corrupt the readiness estimate." — **Moderate**

*Response.* Self-marking is explicit, requires an action per question, and is excluded from
objective readiness weighting except as a binary correct/incorrect at half marks. The
calibration table exposes systematic over-marking.

*Residual.* Dishonest marking produces flattering readiness. Nothing in the app can prevent it.

## A12. "Copyright: you reproduced the sample paper." — **Low**

*Response.* The attribution file records question number, section, marks and chapter — metadata,
not text. No question wording is stored. The app's 84 items are original and labelled.

*Residual.* The MTG-derived aggregates are facts about a commercial compilation; they are
summarised, not reproduced page by page.

## A13. "Your workbook may contain silent errors." — **Low (tested)**

*Response.* 736 formula cells, compiled and evaluated with `formulas` 1.3.4; nine live audit
checks return OK; the validator re-checks for unbalanced parentheses, unquoted sheet references,
and the presence of the required sheets. The workbook's computed baseline (40.90), target
(65.13) and ROI vector match the Python model to three decimals.

*Residual.* `formulas` is not Excel. A function behaving differently in Excel would not be
caught; only simple, universally supported functions are used for that reason.

## A14. "Reports can drift from the model." — **Low (tested)**

*Response.* All reports are generated from the CSVs; the validator asserts that every ROI value
appears in the Markdown, that counts match, and that the app's embedded ranking equals the CSV.

*Residual.* Narrative sentences not generated from data can still go stale; the numbers that
matter are generated.

## A15. "No real browser test was run, yet you ship a PWA." — **Moderate**

*Response.* Stated plainly in the architecture document and the verification report. What was
executed: 53 logic assertions, 30 jsdom DOM/behaviour assertions, `node --check` on all scripts,
static checks on the manifest, service-worker cache list, absence of external URLs, and build
hash equality. What was not: real rendering, service-worker installation, install prompts.

*Residual.* A layout or service-worker defect could survive. The app is a study tool, not a
system of record; data export is available.

## A16. "Why is Chapter 14 first? Semiconductors feel small." — **Checked**

*Challenge.* Intuition says a 7-mark unit should not top a marks-per-hour ranking.

*Response.* Unit IX carries 7 official marks and the chapter has low study cost; its marginal
return per hour is therefore high. The report shows exposure (6.17 marks) next to ROI so the
reader sees that it is a *marginal* result, not a claim that Chapter 14 is the most important
chapter. It is also the chapter where the deletion discount is largest (15%), which is
conservative rather than flattering.

---

## Summary of residual risk

| Risk | Severity after mitigation |
|---|---|
| Chapter split within official unit cells is unverifiable | High, irreducible |
| Hours dominate the ranking | High, disclosed |
| Correlated evidence streams | Moderate, disclosed |
| Single-instance official paper | Moderate, bounded by weights |
| App not validated on students or a real browser | Moderate, disclosed |
| Reports drifting from model | Low, tested |
| Workbook formula errors | Low, tested |

Nothing in this audit was resolved by deleting a criticism. Where a problem could not be
fixed, it is in the limitations document and, where it affects a conclusion, in the report
itself.
