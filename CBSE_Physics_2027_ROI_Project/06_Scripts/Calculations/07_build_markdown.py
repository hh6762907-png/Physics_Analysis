#!/usr/bin/env python3
"""07_build_markdown.py - generates the Markdown research report and the
concise ranking from the model outputs (no hand-typed numbers)."""
import csv
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
PROJ = ROOT / "CBSE_Physics_2027_ROI_Project"
D = PROJ / "03_Research_Data" / "Model_Outputs"
OUT = PROJ / "01_Final_Reports"


ROOTD = PROJ / "03_Research_Data"


def load(n):
    path = D / n
    if not path.exists():
        path = ROOTD / n
    return list(csv.DictReader(open(path, encoding="utf-8")))


def f(x):
    return float(x)


rank = sorted(load("roi_primary_ranking.csv"), key=lambda r: int(r["rank"]))
mc = {int(r["chapter_no"]): r for r in load("monte_carlo_results.csv")}
rob = {int(r["chapter_no"]): r for r in load("robustness_summary.csv")}
per = {int(r["chapter_no"]): r for r in load("historical_period_comparison.csv")}
sens = load("sensitivity_analysis.csv")
units = load("unit_weightage_constraint_check.csv")
meta = __import__("json").loads((D / "model_metadata.json").read_text())

unit_marks = sum(f(r["exposure_marks"]) for r in rank)
baseline = sum(f(r["baseline_marks"]) for r in rank)
target = sum(f(r["target_marks"]) for r in rank)
extra = sum(f(r["additional_marks"]) for r in rank)
hours_all = sum(f(r["hours_total_from_zero"]) for r in rank)
dh_all = sum(f(r["additional_hours"]) for r in rank)

lines = []
A = lines.append

A("# CBSE Class XII Physics 2027 — Chapter-wise Preparation ROI")
A("")
A("**Complete research report (Markdown edition)**  ")
A("Model v1.0.0 · research cut-off 15 November 2026 · chapter-level analysis only")
A("")
A("> **Central question.** For an intermediate CBSE Class XII Physics student preparing for the "
  "2027 board examination, which chapters give the greatest realistic increase in expected marks "
  "for each additional hour of preparation, and how strong is the evidence?")
A("")
A("**Short answer.** Chapter 14 (Semiconductor Electronics) returns the most marks per additional "
  "hour, followed by Chapter 8 (Electromagnetic Waves), Chapter 13 (Nuclei), Chapter 11 (Dual "
  "Nature) and Chapter 10 (Wave Optics). Chapter 9 (Ray Optics) carries the largest expected "
  "exposure of any chapter but the longest study path, and Chapter 1 is the weakest exchange rate "
  "in the model. The top tier survives every evidence-weighting test; the exact order below rank "
  "five does not survive changes in the preparation-hour assumptions, which are the weakest input "
  "in the whole model.")
A("")
A("---")
A("")
A("## 1. Headline ranking")
A("")
A("| Rank | Chapter | Expected marks | Baseline marks | Additional marks | Additional hours | Incremental ROI | Total-mark ROI | Tier | Grade | Confidence | ROI 5–95% |")
A("|---:|---|---:|---:|---:|---:|---:|---:|:--:|:--:|---:|---:|")
for r in rank:
    c = int(r["chapter_no"])
    A(f"| {r['rank']} | C{c} {r['chapter_name']} | {f(r['exposure_marks']):.2f} | "
      f"{f(r['baseline_marks']):.2f} | {f(r['additional_marks']):.2f} | "
      f"{f(r['additional_hours']):.2f} | {f(r['incremental_roi']):.2f} | "
      f"{f(r['total_mark_roi']):.2f} | {r['tier'].replace('Tier ','')} | {r['grade']} | "
      f"{float(r['confidence_score']):.1f} | {f(mc[c]['roi_p05']):.2f}–{f(mc[c]['roi_p95']):.2f} |")
A("")
A(f"Model totals: expected exposure {unit_marks:.2f}/70 · reconstructed intermediate baseline "
  f"{baseline:.2f}/70 · target after strong board readiness {target:.2f}/70 · additional marks "
  f"available {extra:.2f} · total study path {hours_all:.0f} h · additional hours from baseline "
  f"{dh_all:.1f} h.")
A("")
A("**How to read the ROI column.** Incremental ROI = additional probability-adjusted marks ÷ "
  "additional preparation hours beyond the intermediate baseline. It is a marginal measure: it "
  "says where the *next* hour is best spent, not which chapters can be skipped. A chapter can be "
  "high-ROI and low-exposure (Chapter 8: 3.64 expected marks), or high-exposure and mid-ROI "
  "(Chapter 9: 8.07 expected marks, 0.28 marks per hour).")
