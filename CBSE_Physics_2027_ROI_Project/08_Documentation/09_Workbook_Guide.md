# Workbook guide (26 sheets, live formulas)

Input cells are pale yellow. Everything else calculates. Change an input on `03_Inputs` and the
ranking, ROIs, scenario grid and dashboard move with it.

| Sheet | Purpose |
|---|---|
| `01_Instructions` | Read-first page: what to change, what not to |
| `02_Dashboard` | KPIs, top-three chapters, tier counts, charts |
| `03_Inputs` | Per-chapter exposure, readiness, hours, deletion share, difficulty — the editable surface |
| `04_Final_Ranking` | The primary 1–14 ranking with live RANK/INDEX-MATCH |
| `05_Historical_Evidence` | Stream A counts by year and the three weighting variants |
| `06_MTG_Evidence` | Stream B ten-year marks and derived shares |
| `07_Sample_Paper` | The 33-question attribution and its 70-mark total check |
| `08_Reconciliation` | Weighted combination and unit-cell raking with checks |
| `09_Choice_Model` | Optional-slot share, choice advantage, effective coefficient |
| `10_Hours` | Hours low/central/high, independent/guided split |
| `11_ROI_Incremental` | Primary ROI and its components |
| `12_ROI_Total` | Secondary total-mark ROI |
| `13_Confidence` | Evidence consistency, source quality, mapping certainty, grade |
| `14_Scenario_Control` | Dropdowns for ability / performance / readiness with data validation |
| `15_Scenario_Grid` | All 27 combinations |
| `16_Sensitivity` | 16 structural variants |
| `17_Uncertainty` | Monte Carlo percentiles and P(top 3)/P(top 5) with sum checks |
| `18_Unit_Constraint` | Official cells vs gross and deletion-adjusted vectors |
| `19_Syllabus_Crosswalk` | 2026-27 deletions with discount shares |
| `20_Source_Register` | Sources, authority level, verification status |
| `21_Image_Register` | The 15/15 photograph register |
| `22_Evidence_Coverage` | What is covered, what is missing |
| `23_Audit_Checks` | Nine live consistency checks, each showing OK/CHECK |
| `24_Methodology` | Formulae as implemented |
| `25_Personal_Diagnostic` | Enter your own readiness per chapter to get a personalised gap and ROI |
| `26_Version_History` | Model/app versions and change log |

## Using the personal diagnostic

Put your measured readiness (0–1) from the app into column E on `25_Personal_Diagnostic`. The
sheet computes your gap in probability-adjusted marks and your marginal ROI using the research
exposure and hours. It is a what-if surface, not a promise.

## Recalculation

The workbook stores formulas, not cached values, so it recalculates on open in Excel, LibreOffice
or Google Sheets. During the build, every formula was compiled and evaluated with `formulas`
1.3.4: 736 formula cells, zero syntax errors, and the checks on `23_Audit_Checks` all return OK.

## Compatibility notes

Only `SUM`, `ROUND`, `IF`, `AND`, `ABS`, `SUMPRODUCT`, `COUNTIF`, `RANK`, `INDEX`, `MATCH`,
`MIN`, `MAX` and `COUNTA` are used, so the file opens on mobile Excel without dynamic-array or
LAMBDA support. Charts are native Excel charts, editable.
