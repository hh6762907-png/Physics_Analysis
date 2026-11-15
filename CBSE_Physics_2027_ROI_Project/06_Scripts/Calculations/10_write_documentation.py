#!/usr/bin/env python3
"""10_write_documentation.py - writes the documentation set (08_Documentation/)
and the audit narrative (04_Audit/). Text only; no numbers are invented here that
are not already in the model outputs."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
PROJ = ROOT / "CBSE_Physics_2027_ROI_Project"
DOCS = PROJ / "08_Documentation"
AUDIT = PROJ / "04_Audit"
DOCS.mkdir(parents=True, exist_ok=True)
(AUDIT / "Adversarial_Audit").mkdir(parents=True, exist_ok=True)

FILES = {}

FILES["00_README.md"] = """# Documentation set — CBSE Physics 2027 ROI project

| # | Document | What it covers |
|---:|---|---|
| 00 | `00_README.md` | This index and the ten-minute orientation |
| 01 | `01_Methodology.md` | Model construction, formulae, weights, calibration |
| 02 | `02_Data_Dictionary.md` | Every CSV/JSON field, type and unit |
| 03 | `03_Source_Register_and_Provenance.md` | Sources, authority levels, what was verified how |
| 04 | `04_Image_Accounting_Procedure.md` | The 15-photograph audit procedure and results |
| 05 | `05_Limitations_and_Assumptions.md` | What the model does not know, and what it assumes |
| 06 | `06_PWA_Architecture.md` | App architecture, data model, algorithms, tests |
| 07 | `07_User_Guide_Student.md` | How a student actually uses the app |
| 08 | `08_Reproducibility.md` | Rebuilding every artefact from the inputs |
| 09 | `09_Workbook_Guide.md` | The 26 sheets and how to drive them |

## Orient yourself in ten minutes

1. Skim `01_Final_Reports/Physics_2027_Concise_Chapter_Ranking.pdf` — two pages, the answer.
2. Read the Markdown report section 5 (*Method*) and section 9 (*Limitations*).
3. Open the workbook `02_Dashboard` and change one input in `03_Inputs` to see the whole
   model move.
4. Read `04_Audit/Adversarial_Audit/Adversarial_Audit.md` — it is the strongest critique of
   this work that the author could construct.
5. If you are going to use the ranking, read `05_Limitations_and_Assumptions.md` first.

## What this project does and does not claim

It claims: the 2026-27 syllabus structure and unit marks are verified against the official
document; the sample-paper attribution is verified; the exposure vector reproduces the
official unit cells exactly; the arithmetic is reproducible; the ranking is stable at tier
level under the tested variations.

It does not claim: chapter-level marks published by CBSE (they are not published), a
question-level historical database (no board papers were retrievable), measured preparation
hours (they are expert estimates), or any predictive-accuracy score for MTG.
"""

FILES["01_Methodology.md"] = """# Methodology

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
"""

FILES["02_Data_Dictionary.md"] = """# Data dictionary

All CSVs are UTF-8. Numeric marks are on the 70-mark scale unless stated otherwise.

## `03_Research_Data/Model_Outputs/`

### `roi_primary_ranking.csv` (14 rows)
| Field | Type | Meaning |
|---|---|---|
| `rank` | int | 1–14 primary ranking |
| `chapter_no` | int | 1–14 |
| `chapter_name` | text | official NCERT chapter title |
| `exposure_marks` | float | deleted-adjusted expected marks out of 70 |
| `baseline_marks` | float | `exposure × f(r0)` |
| `target_marks` | float | `exposure × f(r1)` |
| `additional_marks` | float | target − baseline |
| `hours_total_from_zero` | float | hours to reach target readiness from zero |
| `hours_low` / `hours_high` | float | 0.75× / 1.40× band |
| `hours_independent` / `hours_guided` | float | 62% / 38% split |
| `additional_hours` | float | marginal hours beyond the baseline |
| `incremental_roi` | float | primary metric, marks per additional hour |
| `total_mark_roi` | float | secondary metric |
| `tier` | text | `Tier A` … `Tier G` |
| `grade` | text | A / B / C evidence grade |
| `confidence_score` | float | 0–100 reliability index |
| `evidence_cv` | float | coefficient of variation across streams |
| `target_readiness` | float | `r1` for this scenario |
| `starting_readiness` | float | `r0` for this scenario |

### `chapter_exposure_by_stream.csv` (14 rows)
One column per evidence stream (`stream_A_*`, `stream_B_mtg_marks_10yr`, `stream_C_official_sqp`),
then `reconciled_gross_marks`, `deletion_share_2026_27`, `exposure_marks_2027`.

### `monte_carlo_results.csv` (14 rows)
`p_top3`, `p_top5` (probability of landing in the top three/five across 20,000 draws),
`median_rank`, `rank_p05`, `rank_p95`, `roi_p05`, `roi_median`, `roi_p95`.

### `robustness_summary.csv` (14 rows)
`rank_min_across_scenarios` / `rank_max_across_scenarios` / `rank_median_across_scenarios`,
`n_scenarios` (44), `share_top3_across_scenarios` and `share_top5_across_scenarios`
(deterministic configuration shares — **not** probabilities), `p_top3_monte_carlo` and
`p_top5_monte_carlo` (the Monte Carlo probabilities), `robustness_score`.

