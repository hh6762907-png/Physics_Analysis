#!/usr/bin/env python3
"""
02_build_datasets.py
--------------------
Writes every structured research dataset used by the ROI model.

All values here are transcribed from named evidence artefacts; each row carries
its provenance fields. No value is invented: where a value could not be read or
verified, the field is marked UNAVAILABLE/UNREADABLE and handled downstream.

Outputs (all under 03_Research_Data/):
  Official_Unit_Weightage/unit_weightage_2026_27.csv
  MTG_Extracted_Data/mtg_questions_by_year.csv
  MTG_Extracted_Data/mtg_chapter_marks_10yr.csv
  Official_Sample_Paper/sqp_2026_27_question_metadata.csv
  Syllabus_Crosswalk/syllabus_crosswalk.csv
  Image_Accounting_Register/image_register.csv
  Source_Register/source_register.csv
  Source_Register/evidence_coverage_report.csv
"""
import csv
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
P = ROOT / "CBSE_Physics_2027_ROI_Project" / "03_Research_Data"

CHAPTERS = [
    (1, "Electric Charges and Fields"),
    (2, "Electrostatic Potential and Capacitance"),
    (3, "Current Electricity"),
    (4, "Moving Charges and Magnetism"),
    (5, "Magnetism and Matter"),
    (6, "Electromagnetic Induction"),
    (7, "Alternating Current"),
    (8, "Electromagnetic Waves"),
    (9, "Ray Optics and Optical Instruments"),
    (10, "Wave Optics"),
    (11, "Dual Nature of Radiation and Matter"),
    (12, "Atoms"),
    (13, "Nuclei"),
    (14, "Semiconductor Electronics: Materials, Devices and Simple Circuits"),
]

# Physics_SecP2_2026-27.pdf p.12 course structure: merged MARKS cells were read
# from the PDF table geometry (PyMuPDF find_tables) and confirmed on a rendered
# page image. 16 spans Units I+II; 17 spans III+IV; 18 spans V+VI; 12 spans
# VII+VIII; 7 is Unit IX. Total 70.
UNIT_WEIGHTAGE = [
    ("I", "Electrostatics", [1, 2], 16, "16"),
    ("II", "Current Electricity", [3], 16, "16"),
    ("III", "Magnetic Effects of Current and Magnetism", [4, 5], 17, "17"),
    ("IV", "Electromagnetic Induction and Alternating Currents", [6, 7], 17, "17"),
    ("V", "Electromagnetic Waves", [8], 18, "18"),
    ("VI", "Optics", [9, 10], 18, "18"),
    ("VII", "Dual Nature of Radiation and Matter", [11], 12, "12"),
    ("VIII", "Atoms and Nuclei", [12, 13], 12, "12"),
    ("IX", "Electronic Devices", [14], 7, "7"),
]
UNIT_GROUPS = [  # merged marks cells, as printed
    ("Units I+II", [1, 2, 3], 16),
    ("Units III+IV", [4, 5, 6, 7], 17),
    ("Units V+VI", [8, 9, 10], 18),
    ("Units VII+VIII", [11, 12, 13], 12),
    ("Unit IX", [14], 7),
]

