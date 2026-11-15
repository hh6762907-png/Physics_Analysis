#!/usr/bin/env python3
"""
04_make_charts.py
-----------------
Renders the figures used by the PDF report and the Excel dashboard.
Input  : 03_Research_Data/Model_Outputs/*.csv
Output : 01_Final_Reports/figures/*.png
"""
import csv
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
PROJ = ROOT / "CBSE_Physics_2027_ROI_Project"
OUT = PROJ / "01_Final_Reports" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
DATA = PROJ / "03_Research_Data" / "Model_Outputs"

PINK = "#c2185b"
SLATE = "#37474f"
GREY = "#90a4ae"
LIGHT = "#f8bbd0"


def load(name):
    return list(csv.DictReader(open(DATA / name, encoding="utf-8")))


def f(x):
    return float(x)


def short(name):
    repl = {
        "Electric Charges and Fields": "Charges & Fields",
        "Electrostatic Potential and Capacitance": "Potential & Capacitance",
        "Current Electricity": "Current Electricity",
        "Moving Charges and Magnetism": "Moving Charges & Mag.",
        "Magnetism and Matter": "Magnetism & Matter",
        "Electromagnetic Induction": "EM Induction",
        "Alternating Current": "Alternating Current",
        "Electromagnetic Waves": "EM Waves",
        "Ray Optics and Optical Instruments": "Ray Optics",
        "Wave Optics": "Wave Optics",
        "Dual Nature of Radiation and Matter": "Dual Nature",
        "Atoms": "Atoms",
        "Nuclei": "Nuclei",
        "Semiconductor Electronics: Materials, Devices and Simple Circuits":
            "Semiconductor Devices",
    }
    return repl.get(name, name)


