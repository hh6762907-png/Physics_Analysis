/*
 * tests/logic.test.js - dependency-free test suite for logic.js.
 * Run: node tests/logic.test.js      (exit code 0 = all assertions passed)
 */
const fs = require("fs");
const path = require("path");
const L = require("../Application_Source/logic.js");

const bankPath = path.join(__dirname, "..", "Question_Bank", "physics_question_bank_v1.json");
const bank = JSON.parse(fs.readFileSync(bankPath, "utf8"));

let pass = 0, fail = 0;
function ok(name, cond, detail) {
  if (cond) { pass++; console.log("PASS  " + name); }
  else { fail++; console.log("FAIL  " + name + (detail ? "  -> " + detail : "")); }
}
function close(a, b, tol) { return Math.abs(a - b) <= (tol === undefined ? 1e-6 : tol); }

/* ---------------------------------------------------------- bank integrity */
ok("bank has 84 items", bank.items.length === 84, bank.items.length);
ok("bank covers all 14 chapters", bank.chapters_covered.length === 14);
ok("bank marks are 1 or 2", bank.items.every(i => i.marks === 1 || i.marks === 2));
ok("every item is labelled original", bank.items.every(i => i.source_class === "ORIGINAL"));
ok("mcq/ar items have 4 options and a valid key",
  bank.items.filter(i => i.options).every(i => i.options.length === 4 && i.answer_index >= 0 && i.answer_index < 4));
ok("written items carry a rubric", bank.items.filter(i => i.format === "SA").every(i => !!i.rubric));
const ids = new Set(bank.items.map(i => i.id));
ok("item ids are unique", ids.size === bank.items.length);

/* ------------------------------------------------------------ readiness */
const fake = [
  { itemId: "a", chapter: 1, difficulty: 1, correct: true, confidence: 0.9, timestamp: 1 },
  { itemId: "b", chapter: 1, difficulty: 2, correct: true, confidence: 0.8, timestamp: 2 },
  { itemId: "c", chapter: 1, difficulty: 2, correct: false, confidence: 0.3, timestamp: 3 },
  { itemId: "d", chapter: 1, difficulty: 3, correct: false, confidence: 0.6, timestamp: 4 },
  { itemId: "e", chapter: 1, difficulty: 1, correct: true, confidence: 0.7, timestamp: 5 }
];
const r1 = L.estimateReadiness(fake, 1);
ok("readiness is a probability", r1.readiness > 0 && r1.readiness < 1, r1.readiness);
ok("attempt count is counted", r1.attempts === 5);
ok("estimate is not provisional at 5 attempts", r1.provisional === false);
ok("empty chapter returns null readiness", L.estimateReadiness(fake, 7).readiness === null);
ok("fewer than 5 attempts is provisional", L.estimateReadiness(fake.slice(0, 3), 1).provisional === true);
const allRight = fake.map(r => Object.assign({}, r, { correct: true }));
ok("all-correct readiness stays below 1", L.estimateReadiness(allRight, 1).readiness < 1);
const allWrong = fake.map(r => Object.assign({}, r, { correct: false }));
ok("all-wrong readiness stays above 0", L.estimateReadiness(allWrong, 1).readiness > 0);

/* --------------------------------------------------------------- Brier */
const brier = L.brierScore([
  { confidence: 1, correct: true }, { confidence: 0, correct: false }
]);
ok("perfect calibration gives Brier 0", close(brier, 0, 1e-9), brier);
ok("no confidence data gives null Brier", L.brierScore([{ correct: true }]) === null);
const buckets = L.calibrationBuckets(fake);
ok("calibration buckets cover the range", buckets.length === 5);
ok("bucket counts sum to sample size", buckets.reduce((a, b) => a + b.n, 0) === 5);

/* ----------------------------------------------------------- selection */
const roiByChapter = { 1: 0.17, 2: 0.32, 3: 0.30, 4: 0.26, 5: 0.18, 6: 0.30, 7: 0.23, 8: 0.40,
  9: 0.28, 10: 0.34, 11: 0.35, 12: 0.32, 13: 0.36, 14: 0.48 };
const first = L.selectNextItem(bank.items, { responses: [], roiByChapter });
ok("first item comes from the highest-ROI untouched chapter", first.chapter === 14, first && first.chapter);
const second = L.selectNextItem(bank.items, {
  responses: [{ itemId: first.id, chapter: first.chapter, difficulty: first.difficulty, correct: true, confidence: 0.8, timestamp: 1 }],
  roiByChapter
});
ok("selection prefers untested chapters", second.chapter !== 14 || second.id !== first.id);
const repeat = L.selectNextItem(bank.items.slice(0, 6), {
  responses: bank.items.slice(0, 6).map((it, i) => ({ itemId: it.id, chapter: it.chapter, difficulty: it.difficulty, correct: true, confidence: 0.8, timestamp: i })),
  roiByChapter
});
ok("exhausted bank still returns an item", !!repeat && !!repeat.id);
const lowReady = L.selectNextItem(bank.items, { responses: [], roiByChapter, readiness: 0.2 });
ok("low readiness targets easier items", lowReady.difficulty === 1, lowReady.difficulty);
ok("target difficulty is monotone", L.targetDifficulty(0.2) <= L.targetDifficulty(0.5) && L.targetDifficulty(0.5) <= L.targetDifficulty(0.9));

