#!/usr/bin/env python3
"""
06_validate_outputs.py
======================
Independent validation of the delivered artefacts. It re-reads the files on
disk (never the in-memory model) and checks structure, arithmetic, internal
consistency, provenance and packaging rules.

    python 06_validate_outputs.py

Writes:
    04_Audit/Validation_Reports/validation_report.md
    04_Audit/Validation_Reports/validation_results.json
Exit code 0 only if every blocking check passes.
"""
import csv
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
PROJ = ROOT / "CBSE_Physics_2027_ROI_Project"
DATA = PROJ / "03_Research_Data"
OUTD = PROJ / "03_Research_Data" / "Model_Outputs"
REPORTS = PROJ / "01_Final_Reports"
APP = PROJ / "05_Diagnostic_Application"
PWA = APP / "PWA"

results = []


def check(group, name, ok, detail="", blocking=True):
    results.append({"group": group, "name": name, "ok": bool(ok),
                    "detail": str(detail), "blocking": blocking})
    return ok


def load_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def sha256(path):
    h = hashlib.sha256()
    h.update(pathlib.Path(path).read_bytes())
    return h.hexdigest()


# --------------------------------------------------------------- A. inputs
def check_inputs():
    g = "A. Supplied originals unchanged"
    hashfile = PROJ / "07_Source_Archive" / "Metadata" / "input_hashes_sha256.txt"
    if not hashfile.exists():
        return check(g, "hash register present", False, "missing " + str(hashfile))
    rows = [ln.split() for ln in hashfile.read_text().splitlines() if ln.strip() and not ln.startswith("#")]
    check(g, "hash register lists 16 inputs", len(rows) == 16, f"{len(rows)} rows")
    bad, missing = [], []
    for row in rows:
        digest, name = row[0], row[-1]
        path = ROOT / pathlib.Path(name).name
        if not path.exists():
            missing.append(name)
        elif sha256(path) != digest:
            bad.append(name)
    check(g, "all 16 originals still present", not missing, ", ".join(missing))
    check(g, "all 16 originals byte-identical to first registration", not bad, ", ".join(bad))


# ---------------------------------------------------------------- B. model
def check_model():
    g = "B. Model outputs"
    rank = load_csv(OUTD / "roi_primary_ranking.csv")
    exp = load_csv(OUTD / "chapter_exposure_by_stream.csv")
    mc = load_csv(OUTD / "monte_carlo_results.csv")
    scr = load_csv(OUTD / "scenario_rankings.csv")
    sens = load_csv(OUTD / "sensitivity_analysis.csv")

    check(g, "ranking has 14 chapters", len(rank) == 14, len(rank))
    ranks = sorted(int(r["rank"]) for r in rank)
    check(g, "ranks are the integers 1-14, each once", ranks == list(range(1, 15)), ranks)
    total = sum(float(r["exposure_marks"]) for r in rank)
    check(g, "reconciled exposure sums to 70.00", abs(total - 70) < 1e-6, f"{total:.6f}")
    check(g, "baseline + additional = target for every chapter",
          all(abs(float(r["baseline_marks"]) + float(r["additional_marks"]) - float(r["target_marks"])) < 5e-3
              for r in rank))
    check(g, "no negative or zero hours", all(float(r["additional_hours"]) > 0 for r in rank))
    check(g, "ROI = additional marks / additional hours (within rounding)",
          all(abs(float(r["additional_marks"]) / float(r["additional_hours"]) -
                  float(r["incremental_roi"])) < 0.006 for r in rank))
    check(g, "ROI order is monotone with rank",
          all(float(rank[i]["incremental_roi"]) >= float(rank[i + 1]["incremental_roi"]) - 1e-9
              for i in range(len(rank) - 1)))
    check(g, "tiers are single letters A-G",
          all(re.fullmatch(r"Tier [A-G]", r["tier"]) for r in rank),
          sorted({r["tier"] for r in rank}))
    check(g, "grades are A, B or C", all(r["grade"] in "ABC" for r in rank))
    check(g, "confidence scores lie in 0-100",
          all(0 <= float(r["confidence_score"]) <= 100 for r in rank))

    tgt = sum(float(r["target_marks"]) for r in rank)
    check(g, "target marks below the 70-mark ceiling", tgt < 70, f"{tgt:.2f}")
    need = ("stream_A_historical_counts_recency", "stream_A_last5_equal", "stream_A_last10_equal",
            "stream_B_mtg_marks_10yr", "stream_C_official_sqp", "reconciled_gross_marks",
            "deletion_share_2026_27", "exposure_marks_2027")
    check(g, "exposure table carries every evidence stream plus the reconciled vector",
          all(k in exp[0] for k in need), [k for k in need if k not in exp[0]])
    check(g, "SQP stream sums to 70 marks",
          abs(sum(float(r["stream_C_official_sqp"]) for r in exp) - 70) < 0.01,
          f"{sum(float(r['stream_C_official_sqp']) for r in exp):.2f}")

    p3 = sum(float(r["p_top3"]) for r in mc)
    p5 = sum(float(r["p_top5"]) for r in mc)
    check(g, "Monte Carlo P(top 3) sums to 3.0", abs(p3 - 3) < 0.01, f"{p3:.4f}")
    check(g, "Monte Carlo P(top 5) sums to 5.0", abs(p5 - 5) < 0.01, f"{p5:.4f}")
    check(g, "rank p05 <= median <= p95 for every chapter",
          all(float(r["rank_p05"]) <= float(r["median_rank"]) <= float(r["rank_p95"]) for r in mc))
    check(g, "ROI p05 <= median <= p95 for every chapter",
          all(float(r["roi_p05"]) <= float(r["roi_median"]) <= float(r["roi_p95"]) for r in mc))

    check(g, "scenario grid holds 27 combinations and 4 evidence streams",
          len(scr) == 14 * 31, len(scr))
    check(g, "sensitivity analysis holds 16 variants", len(sens) == 14 * 16, len(sens))

    # reproducibility: re-running the model must not change the CSVs
    before = {p.name: sha256(p) for p in OUTD.glob("*.csv")}
    proc = subprocess.run([sys.executable, str(PROJ / "06_Scripts" / "Calculations" / "03_roi_model.py")],
                          capture_output=True, text=True, cwd=str(ROOT))
    after = {p.name: sha256(p) for p in OUTD.glob("*.csv")}
    check(g, "model script re-runs without error", proc.returncode == 0, proc.stderr[-300:])
    check(g, "model re-run reproduces every CSV byte-for-byte", before == after,
          [k for k in before if before.get(k) != after.get(k)])