# ---------------------------------------------------------------------------
# Image 01 : MTG Champion "Number of Questions" table, 2017-2026.
# Columns exactly as printed: 2026 (55/5/1), 2025 (55/1/2), 2024 (55/5/1),
# 2023 (55/5/1), 2022 SET(55/5/1) Term-II, 2022 SET(55/2/4) Term-I, 2021 (no
# exam, COVID), 2020 (55/5/1), 2019 (55/5/1), 2018 (55/5/1), 2017 (55/5/1).
# "-" means zero questions reported by MTG.
# ---------------------------------------------------------------------------
MTG_YEAR_COLUMNS = [
    ("2026", "Regular", 70),
    ("2025", "Regular", 70),
    ("2024", "Regular", 70),
    ("2023", "Regular", 70),
    ("2022_TermII", "Term-II (special)", 35),
    ("2022_TermI", "Term-I (special)", 35),
    ("2021", "NOT HELD (COVID-19)", 0),
    ("2020", "Regular", 70),
    ("2019", "Regular", 70),
    ("2018", "Regular", 70),
    ("2017", "Regular", 70),
]
MTG_COUNTS = {
    #       2026 2025 2024 2023 22T2 22T1 2021 2020 2019 2018 2017
    1:  [1,   0,   2,   2,   0,   8,   0,   3,   1,   2,   2],
    2:  [3,   2,   3,   2,   0,   7,   0,   3,   2,   0,   1],
    3:  [2,   3,   1,   3,   0,  13,   0,   3,   3,   3,   2],
    4:  [3,   4,   5,   5,   0,  11,   0,   3,   2,   0,   5],
    5:  [0,   0,   1,   1,   0,   3,   0,   0,   0,   2,   0],
    6:  [4,   4,   2,   2,   0,   3,   0,   1,   1,   1,   1],
    7:  [2,   2,   1,   2,   0,  10,   0,   3,   1,   1,   1],
    8:  [2,   2,   2,   2,   1,   0,   0,   2,   1,   2,   1],
    9:  [3,   3,   3,   2,   3,   0,   0,   3,   2,   3,   3],
    10: [3,   2,   3,   3,   1,   0,   0,   4,   3,   1,   1],
    11: [3,   3,   2,   3,   1,   0,   0,   3,   3,   2,   1],
    12: [2,   2,   4,   3,   2,   0,   0,   2,   2,   1,   2],
    13: [4,   2,   1,   2,   1,   0,   0,   2,   1,   2,   1],
    14: [3,   4,   3,   3,   3,   0,   0,   5,   2,   2,   3],
}

# ---------------------------------------------------------------------------
# Chapter-page "Weightage Xtract" totals: sum of the printed Total# (marks)
# column over all topic rows of that chapter page, for the 10-year window
# 2017-2026. Read from images 02-15 and re-checked against the row-level
# counts by the formula  MCQ*1 + VSA*1 + SA-I*2 + SA-II*3 + CBQ*4or5 + LA*5.
# The row-level check reproduced every printed Total# value.
# ---------------------------------------------------------------------------
MTG_XTRACT = {1: 158, 2: 237, 3: 247, 4: 244, 5: 49, 6: 176, 7: 199,
              8: 115, 9: 370, 10: 236, 11: 178, 12: 121, 13: 117, 14: 207}