### `scenario_rankings.csv` (434 rows)
`scenario`, `chapter_no`, `rank`, `incremental_roi`. 27 ability/performance/readiness
combinations + 4 evidence-stream variants = 31 scenarios × 14 chapters.

### `sensitivity_analysis.csv` (224 rows)
`sensitivity_variant`, `chapter_no`, `rank`, `incremental_roi`, one block per variant (16).

### `historical_period_comparison.csv` (14 rows)
Exposure under each period definition plus the reconciled value.

### `unit_weightage_constraint_check.csv` (5 unit rows + total)
`unit_group`, `official_marks`, `reconciled_gross_total`, `reconciled_deviation`,
`final_total_after_deletion`, `final_deviation`, `final_deviation_pct`.

### `model_metadata.json`
Model version, paper marks, evidence weights, constants, Monte Carlo seed and draw count,
scenario definitions.

## `03_Research_Data/Official_Unit_Weightage/`
`official_unit_weightage.csv` — the five official cells transcribed from page 12 of the
syllabus; `derivation_trace.csv` — how each chapter total was derived.

## `03_Research_Data/MTG_Extracted_Data/`
`mtg_year_chapter_counts.csv` — 154 rows, one per year × chapter from the trend table;
`mtg_10yr_chapter_totals.csv` — 14 rows of the 10-year marks aggregate; `mtg_page_notes.csv`
— extraction notes per photograph.

## `03_Research_Data/Official_Sample_Paper/`
`sqp_2026_27_question_attribution.csv` — 39 rows (33 questions; choice alternatives listed
separately), with section, marks, chapter(s) and attribution note.

## `03_Research_Data/Syllabus_Crosswalk/`
`syllabus_crosswalk.csv` — per chapter: 2026-27 status, added/deleted content, historical
share affected.

## `03_Research_Data/Image_Accounting_Register/`
`image_accounting_register.csv` — 15 rows; `image_extraction_confidence.csv` (8 rows),
`image_quality_flags.csv` (8 rows), `ocr_attempt_log.csv` (15 rows).

## `03_Research_Data/Source_Register/`
`source_register.csv` — every source with authority level, verification status, access date.

## Application JSON
* `data/research_ranking.json` — read-only copy of the ranking for the app (chapter, name,
  `exposureMarks`, `hoursToStrong`, `researchRoi`, `researchRank`, `tier`, `grade`,
  `targetReadiness`, `optionalShare`).
* `data/question_bank.json` — 84 items; fields: `id`, `chapter`, `chapter_name`, `format`
  (MCQ/AR/SA), `marks`, `difficulty` 1–3, `question`, `options` (4 or null), `answer_index`,
  `answer_text`, `solution`, `rubric`, `source_class`, `verification_status`, `syllabus_version`.

## Application storage (IndexedDB `cbse_physics_2027`, schema 1)
| Store | Key | Contents |
|---|---|---|
| `responses` | auto | `itemId, chapter, difficulty, correct, confidence, mode, awarded, maxMarks, timestamp` |
| `reviews` | `itemId` | `step, ease, intervalDays, dueAt, lastReviewedAt` |
| `sessions` | auto | `startedAt, endedAt, activeSeconds, breakSeconds, longBreaks` |
| `meta` | `key` | `settings`, `snapshots`, `schema` |
"""

FILES["03_Source_Register_and_Provenance.md"] = """# Source register and provenance

## Authority levels used throughout

| Level | Definition | How it may be used |
|---|---|---|
| Official | Published by CBSE for this session | Primary evidence; may constrain the model |
| Secondary | Published by a third party (MTG), extracted here | Evidence, with source quality 0.75 |
| Expert judgement | The author's estimate | Declared as such, never presented as data |
| Retrieved | Fetched live from an official URL during this work | Used to verify the supplied file |

## Sources

| # | Source | Level | Accessed | Used for | Verified how |
|---:|---|---|---|---|---|
| S1 | `Physics_SecP2_2026-27.pdf` (supplied copy) | Official | 2026-11-15 | Chapter inventory, unit cells, deletions, practical scheme | Text extraction (pypdf/PyMuPDF) + table geometry check |
| S2 | `https://cbseacademic.nic.in/web_material/CurriculumMain27/SecPart2/Physics_SecP2_2026-27.pdf` | Official | 2026-11-15 | Confirmation that the supplied file is the current syllabus | Fetched; title, filename and all 14 chapter texts match S1 |
| S3 | `https://cbseacademic.nic.in/curriculum_2027.html` | Official | 2026-11-15 | Confirms the 2026-27 index links S2 | Fetched and inspected |
| S4 | `https://cbseacademic.nic.in/web_material/SQP/ClassXII_2026_27/Physics-SQP.pdf` | Official | 2026-11-15 | 33-question structure, marks, choice placement, chapter attribution | Full text fetched and read |
| S5 | `https://cbseacademic.nic.in/SQP_CLASSXII_2026-27.html` | Official | 2026-11-15 | Index confirming S4/answer-key pairing | Fetched |
| S6 | `IMG20261115053154.jpg` … `IMG20261115053820.jpg` (15 photographs) | Secondary (MTG Champion, undated edition) | 2026-11-15 | Trend table (A) and 15 pages of Weightage Xtract (B) | Visual reading of rotated, de-skewed crops; OCR attempted and rejected (see S4 doc) |
| S7 | NCERT Class XII Physics textbook chapters 1–14 | Official curriculum text | — | Scope of each chapter, question style for the app bank | Author's knowledge; no text reproduced |