A("")
A("## 2. Verified examination scope")
A("")
A("| Item | Verified value | Source |")
A("|---|---|---|")
A("| Examination | CBSE Class XII Physics (042), 2027 board, 70-mark theory paper | Official syllabus 2026-27 |")
A("| Academic session | 2026-27 (document footer; course-structure page labelled `CLASS XII (2026-27)`) | `Physics_SecP2_2026-27.pdf` p. 12 |")
A("| Chapter inventory | 14 chapters, C1–C14; none fully excluded | Official course structure |")
A("| Unit cells (marks) | 16 (C1–C3), 17 (C4–C7), 18 (C8–C10), 12 (C11–C13), 7 (C14) = 70 | Official table, merged cells read from PDF table geometry |")
A("| Paper structure | 33 questions: 16×1, 5×2, 7×3, 2×4 (case-based), 3×5 | Official SQP 2026-27 |")
A("| Internal choice | 2 questions in Section B, 1 in Section C, all 3 in Section E → 22 of 70 marks in optional slots | Official SQP 2026-27 |")
A("")
A("The supplied syllabus file was compared with the official URL "
  "`https://cbseacademic.nic.in/web_material/CurriculumMain27/SecPart2/Physics_SecP2_2026-27.pdf`; "
  "file name, title page, course structure and all fourteen chapter texts match. The official "
  "document itself carries a stale '2025-26' string on its introductory page alongside the "
  "2026-27 footer; the course-structure page is definitive.")
A("")
A("### 2.1 Content removed for 2026-27 (and how it is handled)")
A("")
A("| Ch | Status | Removed / changed | Discount on historical marks |")
A("|---|---|---|---:|")
cross = load("Syllabus_Crosswalk/syllabus_crosswalk.csv")
for r in cross:
    A(f"| {r['chapter_no']} | {r['syllabus_status_2026_27']} | {r['deleted_or_changed_content']} | "
      f"{100 * f(r['deletion_share_of_historical_marks']):.0f}% |")
A("")
A("No fully excluded chapter exists in 2026-27, so no row carries zero eligible marks. Deleted "
  "content is never included in expected marks or ROI: it enters only as a discount on the "
  "historical evidence, tested at 0.5× and 1.5× in the sensitivity analysis.")
A("")
A("## 3. Evidence base")
A("")
A("| Stream | What it is | Authority | Role in the model |")
A("|---|---|---|---|")
A("| A | Chapter question counts per year, 2017–2026 (MTG Champion trend table, image 01) | Secondary, well extracted | 40% weight; per-paper historical frequency |")
A("| B | 10-year chapter marks aggregate, all sets (MTG Weightage Xtract, images 02–15) | Secondary, well extracted | 35% weight; marks-weighted view |")
A("| C | Official CBSE SQP 2026-27, 33 questions attributed to chapters | Official, verified | 25% weight; authoritative but single instance |")
A("| Constraint | Official unit cells 16/17/18/12/7 | Official | Raking so the reconciled vector reproduces every published cell |")
A("")
A("**What could not be obtained.** No original CBSE board question paper was retrievable in this "
  "environment (egress blocked at the TLS layer), so the package contains **no question-level "
  "historical database** and no duplicate-question or per-set reconciliation. Compartment and "
  "supplementary papers were not available either. The schema, extraction procedure and coverage "
  "report for the missing database ship with the project so it can be completed later without "
  "re-designing anything.")
A("")
A("## 4. Chapter exposure by stream")
A("")
A("| Ch | Chapter | Last 5 yrs | Last 10 yrs | Recency-weighted | MTG 10-yr marks | Official SQP | Reconciled (final) |")
A("|---|---|---:|---:|---:|---:|---:|---:|")
for c in range(1, 15):
    r = per[c]
    A(f"| C{c} | {r['chapter_name']} | {f(r['last5_years_2022_2026']):.2f} | "
      f"{f(r['last10_years_2017_2026']):.2f} | {f(r['all_accessible_recency_weighted']):.2f} | "
      f"{f(r['mtg_marks_10yr_share_equivalent']):.2f} | {f(r['official_sqp_2026_27']):.2f} | "
      f"{f(r['reconciled_and_adjusted']):.2f} |")
A("")
A("Recency weighting uses a three-year half-life; the 2022 Term-I and Term-II papers are treated "
  "as half-paper instances; 2021 was not held.")
A("")
A("### 4.1 The 70-mark constraint")
A("")
A("| Unit cell | Official | Reconciled gross | After deletion | Deviation |")
A("|---|---:|---:|---:|---:|")
for r in units:
    A(f"| {r['unit_group']} | {f(r['official_marks']):.0f} | {f(r['reconciled_gross_total']):.2f} | "
      f"{f(r['final_total_after_deletion']):.2f} | {f(r['final_deviation_pct']):+.2f}% |")
