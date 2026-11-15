# Evidence audit

## What was checked, and how

| Evidence | Check performed | Result |
|---|---|---|
| Supplied syllabus PDF | SHA-256 recorded before work; text extracted with two independent libraries (pypdf, PyMuPDF); page 12 table read from table geometry, not from flattened text | Unit cells 16/17/18/12/7 recovered from merged cells; chapter list 1–14 confirmed |
| Supplied syllabus vs official URL | The official 2026-27 PDF was fetched and compared: filename, course-structure page and all fourteen chapter texts | Match. The supplied file is the current syllabus, not an older edition |
| Session labelling | The PDF carries a stale "2025-26" string on an introductory page alongside a 2026-27 footer and a `CLASS XII (2026-27)` course-structure heading | Treated as a CBSE typographical leftover; course-structure page is definitive; disclosed in the report |
| Official sample paper | Full text fetched; 33 questions counted; marks totalled; optional slots identified question by question | 16×1 + 5×2 + 7×3 + 2×4 + 3×5 = 70; 22/70 marks in optional slots; 19/22 choice pairs same-chapter |
| 15 MTG photographs | Individual register, rotation, crop, visual read, OCR cross-check (rejected), page-total reconciliation | 15/15 accounted for; all 154 year×chapter counts extracted; totals reconcile |
| MTG aggregate | Sum of yearly counts vs printed 10-year aggregate | Consistent to the precision printed |
| Third-party secondary sources | Encountered during search; excluded unless traceable to CBSE or to the photographed pages | None used |

## Evidence classes kept separate

1. **Official** — syllabus structure, unit cells, sample paper. May constrain the model.
2. **Secondary observation** — MTG counts and marks. Enter with source quality 0.75.
3. **Expert judgement** — hours, difficulty, readiness, deletion shares. Declared, never
   presented as data.
4. **Author's own content** — the 84 app questions, labelled ORIGINAL in every record.

## Gaps recorded rather than filled

* No board question paper: no question-level database, no set-duplicate check.
* No compartment/supplementary papers.
* No earlier MTG edition: no assessment of the publisher's predictive accuracy, and none is
  claimed anywhere in the deliverables.
