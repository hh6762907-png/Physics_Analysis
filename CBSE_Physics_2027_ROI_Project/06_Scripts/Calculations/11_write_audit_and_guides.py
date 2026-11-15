#!/usr/bin/env python3
"""11_write_audit_and_guides.py - remaining documentation, the adversarial audit
and the audit summary."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
PROJ = ROOT / "CBSE_Physics_2027_ROI_Project"
DOCS = PROJ / "08_Documentation"
AUDIT = PROJ / "04_Audit"
DOCS.mkdir(parents=True, exist_ok=True)
(AUDIT / "Adversarial_Audit").mkdir(parents=True, exist_ok=True)

FILES = {}

FILES[DOCS / "05_Limitations_and_Assumptions.md"] = """# Limitations and assumptions

Everything in this document is a reason to trust the report *less* than a casual reading
suggests. It is deliberately complete.

## 1. What CBSE does not publish, and this project cannot invent

CBSE publishes **unit** marks (16/17/18/12/7) and question papers. It does **not** publish
chapter-level marks. Every chapter-level number in this project is therefore an estimate
constrained to sum to an official total. The unit cells are verified; the split *within* a
cell between its chapters is inferred.

## 2. The missing question-level database

No original board paper could be retrieved (see `03_Source_Register_and_Provenance.md`).
Consequences:

* no count of questions per chapter per set, only the publisher's annual counts;
* no duplicate detection across sets;
* no compartment or supplementary evidence at all;
* no verification of MTG's own inclusion rules.

The schema and extraction procedure ship in `03_Research_Data/` so the database can be added
later without changing the model.

## 3. Circularity in the constraint check

Because the reconciled vector is *raked* to the official unit cells, "it reproduces every cell
exactly" is true by construction, not an empirical finding. It is a statement that the model
is consistent with the official constraint, not that it is correct. The gross deviation
(before raking) is reported separately so the reader can see how far the raw evidence was
moved.

## 4. Expert judgement enters in four places

| Parameter | Value | Why it cannot be measured here |
|---|---|---|
| Hours to strong readiness per chapter | 6–19 h | No dataset of student study time exists; could be measured in the app |
| Chapter difficulty index (drives `r0`) | 0.35–0.72 | Requires item-level response data |
| Readiness targets (`r1`) | 0.45–0.95 by scenario | Definitional, but the values are chosen |
| Deletion shares | 0–15% | Weighs removed content against the historical evidence; no published weights |

Each is varied in the sensitivity analysis; the ranking's sensitivity to hours is the largest
single vulnerability and is stated in the report rather than buried.

## 5. Evidence asymmetries

* Stream C (the official sample paper) is a **single instance** carrying 25% weight. One paper
  is a weak estimate of a distribution, and its topic mix may reflect one setter's preferences.
* Stream A and B both come from the same publisher and are correlated. Treating them as
  independent evidence overstates the amount of independent information (the weights
  0.40/0.35/0.25 do not correct for this).
* The 2022 session was split into two terms with reduced syllabi; treating each as a half
  paper is a modelling choice, not a fact.

## 6. Internal choice is modelled, not observed

`f(r) = r + 0.157(1 − r)` assumes a student facing two alternatives has prepared exactly one of
them with probability 0.5 and gains 50% of the remaining gap. Reality is heterogeneous: some
students prepare both (no gain), some neither (no gain). The aggregate is plausible; the
per-student prediction is not.

## 7. Deletion adjustment renormalises

Removing content and rescaling to 70 implies that marks freed by deletion are redistributed to
the remaining content pro rata. CBSE could instead redistribute them to specific units. The
observable effect (Unit IX −11.9%) is published; the assumption is not hidden.

## 8. Thresholds are conventions

Tier boundaries (10% of tier leader), near-tie labelling (5%), grade cut-offs (74/64),
confidence weights (0.45/0.25/0.30) and the ROI-per-hour floor (1.5 h) are conventions chosen
for interpretability. Different conventions move individual ranks, not the top tier.

## 9. The application is not validated on students

The adaptive selector, readiness estimator, scheduler and calibration statistics are verified
by 53 logic assertions and 30 DOM/behaviour assertions. That is software correctness, not
pedagogical validity. No student cohort was available. The 84-item bank is small: after roughly
six sessions the app begins to repeat items, and its readiness estimates then depend on
recalled answers.

## 10. Copyright and reproduction