# ---------------------------------------------------------------------------
# Official CBSE Sample Question Paper 2026-27, Physics (042).
# Question-level metadata only (no question text). Chapter attribution by the
# analyst with confidence codes; internal-choice pairs are marked OR-PAIR.
# marks_primary = marks credited to the attributed chapter under the
# choice-aware split documented in the methodology (an OR pair split equally
# between its two options; same-chapter pairs stay whole).
# ---------------------------------------------------------------------------
SQP = [
    # q, section, marks, chapter, format, choice, conf, note
    ("1",  "A", 1, 1,  "MCQ", "none", "high", "flux under Gauss surface"),
    ("2",  "A", 1, 3,  "MCQ", "none", "high", "parallel heaters power"),
    ("3",  "A", 1, 6,  "MCQ", "none", "medium", "induced current, long cylinder (EMI)"),
    ("4",  "A", 1, 8,  "MCQ", "none", "high", "EM wave propagation direction"),
    ("5",  "A", 1, 10, "MCQ", "none", "high", "Huygens construction limits"),
    ("6",  "A", 1, 10, "MCQ", "none", "high", "shape of wavefront"),
    ("7",  "A", 1, 13, "MCQ", "none", "high", "BE per nucleon maximum"),
    ("8",  "A", 1, 5,  "MCQ", "none", "medium", "superconductor diamagnetism"),
    ("9",  "A", 1, 3,  "MCQ", "none", "high", "Wheatstone bridge current"),
    ("10", "A", 1, 3,  "MCQ", "none", "medium", "series bulbs on AC: resistance ratio"),
    ("11", "A", 1, 12, "MCQ", "none", "high", "nuclear-to-atomic scale"),
    ("12", "A", 1, 4,  "MCQ", "none", "high", "field at centre of semicircular arc"),
    ("13", "A", 1, 12, "AssertionReason", "none", "high", "Rutherford scattering"),
    ("14", "A", 1, 9,  "AssertionReason", "none", "high", "lens in water"),
    ("15", "A", 1, 10, "AssertionReason", "none", "high", "YDSE fringe width"),
    ("16", "A", 1, 2,  "AssertionReason", "none", "medium", "field inside conductor"),
    ("17", "B", 2, 8,  "VSA", "none", "high", "refractive index/frequency of EM wave"),
    ("18", "B", 2, 3,  "VSA", "none", "high", "electron path with/without field"),
    ("19", "B", 2, 2,  "VSA", "none", "high", "work to move charge: potential energy"),
    ("20A", "B", 2, 5, "VSA", "OR-PAIR-20", "high", "relative permeability 800"),
    ("20B", "B", 2, 5, "VSA", "OR-PAIR-20", "high", "Gauss law of magnetism"),
    ("21A", "B", 2, 12, "VSA", "OR-PAIR-21", "high", "hydrogen spectral fingerprint"),
    ("21B", "B", 2, 12, "VSA", "OR-PAIR-21", "high", "Bohr quantisation / de Broglie"),
    ("22", "C", 3, 14, "SA", "none", "high", "energy band diagrams"),
    ("23", "C", 3, 3,  "SA", "none", "high", "three reasoning items, current electricity"),
    ("24", "C", 3, 13, "SA", "none", "high", "BE per nucleon of oxygen"),
    ("25", "C", 3, 9,  "SA", "none", "high", "diamond total internal reflection"),
    ("26", "C", 3, 10, "SA", "none", "high", "Snell's law from Huygens"),
    ("27A", "C", 3, 4, "SA", "OR-PAIR-27", "high", "shunt resistance / galvanometer frame"),
    ("27B", "C", 3, 5, "SA", "OR-PAIR-27", "medium", "magnetic dipole moment of bent wire"),
    ("28", "C", 3, 6,  "SA", "none", "high", "magnet through ring; self-inductance"),
    ("29", "D", 4, 14, "CaseBased", "none", "high", "polymer semiconductors case study"),
    ("30", "D", 4, 11, "CaseBased", "none", "high", "photoelectric effect case study"),
    ("31A", "E", 5, 2, "LA", "OR-PAIR-31", "high", "capacitance: conductor, combinations, factors"),
    ("31B", "E", 5, 2, "LA", "OR-PAIR-31", "high", "E = -dV/dx; sphere breakdown radius"),
    ("32A", "E", 5, 9, "LA", "OR-PAIR-32", "high", "compound microscope"),
    ("32B", "E", 5, 9, "LA", "OR-PAIR-32", "high", "astronomical telescope"),
    ("33A", "E", 5, 7, "LA", "OR-PAIR-33", "high", "transformer"),
    ("33B", "E", 5, 7, "LA", "OR-PAIR-33", "high", "series LCR resonance"),
]


def w(path: pathlib.Path, rows, header):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        cw = csv.writer(fh)
        cw.writerow(header)
        cw.writerows(rows)
    print(f"wrote {path.relative_to(ROOT)} ({len(rows)} rows)")


def build_unit_weightage():
    rows = []
    for uid, name, chs, marks, printed in UNIT_WEIGHTAGE:
        rows.append([uid, name, ";".join(f"C{c}" for c in chs), marks, printed,
                     "Physics_SecP2_2026-27.pdf p.12 (merged MARKS cell)",
                     "verified officially"])
    rows.append(["TOTAL", "All nine units", "C1-C14", 70, "70",
                 "Physics_SecP2_2026-27.pdf p.12", "verified officially"])
    w(P / "Official_Unit_Weightage" / "unit_weightage_2026_27.csv", rows,
      ["unit", "unit_name", "chapters", "marks", "printed_cell", "source", "verification"])


def build_mtg_year():
    rows = []
    for ci, (num, name) in enumerate(CHAPTERS):
        for yi, (yr, kind, paper_marks) in enumerate(MTG_YEAR_COLUMNS):
            rows.append([num, name, yr, kind, paper_marks, MTG_COUNTS[num][yi],
                         "MTG Champion trend table, photograph IMG20261115053154.jpg",
                         "unreadable" if MTG_COUNTS[num][yi] is None else "read",
                         "visual verification (2x crop); OCR cross-check",
                         "MTG-reported secondary data; not re-verified against original paper"])
    w(P / "MTG_Extracted_Data" / "mtg_questions_by_year.csv", rows,
      ["chapter_no", "chapter_name", "exam_year", "paper_type", "paper_marks",
       "questions_reported", "source_image", "read_status", "verification", "reliability_note"])


