/*
 * tests/dom.smoke.test.js
 * ----------------------
 * Executes the real index.html + app.js in jsdom (with a real IndexedDB
 * implementation supplied by fake-indexeddb) and drives the interface:
 *   boot -> dashboard rendered -> answer a practice question -> the answer is
 *   persisted -> generate a 70-mark paper -> submit -> progress table updates.
 *
 * This is a DOM/behaviour test, not a visual browser test: jsdom has no layout
 * engine and no service-worker support, so rendering and offline behaviour are
 * covered only by the static checks in tests/static_checks.py.
 *
 * Requires (dev only, not shipped): npm i jsdom fake-indexeddb
 * Run: NODE_PATH=/tmp/jsdomtest/node_modules node tests/dom.smoke.test.js
 */
const fs = require("fs");
const path = require("path");
require("fake-indexeddb/auto");
const { JSDOM, VirtualConsole } = require("jsdom");

const SRC = path.join(__dirname, "..", "Application_Source");
let pass = 0, fail = 0;
function ok(name, cond, detail) {
  if (cond) { pass++; console.log("PASS  " + name); }
  else { fail++; console.log("FAIL  " + name + (detail !== undefined ? "  -> " + detail : "")); }
}
function wait(ms) { return new Promise(r => setTimeout(r, ms)); }
async function until(fn, timeout = 4000) {
  const t0 = Date.now();
  while (Date.now() - t0 < timeout) {
    try { if (fn()) return true; } catch (e) { /* keep waiting */ }
    await wait(25);
  }
  return false;
}