No CBSE question text and no MTG content is reproduced. The sample paper is used as *metadata*
(section, marks, chapter) and the answer attribution is a factual mapping. The app's questions
are original. If a future maintainer adds real past-paper text, they must clear rights first.

## 11. Scope exclusions

The 30-mark practical examination, the 2027 sample paper (not yet published), and any change
CBSE makes after 15 November 2026 are outside the model. If the syllabus changes, the
reconciliation must be recomputed from `official_unit_weightage.csv`.
"""

FILES[DOCS / "06_PWA_Architecture.md"] = """# Offline application: architecture and algorithms

## Files

| File | Role |
|---|---|
| `index.html` | Single-page shell; seven views; no external assets |
| `styles.css` | Layout and theme; responsive down to 360 px |
| `logic.js` | Pure logic: readiness, selection, scheduling, ROI, exam builder, backup validation, session accounting. Loaded in the browser and `require`d by the tests |
| `app.js` | DOM, IndexedDB, timers, import/export, rendering |
| `sw.js` | Service worker: precache shell, cache-first, navigation fallback |
| `manifest.webmanifest` | Install metadata, icons, shortcuts, standalone display |
| `data/research_ranking.json` | Read-only research values (chapters, exposure, hours, ROI, tier, grade) |
| `data/question_bank.json` | 84 original items |

`Application_Source/` is the reviewed source; `PWA/` is a byte-identical build produced by
`09_build_pwa.py` with a SHA-256 manifest (`PWA/build_manifest.json`).

## Data model

IndexedDB database `cbse_physics_2027`, version 1, four object stores: `responses`
(auto-increment), `reviews` (keyed by item id), `sessions` (auto-increment), `meta`
(key-value: settings, snapshots, schema). No data leaves the device: there is no network call
after installation and no third-party script.

## Readiness estimation

```
w_i = 0.8, 1.0, 1.25   for difficulty 1, 2, 3
accuracy   = Σ w_i · correct_i / Σ w_i
observed   = correct_count / n
raw        = 0.75·accuracy + 0.25·observed
readiness  = 0.5 + (raw − 0.5) · n/(n+5)
```

The shrinkage term keeps a two-answer chapter near 50% instead of declaring mastery. Estimates
are flagged `provisional` below five attempts, and the UI never shows a provisional chapter as
measured. Confidence is recorded separately and never folded into readiness; calibration is
reported through the Brier score and a five-band table.

## Adaptive selection

1. Fewest attempts first (coverage);
2. then highest research ROI;
3. then difficulty closest to the productive-struggle band (`<0.45 → 1`, `>0.75 → 3`, else 2);
4. unseen before seen, then least-recently seen; ties break on item id.

Ordering the coverage rule above ROI is a deliberate choice: a diagnostic that only samples
high-ROI chapters leaves the rest unmeasured, which would make the personalised recommendation
circular.

## Spaced repetition

Ladder 1, 3, 7, 16, 35, 75 days; ease 1.3–2.5; a correct answer advances a rung, a wrong
answer returns to the first. Intervals are `base × ease/2`, capped at 180 days. Due items are
surfaced on the dashboard.

## Personalised recommendation

```
f(r)   = r + 0.5·0.3143·(1 − r)
gain   = exposure · (f(target) − f(measured))
hours  = max(1.5, hoursToStrong · (target − measured)/target)
ROI    = gain / hours
```

Research exposure and hours are inputs; the measured readiness replaces the research baseline
rather than being averaged with it, so no quantity is counted twice.

## Strict exam mode

`buildExamPaper(seed)` creates 16×1 + 5×2 + 7×3 + 2×4 + 3×5 = 70 marks from the bank, grouping
same-chapter items into composite 3/4/5-mark slots so the marks are exact. The paper is
reproducible from the seed, refuses to start if the total is not 70, and never reuses an item
inside one paper. Duration 180 min with a live countdown. Objective items are auto-marked;
written items are self-marked against the rubric, one mark at a time, and nothing is guessed on
the student's behalf.

## Backup, restore, versions

Export produces `{app, schema, appVersion, exportedAt, settings, responses, reviews, sessions}`.
Import validates app id, schema, and every response record before touching existing data,
migrates older schemas, and requires confirmation. Up to ten version snapshots are kept in
`meta.snapshots`; restoring one first snapshots the current state, so rollback is itself
reversible.

## Tests

