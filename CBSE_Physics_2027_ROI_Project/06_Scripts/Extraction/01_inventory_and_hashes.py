#!/usr/bin/env python3
"""
01_inventory_and_hashes.py
--------------------------
Builds the input file inventory for the repository (originals only), records
sizes, modification times, SHA-256 hashes and basic readability checks, and
writes:
    03_Research_Data/Source_Register/input_inventory.csv
    07_Source_Archive/Metadata/input_hashes_sha256.txt

Read-only with respect to the supplied originals. Never modifies inputs.
"""
import csv
import hashlib
import os
import pathlib
import datetime

ROOT = pathlib.Path(__file__).resolve().parents[3]          # repository root
PROJ = ROOT / "CBSE_Physics_2027_ROI_Project"
OUT_CSV = PROJ / "03_Research_Data" / "Source_Register" / "input_inventory.csv"
OUT_HASH = PROJ / "07_Source_Archive" / "Metadata" / "input_hashes_sha256.txt"

EXPECTED_IMAGES = 15
EXPECTED_PDFS = 1


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def can_open_pdf(path: pathlib.Path) -> tuple[bool, str]:
    try:
        from pypdf import PdfReader
        r = PdfReader(str(path))
        return True, f"{len(r.pages)} pages"
    except Exception as exc:                                   # pragma: no cover
        return False, f"error: {exc}"


def image_dims(path: pathlib.Path) -> tuple[bool, str]:
    try:
        from PIL import Image
        with Image.open(path) as im:
            im.verify()
        with Image.open(path) as im:
            return True, f"{im.size[0]}x{im.size[1]} {im.format}"
    except Exception as exc:                                   # pragma: no cover
        return False, f"error: {exc}"


def main() -> None:
    rows = []
    hashes = []
    supplied = sorted(
        p for p in ROOT.iterdir()
        if p.is_file() and not p.name.startswith(".")
    )
    for p in supplied:
        st = p.stat()
        ext = p.suffix.lower()
        if ext in {".jpg", ".jpeg", ".png"}:
            kind, ok, detail = "photograph (MTG Champion trend analysis)", *image_dims(p)
        elif ext == ".pdf":
            kind, ok, detail = "syllabus document (PDF)", *can_open_pdf(p)
        else:
            kind, ok, detail = "other", True, ""
        rows.append({
            "filename": p.name,
            "extension": ext,
            "size_bytes": st.st_size,
            "modified_utc": datetime.datetime.utcfromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
            "expected_file_type": kind,
            "opens_successfully": "YES" if ok else "NO",
            "technical_detail": detail,
            "sha256": sha256(p),
        })
        hashes.append(f"{rows[-1]['sha256']}  {p.name}")

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    OUT_HASH.parent.mkdir(parents=True, exist_ok=True)
    OUT_HASH.write_text("\n".join(hashes) + "\n", encoding="utf-8")

    n_img = sum(1 for r in rows if r["extension"] in {".jpg", ".jpeg", ".png"})
    n_pdf = sum(1 for r in rows if r["extension"] == ".pdf")
    print(f"inventory: {len(rows)} files | images={n_img} (expected {EXPECTED_IMAGES}) "
          f"| pdf={n_pdf} (expected {EXPECTED_PDFS})")
    print(f"all readable: {all(r['opens_successfully']=='YES' for r in rows)}")
    print(f"wrote {OUT_CSV.relative_to(ROOT)}")
    print(f"wrote {OUT_HASH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
