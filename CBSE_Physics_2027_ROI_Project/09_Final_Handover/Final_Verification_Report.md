# Final verification report

**Project** CBSE Class XII Physics 2027 chapter-wise preparation-ROI research system · **Version** 1.0.0 · **Verified** 2026-11-15

## 1. Verification result

Validation suite: **102 checks, 102 passed, 0 blocking failures, 0 warnings**.

There are no blocking failures. Every check listed below was executed against the delivered files; nothing is reported as passing on the basis of expectation.

## 2. What was actually executed

| Evidence | Result |
|---|---|
| Validation suite (`06_validate_outputs.py`) | 99 checks: sums, ranks, monotonicity, ROI identity, Monte Carlo sums, byte-for-byte model reproduction, workbook formulas, PDF contents, cross-file consistency, chapter-level-only rule |
| Model reproducibility | Re-ran `03_roi_model.py`; every output CSV identical by SHA-256 |
| Workbook recalc | `formulas` 1.3.4 compiled and evaluated 736 formula cells; 9 live audit cells return OK; workbook baseline/target/ROI match the Python model |
| App logic tests | 53 assertions pass (`node tests/logic.test.js`) |
| App DOM/behaviour tests | 30 assertions pass in jsdom with a real IndexedDB |
| App static checks | manifest fields, precache list completeness, no external URLs, no localhost calls, build-hash equality, `node --check` on all scripts |
| Original inputs | 16 files present and byte-identical to their first registration |

## 3. What was NOT executed (and is therefore not claimed)

- No real browser: layout, service-worker installation and install prompts were not exercised. jsdom has no layout engine and no service-worker support.
- No Excel or LibreOffice recalculation: `formulas` 1.3.4 is the only workbook engine available here and it is stricter than Excel in some respects, looser in others.
- No student cohort: the adaptive engine, readiness estimator and calibration statistics have software tests but no pedagogical validation.
- No original CBSE board paper: the question-level historical database, set-duplicate check and compartment-paper evidence do not exist in this package.

## 4. Deliverables present

| Deliverable | Location |
|---|---|
| Full research report (PDF, 28 pp) | `01_Final_Reports/Physics_2027_Complete_Research_Report.pdf` |
| Concise chapter ranking (PDF) | `01_Final_Reports/Physics_2027_Concise_Chapter_Ranking.pdf` |
| Markdown research report | `01_Final_Reports/Physics_2027_Research_Report.md` |
| Figures (8 PNG) | `01_Final_Reports/figures/` |
| Analysis workbook (26 sheets, live formulas) | `02_Excel_Workbook/Physics_2027_ROI_Analysis.xlsx` |
| Research data, registers, model outputs | `03_Research_Data/` |
| Audit pack (evidence, calculation, adversarial, validation) | `04_Audit/` |
| Diagnostic PWA + question bank + tests | `05_Diagnostic_Application/` |
| Extraction, calculation, validation, handover scripts | `06_Scripts/` |
| Source archive and input hashes | `07_Source_Archive/` |
| Documentation set (10 documents) | `08_Documentation/` |
| Handover manifest, this report, ZIP | `09_Final_Handover/` |

## 5. Package contents

| Category | Files |
|---|---:|
| Application | 27 |
| Audit | 6 |
| Documentation | 10 |
| Report | 11 |
| Research data | 18 |
| Script | 13 |
| Source archive | 1 |
| Workbook | 1 |
| **Total** | **87** |

Every file's size and SHA-256 is listed in `Handover_Manifest.csv`. The ZIP excludes itself, build caches and the 16 supplied originals; the originals remain unmodified in the repository root and are verified by hash in every validation run.

## 6. Known defects and limitations (carried forward, not hidden)

1. **Chapter split inside official unit cells is inferred.** CBSE publishes unit totals only. The reconciled vector matches the official cells by construction (raking).
2. **Preparation hours are expert estimates.** They are the dominant uncertainty; changing them moves mid-table ranks substantially while the top tier holds.
3. **Two of three evidence streams share a publisher** and are therefore correlated; the weighting does not correct for this.
4. **Single official sample paper** carries 25% weight.
5. **No browser execution** of the PWA (see §3).
6. **84-item question bank** repeats after a few sessions.
7. **No predictive accuracy is claimed for MTG**; the term 'prediction' is not used for historical observations anywhere in the deliverables.

## 7. Standing statement

This package is internally consistent, reproducible from its stated inputs, and explicit about its gaps. It does not claim that the ranking predicts the 2027 examination paper, and it does not claim completeness where evidence was unobtainable.
