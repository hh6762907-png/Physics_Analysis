#!/usr/bin/env python3
"""
03_roi_model.py
---------------
Reproducible ROI model for the CBSE Class XII Physics 2027 board examination.

Pipeline
--------
1. Build three independent chapter-exposure evidence streams on a 70-mark scale
      A  historical per-paper question-count shares (MTG, 2017-2026, recency weighted)
      B  MTG 10-year marks aggregate shares (Weightage Xtract totals)
      C  official CBSE Sample Question Paper 2026-27 chapter attribution (choice-aware)
2. Reconcile A, B, C with reliability-calibrated weights, then rake each official
   unit group to its published marks (16/17/18/12/7) so the model reproduces 70.
3. Apply syllabus-deletion adjustment (2026-27 scope) and renormalise to 70.
4. Apply the internal-choice model (SQP-derived optional-slot share and pairing).
5. Estimate baseline and target readiness, additional probability-adjusted marks,
   preparation hours, incremental and total-mark ROI.
6. Scenario grid (3 starting abilities x 3 performance levels x 3 readiness targets),
   evidence-stream-only rankings, sensitivity analysis and Monte Carlo.

Every constant is either transcribed from an evidence artefact (see
03_Research_Data) or declared as an explicit modelling assumption.
"""
from __future__ import annotations

import csv
import json
import math
import pathlib
import random
import statistics
from typing import Dict, List

ROOT = pathlib.Path(__file__).resolve().parents[3]
PROJ = ROOT / "CBSE_Physics_2027_ROI_Project"
DATA = PROJ / "03_Research_Data"
OUT = DATA / "Model_Outputs"
OUT.mkdir(parents=True, exist_ok=True)

CHAPTERS: Dict[int, str] = {
    1: "Electric Charges and Fields",
    2: "Electrostatic Potential and Capacitance",
    3: "Current Electricity",
    4: "Moving Charges and Magnetism",
    5: "Magnetism and Matter",
    6: "Electromagnetic Induction",
    7: "Alternating Current",
    8: "Electromagnetic Waves",
    9: "Ray Optics and Optical Instruments",
    10: "Wave Optics",
    11: "Dual Nature of Radiation and Matter",
    12: "Atoms",
    13: "Nuclei",
    14: "Semiconductor Electronics: Materials, Devices and Simple Circuits",
}
# Official merged-unit groups (Physics_SecP2_2026-27.pdf p.12)
UNIT_GROUPS: List[tuple[str, List[int], int]] = [
    ("Units I+II", [1, 2, 3], 16),
    ("Units III+IV", [4, 5, 6, 7], 17),
    ("Units V+VI", [8, 9, 10], 18),
    ("Units VII+VIII", [11, 12, 13], 12),
    ("Unit IX", [14], 7),
]

# --- evidence calibrations -------------------------------------------------
PAPER_MARKS = 70
SQP_OPTIONAL_SHARE = 22 / 70          # marks printed in optional (internal-choice) slots
SQP_PAIR_SAME_SHARE = 19 / 22         # option marks whose pair sits in the same chapter
SQP_PAIR_CROSS_SHARE = 3 / 22         # option marks whose pair crosses two chapters
CHOICE_BOOST = 0.50                   # share of the gap closed by choosing the better option
GAP_ELASTICITY = 1.00                 # elasticity of hours w.r.t. remaining readiness gap
BASELINE_SLOPE = 0.11                 # readiness penalty per unit of difficulty index
EVIDENCE_WEIGHTS = {"A": 0.40, "B": 0.35, "C": 0.25}
RECENCY_HALF_LIFE_YEARS = 3.0

# Difficulty index D (1 = easiest, 5 = hardest). Expert judgement anchored on
# conceptual load, derivation load and numerical manipulation load, cross-checked
# against the format mix of the MTG question counts (share of 5-mark questions).
DIFFICULTY = {1: 2.5, 2: 3.0, 3: 2.8, 4: 3.2, 5: 2.0, 6: 2.6, 7: 3.3,
              8: 1.8, 9: 3.0, 10: 3.2, 11: 2.2, 12: 2.4, 13: 2.2, 14: 1.8}

# Hours to strong board readiness starting from zero readiness on the chapter.
# Central estimate plus low/high band; independent and guided hours are modelled
# as a fixed split of the total (independent 62%, guided 38%).
HOURS_CENTRAL = {1: 14.0, 2: 16.0, 3: 18.0, 4: 18.0, 5: 8.0, 6: 12.0, 7: 16.0,
                 8: 7.0, 9: 22.0, 10: 14.0, 11: 10.0, 12: 9.0, 13: 8.0, 14: 10.0}
