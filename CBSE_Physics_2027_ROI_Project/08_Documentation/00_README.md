# Documentation set — CBSE Physics 2027 ROI project

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