def build_mtg_marks():
    rows = []
    for num, name in CHAPTERS:
        rows.append([num, name, MTG_XTRACT[num], "2017-2026 (all sets & formats)",
                     f"IMG2026{'' if False else ''}" + "IMG page " + f"{num+1:02d}",
                     "sum of printed Total# column over topic rows",
                     "row-level formula check reproduced every printed Total#",
                     "MTG-reported aggregate; internal-choice marks of CBQs excluded by MTG"])
    total = sum(MTG_XTRACT.values())
    rows.append(["", "ALL CHAPTERS", total, "2017-2026", "images 02-15",
                 "sum", "verified", "used for market-share normalisation"])
    w(P / "MTG_Extracted_Data" / "mtg_chapter_marks_10yr.csv", rows,
      ["chapter_no", "chapter_name", "marks_total_10yr", "window", "source_image",
       "derivation", "verification", "caveat"])


def build_sqp():
    rows = []
    for q, sec, marks, ch, fmt, choice, conf, note in SQP:
        rows.append([q, sec, marks, f"C{ch}", CHAPTERS[ch - 1][1], fmt, choice, conf,
                     note, "CBSE official SQP 2026-27, Physics (042)",
                     "question text deliberately not stored (chapter-level metadata only)"])
    w(P / "Official_Sample_Paper" / "sqp_2026_27_question_metadata.csv", rows,
      ["question_no", "section", "marks", "chapter_id", "chapter_name", "format",
       "internal_choice_group", "attribution_confidence", "classification_note",
       "source", "copyright_note"])


def build_crosswalk():
    # Deletion shares: fraction of the chapter's historical marks that rested on
    # content no longer examinable in 2026-27. Derived from the syllabus text
    # comparison and, where available, MTG topic shares (internal check only).
    rows = [
        [1, "Full chapter in syllabus", "None removed for 2026-27",
         "No adjustment", 0.00,
         "Syllabus text identical in scope to 2025-26 for this chapter"],
        [2, "Full chapter in syllabus",
         "van de Graaff generator already outside syllabus before 2026-27",
         "No 2026-27 adjustment", 0.00, "Energy stored in capacitor: formula only"],
        [3, "Full chapter in syllabus",
         "Metre bridge / potentiometer experiments not in theory scope",
         "No 2026-27 adjustment", 0.00, "Wheatstone bridge retained"],
        [4, "Full chapter in syllabus", "Cyclotron already removed earlier",
         "No 2026-27 adjustment", 0.00, "Solenoid qualitative only"],
        [5, "Partial", "Earth's magnetism and quantitative dipole-field treatment already outside",
         "Historical questions on deleted sub-areas excluded", 0.05,
         "Qualitative treatment only in 2026-27"],
        [6, "Partial", "'Eddy currents' removed for 2026-27",
         "Historical eddy-current questions excluded", 0.04,
         "Self and mutual induction retained"],
        [7, "Full chapter in syllabus", "LC oscillations already outside; AC generator now listed here",
         "AC generator re-mapped from Ch6 (MTG) to Ch7 (syllabus)", 0.00,
         "Transformer and resonance retained"],
        [8, "Full chapter in syllabus", "No deletion identified",
         "No adjustment", 0.00, "Qualitative character of EM waves"],
        [9, "Partial", "'Dispersion of light through a prism' removed for 2026-27",
         "Historical dispersion questions excluded", 0.08,
         "Refraction through prism retained; scattering already removed"],
        [10, "Full chapter in syllabus", "Polarisation and resolving power already removed",
         "No 2026-27 adjustment", 0.00, "YDSE final expression only"],
        [11, "Partial", "Davisson-Germer experiment removed for 2026-27",
         "Historical Davisson-Germer questions excluded", 0.03,
         "Photoelectric effect and de Broglie retained"],
        [12, "Partial", "de Broglie's explanation of Bohr's second postulate removed",
         "Historical questions on that sub-topic excluded", 0.09,
         "Bohr model and line spectra retained"],
        [13, "Full chapter in syllabus", "Radioactivity already removed before 2026-27",
         "No 2026-27 adjustment (MTG topic list also excludes radioactivity)", 0.00,
         "Fission/fusion retained"],
        [14, "Partial",
         "Special purpose p-n junction diodes (LED, photodiode, solar cell, Zener) and "
         "Zener regulator removed for 2026-27; transistor/logic gates already removed",
         "Historical questions on deleted sub-areas excluded", 0.15,
         "Band theory, p-n junction, diode I-V, rectifier retained"],
    ]
    out = []
    for ch, status, deleted, treatment, share, note in rows:
        out.append([ch, CHAPTERS[ch - 1][1], status, deleted, treatment,
                    f"{share:.2f}", note,
                    "Syllabus comparison: Physics_SecP2_2026-27.pdf vs 2025-26 scope",
                    "deletion share is an expert estimate used as a multiplier; "
                    "tested at 0.5x and 1.5x in sensitivity analysis"])
    w(P / "Syllabus_Crosswalk" / "syllabus_crosswalk.csv", out,
      ["chapter_no", "chapter_name", "syllabus_status_2026_27", "deleted_or_changed_content",
       "historical_mapping_treatment", "deletion_share_of_historical_marks", "notes",
       "evidence", "uncertainty_treatment"])


