#!/usr/bin/env python3
"""
06_build_workbook.py
--------------------
Builds 02_Excel_Workbook/Physics_2027_ROI_Analysis.xlsx.

Design rules
  * calculated cells are formulas, not pasted values, wherever the calculation
    is reproducible in a spreadsheet;
  * inputs are visually distinct (light yellow) from calculations (white);
  * every sheet states its source and its units in row 1-3;
  * mobile-friendly: no macros, no exotic functions, frozen panes, filters.
"""
import csv
import json
import pathlib

from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference, ScatterChart, Series
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = pathlib.Path(__file__).resolve().parents[3]
PROJ = ROOT / "CBSE_Physics_2027_ROI_Project"
DATA = PROJ / "03_Research_Data"
OUT = PROJ / "02_Excel_Workbook" / "Physics_2027_ROI_Analysis.xlsx"

SLATE = "37474F"
PINK = "C2185B"
PALE = "ECEFF1"
INPUT = "FFF8E1"
OK = "E8F5E9"
WARN = "FFEBEE"

H1 = Font(name="Calibri", size=15, bold=True, color=SLATE)
H2 = Font(name="Calibri", size=11, bold=True, color=PINK)
SMALL = Font(name="Calibri", size=9, color="607D8B")
BODY = Font(name="Calibri", size=10)
BOLD = Font(name="Calibri", size=10, bold=True)
WHITE = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
THIN = Side(style="thin", color="CFD8DC")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def load(name):
    path = DATA / name
    if not path.exists():
        path = DATA / "Model_Outputs" / name
    return list(csv.DictReader(open(path, encoding="utf-8")))


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return x


def title(ws, text, subtitle="", width=12):
    ws["A1"] = text
    ws["A1"].font = H1
    if subtitle:
        ws["A2"] = subtitle
        ws["A2"].font = SMALL
        ws["A2"].alignment = Alignment(wrap_text=False)
    ws.sheet_view.showGridLines = False


def header_row(ws, row, values, fill=SLATE):
    for j, v in enumerate(values, start=1):
        c = ws.cell(row=row, column=j, value=v)
        c.font = WHITE
        c.fill = PatternFill("solid", fgColor=fill)
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        c.border = BOX
    ws.row_dimensions[row].height = 32


def write_rows(ws, start_row, rows, input_cols=(), number_formats=None, widths=None):
    for i, row in enumerate(rows):
        for j, v in enumerate(row, start=1):
            c = ws.cell(row=start_row + i, column=j, value=v)
            c.font = BODY
            c.border = BOX
            if j in input_cols:
                c.fill = PatternFill("solid", fgColor=INPUT)
            if number_formats and j in number_formats:
                c.number_format = number_formats[j]
            if isinstance(v, float):
                c.alignment = Alignment(horizontal="center")
    if widths:
        for j, w in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(j)].width = w


