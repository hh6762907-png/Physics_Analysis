# Data dictionary

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