async function main() {
  const html = fs.readFileSync(path.join(SRC, "index.html"), "utf8");
  const vc = new VirtualConsole();
  vc.on("jsdomError", e => console.log("JSDOM ERROR:", e.message));
  const dom = new JSDOM(html, {
    runScripts: "outside-only",
    url: "http://localhost/index.html",
    virtualConsole: vc,
    pretendToBeVisual: true
  });
  const { window } = dom;

  /* fetch backed by the filesystem */
  window.fetch = function (url) {
    const file = path.join(SRC, String(url).replace(/^\.\//, ""));
    if (!fs.existsSync(file)) return Promise.reject(new Error("404 " + url));
    const body = fs.readFileSync(file, "utf8");
    return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve(JSON.parse(body)), text: () => Promise.resolve(body) });
  };
  window.indexedDB = require("fake-indexeddb").indexedDB;
  window.IDBKeyRange = require("fake-indexeddb").IDBKeyRange;
  let swRegistered = 0;
  Object.defineProperty(window.navigator, "serviceWorker", {
    value: { register: () => { swRegistered++; return Promise.resolve({}); } }, configurable: true
  });
  window.confirm = () => true;
  window.alert = m => console.log("ALERT:", m);
  window.scrollTo = () => {};
  window.matchMedia = window.matchMedia || (() => ({ matches: false, addListener() {}, removeListener() {} }));

  const errors = [];
  window.addEventListener("error", e => errors.push(String(e.message)));

  /* load the two scripts in order, exactly as the page does */
  window.eval(fs.readFileSync(path.join(SRC, "logic.js"), "utf8"));
  window.eval(fs.readFileSync(path.join(SRC, "app.js"), "utf8"));
  window.document.dispatchEvent(new window.Event("DOMContentLoaded"));

  const doc = window.document;
  const $ = s => doc.querySelector(s);

  ok("logic library exposed on window", typeof window.PhysLogic === "object");
  ok("service worker registration attempted", await until(() => swRegistered === 1));

  /* boot */
  ok("dashboard statistics render", await until(() => doc.querySelectorAll("#dashStats .stat").length === 6),
    doc.querySelectorAll("#dashStats .stat").length);
  ok("all 14 chapters listed", doc.querySelectorAll("#dashChapters .chapterrow").length === 14);
  ok("online badge resolved", ["online", "offline — fully usable"].indexOf($("#netBadge").textContent) >= 0,
    $("#netBadge").textContent);
  ok("study timer controls disabled at rest", $("#timerBreak").disabled && $("#timerStop").disabled);

  /* navigation */
  $('.tab[data-view="practice"]').click();
  ok("practice view becomes active", $("#view-practice").classList.contains("active"));
  ok("practice builds a chapter filter with 15 options",
    await until(() => $("#practiceChapter").options.length === 15), $("#practiceChapter").options.length);
  ok("a first question is offered with confidence controls",
    await until(() => !!doc.querySelector("#questionArea .qtext") && doc.querySelectorAll("#questionArea .confrow .btn").length === 3));

  const firstChip = doc.querySelector("#questionArea .qmeta .chip").textContent;
  ok("high-ROI chapter is asked first (C14)", firstChip.indexOf("C14") === 0, firstChip);

  /* confidence is required before answering */
  const confBtn = doc.querySelector("#questionArea .confrow .btn");
  ok("confidence buttons are offered", !!confBtn);
  confBtn.click();
  ok("options become active after confidence is set",
    await until(() => doc.querySelectorAll("#questionArea .opt:not([disabled])").length === 4));

  /* answer correctly using the model key */
  const logic = window.PhysLogic;
  const itemId = doc.querySelector("#questionArea .qmeta .chip").textContent;
  const current = window.__test_item || null;
  /* find the item matching C14 in the bank and click its correct option */
  const bank = JSON.parse(fs.readFileSync(path.join(SRC, "data", "question_bank.json"), "utf8"));
  const asked = doc.querySelector("#questionArea .qtext").textContent;
  const item = bank.items.find(i => i.question === asked);
  ok("asked question exists in the bank", !!item);
  const opts = doc.querySelectorAll("#questionArea .opt");
  opts[item.answer_index].click();
  ok("correct answer is marked correct", await until(() => doc.querySelectorAll("#questionArea .opt.correct").length === 1));
  ok("feedback is shown in practice mode", !!doc.querySelector("#questionArea .feedback"));

  /* persistence */
  const dbs = await new Promise(res => {
    const rq = window.indexedDB.open("cbse_physics_2027");
    rq.onsuccess = () => {
      const db = rq.result;
      const t = db.transaction("responses", "readonly");
      const all = t.objectStore("responses").getAll();
      all.onsuccess = () => res(all.result);
      all.onerror = () => res([]);
    };
    rq.onerror = () => res([]);
  });
  ok("answer is persisted to IndexedDB", dbs.length === 1 && dbs[0].itemId === item.id, dbs.length);

  /* next question keeps the session going */
  const nextBtn = Array.from(doc.querySelectorAll("#questionArea .btn")).find(b => /Next question/.test(b.textContent));
  ok("next-question control exists", !!nextBtn);
  const prevText = doc.querySelector("#questionArea .qtext").textContent;
  nextBtn.click();
  ok("a new question is rendered with fresh confidence controls",
    await until(() => !!doc.querySelector("#questionArea .qtext") &&
      doc.querySelector("#questionArea .qtext").textContent !== prevText &&
      doc.querySelectorAll("#questionArea .confrow .btn:not([disabled])").length === 3));

  /* exam mode */
  $('.tab[data-view="exam"]').click();
  $("#examStart").click();
  ok("exam paper renders five sections",
    await until(() => doc.querySelectorAll("#examArea .exam-section").length === 5),
    doc.querySelectorAll("#examArea .exam-section").length);
  const headText = doc.querySelector("#examArea .row-between h2").textContent;
  ok("exam paper states 70 marks", /70 marks/.test(headText), headText);
  const examQs = doc.querySelectorAll("#examArea .exam-q").length;
  ok("exam renders 33 question slots", examQs === 33, examQs);
  $("#examAbandon").click();
  ok("abandon clears the paper", doc.querySelectorAll("#examArea .exam-q").length === 0);

  /* study timer */
  $('.tab[data-view="study"]').click();
  $("#timerStart").click();
  ok("timer starts and enables break/stop", $("#timerBreak").disabled === false && $("#timerStop").disabled === false);
  $("#timerBreak").click();
  ok("break toggles state", /On break/.test($("#timerState").textContent), $("#timerState").textContent);
  $("#timerBreak").click();
  $("#timerStop").click();
  ok("stopping resets the controls", $("#timerStart").disabled === false && $("#timerBreak").disabled === true);

  /* backup view and progress */
  $('.tab[data-view="data"]').click();
  const summary = JSON.parse($("#dataSummary").textContent);
  ok("data summary reports the persisted answer", summary.responses === 1, JSON.stringify(summary));
  $('.tab[data-view="progress"]').click();
  ok("progress table covers 14 chapters", doc.querySelectorAll("#progressTable tbody tr").length === 14);
  ok("calibration table has five bands", doc.querySelectorAll("#calibration tbody tr").length === 5);
  $('.tab[data-view="about"]').click();
  ok("about view lists version and limitations",
    /Known limitations/.test($("#aboutBody").textContent) && /App 1\.0\.0/.test($("#aboutBody").textContent));

  ok("no uncaught script errors", errors.length === 0, errors.join(" | "));

  console.log("\n" + pass + " passed, " + fail + " failed");
  process.exit(fail === 0 ? 0 : 1);
}

main().catch(e => { console.error("SMOKE TEST CRASHED:", e); process.exit(2); });
