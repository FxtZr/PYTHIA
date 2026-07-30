/* PYTHIA -- the Spectroscopy view.
 *
 * Correlation tables, and the reasoning that turns three of them into one
 * structure. No spectra are shown, because a real spectrum is noisy and
 * unannotated and teaches less than a table with every band explained.
 *
 * The scales are drawn rather than tabulated. Where a signal appears is a
 * spatial fact, and a student who has seen the aromatic region sitting
 * between the vinyl and the aldehyde will recall it long after forgetting
 * that it runs 6.5 to 8.5.
 */
(function (root) {
  "use strict";

  var state = { section: "ir", revealed: {} };

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

  var NS = "http://www.w3.org/2000/svg";
  function s(tag, attrs) {
    var node = document.createElementNS(NS, tag);
    for (var k in (attrs || {})) {
      if (attrs[k] !== null && attrs[k] !== undefined) {
        node.setAttribute(k, attrs[k]);
      }
    }
    return node;
  }

  function data() { return root.PYTHIA_SPECTROSCOPY || null; }

  function molecule(id) {
    var all = root.PYTHIA_MOLECULES || [];
    for (var i = 0; i < all.length; i++) {
      if (all[i].id === id) return all[i];
    }
    return null;
  }

  /* ---- a scale of ranges ----------------------------------------------- */

  /* Rows of bars on a shared axis. Ranges that would collide are pushed to
   * the next row rather than overlapped, so nothing is hidden behind
   * anything else. */
  function scale(ranges, opts) {
    var W = 640, pad = 40, rowH = 17, axisH = 26;
    var lo = opts.min, hi = opts.max;
    var reversed = !!opts.reversed;

    function x(v) {
      var t = (v - lo) / (hi - lo);
      if (reversed) t = 1 - t;
      return pad + t * (W - pad * 2);
    }

    var rows = [];
    ranges.forEach(function (r) {
      var a = Math.min(x(r.low), x(r.high));
      var b = Math.max(x(r.low), x(r.high));
      var placed = false;
      for (var i = 0; i < rows.length && !placed; i++) {
        var clash = rows[i].some(function (o) {
          return !(b + 58 < o.a || a > o.b + 58);
        });
        if (!clash) { rows[i].push({ a: a, b: b, r: r }); placed = true; }
      }
      if (!placed) rows.push([{ a: a, b: b, r: r }]);
    });

    var H = axisH + rows.length * rowH + 10;
    var svg = s("svg", {
      viewBox: "0 0 " + W + " " + H, width: W, height: H,
      class: "scale", role: "img",
      "aria-label": opts.label
    });

    var ticks = opts.ticks || [];
    ticks.forEach(function (t) {
      svg.appendChild(s("line", {
        x1: x(t).toFixed(1), y1: 0, x2: x(t).toFixed(1), y2: H - axisH + 4,
        class: "scale-grid"
      }));
      var lbl = s("text", {
        x: x(t).toFixed(1), y: H - 8, "text-anchor": "middle",
        class: "scale-tick"
      });
      lbl.textContent = String(t);
      svg.appendChild(lbl);
    });

    svg.appendChild(s("line", {
      x1: pad, y1: H - axisH + 4, x2: W - pad, y2: H - axisH + 4,
      class: "scale-axis"
    }));

    rows.forEach(function (row, i) {
      var y = 8 + i * rowH;
      row.forEach(function (item) {
        svg.appendChild(s("rect", {
          x: item.a.toFixed(1), y: y, rx: 1,
          width: Math.max(2, item.b - item.a).toFixed(1), height: 8,
          class: "scale-band"
        }));
        var label = s("text", {
          x: (item.b + 6).toFixed(1), y: (y + 7).toFixed(1),
          class: "scale-label"
        });
        label.textContent = item.r.label;
        svg.appendChild(label);
      });
    });

    return svg;
  }

  /* ---- infrared -------------------------------------------------------- */

  function renderIR(d) {
    var ranges = d.ir.map(function (b) {
      return { low: b.low, high: b.high, label: b.bond };
    });

    var body = h("tbody");
    d.ir.forEach(function (b) {
      body.appendChild(h("tr", null, [
        h("th", { scope: "row", text: b.bond }),
        h("td", { text: b.group }),
        h("td", { text: b.low + "\u2013" + b.high }),
        h("td", { text: b.intensity + ", " + b.shape }),
        h("td", { class: "spec-note", text: b.note || "" })
      ]));
    });

    return h("div", null, [
      h("div", { class: "section-head" }, [
        h("h2", { text: "Infrared" }),
        h("p", { text: "Where each bond absorbs, and what the band looks "
                       + "like" })
      ]),
      h("p", {
        class: "lesson-text",
        text: "Read from the left. The single most useful landmark is 3000: "
            + "a C-H band above it belongs to an sp2 or sp carbon, below it "
            + "to an sp3 carbon. After that, look for a carbonyl near 1700 "
            + "and decide what kind it is."
      }),
      h("figure", { class: "scale-figure" }, [
        scale(ranges, {
          min: 400, max: 4000, reversed: true,
          ticks: [4000, 3000, 2000, 1500, 1000, 400],
          label: "Infrared absorption ranges in wavenumbers"
        }),
        h("figcaption", {
          class: "example-caption",
          text: "Wavenumber in cm\u207b\u00b9, running high to low as a "
              + "spectrum is printed."
        })
      ]),
      h("table", { class: "rows spec-table" }, [
        h("thead", null, [h("tr", null, [
          h("th", { scope: "col", text: "Bond" }),
          h("th", { scope: "col", text: "In" }),
          h("th", { scope: "col", text: "cm\u207b\u00b9" }),
          h("th", { scope: "col", text: "Appearance" }),
          h("th", { scope: "col", text: "" })
        ])]),
        body
      ]),
      h("div", { class: "callout" }, [
        h("p", { class: "label", text: "The fingerprint region" }),
        h("p", { text: d.fingerprint })
      ])
    ]);
  }

  /* ---- NMR ------------------------------------------------------------- */

  function renderNMR(d, which) {
    var regions = which === "proton" ? d.proton : d.carbon;
    var isProton = which === "proton";

    var ranges = regions.map(function (r) {
      return { low: r.low, high: r.high, label: r.environment };
    });

    var body = h("tbody");
    regions.forEach(function (r) {
      body.appendChild(h("tr", null, [
        h("th", { scope: "row", text: r.environment }),
        h("td", { text: r.low + "\u2013" + r.high }),
        h("td", { class: "spec-note", text: r.note || "" })
      ]));
    });

    var kids = [
      h("div", { class: "section-head" }, [
        h("h2", { text: isProton ? "Proton NMR" : "Carbon-13 NMR" }),
        h("p", { text: "Chemical shift in ppm" })
      ]),
      h("p", {
        class: "lesson-text",
        text: isProton
          ? "Every region below is the alkyl baseline moved downfield by "
            + "something pulling electron density away from the proton. "
            + "Learn the baseline and the reason, and the table stops "
            + "needing to be memorised."
          : "The range is twenty times wider than for protons, so signals "
            + "rarely overlap. A carbon spectrum answers how many distinct "
            + "carbons there are before it answers anything else."
      }),
      h("figure", { class: "scale-figure" }, [
        scale(ranges, {
          min: isProton ? 0 : 0, max: isProton ? 14 : 230, reversed: true,
          ticks: isProton ? [14, 12, 10, 8, 6, 4, 2, 0]
                          : [220, 180, 140, 100, 60, 20, 0],
          label: (isProton ? "Proton" : "Carbon-13")
               + " chemical shift regions in ppm"
        }),
        h("figcaption", {
          class: "example-caption",
          text: "Shift in ppm, downfield to the left as a spectrum is "
              + "printed."
        })
      ]),
      h("table", { class: "rows spec-table" }, [
        h("thead", null, [h("tr", null, [
          h("th", { scope: "col", text: "Environment" }),
          h("th", { scope: "col", text: "ppm" }),
          h("th", { scope: "col", text: "" })
        ])]),
        body
      ])
    ];

    if (isProton) {
      kids.push(h("div", { class: "callout" }, [
        h("p", { class: "label", text: "Splitting" }),
        h("p", { text: d.multiplicity })
      ]));
    }
    return h("div", null, kids);
  }

  /* ---- mass spectrometry ----------------------------------------------- */

  function renderMS(d) {
    function lossTable(rows, firstHeader) {
      var body = h("tbody");
      rows.forEach(function (l) {
        body.appendChild(h("tr", null, [
          h("th", { scope: "row", text: String(l.mass) }),
          h("td", { text: l.fragment }),
          h("td", { text: l.origin }),
          h("td", { class: "spec-note", text: l.note || "" })
        ]));
      });
      return h("table", { class: "rows spec-table" }, [
        h("thead", null, [h("tr", null, [
          h("th", { scope: "col", text: firstHeader }),
          h("th", { scope: "col", text: "Fragment" }),
          h("th", { scope: "col", text: "From" }),
          h("th", { scope: "col", text: "" })
        ])]),
        body
      ]);
    }

    var rules = h("div", null, []);
    d.fragmentations.forEach(function (r) {
      rules.appendChild(h("div", { class: "frag-rule" }, [
        h("h3", { text: r.name }),
        h("table", { class: "rows" }, [h("tbody", null, [
          h("tr", null, [h("th", { scope: "row", text: "Needs" }),
                         h("td", { text: r.requires })]),
          h("tr", null, [h("th", { scope: "row", text: "Gives" }),
                         h("td", { text: r.gives })])
        ])]),
        h("p", { class: "spec-note", text: r.note })
      ]));
    });

    return h("div", null, [
      h("div", { class: "section-head" }, [
        h("h2", { text: "Mass spectrometry" }),
        h("p", { text: "What comes off, and what is left holding the "
                       + "charge" })
      ]),
      h("div", { class: "callout" }, [
        h("p", { class: "label", text: "The nitrogen rule" }),
        h("p", { text: d.nitrogenRule })
      ]),
      h("p", { class: "label", text: "Common neutral losses",
               style: "margin-top:var(--gap-lg)" }),
      lossTable(d.losses, "Loss"),
      h("p", { class: "label", text: "Ions worth recognising",
               style: "margin-top:var(--gap-lg)" }),
      lossTable(d.ions, "m/z"),
      h("p", { class: "label", text: "How molecules break",
               style: "margin-top:var(--gap-lg)" }),
      rules,
      h("p", {
        class: "example-caption",
        text: "The isotope pattern of a formula can be computed under "
            + "Calculators. Chlorine and bromine are recognisable there at "
            + "a glance."
      })
    ]);
  }

  /* ---- elucidation problems -------------------------------------------- */

  function renderProblem(p) {
    function listBlock(title, items) {
      var ul = h("ul", { class: "spec-data" });
      items.forEach(function (line) {
        ul.appendChild(h("li", { text: line }));
      });
      return h("div", null, [h("p", { class: "label", text: title }), ul]);
    }

    var kids = [
      h("div", { class: "section-head" }, [
        h("h2", { text: p.formula }),
        h("p", { text: "Deduce the structure" })
      ]),
      h("table", { class: "rows" }, [h("tbody", null, [
        h("tr", null, [h("th", { scope: "row", text: "Molecular formula" }),
                       h("td", { text: p.formula })]),
        h("tr", null, [h("th", { scope: "row",
                                 text: "Degrees of unsaturation" }),
                       h("td", { text: String(p.unsaturation) })]),
        h("tr", null, [h("th", { scope: "row", text: "Proton signals" }),
                       h("td", { text: String(p.signals) })])
      ])]),
      h("div", { class: "grid-2", style: "margin-top:var(--gap-lg)" }, [
        listBlock("Infrared", p.ir),
        listBlock("Proton NMR", p.nmr),
        listBlock("Mass spectrum", p.ms)
      ])
    ];

    if (state.revealed[p.id]) {
      var m = molecule(p.answer);
      var panel = [
        h("p", { class: "label", text: "Answer" }),
        h("p", { class: "calc-answer", text: p.answerName })
      ];
      if (m) {
        var svg = root.PYTHIA.depict(m.d2, {
          bondLength: 36,
          highlight: m.centres.map(function (c) { return c.atom; })
        });
        svg.setAttribute("aria-label", "Structure of " + m.name);
        var open = h("button", {
          type: "button", class: "example-open",
          title: "Open " + m.name + " in Explore"
        }, [svg, h("span", { class: "example-name", text: m.name })]);
        open.addEventListener("click", function () {
          if (root.PYTHIA.views.explore && root.PYTHIA.views.explore.open) {
            root.PYTHIA.views.explore.open(m.id);
          }
        });
        panel.push(h("div", { class: "example-row" },
                     [h("div", { class: "example-card" }, [open])]));
      }
      panel.push(h("p", { class: "lesson-text", text: p.reasoning }));
      kids.push(h("div", { class: "reveal" }, panel));
    } else {
      var btn = h("button", { type: "button", text: "Show the reasoning",
                              style: "margin-top:var(--gap-lg)" });
      btn.addEventListener("click", function () {
        state.revealed[p.id] = true;
        render();
      });
      kids.push(btn);
    }

    return h("div", null, kids);
  }

  /* ---- browser and assembly -------------------------------------------- */

  function sections(d) {
    var out = [
      { key: "ir", label: "Infrared", group: "Reference" },
      { key: "proton", label: "Proton NMR", group: "Reference" },
      { key: "carbon", label: "Carbon-13 NMR", group: "Reference" },
      { key: "ms", label: "Mass spectrometry", group: "Reference" }
    ];
    d.problems.forEach(function (p) {
      out.push({ key: "p:" + p.id, label: p.formula, group: "Problems" });
    });
    return out;
  }

  function renderBrowser(d, onPick) {
    var wrap = h("div", { class: "browser" });
    var list = h("div", { class: "group-list" });
    var seen = null;
    var ul = null;

    sections(d).forEach(function (item) {
      if (item.group !== seen) {
        seen = item.group;
        list.appendChild(h("p", { class: "label group-name",
                                  text: item.group }));
        ul = h("ul", { class: "mol-list" });
        list.appendChild(ul);
      }
      var btn = h("button", {
        type: "button", text: item.label,
        "aria-current": state.section === item.key ? "true" : null
      });
      btn.addEventListener("click", function () { onPick(item.key); });
      ul.appendChild(h("li", null, [btn]));
    });

    wrap.appendChild(list);
    return wrap;
  }

  function renderSection(d) {
    if (state.section === "ir") return renderIR(d);
    if (state.section === "proton") return renderNMR(d, "proton");
    if (state.section === "carbon") return renderNMR(d, "carbon");
    if (state.section === "ms") return renderMS(d);
    var id = state.section.slice(2);
    for (var i = 0; i < d.problems.length; i++) {
      if (d.problems[i].id === id) return renderProblem(d.problems[i]);
    }
    return renderIR(d);
  }

  function render() {
    var mount = document.getElementById("view");
    if (!mount) return;

    var d = data();
    if (!d) {
      mount.innerHTML = "";
      mount.appendChild(h("p", {
        class: "disclaimer",
        text: "The spectroscopy data did not load. Check that "
            + "data/spectroscopy.js is present next to index.html."
      }));
      return;
    }

    mount.innerHTML = "";
    mount.appendChild(h("div", { class: "explore" }, [
      renderBrowser(d, function (key) {
        state.section = key;
        render();
        document.getElementById("main").focus();
      }),
      renderSection(d)
    ]));
  }

  root.PYTHIA = root.PYTHIA || {};
  root.PYTHIA.views = root.PYTHIA.views || {};
  root.PYTHIA.views.spectroscopy = {
    label: "Spectroscopy",
    render: render
  };
})(typeof window !== "undefined" ? window : this);