| Suite | Assertions | What it proves |
|---|---|---|
| `tests/logic.test.js` | 53 | Pure logic: readiness, Brier, calibration buckets, selection, scheduler, ROI, exam totals/uniqueness/determinism, backup validation, migration, session accounting |
| `tests/dom.smoke.test.js` | 30 | The real `index.html` + `app.js` in jsdom with a real IndexedDB: boot, dashboard, navigation, answering a question, persistence, exam generation, timer, backup view |

Run: `node tests/logic.test.js` and (with jsdom and fake-indexeddb installed)
`NODE_PATH=<node_modules> node tests/dom.smoke.test.js`. `06_validate_outputs.py` runs both and
records the result; if the dev dependencies are absent the DOM suite is reported as a warning,
never as a pass.

## What is *not* verified

No real browser was available in the build environment (no Chromium/Playwright), so layout,
service-worker installation and install prompt behaviour were validated by static checks
(asset presence, cache list, no external URLs, manifest fields) rather than by execution. See
the limitations document.
"""

FILES[DOCS / "07_User_Guide_Student.md"] = """# Using the app

## Install

Serve the `PWA/` folder over HTTP and open it — for example
`python -m http.server 8080` inside `PWA/`, then `http://localhost:8080/`. Install from the
browser menu (Chrome/Edge install icon, Android *Add to Home screen*, iOS *Share → Add to Home
Screen*). After the first load the app works with no network: the shell, the question bank and
the research values are precached.

## First session (about 15 minutes)

1. **Practice.** Answer six to ten questions. Pick *Low / Medium / High* confidence *before*
   answering — this is what makes the calibration statistics meaningful later.
2. **Dashboard.** Chapters you have touched now show a readiness bar; the rest say *not set*.
   The recommendation cards appear as soon as at least one chapter is measured.
3. **Study.** Start the timer when you begin working; use *Start break* rather than stopping the
   timer, so break time is recorded separately.

## A working week

| When | Do | Why |
|---|---|---|
| Daily, 10 min | Practice until the dashboard's *Due today* list is empty | Spaced repetition keeps earlier chapters alive |
| Twice a week | Strict exam mode (seed default) | Full-paper timing and stamina |
| After each exam | Self-mark written answers honestly | The readiness estimate depends on it |
| Weekly | Check *Progress → Confidence calibration* | A positive gap means overconfidence |

## Reading your own numbers

* **Readiness** is a weighted accuracy shrunk towards 50% until five questions are answered.
  Below five attempts it is labelled *provisional* and should not drive decisions.
* **Gap** (confidence − actual accuracy) above +10% means you are overconfident in that
  chapter; the fix is more checking, not more content.
* **Brier score**: 0.25 is what you get by always saying 50%; lower is better. It moves slowly
  and is not a grade.
* **Recommendation cards** show *your* gap, *your* hours and *your* marginal return. They will
  differ from the research ranking, because they use your measured starting point.

## Data care

Export a backup from the **Backup** tab after any substantial session. Snapshots are kept in
the browser, but clearing site data removes everything, snapshots included. Importing a
backup replaces current data after confirmation; the import report tells you exactly what was
loaded or why it was refused.

## Honest limits

84 questions means repeats after a few sessions; use the exam mode and the workbook between
sessions. Self-marking is only as honest as you are. The app measures what you can do on
CBSE-style questions, not what you will score in March.
"""

FILES[DOCS / "08_Reproducibility.md"] = """# Reproducibility

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
"""

FILES[DOCS / "09_Workbook_Guide.md"] = """# Workbook guide (26 sheets, live formulas)

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
"""

FILES[AUDIT / "Adversarial_Audit" / "Adversarial_Audit.md"] = """# Adversarial audit

**Purpose.** To attack this project as a hostile reviewer would, before anyone else does. Each
entry states the challenge, the evidence, what was done about it, and what risk remains. No
entry is resolved by assertion alone.

---

## A1. "Reproducing the official unit cells is circular." — **Serious**

*Challenge.* The exposure vector is raked to 16/17/18/12/7, so the check "it matches every
cell" is guaranteed by construction. Presenting it as validation is misleading.

*Response.* Accepted. The report now describes the check as consistency with a constraint, not
as empirical corroboration, and publishes the pre-raking deviations so the size of the
adjustment is visible (`unit_weightage_constraint_check.csv`: `reconciled_deviation`).

*Residual.* The chapter-level split inside each cell still rests on MTG and the sample paper.
There is no way to test it without CBSE chapter-level marks, which do not exist publicly.

