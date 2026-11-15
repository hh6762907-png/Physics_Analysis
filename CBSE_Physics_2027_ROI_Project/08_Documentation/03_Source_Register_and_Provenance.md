# Source register and provenance

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
