# Using the app

## Install

Serve the `PWA/` folder over HTTP and open it — for example
`python -m http.server 8080` inside `PWA/`, then `http://localhost:8080/`. Install from the
browser menu (Chrome/Edge install icon, Android *Add to Home screen*, iOS *Share → Add to Home
Screen*). After the first load the app works with no network: the shell, the question bank and
the research values are precached.

## First session (about 15 minutes)

1. **Practice.** Answer six to ten questions. Pick *Low / Medium / High* confidence *before*
   answering — this is what makes the calibration statistics meaningful later.
2. **Dashboard.** Chapters you have touched now show a readiness bar; the rest say *not set*.
   The recommendation cards appear as soon as at least one chapter is measured.
3. **Study.** Start the timer when you begin working; use *Start break* rather than stopping the
   timer, so break time is recorded separately.

## A working week

| When | Do | Why |
|---|---|---|
| Daily, 10 min | Practice until the dashboard's *Due today* list is empty | Spaced repetition keeps earlier chapters alive |
| Twice a week | Strict exam mode (seed default) | Full-paper timing and stamina |
| After each exam | Self-mark written answers honestly | The readiness estimate depends on it |
| Weekly | Check *Progress → Confidence calibration* | A positive gap means overconfidence |

## Reading your own numbers

* **Readiness** is a weighted accuracy shrunk towards 50% until five questions are answered.
  Below five attempts it is labelled *provisional* and should not drive decisions.
* **Gap** (confidence − actual accuracy) above +10% means you are overconfident in that
  chapter; the fix is more checking, not more content.
* **Brier score**: 0.25 is what you get by always saying 50%; lower is better. It moves slowly
  and is not a grade.
* **Recommendation cards** show *your* gap, *your* hours and *your* marginal return. They will
  differ from the research ranking, because they use your measured starting point.

## Data care

Export a backup from the **Backup** tab after any substantial session. Snapshots are kept in
the browser, but clearing site data removes everything, snapshots included. Importing a
backup replaces current data after confirmation; the import report tells you exactly what was
loaded or why it was refused.

## Honest limits

84 questions means repeats after a few sessions; use the exam mode and the workbook between
sessions. Self-marking is only as honest as you are. The app measures what you can do on
CBSE-style questions, not what you will score in March.