HOURS_LOW_FACTOR, HOURS_HIGH_FACTOR = 0.75, 1.40
INDEPENDENT_SHARE = 0.62

# Deletion share of historical marks no longer examinable in 2026-27
# (Syllabus_Crosswalk/syllabus_crosswalk.csv)
DELETION = {1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.05, 6: 0.04, 7: 0.00,
            8: 0.00, 9: 0.08, 10: 0.00, 11: 0.03, 12: 0.09, 13: 0.00, 14: 0.15}

# Prerequisite graph used only for the supplementary dependency-adjusted ROI.
PREREQ = {1: [], 2: [1], 3: [1], 4: [1, 3], 5: [4], 6: [4], 7: [6],
          8: [7], 9: [1, 4], 10: [9], 11: [10], 12: [11], 13: [12], 14: [3]}
PREREQ_CREDIT = 0.10   # fraction of a prerequisite's hours that overlaps

MIN_ADDITIONAL_HOURS = 1.5


# ---------------------------------------------------------------------------
# evidence loading
# ---------------------------------------------------------------------------
def load_mtg_counts():
    rows = list(csv.DictReader(open(DATA / "MTG_Extracted_Data" / "mtg_questions_by_year.csv",
                                    encoding="utf-8")))
    years = []
    table: Dict[int, Dict[str, int]] = {c: {} for c in CHAPTERS}
    meta: Dict[str, tuple[str, int]] = {}
    for r in rows:
        y = r["exam_year"]
        meta[y] = (r["paper_type"], int(r["paper_marks"]))
        table[int(r["chapter_no"])][y] = int(r["questions_reported"])
    for y in dict.fromkeys(r["exam_year"] for r in rows):
        years.append(y)
    return table, meta, years


def load_mtg_marks():
    rows = list(csv.DictReader(open(DATA / "MTG_Extracted_Data" / "mtg_chapter_marks_10yr.csv",
                                    encoding="utf-8")))
    return {int(r["chapter_no"]): float(r["marks_total_10yr"])
            for r in rows if r["chapter_no"]}


def load_sqp():
    rows = list(csv.DictReader(open(DATA / "Official_Sample_Paper" / "sqp_2026_27_question_metadata.csv",
                                    encoding="utf-8")))
    # choice-aware split: an OR pair gives one question's marks at stake, shared
    # equally when the two options come from different chapters.
    pairs: Dict[str, List[dict]] = {}
    for r in rows:
        pairs.setdefault(r["internal_choice_group"], []).append(r)
    exposure = {c: 0.0 for c in CHAPTERS}
    for group, items in pairs.items():
        marks = float(items[0]["marks"])
        if group == "none":
            for it in items:                      # independent questions keep own marks
                exposure[int(it["chapter_id"][1:])] += float(it["marks"])
        else:
            chs = {int(it["chapter_id"][1:]) for it in items}
            if len(chs) == 1:                      # same-chapter option pair
                exposure[chs.pop()] += marks
            else:                                  # cross-chapter option pair
                for it in items:
                    exposure[int(it["chapter_id"][1:])] += marks / 2.0
    return exposure


# ---------------------------------------------------------------------------
# stream A : historical question-count shares, recency weighted
# ---------------------------------------------------------------------------
def stream_A(table, meta, years):
    """Return (A_recency, A_last5_equal, A_last10_equal, per-year detail)."""
    # weights: half-life decay on exam year, with 2022 Term papers (special,
    # split papers carrying 35 marks each) sharing one year's weight.
    weights: Dict[str, float] = {}
    for y in years:
        if y == "2021":
            weights[y] = 0.0
            continue
        if y.startswith("2022"):
            weights[y] = 0.5 * 0.5 ** ((2026 - 2022) / RECENCY_HALF_LIFE_YEARS)
        else:
            weights[y] = 0.5 ** ((2026 - int(y)) / RECENCY_HALF_LIFE_YEARS)

    detail = []
    for y in years:
        total_q = sum(table[c][y] for c in CHAPTERS)
        detail.append({"year": y, "paper_type": meta[y][0], "paper_marks": meta[y][1],
                       "questions": total_q, "weight": round(weights[y], 6)})

    def share_vector(year_subset, weight_vector):
        num = {c: 0.0 for c in CHAPTERS}
        den = 0.0
        for y in year_subset:
            total_q = sum(table[c][y] for c in CHAPTERS)
            if total_q == 0 or weights[y] == 0:
                continue
            w = weight_vector(y)
            den += w
            for c in CHAPTERS:
                num[c] += w * table[c][y] / total_q
        return {c: (num[c] / den * PAPER_MARKS if den else 0.0) for c in CHAPTERS}

    A_all = share_vector([y for y in years if not y.startswith("2022")] +
                         ["2022_TermI", "2022_TermII"], lambda y: weights[y])
    A5 = share_vector(["2022_TermI", "2022_TermII", "2023", "2024", "2025", "2026"],
                      lambda y: 1.0)
    A10 = share_vector([y for y in years if y != "2021"], lambda y: 1.0)
    return A_all, A5, A10, detail, weights


