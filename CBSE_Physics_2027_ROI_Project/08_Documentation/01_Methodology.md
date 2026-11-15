# Methodology

## 1. Question and scope

*For an intermediate CBSE Class XII Physics student preparing for the 2027 board
examination, which chapters give the greatest realistic increase in expected marks for each
additional hour of preparation?*

Scope is the 70-mark theory paper of Physics (042), session 2026-27, chapters 1–14. Analysis
is chapter-level only. The practical examination (30 marks) is out of scope and is not modelled.

## 2. Evidence streams

| Stream | Content | Authority | Weight |
|---|---|---|---|
| A | Chapter question counts per year 2017–2026, plus recency weighting | Secondary (MTG Champion trend table) | 0.40 |
| B | 10-year chapter marks aggregate, all sets | Secondary (MTG Weightage Xtract) | 0.35 |
| C | Official CBSE sample paper 2026-27, 33 questions attributed to chapters | Primary/official | 0.25 |
| Constraint | Official unit totals 16 / 17 / 18 / 12 / 7 | Primary/official | raking target |

Stream A is used in three forms: equal-weight last five years, equal-weight last ten years,
and an exponential recency weighting with a three-year half-life. The last ten years span
2017–2026; the 2022 session contributes its Term-I and Term-II papers as half-paper
instances; 2021 was not held as a board examination.

## 3. From evidence to exposure

1. Each stream is normalised to a 70-mark scale.
2. `E_raw = 0.40·A + 0.35·B + 0.25·C`, normalised again to 70.
3. **Raking**: within each official merged unit cell, `E_raked = E_raw × official_cell / Σ E_raw(cell)`.
   The reconciled vector therefore reproduces 16/17/18/12/7 exactly (verified in
   `unit_weightage_constraint_check.csv`, deviation 0.00% gross).
4. **Deletion adjustment** for content removed in 2026-27: `E = E_raked × (1 − d_c)`,
   renormalised to 70. This moves individual chapters but shifts the unit cells slightly;
   the deviations are published in the same file (largest: Unit IX, −11.9%, from the removal
   of Zener regulation and special-purpose diodes).

## 4. From exposure to marks

Internal choice matters: 22 of the 70 marks sit in optional slots (Section B 2 questions,
Section C 1, Section E 3). A student who has prepared *both* alternatives is not helped on
average; a student who has prepared one of two is helped by 50% of the gap. The model
therefore applies a choice-adjusted success probability:

```
f(r) = r + 0.50 × (22/70) × (1 − r)   =   r + 0.1571 × (1 − r)
```

where `r` is the probability of answering a prepared chapter's question correctly.
Then, per chapter:

```
baseline_marks = E × f(r0)          r0 = intermediate starting ability
target_marks   = E × f(r1)          r1 = strong board readiness
additional     = E × (f(r1) − f(r0))
```

Choice is applied once. It is not compounded with a separate "risk discount", because that
would double-count the same phenomenon.

## 5. Preparation hours and ROI

Hours are expert estimates of the time needed to reach strong board readiness from zero,
split 62% independent study and 38% guided instruction. The additional hours to move from
`r0` to `r1` scale with the fraction of the chapter's difficulty still unmet:

```
additional_hours = max(1.5, H × (r1 − r0)/r1)
```

Two ROI measures are reported and never mixed:

* **Incremental ROI (primary)** = additional marks ÷ additional hours beyond the baseline.
  A marginal quantity: where the next hour goes.
* **Total-mark ROI (secondary)** = target marks ÷ total hours from zero. An average quantity.

## 6. Scenarios

Three axes are kept separate rather than multiplied into one number:

* starting ability: weak / intermediate / strong (sets `r0` through a chapter difficulty index);
* performance: conservative / realistic / strong (scales the realised share of target marks);
* readiness: basic / strong board / high proficiency (sets `r1`).

That is 27 combinations for the primary evidence set, plus four evidence-stream variants
(historical only, MTG only, SQP only, reconciled). All 31 rankings are in
`scenario_rankings.csv`.

## 7. Uncertainty

* **Monte Carlo**, 20,000 draws, seed 20261115: exposure `N(E, 0.15E)` renormalised to 70,
  hours triangular (low, central, high), `r0` `N(profile, 0.06)`, `r1` `N(target, 0.03)`.
  Correlations are not imposed; the sampling is independent by design and this is disclosed.
* **Sensitivity**: 16 structural variants (weights, half-life, hours multipliers, choice
  slope, deletion scale, difficulty index ±20%).
* **Robustness**: rank range and top-3/top-5 shares across all 44 configurations.

The Monte Carlo distributions are subjective uncertainty statements. They are not fitted to
data and must not be read as sampling error.

## 8. Reliability scoring

`confidence = 100 × (0.45·consistency + 0.25·source_quality + 0.30·mapping_certainty)`

* consistency = `1 − min(1, CV/0.45)` where CV is the coefficient of variation of the three
  evidence streams (they agree → higher score);
* source quality: official 1.00, secondary 0.75, expert judgement 0.55;
* mapping certainty = `max(0, 1 − 2·deletion_share)`.

Grades: A ≥ 74, B ≥ 64, C below 64. Tiers group chapters whose ROI is within 10% of the tier
leader; tiers are ordered A (best) to G.

## 9. Ranking rules

Ties are broken by (1) additional marks, (2) evidence grade, (3) narrower ROI interval.
Adjacent ROI values within 5% are labelled near-ties. The report states explicitly that
tier membership is the defensible output, not exact rank.
