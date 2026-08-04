/* PYTHIA -- the Nomenclature view.
 *
 * Three things: the rules in the order they are applied, the seniority
 * table that settles most of the hard cases, and worked names taken apart
 * piece by piece.
 *
 * The taking apart is the point. A name like
 * (S)-2-amino-4-methylpentanoic acid is not a word to be memorised, it is
 * an assembly, and a reader who can see the seams can build one.
 */
(function (root) {
  "use strict";

  var state = { section: null, part: null };

  var KIND_LABELS = {
    "stereo": "Stereodescriptor",
    "locant": "Locant",
    "multiplier": "Multiplying prefix",
    "substituent": "Substituent prefix",
    "parent": "Parent",
    "suffix": "Suffix",
    "sep": "Separator"
  };

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

  function data() { return root.PYTHIA_NOMENCLATURE || null; }

  function molecule(id) {
    var all = root.PYTHIA_MOLECULES || [];
    for (var i = 0; i < all.length; i++) {
      if (all[i].id === id) return all[i];
    }
    return null;
  }

  /* ---- shared blocks, same vocabulary as the lessons ------------------- */

  function structure(id, size) {
    var m = molecule(id);
    if (!m) return h("p", { class: "hint", text: "Missing structure: " + id });
    var svg = root.PYTHIA.depict(m.d2, {
      bondLength: size || 30,
      highlight: m.centres.map(function (c) { return c.atom; })
    });
    svg.setAttribute("aria-label", "Structure of " + m.name);
    return svg;
  }

  function openInExplore(id) {
    if (root.PYTHIA.views.explore && root.PYTHIA.views.explore.open) {
      root.PYTHIA.views.explore.open(id);
    }
  }

  function card(id) {
    var m = molecule(id);
    if (!m) return h("p", { class: "hint", text: "Missing: " + id });
    var btn = h("button", {
      type: "button",
      class: "example-open",
      title: "Open " + m.name + " in Explore"
    }, [
      structure(id),
      h("span", { class: "example-name", text: m.name })
    ]);
    btn.addEventListener("click", function () { openInExplore(id); });
    return h("div", { class: "example-card" }, [btn]);
  }

  function renderBlock(block) {
    if (block.kind === "text") {
      return h("p", { class: "lesson-text", text: block.text });
    }
    if (block.kind === "callout") {
      return h("div", { class: "callout" }, [
        h("p", { class: "label", text: block.title }),
        h("p", { text: block.text })
      ]);
    }
    if (block.kind === "examples") {
      var row = h("div", { class: "example-row" });
      block.ids.forEach(function (id) { row.appendChild(card(id)); });
      var kids = [row];
      if (block.caption) {
        kids.push(h("p", { class: "example-caption", text: block.caption }));
      }
      return h("figure", { class: "lesson-figure" }, kids);
    }
    return null;
  }

  /* ---- a name taken apart --------------------------------------------- */

  function renderWorkedName(worked) {
    var wrap = h("div", null, []);

    wrap.appendChild(h("div", { class: "section-head" }, [
      h("h2", { text: worked.name }),
      h("p", { text: "How this name is put together" })
    ]));

    /* The name itself, with every piece a control. Separators are shown
     * but not selectable: there is nothing to say about a hyphen. */
    var strip = h("p", { class: "name-strip" });
    var buttons = [];

    worked.parts.forEach(function (part, i) {
      if (part.kind === "sep") {
        strip.appendChild(h("span", { class: "name-sep", text: part.text }));
        return;
      }
      var btn = h("button", {
        type: "button",
        class: "name-part is-" + part.kind,
        text: part.text,
        "aria-pressed": state.part === i ? "true" : "false"
      });
      btn.addEventListener("click", function () {
        state.part = (state.part === i) ? null : i;
        render();
      });
      buttons.push(btn);
      strip.appendChild(btn);
    });

    wrap.appendChild(strip);

    var legend = h("div", { class: "pair" }, [
      h("section", { class: "panel" }, [
        h("div", { class: "panel-head" }, [
          h("p", { class: "label", text: "Structure" })
        ]),
        h("div", { class: "panel-body" }, [structure(worked.molecule, 36)])
      ]),
      h("section", { class: "panel" }, [
        h("div", { class: "panel-head" }, [
          h("p", { class: "label", text: "Piece by piece" })
        ]),
        h("div", { class: "panel-body", style: "display:block" }, [
          renderPartList(worked)
        ])
      ])
    ]);
    wrap.appendChild(legend);

    wrap.appendChild(h("p", {
      class: "note",
      style: "margin-top:var(--gap-lg)",
      text: worked.commentary
    }));

    var open = h("button", {
      type: "button",
      text: "Open in Explore",
      style: "margin-top:var(--gap-md)"
    });
    open.addEventListener("click", function () {
      openInExplore(worked.molecule);
    });
    wrap.appendChild(open);

    return wrap;
  }

  function renderPartList(worked) {
    var list = h("dl", { class: "part-list" });
    worked.parts.forEach(function (part, i) {
      if (part.kind === "sep") return;
      var row = h("div", {
        class: "part-row" + (state.part === i ? " is-on" : "")
      }, [
        h("dt", null, [
          h("span", { class: "part-text", text: part.text }),
          h("span", {
            class: "part-kind",
            text: KIND_LABELS[part.kind] || part.kind
          })
        ]),
        h("dd", { text: part.why || "" })
      ]);
      list.appendChild(row);
    });
    return list;
  }

  /* ---- seniority ------------------------------------------------------- */

  function renderSeniority(table) {
    var body = h("tbody");
    table.forEach(function (g) {
      var exampleCell;
      if (g.example) {
        var m = molecule(g.example);
        var link = h("button", {
          type: "button",
          class: "inline-link",
          text: m ? m.name : g.example
        });
        link.addEventListener("click", function () {
          openInExplore(g.example);
        });
        exampleCell = h("td", null, [link]);
      } else {
        exampleCell = h("td", { text: "\u2014" });
      }

      body.appendChild(h("tr", null, [
        h("th", { scope: "row", text: String(g.rank) + ". " + g.name }),
        h("td", { text: g.suffix }),
        h("td", { text: g.prefix }),
        exampleCell
      ]));
    });

    return h("div", null, [
      h("div", { class: "section-head" }, [
        h("h2", { text: "Order of seniority" }),
        h("p", { text: "Which group gets the suffix" })
      ]),
      h("p", {
        class: "lesson-text",
        text: "When a molecule carries more than one functional group, only "
            + "the most senior takes the suffix. Every other group is "
            + "demoted to its prefix form. Reading down this table settles "
            + "most of the questions that make naming feel arbitrary."
      }),
      h("table", { class: "rows seniority" }, [
        h("thead", null, [
          h("tr", null, [
            h("th", { scope: "col", text: "Group" }),
            h("th", { scope: "col", text: "As suffix" }),
            h("th", { scope: "col", text: "As prefix" }),
            h("th", { scope: "col", text: "Example" })
          ])
        ]),
        body
      ]),
      h("p", {
        class: "example-caption",
        style: "margin-top:var(--gap-md)",
        text: "Alkenes and alkynes are not in this table. They are not "
            + "functional groups in this sense: they take an ending of "
            + "their own and never compete for the suffix."
      })
    ]);
  }

  /* ---- browser --------------------------------------------------------- */

  function renderBrowser(onPick) {
    var d = data();
    var wrap = h("div", { class: "browser" });
    var list = h("div", { class: "group-list" });

    function group(title, items) {
      list.appendChild(h("p", { class: "label group-name", text: title }));
      var ul = h("ul", { class: "mol-list" });
      items.forEach(function (item) {
        var btn = h("button", {
          type: "button",
          text: item.label,
          "aria-current": state.section === item.key ? "true" : null
        });
        btn.addEventListener("click", function () { onPick(item.key); });
        ul.appendChild(h("li", null, [btn]));
      });
      list.appendChild(ul);
    }

    group("Rules", d.rules.map(function (r) {
      return { key: "rule:" + r.id, label: r.title };
    }));
    group("Reference", [{ key: "seniority", label: "Order of seniority" }]);
    group("Worked names", d.names.map(function (n) {
      return { key: "name:" + n.molecule, label: n.name };
    }));

    wrap.appendChild(list);
    return wrap;
  }

  /* ---- assembly -------------------------------------------------------- */

  function renderSection(d) {
    if (state.section === "seniority") {
      return renderSeniority(d.seniority);
    }

    if (state.section.indexOf("name:") === 0) {
      var id = state.section.slice(5);
      for (var i = 0; i < d.names.length; i++) {
        if (d.names[i].molecule === id) return renderWorkedName(d.names[i]);
      }
    }

    var rid = state.section.slice(5);
    for (var j = 0; j < d.rules.length; j++) {
      if (d.rules[j].id !== rid) continue;
      var rule = d.rules[j];
      var kids = [h("div", { class: "section-head" }, [
        h("h2", { text: rule.title }),
        h("p", { text: "Rule " + (j + 1) + " of " + d.rules.length })
      ])];
      rule.blocks.forEach(function (b) {
        var node = renderBlock(b);
        if (node) kids.push(node);
      });
      return h("div", null, kids);
    }
    return h("p", { class: "hint", text: "Nothing selected." });
  }

  function render() {
    var mount = document.getElementById("view");
    if (!mount) return;

    var d = data();
    if (!d) {
      mount.innerHTML = "";
      mount.appendChild(h("p", {
        class: "disclaimer",
        text: "The nomenclature data did not load. Check that "
            + "data/nomenclature.js is present next to index.html."
      }));
      return;
    }

    if (!state.section) state.section = "rule:" + d.rules[0].id;

    mount.innerHTML = "";
    mount.appendChild(h("div", { class: "explore" }, [
      renderBrowser(function (key) {
        state.section = key;
        state.part = null;
        render();
        document.getElementById("main").focus();
      }),
      renderSection(d)
    ]));
  }

  root.PYTHIA = root.PYTHIA || {};
  root.PYTHIA.views = root.PYTHIA.views || {};
  root.PYTHIA.views.nomenclature = {
    label: "Naming",
    render: render
  };
})(typeof window !== "undefined" ? window : this);