def stream_B(mtg_marks):
    total = sum(mtg_marks.values())
    return {c: mtg_marks[c] / total * PAPER_MARKS for c in CHAPTERS}


def normalise(vec):
    s = sum(vec.values())
    return {c: v / s * PAPER_MARKS for c, v in vec.items()}


def rake_to_units(vec):
    """Scale inside each official merged-unit group so the group total matches
    the published marks. The groups are disjoint, so a single pass is exact."""
    out = dict(vec)
    for name, chs, marks in UNIT_GROUPS:
        sub = sum(vec[c] for c in chs)
        factor = marks / sub if sub else 0.0
        for c in chs:
            out[c] = vec[c] * factor
    return out


def reconcile(A, B, C):
    raw = {c: EVIDENCE_WEIGHTS["A"] * A[c] + EVIDENCE_WEIGHTS["B"] * B[c] +
              EVIDENCE_WEIGHTS["C"] * C[c] for c in CHAPTERS}
    return rake_to_units(normalise(raw))


def apply_deletions(vec):
    out = {c: vec[c] * (1 - DELETION[c]) for c in CHAPTERS}
    return normalise(out)


# ---------------------------------------------------------------------------
# readiness / scoring model
# ---------------------------------------------------------------------------
def readiness_baseline_mid(d):
    """Intermediate starting ability. Calibrated so that the reconstructed paper
    total matches a mid-band board performance (~50-55%)."""
    return min(0.70, max(0.12, 0.80 - BASELINE_SLOPE * d))


def target_readiness(d, level="strong"):
    base = 0.93 - 0.03 * (d - 1) / 4.0
    if level == "basic":
        return base * 0.78
    if level == "high":
        return min(0.985, base + 0.055)
    return base


def choice_effective(p):
    """Expected success on probability p, after internal-choice advantage."""
    return p + CHOICE_BOOST * SQP_OPTIONAL_SHARE * (1 - p)


def additional_hours(hours_total, r0, r1):
    gap = max(0.0, (r1 - r0) / r1) if r1 > 0 else 1.0
    return max(MIN_ADDITIONAL_HOURS, hours_total * (gap ** GAP_ELASTICITY))


# ---------------------------------------------------------------------------
# single evaluation of the model
# ---------------------------------------------------------------------------
def evaluate(E, *, ability="intermediate", performance="realistic", level="strong",
             hours=HOURS_CENTRAL, r0_vec=None, r1_vec=None, deletion=True):
    rows = []
    for c in CHAPTERS:
        d = DIFFICULTY[c]
        r0 = r0_vec[c] if r0_vec else readiness_baseline_mid(d)
        if ability == "weak":
            r0 *= 0.60
        elif ability == "strong":
            r0 = min(0.78, r0 * 1.36)
        r1 = r1_vec[c] if r1_vec else target_readiness(d, level)
        if performance == "conservative":
            r1 *= 0.885
        elif performance == "strong":
            r1 = min(0.99, r1 * 1.05)
        h = hours[c]
        dh = additional_hours(h, r0, r1)
        base_marks = E[c] * choice_effective(r0)
        tgt_marks = E[c] * choice_effective(r1)
        rows.append({
            "chapter_no": c,
            "chapter_name": CHAPTERS[c],
            "exposure_marks": E[c],
            "difficulty": d,
            "baseline_readiness": r0,
            "target_readiness": r1,
            "baseline_marks": base_marks,
            "target_marks": tgt_marks,
            "additional_marks": tgt_marks - base_marks,
            "hours_total_from_zero": h,
            "hours_independent": h * INDEPENDENT_SHARE,
            "hours_guided": h * (1 - INDEPENDENT_SHARE),
            "additional_hours": dh,
            "incremental_roi": (tgt_marks - base_marks) / dh,
            "total_mark_roi": tgt_marks / h,
        })
    return rows


