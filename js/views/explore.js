/* PYTHIA -- the Explore view.
 *
 * A molecule shown twice: flat on the left, in space on the right. Pointing
 * at an atom in either place lights it up in the other. That link is the
 * whole reason this view exists, because the thing a reader has to build is
 * the habit of reading a wedge as depth.
 */
(function (root) {
  "use strict";

  var GROUP_LABELS = {
    "chirality": "Chirality",
    "diastereomers": "More than one centre",
    "alkene-geometry": "Double bond geometry",
    "conformation": "Conformation",
    "nomenclature": "Naming",
    "amino-acids": "Amino acids",
    "nucleobases": "Nucleobases",
    "sugars": "Sugars",
    "lipids": "Fatty acids",
    "cofactors": "Cofactors",
    "vitamins": "Vitamins"
  };

  var GROUP_ORDER = [
    "chirality", "diastereomers", "alkene-geometry", "conformation",
    "nomenclature", "amino-acids", "nucleobases", "sugars", "lipids",
    "cofactors", "vitamins"
  ];

  var TAG_LABELS = {
    "indispensable": "indispensable",
    "conditionally-indispensable": "conditionally indispensable",
    "dispensable": "dispensable",
    "essential-fatty-acid": "essential fatty acid"
  };

  var RANK_LETTERS = ["a", "b", "c", "d"];

  var state = { id: null, filter: "", elementColour: false, centre: 0 };
  var viewer = null;
  var drawing = null;

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
    (children || []).forEach(function (c) {
      if (c) node.appendChild(c);
    });
    return node;
  }

  function molecules() {
    return root.PYTHIA_MOLECULES || [];
  }

  function find(id) {
    var all = molecules();
    for (var i = 0; i < all.length; i++) {
      if (all[i].id === id) return all[i];
    }
    return null;
  }

  function matches(m, q) {
    if (!q) return true;
    q = q.toLowerCase();
    return (m.name + " " + (m.common || "") + " " + m.formula + " " + m.group)
      .toLowerCase().indexOf(q) >= 0;
  }

  /* ---- the browser ---------------------------------------------------- */

  function renderBrowser(onPick) {
    var box = h("div", { class: "browser" });

    var search = h("input", {
      type: "search",
      class: "search",
      placeholder: "Filter by name or formula",
      "aria-label": "Filter the library",
      value: state.filter
    });
    search.addEventListener("input", function () {
      state.filter = search.value;
      var list = box.querySelector(".group-list");
      var fresh = renderGroups(onPick);
      list.replaceWith(fresh);
    });
    box.appendChild(search);
    box.appendChild(renderGroups(onPick));
    return box;
  }

  function renderGroups(onPick) {
    var wrap = h("div", { class: "group-list" });
    var shown = 0;

    GROUP_ORDER.forEach(function (group) {
      var items = molecules().filter(function (m) {
        return m.group === group && matches(m, state.filter);
      });
      if (!items.length) return;
      shown += items.length;

      wrap.appendChild(h("p", {
        class: "label group-name",
        text: GROUP_LABELS[group] || group
      }));

      var ul = h("ul", { class: "mol-list" });
      items.forEach(function (m) {
        var btn = h("button", {
          type: "button",
          text: m.common || m.name,
          title: m.name,
          "aria-current": m.id === state.id ? "true" : null
        });
        btn.addEventListener("click", function () { onPick(m.id); });
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

  /* ---- linked structure pair ------------------------------------------ */

  function highlightAtom(index) {
    if (viewer) viewer.mark(index);
    if (!drawing) return;
    var nodes = drawing.querySelectorAll(".depict-atom");
    for (var i = 0; i < nodes.length; i++) {
      var isIt = String(index) === nodes[i].getAttribute("data-atom");
      nodes[i].classList.toggle("is-active", isIt);
    }
  }

  /* The priority letters belong on the structure, not only in a list beside
   * it. They are shown for one stereocentre at a time: priority is defined
   * per centre, so putting every centre's letters up at once would be four
   * overlapping answers to four different questions. */
  function ranksFor(m) {
    var centre = m.centres[state.centre];
    if (!centre || !centre.ranking) return null;
    var out = {};
    centre.ranking.forEach(function (idx, i) {
      if (idx !== null && idx !== undefined) out[idx] = RANK_LETTERS[i];
    });
    return out;
  }

  function renderPair(m) {
    var centres = m.centres.map(function (c) { return c.atom; });
    var selected = m.centres[state.centre];

    drawing = root.PYTHIA.depict(m.d2, {
      highlight: selected ? [selected.atom] : centres,
      ranks: ranksFor(m),
      bondLength: 40,
      elementColour: state.elementColour,
      interactive: true,
      onAtomEnter: highlightAtom,
      onAtomLeave: function () { highlightAtom(null); },
      onAtomClick: highlightAtom
    });
    drawing.setAttribute("aria-label",
      "Skeletal formula of " + m.name + ", " + m.formula);

    var flatBody = h("div", { class: "panel-body" }, [drawing]);
    var flat = h("section", { class: "panel" }, [
      h("div", { class: "panel-head" }, [
        h("p", { class: "label", text: "Flat" }),
        h("p", { class: "label", text: m.formula })
      ]),
      flatBody,
      h("p", {
        class: "hint",
        text: "A bold wedge comes towards you, a hashed one goes away. "
            + "Point at any atom."
      })
    ]);

    var host = h("div", { class: "viewer3d" });
    var spinBtn = h("button", { type: "button", text: "Spin",
                                "aria-pressed": "false" });

    var space = h("section", { class: "panel" }, [
      h("div", { class: "panel-head" }, [
        h("p", { class: "label", text: "In space" }),
        spinBtn
      ]),
      h("div", { class: "panel-body" }, [host]),
      h("p", {
        class: "hint",
        text: "Drag to rotate, scroll to zoom. Geometry is computed, not "
            + "measured."
      })
    ]);

    // 3Dmol needs the element in the document before it can size itself
    setTimeout(function () {
      viewer = new root.PYTHIA.Viewer3D(host);
      viewer.load(m.sdf);
      spinBtn.addEventListener("click", function () {
        var now = spinBtn.getAttribute("aria-pressed") !== "true";
        var applied = viewer.spin(now);
        spinBtn.setAttribute("aria-pressed", applied ? "true" : "false");
      });
    }, 0);

    return h("div", { class: "pair" }, [flat, space]);
  }

  /* ---- properties ----------------------------------------------------- */

  function row(label, value) {
    return h("tr", null, [
      h("th", { scope: "row", text: label }),
      h("td", { text: value })
    ]);
  }

  function renderProperties(m) {
    var body = h("tbody", null, [
      row("Preferred name", m.name),
      m.common ? row("Also called", m.common) : null,
      row("Formula", m.formula),
      row("Molar mass", m.mw.toFixed(3) + " g/mol"),
      row("Monoisotopic mass", m.exact.toFixed(5)),
      row("Heavy atoms", String(m.heavy)),
      row("Rings", String(m.rings)),
      row("Stereocentres", String(m.centres.length)),
      row("SMILES", m.smiles)
    ]);

    var block = [h("table", { class: "rows" }, [body])];

    if (m.tags && m.tags.length) {
      var tags = h("div", { class: "tags" });
      m.tags.forEach(function (t) {
        tags.appendChild(h("span", {
          class: "tag", text: TAG_LABELS[t] || t
        }));
      });
      block.push(tags);
    }
    return h("div", null, block);
  }

  /* ---- CIP walkthrough ------------------------------------------------ */

  function describeAtom(m, index) {
    if (index === null || index === undefined) return "an implicit hydrogen";
    var a = m.d2.atoms[index];
    var s = a.el;
    if (a.nH === 1) s += "H";
    else if (a.nH > 1) s += "H" + a.nH;
    return s + " (atom " + index + ")";
  }

  function renderCentre(m, centre, ordinal) {
    var kids = [];

    var isOn = m.centres[state.centre] === centre;
    var head = h("button", {
      type: "button",
      class: "centre-head" + (isOn ? " is-on" : ""),
      "aria-pressed": isOn ? "true" : "false",
      title: "Show this centre's priorities on the structure"
    }, [
      h("span", { class: "label", text: "Stereocentre " + ordinal
                                        + " \u00b7 atom " + centre.atom }),
      h("span", { class: "descriptor", text: centre.label })
    ]);
    head.addEventListener("click", function () {
      state.centre = ordinal - 1;
      render();
    });
    kids.push(head);

    if (!centre.steps) {
      kids.push(h("p", {
        class: "no-walkthrough",
        text: "The configuration above is computed and reliable, but the "
            + "priority order at this centre is not settled by atomic "
            + "number alone. Resolving it needs the later CIP rules, which "
            + "this program does not walk through, so no step-by-step is "
            + "offered here rather than an explanation that might be wrong."
      }));
      return h("div", { class: "centre-block" }, kids);
    }

    var ranked = h("div", { class: "ranked" });
    centre.ranking.forEach(function (idx, i) {
      var span = h("span", null, [
        h("b", { text: RANK_LETTERS[i] })
      ]);
      span.appendChild(document.createTextNode(" " + describeAtom(m, idx)));
      ranked.appendChild(span);
    });
    kids.push(ranked);

    if (centre.ranking[3] === null || centre.ranking[3] === undefined) {
      kids.push(h("p", {
        class: "example-caption",
        text: "The lowest priority here is a hydrogen that the skeletal "
            + "drawing leaves implicit, so only a, b and c are marked on the "
            + "structure. It is the one pointing away from you."
      }));
    }

    var steps = h("ol", { class: "steps" });
    centre.steps.forEach(function (s) {
      steps.appendChild(h("li", { text: s.why }));
    });
    steps.appendChild(h("li", {
      text: "With " + RANK_LETTERS[3] + " pointing away from you, "
          + RANK_LETTERS[0] + " to " + RANK_LETTERS[1] + " to "
          + RANK_LETTERS[2] + " turns "
          + (centre.label === "R" ? "clockwise, which is R."
                                  : "anticlockwise, which is S.")
    }));
    kids.push(steps);

    return h("div", { class: "centre-block" }, kids);
  }

  function renderStereo(m) {
    var kids = [];

    if (m.centres.length) {
      m.centres.forEach(function (c, i) {
        kids.push(renderCentre(m, c, i + 1));
      });
    }

    if (m.doubleBonds && m.doubleBonds.length) {
      m.doubleBonds.forEach(function (b) {
        kids.push(h("div", { class: "centre-block" }, [
          h("div", { class: "centre-head" }, [
            h("p", {
              class: "label",
              text: "Double bond \u00b7 atoms " + b.a + " and " + b.b
            }),
            h("span", { class: "descriptor", text: b.label })
          ]),
          h("p", {
            class: "note",
            text: b.label === "Z"
              ? "The higher priority group on each carbon sits on the same "
                + "side. Z, from zusammen."
              : "The higher priority group on each carbon sits on opposite "
                + "sides. E, from entgegen."
          })
        ]));
      });
    }

    if (!kids.length) {
      kids.push(h("p", {
        class: "note",
        text: "No stereocentre and no fixed double bond geometry. Worth "
            + "checking why: look for a carbon with two identical "
            + "substituents, or a mirror plane through the molecule."
      }));
    }
    return h("div", null, kids);
  }

  /* ---- assembly ------------------------------------------------------- */

  function renderDetail(m) {
    var toggle = h("button", {
      type: "button",
      text: "Colour heteroatoms",
      "aria-pressed": state.elementColour ? "true" : "false"
    });
    toggle.addEventListener("click", function () {
      state.elementColour = !state.elementColour;
      render();
    });

    return h("div", null, [
      h("div", { class: "section-head" }, [
        h("h2", { text: m.common || m.name }),
        h("p", { text: m.common ? m.name : m.formula })
      ]),
      h("p", { class: "note", text: m.note }),
      h("div", { style: "margin:var(--gap-md) 0" }, [toggle]),
      renderPair(m),
      h("div", { class: "grid-2" }, [
        h("div", null, [
          h("p", { class: "label", text: "Identity" }),
          renderProperties(m)
        ]),
        h("div", null, [
          h("p", { class: "label", text: "Configuration" }),
          renderStereo(m)
        ])
      ])
    ]);
  }

  function render() {
    var mount = document.getElementById("view");
    if (!mount) return;

    var all = molecules();
    if (!all.length) {
      mount.innerHTML = "";
      mount.appendChild(h("p", {
        class: "disclaimer",
        text: "The molecule library did not load. Check that "
            + "data/molecules.js is present next to index.html."
      }));
      return;
    }

    if (!state.id || !find(state.id)) state.id = all[0].id;
    var m = find(state.id);

    viewer = null;
    mount.innerHTML = "";
    mount.appendChild(h("div", { class: "explore" }, [
      renderBrowser(function (id) {
        state.id = id;
        state.centre = 0;
        render();
        document.getElementById("main").focus();
      }),
      renderDetail(m)
    ]));
  }

  root.PYTHIA = root.PYTHIA || {};
  root.PYTHIA.views = root.PYTHIA.views || {};
  root.PYTHIA.views.explore = {
    label: "Explore",
    render: render,

    /* Called from the lessons, so a structure mentioned in prose can be
     * opened where it can be turned in space. Setting the hash normally
     * triggers a route and a render; when Explore is already the current
     * view no hashchange fires, so render is called directly. It is
     * idempotent. */
    open: function (id) {
      state.id = id;
      state.centre = 0;
      root.location.hash = "#/explore";
      render();
      var main = document.getElementById("main");
      if (main) main.focus();
    }
  };
})(typeof window !== "undefined" ? window : this);