## A2. "Hours dominate the answer, so this is a study-time ranking, not a marks ranking." — **Serious**

*Challenge.* Sensitivity variant `hours_hard_chapters_x1_35` moves Chapter 7 from 12 to 1.

*Response.* Accepted and stated in the report, the Markdown edition and the app's About page.
The incremental ROI is reported alongside exposure so a reader can see the two components.

*Residual.* Unresolved by design. Hours are the one input the application can eventually
replace with measured study time; until then, tier-level conclusions are the defensible ones.

## A3. "The evidence weights 0.40/0.35/0.25 are arbitrary." — **Moderate**

*Response.* They are conventions, disclosed as such, and varied in the sensitivity analysis
(`weights_mtg_heavy`, equal weights, SQP-heavy). Stream C is official but single-instance,
which is why it does not dominate.

*Residual.* No data-driven weighting is possible: there is no ground truth of chapter marks.

## A4. "Two of your three streams come from the same publisher and are correlated." — **Serious**

*Response.* Stated in the limitations: treating A and B as independent overstates the
independent information. The weights do not correct for it.

*Residual.* A correlation-aware weighting would need per-year per-set data, which the
photographs do not support.

## A5. "The choice parameter 0.157 is invented." — **Moderate**

*Response.* The share (22/70) is verified from the official paper. The 50% split is an
assumption, tested at 0 and 0.75 in sensitivity; the top tier is unaffected, mid-ranks move.

*Residual.* Heterogeneous student behaviour is not modelled.

## A6. "Deletion shares are guesses." — **Moderate**

*Response.* They are declared expert estimates, applied once, renormalised, and varied by
0.5×/1.5×. Their effect is reported (Unit IX −11.9%).

*Residual.* A better estimate would require knowing the deleted content's historical weight,
which the MTG pages do not break out at that granularity.

## A7. "The confidence score and grade thresholds are arbitrary numbers." — **Moderate**

*Response.* Disclosed in the methodology; the score is a summary of three declared components,
not a measurement. Ranks are not reordered by it — it is used for tie-breaking only.

*Residual.* Cosmetic authority risk: a 0–100 score looks more precise than it is. The report
prints the grade next to it and warns against reading it as probability of success.

## A8. "Monte Carlo with subjective distributions is theatre." — **Serious-ish**

*Challenge.* Assuming normal/triangular distributions the analyst chose is not evidence.

*Response.* The report calls them uncertainty statements and prints the assumptions. The
sensitivity analysis — which is distribution-free — carries the robustness argument; Monte
Carlo is supporting, not primary. Sum checks (P(top 3) = 3.0, P(top 5) = 5.0) verify arithmetic
only.

*Residual.* Readers who treat "86%" as a probability of a 2027 outcome will over-read it. The
report says explicitly that it is not a predictive accuracy score.

## A9. "One official paper is not evidence of a distribution." — **Serious**

*Response.* Stated. Stream C is capped at 25% and varied down to 0 in sensitivity.

*Residual.* The 2027 paper may differ from the 2026-27 sample paper.

## A10. "The app's 'adaptive' engine is marketing." — **Moderate**

*Response.* The algorithm is published, deterministic and tested; the coverage-first rule is
justified (a diagnostic that ignores 9 chapters cannot personalise); the bank is small and the
repeats are disclosed.

*Residual.* No student validation. The engine cannot be said to improve outcomes.

## A11. "Self-marked written answers corrupt the readiness estimate." — **Moderate**

*Response.* Self-marking is explicit, requires an action per question, and is excluded from
objective readiness weighting except as a binary correct/incorrect at half marks. The
calibration table exposes systematic over-marking.

*Residual.* Dishonest marking produces flattering readiness. Nothing in the app can prevent it.

## A12. "Copyright: you reproduced the sample paper." — **Low**

*Response.* The attribution file records question number, section, marks and chapter — metadata,
not text. No question wording is stored. The app's 84 items are original and labelled.

*Residual.* The MTG-derived aggregates are facts about a commercial compilation; they are
summarised, not reproduced page by page.

## A13. "Your workbook may contain silent errors." — **Low (tested)**

*Response.* 736 formula cells, compiled and evaluated with `formulas` 1.3.4; nine live audit
checks return OK; the validator re-checks for unbalanced parentheses, unquoted sheet references,
and the presence of the required sheets. The workbook's computed baseline (40.90), target
(65.13) and ROI vector match the Python model to three decimals.