# --------------------------------------------------------------- C. units
def check_units():
    g = "C. Official unit constraint"
    rows = [r for r in load_csv(OUTD / "unit_weightage_constraint_check.csv")
            if r["official_marks"] and not r["unit_group"].lower().startswith(("total", "all"))]
    official = [float(r["official_marks"]) for r in rows]
    check(g, "official cells are 16/17/18/12/7", official == [16, 17, 18, 12, 7], official)
    check(g, "official cells total 70", abs(sum(official) - 70) < 1e-9)
    final = sum(float(r["final_total_after_deletion"]) for r in rows)
    check(g, "deletion-adjusted vector still totals 70", abs(final - 70) < 0.01, f"{final:.4f}")
    check(g, "deviations from official cells are reported with sign",
          all("final_deviation_pct" in r for r in rows))
    worst = max(rows, key=lambda r: abs(float(r["final_deviation_pct"])))
    check(g, "largest deviation is documented (no silent drift)",
          abs(float(worst["final_deviation_pct"])) < 15,
          f"{worst['unit_group']} {worst['final_deviation_pct']}%")


# ---------------------------------------------------------- D. question bank
def check_bank():
    g = "D. Question bank"
    master = APP / "Question_Bank" / "physics_question_bank_v1.json"
    dc = APP / "PWA" / "data" / "question_bank.json"
    if not master.exists():
        return check(g, "question bank present", False, "missing")
    bank = json.loads(master.read_text())
    items = bank["items"]
    check(g, "84 items", len(items) == 84, len(items))
    check(g, "6 items per chapter", all(sum(1 for i in items if i["chapter"] == c) == 6 for c in range(1, 15)))
    check(g, "all 14 chapters covered", sorted({i["chapter"] for i in items}) == list(range(1, 15)))
    check(g, "ids unique", len({i["id"] for i in items}) == len(items))
    check(g, "choice items have four options and an in-range key",
          all(len(i["options"]) == 4 and i["answer_index"] in (0, 1, 2, 3)
              for i in items if i["options"]))
    check(g, "written items carry a rubric and model answer",
          all(i["rubric"] and i["answer_text"] for i in items if not i["options"]))
    check(g, "every item is labelled ORIGINAL",
          all(i["source_class"] == "ORIGINAL" for i in items))
    check(g, "no item claims to be a previous-year question",
          not any("previous year question" in json.dumps(i).lower().replace("not a previous-year question", "")
                  for i in items))
    check(g, "app data copy is identical to the master bank",
          dc.exists() and sha256(dc) == sha256(master))
    per_ch = {c: sum(i["marks"] for i in items if i["chapter"] == c) for c in range(1, 15)}
    check(g, "every chapter carries at least 7 marks of practice material",
          all(v >= 7 for v in per_ch.values()), per_ch)


