/*
 * sw.js - offline shell for the Physics 2027 diagnostic app.
 * Strategy: precache the shell and data on install, serve cache-first with a
 * background refresh for data files. Version string changes force a new cache.
 */
var CACHE = "physics2027-v1.0.0";
var SHELL = [
  "./",
  "index.html",
  "styles.css",
  "logic.js",
  "app.js",
  "manifest.webmanifest",
  "data/research_ranking.json",
  "data/question_bank.json",
  "icons/icon-192.png",
  "icons/icon-512.png"
];

self.addEventListener("install", function (event) {
  event.waitUntil(
    caches.open(CACHE).then(function (cache) {
      return cache.addAll(SHELL).catch(function (e) {
        /* A missing optional asset must not block installation of the rest. */
        console.warn("precache partial:", e);
        return Promise.all(SHELL.map(function (u) {
          return cache.add(u).catch(function () { return null; });
        }));
      });
    }).then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function (event) {
  event.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.filter(function (k) { return k !== CACHE; })
        .map(function (k) { return caches.delete(k); }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener("fetch", function (event) {
  var req = event.request;
  if (req.method !== "GET") return;
  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return;   /* never cache third parties */

  event.respondWith(
    caches.match(req).then(function (hit) {
      if (hit) {
        /* refresh data files quietly; shell files stay as installed */
        if (/\.(json)$/.test(url.pathname)) {
          fetch(req).then(function (res) {
            if (res && res.ok) caches.open(CACHE).then(function (c) { c.put(req, res.clone()); });
          }).catch(function () {});
        }
        return hit;
      }
      return fetch(req).then(function (res) {
        if (res && res.ok) {
          var copy = res.clone();
          caches.open(CACHE).then(function (c) { c.put(req, copy); });
        }
        return res;
      }).catch(function () {
        return caches.match("index.html");   /* navigation fallback when offline */
      });
    })
  );
});