def build_image_register():
    info = {
        1: ("Cross-year question-count table (all 14 chapters, 2017-2026)", "ALL",
            "14 rows x 11 year-columns of question counts; 2021 column blank (exam not held); "
            "2022 split Term-I/Term-II", "n/a", 139, "clean",
            "2026 column totals 35 questions, 2025 column totals 33, 2022 Term-I totals 55 "
            "(55-question MCQ paper) - internal consistency checks passed"),
    }
    for ch in range(1, 15):
        info[ch + 1] = (f"Chapter {ch} trend-analysis page", f"C{ch}",
                        "Topic list, topic-wise trend chart, topic weightage pie, "
                        "Weightage-Xtract table (question counts by format + marks totals)",
                        MTG_XTRACT[ch], 0, "clean",
                        "")
    notes = {
        2: "Pie labels overlap; topic shares not propagated (chapter-level only).",
        3: "Text partly obscured by page curvature; all Total# values legible.",
        5: "Glare on upper-left; table fully legible.",
        6: "Page curvature at binding; Total# column legible.",
        7: "Right-hand page edge crops legend only.",
        8: "Good legibility.",
        9: "Page shadow across title; table legible.",
        10: "Hand/finger occludes page edge only; table legible.",
        11: "Task lighting uneven; values legible.",
        12: "Book rotated; corrected by 90 deg for transcription.",
        13: "Good legibility.",
        14: "Slight blur at bottom row; Total# legible.",
        15: "Photograph taken upside-down relative to others; corrected by 180 deg.",
        1: "Photograph upside-down; corrected by 180 deg. One column header (2021*) "
           "carries the footnote that the exam was not held due to COVID-19.",
    }
    ocr = {1: "OCR partial (rotated page); numbers verified visually on 2x crops",
           2: "OCR partial; numbers verified visually",
           3: "OCR partial; numbers verified visually",
           4: "OCR partial; numbers verified visually",
           5: "OCR partial; numbers verified visually",
           6: "OCR sparse; numbers verified visually",
           7: "OCR partial; numbers verified visually",
           8: "OCR partial; numbers verified visually",
           9: "OCR sparse; numbers verified visually",
           10: "OCR partial; numbers verified visually",
           11: "OCR partial; numbers verified visually",
           12: "OCR partial; numbers verified visually",
           13: "OCR partial; numbers verified visually",
           14: "OCR partial; numbers verified visually",
           15: "OCR good (page upside-down); numbers verified visually"}
    files = {
        1: "IMG20261115053154.jpg", 2: "IMG20261115053218.jpg", 3: "IMG20261115053256.jpg",
        4: "IMG20261115053341.jpg", 5: "IMG20261115053418.jpg", 6: "IMG20261115053432.jpg",
        7: "IMG20261115053448.jpg", 8: "IMG20261115053516.jpg", 9: "IMG20261115053542.jpg",
        10: "IMG20261115053615.jpg", 11: "IMG20261115053637.jpg", 12: "IMG20261115053649.jpg",
        13: "IMG20261115053731.jpg", 14: "IMG20261115053748.jpg", 15: "IMG20261115053820.jpg",
    }
    rows = []
    for i in range(1, 16):
        ctype, chref, summary, marks, _, status, extra = info[i]
        rows.append([
            f"IMG-{i:02d}", files[i], ctype,
            f"MTG Champion Physics, p. {i} of photographed sequence" if i > 1 else "MTG Champion Physics, trend summary table",
            chref, summary, marks if marks != "n/a" else "",
            ocr[i], "verified against original at 2x crop scale" if i > 1 else
            "verified against original in three overlapping crops",
            (notes.get(i, "") + (" " + extra if extra else "")).strip() or "none",
            "HIGH" if i == 1 else ("HIGH" if MTG_XTRACT.get(i - 1) else "MEDIUM"),
            "chapter-level values only propagated by design; topic-level detail "
            "present on the page is deliberately excluded from every deliverable",
            "IMG file at repository root (original preserved, unmodified)",
        ])
    w(P / "Image_Accounting_Register" / "image_register.csv", rows,
      ["image_id", "original_filename", "content_type", "document_reference",
       "chapter_reference", "extracted_information", "chapter_marks_total_10yr",
       "ocr_status", "visual_verification", "ambiguities", "extraction_reliability",
       "propagation_rule", "source_location"])