def rank(rows, key="incremental_roi"):
    ordered = sorted(rows, key=lambda r: (-r[key], -r["additional_marks"], r["chapter_no"]))
    for i, r in enumerate(ordered, 1):
        r["rank"] = i
    return ordered


def tiers(rows):
    """Relative ROI tiers: consecutive chapters whose incremental ROI is within
    10% of the tier leader share a tier (practical near-tie detection)."""
    ordered = sorted(rows, key=lambda r: -r["incremental_roi"])
    tiers_list, current, leader = [], [], None
    for r in ordered:
        if leader is None or r["incremental_roi"] >= 0.90 * leader:
            current.append(r)
            leader = max(leader or 0, r["incremental_roi"])
        else:
            tiers_list.append(current)
            current, leader = [r], r["incremental_roi"]
    if current:
        tiers_list.append(current)
    out = {}
    for i, group in enumerate(tiers_list, 1):
        label = "Tier " + "ABCDEFGHIJ"[i - 1]
        for r in group:
            out[r["chapter_no"]] = label
    return out


def confidence_scores(streams, E):
    """Explicit reliability index (0-100).

    reliability = 100 * (0.45*consistency + 0.25*source_quality + 0.30*mapping)
      consistency    = 1 - min(1, CV/0.45) over the three stream estimates
      source_quality = 0.75 constant (secondary historical counts + secondary
                       marks aggregate + one official sample paper; no original
                       board paper was accessible)
      mapping        = 1 - 2*deletion_share (capped to [0,1])
    """
    out = {}
    for c in CHAPTERS:
        vals = [streams[k][c] for k in ("A", "B", "C")]
        mean = statistics.fmean(vals)
        cv = statistics.pstdev(vals) / mean if mean else 1.0
        consistency = max(0.0, 1 - min(1.0, cv / 0.45))
        mapping = max(0.0, min(1.0, 1 - 2 * DELETION[c]))
        score = 100 * (0.45 * consistency + 0.25 * 0.75 + 0.30 * mapping)
        grade = "A" if score >= 74 else ("B" if score >= 64 else "C")
        out[c] = {"score": score, "grade": grade, "cv": cv,
                  "consistency": consistency, "mapping": mapping}
    return out


# ---------------------------------------------------------------------------
# Monte Carlo
# ---------------------------------------------------------------------------
def monte_carlo(E, n=20000, seed=20261115):
    rng = random.Random(seed)
    counts_top3 = {c: 0 for c in CHAPTERS}
    counts_top5 = {c: 0 for c in CHAPTERS}
    rank_samples = {c: [] for c in CHAPTERS}
    roi_samples = {c: [] for c in CHAPTERS}
    for _ in range(n):
        Es = {c: max(0.01, rng.gauss(E[c], 0.15 * E[c])) for c in CHAPTERS}
        Es = normalise(Es)
        Hs = {}
        for c in CHAPTERS:
            low = HOURS_CENTRAL[c] * HOURS_LOW_FACTOR
            high = HOURS_CENTRAL[c] * HOURS_HIGH_FACTOR
            Hs[c] = rng.triangular(low, high, HOURS_CENTRAL[c])
        r0s = {c: min(0.85, max(0.05, rng.gauss(readiness_baseline_mid(DIFFICULTY[c]), 0.06)))
               for c in CHAPTERS}
        r1s = {c: min(0.995, max(0.6, rng.gauss(target_readiness(DIFFICULTY[c]), 0.03)))
               for c in CHAPTERS}
        rows = evaluate(Es, hours=Hs, r0_vec=r0s, r1_vec=r1s)
        ordered = rank(rows)
        for i, r in enumerate(ordered, 1):
            c = r["chapter_no"]
            rank_samples[c].append(i)
            roi_samples[c].append(r["incremental_roi"])
            if i <= 3:
                counts_top3[c] += 1
            if i <= 5:
                counts_top5[c] += 1
    out = {}
    for c in CHAPTERS:
        rs = sorted(roi_samples[c])
        out[c] = {
            "p_top3": counts_top3[c] / n,
            "p_top5": counts_top5[c] / n,
            "median_rank": statistics.median(rank_samples[c]),
            "rank_p05": _pct(sorted(rank_samples[c]), 0.05),
            "rank_p95": _pct(sorted(rank_samples[c]), 0.95),
            "roi_p05": _pct(rs, 0.05),
            "roi_median": statistics.median(rs),
            "roi_p95": _pct(rs, 0.95),
        }
    return out


