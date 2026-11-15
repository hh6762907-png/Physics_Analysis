#!/usr/bin/env python3
"""
09_build_pwa.py
---------------
Builds the deployable PWA folder from the application source and writes an
asset manifest with SHA-256 hashes. Copy-only build: no bundling, no minifying,
so the deployed files are byte-identical to the reviewed source.

    python 09_build_pwa.py            build 05_Diagnostic_Application/PWA
    python 09_build_pwa.py --check    verify the build is current
"""
import argparse
import hashlib
import json
import shutil
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
APP = ROOT / "CBSE_Physics_2027_ROI_Project" / "05_Diagnostic_Application"
SRC = APP / "Application_Source"
OUT = APP / "PWA"
FILES = ["index.html", "styles.css", "logic.js", "app.js", "sw.js", "manifest.webmanifest",
         "icons/icon-192.png", "icons/icon-512.png", "icons/icon-maskable-512.png",
         "data/research_ranking.json", "data/question_bank.json"]


def sha(path):
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    # the question bank master lives in Question_Bank/; keep the app copy in step
    master = APP / "Question_Bank" / "physics_question_bank_v1.json"
    appcopy = SRC / "data" / "question_bank.json"
    if master.exists() and (not appcopy.exists() or master.read_bytes() != appcopy.read_bytes()):
        shutil.copyfile(master, appcopy)
        print("refreshed app copy of the question bank")

    missing = [f for f in FILES if not (SRC / f).exists()]
    if missing:
        print("MISSING SOURCE FILES:", missing)
        return 1

    if args.check:
        bad = [f for f in FILES if not (OUT / f).exists() or sha(OUT / f) != sha(SRC / f)]
        print("build is current" if not bad else f"stale or missing: {bad}")
        return 0 if not bad else 1

    if OUT.exists():
        shutil.rmtree(OUT)
    for rel in FILES:
        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SRC / rel, dst)

    manifest = {
        "build": "PWA-1.0.0",
        "built": "2026-11-15",
        "source": "05_Diagnostic_Application/Application_Source",
        "note": "Byte-identical copies; see Documentation/06_PWA_Architecture.md",
        "assets": [{"path": rel, "bytes": (OUT / rel).stat().st_size, "sha256": sha(OUT / rel)}
                   for rel in FILES],
    }
    (OUT / "build_manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    (OUT / "INSTALL.txt").write_text(
        "CBSE Physics 2027 - Diagnostic PWA (build PWA-1.0.0)\n"
        "====================================================\n\n"
        "The app is a static site. Serve this folder over HTTP (not file://) so the\n"
        "service worker can register:\n\n"
        "    python -m http.server 8080\n\n"
        "then open http://localhost:8080/ and use the browser's Install action\n"
        "(Chrome/Edge: address-bar install icon; Android: Add to Home screen;\n"
        "iOS Safari: Share > Add to Home Screen).\n\n"
        "After the first load the app works with no network at all. Data stays in\n"
        "this browser's IndexedDB; export a JSON backup from the Backup tab.\n",
        encoding="utf-8")
    total = sum(a["bytes"] for a in manifest["assets"])
    print(f"built {OUT.relative_to(ROOT)}: {len(FILES)} assets, {total / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