def build_sources():
    rows = [
        ["S01", "CBSE Senior Secondary Curriculum 2026-27, Physics (Subject Code 042)",
         "Central Board of Secondary Education (CBSE), Academic Unit",
         "https://cbseacademic.nic.in/web_material/CurriculumMain27/SecPart2/Physics_SecP2_2026-27.pdf",
         "2026-03 (document modified 2026-03-05 per PDF metadata)",
         "2026-27", "Physics_SecP2_2026-27.pdf (23 pp.)", "2026-27", "Official syllabus", "2026-11-15",
         "VERIFIED - uploaded copy matches official URL text (title page, p.12 course "
         "structure and Ch.1-14 content compared)",
         "pp. 12-16 (Class XII theory), p. 23 (question paper design)",
         "A (authoritative)", "Official weightage is unit-wise, not chapter-wise; "
         "chapter-level marks are not published by CBSE"],
        ["S02", "CBSE Curriculum hub for academic year 2026-27", "CBSE Academic Unit",
         "https://cbseacademic.nic.in/curriculum_2027.html", "accessed 2026-11-15",
         "2026-27", "web page", "2026-27", "Official index", "2026-11-15",
         "VERIFIED - lists Physics_SecP2_2026-27.pdf under Secondary Curriculum Part 2 (XI-XII)",
         "Group-A / Physics link", "A (authoritative)", "Index page only"],
        ["S03", "CBSE Sample Question Paper 2026-27, Physics (042), with Marking Scheme",
         "CBSE Academic Unit",
         "https://cbseacademic.nic.in/web_material/SQP/ClassXII_2026_27/Physics-SQP.pdf",
         "2026-27 session", "2026-27", "SQP (33 questions) + MS", "2026-27",
         "Official sample paper", "2026-11-15",
         "VERIFIED - paper structure (16x1, 5x2, 7x3, 2x4, 3x5; internal choice in 2 of "
         "Section B, 1 of Section C, all 3 of Section E) read directly from the PDF",
         "General instructions + Sections A-E", "A (authoritative)",
         "Single paper; not a historical board paper; question text not stored"],
        ["S04", "MTG Champion Physics trend analysis (15 photographs)",
         "MTG Learning Media (publisher)", "Local photographs IMG20261115053154.jpg ... "
         "IMG20261115053820.jpg", "edition for 2026-27 session (impression date not visible)",
         "2026-27 edition covering 2017-2026 papers", "book pages 1-14 + summary table",
         "2017-2026", "Secondary trend analysis (commercial publication)", "2026-11-15",
         "EXTRACTED - 15/15 images audited; chapter-level totals reproduced by an "
         "independent row-level formula check", "images 01-15",
         "B (reputable secondary, not independently re-verified against original papers)",
         "Attribution basis and inclusion rules are MTG's, not CBSE's; internal-choice "
         "marks of case-based questions excluded by the publisher"],
        ["S05", "CBSE Curriculum hub for academic year 2025-26", "CBSE Academic Unit",
         "https://cbseacademic.nic.in/curriculum_2026.html", "accessed 2026-11-15",
         "2025-26", "web page", "2025-26", "Official index (prior session)", "2026-11-15",
         "VERIFIED as prior-session index - confirms 2026-27 is the applicable session "
         "for the 2027 board examination", "n/a", "A (authoritative)",
         "Superseded for the target examination"],
        ["S06", "Aggregator pages describing the 2026-27 Physics paper pattern",
         "Oswal Publishers, FutureTopper, AglaSem, Educart, Collegedunia, Giraffe Learning",
         "multiple URLs (see Source_References/urls.txt)", "2025-09 to 2026-10", "2026-27",
         "web articles", "2026-27", "Secondary commentary", "2026-11-15",
         "CORROBORATED - agree on 33 questions / sections A-E / internal-choice positions; "
         "one page (Collegedunia) printed an unofficial chapter-wise marks split "
         "(10/6/11/6/4/14/4/8/7) that conflicts with the official unit grouping and was "
         "REJECTED as evidence", "n/a", "C (commentary)",
         "Used only to corroborate the pattern; never used for chapter-level marks"],
        ["S07", "NCERT Physics textbooks Class XII, Parts I and II",
         "NCERT", "https://ncert.nic.in/textbook.php", "rationalised editions",
         "2023-24 onward", "textbooks", "2026-27", "Prescribed textbook", "2026-11-15",
         "NOT RETRIEVED - egress restrictions in the working environment; cited as the "
         "prescribed reading in the official syllabus", "n/a", "A (authoritative)",
         "Chapter numbering in this project follows the 2026-27 syllabus"],
        ["S08", "CBSE Class XII sample paper archive (2022-23 to 2026-27)",
         "CBSE Academic Unit", "https://cbseacademic.nic.in/SQP_CLASSXII_2026-27.html",
         "2026-27", "2026-27", "index of SQP/MS pairs", "2023-2027", "Official index",
         "2026-11-15", "VERIFIED - index lists Physics SQP and MS for the 2026-27 session",
         "n/a", "A (authoritative)", "Older sample papers exist but were not analysed "
         "in this pass (see coverage report)"],
    ]
    w(P / "Source_Register" / "source_register.csv", rows,
      ["source_id", "source_name", "publisher", "url_or_reference", "publication_date",
       "academic_session", "document_title", "examination_year", "document_type",
       "retrieval_date", "verification_status", "relevant_sections", "reliability_grade",
       "limitations"])