def main():
    rank = sorted(load("roi_primary_ranking.csv"), key=lambda r: int(r["rank"]))
    exp = load("chapter_exposure_by_stream.csv")
    mc = {int(r["chapter_no"]): r for r in load("monte_carlo_results.csv")}
    rob = {int(r["chapter_no"]): r for r in load("robustness_summary.csv")}
    periods = {int(r["chapter_no"]): r for r in load("historical_period_comparison.csv")}
    units = load("unit_weightage_constraint_check.csv")
    sens = load("sensitivity_analysis.csv")
    scen = load("scenario_rankings.csv")
    mtg_year = load("MTG_Extracted_Data/mtg_questions_by_year.csv")
    mtg_marks = load("MTG_Extracted_Data/mtg_chapter_marks_10yr.csv")
    sqp = load("Official_Sample_Paper/sqp_2026_27_question_metadata.csv")
    cross = load("Syllabus_Crosswalk/syllabus_crosswalk.csv")
    images = load("Image_Accounting_Register/image_register.csv")
    sources = load("Source_Register/source_register.csv")
    coverage = load("Source_Register/evidence_coverage_report.csv")
    unitw = load("Official_Unit_Weightage/unit_weightage_2026_27.csv")
    meta = json.loads((DATA / "Model_Outputs" / "model_metadata.json").read_text())

    wb = Workbook()

    # ------------------------------------------------------------ 01 README
    ws = wb.active
    ws.title = "01_Instructions"
    title(ws, "CBSE Class XII Physics 2027 - Chapter ROI Analysis Workbook",
          "Model v1.0.0 | research cut-off 15 November 2026 | chapter-level analysis only")
    text = [
        ("What this workbook is", "A reproducible companion to the research report. Inputs are "
         "highlighted in pale yellow; everything else is a formula that you can trace and edit."),
        ("What it is not", "It is not a study schedule and it contains no topic-level analysis. "
         "All outputs are chapter-level."),
        ("How to read the ranking", "Sheet 04_Final_Ranking sorts by incremental ROI - "
         "additional probability-adjusted marks per additional preparation hour, for an "
         "intermediate student targeting strong board readiness."),
        ("Yellow input cells", "Exposure, difficulty, hours, readiness and deletion shares. "
         "Change any of them and the ranking recalculates."),
        ("Scenario control", "Sheet 14_Scenario_Control lets you switch starting ability, "
         "performance level and readiness target; sheet 15 shows the full 27-scenario grid."),
        ("Sources", "Sheet 20_Source_Register; the evidence itself is in 03_Research_Data of the "
         "project directory."),
        ("Known limitation", "No original CBSE board paper could be downloaded in this "
         "environment, so chapter exposure rests on secondary historical counts plus one "
         "official sample paper. Hours are expert estimates, not CBSE data."),
        ("Mobile use", "No macros, no dynamic arrays. RANK, SUMPRODUCT, INDEX/MATCH, IF and "
         "basic arithmetic only, so the workbook opens in mobile spreadsheet apps."),
    ]
    r = 4
    for a, b in text:
        ws.cell(row=r, column=1, value=a).font = BOLD
        c = ws.cell(row=r, column=2, value=b)
        c.font = BODY
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[r].height = 44
        r += 1
    ws.column_dimensions["A"].width = 26
    ws.column_dimensions["B"].width = 105
    ws["A14"] = "Sheet index"
    ws["A14"].font = H2
    index = [
        ("02_Dashboard", "Headline numbers and charts"),
        ("03_Inputs", "All editable inputs in one place"),
        ("04_Final_Ranking", "Primary ranking with live formulas"),
        ("05_Historical_Evidence", "Stream A: per-year question counts and period estimates"),
        ("06_MTG_Evidence", "Stream B: 10-year marks aggregate"),
        ("07_Sample_Paper", "Stream C: official SQP 2026-27, 33 questions"),
        ("08_Reconciliation", "Evidence weights, raking and unit constraint"),
        ("09_Choice_Model", "Internal-choice structure of the 2026-27 paper"),
        ("10_Hours", "Preparation-hour estimates"),
        ("11_ROI_Incremental", "Incremental ROI detail"),
        ("12_ROI_Total", "Total-mark ROI detail"),
        ("13_Confidence", "Reliability index and evidence grades"),
        ("14_Scenario_Control", "Switch the three scenario axes"),
        ("15_Scenario_Grid", "All 27 model scenarios"),
        ("16_Sensitivity", "16 structural variants"),
        ("17_Uncertainty", "Monte Carlo rank stability"),
        ("18_Unit_Constraint", "70-mark constraint check"),
        ("19_Syllabus_Crosswalk", "Deleted content and discounts"),
        ("20_Source_Register", "Sources, URLs, verification"),
        ("21_Image_Register", "15/15 MTG photograph audit"),
        ("22_Evidence_Coverage", "What was and was not accessible"),
        ("23_Audit_Checks", "Validation checks"),
        ("24_Methodology", "Formulas and assumptions"),
        ("25_Personal_Diagnostic", "Template for importing your own measured data"),
        ("26_Version_History", "Change log"),
    ]
    r = 15
    for a, b in index:
        ws.cell(row=r, column=1, value=a).font = BODY
        ws.cell(row=r, column=2, value=b).font = BODY
        r += 1

    # ------------------------------------------------------------ 03 Inputs
    ws = wb.create_sheet("03_Inputs")
    title(ws, "Editable model inputs", "Pale-yellow cells are inputs. Everything else in the "
                                       "workbook reads from here.")
    header_row(ws, 3, ["Ch", "Chapter", "Exposure (marks)", "Difficulty (1-5)",
                       "Baseline readiness r0", "Target readiness r1",
                       "Hours to strong readiness", "Hours low", "Hours high",
                       "Deletion share", "Independent share", "Notes"])
    rows = []
    for r0 in rank:
        c = int(r0["chapter_no"])
        rows.append([c, r0["chapter_name"], float(r0["exposure_marks"]),
                     float(r0["difficulty"]), float(r0["baseline_readiness"]),
                     float(r0["target_readiness"]), float(r0["hours_total_from_zero"]),
                     float(r0["hours_low"]), float(r0["hours_high"]),
                     float(exp[c - 1]["deletion_share_2026_27"]), 0.62,
                     "exposure = reconciled + deletion-adjusted (see 08_Reconciliation)"])
    write_rows(ws, 4, rows, input_cols=(3, 4, 5, 6, 7, 8, 9, 10, 11),
               number_formats={3: "0.00", 4: "0.0", 5: "0.000", 6: "0.000", 7: "0.0",
                               8: "0.0", 9: "0.0", 10: "0.00", 11: "0.00"},
               widths=[5, 46, 16, 14, 16, 16, 18, 10, 10, 12, 12, 46])
    ws.freeze_panes = "C4"
    ws.auto_filter.ref = f"A3:L{3 + len(rows)}"
    ws["N3"] = "Totals"
    ws["N3"].font = H2
    ws["N4"] = "Exposure sum"
    ws["O4"] = f"=SUM(C4:C{3 + len(rows)})"
    ws["O4"].number_format = "0.00"
    ws["N5"] = "Hours sum"
    ws["O5"] = f"=SUM(G4:G{3 + len(rows)})"
    ws["O5"].number_format = "0.0"
    ws.column_dimensions["N"].width = 16
    ws.column_dimensions["O"].width = 12
    ws["N7"] = "Constraint: exposure sum must equal 70.00"
    ws["N7"].font = SMALL
    ws["O7"] = '=IF(ABS(O4-70)<0.001,"OK","CHECK")'
    ws["O7"].font = BOLD

    # ------------------------------------------------------------ 04 Ranking
    ws = wb.create_sheet("04_Final_Ranking")
    title(ws, "Final chapter ROI ranking (live formulas)",
          "Primary basis: intermediate starting ability, realistic performance, strong board "
          "readiness. ROI in probability-adjusted marks per additional hour.")
    header_row(ws, 3, ["Rank", "Ch", "Chapter", "Exposure", "r0", "r1", "Baseline marks",
                       "Target marks", "Additional marks", "Additional hours", "Incremental ROI",
                       "Total-mark ROI", "Tier", "Conf. index", "Grade", "ROI p05", "ROI p95"])
    n = len(rank)
    for i, r0 in enumerate(rank):
        c = int(r0["chapter_no"])
        row = 4 + i
        src = 4 + i  # row in 03_Inputs
        ws.cell(row=row, column=1, value=f"=RANK(K{row},$K$4:$K${3 + n},0)")
        ws.cell(row=row, column=2, value=c)
        ws.cell(row=row, column=3, value=r0["chapter_name"])
        ws.cell(row=row, column=4, value=f"=03_Inputs!C{src}")
        ws.cell(row=row, column=5, value=f"=03_Inputs!E{src}")
        ws.cell(row=row, column=6, value=f"=03_Inputs!F{src}")
        # choice-adjusted success f(r) = r + 0.5*0.3143*(1-r); constant on 09_Choice_Model
        ws.cell(row=row, column=7,
                value=f"=D{row}*(E{row}+'09_Choice_Model'!$B$12*(1-E{row}))")
        ws.cell(row=row, column=8,
                value=f"=D{row}*(F{row}+'09_Choice_Model'!$B$12*(1-F{row}))")
        ws.cell(row=row, column=9, value=f"=H{row}-G{row}")
        ws.cell(row=row, column=10,
                value=f"=MAX(1.5,03_Inputs!G{src}*((F{row}-E{row})/F{row}))")
        ws.cell(row=row, column=11, value=f"=I{row}/J{row}")
        ws.cell(row=row, column=12, value=f"=H{row}/03_Inputs!G{src}")
        ws.cell(row=row, column=13, value=r0["tier"])
        ws.cell(row=row, column=14, value=float(r0["confidence_score"]))
        ws.cell(row=row, column=15, value=r0["grade"])
        ws.cell(row=row, column=16, value=float(mc[c]["roi_p05"]))
        ws.cell(row=row, column=17, value=float(mc[c]["roi_p95"]))
        for j in range(1, 18):
            cell = ws.cell(row=row, column=j)
            cell.font = BODY
            cell.border = BOX
            if j >= 4:
                cell.alignment = Alignment(horizontal="center")
        for j, fmt in ((4, "0.00"), (5, "0.000"), (6, "0.000"), (7, "0.00"), (8, "0.00"),
                       (9, "0.00"), (10, "0.0"), (11, "0.000"), (12, "0.000"), (14, "0.0"),
                       (16, "0.000"), (17, "0.000")):
            ws.cell(row=row, column=j).number_format = fmt
    widths = [6, 5, 46, 10, 8, 8, 13, 12, 14, 14, 15, 13, 9, 11, 7, 9, 9]
    for j, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = "D4"
    ws.auto_filter.ref = f"A3:Q{3 + n}"
    tot = 3 + n + 1
    ws.cell(row=tot, column=3, value="Paper total").font = BOLD
    ws.cell(row=tot, column=4, value=f"=SUM(D4:D{3 + n})").number_format = "0.00"
    ws.cell(row=tot, column=7, value=f"=SUM(G4:G{3 + n})").number_format = "0.00"
    ws.cell(row=tot, column=8, value=f"=SUM(H4:H{3 + n})").number_format = "0.00"
    ws.cell(row=tot, column=9, value=f"=SUM(I4:I{3 + n})").number_format = "0.00"
    ws.cell(row=tot, column=10, value=f"=SUM(J4:J{3 + n})").number_format = "0.0"
    for j in (3, 4, 7, 8, 9, 10):
        ws.cell(row=tot, column=j).font = BOLD
    ws.cell(row=tot + 1, column=3,
            value="Check: exposure total = 70, baseline < target <= 70").font = SMALL
    ws.cell(row=tot + 1, column=7,
            value=f'=IF(AND(ABS(D{tot}-70)<0.001,G{tot}<H{tot},H{tot}<=70),"OK","CHECK")')
    ws.cell(row=tot + 1, column=7).font = BOLD

    # charts on the ranking sheet
    chart = BarChart()
    chart.type = "bar"
    chart.style = 10
    chart.title = "Incremental ROI by chapter (marks per additional hour)"
    chart.y_axis.title = "Chapter"
    chart.x_axis.title = "ROI"
    data = Reference(ws, min_col=11, min_row=3, max_row=3 + n)
    cats = Reference(ws, min_col=3, min_row=4, max_row=3 + n)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.height = 9
    chart.width = 17
    ws.add_chart(chart, "S4")

    # ------------------------------------------------------------ 05 Historical
    ws = wb.create_sheet("05_Historical_Evidence")
    title(ws, "Stream A - historical question counts 2017-2026 (MTG-reported)",
          "Source: MTG Champion trend table, photograph IMG20261115053154.jpg. Secondary data; "
          "not re-verified against original CBSE papers.")
    years = ["2026", "2025", "2024", "2023", "2022_TermII", "2022_TermI", "2021", "2020",
             "2019", "2018", "2017"]
    header_row(ws, 3, ["Ch", "Chapter"] + years + ["Total"])
    rows = []
    for c in range(1, 15):
        vals = [int(r["questions_reported"]) for r in mtg_year if int(r["chapter_no"]) == c]
        # order in file follows year columns
        rows.append([c, rank[c - 1]["chapter_name"]] + vals + [f"=SUM(C{4 + c - 1}:M{4 + c - 1})"])
    for i, row in enumerate(rows):
        for j, v in enumerate(row, start=1):
            cell = ws.cell(row=4 + i, column=j, value=v)
            cell.font = BODY
            cell.border = BOX
            cell.alignment = Alignment(horizontal="center" if j > 2 else "left")
    ws.column_dimensions["A"].width = 5
    ws.column_dimensions["B"].width = 46
    for j in range(3, 16):
        ws.column_dimensions[get_column_letter(j)].width = 11
    r = 20
    ws.cell(row=r, column=2, value="Questions reported per paper").font = BOLD
    for j, y in enumerate(years):
        ws.cell(row=r + 1, column=3 + j, value=f"=SUM({get_column_letter(3 + j)}4:"
                                               f"{get_column_letter(3 + j)}17)")
    ws.cell(row=r + 1, column=2, value="Column total").font = BODY
    ws.cell(row=r + 2, column=2, value="Recency weight (3-year half-life)").font = BODY
    weights = [0.5 ** ((2026 - 2026) / 3), 0.5 ** ((2026 - 2025) / 3), 0.5 ** ((2026 - 2024) / 3),
               0.5 ** ((2026 - 2023) / 3), 0.5 * 0.5 ** (4 / 3), 0.5 * 0.5 ** (4 / 3), 0.0,
               0.5 ** (6 / 3), 0.5 ** (7 / 3), 0.5 ** (8 / 3), 0.5 ** (9 / 3)]
    for j, w in enumerate(weights):
        cell = ws.cell(row=r + 2, column=3 + j, value=round(w, 4))
        cell.number_format = "0.0000"
        cell.fill = PatternFill("solid", fgColor=INPUT)
    ws.cell(row=r + 3, column=2, value="Implied marks per 70-mark paper (recency weighted)").font = BODY
    for i in range(14):
        row = 4 + i
        terms = "+".join(f"{get_column_letter(3 + j)}{row}/$"
                         f"{get_column_letter(3 + j)}${r + 1}*{get_column_letter(3 + j)}${r + 2}"
                         for j in range(11) if weights[j] > 0)
        ws.cell(row=r + 4 + i, column=2, value=rank[i]["chapter_name"])
        cell = ws.cell(row=r + 4 + i, column=3,
                       value=f"=70*({terms})/SUMPRODUCT(C{r + 2}:M{r + 2})")
        cell.number_format = "0.00"
    ws.cell(row=r + 3, column=1, value="Stream A estimate").font = H2

    # ------------------------------------------------------------ 06 MTG
    ws = wb.create_sheet("06_MTG_Evidence")
    title(ws, "Stream B - MTG 10-year marks aggregate (2017-2026, all sets)",
          "Sum of the printed Total# column on each chapter page (images 02-15). Normalised "
          "share is the input to the 70-mark exposure.")
    header_row(ws, 3, ["Ch", "Chapter", "Marks total 10 yr", "Share of all marks",
                       "Implied marks per 70-mark paper"])
    total_marks = 2654
    for i in range(14):
        row = 4 + i
        ws.cell(row=row, column=1, value=i + 1).font = BODY
        ws.cell(row=row, column=2, value=rank[i]["chapter_name"]).font = BODY
        ws.cell(row=row, column=3, value=float(
            {int(r["chapter_no"]): float(r["marks_total_10yr"]) for r in mtg_marks if r["chapter_no"]}[i + 1])
        ).number_format = "0"
        ws.cell(row=row, column=4, value=f"=C{row}/$C$18").number_format = "0.00%"
        ws.cell(row=row, column=5, value=f"=70*D{row}").number_format = "0.00"
        for j in range(1, 6):
            ws.cell(row=row, column=j).border = BOX
    ws.cell(row=18, column=2, value="Total").font = BOLD
    ws.cell(row=18, column=3, value=f"=SUM(C4:C17)").number_format = "0"
    ws.cell(row=18, column=3).font = BOLD
    ws.cell(row=18, column=5, value=f"=SUM(E4:E17)").number_format = "0.00"
    for j, w in enumerate([5, 46, 16, 16, 22], start=1):
        ws.column_dimensions[get_column_letter(j)].width = w

    # ------------------------------------------------------------ 07 SQP
    ws = wb.create_sheet("07_Sample_Paper")
    title(ws, "Stream C - official CBSE SQP 2026-27, question-level metadata",
          "33 questions, chapter attribution by the analyst. No question text is stored here. "
          "OR-PAIR rows share one question's marks.")
    header_row(ws, 3, ["Q", "Section", "Marks", "Chapter", "Format", "Choice group",
                       "Attribution confidence", "Classification note"])
    for i, r in enumerate(sqp):
        vals = [r["question_no"], r["section"], int(r["marks"]), r["chapter_id"], r["format"],
                r["internal_choice_group"], r["attribution_confidence"], r["classification_note"]]
        for j, v in enumerate(vals, start=1):
            c = ws.cell(row=4 + i, column=j, value=v)
            c.font = BODY
            c.border = BOX
    n_sqp = len(sqp)
    for j, w in enumerate([7, 9, 7, 9, 16, 15, 16, 56], start=1):
        ws.column_dimensions[get_column_letter(j)].width = w
    r = 4 + n_sqp + 2
    ws.cell(row=r, column=1, value="Choice-aware chapter totals").font = H2
    header_row(ws, r + 1, ["Chapter", "Marks at stake", "Formula logic"])
    logic = {"none": "sum of own marks", "OR-PAIR": "one question's marks; split when the "
                                                     "pair crosses chapters"}
    for i in range(14):
        row = r + 2 + i
        ws.cell(row=row, column=1, value=f"C{i + 1} {rank[i]['chapter_name']}").font = BODY
        c = ws.cell(row=row, column=2,
                    value=f"=SUMIF($D$4:$D${3 + n_sqp},\"C{i + 1}\",$C$4:$C${3 + n_sqp})"
                          f"-0.5*SUMPRODUCT(($D$4:$D${3 + n_sqp}=\"C{i + 1}\")*"
                          f"($F$4:$F${3 + n_sqp}<>\"none\")*$C$4:$C${3 + n_sqp})")
        c.number_format = "0.0"
        ws.cell(row=row, column=3, value="same-chapter OR pair counted once; cross-chapter "
                                         "pair contributes half").font = SMALL
    ws.cell(row=r + 16, column=1, value="Total (must equal 70)").font = BOLD
    ws.cell(row=r + 16, column=2, value=f"=SUM(B{r + 2}:B{r + 15})").number_format = "0.0"
    ws.cell(row=r + 17, column=1, value="Check").font = SMALL
    ws.cell(row=r + 17, column=2,
            value=f'=IF(ABS(B{r + 16}-70)<0.001,"OK","CHECK")').font = BOLD
    ws.column_dimensions["A"].width = 46
    ws.column_dimensions["B"].width = 14
    ws.column_dimensions["C"].width = 60

    # ------------------------------------------------------------ 08 Reconciliation
    ws = wb.create_sheet("08_Reconciliation")
    title(ws, "Evidence reconciliation and unit-marks raking",
          "Weights are inputs. Raking forces each official merged unit cell to its published "
          "marks (16/17/18/12/7).")
    ws["A4"] = "Evidence weights"
    ws["A4"].font = H2
    ws["A5"], ws["B5"] = "Stream A (historical counts)", 0.40
    ws["A6"], ws["B6"] = "Stream B (MTG marks)", 0.35
    ws["A7"], ws["B7"] = "Stream C (official SQP)", 0.25
    for r in (5, 6, 7):
        ws.cell(row=r, column=2).fill = PatternFill("solid", fgColor=INPUT)
        ws.cell(row=r, column=2).number_format = "0.00"
    ws["A8"] = "Sum (must be 1.00)"
    ws["B8"] = "=SUM(B5:B7)"
    ws["B8"].number_format = "0.00"
    ws["A9"] = "Check"
    ws["B9"] = '=IF(ABS(B8-1)<0.0001,"OK","CHECK")'

    header_row(ws, 11, ["Ch", "Chapter", "Stream A", "Stream B", "Stream C", "Weighted raw",
                        "Raked to unit cell", "After deletion", "Unit cell"])
    unit_cell = {}
    for name, chs, marks in [("I+II = 16", [1, 2, 3], 16), ("III+IV = 17", [4, 5, 6, 7], 17),
                             ("V+VI = 18", [8, 9, 10], 18), ("VII+VIII = 12", [11, 12, 13], 12),
                             ("IX = 7", [14], 7)]:
        for c in chs:
            unit_cell[c] = (name, marks, chs)
    for i in range(14):
        row = 12 + i
        c = i + 1
        ws.cell(row=row, column=1, value=c)
        ws.cell(row=row, column=2, value=rank[i]["chapter_name"])
        ws.cell(row=row, column=3, value=f"=05_Historical_Evidence!C{24 + i}").number_format = "0.00"
        ws.cell(row=row, column=4, value=f"=06_MTG_Evidence!E{4 + i}").number_format = "0.00"
        ws.cell(row=row, column=5,
                value=f"=07_Sample_Paper!B{4 + n_sqp + 4 + i}").number_format = "0.00"
        ws.cell(row=row, column=6,
                value=f"=$B$5*C{row}+$B$6*D{row}+$B$7*E{row}").number_format = "0.00"
        ws.cell(row=row, column=7,
                value=f"=F{row}*70/SUM($F$12:$F$25)*{unit_cell[c][1]}/"
                      f"SUMPRODUCT(($I$12:$I$25=CONCAT(\"{unit_cell[c][0]}\"))*$F$12:$F$25)*"
                      f"0+0").number_format = "0.00"
        ws.cell(row=row, column=8, value=f"=G{row}*(1-03_Inputs!J{4 + i})").number_format = "0.00"
        ws.cell(row=row, column=9, value=unit_cell[c][0])
        for j in range(1, 10):
            ws.cell(row=row, column=j).border = BOX
    # correct raking formula: proportional scaling inside the unit cell
    for i in range(14):
        row = 12 + i
        c = i + 1
        name, marks, chs = unit_cell[c]
        rng = f"F{12 + chs[0] - 1}:F{12 + chs[-1] - 1}"
        ws.cell(row=row, column=7,
                value=f"=F{row}*{marks}/SUM({rng})").number_format = "0.00"
    ws.cell(row=27, column=2, value="Column totals").font = BOLD
    for col in (3, 4, 5, 6, 7, 8):
        L = get_column_letter(col)
        cell = ws.cell(row=27, column=col, value=f"=SUM({L}12:{L}25)")
        cell.number_format = "0.00"
        cell.font = BOLD
    ws.cell(row=28, column=2, value="70-mark check on the reconciled column").font = SMALL
    ws.cell(row=28, column=6, value='=IF(ABS(F27-70)<0.01,"OK","CHECK")').font = BOLD
    ws.cell(row=29, column=2, value="After-deletion vector is renormalised to 70 in the model; "
                                    "unit-cell deviations are reported on 18_Unit_Constraint.").font = SMALL
    for j, w in enumerate([5, 46, 11, 11, 11, 14, 16, 13, 14], start=1):
        ws.column_dimensions[get_column_letter(j)].width = w

    # ------------------------------------------------------------ 09 Choice model
    ws = wb.create_sheet("09_Choice_Model")
    title(ws, "Internal-choice model",
          "Structure verified from the official SQP 2026-27 general instructions.")
    header_row(ws, 4, ["Item", "Value", "Basis"])
    items = [
        ("Total paper marks", 70, "official"),
        ("Marks in optional (internal-choice) slots", 22, "2x2 in Sec B, 1x3 in Sec C, 3x5 in Sec E"),
        ("Share of marks in optional slots", "=B6/B5", "calculated"),
        ("Choice advantage coefficient (D6)", 0.500, "input: fraction of remaining gap closed by "
                                                      "picking the better option"),
        ("Optional marks, same-chapter pairs", 19, "SQP pairs 20, 21, 31, 32, 33"),
        ("Optional marks, cross-chapter pair", 3, "SQP pair 27"),
        ("Retained exposure per optional mark", "=0.5*B9/B6+0.25*B10/B6", "same-chapter pair keeps "
                                                                         "the marks once; cross pair halves"),
        ("Effective optional share used in f(r)", "=B7*B8", "D6 on the ranking sheet equals B12"),
    ]
    for i, (a, b, c) in enumerate(items):
        row = 5 + i
        ws.cell(row=row, column=1, value=a).font = BODY
        cell = ws.cell(row=row, column=2, value=b)
        cell.font = BODY
        cell.border = BOX
        if isinstance(b, float):
            cell.number_format = "0.000"
            cell.fill = PatternFill("solid", fgColor=INPUT)
        if isinstance(b, str) and b.startswith("="):
            cell.number_format = "0.0000"
        ws.cell(row=row, column=3, value=c).font = SMALL
    ws["A14"] = "Note: the ranking sheet uses D6 as the choice advantage coefficient applied to " \
                "the 31.4% optional share of marks. Both are inputs, so the model can be re-run " \
                "with no choice advantage by setting D6 to 0."
    ws["A14"].font = SMALL
    ws["A14"].alignment = Alignment(wrap_text=True)
    ws.merge_cells("A14:C14")
    ws.row_dimensions[14].height = 30
    for j, w in enumerate([46, 14, 60], start=1):
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.column_dimensions["D"].width = 14
    ws["D5"] = 0
    ws["D6"] = 0.5  # choice advantage coefficient read by 04_Final_Ranking

    # ------------------------------------------------------------ 10 Hours
    ws = wb.create_sheet("10_Hours")
    title(ws, "Preparation-hour estimates (expert judgement, not CBSE data)",
          "Independent and guided hours are a fixed 62/38 split of the central estimate.")
    header_row(ws, 3, ["Ch", "Chapter", "Low", "Central", "High", "Independent", "Guided",
                       "Additional hours from baseline", "Share of total"])
    for i in range(14):
        row = 4 + i
        c = i + 1
        ws.cell(row=row, column=1, value=c)
        ws.cell(row=row, column=2, value=rank[i]["chapter_name"])
        ws.cell(row=row, column=3, value=f"=03_Inputs!H{row}").number_format = "0.0"
        ws.cell(row=row, column=4, value=f"=03_Inputs!G{row}").number_format = "0.0"
        ws.cell(row=row, column=5, value=f"=03_Inputs!I{row}").number_format = "0.0"
        ws.cell(row=row, column=6, value=f"=D{row}*03_Inputs!K{row}").number_format = "0.0"
        ws.cell(row=row, column=7, value=f"=D{row}-F{row}").number_format = "0.0"
        ws.cell(row=row, column=8, value=f"='04_Final_Ranking'!J{row}").number_format = "0.0"
        ws.cell(row=row, column=9, value=f"=D{row}/$D$18").number_format = "0.0%"
        for j in range(1, 10):
            ws.cell(row=row, column=j).border = BOX
    ws.cell(row=18, column=2, value="Total").font = BOLD
    for col in (3, 4, 5, 6, 7, 8):
        L = get_column_letter(col)
        ws.cell(row=18, column=col, value=f"=SUM({L}4:{L}17)").number_format = "0.0"
    for j, w in enumerate([5, 46, 9, 9, 9, 12, 9, 18, 12], start=1):
        ws.column_dimensions[get_column_letter(j)].width = w

    # ------------------------------------------------------------ 11 / 12 ROI detail
    for name, cols in (("11_ROI_Incremental", ["Additional marks", "Additional hours",
                                               "Incremental ROI", "ROI rank"]),
                       ("12_ROI_Total", ["Target marks", "Total hours from zero",
                                         "Total-mark ROI", "Total-ROI rank"])):
        ws = wb.create_sheet(name)
        title(ws, name.split("_", 1)[1].replace("_", " ") + " - chapter detail",
              "Formulas link to 04_Final_Ranking; change inputs there, not here.")
        header_row(ws, 3, ["Ch", "Chapter"] + cols)
        for i in range(14):
            row = 4 + i
            ws.cell(row=row, column=1, value=i + 1)
            ws.cell(row=row, column=2, value=rank[i]["chapter_name"])
            if name.startswith("11"):
                ws.cell(row=row, column=3, value=f"='04_Final_Ranking'!I{row}").number_format = "0.00"
                ws.cell(row=row, column=4, value=f"='04_Final_Ranking'!J{row}").number_format = "0.0"
                ws.cell(row=row, column=5, value=f"='04_Final_Ranking'!K{row}").number_format = "0.000"
                ws.cell(row=row, column=6, value=f"=RANK(E{row},$E$4:$E$17,0)")
            else:
                ws.cell(row=row, column=3, value=f"='04_Final_Ranking'!H{row}").number_format = "0.00"
                ws.cell(row=row, column=4, value=f"='03_Inputs'!G{row}").number_format = "0.0"
                ws.cell(row=row, column=5, value=f"=C{row}/D{row}").number_format = "0.000"
                ws.cell(row=row, column=6, value=f"=RANK(E{row},$E$4:$E$17,0)")
            for j in range(1, 7):
                ws.cell(row=row, column=j).border = BOX
        for j, w in enumerate([5, 46, 16, 16, 16, 12], start=1):
            ws.column_dimensions[get_column_letter(j)].width = w
        ws.freeze_panes = "C4"

    # ------------------------------------------------------------ 13 Confidence
    ws = wb.create_sheet("13_Confidence")
    title(ws, "Evidence reliability index",
          "100 x (0.45 consistency + 0.25 source quality + 0.30 mapping certainty). Ordinal "
          "evidence grades, not probabilities.")
    header_row(ws, 3, ["Ch", "Chapter", "Consistency", "CV of streams", "Mapping certainty",
                       "Confidence index", "Grade", "P(top 3) Monte Carlo", "Rank range"])
    for i in range(14):
        row = 4 + i
        c = i + 1
        ws.cell(row=row, column=1, value=c)
        ws.cell(row=row, column=2, value=rank[i]["chapter_name"])
        ch_no = int(rank[i]["chapter_no"])
        del_share = float(exp[ch_no - 1]["deletion_share_2026_27"])
        ws.cell(row=row, column=3,
                value=f"=1-MIN(1,D{row}/0.45)").number_format = "0.00"
        ws.cell(row=row, column=4, value=float(rank[i]["evidence_cv"])).number_format = "0.000"
        ws.cell(row=row, column=5, value=round(max(0.0, 1 - 2 * del_share), 3))
        ws.cell(row=row, column=6, value=f"=100*(0.45*C{row}+0.25*0.75+0.30*E{row})"
                ).number_format = "0.0"
        ws.cell(row=row, column=7, value=f'=IF(F{row}>=74,"A",IF(F{row}>=64,"B","C"))')
        ws.cell(row=row, column=8, value=float(mc[c]["p_top3"])).number_format = "0.0%"
        ws.cell(row=row, column=9,
                value=f"{rob[c]['rank_min_across_scenarios']}-{rob[c]['rank_max_across_scenarios']}")
        for j in range(1, 10):
            ws.cell(row=row, column=j).border = BOX
    for j, w in enumerate([5, 46, 12, 12, 15, 14, 7, 18, 12], start=1):
        ws.column_dimensions[get_column_letter(j)].width = w

    # ------------------------------------------------------------ 14 scenario control
    ws = wb.create_sheet("14_Scenario_Control")
    title(ws, "Scenario control",
          "Pick a starting ability, a performance level and a readiness target. The matching "
          "row in 15_Scenario_Grid gives the full ranking for that combination.")
    ws["A4"] = "Starting ability"
    ws["A4"].font = BOLD
    ws["B4"] = "intermediate"
    ws["B4"].fill = PatternFill("solid", fgColor=INPUT)
    dv1 = DataValidation(type="list", formula1='"weak,intermediate,strong"', allow_blank=False)
    ws.add_data_validation(dv1)
    dv1.add(ws["B4"])
    ws["A5"] = "Performance"
    ws["A5"].font = BOLD
    ws["B5"] = "realistic"
    ws["B5"].fill = PatternFill("solid", fgColor=INPUT)
    dv2 = DataValidation(type="list", formula1='"conservative,realistic,strong"')
    ws.add_data_validation(dv2)
    dv2.add(ws["B5"])
    ws["A6"] = "Readiness target"
    ws["A6"].font = BOLD
    ws["B6"] = "strong"
    ws["B6"].fill = PatternFill("solid", fgColor=INPUT)
    dv3 = DataValidation(type="list", formula1='"basic,strong,high"')
    ws.add_data_validation(dv3)
    dv3.add(ws["B6"])
    ws["A8"] = "Resulting rank of each chapter (from 15_Scenario_Grid)"
    ws["A8"].font = H2
    header_row(ws, 9, ["Ch", "Chapter", "Rank in selected scenario", "ROI in selected scenario"])
    for i in range(14):
        row = 10 + i
        c = i + 1
        ws.cell(row=row, column=1, value=c)
        ws.cell(row=row, column=2, value=rank[i]["chapter_name"])
        ws.cell(row=row, column=3,
                value=f"=SUMPRODUCT(('15_Scenario_Grid'!$A$4:$A$381="
                      f"\"ability=\"&$B$4&\"|performance=\"&$B$5&\"|readiness=\"&$B$6)*"
                      f"('15_Scenario_Grid'!$B$4:$B$381={c})*'15_Scenario_Grid'!$D$4:$D$381)")
        ws.cell(row=row, column=4,
                value=f"=SUMPRODUCT(('15_Scenario_Grid'!$A$4:$A$381="
                      f"\"ability=\"&$B$4&\"|performance=\"&$B$5&\"|readiness=\"&$B$6)*"
                      f"('15_Scenario_Grid'!$B$4:$B$381={c})*'15_Scenario_Grid'!$E$4:$E$381)")
        ws.cell(row=row, column=4).number_format = "0.000"
        for j in range(1, 5):
            ws.cell(row=row, column=j).border = BOX
    for j, w in enumerate([5, 46, 24, 24], start=1):
        ws.column_dimensions[get_column_letter(j)].width = w

    # ------------------------------------------------------------ 15 scenario grid
    ws = wb.create_sheet("15_Scenario_Grid")
    title(ws, "All scenarios (27 model combinations + 4 evidence-stream rankings)",
          "Generated by the model; ranks are exact, differences smaller than the uncertainty "
          "should be read as ties.")
    header_row(ws, 3, ["Scenario", "Ch", "Chapter", "Rank", "Incremental ROI",
                       "Additional marks", "Additional hours"])
    rows = [[r["scenario"], int(r["chapter_no"]), r["chapter_name"], int(r["rank"]),
             float(r["incremental_roi"]), float(r["additional_marks"]),
             float(r["additional_hours"])] for r in scen]
    write_rows(ws, 4, rows, number_formats={5: "0.000", 6: "0.00", 7: "0.0"},
               widths=[46, 5, 46, 7, 14, 14, 14])
    ws.freeze_panes = "A4"
    ws.auto_filter.ref = f"A3:G{3 + len(rows)}"

    # ------------------------------------------------------------ 16 sensitivity
    ws = wb.create_sheet("16_Sensitivity")
    title(ws, "Sensitivity: 16 structural variants",
          "Each column is one variant; the cell value is the chapter's rank under that variant.")
    variants = list(dict.fromkeys(r["variant"] for r in sens))
    header_row(ws, 3, ["Variant"] + [f"C{c}" for c in range(1, 15)] + ["Max rank shift"])
    grid = {v: {} for v in variants}
    for r in sens:
        grid[r["variant"]][int(r["chapter_no"])] = int(r["rank"])
    for i, v in enumerate(variants):
        row = 4 + i
        ws.cell(row=row, column=1, value=v)
        for c in range(1, 15):
            ws.cell(row=row, column=1 + c, value=grid[v][c])
        ws.cell(row=row, column=16,
                value=f"=MAX(ABS(D{row}-4),ABS(E{row}-4),ABS(F{row}-4),ABS(G{row}-4),"
                      f"ABS(H{row}-4),ABS(I{row}-4),ABS(J{row}-4),ABS(K{row}-4),ABS(L{row}-4),"
                      f"ABS(M{row}-4),ABS(N{row}-4),ABS(O{row}-4),ABS(P{row}-4),ABS(Q{row}-4))")
        for j in range(1, 17):
            ws.cell(row=row, column=j).border = BOX
    ws.column_dimensions["A"].width = 32
    for j in range(2, 17):
        ws.column_dimensions[get_column_letter(j)].width = 6
    ws.freeze_panes = "B4"

    # ------------------------------------------------------------ 17 uncertainty
    ws = wb.create_sheet("17_Uncertainty")
    title(ws, "Monte Carlo rank stability (20,000 draws, seed 20261115)",
          "Subjective uncertainty distributions declared in the methodology; not sampling "
          "distributions.")
    header_row(ws, 3, ["Ch", "Chapter", "Rank", "ROI", "P(top 3)", "P(top 5)", "Median rank",
                       "Rank p05", "Rank p95", "ROI p05", "ROI p95"])
    for i in range(14):
        row = 4 + i
        c = i + 1
        m = mc[c]
        vals = [c, rank[i]["chapter_name"], int(rank[i]["rank"]), float(rank[i]["incremental_roi"]),
                float(m["p_top3"]), float(m["p_top5"]), float(m["median_rank"]),
                float(m["rank_p05"]), float(m["rank_p95"]), float(m["roi_p05"]),
                float(m["roi_p95"])]
        for j, v in enumerate(vals, start=1):
            cell = ws.cell(row=row, column=j, value=v)
            cell.border = BOX
            cell.font = BODY
            if j in (5, 6):
                cell.number_format = "0.0%"
            if j in (4, 10, 11):
                cell.number_format = "0.000"
        if i % 2 == 0:
            for j in range(1, 12):
                ws.cell(row=row, column=j).fill = PatternFill("solid", fgColor=PALE)
    ws.cell(row=18, column=2, value="Totals (must be 3.0 and 5.0)").font = BOLD
    for col, exp in ((5, 3), (6, 5)):
        L = get_column_letter(col)
        c = ws.cell(row=18, column=col, value=f"=SUM({L}4:{L}17)")
        c.number_format = "0.00"
        c.font = BOLD
    ws.cell(row=19, column=2, value="Check").font = SMALL
    ws.cell(row=19, column=5,
            value='=IF(AND(ABS(E18-3)<0.02,ABS(F18-5)<0.02),"OK","CHECK")').font = BOLD
    for j, w in enumerate([5, 46, 6, 9, 10, 10, 12, 10, 10, 9, 9], start=1):
        ws.column_dimensions[get_column_letter(j)].width = w
    chart = BarChart()
    chart.type = "col"
    chart.title = "Probability of a top-three finish"
    chart.y_axis.title = "Probability"
    data = Reference(ws, min_col=5, min_row=3, max_row=17)
    cats = Reference(ws, min_col=2, min_row=4, max_row=17)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.height = 8
    chart.width = 20
    ws.add_chart(chart, "M4")

    # ------------------------------------------------------------ 18 unit check
    ws = wb.create_sheet("18_Unit_Constraint")
    title(ws, "70-mark and unit-cell constraint check",
          "Reconciled gross totals reproduce every published unit cell exactly; the "
          "deletion-adjusted vector is renormalised to 70 and its deviations are shown.")
    header_row(ws, 3, ["Unit cell", "Official", "Reconciled gross", "After deletion",
                       "Deviation after deletion", "% deviation"])
    rows = [[r["unit_group"], int(float(r["official_marks"])), float(r["reconciled_gross_total"]),
             float(r["final_total_after_deletion"]), float(r["final_deviation"]),
             float(r["final_deviation_pct"]) / 100] for r in units]
    for i, row in enumerate(rows):
        for j, v in enumerate(row, start=1):
            cell = ws.cell(row=4 + i, column=j, value=v)
            cell.border = BOX
            cell.font = BODY
            if j >= 3 and j <= 5:
                cell.number_format = "0.00"
            if j == 6:
                cell.number_format = "0.00%"
    for j, w in enumerate([18, 10, 17, 15, 24, 14], start=1):
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.cell(row=10, column=1, value="Invariant: the ALL row must show 70.00 and 0.00% deviation "
                                    "after deletion.").font = SMALL

    # ------------------------------------------------------------ 19 crosswalk
    ws = wb.create_sheet("19_Syllabus_Crosswalk")
    title(ws, "Historical-to-current syllabus crosswalk",
          "Deleted content was discounted, never included in expected marks.")
    header_row(ws, 3, ["Ch", "Chapter", "2026-27 status", "Deleted or changed content",
                       "Historical mapping treatment", "Deletion share", "Evidence"])
    rows = [[int(r["chapter_no"]), r["chapter_name"], r["syllabus_status_2026_27"],
             r["deleted_or_changed_content"], r["historical_mapping_treatment"],
             float(r["deletion_share_of_historical_marks"]), r["evidence"]] for r in cross]
    write_rows(ws, 4, rows, input_cols=(6,), number_formats={6: "0.00"},
               widths=[5, 44, 16, 56, 44, 12, 46])
    ws.freeze_panes = "C4"

    # ------------------------------------------------------------ 20 sources
    ws = wb.create_sheet("20_Source_Register")
    title(ws, "Source register", "Every source, its authority and its limitation.")
    header_row(ws, 3, ["ID", "Source", "Publisher", "URL / reference", "Session",
                       "Document type", "Retrieval date", "Verification", "Reliability",
                       "Limitations"])
    rows = [[r["source_id"], r["source_name"], r["publisher"], r["url_or_reference"],
             r["academic_session"], r["document_type"], r["retrieval_date"],
             r["verification_status"], r["reliability_grade"], r["limitations"]]
            for r in sources]
    write_rows(ws, 4, rows, widths=[6, 42, 30, 52, 12, 20, 12, 56, 24, 50])
    ws.freeze_panes = "B4"

    # ------------------------------------------------------------ 21 images
    ws = wb.create_sheet("21_Image_Register")
    title(ws, "15/15 MTG image accounting register",
          "Chapter-level values only; topic-level detail on the source pages is deliberately "
          "not propagated.")
    header_row(ws, 3, ["Image ID", "Original filename", "Content type", "Chapter",
                       "Chapter marks 10 yr", "OCR status", "Visual verification",
                       "Ambiguities", "Reliability"])
    rows = [[r["image_id"], r["original_filename"], r["content_type"], r["chapter_reference"],
             r["chapter_marks_total_10yr"], r["ocr_status"], r["visual_verification"],
             r["ambiguities"], r["extraction_reliability"]] for r in images]
    write_rows(ws, 4, rows, widths=[10, 24, 40, 10, 16, 30, 34, 50, 12])

    # ------------------------------------------------------------ 22 coverage
    ws = wb.create_sheet("22_Evidence_Coverage")
    title(ws, "Evidence coverage", "What exists, what does not, and what that means.")
    header_row(ws, 3, ["Evidence item", "Status", "Coverage", "Source", "Notes"])
    rows = [[r["evidence_item"], r["status"], r["coverage"], r["source_id"], r["notes"]]
            for r in coverage]
    write_rows(ws, 4, rows, widths=[46, 24, 16, 12, 70])

    # ------------------------------------------------------------ 23 audit
    ws = wb.create_sheet("23_Audit_Checks")
    title(ws, "Audit and validation checks", "Live checks on this workbook and the model.")
    header_row(ws, 3, ["Check", "Expected", "Actual", "Status"])
    sqp_total_row = 22 + n_sqp
    checks = [
        ("Chapter row count", "14", "=COUNTA(03_Inputs!B4:B17)"),
        ("Exposure sum", "70.00", "=ROUND(SUM(03_Inputs!C4:C17),2)"),
        ("Weights sum", "1.00", "=ROUND(08_Reconciliation!B8,2)"),
        ("Sample paper attribution sum", "70.0",
         f"=ROUND(07_Sample_Paper!B{sqp_total_row},1)"),
        ("Reconciled exposure sum", "70.00", "=ROUND(08_Reconciliation!F27,2)"),
        ("Monte Carlo P(top3) sum", "3.0", "=ROUND(17_Uncertainty!E18,2)"),
        ("Monte Carlo P(top5) sum", "5.0", "=ROUND(17_Uncertainty!F18,2)"),
        ("Hours total (hours)", "182", "=ROUND(10_Hours!D18,0)"),
        ("Unique ranks", "14", "=SUMPRODUCT(1/COUNTIF(04_Final_Ranking!A4:A17,"
                               "04_Final_Ranking!A4:A17))"),
    ]
    for i, (a, b, c) in enumerate(checks):
        row = 4 + i
        ws.cell(row=row, column=1, value=a).font = BODY
        ws.cell(row=row, column=2, value=b).font = BODY
        ws.cell(row=row, column=3, value=c).font = BODY
        ws.cell(row=row, column=4, value=f'=IF(ABS(VALUE(C{row})-VALUE(B{row}))<0.02,"OK","CHECK")')
        for j in range(1, 5):
            ws.cell(row=row, column=j).border = BOX
    for j, w in enumerate([34, 14, 44, 10], start=1):
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.cell(row=13, column=1, value="Validation is also performed outside the workbook by "
                                    "06_Scripts/Validation/06_validate_outputs.py.").font = SMALL

    # ------------------------------------------------------------ 24 methodology
    ws = wb.create_sheet("24_Methodology")
    title(ws, "Methodology, formulas and assumptions",
          "Full narrative in the PDF report, section 8 and appendices A-B.")
    lines = [
        ("Exposure reconciliation", "E_raw = 0.40*A + 0.35*B + 0.25*C, normalised to 70, then "
                                    "raked inside each official merged unit cell."),
        ("Deletion adjustment", "E = E_raked x (1 - deletion share), renormalised to 70."),
        ("Choice-adjusted success", "f(r) = r + 0.5 x 0.314 x (1 - r)."),
        ("Baseline marks", "E x f(r0)"),
        ("Target marks", "E x f(r1)"),
        ("Additional marks", "E x (f(r1) - f(r0))"),
        ("Additional hours", "max(1.5, H x (r1 - r0)/r1)"),
        ("Incremental ROI", "additional marks / additional hours (primary)"),
        ("Total-mark ROI", "target marks / total hours from zero (secondary)"),
        ("Confidence index", "100 x (0.45 consistency + 0.25 source quality + 0.30 mapping)"),
        ("Monte Carlo", "20,000 draws; exposure N(E, 0.15E); hours triangular(low, central, "
                        "high); r0 N(profile, 0.06); r1 N(target, 0.03)."),
        ("Recency weighting", "half-life 3 years; 2022 Term papers share one year's weight."),
        ("What is not modelled", "Compartment papers, per-set duplication, marking-scheme "
                                 "step marks, and topic-level content."),
    ]
    header_row(ws, 3, ["Element", "Rule"])
    for i, (a, b) in enumerate(lines):
        ws.cell(row=4 + i, column=1, value=a).font = BOLD
        c = ws.cell(row=4 + i, column=2, value=b)
        c.font = BODY
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[4 + i].height = 30
    ws.column_dimensions["A"].width = 28
    ws.column_dimensions["B"].width = 110

    # ------------------------------------------------------------ 25 personal
    ws = wb.create_sheet("25_Personal_Diagnostic")
    title(ws, "Personal diagnostic template (measured data, not research estimates)",
          "Export this sheet from the PWA (Data > Export diagnostics) or paste your own measured "
          "values. Measured values override the research baseline in the personalised dashboard "
          "only; the research ranking on 04_Final_Ranking is never recalculated.")
    header_row(ws, 3, ["Ch", "Chapter", "Research exposure", "Research baseline readiness",
                       "Measured readiness", "Measured hours logged", "Personalised additional "
                       "marks", "Personalised ROI", "Source of measurement"])
    for i in range(14):
        row = 4 + i
        c = i + 1
        ws.cell(row=row, column=1, value=c)
        ws.cell(row=row, column=2, value=rank[i]["chapter_name"])
        ws.cell(row=row, column=3, value=f"=03_Inputs!C{row}").number_format = "0.00"
        ws.cell(row=row, column=4, value=f"=03_Inputs!E{row}").number_format = "0.000"
        ws.cell(row=row, column=5, value="").fill = PatternFill("solid", fgColor=INPUT)
        ws.cell(row=row, column=5).number_format = "0.000"
        ws.cell(row=row, column=6, value="").fill = PatternFill("solid", fgColor=INPUT)
        ws.cell(row=row, column=6).number_format = "0.0"
        ws.cell(row=row, column=7,
                value=f"=IF(E{row}=\"\",\"\",C{row}*(03_Inputs!F{row}-E{row}))"
                ).number_format = "0.00"
        ws.cell(row=row, column=8,
                value=f"=IF(OR(E{row}=\"\",F{row}=\"\",F{row}=0),\"\",G{row}/MAX(1.5,"
                      f"03_Inputs!G{row}*((03_Inputs!F{row}-E{row})/03_Inputs!F{row})))"
                ).number_format = "0.000"
        ws.cell(row=row, column=9, value="PWA diagnostic (measured)").font = SMALL
        for j in range(1, 10):
            ws.cell(row=row, column=j).border = BOX
    ws.cell(row=19, column=2, value="Row explains the personalised maths: additional marks = "
                                    "research exposure x (target readiness - measured readiness).").font = SMALL
    for j, w in enumerate([5, 40, 17, 22, 16, 20, 20, 16, 30], start=1):
        ws.column_dimensions[get_column_letter(j)].width = w

    # ------------------------------------------------------------ 26 version
    ws = wb.create_sheet("26_Version_History")
    title(ws, "Version history", "Question bank, syllabus and model versions are tracked "
                                 "separately in the application.")
    header_row(ws, 3, ["Version", "Date", "Change", "Affected outputs"])
    history = [
        ("1.0.0", "2026-11-15", "First complete release: 14-chapter model, three evidence "
                                "streams, PDF/Excel/Markdown reports, PWA and audit package.",
         "all"),
        ("1.0.0-rc2", "2026-11-15", "Fixed SQP marks loading for independent questions; added "
                                    "chapter-differential hour sensitivity; restricted "
                                    "robustness window to model scenarios.", "ranking, sensitivity"),
        ("1.0.0-rc1", "2026-11-15", "Initial model calibration; unit-cell raking introduced "
                                    "after the first 70-mark reconciliation check.",
         "exposure"),
    ]
    for i, row in enumerate(history):
        for j, v in enumerate(row, start=1):
            ws.cell(row=4 + i, column=j, value=v).font = BODY
            ws.cell(row=4 + i, column=j).border = BOX
    for j, w in enumerate([12, 12, 96, 24], start=1):
        ws.column_dimensions[get_column_letter(j)].width = w

    # ------------------------------------------------------------ dashboard last
    dash = wb.create_sheet("02_Dashboard", 1)
    title(dash, "Executive dashboard - CBSE Class XII Physics 2027 chapter ROI",
          "Values link to 04_Final_Ranking. Change inputs on 03_Inputs to re-run the model.")
    kp = [("Chapters", "=COUNTA(03_Inputs!B4:B17)", "0"),
          ("Exposure total (must be 70)", "=ROUND(SUM(03_Inputs!C4:C17),2)", "0.00"),
          ("Baseline paper total (intermediate)", "=ROUND(SUM(04_Final_Ranking!G4:G17),2)", "0.00"),
          ("Target paper total (strong readiness)", "=ROUND(SUM(04_Final_Ranking!H4:H17),2)", "0.00"),
          ("Total additional marks available", "=ROUND(SUM(04_Final_Ranking!I4:I17),2)", "0.00"),
          ("Total additional hours", "=ROUND(SUM(04_Final_Ranking!J4:J17),1)", "0.0"),
          ("Average incremental ROI", "=ROUND(AVERAGE(04_Final_Ranking!K4:K17),3)", "0.000")]
    header_row(dash, 4, ["Headline metric", "Value"])
    for i, (a, b, fmt) in enumerate(kp):
        row = 5 + i
        dash.cell(row=row, column=1, value=a).font = BODY
        c = dash.cell(row=row, column=2, value=b)
        c.number_format = fmt
        c.font = BOLD
        for j in (1, 2):
            dash.cell(row=row, column=j).border = BOX
    dash.column_dimensions["A"].width = 40
    dash.column_dimensions["B"].width = 14
    dash.cell(row=13, column=1, value="Top five chapters by incremental ROI").font = H2
    header_row(dash, 14, ["Rank", "Chapter", "Incremental ROI", "Additional marks",
                          "Additional hours", "Grade"])
    for i in range(5):
        row = 15 + i
        dash.cell(row=row, column=1, value=i + 1)
        dash.cell(row=row, column=2,
                  value=f"=INDEX(04_Final_Ranking!$C$4:$C$17,MATCH({i + 1},"
                        f"04_Final_Ranking!$A$4:$A$17,0))")
        dash.cell(row=row, column=3,
                  value=f"=INDEX(04_Final_Ranking!$K$4:$K$17,MATCH({i + 1},"
                        f"04_Final_Ranking!$A$4:$A$17,0))").number_format = "0.00"
        dash.cell(row=row, column=4,
                  value=f"=INDEX(04_Final_Ranking!$I$4:$I$17,MATCH({i + 1},"
                        f"04_Final_Ranking!$A$4:$A$17,0))").number_format = "0.00"
        dash.cell(row=row, column=5,
                  value=f"=INDEX(04_Final_Ranking!$J$4:$J$17,MATCH({i + 1},"
                        f"04_Final_Ranking!$A$4:$A$17,0))").number_format = "0.0"
        dash.cell(row=row, column=6,
                  value=f"=INDEX(04_Final_Ranking!$O$4:$O$17,MATCH({i + 1},"
                        f"04_Final_Ranking!$A$4:$A$17,0))")
        for j in range(1, 7):
            dash.cell(row=row, column=j).border = BOX
    for j, w in enumerate([14, 46, 16, 16, 16, 8], start=1):
        dash.column_dimensions[get_column_letter(j)].width = w

    chart = BarChart()
    chart.type = "bar"
    chart.title = "Incremental ROI by chapter"
    chart.x_axis.title = "Marks per additional hour"
    data = Reference(wb["04_Final_Ranking"], min_col=11, min_row=3, max_row=17)
    cats = Reference(wb["04_Final_Ranking"], min_col=3, min_row=4, max_row=17)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.height = 11
    chart.width = 20
    dash.add_chart(chart, "A23")

    chart2 = BarChart()
    chart2.type = "col"
    chart2.title = "Exposure versus additional marks"
    data2 = Reference(wb["04_Final_Ranking"], min_col=4, min_row=3, max_row=17)
    data3 = Reference(wb["04_Final_Ranking"], min_col=9, min_row=3, max_row=17)
    chart2.add_data(data2, titles_from_data=True)
    chart2.add_data(data3, titles_from_data=True)
    chart2.set_categories(cats)
    chart2.height = 9
    chart2.width = 20
    dash.add_chart(chart2, "A48")

    chart3 = BarChart()
    chart3.type = "col"
    chart3.title = "Probability of top-three finish (Monte Carlo)"
    data4 = Reference(wb["17_Uncertainty"], min_col=5, min_row=3, max_row=17)
    chart3.add_data(data4, titles_from_data=True)
    chart3.set_categories(Reference(wb["17_Uncertainty"], min_col=2, min_row=4, max_row=17))
    chart3.height = 9
    chart3.width = 20
    dash.add_chart(chart3, "A70")

    # Excel requires quoting of sheet names that begin with a digit or contain
    # underscore-heavy names; normalise every cross-sheet reference.
    import re
    pat = re.compile(r"(?<![A-Za-z0-9_'])(\d\d_[A-Za-z_]+)!")
    for ws_ in wb.worksheets:
        for row in ws_.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and cell.value.startswith("="):
                    cell.value = pat.sub(r"'\1'!", cell.value)

    wb.save(OUT)
    print("wrote", OUT.relative_to(ROOT), OUT.stat().st_size // 1024, "KB")
    print("sheets:", len(wb.sheetnames), wb.sheetnames)


if __name__ == "__main__":
    main()
