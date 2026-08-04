/* PYTHIA -- the Glossary.
 *
 * The vocabulary used everywhere else, in one place. Cross-references are
 * live: a term that mentions another can be followed to it, which is what
 * makes a glossary usable rather than merely present.
 *
 * Where two words are routinely confused, the entry pairs them. That
 * pairing is most of the value here: nobody looks up "conformation"
 * because they have never met it, they look it up because they cannot
 * keep it apart from configuration.
 */
(function (root) {
  "use strict";

  var state = { term: null, filter: "" };

  var SECTION_ORDER = ["Stereochemistry", "Nomenclature", "Mechanisms",
                       "Biochemistry", "Spectroscopy", "Calculation"];

  function h(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      for (var k in attrs) {
        if (k === "class") node.className = attrs[k];
        else if (k === "text") node.textContent = attrs[k];
        else if (attrs[k] !== null && attrs[k] !== undefined) {
          node.setAttribute(k, attrs[k]);
        }
      }
    }
    (children || []).forEach(function (c) { if (c) node.appendChild(c); });
    return node;
  }

  function terms() {
    var d = root.PYTHIA_GLOSSARY;
    return d ? d.terms : [];
  }

  function find(name) {
    var all = terms();
    for (var i = 0; i < all.length; i++) {
      if (all[i].term === name) return all[i];
    }
    return null;
  }

  function matches(t, q) {
    if (!q) return true;
    q = q.toLowerCase();
    return (t.term + " " + (t.aka || "") + " " + t.definition + " "
            + t.section).toLowerCase().indexOf(q) >= 0;
  }

  function molecule(id) {
    var all = root.PYTHIA_MOLECULES || [];
    for (var i = 0; i < all.length; i++) {
      if (all[i].id === id) return all[i];
    }
    return null;
  }

  /* ---- browser --------------------------------------------------------- */

  function renderBrowser(onPick) {
    var box = h("div", { class: "browser" });

    var search = h("input", {
      type: "search",
      class: "search",
      placeholder: "Search the glossary",
      "aria-label": "Search the glossary",
      value: state.filter
    });
    search.addEventListener("input", function () {
      state.filter = search.value;
      var old = box.querySelector(".group-list");
      old.replaceWith(renderList(onPick));
    });

    box.appendChild(search);
    box.appendChild(renderList(onPick));
    return box;
  }

  function renderList(onPick) {
    var wrap = h("div", { class: "group-list" });
    var shown = 0;

    SECTION_ORDER.forEach(function (section) {
      var items = terms().filter(function (t) {
        return t.section === section && matches(t, state.filter);
      });
      if (!items.length) return;
      shown += items.length;

      wrap.appendChild(h("p", { class: "label group-name", text: section }));
      var ul = h("ul", { class: "mol-list" });
      items.forEach(function (t) {
        var btn = h("button", {
          type: "button",
          text: t.term,
          "aria-current": t.term === state.term ? "true" : null
        });
        btn.addEventListener("click", function () { onPick(t.term); });
        ul.appendChild(h("li", null, [btn]));
      });
      wrap.appendChild(ul);
    });

    if (!shown) {
      wrap.appendChild(h("p", {
        class: "hint",
        text: "Nothing matches \u201c" + state.filter + "\u201d."
      }));
    }
    return wrap;
  }

  /* ---- entry ----------------------------------------------------------- */

  function renderEntry(t) {
    var kids = [
      h("div", { class: "section-head" }, [
        h("h2", { text: t.term }),
        h("p", { text: t.aka ? t.section + " \u00b7 also " + t.aka
                             : t.section })
      ]),
      h("p", { class: "lesson-blurb", text: t.definition })
    ];

    if (t.molecules && t.molecules.length) {
      var row = h("div", { class: "example-row" });
      t.molecules.forEach(function (id) {
        var m = molecule(id);
        if (!m) return;
        var svg = root.PYTHIA.depict(m.d2, {
          bondLength: 30,
          highlight: m.centres.map(function (c) { return c.atom; })
        });
        svg.setAttribute("aria-label", "Structure of " + m.name);
        var btn = h("button", {
          type: "button",
          class: "example-open",
          title: "Open " + m.name + " in Explore"
        }, [svg, h("span", { class: "example-name",
                             text: m.common || m.name })]);
        btn.addEventListener("click", function () {
          if (root.PYTHIA.views.explore && root.PYTHIA.views.explore.open) {
            root.PYTHIA.views.explore.open(id);
          }
        });
        row.appendChild(h("div", { class: "example-card" }, [btn]));
      });
      if (row.childNodes.length) {
        kids.push(h("figure", { class: "lesson-figure" }, [row]));
      }
    }

    if (t.see && t.see.length) {
      var refs = h("div", { class: "see-also" });
      refs.appendChild(h("span", { class: "label", text: "See also" }));
      t.see.forEach(function (name) {
        var link = h("button", {
          type: "button",
          class: "inline-link",
          text: name
        });
        link.addEventListener("click", function () {
          state.term = name;
          render();
          document.getElementById("main").focus();
        });
        refs.appendChild(link);
      });
      kids.push(refs);
    }

    /* Which entries point here. Useful in the other direction: a reader
     * who has landed on a term can see what context it belongs to. */
    var incoming = terms().filter(function (other) {
      return other.see.indexOf(t.term) >= 0;
    });
    if (incoming.length) {
      var back = h("div", { class: "see-also" });
      back.appendChild(h("span", { class: "label", text: "Referred to from" }));
      incoming.forEach(function (other) {
        var link = h("button", {
          type: "button",
          class: "inline-link",
          text: other.term
        });
        link.addEventListener("click", function () {
          state.term = other.term;
          render();
        });
        back.appendChild(link);
      });
      kids.push(back);
    }

    return h("div", null, kids);
  }

  function render() {
    var mount = document.getElementById("view");
    if (!mount) return;

    var all = terms();
    if (!all.length) {
      mount.innerHTML = "";
      mount.appendChild(h("p", {
        class: "disclaimer",
        text: "The glossary did not load. Check that data/glossary.js is "
            + "present next to index.html."
      }));
      return;
    }

    if (!state.term || !find(state.term)) state.term = all[0].term;

    mount.innerHTML = "";
    mount.appendChild(h("div", { class: "explore" }, [
      renderBrowser(function (name) {
        state.term = name;
        render();
        document.getElementById("main").focus();
      }),
      renderEntry(find(state.term))
    ]));
  }

  root.PYTHIA = root.PYTHIA || {};
  root.PYTHIA.views = root.PYTHIA.views || {};
  root.PYTHIA.views.glossary = {
    label: "Glossary",
    render: render,
    open: function (name) {
      state.term = name;
      root.location.hash = "#/glossary";
      render();
    }
  };
})(typeof window !== "undefined" ? window : this);