def _pct(sorted_vals, q):
    if not sorted_vals:
        return float("nan")
    k = (len(sorted_vals) - 1) * q
    lo, hi = math.floor(k), math.ceil(k)
    if lo == hi:
        return sorted_vals[int(k)]
    return sorted_vals[lo] * (hi - k) + sorted_vals[hi] * (k - lo)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    table, meta, years = load_mtg_counts()
    mtg_marks = load_mtg_marks()
    sqp = load_sqp()

    A, A5, A10, detail, weights = stream_A(table, meta, years)
    B = stream_B(mtg_marks)
    C = normalise(sqp)
    streams = {"A": normalise(A), "B": B, "C": C}

    reconciled = reconcile(A, B, C)
    E_final = apply_deletions(reconciled)

    # ---- exposure tables --------------------------------------------------
    exp_rows = []
    for c in CHAPTERS:
        exp_rows.append({
            "chapter_no": c, "chapter_name": CHAPTERS[c],
            "stream_A_historical_counts_recency": round(A[c], 4),
            "stream_A_last5_equal": round(A5[c], 4),
            "stream_A_last10_equal": round(A10[c], 4),
            "stream_B_mtg_marks_10yr": round(B[c], 4),
            "stream_C_official_sqp": round(C[c], 4),
            "reconciled_gross_marks": round(reconciled[c], 4),
            "deletion_share_2026_27": DELETION[c],
            "exposure_marks_2027": round(E_final[c], 4),
        })
    write_csv(OUT / "chapter_exposure_by_stream.csv", exp_rows)

    # ---- unit constraint check -------------------------------------------
    unit_rows = []
    for name, chs, marks in UNIT_GROUPS:
        gross = sum(reconciled[c] for c in chs)
        final = sum(E_final[c] for c in chs)
        unit_rows.append({"unit_group": name, "official_marks": marks,
                          "reconciled_gross_total": round(gross, 4),
                          "reconciled_deviation": round(gross - marks, 4),
                          "final_total_after_deletion": round(final, 4),
                          "final_deviation": round(final - marks, 4),
                          "final_deviation_pct": round((final - marks) / marks * 100, 2)})
    unit_rows.append({"unit_group": "ALL", "official_marks": 70,
                      "reconciled_gross_total": round(sum(reconciled.values()), 4),
                      "reconciled_deviation": round(sum(reconciled.values()) - 70, 4),
                      "final_total_after_deletion": round(sum(E_final.values()), 4),
                      "final_deviation": round(sum(E_final.values()) - 70, 4),
                      "final_deviation_pct": round((sum(E_final.values()) - 70) / 70 * 100, 2)})
    write_csv(OUT / "unit_weightage_constraint_check.csv", unit_rows)

    # ---- primary model ----------------------------------------------------
    primary = rank(evaluate(E_final))
    tier_map = tiers(primary)
    conf = confidence_scores(streams, E_final)

    # total hours from zero, dependency adjusted
    dep_hours = {}
    for c in CHAPTERS:
        shared = sum(PREREQ_CREDIT * HOURS_CENTRAL[p] for p in PREREQ[c])
        dep_hours[c] = max(1.0, HOURS_CENTRAL[c] - shared)

    base_total = sum(r["baseline_marks"] for r in primary)
    tgt_total = sum(r["target_marks"] for r in primary)

    for r in primary:
        c = r["chapter_no"]
        r["grade"] = conf[c]["grade"]
        r["confidence_score"] = round(conf[c]["score"], 1)
        r["evidence_cv"] = round(conf[c]["cv"], 3)
        r["tier"] = tier_map[c]
        r["hours_low"] = round(HOURS_CENTRAL[c] * HOURS_LOW_FACTOR, 2)
        r["hours_high"] = round(HOURS_CENTRAL[c] * HOURS_HIGH_FACTOR, 2)
        r["dep_adjusted_hours"] = round(dep_hours[c], 2)
        r["dep_adjusted_incremental_roi"] = round(
            r["additional_marks"] / additional_hours(dep_hours[c], r["baseline_readiness"],
                                                    r["target_readiness"]), 4)
        r["incremental_roi_low_hours"] = round(r["additional_marks"] /
                                               max(MIN_ADDITIONAL_HOURS,
                                                   r["additional_hours"] * 0.75), 4)
        r["incremental_roi_high_hours"] = round(r["additional_marks"] /
                                                (r["additional_hours"] * 1.40), 4)

    # near-tie flag: within 5% of the neighbour immediately above
    for i, r in enumerate(primary):
        r["near_tie_with_previous"] = bool(
            i > 0 and abs(r["incremental_roi"] - primary[i - 1]["incremental_roi"]) /
            primary[i - 1]["incremental_roi"] < 0.05)

    write_csv(OUT / "roi_primary_ranking.csv", primary)

    # ---- scenario grid ----------------------------------------------------
    scen_rows = []
    scen_rank_store = {}
    for ability in ("weak", "intermediate", "strong"):
        for perf in ("conservative", "realistic", "strong"):
            for level in ("basic", "strong", "high"):
                hours = HOURS_CENTRAL
                rows = rank(evaluate(E_final, ability=ability, performance=perf, level=level))
                label = f"ability={ability}|performance={perf}|readiness={level}"
                scen_rank_store[label] = {r["chapter_no"]: r["rank"] for r in rows}
                for r in rows:
                    scen_rows.append({
                        "scenario": label, "chapter_no": r["chapter_no"],
                        "chapter_name": r["chapter_name"], "rank": r["rank"],
                        "incremental_roi": round(r["incremental_roi"], 4),
                        "additional_marks": round(r["additional_marks"], 3),
                        "additional_hours": round(r["additional_hours"], 3),
                        "baseline_marks": round(r["baseline_marks"], 3),
                        "target_marks": round(r["target_marks"], 3),
                        "exposure_marks": "",
                    })
    # evidence-stream-only rankings (intermediate / realistic / strong)
    evidence_streams = {
        "evidence=historical_only": normalise(A),
        "evidence=mtg_marks_only": B,
        "evidence=official_sqp_only": C,
        "evidence=reconciled": E_final,
    }
    ev_rows = []
    for label, vec in evidence_streams.items():
        rows = rank(evaluate(vec))
        scen_rank_store[label] = {r["chapter_no"]: r["rank"] for r in rows}
        for r in rows:
            ev_rows.append({"scenario": label, "chapter_no": r["chapter_no"],
                            "chapter_name": r["chapter_name"], "rank": r["rank"],
                            "exposure_marks": round(vec[r["chapter_no"]], 3),
                            "incremental_roi": round(r["incremental_roi"], 4),
                            "additional_marks": round(r["additional_marks"], 3),
                            "additional_hours": round(r["additional_hours"], 3)})
        scen_rows.extend(ev_rows[-14:])
    write_csv(OUT / "scenario_rankings.csv", scen_rows)

    # ---- sensitivity ------------------------------------------------------
    sens_rows = []
    global DIFFICULTY, CHOICE_BOOST, GAP_ELASTICITY, BASELINE_SLOPE
    saved = (dict(DIFFICULTY), CHOICE_BOOST, GAP_ELASTICITY, BASELINE_SLOPE)

    def complexity_hours(hi_factor, lo_factor):
        return {c: HOURS_CENTRAL[c] * (hi_factor if DIFFICULTY[c] >= 3.0 else lo_factor)
                for c in CHAPTERS}

    variants = {
        "base": dict(E=E_final),
        "weights_equal": dict(E=rake_to_units(normalise(
            {c: (A[c] + B[c] + C[c]) / 3 for c in CHAPTERS}))),
        "weights_historical_heavy": dict(E=rake_to_units(normalise(
            {c: 0.60 * A[c] + 0.25 * B[c] + 0.15 * C[c] for c in CHAPTERS}))),
        "weights_mtg_heavy": dict(E=rake_to_units(normalise(
            {c: 0.25 * A[c] + 0.60 * B[c] + 0.15 * C[c] for c in CHAPTERS}))),
        "no_deletion_adjustment": dict(E=reconciled),
        "deletion_x1_5": dict(E=normalise({c: reconciled[c] * (1 - min(0.6, 1.5 * DELETION[c]))
                                           for c in CHAPTERS})),
        "deletion_x0_5": dict(E=normalise({c: reconciled[c] * (1 - 0.5 * DELETION[c])
                                           for c in CHAPTERS})),
        "hours_hard_chapters_x1_35": dict(E=E_final, hours=complexity_hours(1.35, 0.90)),
        "hours_hard_chapters_x0_75": dict(E=E_final, hours=complexity_hours(0.75, 1.10)),
        "ac_generator_in_ch6": dict(E=E_final),
        "baseline_slope_flat_0_06": dict(E=E_final, slope=0.06),
        "baseline_slope_steep_0_17": dict(E=E_final, slope=0.17),
        "gap_elasticity_0_7": dict(E=E_final, elasticity=0.7),
        "gap_elasticity_1_3": dict(E=E_final, elasticity=1.3),
        "choice_boost_0": dict(E=E_final, choice=0.0),
        "choice_boost_0_75": dict(E=E_final, choice=0.75),
    }
    base_ranks = {r["chapter_no"]: r["rank"] for r in primary}
    robust_ranks = {c: [base_ranks[c]] for c in CHAPTERS}
    for name, cfg in variants.items():
        DIFFICULTY, CHOICE_BOOST, GAP_ELASTICITY, BASELINE_SLOPE = (
            dict(saved[0]), saved[1], saved[2], saved[3])
        if "slope" in cfg:
            BASELINE_SLOPE = cfg["slope"]
        if "elasticity" in cfg:
            GAP_ELASTICITY = cfg["elasticity"]
        if "choice" in cfg:
            CHOICE_BOOST = cfg["choice"]
        E = dict(cfg["E"])
        if name == "ac_generator_in_ch6":
            # MTG places the AC generator topic in Ch6; the 2026-27 syllabus lists it
            # in Ch7. Reallocate the estimated generator marks (38 of 2654 marks in the
            # MTG aggregate) between the two chapters and re-rake.
            shift = 38 / 2654 * 70 * 0.5
            E[6] += shift
            E[7] = max(0.1, E[7] - shift)
            E = rake_to_units(normalise(E))
        rows = rank(evaluate(E, hours=cfg.get("hours", HOURS_CENTRAL)))
        for r in rows:
            sens_rows.append({"variant": name, "chapter_no": r["chapter_no"],
                              "chapter_name": r["chapter_name"], "rank": r["rank"],
                              "rank_change_vs_base": base_ranks[r["chapter_no"]] - r["rank"],
                              "incremental_roi": round(r["incremental_roi"], 4)})
            robust_ranks[r["chapter_no"]].append(r["rank"])
    DIFFICULTY, CHOICE_BOOST, GAP_ELASTICITY, BASELINE_SLOPE = saved
    write_csv(OUT / "sensitivity_analysis.csv", sens_rows)

    # ---- Monte Carlo ------------------------------------------------------
    mc = monte_carlo(E_final, n=20000)
    mc_rows = []
    for c in CHAPTERS:
        r = next(x for x in primary if x["chapter_no"] == c)
        mc_rows.append({"chapter_no": c, "chapter_name": CHAPTERS[c], "rank": r["rank"],
                        "incremental_roi": round(r["incremental_roi"], 4),
                        "p_top3": round(mc[c]["p_top3"], 4),
                        "p_top5": round(mc[c]["p_top5"], 4),
                        "median_rank": mc[c]["median_rank"],
                        "rank_p05": round(mc[c]["rank_p05"], 2),
                        "rank_p95": round(mc[c]["rank_p95"], 2),
                        "roi_p05": round(mc[c]["roi_p05"], 4),
                        "roi_median": round(mc[c]["roi_median"], 4),
                        "roi_p95": round(mc[c]["roi_p95"], 4)})
    write_csv(OUT / "monte_carlo_results.csv", mc_rows)

    # ---- robustness summary ----------------------------------------------
    rob_rows = []
    model_ranks = {c: [] for c in CHAPTERS}
    for label, mapping in scen_rank_store.items():
        if label.startswith("evidence="):
            continue
        for c, rk in mapping.items():
            model_ranks[c].append(rk)
    for c in CHAPTERS:
        ranks = model_ranks[c] + robust_ranks[c]
        rob_rows.append({
            "chapter_no": c, "chapter_name": CHAPTERS[c],
            "primary_rank": base_ranks[c],
            "rank_min_across_scenarios": min(ranks),
            "rank_max_across_scenarios": max(ranks),
            "rank_median_across_scenarios": statistics.median(ranks),
            "n_scenarios": len(ranks),
            # Share of the 44 deterministic scenario configurations in which the
            # chapter lands in the top three / five. This is NOT a probability and
            # must not be compared with the Monte Carlo columns below; the two
            # answer different questions (configuration coverage vs sampling).
            "share_top3_across_scenarios": round(sum(1 for x in ranks if x <= 3) / len(ranks), 4),
            "share_top5_across_scenarios": round(sum(1 for x in ranks if x <= 5) / len(ranks), 4),
            "p_top3_monte_carlo": round(mc[c]["p_top3"], 4),
            "p_top5_monte_carlo": round(mc[c]["p_top5"], 4),
            # Composite robustness: percentile rank spread (outlier-robust) and the
            # share of configurations in which the chapter reaches the top three.
            # Range-only scores punish a single unusual configuration and would call
            # the most stable chapter unstable; both components are on 0-1.
            "robustness_score": round(
                0.5 * (1 - (mc[c]["rank_p95"] - mc[c]["rank_p05"]) / 13)
                + 0.5 * (sum(1 for x in ranks if x <= 3) / len(ranks)), 3),
        })
    write_csv(OUT / "robustness_summary.csv", rob_rows)

    # ---- model metadata ---------------------------------------------------
    meta_out = {
        "model_version": "1.0.0",
        "generated": "2026-11-15",
        "paper_marks": PAPER_MARKS,
        "evidence_weights": EVIDENCE_WEIGHTS,
        "recency_half_life_years": RECENCY_HALF_LIFE_YEARS,
        "sqp_optional_share_of_marks": round(SQP_OPTIONAL_SHARE, 4),
        "sqp_same_chapter_option_share": round(SQP_PAIR_SAME_SHARE, 4),
        "choice_boost": CHOICE_BOOST,
        "independent_hours_share": INDEPENDENT_SHARE,
        "hours_low_factor": HOURS_LOW_FACTOR,
        "hours_high_factor": HOURS_HIGH_FACTOR,
        "min_additional_hours": MIN_ADDITIONAL_HOURS,
        "reconstructed_baseline_paper_total": round(base_total, 3),
        "reconstructed_target_paper_total": round(tgt_total, 3),
        "exposure_sum": round(sum(E_final.values()), 6),
        "note": ("Stream A is a secondary historical count series published by MTG; no original "
                 "CBSE board paper could be retrieved in this environment, so no question-level "
                 "historical marks database exists. Stream C is a verified official artefact "
                 "(CBSE SQP 2026-27) attributed question by question."),
        "historical_period_estimates_included": {
            "last5_equal_weight": {str(c): round(A5[c], 3) for c in CHAPTERS},
            "last10_equal_weight": {str(c): round(A10[c], 3) for c in CHAPTERS},
            "all_accessible_recency_weighted": {str(c): round(A[c], 3) for c in CHAPTERS},
        },
        "monte_carlo_draws": 20000,
        "random_seed": 20261115,
    }
    (OUT / "model_metadata.json").write_text(json.dumps(meta_out, indent=2), encoding="utf-8")

    # period table
    per_rows = []
    for c in CHAPTERS:
        per_rows.append({"chapter_no": c, "chapter_name": CHAPTERS[c],
                         "last5_years_2022_2026": round(A5[c], 3),
                         "last10_years_2017_2026": round(A10[c], 3),
                         "all_accessible_recency_weighted": round(A[c], 3),
                         "mtg_marks_10yr_share_equivalent": round(B[c], 3),
                         "official_sqp_2026_27": round(C[c], 3),
                         "reconciled_and_adjusted": round(E_final[c], 3)})
    write_csv(OUT / "historical_period_comparison.csv", per_rows)

    print(f"primary ranking (intermediate / realistic / strong readiness)")
    print(f"  baseline paper total = {base_total:.2f}/70, target = {tgt_total:.2f}/70")
    for r in primary:
        print(f"  {r['rank']:2d}. C{r['chapter_no']:<2d} E={r['exposure_marks']:5.2f} "
              f"dM={r['additional_marks']:5.2f} dH={r['additional_hours']:5.2f} "
              f"ROI={r['incremental_roi']:.3f} {r['tier']:7s} {r['grade']} "
              f"P(top3)={mc[r['chapter_no']]['p_top3']:.2f}")
    print(f"wrote {OUT.relative_to(ROOT)}/")


def write_csv(path: pathlib.Path, rows):
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as fh:
        cw = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        cw.writeheader()
        for r in rows:
            cw.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
    print(f"  wrote {path.name} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