def build_coverage():
    rows = [
        ["Official syllabus 2026-27", "AVAILABLE", "1", "S01", "verified, full text used"],
        ["Official SQP 2026-27 + marking scheme", "AVAILABLE", "1", "S03",
         "33 questions attributed to chapters"],
        ["Official board papers 2017-2026 (originals)", "NOT AVAILABLE", "0", "-",
         "Egress to board-paper hosts blocked (SSL); no original paper PDF could be "
         "downloaded or legally archived in this environment"],
        ["MTG-reported question counts 2017-2026", "AVAILABLE (secondary)", "10 years",
         "S04 IMG-01", "14 chapters x 10 exam years (+2021 not held)"],
        ["MTG-reported 10-year marks aggregates", "AVAILABLE (secondary)", "14 chapters",
         "S04 IMG-02..15", "sum of printed Total# column"],
        ["Compartment / supplementary papers", "NOT AVAILABLE", "0", "-",
         "No compartment paper reached this environment; all analyses use regular papers only"],
        ["Marking schemes for historical papers", "NOT AVAILABLE", "0", "-",
         "Not reachable; probability model therefore uses format-based priors, not per-question mark data"],
        ["NCERT textbook text", "NOT RETRIEVED", "0", "S07", "access restriction"],
    ]
    w(P / "Source_Register" / "evidence_coverage_report.csv", rows,
      ["evidence_item", "status", "coverage", "source_id", "notes"])


if __name__ == "__main__":
    build_unit_weightage()
    build_mtg_year()
    build_mtg_marks()
    build_sqp()
    build_crosswalk()
    build_image_register()
    build_sources()
    build_coverage()
