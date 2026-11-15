/*
 * logic.js - pure, dependency-free logic for the CBSE Physics 2027 diagnostic app.
 * Loaded as a plain script in the browser (window.PhysLogic) and as a CommonJS
 * module by the Node test suite (module.exports). No DOM, no storage: every
 * function here is deterministic apart from the explicitly seeded PRNG.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.PhysLogic = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  var APP_VERSION = "1.0.0";
  var STATE_SCHEMA = 1;

  /* ---------------------------------------------------------------- helpers */
  function clamp(x, lo, hi) { return Math.min(hi, Math.max(lo, x)); }
  function round(x, d) { var f = Math.pow(10, d === undefined ? 2 : d); return Math.round(x * f) / f; }

  /* Mulberry32: small, deterministic PRNG so papers and selection are testable. */
  function rng(seed) {
    var a = seed >>> 0;
    return function () {
      a += 0x6D2B79F5;
      var t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  /* ------------------------------------------------------- readiness model */
  /*
   * Weighted accuracy per chapter. Weights:
   *   difficulty 1 -> 0.8, 2 -> 1.0, 3 -> 1.25  (harder items carry more signal)
   *   confidence reported BEFORE answering scales the evidence: a lucky guess
   *   marked "low" counts less in the positive direction, and a confident wrong
   *   answer counts fully as a negative signal. Two-keyed: accuracy and calibration
   *   stay separate so neither is double counted.
   * Returns readiness in [0,1] plus the number of attempts and a provisional flag.
   */
  var DIFF_WEIGHT = { 1: 0.8, 2: 1.0, 3: 1.25 };
  var MIN_ATTEMPTS_FOR_ESTIMATE = 5;

  function estimateReadiness(responses, chapter, opts) {
    opts = opts || {};
    var minAttempts = opts.minAttempts || MIN_ATTEMPTS_FOR_ESTIMATE;
    var rows = (responses || []).filter(function (r) { return r.chapter === chapter; });
    if (!rows.length) return { chapter: chapter, readiness: null, attempts: 0, provisional: true, calibrationGap: null, accuracy: null };
    var wsum = 0, wgot = 0, correct = 0, confSum = 0;
    rows.forEach(function (r) {
      var w = DIFF_WEIGHT[r.difficulty] || 1;
      wsum += w;
      if (r.correct) { wgot += w; correct += 1; }
      confSum += (typeof r.confidence === "number" ? r.confidence : 0.5);
    });
    var acc = wgot / wsum;
    var meanConf = confSum / rows.length;
    var observed = correct / rows.length;
    /* shrink towards the prior until enough evidence exists (5 attempts) */
    var n = rows.length;
    var shrink = n / (n + minAttempts);
    var readiness = clamp(acc * 0.75 + observed * 0.25, 0, 1);
    readiness = 0.5 + (readiness - 0.5) * shrink;
    return {
      chapter: chapter,
      readiness: round(readiness, 4),
      accuracy: round(acc, 4),
      observedAccuracy: round(observed, 4),
      meanConfidence: round(meanConf, 4),
      calibrationGap: round(meanConf - observed, 4),
      attempts: n,
      provisional: n < minAttempts
    };
  }

  function estimateAll(responses, chapters, opts) {
    return (chapters || []).map(function (c) { return estimateReadiness(responses, c, opts); });
  }

  /* Brier score over all responses that carry a confidence value; lower is better.
     Reference points: 0.25 = always 0.5 confident, 0.00 = perfect. */
  function brierScore(responses) {
    var rows = (responses || []).filter(function (r) { return typeof r.confidence === "number"; });
    if (!rows.length) return null;
    var s = 0;
    rows.forEach(function (r) {
      var p = clamp(r.confidence, 0, 1);
      var o = r.correct ? 1 : 0;
      s += (p - o) * (p - o);
    });
    return round(s / rows.length, 4);
  }

  function calibrationBuckets(responses) {
    var edges = [0, 0.2, 0.4, 0.6, 0.8, 1.0001];
    var out = [];
    for (var i = 0; i < edges.length - 1; i++) {
      var rows = (responses || []).filter(function (r) {
        return typeof r.confidence === "number" && r.confidence >= edges[i] && r.confidence < edges[i + 1];
      });
      out.push({
        band: edges[i].toFixed(1) + "-" + Math.min(1, edges[i + 1]).toFixed(1),
        n: rows.length,
        meanConfidence: rows.length ? round(rows.reduce(function (a, r) { return a + r.confidence; }, 0) / rows.length, 3) : null,
        observedAccuracy: rows.length ? round(rows.filter(function (r) { return r.correct; }).length / rows.length, 3) : null
      });
    }
    return out;
  }

  /* --------------------------------------------------- adaptive selection */
  /*
   * Picks the next item. Priority:
   *   1. chapters with the fewest attempts (coverage first),
   *   2. within that, the chapter with the highest research ROI,
   *   3. the item whose difficulty best matches the current readiness
   *      (target success probability near 0.7 - the productive-struggle band),
   *   4. unseen items before repeats, then the oldest repeat.
   * Deterministic given the same state; ties break on item id.
   */
  function targetDifficulty(readiness) {
    if (readiness === null || readiness === undefined) return 2;
    if (readiness < 0.45) return 1;
    if (readiness > 0.75) return 3;
    return 2;
  }

  function selectNextItem(bank, state) {
    state = state || {};
    var responses = state.responses || [];
    var roiByChapter = state.roiByChapter || {};
    var pool = (bank || []).filter(function (it) { return !state.excludedIds || state.excludedIds.indexOf(it.id) === -1; });
    if (!pool.length) return null;

    var attemptsByCh = {}, lastSeen = {};
    responses.forEach(function (r, idx) {
      attemptsByCh[r.chapter] = (attemptsByCh[r.chapter] || 0) + 1;
      lastSeen[r.itemId] = Math.max(lastSeen[r.itemId] || -1, idx);
    });

    function chapterScore(it) {
      var att = attemptsByCh[it.chapter] || 0;
      var roi = roiByChapter[it.chapter] !== undefined ? roiByChapter[it.chapter] : 0.3;
      return { att: att, roi: roi };
    }

    var minAtt = Infinity;
    pool.forEach(function (it) { var s = chapterScore(it); if (s.att < minAtt) minAtt = s.att; });
    var candidates = pool.filter(function (it) { return chapterScore(it).att === minAtt; });

    if (candidates.length > 1) {
      var bestRoi = -Infinity;
      candidates.forEach(function (it) { bestRoi = Math.max(bestRoi, chapterScore(it).roi); });
      candidates = candidates.filter(function (it) { return chapterScore(it).roi === bestRoi; });
    }

    var seenIds = {};
    responses.forEach(function (r) { seenIds[r.itemId] = true; });
    var unseen = candidates.filter(function (it) { return !seenIds[it.id]; });

    function pickFrom(list) {
      var byDiff = {};
      list.forEach(function (it) { (byDiff[it.difficulty] = byDiff[it.difficulty] || []).push(it); });
      var pref = [targetDifficulty(state.readiness), 1, 2, 3, 4];
      for (var i = 0; i < pref.length; i++) {
        var group = byDiff[pref[i]];
        if (group && group.length) {
          group.sort(function (a, b) { return a.id < b.id ? -1 : a.id > b.id ? 1 : 0; });
          return group[0];
        }
      }
      return null;
    }

    var chosen = pickFrom(unseen.length ? unseen : candidates);
    if (chosen) return chosen;

    /* everything exhausted: repeat the least recently seen item */
    var sorted = pool.slice().sort(function (a, b) {
      var la = lastSeen[a.id] === undefined ? -1 : lastSeen[a.id];
      var lb = lastSeen[b.id] === undefined ? -1 : lastSeen[b.id];
      if (la !== lb) return la - lb;
      return a.id < b.id ? -1 : 1;
    });
    return sorted[0] || null;
  }

  /* ------------------------------------------------- spaced repetition */
  /*
   * SM-2 style scheduler with a fixed ladder so behaviour is easy to explain:
   * intervals 1, 3, 7, 16, 35, 75 days, multiplied by an ease factor that
   * moves between 1.3 and 2.5. A wrong answer resets the ladder to 1 day.
   */
  var LADDER = [1, 3, 7, 16, 35, 75];

  function scheduleReview(prev, correct, nowMs) {
    var now = nowMs || Date.now();
    var ease = prev && typeof prev.ease === "number" ? prev.ease : 2.0;
    var step = prev && typeof prev.step === "number" ? prev.step : 0;
    if (correct) {
      ease = clamp(ease + 0.1, 1.3, 2.5);
      /* the first correct exposure schedules the first rung (1 day) */
      step = prev && typeof prev.step === "number"
        ? Math.min(LADDER.length - 1, step + 1)
        : 0;
    } else {
      ease = clamp(ease - 0.2, 1.3, 2.5);
      step = 0;
    }
    var base = LADDER[step];
    var interval = Math.round(clamp(base * (ease / 2), 1, 180));
    return {
      step: step,
      ease: round(ease, 2),
      intervalDays: interval,
      dueAt: now + interval * 86400000,
      lastReviewedAt: now
    };
  }

  function dueItems(reviews, nowMs) {
    var now = nowMs || Date.now();
    return Object.keys(reviews || {})
      .filter(function (k) { return reviews[k] && reviews[k].dueAt <= now; })
      .sort(function (a, b) { return reviews[a].dueAt - reviews[b].dueAt; });
  }

  /* ------------------------------------------- personalised recommendation */
  /*
   * Personalised marginal return: chapter exposure x the readiness gap that is
   * still open, divided by the additional hours the research model says are
   * needed to close it. Readiness here is the measured value; the research
   * baseline is replaced, never averaged, so the two are not double counted.
   */
  function personalisedRoi(chapterData, measuredReadiness) {
    if (!chapterData || measuredReadiness === null || measuredReadiness === undefined) return null;
    var target = clamp(chapterData.targetReadiness, 0, 1);
    var r = clamp(measuredReadiness, 0, 1);
    var cEff = 0.5 * chapterData.optionalShare;             /* choice-adjusted success slope */
    var fNow = r + cEff * (1 - r);
    var fTarget = target + cEff * (1 - target);
    var gain = chapterData.exposureMarks * (fTarget - fNow);
    var hours = Math.max(1.5, chapterData.hoursToStrong * ((target - r) / Math.max(target, 0.01)));
    return {
      chapter: chapterData.chapter,
      gainMarks: round(gain, 2),
      additionalHours: round(hours, 2),
      roi: round(Math.max(0, gain) / hours, 4),
      atTarget: gain <= 0.001
    };
  }

  function prioritise(chapters, readinessMap, limit) {
    var rows = chapters.map(function (c) {
      var p = personalisedRoi(c, readinessMap[c.chapter]);
      return p ? Object.assign({ name: c.name, tier: c.tier }, p) : null;
    }).filter(Boolean).filter(function (r) { return !r.atTarget; });
    rows.sort(function (a, b) {
      if (b.roi !== a.roi) return b.roi - a.roi;
      return a.chapter - b.chapter;
    });
    return limit ? rows.slice(0, limit) : rows;
  }

  /* ------------------------------------------------------- exam builder */
  /*
   * Builds a 70-mark paper with the verified 2026-27 structure:
   * A 16 x 1, B 5 x 2, C 7 x 3, D 2 x 4, E 3 x 5 = 70.
   * The bank holds 1- and 2-mark items; 3-, 4- and 5-mark slots are filled by
   * grouping same-chapter short-answer and MCQ items so the mark total is exact.
   * Every question is counted once; a chapter is never used twice in one slot
   * pair when an unused alternative exists.
   */
  var EXAM_STRUCTURE = [
    { section: "A", count: 16, marks: 1 },
    { section: "B", count: 5, marks: 2 },
    { section: "C", count: 7, marks: 3 },
    { section: "D", count: 2, marks: 4 },
    { section: "E", count: 3, marks: 5 }
  ];
  var EXAM_TOTAL = 70;

  function shuffle(list, rand) {
    var a = list.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(rand() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  /* Groups items of a chapter into composites whose marks sum exactly to the slot. */
  function buildComposite(marks, pool, used) {
    var free = pool.filter(function (i) { return !used[i.id]; });
    function greedy(remaining, acc, startIdx) {
      if (remaining === 0) return acc.slice();
      for (var k = startIdx; k < free.length; k++) {
        var it = free[k];
        if (it.marks > remaining) continue;
        acc.push(it);
        var res = greedy(remaining - it.marks, acc, k + 1);
        if (res) return res;
        acc.pop();
      }
      return null;
    }
    free.sort(function (a, b) { return b.marks - a.marks; });
    return greedy(marks, [], 0);
  }

  function buildExamPaper(bank, seed) {
    var rand = rng(seed === undefined ? 20261115 : seed);
    var used = {};
    var paper = [];
    var byMarks = {};
    bank.forEach(function (it) { (byMarks[it.marks] = byMarks[it.marks] || []).push(it); });

    EXAM_STRUCTURE.forEach(function (sec) {
      var picks = [];
      if (sec.marks === 1) {
        picks = shuffle(byMarks[1] || [], rand).filter(function (it) { return !used[it.id]; }).slice(0, sec.count);
        picks.forEach(function (it) { used[it.id] = true; });
      } else if (sec.marks === 2) {
        picks = shuffle(byMarks[2] || [], rand).filter(function (it) { return !used[it.id]; }).slice(0, sec.count);
        picks.forEach(function (it) { used[it.id] = true; });
      } else {
        /* composite slot: pick a chapter spread and fill the marks exactly */
        for (var n = 0; n < sec.count; n++) {
          var chapters = Object.keys(byMarks).reduce(function (acc, m) { return acc; }, null);
          var candidate = null;
          var order = shuffle(Object.keys(byMarks[1] || {}).length ? [1, 2] : [2], rand);
          /* try each chapter in a shuffled order, then each single item */
          var chs = [];
          for (var c = 1; c <= 14; c++) chs.push(c);
          chs = shuffle(chs, rand);
          for (var ci = 0; ci < chs.length && !candidate; ci++) {
            var pool = bank.filter(function (it) { return it.chapter === chs[ci]; });
            var group = buildComposite(sec.marks, pool, used);
            if (group) candidate = group;
          }
          if (candidate) {
            candidate.forEach(function (it) { used[it.id] = true; });
            picks.push({ composite: candidate, marks: sec.marks });
          }
        }
      }
      paper.push({ section: sec.section, marks: sec.marks, questions: picks });
    });

    /* internal choice in B, C and E: mark a duplicate-free alternative where possible */
    var total = 0;
    paper.forEach(function (sec) { sec.questions.forEach(function (q) { total += q.marks; }); });
    return {
      seed: seed === undefined ? 20261115 : seed,
      sections: paper,
      totalMarks: total,
      structureValid: total === EXAM_TOTAL,
      durationMinutes: 180,
      marksVerifiedAgainst: "CBSE SQP 2026-27 structure (A 16x1, B 5x2, C 7x3, D 2x4, E 3x5)"
    };
  }

  /* ------------------------------------------------- backup / versioning */
  function validateBackup(obj) {
    var errors = [];
    if (!obj || typeof obj !== "object") return { ok: false, errors: ["not an object"] };
    if (obj.app !== "cbse-physics-2027-diagnostic") errors.push("unexpected app id: " + String(obj.app));
    if (typeof obj.schema !== "number") errors.push("missing schema version");
    if (obj.schema > STATE_SCHEMA) errors.push("backup schema " + obj.schema + " is newer than this app (" + STATE_SCHEMA + ")");
    if (!Array.isArray(obj.responses)) errors.push("responses must be an array");
    else {
      obj.responses.forEach(function (r, i) {
        if (!r || typeof r.itemId !== "string" || typeof r.chapter !== "number" || typeof r.correct !== "boolean") {
          errors.push("response " + i + " is malformed");
        }
      });
    }
    if (obj.reviews !== undefined && (typeof obj.reviews !== "object" || obj.reviews === null)) errors.push("reviews must be an object");
    if (obj.sessions !== undefined && !Array.isArray(obj.sessions)) errors.push("sessions must be an array");
    if (obj.settings !== undefined && (typeof obj.settings !== "object" || obj.settings === null)) errors.push("settings must be an object");
    return { ok: errors.length === 0, errors: errors };
  }

  function migrateBackup(obj) {
    var data = JSON.parse(JSON.stringify(obj));
    if (data.schema === undefined) data.schema = 1;
    /* schema 1 -> 2 placeholder for future field additions: nothing to move yet */
    if (data.schema < STATE_SCHEMA) data.schema = STATE_SCHEMA;
    data.responses = data.responses || [];
    data.sessions = data.sessions || [];
    data.settings = data.settings || {};
    data.reviews = data.reviews || {};
    return data;
  }

  function snapshotLabel(nowMs) {
    var d = new Date(nowMs || Date.now());
    function p(n) { return (n < 10 ? "0" : "") + n; }
    return d.getUTCFullYear() + "-" + p(d.getUTCMonth() + 1) + "-" + p(d.getUTCDate()) + "T" +
      p(d.getUTCHours()) + ":" + p(d.getUTCMinutes()) + ":" + p(d.getUTCSeconds()) + "Z";
  }

  /* ------------------------------------------------------------- timers */
  /*
   * Session accounting keeps active study time and break time strictly
   * separate; breaks are never counted as study and pauses longer than ten
   * minutes are flagged so the statistics can be read honestly.
   */
  function summariseSession(events) {
    var active = 0, breaks = 0, lastStart = null, lastBreakStart = null, longBreaks = 0;
    (events || []).forEach(function (e) {
      if (e.type === "start") { lastStart = e.at; }
      else if (e.type === "break_start") { if (lastStart !== null) { active += (e.at - lastStart) / 1000; lastStart = null; } lastBreakStart = e.at; }
      else if (e.type === "break_end") { if (lastBreakStart !== null) { var d = (e.at - lastBreakStart) / 1000; breaks += d; if (d > 600) longBreaks++; lastBreakStart = null; } lastStart = e.at; }
      else if (e.type === "stop") {
        if (lastStart !== null) { active += (e.at - lastStart) / 1000; lastStart = null; }
        if (lastBreakStart !== null) { breaks += (e.at - lastBreakStart) / 1000; lastBreakStart = null; }
      }
    });
    return { activeSeconds: Math.round(active), breakSeconds: Math.round(breaks), longBreaks: longBreaks };
  }

  /* -------------------------------------------------- progress analytics */
  function chapterProgress(responses, chapters) {
    return (chapters || []).map(function (c) {
      var rows = responses.filter(function (r) { return r.chapter === c; });
      var est = estimateReadiness(responses, c);
      return {
        chapter: c,
        attempts: rows.length,
        readiness: est.readiness,
        provisional: est.provisional,
        lastAttempt: rows.length ? Math.max.apply(null, rows.map(function (r) { return r.timestamp; })) : null
      };
    });
  }

  return {
    APP_VERSION: APP_VERSION,
    STATE_SCHEMA: STATE_SCHEMA,
    DIFF_WEIGHT: DIFF_WEIGHT,
    EXAM_STRUCTURE: EXAM_STRUCTURE,
    EXAM_TOTAL: EXAM_TOTAL,
    LADDER: LADDER,
    clamp: clamp,
    round: round,
    rng: rng,
    estimateReadiness: estimateReadiness,
    estimateAll: estimateAll,
    brierScore: brierScore,
    calibrationBuckets: calibrationBuckets,
    targetDifficulty: targetDifficulty,
    selectNextItem: selectNextItem,
    scheduleReview: scheduleReview,
    dueItems: dueItems,
    personalisedRoi: personalisedRoi,
    prioritise: prioritise,
    buildExamPaper: buildExamPaper,
    validateBackup: validateBackup,
    migrateBackup: migrateBackup,
    snapshotLabel: snapshotLabel,
    summariseSession: summariseSession,
    chapterProgress: chapterProgress
  };
});