*Residual.* `formulas` is not Excel. A function behaving differently in Excel would not be
caught; only simple, universally supported functions are used for that reason.

## A14. "Reports can drift from the model." — **Low (tested)**

*Response.* All reports are generated from the CSVs; the validator asserts that every ROI value
appears in the Markdown, that counts match, and that the app's embedded ranking equals the CSV.

*Residual.* Narrative sentences not generated from data can still go stale; the numbers that
matter are generated.

## A15. "No real browser test was run, yet you ship a PWA." — **Moderate**

*Response.* Stated plainly in the architecture document and the verification report. What was
executed: 53 logic assertions, 30 jsdom DOM/behaviour assertions, `node --check` on all scripts,
static checks on the manifest, service-worker cache list, absence of external URLs, and build
hash equality. What was not: real rendering, service-worker installation, install prompts.

*Residual.* A layout or service-worker defect could survive. The app is a study tool, not a
system of record; data export is available.

## A16. "Why is Chapter 14 first? Semiconductors feel small." — **Checked**

*Challenge.* Intuition says a 7-mark unit should not top a marks-per-hour ranking.

*Response.* Unit IX carries 7 official marks and the chapter has low study cost; its marginal
return per hour is therefore high. The report shows exposure (6.17 marks) next to ROI so the
reader sees that it is a *marginal* result, not a claim that Chapter 14 is the most important
chapter. It is also the chapter where the deletion discount is largest (15%), which is
conservative rather than flattering.

---

## Summary of residual risk

| Risk | Severity after mitigation |
|---|---|
| Chapter split within official unit cells is unverifiable | High, irreducible |
| Hours dominate the ranking | High, disclosed |
| Correlated evidence streams | Moderate, disclosed |
| Single-instance official paper | Moderate, bounded by weights |
| App not validated on students or a real browser | Moderate, disclosed |
| Reports drifting from model | Low, tested |
| Workbook formula errors | Low, tested |

Nothing in this audit was resolved by deleting a criticism. Where a problem could not be
fixed, it is in the limitations document and, where it affects a conclusion, in the report
itself.
"""

FILES[AUDIT / "Audit_Summary.md"] = """# Audit summary

| Audit | Location | Scope | Result |
|---|---|---|---|
| Input integrity | `07_Source_Archive/Metadata/input_hashes_sha256.txt` | 16 supplied files | All present, all byte-identical to first registration |
| Image accounting | `03_Research_Data/Image_Accounting_Register/` | 15 photographs | 15/15 registered; OCR rejected as evidence; quality flagged per page |
| Source register | `03_Research_Data/Source_Register/source_register.csv` | Every source used | Authority level and verification status recorded per source |
| Dataset build | `03_Research_Data/**/*.csv` | 8 evidence CSVs | Row counts and totals checked by the validator |
| Model | `03_Research_Data/Model_Outputs/` | 8 CSVs + metadata | Invariants (sums, ranks, monotonicity, ROI identity) and byte-for-byte reproducibility |
| Workbook | `02_Excel_Workbook/` | 26 sheets, 736 formulas | Compiled and evaluated; 9 live checks OK; no unbalanced parentheses; quoted sheet refs |
| Reports | `01_Final_Reports/` | PDF (28 pp), concise PDF, Markdown | Key values present and matched to CSVs; limitations stated |
| Application | `05_Diagnostic_Application/` | PWA build | 53 logic + 30 DOM assertions pass; static offline/manifest checks pass; no browser execution performed |
| Adversarial review | `04_Audit/Adversarial_Audit/Adversarial_Audit.md` | 16 challenges | 4 accepted and disclosed, 3 tested and low-risk, remainder bounded by disclosed assumptions |
| Validation suite | `04_Audit/Validation_Reports/` | 99 checks | See `validation_report.md`; WARN entries are unexecuted checks, not passes |

## Standing statement

The validator and these audits establish that the artefacts are internally consistent,
reproducible from the stated inputs, and honest about what they do not contain. They do **not**
establish that the ranking predicts the 2027 paper. Chapter-level marks are not published by
CBSE; the chapter split inside each official unit cell is an inference, and the largest single
uncertainty is the preparation-hour estimate.
"""
for path, text in FILES.items():
    path.write_text(text, encoding="utf-8")
print("wrote", len(FILES), "files")
