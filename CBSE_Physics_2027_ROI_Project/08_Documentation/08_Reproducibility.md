# Reproducibility

## Environment

Python 3 with `pypdf`, `pymupdf`, `pdfplumber`, `openpyxl`, `reportlab`, `matplotlib`, `numpy`,
`pillow`; Node 22 for the app tests; `formulas` 1.3.4 for workbook recalc validation. The
project virtualenv used during the build is `.venv/` at the repository root (not shipped in the
handover ZIP).

## Rebuild everything, in order

```
cd CBSE_Physics_2027_ROI_Project
python 06_Scripts/Extraction/01_inventory_and_hashes.py      # inventory + SHA-256 of the originals
python 06_Scripts/Extraction/02_build_datasets.py            # eight evidence CSVs
python 06_Scripts/Calculations/03_roi_model.py               # model outputs + metadata
python 06_Scripts/Calculations/04_make_charts.py             # eight figures
python 06_Scripts/Calculations/05_build_pdf_report.py        # full + concise PDF
python 06_Scripts/Calculations/06_build_workbook.py          # 26-sheet workbook
python 06_Scripts/Calculations/07_build_markdown.py           # Markdown report
python 06_Scripts/Calculations/08_build_question_bank.py     # 84 items
python 06_Scripts/Calculations/09_build_pwa.py               # deployable PWA + hash manifest
python 06_Scripts/Calculations/10_write_documentation.py     # documentation set
python 06_Scripts/Calculations/11_write_audit_and_guides.py  # audit + remaining docs
python 06_Scripts/Validation/06_validate_outputs.py          # all checks
python 06_Scripts/Handover/build_handover.py                 # manifest, verification, ZIP
```

## Determinism

* The model uses a fixed Monte Carlo seed (20261115, 20,000 draws); re-running
  `03_roi_model.py` reproduces every CSV byte-for-byte, and the validator asserts this.
* Exam papers in the app are reproducible from an integer seed.
* Item selection is deterministic given the response history.
* The PDF and Markdown reports are generated from the CSVs, not typed by hand; the validator
  checks that the CSV values appear in the rendered documents.

Non-deterministic by nature: PDF byte layout (ReportLab version differences), image raster
rendering, and `formulas` recalc ordering. None of these affect numeric content.

## Verification entry points

| Question | Run |
|---|---|
| Are the supplied originals untouched? | `06_validate_outputs.py` group A |
| Does the model reproduce? | group B (`model re-run reproduces every CSV byte-for-byte`) |
| Do the unit cells hold? | group C |
| Is the question bank complete and labelled? | group D |
| Is the app self-contained and tested? | group E |
| Is the workbook formula-valid? | group F |
| Do the reports state the right numbers? | groups G, H, I |
| Is the chapter-level-only rule respected? | group J |
| Is the package complete? | group K |

## Known build quirks

* The workbook's digit-leading sheet names must be quoted in formulas; the builder applies a
  regex post-pass. `formulas` rejects unquoted references that Excel tolerates.
* No LibreOffice is available, so workbook recalculation is validated with `formulas` 1.3.4,
  which is stricter than Excel about syntax but does not implement every function.