# ----------------------------------------------------------------- E. PWA
def check_pwa():
    g = "E. Offline application"
    required = ["index.html", "styles.css", "logic.js", "app.js", "sw.js", "manifest.webmanifest",
                "icons/icon-192.png", "icons/icon-512.png", "icons/icon-maskable-512.png",
                "data/research_ranking.json", "data/question_bank.json"]
    missing = [r for r in required if not (PWA / r).exists()]
    check(g, "all deployable files present", not missing, missing)

    mf = json.loads((PWA / "manifest.webmanifest").read_text())
    for key in ("name", "short_name", "start_url", "display", "icons", "theme_color", "scope"):
        check(g, f"manifest declares {key}", key in mf)
    check(g, "manifest has a 192px icon", any(i["sizes"] == "192x192" for i in mf["icons"]))
    check(g, "manifest has a 512px icon", any(i["sizes"] == "512x512" for i in mf["icons"]))
    check(g, "manifest has a maskable icon", any(i.get("purpose") == "maskable" for i in mf["icons"]))

    sw = (PWA / "sw.js").read_text()
    listed = re.findall(r'"([^"]+)"', sw.split("var SHELL", 1)[1].split("];", 1)[0])
    missing_sw = [f for f in listed if f != "./" and not (PWA / f).exists()]
    check(g, "every precached asset exists", not missing_sw, missing_sw)
    check(g, "service worker caches the question bank", any("question_bank" in f for f in listed))
    check(g, "service worker ignores cross-origin requests",
          "url.origin !== self.location.origin" in sw)

    external = []
    for f in ("index.html", "app.js", "logic.js", "styles.css", "sw.js"):
        text = (PWA / f).read_text()
        for m in re.finditer(r"https?://[^\s\"'<>)]+", text):
            external.append(f + " -> " + m.group(0))
    check(g, "no external network dependencies in the app shell", not external, external)
    check(g, "no app code calls localhost",
          not any("localhost" in (PWA / f).read_text() or "127.0.0.1" in (PWA / f).read_text()
                  for f in ("index.html", "app.js", "logic.js", "sw.js")))

    build = json.loads((PWA / "build_manifest.json").read_text())
    stale = [a["path"] for a in build["assets"]
             if sha256(PWA / a["path"]) != a["sha256"]]
    check(g, "build manifest hashes match the deployed files", not stale, stale)

    # syntax: node --check on every script
    node = subprocess.run(["node", "--version"], capture_output=True, text=True)
    if node.returncode == 0:
        bad = []
        for f in ("logic.js", "app.js", "sw.js"):
            r = subprocess.run(["node", "--check", str(PWA / f)], capture_output=True, text=True)
            if r.returncode != 0:
                bad.append(f + ": " + r.stderr.strip().splitlines()[-1])
        check(g, "all scripts parse under Node", not bad, bad)
    else:
        check(g, "all scripts parse under Node", False, "node not available", blocking=False)

    # behaviour tests
    tests = APP / "tests"
    r = subprocess.run(["node", str(tests / "logic.test.js")], capture_output=True, text=True)
    tail = (r.stdout.strip().splitlines() or ["no output"])[-1]
    check(g, "logic test suite passes", r.returncode == 0, tail)

    env_jsdom = pathlib.Path("/tmp/jsdomtest/node_modules")
    if env_jsdom.exists():
        r = subprocess.run(["node", str(tests / "dom.smoke.test.js")], capture_output=True, text=True,
                           env={"NODE_PATH": str(env_jsdom), "PATH": "/usr/bin:/bin:/usr/local/bin"})
        tail = (r.stdout.strip().splitlines() or ["no output"])[-1]
        check(g, "DOM smoke test passes in jsdom", r.returncode == 0, tail)
    else:
        check(g, "DOM smoke test passes in jsdom", False,
              "skipped: dev-only jsdom/fake-indexeddb not installed in this environment",
              blocking=False)


