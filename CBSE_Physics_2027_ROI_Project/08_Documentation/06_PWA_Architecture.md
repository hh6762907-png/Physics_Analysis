# Offline application: architecture and algorithms

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
