/* PYTHIA -- application shell.
 *
 * Views register themselves on PYTHIA.views. The navigation is built from
 * whatever has registered, so a section that does not exist yet simply does
 * not appear. No dead links.
 */
(function (root) {
  "use strict";

  var ORDER = ["explore", "stereochemistry", "nomenclature", "mechanisms",
               "pathways", "spectroscopy", "calculators", "glossary"];

  function available() {
    var views = root.PYTHIA && root.PYTHIA.views ? root.PYTHIA.views : {};
    var out = [];
    ORDER.forEach(function (key) {
      if (views[key]) out.push({ key: key, view: views[key] });
    });
    // anything registered but not listed in ORDER still gets a place
    Object.keys(views).forEach(function (key) {
      if (ORDER.indexOf(key) < 0) out.push({ key: key, view: views[key] });
    });
    return out;
  }

  function currentKey(list) {
    var want = (root.location.hash || "").replace(/^#\/?/, "");
    for (var i = 0; i < list.length; i++) {
      if (list[i].key === want) return want;
    }
    return list.length ? list[0].key : null;
  }

  function renderNav(list, active) {
    var nav = document.getElementById("nav");
    if (!nav) return;
    nav.innerHTML = "";
    list.forEach(function (entry) {
      var a = document.createElement("a");
      a.href = "#/" + entry.key;
      a.textContent = entry.view.label || entry.key;
      if (entry.key === active) a.setAttribute("aria-current", "page");
      nav.appendChild(a);
    });
  }

  /* The footer lists every source the loaded data cites, deduplicated, with
   * whether it ships inside this repository or is only referenced. A reader
   * who wants to check something should not have to go looking.
   *
   * Every dataset is walked, not just the molecules. A citation that the
   * build validated but the interface never shows is a citation that might
   * as well not exist. */
  function renderSources() {
    var host = document.getElementById("sources");
    var registry = root.PYTHIA_SOURCES;
    if (!host || !registry) return;

    var cited = {};
    function take(keys) {
      (keys || []).forEach(function (k) { cited[k] = true; });
    }

    (root.PYTHIA_MOLECULES || []).forEach(function (m) { take(m.sources); });
    (root.PYTHIA_MECHANISMS || []).forEach(function (m) { take(m.sources); });
    (root.PYTHIA_LESSONS || []).forEach(function (l) { take(l.sources); });
    (root.PYTHIA_PATHWAYS || []).forEach(function (p) { take(p.sources); });
    if (root.PYTHIA_NOMENCLATURE) take(root.PYTHIA_NOMENCLATURE.sources);
    if (root.PYTHIA_SPECTROSCOPY) take(root.PYTHIA_SPECTROSCOPY.sources);
    if (root.PYTHIA_GLOSSARY) take(root.PYTHIA_GLOSSARY.sources);

    // both ship in the repository whether or not any record names them
    cited["3dmol"] = true;
    cited["ciaaw"] = true;

    var keys = Object.keys(cited).sort(function (a, b) {
      var A = registry[a], B = registry[b];
      if (!A || !B) return 0;
      return (A.authors || "").localeCompare(B.authors || "");
    });

    host.innerHTML = "";
    keys.forEach(function (k) {
      var s = registry[k];
      if (!s) return;
      var item = document.createElement("p");
      item.className = "source-item";

      var b = document.createElement("b");
      b.textContent = s.title;
      item.appendChild(b);

      var parts = [];
      if (s.authors) parts.push(s.authors);
      if (s.publisher) parts.push(s.publisher);
      if (s.year) parts.push(String(s.year));
      if (s.where) parts.push(s.where);
      if (s.licence) {
        parts.push(s.licence
          + (s.use === "redistributed" ? ", included here" : ", cited only"));
      }
      item.appendChild(document.createTextNode(" \u2014 " + parts.join(". ")));

      if (s.url) {
        item.appendChild(document.createTextNode(" "));
        var a = document.createElement("a");
        a.href = s.url;
        a.textContent = s.url.replace(/^https?:\/\//, "");
        a.rel = "noopener noreferrer";
        item.appendChild(a);
      }
      host.appendChild(item);
    });
  }

  function route() {
    var list = available();
    if (!list.length) return;
    var key = currentKey(list);
    renderNav(list, key);
    var entry = list.filter(function (e) { return e.key === key; })[0];
    if (entry && entry.view.render) entry.view.render();
  }

  function start() {
    route();
    renderSources();
    root.addEventListener("hashchange", route);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})(typeof window !== "undefined" ? window : this);
