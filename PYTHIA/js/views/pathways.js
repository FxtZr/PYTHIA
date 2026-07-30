/* PYTHIA -- the Pathways view.
 *
 * A pathway reads down the page as a chain. Each step names its enzyme,
 * what it needs, and whether it can run backwards, because those three
 * facts are what distinguishes a step you can reverse from a step the cell
 * has to build a whole separate route around.
 *
 * Committed and regulated steps are marked. A reader who remembers only
 * those has remembered the part that matters: the rest of a pathway is
 * plumbing, and the control points are where physiology actually happens.
 */
(function (root) {
  "use strict";

  var state = { id: null };

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

  function pathways() { return root.PYTHIA_PATHWAYS || []; }

  function find(id) {
    var all = pathways();
    for (var i = 0; i < all.length; i++) {
      if (all[i].id === id) return all[i];
    }
    return null;
  }

  function molecule(id) {
    var all = root.PYTHIA_MOLECULES || [];
    for (var i = 0; i < all.length; i++) {
      if (all[i].id === id) return all[i];
    }
    return null;
  }

  /* ---- one step -------------------------------------------------------- */

  function renderStep(step, index) {
    var head = h("div", { class: "path-head" }, [
      h("span", { class: "path-number", text: String(index) }),
      h("span", { class: "path-substrate", text: step.substrate }),
      h("span", {
        class: "path-arrow",
        title: step.reversible ? "Reversible" : "Effectively irreversible",
        text: step.reversible ? "\u21cc" : "\u2192"
      }),
      h("span", { class: "path-product", text: step.product })
    ]);

    var meta = h("div", { class: "path-meta" }, [
      h("span", { class: "path-enzyme", text: step.enzyme }),
      h("span", { class: "path-ec", text: "EC " + step.ec })
    ]);

    var kids = [head, meta];

    if (step.cofactors && step.cofactors.length) {
      var cof = h("div", { class: "path-cofactors" });
      cof.appendChild(h("span", { class: "label", text: "Needs" }));
      step.cofactors.forEach(function (c) {
        cof.appendChild(h("span", { class: "tag", text: c }));
      });
      kids.push(cof);
    }

    if (step.key) {
      kids.push(h("p", {
        class: "path-key",
        text: "Committed or regulated step"
      }));
    }

    if (step.note) kids.push(h("p", { class: "path-note", text: step.note }));

    /* Where the library happens to hold the substrate, draw it. Most
     * intermediates are phosphorylated sugars that are not in there, and
     * an empty box would be worse than none. */
    var body = h("div", { class: "path-body" }, kids);
    var m = step.molecule ? molecule(step.molecule) : null;
    if (m) {
      var svg = root.PYTHIA.depict(m.d2, { bondLength: 26 });
      svg.setAttribute("aria-label", "Structure of " + m.name);
      var btn = h("button", {
        type: "button",
        class: "example-open path-structure",
        title: "Open " + m.name + " in Explore"
      }, [svg, h("span", { class: "example-name", text: m.common || m.name })]);
      btn.addEventListener("click", function () {
        if (root.PYTHIA.views.explore && root.PYTHIA.views.explore.open) {
          root.PYTHIA.views.explore.open(m.id);
        }
      });
      return h("li", { class: "path-step has-structure" }, [body, btn]);
    }

    return h("li", { class: "path-step" }, [body]);
  }

  /* ---- assembly -------------------------------------------------------- */

  function renderPathway(p) {
    var steps = h("ol", { class: "path-steps" });
    p.steps.forEach(function (s, i) {
      steps.appendChild(renderStep(s, i + 1));
    });

    var reversible = p.steps.filter(function (s) { return s.reversible; });

    return h("div", null, [
      h("div", { class: "section-head" }, [
        h("h2", { text: p.name }),
        h("p", { text: p.location })
      ]),
      h("p", { class: "lesson-blurb", text: p.summary }),
      h("div", { class: "callout" }, [
        h("p", { class: "label", text: "What it is for" }),
        h("p", { text: p.purpose })
      ]),
      h("div", { class: "legend" }, [
        h("span", { text: "\u2192  effectively irreversible" }),
        h("span", { text: "\u21cc  reversible" }),
        h("span", {
          text: p.steps.length + " steps, " + reversible.length
              + " of them reversible"
        })
      ]),
      steps,
      h("div", { class: "attack-note" }, [
        h("p", {
          class: "label",
          text: "How it is controlled",
          style: "margin-bottom:var(--gap-xs)"
        }),
        h("span", { text: p.regulation })
      ]),
      h("p", {
        class: "example-caption",
        text: "Enzyme numbers follow the IUBMB classification. They are "
            + "given so that a reader can look an enzyme up, not as a "
            + "substitute for doing so."
      })
    ]);
  }

  function renderBrowser(onPick) {
    var wrap = h("div", { class: "browser" });
    var list = h("div", { class: "group-list" });
    list.appendChild(h("p", { class: "label group-name", text: "Pathways" }));

    var ul = h("ul", { class: "mol-list" });
    pathways().forEach(function (p) {
      var btn = h("button", {
        type: "button",
        text: p.name,
        "aria-current": p.id === state.id ? "true" : null
      });
      btn.addEventListener("click", function () { onPick(p.id); });
      ul.appendChild(h("li", null, [btn]));
    });
    list.appendChild(ul);
    wrap.appendChild(list);
    return wrap;
  }

  function render() {
    var mount = document.getElementById("view");
    if (!mount) return;

    var all = pathways();
    if (!all.length) {
      mount.innerHTML = "";
      mount.appendChild(h("p", {
        class: "disclaimer",
        text: "The pathway data did not load. Check that data/pathways.js "
            + "is present next to index.html."
      }));
      return;
    }

    if (!state.id || !find(state.id)) state.id = all[0].id;

    mount.innerHTML = "";
    mount.appendChild(h("div", { class: "explore" }, [
      renderBrowser(function (id) {
        state.id = id;
        render();
        document.getElementById("main").focus();
      }),
      renderPathway(find(state.id))
    ]));
  }

  root.PYTHIA = root.PYTHIA || {};
  root.PYTHIA.views = root.PYTHIA.views || {};
  root.PYTHIA.views.pathways = {
    label: "Pathways",
    render: render
  };
})(typeof window !== "undefined" ? window : this);
