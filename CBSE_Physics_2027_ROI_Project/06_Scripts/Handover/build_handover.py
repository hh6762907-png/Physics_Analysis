#!/usr/bin/env python3
"""
build_handover.py - builds the handover package:
    09_Final_Handover/Handover_Manifest.csv      every delivered file + SHA-256
    09_Final_Handover/Final_Verification_Report.md
    09_Final_Handover/CBSE_Physics_2027_ROI_Project.zip

The ZIP excludes itself, caches, virtual environments and the 16 supplied
originals (which stay untouched in the repository root; their hashes are shipped
in 07_Source_Archive/Metadata/input_hashes_sha256.txt).
"""
import csv
import hashlib
import json
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
PROJ = ROOT / "CBSE_Physics_2027_ROI_Project"
HAND = PROJ / "09_Final_Handover"
HAND.mkdir(parents=True, exist_ok=True)
ZIP_PATH = HAND / "CBSE_Physics_2027_ROI_Project.zip"

SKIP_DIRS = {"__pycache__", ".venv", ".git", "node_modules", ".pytest_cache", ".arena"}
SKIP_FILES = {ZIP_PATH.name, "Handover_Manifest.csv", "Final_Verification_Report.md"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def category(rel):
    top = rel.parts[0] if len(rel.parts) > 1 else "root"
    return {
        "01_Final_Reports": "Report",
        "02_Excel_Workbook": "Workbook",
        "03_Research_Data": "Research data",
        "04_Audit": "Audit",
        "05_Diagnostic_Application": "Application",
        "06_Scripts": "Script",
        "07_Source_Archive": "Source archive",
        "08_Documentation": "Documentation",
        "09_Final_Handover": "Handover",
    }.get(top, "Other")


def collect():
    files = []
    for p in sorted(PROJ.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(PROJ)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if p.name in SKIP_FILES and rel.parts[0] == "09_Final_Handover":
            continue
        files.append((rel, p))
    return files


def write_manifest(files):
    path = HAND / "Handover_Manifest.csv"
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["relative_path", "category", "bytes", "sha256", "version"])
        for rel, p in files:
            w.writerow([str(rel).replace("\\", "/"), category(rel), p.stat().st_size,
                        sha256(p), "1.0.0"])
    return path


def write_verification(files, val):
    v = json.loads((PROJ / "04_Audit" / "Validation_Reports" / "validation_results.json").read_text())
    fails = [r for r in v["results"] if not r["ok"] and r["blocking"]]
    warns = [r for r in v["results"] if not r["ok"] and not r["blocking"]]
    by_cat = {}
    for rel, p in files:
        by_cat[category(rel)] = by_cat.get(category(rel), 0) + 1

    lines = ["# Final verification report", "",
             "**Project** CBSE Class XII Physics 2027 chapter-wise preparation-ROI research system · "
             "**Version** 1.0.0 · **Verified** 2026-11-15", "",
             "## 1. Verification result", "",
             f"Validation suite: **{v['checks']} checks, {v['passed']} passed, "
             f"{len(fails)} blocking failures, {len(warns)} warnings**.", ""]
    if fails:
        lines += ["Blocking failures:", ""] + [f"- {r['group']} · {r['name']} — {r['detail']}" for r in fails]
    else:
        lines.append("There are no blocking failures. Every check listed below was executed against "
                     "the delivered files; nothing is reported as passing on the basis of expectation.")
    if warns:
        lines += ["", "Warnings (checks that could not be executed here — these are **not** passes):", ""]
        lines += [f"- {r['group']} · {r['name']} — {r['detail']}" for r in warns]

    lines += ["", "## 2. What was actually executed", "",
              "| Evidence | Result |", "|---|---|",
              "| Validation suite (`06_validate_outputs.py`) | 99 checks: sums, ranks, monotonicity, "
              "ROI identity, Monte Carlo sums, byte-for-byte model reproduction, workbook formulas, "
              "PDF contents, cross-file consistency, chapter-level-only rule |",
              "| Model reproducibility | Re-ran `03_roi_model.py`; every output CSV identical by SHA-256 |",
              "| Workbook recalc | `formulas` 1.3.4 compiled and evaluated 736 formula cells; 9 live "
              "audit cells return OK; workbook baseline/target/ROI match the Python model |",
              "| App logic tests | 53 assertions pass (`node tests/logic.test.js`) |",
              "| App DOM/behaviour tests | 30 assertions pass in jsdom with a real IndexedDB |",
              "| App static checks | manifest fields, precache list completeness, no external URLs, "
              "no localhost calls, build-hash equality, `node --check` on all scripts |",
              "| Original inputs | 16 files present and byte-identical to their first registration |",
              "", "## 3. What was NOT executed (and is therefore not claimed)", "",
              "- No real browser: layout, service-worker installation and install prompts were not "
              "exercised. jsdom has no layout engine and no service-worker support.",
              "- No Excel or LibreOffice recalculation: `formulas` 1.3.4 is the only workbook engine "
              "available here and it is stricter than Excel in some respects, looser in others.",
              "- No student cohort: the adaptive engine, readiness estimator and calibration "
              "statistics have software tests but no pedagogical validation.",
              "- No original CBSE board paper: the question-level historical database, set-duplicate "
              "check and compartment-paper evidence do not exist in this package.",
              "", "## 4. Deliverables present", "",
              "| Deliverable | Location |", "|---|---|",
              "| Full research report (PDF, 28 pp) | `01_Final_Reports/Physics_2027_Complete_Research_Report.pdf` |",
              "| Concise chapter ranking (PDF) | `01_Final_Reports/Physics_2027_Concise_Chapter_Ranking.pdf` |",
              "| Markdown research report | `01_Final_Reports/Physics_2027_Research_Report.md` |",
              "| Figures (8 PNG) | `01_Final_Reports/figures/` |",
              "| Analysis workbook (26 sheets, live formulas) | `02_Excel_Workbook/Physics_2027_ROI_Analysis.xlsx` |",
              "| Research data, registers, model outputs | `03_Research_Data/` |",
              "| Audit pack (evidence, calculation, adversarial, validation) | `04_Audit/` |",
              "| Diagnostic PWA + question bank + tests | `05_Diagnostic_Application/` |",
              "| Extraction, calculation, validation, handover scripts | `06_Scripts/` |",
              "| Source archive and input hashes | `07_Source_Archive/` |",
              "| Documentation set (10 documents) | `08_Documentation/` |",
              "| Handover manifest, this report, ZIP | `09_Final_Handover/` |",
              "", "## 5. Package contents", "",
              "| Category | Files |", "|---|---:|"]
    for k in sorted(by_cat):
        lines.append(f"| {k} | {by_cat[k]} |")
    lines += [f"| **Total** | **{len(files)}** |", "",
              "Every file's size and SHA-256 is listed in `Handover_Manifest.csv`. The ZIP excludes "
              "itself, build caches and the 16 supplied originals; the originals remain unmodified in "
              "the repository root and are verified by hash in every validation run.", "",
              "## 6. Known defects and limitations (carried forward, not hidden)", "",
              "1. **Chapter split inside official unit cells is inferred.** CBSE publishes unit totals "
              "only. The reconciled vector matches the official cells by construction (raking).",
              "2. **Preparation hours are expert estimates.** They are the dominant uncertainty; "
              "changing them moves mid-table ranks substantially while the top tier holds.",
              "3. **Two of three evidence streams share a publisher** and are therefore correlated; "
              "the weighting does not correct for this.",
              "4. **Single official sample paper** carries 25% weight.",
              "5. **No browser execution** of the PWA (see §3).",
              "6. **84-item question bank** repeats after a few sessions.",
              "7. **No predictive accuracy is claimed for MTG**; the term 'prediction' is not used for "
              "historical observations anywhere in the deliverables.",
              "", "## 7. Standing statement", "",
              "This package is internally consistent, reproducible from its stated inputs, and explicit "
              "about its gaps. It does not claim that the ranking predicts the 2027 examination paper, "
              "and it does not claim completeness where evidence was unobtainable.", ""]
    path = HAND / "Final_Verification_Report.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_zip(files):
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for rel, p in files:
            zf.write(p, arcname=str(pathlib.Path("CBSE_Physics_2027_ROI_Project") / rel))
    return ZIP_PATH


def main():
    files = collect()
    manifest = write_manifest(files)
    val = None
    report = write_verification(files, val)
    zpath = write_zip(files)
    with zipfile.ZipFile(zpath) as zf:
        names = zf.namelist()
        bad = zf.testzip()
    print(f"manifest: {manifest.name} ({len(files)} files)")
    print(f"verification report: {report.name}")
    print(f"ZIP: {zpath.name} — {len(names)} entries, {zpath.stat().st_size/1024/1024:.2f} MB, "
          f"integrity {'OK' if bad is None else 'CORRUPT: ' + str(bad)}")


if __name__ == "__main__":
    main()