# ------------------------------------------------------------- F. workbook
def check_workbook():
    g = "F. Analysis workbook"
    path = PROJ / "02_Excel_Workbook" / "Physics_2027_ROI_Analysis.xlsx"
    check(g, "workbook exists", path.exists())
    if not path.exists():
        return
    try:
        from openpyxl import load_workbook
    except Exception as e:  # pragma: no cover
        return check(g, "openpyxl available", False, str(e), blocking=False)
    wb = load_workbook(path)
    expected = ["01_Instructions", "02_Dashboard", "03_Inputs", "04_Final_Ranking",
                "05_Historical_Evidence", "06_MTG_Evidence", "07_Sample_Paper",
                "08_Reconciliation", "09_Choice_Model", "10_Hours", "11_ROI_Incremental",
                "12_ROI_Total", "13_Confidence", "14_Scenario_Control", "15_Scenario_Grid",
                "16_Sensitivity", "17_Uncertainty", "18_Unit_Constraint", "19_Syllabus_Crosswalk",
                "20_Source_Register", "21_Image_Register", "22_Evidence_Coverage",
                "23_Audit_Checks", "24_Methodology", "25_Personal_Diagnostic", "26_Version_History"]
    check(g, "26 required sheets present", [s for s in expected if s not in wb.sheetnames] == [],
          [s for s in expected if s not in wb.sheetnames])
    formulas, unbalanced, badref = 0, [], []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                v = c.value
                if isinstance(v, str) and v.startswith("="):
                    formulas += 1
                    if v.count("(") != v.count(")"):
                        unbalanced.append(f"{ws.title}!{c.coordinate}")
                    if re.search(r"(?<![A-Za-z0-9_'])\d\d_[A-Za-z_]+!", v):
                        badref.append(f"{ws.title}!{c.coordinate}")
    check(g, "workbook carries live formulas", formulas > 600, f"{formulas} formula cells")
    check(g, "no formula has unbalanced parentheses", not unbalanced, unbalanced[:5])
    check(g, "all digit-leading sheet references are quoted", not badref, badref[:5])
    dash = wb["02_Dashboard"]
    check(g, "dashboard references model cells", any(isinstance(c.value, str) and c.value.startswith("=")
                                                    for row in dash.iter_rows() for c in row))
    dv = wb["14_Scenario_Control"].data_validations.dataValidation
    check(g, "scenario control has data validation", len(dv) > 0, f"{len(dv)} rules")
    check(g, "workbook embeds charts", sum(len(ws._charts) for ws in wb.worksheets) >= 1,
          sum(len(ws._charts) for ws in wb.worksheets))
    check(g, "audit sheet exists with pass/fail cells",
          wb["23_Audit_Checks"].max_row > 5, wb["23_Audit_Checks"].max_row)


# ----------------------------------------------------------------- G. PDF
def check_pdf():
    g = "G. PDF reports"
    full = REPORTS / "Physics_2027_Complete_Research_Report.pdf"
    conc = REPORTS / "Physics_2027_Concise_Chapter_Ranking.pdf"
    check(g, "full report exists", full.exists())
    check(g, "concise ranking exists", conc.exists())
    try:
        from pypdf import PdfReader
    except Exception:
        return check(g, "pypdf available", False, "missing", blocking=False)
    if full.exists():
        r = PdfReader(str(full))
        text = "\n".join((p.extract_text() or "") for p in r.pages)
        check(g, "full report has 25-40 pages", 25 <= len(r.pages) <= 40, len(r.pages))
        for token in ("16", "17", "18", "12", "7", "Semiconductor", "70"):
            check(g, f"full report mentions {token}", token in text)
        check(g, "full report carries the ranking table (all 14 chapters)",
              all(ch in text for ch in ("Electric Charges and Fields", "Nuclei",
                                        "Alternating Current", "Wave Optics")))
        check(g, "full report states the limitations section", "Limitation" in text or "limitation" in text)
        blank = [i + 1 for i, pg in enumerate(r.pages) if len((pg.extract_text() or "").strip()) < 60]
        check(g, "full report has no blank pages", not blank, blank)
        check(g, "full report does not present a predictive-accuracy score for MTG",
              not re.search(r"MTG[^.]{0,80}(accuracy|hit rate)[^.]{0,20}\d+%", text, re.I),
              "no accuracy claim found" )
    if conc.exists():
        r = PdfReader(str(conc))
        text = "\n".join((p.extract_text() or "") for p in r.pages)
        check(g, "concise ranking has 1-4 pages", 1 <= len(r.pages) <= 4, len(r.pages))
        blank = [i + 1 for i, pg in enumerate(r.pages) if len((pg.extract_text() or "").strip()) < 60]
        check(g, "concise ranking has no blank pages", not blank, blank)
        check(g, "concise ranking lists 14 chapters",
              sum(1 for c in range(1, 15) if re.search(rf"\bC{c}\b", text)) == 14)