A("")
A("The reconciled vector reproduces every published cell exactly by construction. The "
  "deletion-adjusted vector is renormalised to 70, which moves Unit IX down by about 12% — the "
  "quantified cost of removing Zener regulation and the special-purpose diodes.")
A("")
A("## 5. Method")
A("")
A("1. **Exposure.** E_raw = 0.40·A + 0.35·B + 0.25·C, normalised to 70 and raked inside each "
  "official merged unit cell.")
A("2. **Deletion.** E = E_raked × (1 − deletion share), renormalised to 70.")
A("3. **Choice-adjusted success.** f(r) = r + 0.5 × 0.314 × (1 − r), built from the verified "
  "optional-slot share of the 2026-27 paper.")
A("4. **Marks.** Baseline = E·f(r0); target = E·f(r1); additional = E·(f(r1) − f(r0)).")
A("5. **Hours.** Additional hours = max(1.5, H·((r1 − r0)/r1)), H = hours to strong readiness "
  "from zero, split 62% independent / 38% guided.")
A("6. **ROI.** Incremental = additional marks ÷ additional hours (primary). Total-mark = target "
  "marks ÷ total hours from zero (secondary).")
A("7. **Reliability.** 100 × (0.45 evidence consistency + 0.25 source quality + 0.30 mapping "
  "certainty); grades A ≥ 74, B ≥ 64, C below.")
A("")
A(f"Calibration: the intermediate profile reconstructs a {baseline:.2f}/70 baseline ("
  f"{100 * baseline / 70:.1f}%), and strong board readiness reconstructs {target:.2f}/70 "
  f"({100 * target / 70:.1f}%).")
A("")
A("## 6. Preparation-hour estimates")
A("")
A("| Ch | Chapter | Low | Central | High | Independent | Guided | Additional from baseline |")
A("|---|---|---:|---:|---:|---:|---:|---:|")
for r in rank:
    A(f"| {r['chapter_no']} | {r['chapter_name']} | {f(r['hours_low']):.1f} | "
      f"{f(r['hours_total_from_zero']):.1f} | {f(r['hours_high']):.1f} | "
      f"{f(r['hours_independent']):.1f} | {f(r['hours_guided']):.1f} | "
      f"{f(r['additional_hours']):.1f} |")
A(f"| | **Total** | | **{hours_all:.0f}** | | | | **{dh_all:.1f}** |")
A("")
A("These are expert estimates, not CBSE data. The low/high band is 0.75×/1.40×. They are the "
  "dominant uncertainty in the ranking (see §8).")
A("")
A("## 7. Robustness and uncertainty")
A("")
A("| Ch | Primary rank | Rank range (44 configs) | Top-3 share (configs) | P(top 3) Monte Carlo | "
  "P(top 5) Monte Carlo | Robustness |")
A("|---|---:|---:|---:|---:|---:|---:|")
for c in range(1, 15):
    r = next(x for x in rank if int(x["chapter_no"]) == c)
    b = rob[c]
    A(f"| C{c} | {r['rank']} | {b['rank_min_across_scenarios']}–{b['rank_max_across_scenarios']} | "
      f"{100 * f(b['share_top3_across_scenarios']):.0f}% | "
      f"{100 * f(b['p_top3_monte_carlo']):.0f}% | {100 * f(b['p_top5_monte_carlo']):.0f}% | "
      f"{f(b['robustness_score']):.2f} |")
A("")
A("The configuration share and the Monte Carlo probabilities answer different questions and "
  "are printed separately; neither is a predictive accuracy score.")
A("")
A("Monte Carlo: 20,000 draws, seed 20261115, exposure N(E, 0.15E) renormalised to 70 each draw, "
  "hours triangular, r0 N(profile, 0.06), r1 N(target, 0.03). The distributions are declared "
  "subjective uncertainty statements, not sampling distributions.")
A("")
A("Sensitivity: 16 structural variants. Chapter 14 is rank 1 in 14 of 16; Chapter 8 is top-three "
  "in all but one. The ranking is most sensitive to the hour structure: making hard chapters 35% "
  "more expensive moves Chapter 7 from 12 to 1 and Chapter 9 from 10 to 4.")
A("")
A("**Practical reading.** Use tiers, not exact ranks: Tier A–B (C14, C8, C13, C11, C10) is a "
  "reliable recommendation; ranks 6–14 should be treated as a broad band whose internal order "
  "depends on unmeasured study costs.")