def style(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#e0e0e0", linewidth=0.7)
    ax.set_axisbelow(True)
    ax.tick_params(colors=SLATE, labelsize=9)


def fig_roi_ranking():
    rows = load("roi_primary_ranking.csv")
    rows.sort(key=lambda r: int(r["rank"]))
    labels = [f"C{r['chapter_no']} {short(r['chapter_name'])}" for r in rows][::-1]
    roi = [f(r["incremental_roi"]) for r in rows][::-1]
    tiers = [r["tier"] for r in rows][::-1]
    colors = [PINK if t in ("Tier A", "Tier B") else (SLATE if t in ("Tier C", "Tier D") else GREY)
              for t in tiers]
    fig, ax = plt.subplots(figsize=(8.6, 5.2), dpi=200)
    bars = ax.barh(labels, roi, color=colors, height=0.68)
    for b, v in zip(bars, roi):
        ax.text(v + 0.006, b.get_y() + b.get_height() / 2, f"{v:.2f}",
                va="center", fontsize=8, color=SLATE)
    ax.set_xlabel("Incremental ROI  (probability-adjusted marks per additional hour)",
                  fontsize=9, color=SLATE)
    ax.set_title("Primary ROI ranking - intermediate starting ability, strong board readiness",
                 fontsize=11, color=SLATE, pad=12)
    style(ax)
    ax.set_xlim(0, max(roi) * 1.16)
    fig.tight_layout()
    fig.savefig(OUT / "fig_roi_ranking.png")
    plt.close(fig)


def fig_exposure_streams():
    rows = load("chapter_exposure_by_stream.csv")
    x = np.arange(len(rows))
    fig, ax = plt.subplots(figsize=(9.2, 4.6), dpi=200)
    w = 0.2
    ax.bar(x - 1.5 * w, [f(r["stream_A_historical_counts_recency"]) for r in rows], w,
           label="A historical counts (2017-26, recency)", color=LIGHT)
    ax.bar(x - 0.5 * w, [f(r["stream_B_mtg_marks_10yr"]) for r in rows], w,
           label="B MTG marks aggregate", color=PINK)
    ax.bar(x + 0.5 * w, [f(r["stream_C_official_sqp"]) for r in rows], w,
           label="C official SQP 2026-27", color=SLATE)
    ax.bar(x + 1.5 * w, [f(r["exposure_marks_2027"]) for r in rows], w,
           label="Reconciled + deletion-adjusted", color=GREY)
    ax.set_xticks(x)
    ax.set_xticklabels([f"C{r['chapter_no']}" for r in rows], fontsize=8)
    ax.set_ylabel("Expected marks in a 70-mark paper", fontsize=9, color=SLATE)
    ax.set_title("Chapter exposure: three evidence streams and the reconciled estimate",
                 fontsize=11, color=SLATE, pad=12)
    ax.legend(fontsize=7.5, frameon=False, ncol=2)
    style(ax)
    fig.tight_layout()
    fig.savefig(OUT / "fig_exposure_streams.png")
    plt.close(fig)


def fig_scatter():
    rows = load("roi_primary_ranking.csv")
    fig, ax = plt.subplots(figsize=(7.4, 4.9), dpi=200)
    for r in rows:
        x, y = f(r["additional_hours"]), f(r["additional_marks"])
        ax.scatter(x, y, s=70, color=PINK if int(r["rank"]) <= 5 else SLATE, zorder=3)
        ax.annotate(f"C{r['chapter_no']}", (x, y), textcoords="offset points",
                    xytext=(6, 4), fontsize=8, color=SLATE)
    xs = np.linspace(0, max(f(r["additional_hours"]) for r in rows) * 1.1, 50)
    for roi, ls in ((0.45, "--"), (0.30, ":"), (0.20, "-.")):
        ax.plot(xs, roi * xs, ls, color=GREY, linewidth=0.8)
        ax.text(xs[-1], roi * xs[-1], f"{roi:.2f} marks/h", fontsize=7, color=GREY,
                ha="right", va="bottom")
    ax.set_xlabel("Additional preparation hours to reach strong board readiness",
                  fontsize=9, color=SLATE)
    ax.set_ylabel("Additional probability-adjusted marks", fontsize=9, color=SLATE)
    ax.set_title("Gain versus cost by chapter (dashed lines are constant-ROI frontiers)",
                 fontsize=11, color=SLATE, pad=12)
    style(ax)
    fig.tight_layout()
    fig.savefig(OUT / "fig_gain_vs_cost.png")
    plt.close(fig)


def fig_monte_carlo():
    rows = load("monte_carlo_results.csv")
    rows.sort(key=lambda r: int(r["rank"]))
    labels = [f"C{r['chapter_no']}" for r in rows]
    p3 = [100 * f(r["p_top3"]) for r in rows]
    p5 = [100 * f(r["p_top5"]) for r in rows]
    x = np.arange(len(rows))
    fig, ax = plt.subplots(figsize=(8.4, 3.8), dpi=200)
    ax.bar(x - 0.2, p3, 0.4, label="P(rank in top 3)", color=PINK)
    ax.bar(x + 0.2, p5, 0.4, label="P(rank in top 5)", color=GREY)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("Probability (%)", fontsize=9, color=SLATE)
    ax.set_title("Monte Carlo ranking stability (20,000 draws)", fontsize=11,
                 color=SLATE, pad=12)
    ax.legend(fontsize=8, frameon=False)
    style(ax)
    fig.tight_layout()
    fig.savefig(OUT / "fig_monte_carlo.png")
    plt.close(fig)


def fig_periods():
    rows = load("historical_period_comparison.csv")
    x = np.arange(len(rows))
    fig, ax = plt.subplots(figsize=(8.8, 3.9), dpi=200)
    ax.plot(x, [f(r["last5_years_2022_2026"]) for r in rows], "-o", color=PINK,
            markersize=4, label="last 5 years (equal weight)")
    ax.plot(x, [f(r["last10_years_2017_2026"]) for r in rows], "-s", color=SLATE,
            markersize=3.5, label="last 10 years (equal weight)")
    ax.plot(x, [f(r["all_accessible_recency_weighted"]) for r in rows], "--", color=GREY,
            label="all accessible, 3-year half-life")
    ax.set_xticks(x)
    ax.set_xticklabels([f"C{r['chapter_no']}" for r in rows], fontsize=8)
    ax.set_ylabel("Implied marks per paper", fontsize=9, color=SLATE)
    ax.set_title("Historical period comparison (stream A, question-count shares)",
                 fontsize=11, color=SLATE, pad=12)
    ax.legend(fontsize=8, frameon=False)
    style(ax)
    fig.tight_layout()
    fig.savefig(OUT / "fig_periods.png")
    plt.close(fig)


def fig_choice_model():
    """Marks at stake by question format in the official SQP 2026-27."""
    formats = ["Section A\nMCQ / A-R\n(1 mark)", "Section B\nVSA\n(2 marks)",
               "Section C\nSA\n(3 marks)", "Section D\nCase-based\n(4 marks)",
               "Section E\nLong answer\n(5 marks)"]
    compulsory = [14, 6, 18, 8, 0]
    optional = [0, 4, 3, 0, 15]
    fig, ax = plt.subplots(figsize=(7.6, 3.6), dpi=200)
    x = np.arange(len(formats))
    ax.bar(x, compulsory, 0.55, label="compulsory marks", color=SLATE)
    ax.bar(x, optional, 0.55, bottom=compulsory, label="marks in internal-choice slots",
           color=PINK)
    for i, (c, o) in enumerate(zip(compulsory, optional)):
        ax.text(i, c + o + 0.4, f"{c + o}", ha="center", fontsize=8, color=SLATE)
    ax.set_xticks(x)
    ax.set_xticklabels(formats, fontsize=7.5)
    ax.set_ylabel("Marks", fontsize=9, color=SLATE)
    ax.set_title("Official SQP 2026-27: where marks sit, and where choice sits",
                 fontsize=11, color=SLATE, pad=12)
    ax.legend(fontsize=8, frameon=False)
    style(ax)
    fig.tight_layout()
    fig.savefig(OUT / "fig_choice_model.png")
    plt.close(fig)


def fig_sensitivity_heatmap():
    rows = load("sensitivity_analysis.csv")
    variants = list(dict.fromkeys(r["variant"] for r in rows))
    chapters = list(range(1, 15))
    grid = np.zeros((len(variants), 14))
    for i, v in enumerate(variants):
        for r in rows:
            if r["variant"] == v:
                grid[i, int(r["chapter_no"]) - 1] = int(r["rank"])
    fig, ax = plt.subplots(figsize=(8.4, 4.6), dpi=200)
    im = ax.imshow(grid, aspect="auto", cmap="RdPu", origin="upper")
    ax.set_xticks(range(14))
    ax.set_xticklabels([f"C{c}" for c in chapters], fontsize=8)
    ax.set_yticks(range(len(variants)))
    ax.set_yticklabels([v.replace("_", " ") for v in variants], fontsize=7)
    for i in range(len(variants)):
        for j in range(14):
            ax.text(j, i, int(grid[i, j]), ha="center", va="center", fontsize=6.5,
                    color="white" if grid[i, j] <= 5 else SLATE)
    ax.set_title("Rank under 16 sensitivity variants (1 = best ROI)", fontsize=11,
                 color=SLATE, pad=12)
    fig.colorbar(im, ax=ax, shrink=0.8, label="rank")
    fig.tight_layout()
    fig.savefig(OUT / "fig_sensitivity.png")
    plt.close(fig)


def fig_sqp_chapters():
    rows = load("chapter_exposure_by_stream.csv")
    fig, ax = plt.subplots(figsize=(7.8, 4.0), dpi=200)
    ax.bar([f"C{r['chapter_no']}" for r in rows],
           [f(r["stream_C_official_sqp"]) for r in rows], color=PINK, width=0.6)
    for i, r in enumerate(rows):
        ax.text(i, f(r["stream_C_official_sqp"]) + 0.12, f"{f(r['stream_C_official_sqp']):.1f}",
                ha="center", fontsize=7.5, color=SLATE)
    ax.set_ylabel("Marks (choice-aware)", fontsize=9, color=SLATE)
    ax.set_title("Official CBSE SQP 2026-27: chapter marks after choice-aware attribution "
                 "(sums to 70)", fontsize=10.5, color=SLATE, pad=12)
    style(ax)
    fig.tight_layout()
    fig.savefig(OUT / "fig_sqp_chapters.png")
    plt.close(fig)


if __name__ == "__main__":
    fig_roi_ranking()
    fig_exposure_streams()
    fig_scatter()
    fig_monte_carlo()
    fig_periods()
    fig_choice_model()
    fig_sensitivity_heatmap()
    fig_sqp_chapters()
    print("figures written to", OUT.relative_to(ROOT))
    for p in sorted(OUT.glob("*.png")):
        print("  ", p.name, p.stat().st_size // 1024, "KB")