# ------------------------------------------------------------ H. Markdown
def check_markdown():
    g = "H. Markdown report"
    path = REPORTS / "Physics_2027_Research_Report.md"
    check(g, "markdown report exists", path.exists())
    if not path.exists():
        return
    text = path.read_text()
    rows = re.findall(r"^\| \d+ \| C\d+ ", text, re.M)
    check(g, "ranked tables cover all 14 chapters in each of the two rankings", len(rows) == 28,
          f"{len(rows)} rows")
    covered = sorted({int(m) for m in re.findall(r"^\| \d+ \| C(\d+) ", text, re.M)})
    check(g, "both tables name the same 14 chapters", covered == list(range(1, 15)), covered)
    rank = load_csv(OUTD / "roi_primary_ranking.csv")
    missing = [r["chapter_no"] for r in rank
               if f"{float(r['incremental_roi']):.2f}" not in text]
    check(g, "every ROI value from the CSV appears in the report", not missing, missing)
    check(g, "report states the 70-mark constraint", "70" in text)
    check(g, "report discloses the missing question-level database",
          "question-level historical database" in text)
    check(g, "report discloses hour estimates as expert judgement", "expert" in text.lower())


# ------------------------------------------------- I. cross-file consistency
def check_consistency():
    g = "I. Cross-file consistency"
    rank = load_csv(OUTD / "roi_primary_ranking.csv")
    research = json.loads((PWA / "data" / "research_ranking.json").read_text())
    app_roi = {c["chapter"]: c["researchRoi"] for c in research["chapters"]}
    csv_roi = {int(r["chapter_no"]): round(float(r["incremental_roi"]), 4) for r in rank}
    check(g, "app ranking data matches the model CSV", app_roi == csv_roi,
          {k: (app_roi.get(k), csv_roi.get(k)) for k in csv_roi if app_roi.get(k) != csv_roi[k]})
    app_exp = {c["chapter"]: c["exposureMarks"] for c in research["chapters"]}
    csv_exp = {int(r["chapter_no"]): round(float(r["exposure_marks"]), 2) for r in rank}
    check(g, "app exposure data matches the model CSV", app_exp == csv_exp)
    summ = PROJ / "03_Research_Data" / "Model_Outputs" / "model_metadata.json"
    if summ.exists():
        meta = json.loads(summ.read_text())
        check(g, "model metadata records the evidence weights",
              "evidence_weights" in meta and abs(sum(meta["evidence_weights"].values()) - 1) < 1e-9,
              meta.get("evidence_weights"))


# ------------------------------------------------------- J. topic discipline
def check_topic_discipline():
    g = "J. Chapter-level-only rule"
    forbidden = ["topic-wise roi", "topic-wise ranking", "topic level ranking", "topic-level ranking",
                 "topic priority list", "topic-wise priority", "topic-wise marks distribution",
                 "topic-wise hours", "topic roi", "sub-topic ranking"]
    targets = []
    targets += list(REPORTS.glob("*.md"))
    targets += list(REPORTS.glob("*.pdf"))
    targets += [PROJ / "02_Excel_Workbook" / "Physics_2027_ROI_Analysis.xlsx"]
    targets += list(APP.glob("PWA/*.html")) + list(APP.glob("PWA/*.js"))
    hits = []
    for t in targets:
        if not t.exists():
            continue
        if t.suffix == ".pdf":
            try:
                from pypdf import PdfReader
                text = "\n".join((p.extract_text() or "") for p in PdfReader(str(t)).pages)
            except Exception:
                text = ""
        elif t.suffix == ".xlsx":
            from openpyxl import load_workbook
            wb = load_workbook(t)
            text = " ".join(str(c.value) for ws in wb.worksheets for row in ws.iter_rows()
                            for c in row if c.value is not None).lower()
        else:
            text = t.read_text().lower()
        for phrase in forbidden:
            start = 0
            while True:
                idx = text.find(phrase, start)
                if idx < 0:
                    break
                context = text[max(0, idx - 60):idx].lower()
                negated = any(w in context for w in ("no ", "not ", "never", "without", "absence",
                                                     "contains no", "n't"))
                if not negated:
                    hits.append(f"{t.name}: {phrase} (context: ...{context[-40:]})")
                start = idx + 1
    check(g, "no topic-level analysis phrase in any deliverable", not hits, hits)


