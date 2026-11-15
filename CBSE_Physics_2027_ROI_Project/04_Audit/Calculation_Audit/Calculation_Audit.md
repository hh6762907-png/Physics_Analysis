# Calculation audit

## Invariants asserted on the delivered CSVs

| Invariant | Where checked | Result |
|---|---|---|
| 14 chapters, ranks exactly 1–14 once each | `06_validate_outputs.py` group B | pass |
| Reconciled exposure sums to 70.000000 | group B | pass |
| baseline + additional = target, every chapter | group B | pass |
| incremental ROI = additional marks / additional hours (within 0.006) | group B | pass |
| ROI is monotone non-increasing with rank | group B | pass |
| Monte Carlo P(top 3) sums to 3.0 and P(top 5) to 5.0 | group B | pass |
| rank p05 ≤ median ≤ p95 and ROI p05 ≤ median ≤ p95 | group B | pass |
| 31 scenario rankings × 14 chapters = 434 rows | group B | pass |
| 16 sensitivity variants × 14 = 224 rows | group B | pass |
| Official unit cells reconstruct 16/17/18/12/7 | group C | pass |
| Deletion-adjusted vector still totals 70 | group C | pass |
| Model re-run reproduces every CSV byte-for-byte | group B | pass |

## Cross-implementation check (Python model vs spreadsheet)

The workbook recomputes the model from formulas rather than storing values. Every formula was
compiled and evaluated with `formulas` 1.3.4. The spreadsheet reproduces:

| Quantity | Python model | Workbook (recalculated) |
|---|---|---|
| Reconstructed baseline | 40.90 / 70 | 40.90 / 70 |
| Target after strong board readiness | 65.13 / 70 | 65.13 / 70 |
| Additional marks | 24.23 | 24.23 |
| Total study hours | 182 | 182 |
| Top-three ROI | 0.4805, 0.4045, 0.3648 | 0.481, 0.404, 0.365 |
| Chapter 14 confidence score | 73.2 | 73.2 |

Agreement at rounding precision across the two independent implementations is the strongest
available evidence that the arithmetic is right.

## Errors found and fixed during the build (recorded, not hidden)

| Defect | Effect if unfixed | Fix |
|---|---|---|
| Workbook formula used the raw choice boost (0.5) instead of the effective coefficient (0.157) | ROI compressed, ranking order wrong in the workbook only | Ranking now references the computed coefficient cell |
| Confidence sheet indexed the deletion vector by rank position instead of chapter number | Confidence aligned to the wrong chapter | Index by chapter number |
| Sample-paper references in the reconciliation sheet were two rows off | SQP stream read zeros | Offsets derived from the actual table position |
| Raking used comma unions that `formulas` rejects | `#VALUE!` | Contiguous range sums |
| `robustness_summary` labelled scenario shares as probabilities | Two different quantities looked comparable and disagreed | Renamed, Monte Carlo probabilities added, wording corrected in PDF and Markdown |

## What remains unverified

* Excel's own recalculation (no LibreOffice/Excel available in the build environment; only
  `formulas` 1.3.4 was executed).
* Any claim about how the 2027 paper will actually distribute marks.