/* ------------------------------------------------------- spaced repetition */
const s0 = L.scheduleReview(null, true, 1000000000000);
ok("first correct review schedules 1 day", s0.intervalDays === 1, s0.intervalDays);
const s1 = L.scheduleReview(s0, true, 1000000000000);
ok("second correct review lengthens the interval", s1.intervalDays >= s0.intervalDays);
const s2 = L.scheduleReview(s1, false, 1000000000000);
ok("a wrong answer resets to the first rung", s2.step === 0 && s2.intervalDays === 1);
ok("ease stays inside 1.3-2.5", s2.ease >= 1.3 && s2.ease <= 2.5);
const due = L.dueItems({ x: { dueAt: 1 }, y: { dueAt: 9e15 } }, 1000);
ok("due list returns only overdue items", due.length === 1 && due[0] === "x");

/* ------------------------------------------------------ personalised ROI */
const chap = { chapter: 10, exposureMarks: 6.26, targetReadiness: 0.95, hoursToStrong: 7.13, optionalShare: 0.3143 };
const pLow = L.personalisedRoi(chap, 0.4);
const pHigh = L.personalisedRoi(chap, 0.85);
ok("lower readiness yields a larger gain", pLow.gainMarks > pHigh.gainMarks, [pLow.gainMarks, pHigh.gainMarks]);
ok("at-target readiness yields no gain", L.personalisedRoi(chap, 0.99).atTarget === true);
ok("hours floor of 1.5 applies", L.personalisedRoi(chap, 0.949).additionalHours >= 1.5);
const ranked = L.prioritise([chap], { 10: 0.4 });
ok("prioritise returns a ranked list", ranked.length === 1 && ranked[0].roi > 0);

/* ------------------------------------------------------------- exam paper */
const paper = L.buildExamPaper(bank.items, 20261115);
ok("exam paper totals exactly 70 marks", paper.totalMarks === 70, paper.totalMarks);
ok("exam paper is flagged structurally valid", paper.structureValid === true);
ok("exam paper has five sections", paper.sections.length === 5);
ok("section A holds 16 one-mark questions",
  paper.sections[0].questions.length === 16 && paper.sections[0].questions.every(q => q.marks === 1));
ok("section B holds 5 two-mark questions",
  paper.sections[1].questions.length === 5 && paper.sections[1].questions.every(q => q.marks === 2));
ok("composite sections reach 3/4/5 marks",
  [2, 3, 4].every(i => paper.sections[i].questions.every(q => q.composite.reduce((a, c) => a + c.marks, 0) === q.marks)));
const usedIds = [];
paper.sections.forEach(s => s.questions.forEach(q => {
  if (q.composite) q.composite.forEach(c => usedIds.push(c.id)); else usedIds.push(q.id);
}));
ok("no question is repeated inside one paper", new Set(usedIds).size === usedIds.length,
  usedIds.length + " picks, " + new Set(usedIds).size + " unique");
const paper2 = L.buildExamPaper(bank.items, 20261115);
ok("paper generation is deterministic for a seed", paper2.totalMarks === paper.totalMarks &&
  paper2.sections[0].questions.map(q => q.id).join() === paper.sections[0].questions.map(q => q.id).join());
const paper3 = L.buildExamPaper(bank.items, 7);
ok("a different seed changes the paper", paper3.sections[0].questions.map(q => q.id).join() !==
  paper.sections[0].questions.map(q => q.id).join());

/* --------------------------------------------------- backup and migration */
const goodBackup = {
  app: "cbse-physics-2027-diagnostic", schema: 1, responses: [
    { itemId: "C01-Q001", chapter: 1, correct: true, confidence: 0.8, timestamp: 1 }],
  reviews: {}, sessions: [], settings: {}
};
ok("valid backup passes validation", L.validateBackup(goodBackup).ok === true);
ok("wrong app id is rejected", L.validateBackup({ app: "x", schema: 1, responses: [] }).ok === false);
ok("malformed response is rejected", L.validateBackup({
  app: "cbse-physics-2027-diagnostic", schema: 1, responses: [{ itemId: 5 }]
}).ok === false);
ok("future schema is rejected", L.validateBackup({
  app: "cbse-physics-2027-diagnostic", schema: 99, responses: []
}).ok === false);
const migrated = L.migrateBackup({ app: "cbse-physics-2027-diagnostic", responses: [] });
ok("migration fills defaults", typeof migrated.reviews === "object" && Array.isArray(migrated.sessions) && migrated.schema === 1);
ok("snapshot labels are ISO-8601 UTC", /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(L.snapshotLabel(0)));

/* ------------------------------------------------------------- sessions */
const sess = L.summariseSession([
  { type: "start", at: 0 }, { type: "break_start", at: 600000 },
  { type: "break_end", at: 900000 }, { type: "stop", at: 1200000 }
]);
ok("active time excludes breaks", sess.activeSeconds === 900, sess.activeSeconds);
ok("break time is tracked separately", sess.breakSeconds === 300, sess.breakSeconds);
ok("long breaks are flagged", sess.longBreaks === 0);
const longBreak = L.summariseSession([
  { type: "start", at: 0 }, { type: "break_start", at: 60000 },
  { type: "break_end", at: 60000 + 1200000 }, { type: "stop", at: 61000 + 1200000 }
]);
ok("breaks over ten minutes are flagged", longBreak.longBreaks === 1);

/* -------------------------------------------------------- progress view */
const prog = L.chapterProgress(fake, [1, 2]);
ok("progress covers the requested chapters", prog.length === 2);
ok("untested chapter reports no attempts", prog[1].attempts === 0 && prog[1].readiness === null);

console.log("\n" + pass + " passed, " + fail + " failed");
process.exit(fail === 0 ? 0 : 1);
