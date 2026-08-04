/* PYTHIA -- the Mechanisms view.
 *
 * One reaction at a time, one step at a time. The rule governing the attack
 * comes first, before any structure, because a reader who has seen twenty
 * mechanisms and learned twenty separate stories has learned nothing. The
 * arrows are the same few ideas applied to different substrates, and saying
 * so up front is the point of the section.
 */
(function (root) {
  "use strict";

  var FAMILY_LABELS = {
    "substitution": "Substitution",
    "elimination": "Elimination",
    "addition": "Addition",
    "radical": "Radical"
  };

  var FAMILY_ORDER = ["substitution", "elimination", "addition", "radical"];

  var state = { id: null, step: null };   // step null means "show them all"

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

  function mechanisms() {
    return root.PYTHIA_MECHANISMS || [];
  }

  function find(id) {
    var all = mechanisms();
    for (var i = 0; i < all.length; i++) {
      if (all[i].id === id) return all[i];
    }
    return null;
  }

  /* ---- browser -------------------------------------------------------- */

  function renderBrowser(onPick) {
    var wrap = h("div", { class: "browser" });
    var list = h("div", { class: "group-list" });

    FAMILY_ORDER.forEach(function (family) {
      var items = mechanisms().filter(function (m) {
        return m.family === family;
      });
      if (!items.length) return;

      list.appendChild(h("p", {
        class: "label group-name",
        text: FAMILY_LABELS[family] || family
      }));

      var ul = h("ul", { class: "mol-list" });
      items.forEach(function (m) {
        var btn = h("button", {
          type: "button",
          text: m.name,
          "aria-current": m.id === state.id ? "true" : null
        });
        btn.addEventListener("click", function () { onPick(m.id); });
        ul.appendChild(h("li", null, [btn]));
      });
      list.appendChild(ul);
    });

    wrap.appendChild(list);
    return wrap;
  }

  /* ---- a single step -------------------------------------------------- */

  function renderStep(step, index, total) {
    var svg = root.PYTHIA.depict(step.d2, {
      bondLength: 38,
      arrows: step.arrows,
      lonePairs: step.lonePairs,
      annotations: step.labels
    });
    svg.setAttribute("aria-label",
      "Step " + index + " of " + total + ": " + step.title);

    return h("div", { class: "mech-step" }, [
      h("div", { class: "mech-stage" }, [svg]),
      h("div", null, [
        h("span", {
          class: "step-index",
          text: "Step " + index + " of " + total
        }),
        h("h3", { text: step.title }),
        h("p", { text: step.text })
      ])
    ]);
  }

  /* ---- legend ---------------------------------------------------------- */

  /* Drawn with the same renderer as the mechanisms themselves, so the key
   * cannot drift away from what the diagrams actually look like. */
  function arrowSample(kind) {
    var spec = {
      atoms: [{ el: "C", x: 0, y: 0, nH: 0, q: 0 },
              { el: "C", x: 1.5, y: 0, nH: 0, q: 0 }],
      bonds: []
    };
    return root.PYTHIA.depict(spec, {
      bondLength: 26,
      padding: 9,
      arrows: [{ from: { atom: 0 }, to: { atom: 1 }, bow: 0.35, kind: kind }]
    });
  }

  function dotSample(count) {
    var spec = {
      atoms: [{ el: "O", x: 0, y: 0, nH: 0, q: 0 }],
      bonds: []
    };
    var opt = { bondLength: 26, padding: 9 };
    if (count === 1) spec.atoms[0].rad = 1;
    else opt.lonePairs = { 0: 1 };
    return root.PYTHIA.depict(spec, opt);
  }

  function renderLegend() {
    return h("div", { class: "legend" }, [
      h("span", null, [arrowSample("pair"),
                       document.createTextNode("a pair of electrons")]),
      h("span", null, [arrowSample("single"),
                       document.createTextNode("one electron")]),
      h("span", null, [dotSample(2),
                       document.createTextNode("lone pair")]),
      h("span", null, [dotSample(1),
                       document.createTextNode("unpaired electron")])
    ]);
  }

  /* ---- assembly -------------------------------------------------------- */

  function renderDetail(m) {
    var kids = [
      h("div", { class: "section-head" }, [
        h("h2", { text: m.name }),
        h("p", { text: FAMILY_LABELS[m.family] || m.family })
      ]),
      h("p", { class: "note", text: m.summary }),
      h("div", { class: "attack-note" }, [
        h("p", {
          class: "label",
          text: "How the attack works",
          style: "margin-bottom:var(--gap-xs)"
        }),
        h("span", { text: m.attack })
      ]),
      renderLegend()
    ];

    m.steps.forEach(function (s, i) {
      kids.push(renderStep(s, i + 1, m.steps.length));
    });

    return h("div", null, kids);
  }

  function render() {
    var mount = document.getElementById("view");
    if (!mount) return;

    var all = mechanisms();
    if (!all.length) {
      mount.innerHTML = "";
      mount.appendChild(h("p", {
        class: "disclaimer",
        text: "The mechanism data did not load. Check that "
            + "data/mechanisms.js is present next to index.html."
      }));
      return;
    }

    if (!state.id || !find(state.id)) state.id = all[0].id;
    var m = find(state.id);

    mount.innerHTML = "";
    mount.appendChild(h("div", { class: "explore" }, [
      renderBrowser(function (id) {
        state.id = id;
        render();
        document.getElementById("main").focus();
      }),
      renderDetail(m)
    ]));
  }

  root.PYTHIA = root.PYTHIA || {};
  root.PYTHIA.views = root.PYTHIA.views || {};
  root.PYTHIA.views.mechanisms = {
    label: "Mechanisms",
    render: render
  };
})(typeof window !== "undefined" ? window : this);