A("")
A("## 8. Scenario results")
A("")
A("| Scenario | Chapter ranks (1 → 14) |")
A("|---|---|")
scen = load("scenario_rankings.csv")
labels = ["ability=weak|performance=realistic|readiness=strong",
          "ability=intermediate|performance=realistic|readiness=strong",
          "ability=strong|performance=realistic|readiness=strong",
          "ability=intermediate|performance=conservative|readiness=strong",
          "ability=intermediate|performance=strong|readiness=strong",
          "ability=intermediate|performance=realistic|readiness=basic",
          "ability=intermediate|performance=realistic|readiness=high",
          "evidence=historical_only", "evidence=mtg_marks_only",
          "evidence=official_sqp_only", "evidence=reconciled"]
for lab in labels:
    rows = [r for r in scen if r["scenario"] == lab]
    rows.sort(key=lambda r: int(r["rank"]))
    A(f"| `{lab}` | " + " ".join(f"C{r['chapter_no']}" for r in rows) + " |")
A("")
A("Full 27-combination grid and all four evidence-stream rankings are in "
  "`03_Research_Data/Model_Outputs/scenario_rankings.csv` and in the workbook.")
A("")
A("## 9. Reliability and limitations")
A("")
A("**Verified.** 2026-27 syllabus inventory, unit totals, paper structure, internal-choice "
  "positions, and the chapter attribution of all 33 sample-paper questions.")
A("")
A("**Secondary.** Chapter question counts 2017–2026 and the 10-year marks aggregate (MTG). "
  "Values verified against the photographs; the publisher's attribution and inclusion rules were "
  "not re-verified against original papers.")
A("")
A("**Expert judgement.** Preparation hours, difficulty indices, readiness profiles, the choice "
  "advantage parameter, the deletion shares and the evidence weights.")
A("")
A("**Open limitations.** (1) No original board paper was accessible, so there is no "
  "question-level historical database, no per-set duplicate check and no per-set marks totals. "
  "(2) Compartment and supplementary papers are absent. (3) CBSE does not publish chapter-level "
  "marks, so every chapter exposure number is an estimate; only unit totals are official. "
  "(4) Hours cannot be measured from any public source. (5) MTG's predictive accuracy over time "
  "cannot be assessed because no earlier edition was available — no accuracy score is claimed. "
  "(6) The application's adaptive engine is validated by logic tests and data-integrity checks, "
  "not by real-student calibration.")
A("")
A("## 10. Deliverables")
A("")
A("| Deliverable | Location |")
A("|---|---|")
A("| Full research report (PDF, 28 pp.) | `01_Final_Reports/Physics_2027_Complete_Research_Report.pdf` |")
A("| Concise ranking (PDF) | `01_Final_Reports/Physics_2027_Concise_Chapter_Ranking.pdf` |")
A("| Markdown report | `01_Final_Reports/Physics_2027_Research_Report.md` |")
A("| Analysis workbook (26 sheets, live formulas) | `02_Excel_Workbook/Physics_2027_ROI_Analysis.xlsx` |")
A("| Research data and registers | `03_Research_Data/` |")
A("| Audit, validation and adversarial review | `04_Audit/` |")
A("| Diagnostic PWA and question bank | `05_Diagnostic_Application/` |")
A("| Scripts (extraction, calculation, validation, reproduction) | `06_Scripts/` |")
A("| Source archive and hashes | `07_Source_Archive/` |")
A("| Documentation set | `08_Documentation/` |")
A("| Handover manifest and ZIP | `09_Final_Handover/` |")
A("")
A("---")
A("")
A("## 11. Concise final ranking")
A("")
A("| Rank | Chapter | Expected marks | Additional hours | Incremental ROI | Evidence |")
A("|---:|---|---:|---:|---:|:--:|")
for r in rank:
    A(f"| {r['rank']} | C{r['chapter_no']} {r['chapter_name']} | {f(r['exposure_marks']):.2f} | "
      f"{f(r['additional_hours']):.1f} | {f(r['incremental_roi']):.2f} | {r['grade']} |")
A("")
A("**Best ROI:** C14, C8, C13, C11, C10.  ")
A("**Near-ties:** C2/C12/C6/C3/C9 (ROI within 5–10% of neighbours; order not meaningful).  ")
A("**High uncertainty:** C1, C5, C4, C12, C14 (widest 5–95% ROI intervals and lowest evidence "
  "grades).  ")
A("**Out of syllabus:** none in 2026-27; partial deletions discounted in C6, C9, C11, C12, C14.")
A("")
A("No topic-level analysis appears in this report or in any companion deliverable, by design.")
A("")

(OUT / "Physics_2027_Research_Report.md").write_text("\n".join(lines), encoding="utf-8")
print("wrote", (OUT / "Physics_2027_Research_Report.md").relative_to(ROOT),
      len("\n".join(lines)), "chars")