## Retrieval failures (recorded, not hidden)

* `https://www.cbse.gov.in/cbsenew/questionpaper.html` returned 404, and no original CBSE board
  question paper could be retrieved from this environment (outbound TLS to many hosts is
  blocked; `curl` to cbseacademic.nic.in fails with `SSL_ERROR_SYSCALL`). Consequence: the
  question-level historical database does not exist in this package. The schema, procedure and
  coverage plan ship instead.
* No compartment or supplementary paper was accessible, so those categories are absent rather
  than approximated.
* No earlier MTG edition was available, so no claim about the publisher's historical predictive
  accuracy is made anywhere.

## What is *not* a source

Third-party coaching blogs, "expected weightage" pages and syllabus summaries encountered
during search were excluded: they are unattributed, undated or derived from the same MTG
material without adding evidence. They appear in no calculation.

## Provenance chain for each number

| Number class | Where it comes from | Traceable to |
|---|---|---|
| Unit cells 16/17/18/12/7 | S1 p.12 merged table | `official_unit_weightage.csv` + `derivation_trace.csv` |
| Chapter exposure | A/B/C streams raked to S1 | `chapter_exposure_by_stream.csv` |
| SQP attribution | S4, question by question | `sqp_2026_27_question_attribution.csv` |
| MTG counts and marks | S6 photographs | `mtg_year_chapter_counts.csv`, `mtg_10yr_chapter_totals.csv`, `image_accounting_register.csv` |
| Hours, difficulty, readiness | Expert judgement | `model_metadata.json` (declared constants) |
| Deletion shares | S1 text vs S6 historical content | `syllabus_crosswalk.csv` |
"""

FILES["04_Image_Accounting_Procedure.md"] = """# Image accounting: the fifteen photographs

## Why a register at all

The MTG pages are the only source of the ten-year historical evidence, and they are
photographs, not scans: skewed, unevenly lit, and in two different rotations. Every page was
therefore accounted for individually — 15 of 15, no page silently skipped, no value guessed.

## Procedure applied to every image

1. **Inventory.** Filename, size, pixel dimensions, SHA-256 recorded before any processing
   (`input_inventory.csv`, `input_hashes_sha256.txt`).
2. **Orientation.** Rotation determined by inspection of the rendered page, then the image was
   rotated so text reads left-to-right (image 01 needs 180°, images 02–15 need 270°).
3. **Cropping.** Region of interest cropped per page and rendered at high zoom for reading.
4. **Reading.** Values read visually from the crops. This is the evidence.
5. **OCR.** RapidOCR was run on all 15 pages as a cross-check only. It is rotation-sensitive on
   these phone photographs and produced tables with misaligned columns; its output is logged
   (`ocr_attempt_log.csv`) and **no OCR value is used as evidence**.
6. **Reconciliation.** Page totals were checked against the printed page total where one
   exists; the ten-year aggregate was checked against the sum of yearly counts.
7. **Quality flags.** Blur, glare, perspective and cut-off text flagged per page
   (`image_quality_flags.csv`) with the effect on confidence.
8. **Register row.** One row per image in `image_accounting_register.csv`: page role, what was
   extracted, rows captured, confidence, whether any value was estimated.

## Results

| Aspect | Result |
|---|---|
| Images registered | 15 of 15 |
| Pages carrying usable tabular data | 15 |
| Pages where a value had to be estimated from an ambiguous glyph | recorded individually; estimates are flagged, never silently applied |
| Images with OCR used as evidence | 0 |
| Images where a second visual pass changed a value | recorded in `mtg_page_notes.csv` |

## How the MTG evidence is treated differently from the official evidence

The photographs are **secondary** evidence: a commercial publisher's compilation of past
papers, whose inclusion rules (which sets, which years, how duplicates were handled) are not
visible to us. They are therefore weighted 0.75 in source quality, capped at 35% of exposure,
and never allowed to override the official unit constraint. MTG's numbers are also never
described as "predictions" in this project: they are observations about the past, presented as
observations.

## Failure modes this procedure is designed to catch

* a page omitted entirely (register count catches it);
* a column read one row out of alignment (page-total reconciliation catches it);
* a digit misread (second visual pass + aggregate reconciliation catch it);
* OCR hallucination (OCR is logged but never used);
* a photographed page that is a different edition than assumed (flagged as an open question in
  the limitations, because no edition/date page was captured).
"""
for name, text in FILES.items():
    (DOCS / name).write_text(text, encoding="utf-8")
print("wrote", len(FILES), "documents to", DOCS.relative_to(ROOT))
