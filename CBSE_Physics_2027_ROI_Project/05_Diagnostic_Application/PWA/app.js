/*
 * app.js - UI, storage and orchestration for the Physics 2027 diagnostic app.
 * All scoring, selection, scheduling and paper-building logic lives in logic.js
 * (tested by tests/logic.test.js). This file only moves data around.
 */
(function () {
  "use strict";
  var L = window.PhysLogic;
  var APP = "cbse-physics-2027-diagnostic";
  var DB_NAME = "cbse_physics_2027";
  var DB_VERSION = 1;
  var SETTINGS_KEY = "settings";
  var SNAPSHOT_KEY = "snapshots";

  var S = {
    db: null, bank: [], chapters: [], research: null,
    responses: [], reviews: {}, sessions: [], settings: {},
    practice: { item: null, chosen: null, answered: false, answeredCount: 0, correctCount: 0, sessionCorrect: 0, sessionTotal: 0 },
    exam: null, timer: { running: false, onBreak: false, startAt: 0, breakAt: 0, events: [], tick: null }
  };

  /* ------------------------------------------------------------ storage */
  function openDB() {
    return new Promise(function (resolve, reject) {
      var req = indexedDB.open(DB_NAME, DB_VERSION);
      req.onupgradeneeded = function (e) {
        var db = e.target.result;
        if (!db.objectStoreNames.contains("responses")) {
          var rs = db.createObjectStore("responses", { keyPath: "id", autoIncrement: true });
          rs.createIndex("chapter", "chapter");
        }
        if (!db.objectStoreNames.contains("reviews")) db.createObjectStore("reviews", { keyPath: "itemId" });
        if (!db.objectStoreNames.contains("sessions")) db.createObjectStore("sessions", { keyPath: "id", autoIncrement: true });
        if (!db.objectStoreNames.contains("meta")) db.createObjectStore("meta", { keyPath: "key" });
      };
      req.onsuccess = function () { resolve(req.result); };
      req.onerror = function () { reject(req.error); };
    });
  }

  function tx(store, mode, fn) {
    return new Promise(function (resolve, reject) {
      var t = S.db.transaction(store, mode);
      var os = t.objectStore(store);
      var out = fn(os);
      t.oncomplete = function () { resolve(out && out.result !== undefined ? out.result : out); };
      t.onerror = function () { reject(t.error); };
      t.onabort = function () { reject(t.error); };
    });
  }

  function getAll(store) {
    return new Promise(function (resolve, reject) {
      var t = S.db.transaction(store, "readonly");
      var rq = t.objectStore(store).getAll();
      rq.onsuccess = function () { resolve(rq.result); };
      rq.onerror = function () { reject(rq.error); };
    });
  }

  function put(store, value) {
    return new Promise(function (resolve, reject) {
      var t = S.db.transaction(store, "readwrite");
      t.objectStore(store).put(value);
      t.oncomplete = resolve;
      t.onerror = function () { reject(t.error); };
    });
  }

  function getKey(store, key) {
    return new Promise(function (resolve, reject) {
      var t = S.db.transaction(store, "readonly");
      var rq = t.objectStore(store).get(key);
      rq.onsuccess = function () { resolve(rq.result); };
      rq.onerror = function () { reject(rq.error); };
    });
  }

  function clearStore(store) {
    return new Promise(function (resolve, reject) {
      var t = S.db.transaction(store, "readwrite");
      t.objectStore(store).clear();
      t.oncomplete = resolve;
      t.onerror = function () { reject(t.error); };
    });
  }

  /* --------------------------------------------------------------- utils */
  function $(sel) { return document.querySelector(sel); }
  function el(tag, attrs, children) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === "class") n.className = attrs[k];
      else if (k === "html") n.innerHTML = attrs[k];
      else if (k === "text") n.textContent = attrs[k];
      else if (k.slice(0, 2) === "on") n.addEventListener(k.slice(2), attrs[k]);
      else n.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) {
      if (c === null || c === undefined) return;
      n.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    });
    return n;
  }
  function fmtPct(x) { return x === null || x === undefined ? "—" : Math.round(x * 100) + "%"; }
  function fmtNum(x, d) { return x === null || x === undefined ? "—" : Number(x).toFixed(d === undefined ? 2 : d); }
  function chapterName(c) {
    var hit = S.chapters.find(function (x) { return x.chapter === c; });
    return hit ? hit.name : "Chapter " + c;
  }
  function chapterData(c) {
    return S.chapters.find(function (x) { return x.chapter === c; });
  }
  function roiMap() {
    var m = {};
    S.chapters.forEach(function (c) { m[c.chapter] = c.researchRoi; });
    return m;
  }
  function readinessMap() {
    var m = {};
    S.chapters.forEach(function (c) { m[c.chapter] = L.estimateReadiness(S.responses, c.chapter).readiness; });
    return m;
  }

  /* ------------------------------------------------------------ feedback */
  function notice(container, text, kind) {
    container.hidden = false;
    container.className = "notice" + (kind ? " " + kind : "");
    container.textContent = text;
  }

  /* ---------------------------------------------------------- navigation */
  function show(view) {
    document.querySelectorAll(".view").forEach(function (v) { v.classList.remove("active"); });
    document.querySelectorAll(".tab").forEach(function (t) { t.classList.toggle("active", t.dataset.view === view); });
    var target = $("#view-" + view);
    if (target) target.classList.add("active");
    if (view === "dashboard") renderDashboard();
    if (view === "progress") renderProgress();
    if (view === "study") renderSessions();
    if (view === "data") renderData();
    if (view === "practice") preparePractice();
    if (view === "about") renderAbout();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  /* ----------------------------------------------------------- dashboard */
  function renderDashboard() {
    var rm = readinessMap();
    var measured = S.chapters.filter(function (c) { return rm[c.chapter] !== null; });
    var avg = measured.length ? measured.reduce(function (a, c) { return a + rm[c.chapter]; }, 0) / measured.length : null;
    var minutes = S.sessions.reduce(function (a, s) { return a + (s.activeSeconds || 0); }, 0) / 60;
    var stats = [
      ["Answers recorded", S.responses.length],
      ["Chapters measured", measured.length + " / 14"],
      ["Mean readiness", fmtPct(avg)],
      ["Study time", Math.round(minutes) + " min"],
      ["Brier score", L.brierScore(S.responses) === null ? "—" : fmtNum(L.brierScore(S.responses), 3)],
      ["Due today", L.dueItems(S.reviews, Date.now()).length]
    ];
    var box = $("#dashStats");
    box.innerHTML = "";
    stats.forEach(function (s) {
      box.appendChild(el("div", { class: "stat" }, [el("b", { text: String(s[1]) }), el("span", { text: s[0] })]));
    });

    var prio = L.prioritise(S.chapters, rm, 4);
    var pc = $("#dashPriority");
    pc.innerHTML = "";
    if (!prio.length) {
      pc.appendChild(el("div", { class: "card" }, [
        el("h3", { text: "Answer a few questions first" }),
        el("p", { class: "muted", text: "Recommendations appear once at least one chapter has a measured readiness. Start with Practice — it spreads questions across chapters." })
      ]));
    } else {
      prio.forEach(function (p) {
        pc.appendChild(el("div", { class: "card" }, [
          el("span", { class: "tier", text: "Tier " + p.tier }),
          el("h3", { text: "C" + p.chapter + " · " + p.name }),
          el("p", { class: "muted", text: "Gap to target: " + fmtNum(p.gainMarks, 2) + " probability-adjusted marks · " + fmtNum(p.additionalHours, 1) + " h of work · " + fmtNum(p.roi, 2) + " marks per hour (your numbers)" })
        ]));
      });
    }

    var due = L.dueItems(S.reviews, Date.now()).slice(0, 5);
    var dc = $("#dashDue");
    dc.innerHTML = "";
    if (!due.length) dc.appendChild(el("div", { class: "card" }, [el("p", { class: "muted", text: "Nothing due. New items are scheduled as you answer them." })]));
    due.forEach(function (id) {
      var rv = S.reviews[id];
      var item = S.bank.find(function (i) { return i.id === id; });
      dc.appendChild(el("div", { class: "card" }, [
        el("h3", { text: item ? "C" + item.chapter + " · " + item.format : id }),
        el("p", { class: "muted", text: "Overdue by " + Math.max(0, Math.round((Date.now() - rv.dueAt) / 3600000)) + " h · interval " + rv.intervalDays + " d" }),
        el("button", { class: "btn btn-small", onclick: function () { startPracticeWith(id); } }, ["Review now"])
      ]));
    });

    var list = $("#dashChapters");
    list.innerHTML = "";
    S.chapters.forEach(function (c) {
      var r = rm[c.chapter];
      var row = el("div", { class: "chapterrow" }, [
        el("strong", { text: "C" + c.chapter }),
        el("span", { text: c.name }),
        el("div", { class: "bar" }, [el("i", { style: "width:" + Math.round((r || 0) * 100) + "%" })]),
        el("span", { class: "num", text: r === null ? "not set" : fmtPct(r) })
      ]);
      list.appendChild(row);
    });
  }

  /* ------------------------------------------------------------ practice */
  function preparePractice() {
    var sel = $("#practiceChapter");
    if (sel.options.length === 0) {
      sel.appendChild(el("option", { value: "0", text: "All chapters (adaptive)" }));
      S.chapters.forEach(function (c) {
        sel.appendChild(el("option", { value: String(c.chapter), text: "C" + c.chapter + " · " + c.name }));
      });
      sel.addEventListener("change", function () { S.practice.item = null; nextQuestion(true); });
      $("#practiceMode").addEventListener("change", function () { /* mode applies to the next item */ });
    }
    if (!S.practice.item) nextQuestion(true);
  }

  function pickExcluding(excluded) {
    var chFilter = Number($("#practiceChapter").value || 0);
    var bank = S.bank;
    if (chFilter) bank = bank.filter(function (i) { return i.chapter === chFilter; });
    var resps = S.responses;
    if (excluded && excluded.length) {
      resps = resps.concat(excluded.map(function (id, i) {
        return { itemId: id, chapter: 0, difficulty: 1, correct: true, confidence: 0.5, timestamp: i };
      }));
    }
    var item = L.selectNextItem(bank, {
      responses: resps,
      roiByChapter: roiMap(),
      readiness: chFilter ? L.estimateReadiness(S.responses, chFilter).readiness : null,
      excludedIds: excluded || []
    });
    return item;
  }

  function nextQuestion(fresh) {
    var item = pickExcluding(fresh ? [] : []);
    S.practice.item = item;
    S.practice.chosen = null;
    S.practice.answered = false;
    renderQuestion();
  }

  function startPracticeWith(itemId) {
    var item = S.bank.find(function (i) { return i.id === itemId; });
    show("practice");
    S.practice.item = item || pickExcluding([]);
    S.practice.chosen = null;
    S.practice.answered = false;
    renderQuestion();
  }

  function renderQuestion() {
    var area = $("#questionArea");
    area.innerHTML = "";
    var item = S.practice.item;
    if (!item) {
      area.appendChild(el("p", { class: "muted", text: "No items available for this filter." }));
      return;
    }
    var strict = $("#practiceMode").value === "strict";
    area.appendChild(el("div", { class: "qmeta" }, [
      el("span", { class: "chip", text: "C" + item.chapter + " · " + item.chapter_name }),
      el("span", { class: "chip", text: item.format + " · " + item.marks + " mark" + (item.marks > 1 ? "s" : "") }),
      el("span", { class: "chip", text: "difficulty " + item.difficulty + "/3" }),
      el("span", { class: "chip", text: item.source_class.toLowerCase() })
    ]));
    area.appendChild(el("div", { class: "qtext", text: item.question }));

    var confWrap = el("div", { class: "confrow" });
    confWrap.appendChild(el("span", { class: "muted", text: "How confident are you?" }));
    var confBtns = [];
    [["Low", 0.3], ["Medium", 0.6], ["High", 0.9]].forEach(function (pair) {
      var b = el("button", { class: "btn btn-ghost btn-small", onclick: function () {
        confBtns.forEach(function (x) { x.disabled = true; });
        S.practice.confidence = pair[1];
        if (item.options) showOptions(pair[1]);
        else showWritten(pair[1]);
      } }, [pair[0]]);
      confBtns.push(b);
      confWrap.appendChild(b);
    });
    area.appendChild(confWrap);
    S.practice.confBtns = confBtns;
  }

  function showOptions(confidence) {
    var item = S.practice.item;
    var strict = $("#practiceMode").value === "strict";
    var area = $("#questionArea");
    var wrap = el("div", { class: "options" });
    item.options.forEach(function (text, idx) {
      var b = el("button", { class: "opt", onclick: function () { answer(idx, confidence, wrap); } }, [String.fromCharCode(65 + idx) + ". " + text]);
      wrap.appendChild(b);
    });
    area.appendChild(wrap);
    if (strict) area.appendChild(el("p", { class: "muted", text: "Strict mode: feedback appears at the end of the session." }));
  }

  function showWritten(confidence) {
    var item = S.practice.item;
    var area = $("#questionArea");
    var ta = el("textarea", { placeholder: "Write your answer (self-marked against the rubric)." });
    area.appendChild(ta);
    area.appendChild(el("button", { class: "btn", onclick: function () { answerWritten(ta.value, confidence); } }, ["Submit for marking"]));
  }

  function answer(choice, confidence, wrap) {
    if (S.practice.answered) return;
    var item = S.practice.item;
    var correct = choice === item.answer_index;
    S.practice.answered = true;
    S.practice.sessionTotal += 1;
    if (correct) S.practice.sessionCorrect += 1;
    Array.prototype.forEach.call(wrap.children, function (b, i) {
      b.disabled = true;
      if (i === item.answer_index) b.classList.add("correct");
      else if (i === choice) b.classList.add("wrong");
    });
    var strict = $("#practiceMode").value === "strict";
    if (!strict) {
      var fb = el("div", { class: "feedback " + (correct ? "good" : "bad") }, [
        el("strong", { text: correct ? "Correct." : "Not correct." }),
        el("p", { text: "Answer: " + (item.options ? item.options[item.answer_index] : item.answer_text) }),
        el("p", { class: "muted", text: item.solution })
      ]);
      $("#questionArea").appendChild(fb);
    }
    record(item, correct, confidence, "practice", correct ? item.marks : 0, item.marks);
    $("#questionArea").appendChild(el("div", { class: "row", style: "margin-top:.9rem" }, [
      el("button", { class: "btn", onclick: function () { nextQuestion(false); } }, ["Next question"])
    ]));
    if (strict) $("#questionArea").appendChild(el("p", { class: "muted", text: "Session: " + S.practice.sessionCorrect + " / " + S.practice.sessionTotal + " correct so far." }));
  }

  function answerWritten(text, confidence) {
    if (S.practice.answered) return;
    var item = S.practice.item;
    S.practice.answered = true;
    var area = $("#questionArea");
    var awarded = 0;
    var sel = el("select", { class: "input" });
    for (var m = 0; m <= item.marks * 2; m++) {
      sel.appendChild(el("option", { value: String(m / 2), text: (m / 2) + " mark" + (m === 2 ? "" : "s") }));
    }
    sel.value = String(item.marks);
    area.appendChild(el("div", { class: "feedback" }, [
      el("strong", { text: "Model answer" }),
      el("p", { text: item.answer_text }),
      el("p", { class: "muted", text: item.solution }),
      el("p", { class: "muted", text: "Rubric: " + item.rubric }),
      el("div", { class: "row" }, [el("span", { class: "muted", text: "Marks I would give myself:" }), sel,
        el("button", { class: "btn btn-small", onclick: function () {
          awarded = Number(sel.value);
          var correct = awarded >= item.marks / 2;
          S.practice.sessionTotal += 1; if (correct) S.practice.sessionCorrect += 1;
          record(item, correct, confidence, "practice", awarded, item.marks);
          sel.disabled = true;
          area.appendChild(el("div", { class: "row", style: "margin-top:.6rem" }, [
            el("button", { class: "btn", onclick: function () { nextQuestion(false); } }, ["Next question"])
          ]));
        } }, ["Save mark"])])
    ]));
    if (!text || !text.trim()) area.appendChild(el("p", { class: "muted", text: "You submitted an empty answer — it is marked 0 unless you say otherwise." }));
  }

  function record(item, correct, confidence, mode, awarded, maxMarks) {
    var resp = {
      itemId: item.id, chapter: item.chapter, difficulty: item.difficulty,
      correct: !!correct, confidence: confidence, mode: mode,
      awarded: awarded, maxMarks: maxMarks, timestamp: Date.now(), appVersion: L.APP_VERSION
    };
    S.responses.push(resp);
    put("responses", resp).catch(function (e) { console.error(e); });
    var rev = L.scheduleReview(S.reviews[item.id] || null, correct, Date.now());
    var rec = Object.assign({ itemId: item.id, chapter: item.chapter }, rev);
    S.reviews[item.id] = rec;
    put("reviews", rec).catch(function (e) { console.error(e); });
  }

  /* ---------------------------------------------------------------- exam */
  function startExam() {
    var seed = Number($("#examSeed").value || 20261115);
    var paper = L.buildExamPaper(S.bank, seed);
    if (!paper.structureValid) {
      alert("The generated paper did not reach 70 marks; this is a bug. No paper was started.");
      return;
    }
    S.exam = {
      paper: paper, answers: {}, startedAt: Date.now(), finishedAt: null,
      remaining: paper.durationMinutes * 60, tick: null, submitted: false
    };
    $("#examAbandon").hidden = false;
    renderExam();
    S.exam.tick = setInterval(function () {
      if (!S.exam || S.exam.submitted) return;
      S.exam.remaining -= 1;
      var t = $("#examTimer");
      if (t) {
        var m = Math.floor(Math.max(0, S.exam.remaining) / 60), s = Math.max(0, S.exam.remaining) % 60;
        t.textContent = (m < 10 ? "0" : "") + m + ":" + (s < 10 ? "0" : "") + s;
      }
      if (S.exam.remaining <= 0) submitExam();
    }, 1000);
  }

  function renderExam() {
    var area = $("#examArea");
    area.innerHTML = "";
    if (!S.exam) {
      area.appendChild(el("p", { class: "muted", text: "No paper in progress." }));
      return;
    }
    if (S.exam.submitted) { renderExamResult(); return; }
    var head = el("div", { class: "row-between" }, [
      el("h2", { text: "Paper " + S.exam.paper.seed + " · " + S.exam.paper.totalMarks + " marks" }),
      el("div", { class: "row" }, [
        el("span", { class: "chip", text: "Time left" }),
        el("strong", { id: "examTimer", text: "180:00" }),
        el("button", { class: "btn", onclick: submitExam }, ["Submit paper"])
      ])
    ]);
    area.appendChild(head);

    S.exam.paper.sections.forEach(function (sec) {
      var marksInSec = sec.questions.reduce(function (a, q) { return a + q.marks; }, 0);
      var block = el("div", { class: "exam-section" }, [
        el("h3", { text: "Section " + sec.section + " · " + sec.questions.length + " questions · " + marksInSec + " marks" })
      ]);
      sec.questions.forEach(function (q, qi) {
        var items = q.composite || [q];
        var qid = "s" + sec.section + "q" + qi;
        var text = items.map(function (it) { return it.question; }).join("  ");
        var opts = items.length === 1 && items[0].options ? items[0].options : null;
        var wrap = el("div", { class: "exam-q" }, [
          el("div", { class: "qtext", text: (qi + 1) + ". " + text + "  [" + q.marks + "]" })
        ]);
        if (opts) {
          var orow = el("div", { class: "options" });
          opts.forEach(function (o, oi) {
            var b = el("button", { class: "opt", onclick: function () {
              Array.prototype.forEach.call(orow.children, function (x) { x.classList.remove("correct"); });
              b.classList.add("correct");
              S.exam.answers[qid] = { choice: oi, items: items.map(function (i) { return i.id; }), marks: q.marks, type: "mcq" };
            } }, [String.fromCharCode(65 + oi) + ". " + o]);
            orow.appendChild(b);
          });
          wrap.appendChild(orow);
        } else {
          var ta = el("textarea", { placeholder: "Your answer (self-marked after submission)." });
          ta.addEventListener("input", function () {
            S.exam.answers[qid] = { text: ta.value, items: items.map(function (i) { return i.id; }), marks: q.marks, type: "written" };
          });
          wrap.appendChild(ta);
        }
        block.appendChild(wrap);
      });
      area.appendChild(block);
    });
  }

  function submitExam() {
    if (!S.exam || S.exam.submitted) return;
    clearInterval(S.exam.tick);
    S.exam.submitted = true;
    S.exam.finishedAt = Date.now();
    renderExamResult();
  }

  function renderExamResult() {
    var area = $("#examArea");
    area.innerHTML = "";
    var paper = S.exam.paper;
    var auto = 0, autoMax = 0;
    var writtenRows = [];
    paper.sections.forEach(function (sec, si) {
      sec.questions.forEach(function (q, qi) {
        var qid = "s" + sec.section + "q" + qi;
        var ans = S.exam.answers[qid];
        var items = q.composite || [q];
        if (q.composite || !items[0].options) {
          writtenRows.push({ qid: qid, q: q, items: items, ans: ans });
        } else {
          autoMax += q.marks;
          if (ans && ans.type === "mcq" && ans.choice === items[0].answer_index) auto += q.marks;
        }
      });
    });

    area.appendChild(el("h2", { text: "Auto-marked: " + auto + " / " + autoMax + " marks" }));
    area.appendChild(el("p", { class: "muted", text: "Written answers are yours to mark. Enter a mark for each and press Save — nothing is guessed on your behalf." }));

    var table = el("table");
    table.appendChild(el("thead", null, [el("tr", null, [
      el("th", { text: "Question" }), el("th", { text: "Max" }), el("th", { text: "Your mark" })
    ])]));
    var tbody = el("tbody");
    var writtenMax = 0, writtenGot = 0;
    var saved = 0;
    writtenRows.forEach(function (row) {
      writtenMax += row.q.marks;
      var sel = el("select", { class: "input" });
      for (var m = 0; m <= row.q.marks * 2; m++) sel.appendChild(el("option", { value: String(m / 2), text: String(m / 2) }));
      sel.value = String(row.ans && row.ans.selfMark !== undefined ? row.ans.selfMark : 0);
      var cell = el("td");
      cell.appendChild(sel);
      var btn = el("button", { class: "btn btn-small", onclick: function () {
        row.ans = row.ans || { items: row.items.map(function (i) { return i.id; }), marks: row.q.marks, type: "written" };
        row.ans.selfMark = Number(sel.value);
        sel.disabled = true; btn.disabled = true;
        row.items.forEach(function (it) {
          var share = row.items.length > 1 ? Number(sel.value) / row.items.length : Number(sel.value);
          record(it, share >= it.marks / 2, 0.6, "exam", Math.min(share, it.marks), it.marks);
        });
        saved += 1;
        if (saved === writtenRows.length) finishExam(auto, autoMax, writtenRows);
      } }, ["Save"]);
      cell.appendChild(btn);
      tbody.appendChild(el("tr", null, [
        el("td", { text: "Section " + row.q.section ? "Section " + (row.q.section || "") : row.qid }),
        el("td", { text: String(row.q.marks) }), cell
      ]));
    });
    table.appendChild(tbody);
    if (writtenRows.length) {
      area.appendChild(el("h3", { text: "Mark your written answers (" + writtenMax + " marks)" }));
      var wrap = el("div", { class: "tablewrap" }); wrap.appendChild(table); area.appendChild(wrap);
    } else {
      finishExam(auto, autoMax, writtenRows);
    }
    area.appendChild(el("div", { class: "row", style: "margin-top:1rem" }, [
      el("button", { class: "btn btn-ghost", onclick: function () { S.exam = null; $("#examAbandon").hidden = true; $("#examArea").innerHTML = ""; } }, ["Done"])
    ]));
  }

  function finishExam(auto, autoMax, writtenRows) {
    var writtenGot = 0, writtenMax = 0;
    writtenRows.forEach(function (r) {
      writtenMax += r.q.marks;
      if (r.ans && r.ans.selfMark !== undefined) writtenGot += r.ans.selfMark;
    });
    var total = auto + writtenGot, max = autoMax + writtenMax;
    var area = $("#examArea");
    var summary = el("div", { class: "feedback good" }, [
      el("strong", { text: "Paper complete: " + fmtNum(total, 1) + " / " + max }),
      el("p", { class: "muted", text: "Auto-marked " + auto + "/" + autoMax + " · self-marked " + fmtNum(writtenGot, 1) + "/" + writtenMax + ". Every answer is now in your progress data." })
    ]);
    area.insertBefore(summary, area.firstChild);
    S.exam.submitted = true;
  }

  /* ------------------------------------------------------------ progress */
  function renderProgress() {
    var rm = readinessMap();
    var brier = L.brierScore(S.responses);
    var correct = S.responses.filter(function (r) { return r.correct; }).length;
    var stats = [
      ["Answers", S.responses.length],
      ["Correct", correct + (S.responses.length ? " (" + Math.round(100 * correct / S.responses.length) + "%)" : "")],
      ["Brier score", brier === null ? "—" : fmtNum(brier, 3)],
      ["Study minutes", Math.round(S.sessions.reduce(function (a, s) { return a + (s.activeSeconds || 0); }, 0) / 60)]
    ];
    var box = $("#progressStats"); box.innerHTML = "";
    stats.forEach(function (s) { box.appendChild(el("div", { class: "stat" }, [el("b", { text: String(s[1]) }), el("span", { text: s[0] })])); });

    var table = el("table");
    table.appendChild(el("thead", null, [el("tr", null, [
      el("th", { text: "Ch" }), el("th", { text: "Chapter" }), el("th", { text: "Attempts" }),
      el("th", { text: "Readiness" }), el("th", { text: "Confidence" }), el("th", { text: "Gap" }),
      el("th", { text: "Research rank" }), el("th", { text: "Status" })
    ])]));
    var tb = el("tbody");
    S.chapters.forEach(function (c) {
      var est = L.estimateReadiness(S.responses, c.chapter);
      tb.appendChild(el("tr", null, [
        el("td", { text: "C" + c.chapter }),
        el("td", { text: c.name }),
        el("td", { text: String(est.attempts) }),
        el("td", { text: est.readiness === null ? "—" : fmtPct(est.readiness) }),
        el("td", { text: est.meanConfidence === undefined ? "—" : fmtPct(est.meanConfidence) }),
        el("td", { text: est.calibrationGap === null || est.calibrationGap === undefined ? "—" : (est.calibrationGap > 0 ? "+" : "") + fmtPct(est.calibrationGap) }),
        el("td", { text: String(c.researchRank) }),
        el("td", { text: est.provisional ? "provisional" : "measured" })
      ]));
    });
    table.appendChild(tb);
    var wrap = $("#progressTable"); wrap.innerHTML = ""; wrap.appendChild(table);

    var buckets = L.calibrationBuckets(S.responses);
    var ct = el("table");
    ct.appendChild(el("thead", null, [el("tr", null, [
      el("th", { text: "Confidence band" }), el("th", { text: "Answers" }),
      el("th", { text: "Mean confidence" }), el("th", { text: "Actual accuracy" }), el("th", { text: "Gap" })
    ])]));
    var cb = el("tbody");
    buckets.forEach(function (b) {
      cb.appendChild(el("tr", null, [
        el("td", { text: b.band }), el("td", { text: String(b.n) }),
        el("td", { text: b.meanConfidence === null ? "—" : fmtPct(b.meanConfidence) }),
        el("td", { text: b.observedAccuracy === null ? "—" : fmtPct(b.observedAccuracy) }),
        el("td", { text: b.meanConfidence === null || b.observedAccuracy === null ? "—" : (b.meanConfidence - b.observedAccuracy > 0 ? "+" : "") + fmtPct(b.meanConfidence - b.observedAccuracy) })
      ]));
    });
    ct.appendChild(cb);
    var cw = $("#calibration"); cw.innerHTML = ""; cw.appendChild(ct);
  }

  /* --------------------------------------------------------------- study */
  function startTimer(withBreak) {
    if (!S.timer.running) {
      S.timer.running = true;
      S.timer.startAt = Date.now();
      S.timer.events = [{ type: "start", at: Date.now() }];
      $("#timerStart").disabled = true;
      $("#timerBreak").disabled = false;
      $("#timerStop").disabled = false;
      $("#timerState").textContent = "Studying";
      S.timer.tick = setInterval(paintTimer, 1000);
      paintTimer();
    }
  }

  function paintTimer() {
    var t = S.timer;
    var now = Date.now();
    var summary = L.summariseSession(t.events.concat([{ type: "stop", at: now }]));
    var secs = summary.activeSeconds;
    var h = Math.floor(secs / 3600), m = Math.floor((secs % 3600) / 60), s = secs % 60;
    $("#timerDisplay").textContent = [h, m, s].map(function (x) { return (x < 10 ? "0" : "") + x; }).join(":");
    $("#timerState").textContent = (t.onBreak ? "On break · " : "Studying · ") + "break " + Math.round(summary.breakSeconds / 60) + " min";
  }

  function toggleBreak() {
    var t = S.timer;
    if (!t.running) return;
    if (!t.onBreak) { t.events.push({ type: "break_start", at: Date.now() }); t.onBreak = true; $("#timerBreak").textContent = "End break"; }
    else { t.events.push({ type: "break_end", at: Date.now() }); t.onBreak = false; $("#timerBreak").textContent = "Start break"; }
    paintTimer();
  }

  function stopTimer() {
    var t = S.timer;
    if (!t.running) return;
    t.events.push({ type: "stop", at: Date.now() });
    clearInterval(t.tick);
    var sum = L.summariseSession(t.events);
    if (sum.activeSeconds < 30) {
      $("#timerState").textContent = "Session under 30 s was not saved.";
    } else {
      var session = {
        startedAt: t.events[0].at, endedAt: Date.now(),
        activeSeconds: sum.activeSeconds, breakSeconds: sum.breakSeconds,
        longBreaks: sum.longBreaks, appVersion: L.APP_VERSION
      };
      S.sessions.push(session);
      put("sessions", session).catch(function (e) { console.error(e); });
      $("#timerState").textContent = "Saved: " + Math.round(sum.activeSeconds / 60) + " min study, " + Math.round(sum.breakSeconds / 60) + " min break.";
      renderSessions();
    }
    t.running = false; t.onBreak = false; t.events = [];
    $("#timerStart").disabled = false;
    $("#timerBreak").disabled = true; $("#timerBreak").textContent = "Start break";
    $("#timerStop").disabled = true;
    $("#timerDisplay").textContent = "00:00:00";
  }

  function renderSessions() {
    var wrap = $("#sessionList");
    wrap.innerHTML = "";
    if (!S.sessions.length) { wrap.appendChild(el("p", { class: "muted", text: "No sessions yet." })); return; }
    var table = el("table");
    table.appendChild(el("thead", null, [el("tr", null, [
      el("th", { text: "Started" }), el("th", { text: "Study (min)" }), el("th", { text: "Break (min)" }), el("th", { text: "Long breaks" })
    ])]));
    var tb = el("tbody");
    S.sessions.slice().sort(function (a, b) { return b.startedAt - a.startedAt; }).slice(0, 12).forEach(function (s) {
      tb.appendChild(el("tr", null, [
        el("td", { text: new Date(s.startedAt).toLocaleString() }),
        el("td", { text: String(Math.round(s.activeSeconds / 60)) }),
        el("td", { text: String(Math.round(s.breakSeconds / 60)) }),
        el("td", { text: String(s.longBreaks || 0) })
      ]));
    });
    table.appendChild(tb);
    wrap.appendChild(table);
  }

  /* ---------------------------------------------------------------- data */
  function backupObject() {
    return {
      app: APP, schema: L.STATE_SCHEMA, appVersion: L.APP_VERSION,
      exportedAt: new Date().toISOString(),
      settings: S.settings, responses: S.responses,
      reviews: S.reviews, sessions: S.sessions
    };
  }

  function exportBackup() {
    var blob = new Blob([JSON.stringify(backupObject(), null, 1)], { type: "application/json" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "physics2027-backup-" + L.snapshotLabel() + ".json";
    document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
  }

  function importBackup(file) {
    var report = $("#importReport");
    var reader = new FileReader();
    reader.onload = function () {
      var data;
      try { data = JSON.parse(reader.result); }
      catch (e) { return notice(report, "Import failed: the file is not valid JSON.", "bad"); }
      var check = L.validateBackup(data);
      if (!check.ok) return notice(report, "Import refused: " + check.errors.join("; "), "bad");
      var migrated = L.migrateBackup(data);
      var proceed = confirm("Importing will replace your current data (" + S.responses.length + " answers, " + S.sessions.length + " sessions). Continue?");
      if (!proceed) return notice(report, "Import cancelled. Your data is unchanged.", "");
      Promise.all([clearStore("responses"), clearStore("reviews"), clearStore("sessions"), clearStore("meta")])
        .then(function () {
          S.responses = migrated.responses; S.reviews = migrated.reviews || {};
          S.sessions = migrated.sessions; S.settings = migrated.settings || {};
          return Promise.all(
            migrated.responses.map(function (r) { return put("responses", r); })
              .concat(Object.keys(S.reviews).map(function (k) { return put("reviews", S.reviews[k]); }))
              .concat(S.sessions.map(function (s) { return put("sessions", s); }))
              .concat([put("meta", { key: SETTINGS_KEY, value: S.settings }), put("meta", { key: "schema", value: L.STATE_SCHEMA })])
          );
        })
        .then(function () {
          notice(report, "Imported " + S.responses.length + " answers and " + S.sessions.length + " sessions.", "good");
          renderDashboard(); renderData();
        })
        .catch(function (e) { notice(report, "Import failed while writing: " + e.message, "bad"); });
    };
    reader.readAsText(file);
  }

  function saveSnapshot() {
    getKey("meta", SNAPSHOT_KEY).then(function (rec) {
      var list = (rec && rec.value) || [];
      list.unshift({ label: L.snapshotLabel(), createdAt: Date.now(), state: backupObject() });
      list = list.slice(0, 10);
      return put("meta", { key: SNAPSHOT_KEY, value: list });
    }).then(function () { renderData(); });
  }

  function restoreSnapshot(idx) {
    getKey("meta", SNAPSHOT_KEY).then(function (rec) {
      var list = (rec && rec.value) || [];
      var snap = list[idx];
      if (!snap) return;
      if (!confirm("Restore the snapshot from " + snap.label + "? Current data will be replaced (a fresh snapshot of the current state is saved first).")) return;
      return saveSnapshot().then(function () {
        var data = snap.state;
        var check = L.validateBackup(data);
        if (!check.ok) { alert("Snapshot is not valid: " + check.errors.join("; ")); return; }
        var migrated = L.migrateBackup(data);
        return Promise.all([clearStore("responses"), clearStore("reviews"), clearStore("sessions")]).then(function () {
          S.responses = migrated.responses; S.reviews = migrated.reviews || {}; S.sessions = migrated.sessions;
          return Promise.all(migrated.responses.map(function (r) { return put("responses", r); })
            .concat(Object.keys(S.reviews).map(function (k) { return put("reviews", S.reviews[k]); }))
            .concat(S.sessions.map(function (s) { return put("sessions", s); })));
        }).then(function () { renderDashboard(); renderData(); });
      });
    });
  }

  function renderData() {
    $("#dataSummary").textContent = JSON.stringify({
      app: APP, schema: L.STATE_SCHEMA, appVersion: L.APP_VERSION,
      responses: S.responses.length, reviews: Object.keys(S.reviews).length,
      sessions: S.sessions.length, bank_items: S.bank.length,
      storage: "IndexedDB " + DB_NAME
    }, null, 1);
    getKey("meta", SNAPSHOT_KEY).then(function (rec) {
      var list = (rec && rec.value) || [];
      var wrap = $("#versionList");
      wrap.innerHTML = "";
      if (!list.length) { wrap.appendChild(el("p", { class: "muted", text: "No snapshots yet." })); return; }
      var table = el("table");
      table.appendChild(el("thead", null, [el("tr", null, [
        el("th", { text: "Snapshot" }), el("th", { text: "Answers" }), el("th", { text: "Sessions" }), el("th", { text: "" })
      ])]));
      var tb = el("tbody");
      list.forEach(function (s, i) {
        tb.appendChild(el("tr", null, [
          el("td", { text: s.label }),
          el("td", { text: String((s.state.responses || []).length) }),
          el("td", { text: String((s.state.sessions || []).length) }),
          el("td", null, [el("button", { class: "btn btn-small btn-ghost", onclick: function () { restoreSnapshot(i); } }, ["Restore"])])
        ]));
      });
      table.appendChild(tb); wrap.appendChild(table);
    });
  }

  function wipe() {
    if (!confirm("Delete all answers, reviews, sessions and snapshots stored in this browser? Export a backup first if you might want them.")) return;
    if (!confirm("This cannot be undone. Delete everything now?")) return;
    Promise.all([clearStore("responses"), clearStore("reviews"), clearStore("sessions"), clearStore("meta")]).then(function () {
      S.responses = []; S.reviews = {}; S.sessions = []; S.settings = {};
      renderDashboard(); renderData();
    });
  }

  /* --------------------------------------------------------------- about */
  function renderAbout() {
    var box = $("#aboutBody");
    box.innerHTML = "";
    var sections = [
      ["What this app is", "An offline diagnostic and revision tool for the CBSE Class XII Physics (042) 2027 theory paper. It measures your chapter readiness from your own answers, recommends where the next hour is best spent, schedules revision, and runs strict exam simulations. Chapter level only — it deliberately contains no topic-level analysis."],
      ["What the numbers mean", "Readiness is a weighted accuracy (harder questions count more) shrunk towards 50% until five questions are answered, so early estimates are cautious. Confidence is recorded before each answer; the Brier score and the confidence table tell you whether you are over- or under-confident. Recommendations use your measured readiness together with the research model's chapter exposure and preparation hours."],
      ["Where the research values come from", "Chapter exposure, hours and ROI tiers are copied read-only from the research model (v1.0.0) built for the 2026-27 syllabus. The app never edits them, and never mixes them into your measured readiness."],
      ["Question bank", "84 original questions (6 per chapter: four multiple-choice, one assertion–reason, one written with a rubric). No CBSE previous-year question text and no MTG content is reproduced. Every item is labelled ORIGINAL."],
      ["Privacy", "Nothing leaves this device. There is no account, no analytics and no network request after installation. Backups are JSON files you create and control."],
      ["Known limitations", "The adaptive engine and scheduler are validated by logic tests and data-integrity checks, not by real-student calibration. 84 questions is a small bank: repeats begin after a few sessions. Self-marked written answers are only as honest as the marking. Browser storage can be cleared by the browser itself — keep backups."],
      ["Version", "App " + L.APP_VERSION + " · schema " + L.STATE_SCHEMA + " · bank " + S.bank.length + " items · research model 1.0.0 (2026-27 syllabus)"]
    ];
    sections.forEach(function (s) {
      box.appendChild(el("div", { class: "card", style: "margin:.6rem 0" }, [
        el("h3", { text: s[0] }), el("p", { class: "muted", text: s[1] })
      ]));
    });
  }

  /* ---------------------------------------------------------------- boot */
  function wire() {
    document.querySelectorAll(".tab").forEach(function (t) {
      t.addEventListener("click", function () { show(t.dataset.view); });
    });
    $("#timerStart").addEventListener("click", function () { startTimer(); });
    $("#timerBreak").addEventListener("click", toggleBreak);
    $("#timerStop").addEventListener("click", stopTimer);
    $("#examStart").addEventListener("click", startExam);
    $("#examAbandon").addEventListener("click", function () {
      if (!confirm("Abandon this paper? Nothing will be saved.")) return;
      if (S.exam && S.exam.tick) clearInterval(S.exam.tick);
      S.exam = null; $("#examAbandon").hidden = true; $("#examArea").innerHTML = "";
    });
    $("#exportBtn").addEventListener("click", exportBackup);
    $("#importFile").addEventListener("change", function (e) {
      if (e.target.files && e.target.files[0]) importBackup(e.target.files[0]);
    });
    $("#snapshotBtn").addEventListener("click", saveSnapshot);
    $("#wipeBtn").addEventListener("click", wipe);
    window.addEventListener("online", paintNet);
    window.addEventListener("offline", paintNet);
    window.addEventListener("beforeinstallprompt", function (e) {
      e.preventDefault();
      var btn = $("#installBtn");
      btn.hidden = false;
      btn.addEventListener("click", function () { e.prompt(); });
    });
  }

  function paintNet() {
    var b = $("#netBadge");
    var on = navigator.onLine;
    b.textContent = on ? "online" : "offline — fully usable";
    b.className = "badge " + (on ? "badge-on" : "badge-off");
  }

  function registerSW() {
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("sw.js").catch(function (e) { console.warn("Service worker registration failed", e); });
    }
  }

  function boot() {
    wire();
    paintNet();
    registerSW();
    $("#footVersion").textContent = "v" + L.APP_VERSION;
    Promise.all([
      fetch("data/research_ranking.json").then(function (r) { return r.json(); }),
      fetch("data/question_bank.json").then(function (r) { return r.json(); }),
      openDB()
    ]).then(function (res) {
      S.research = res[0];
      S.chapters = res[0].chapters;
      S.bank = res[1].items;
      S.db = res[2];
      return Promise.all([getAll("responses"), getAll("reviews"), getAll("sessions"), getKey("meta", SETTINGS_KEY)]);
    }).then(function (res) {
      S.responses = res[0] || [];
      (res[1] || []).forEach(function (r) { S.reviews[r.itemId] = r; });
      S.sessions = res[2] || [];
      S.settings = (res[3] && res[3].value) || {};
      renderDashboard();
    }).catch(function (e) {
      console.error(e);
      document.querySelector("#dashStats").innerHTML =
        '<div class="notice bad">The app could not load its data: ' + e.message + '</div>';
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