# ------------------------------------------------------------ K. packaging
def check_packaging():
    g = "K. Project packaging"
    top = sorted(p.name for p in PROJ.iterdir() if p.is_dir())
    expected = ["01_Final_Reports", "02_Excel_Workbook", "03_Research_Data", "04_Audit",
                "05_Diagnostic_Application", "06_Scripts", "07_Source_Archive",
                "08_Documentation", "09_Final_Handover"]
    check(g, "the nine top-level folders exist", [e for e in expected if e not in top] == [],
          [e for e in expected if e not in top])
    docs = PROJ / "08_Documentation"
    check(g, "documentation set has at least eight documents",
          len(list(docs.glob("*.md"))) >= 8, len(list(docs.glob("*.md"))) if docs.exists() else 0)
    scripts = PROJ / "06_Scripts"
    check(g, "scripts present in extraction/calculations/validation",
          all((scripts / d).exists() for d in ("Extraction", "Calculations", "Validation")))
    archive = PROJ / "07_Source_Archive" / "Metadata" / "input_hashes_sha256.txt"
    check(g, "source archive retains the input hash register", archive.exists())
    zip_path = PROJ / "09_Final_Handover" / "CBSE_Physics_2027_ROI_Project.zip"
    if zip_path.exists():
        with zipfile.ZipFile(zip_path) as zf:
            names = zf.namelist()
        check(g, "handover ZIP opens and contains the reports", len(names) > 50, len(names))
        check(g, "handover ZIP contains no supplied original images",
              not any(re.search(r"IMG\d{14}\.jpg$", n) for n in names))
    else:
        check(g, "handover ZIP exists", False, "not built yet", blocking=False)


def main():
    for fn in (check_inputs, check_model, check_units, check_bank, check_pwa, check_workbook,
               check_pdf, check_markdown, check_consistency, check_topic_discipline, check_packaging):
        try:
            fn()
        except Exception as e:  # a crashed check is a failed check, never a silent pass
            check(fn.__name__, "check ran without crashing", False, repr(e))

    blocking_fail = [r for r in results if not r["ok"] and r["blocking"]]
    warnings = [r for r in results if not r["ok"] and not r["blocking"]]
    passed = sum(1 for r in results if r["ok"])

    REPORTS_DIR = PROJ / "04_Audit" / "Validation_Reports"
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "validation_results.json").write_text(json.dumps({
        "generated": "2026-11-15", "checks": len(results), "passed": passed,
        "failed_blocking": len(blocking_fail), "warnings": len(warnings),
        "results": results}, indent=1), encoding="utf-8")

    lines = ["# Validation report", "",
             "Generated by `06_Scripts/Validation/06_validate_outputs.py` on the delivered files. "
             "The validator re-reads every artefact from disk and recomputes the model; it does "
             "not trust in-memory values.", "",
             f"**{len(results)} checks · {passed} passed · {len(blocking_fail)} blocking failures · "
             f"{len(warnings)} warnings**", ""]
    group = None
    for r in results:
        if r["group"] != group:
            group = r["group"]
            lines += ["", f"## {group}", "", "| Check | Result | Detail |", "|---|---|---|"]
        mark = "PASS" if r["ok"] else ("FAIL" if r["blocking"] else "WARN")
        detail = r["detail"].replace("|", "/")[:180]
        lines.append(f"| {r['name']} | {mark} | {detail} |")
    lines += ["", "## Interpretation", "",
              "PASS means the check was executed against the delivered files and met its assertion. "
              "WARN means the check could not be executed in this environment (for example a "
              "dev-only dependency is absent); it is not a pass and is not counted as one. "
              "FAIL blocks handover.", ""]
    (REPORTS_DIR / "validation_report.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"{len(results)} checks, {passed} passed, {len(blocking_fail)} blocking failures, "
          f"{len(warnings)} warnings -> {REPORTS_DIR.relative_to(ROOT)}")
    for r in blocking_fail:
        print("  FAIL", r["group"], "|", r["name"], "->", r["detail"][:160])
    for r in warnings:
        print("  WARN", r["group"], "|", r["name"], "->", r["detail"][:160])
    return 0 if not blocking_fail else 1


if __name__ == "__main__":
    sys.exit(main())
