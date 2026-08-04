/* PYTHIA -- the Calculators view.
 *
 * Nine tools. Each states the relation it uses, because a number with no
 * visible provenance is a number the reader cannot check, and a teaching
 * tool that asks to be trusted has failed at the only thing it was for.
 *
 * Bad input produces a stated reason, never a quiet wrong answer.
 */
(function (root) {
  "use strict";

  var MESSAGES = {
    "EMPTY_FORMULA": "Enter a formula.",
    "BAD_CHARACTER": "That character cannot appear in a formula.",
    "UNKNOWN_ELEMENT": "No element with that symbol.",
    "UNBALANCED_BRACKET": "The brackets do not close.",
    "NO_STABLE_ISOTOPE": "That element has no stable isotope, so it has no "
                       + "natural isotope pattern.",
    "NEEDS_TWO_SIDES": "Write the equation with an arrow: A + B -> C + D.",
    "EMPTY_SIDE": "Both sides of the arrow need at least one species.",
    "TOO_MANY_SPECIES": "Too many species to balance reliably.",
    "NO_SOLUTION": "These species cannot be balanced as written. Check the "
                 + "formulas.",
    "UNDERDETERMINED": "More than one balance is possible, which usually "
                     + "means a species is missing or duplicated.",
    "MUST_BE_POSITIVE": "This value has to be greater than zero.",
    "DIVIDE_BY_ZERO": "That would divide by zero.",
    "NEED_TWO_REAGENTS": "Give at least two reagents.",
    "LEAVE_ONE_BLANK": "Fill in exactly three of the four boxes.",
    "FACTOR_ABOVE_ONE": "The dilution factor has to be greater than 1.",
    "NEED_ONE_STEP": "Ask for at least one step.",
    "BELOW_ABSOLUTE_ZERO": "That is below absolute zero.",
    "UNKNOWN_UNIT": "Unknown unit.",
    "NO_ELEMENT_DATA": "The element table did not load."
  };

  var state = { tool: "molar-mass", inputs: {} };

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

  function calc() { return root.PYTHIA.calc; }

  function say(err) {
    if (err && err.code) {
      var base = MESSAGES[err.code] || err.code;
      return err.detail ? base + " (" + err.detail + ")" : base;
    }
    return String(err);
  }

  function num(value, places) {
    if (!isFinite(value)) return "\u2014";
    return value.toFixed(places === undefined ? 4 : places);
  }

  /* ---- form scaffolding ------------------------------------------------ */

  function field(key, label, opts) {
    opts = opts || {};
    var id = "calc-" + key;
    var input = h("input", {
      type: opts.type || "text",
      id: id,
      value: state.inputs[key] === undefined ? (opts.value || "")
                                             : state.inputs[key],
      placeholder: opts.placeholder || "",
      inputmode: opts.type === "number" ? "decimal" : null,
      step: opts.step || null
    });
    input.addEventListener("input", function () {
      state.inputs[key] = input.value;
      recompute();
    });
    return h("div", { class: "calc-field" }, [
      h("label", { class: "label", "for": id, text: label }),
      input
    ]);
  }

  function select(key, label, options, fallback) {
    var id = "calc-" + key;
    var sel = h("select", { id: id });
    options.forEach(function (o) {
      var opt = h("option", { value: o, text: o });
      if ((state.inputs[key] || fallback) === o) opt.selected = true;
      sel.appendChild(opt);
    });
    sel.addEventListener("change", function () {
      state.inputs[key] = sel.value;
      recompute();
    });
    return h("div", { class: "calc-field" }, [
      h("label", { class: "label", "for": id, text: label }),
      sel
    ]);
  }

  function value(key, fallback) {
    var v = state.inputs[key];
    return (v === undefined || v === "") ? fallback : v;
  }

  function number(key, fallback) {
    var v = value(key, fallback);
    return v === null || v === "" ? NaN : Number(v);
  }

  function resultRows(rows) {
    var body = h("tbody");
    rows.forEach(function (r) {
      body.appendChild(h("tr", null, [
        h("th", { scope: "row", text: r[0] }),
        h("td", { text: r[1] })
      ]));
    });
    return h("table", { class: "rows" }, [body]);
  }

  /* ---- the tools ------------------------------------------------------- */

  var TOOLS = [
    {
      id: "molar-mass",
      label: "Molar mass",
      group: "Mass",
      relation: "M = sum over elements of (standard atomic weight x count)",
      fields: function () {
        return [field("formula", "Formula", {
          placeholder: "C6H12O6, Ca(OH)2, CuSO4.5H2O"
        })];
      },
      run: function () {
        var r = calc().molarMass(value("formula", "C6H12O6"));
        var body = h("tbody");
        r.breakdown.forEach(function (row) {
          body.appendChild(h("tr", null, [
            h("th", { scope: "row",
                      text: row.symbol + " \u00d7 " + row.count }),
            h("td", { text: num(row.contribution, 3) + " g/mol" }),
            h("td", { text: num(row.percent, 2) + " %" })
          ]));
        });
        var dou = calc().degreesOfUnsaturation(value("formula", "C6H12O6"));
        return h("div", null, [
          h("p", { class: "calc-answer",
                   text: num(r.total, 4) + " g/mol" }),
          h("p", {
            class: "example-caption",
            text: dou.whole
              ? "Degrees of unsaturation: " + dou.value
                + ". That many rings and pi bonds between them."
              : "Degrees of unsaturation come out fractional, which means "
                + "this formula cannot describe a neutral molecule. Check "
                + "the hydrogen count."
          }),
          r.charge ? h("p", {
            class: "example-caption",
            text: "The charge of " + (r.charge > 0 ? "+" : "") + r.charge
                + " is noted but not applied: the mass of an electron is far "
                + "below the precision shown here."
          }) : null,
          h("table", { class: "rows" }, [body])
        ]);
      }
    },
    {
      id: "exact-mass",
      label: "Monoisotopic mass",
      group: "Mass",
      relation: "Sum of the most abundant isotope of each atom, not the "
              + "natural average",
      fields: function () {
        return [field("formula2", "Formula", { placeholder: "C6H12O6" })];
      },
      run: function () {
        var formula = value("formula2", "C6H12O6");
        var exact = calc().monoisotopicMass(formula);
        var average = calc().molarMass(formula).total;
        return h("div", null, [
          h("p", { class: "calc-answer", text: num(exact, 5) }),
          resultRows([
            ["Monoisotopic", num(exact, 5)],
            ["Average molar mass", num(average, 4) + " g/mol"],
            ["Difference", num(average - exact, 4)]
          ]),
          h("p", {
            class: "example-caption",
            text: "A mass spectrometer with enough resolution reports the "
                + "monoisotopic value. A balance reports the average. They "
                + "are not interchangeable and the gap grows with molecular "
                + "size."
          })
        ]);
      }
    },
    {
      id: "isotope-pattern",
      label: "Isotope pattern",
      group: "Mass",
      relation: "Each element's natural distribution, convolved once per "
              + "atom",
      fields: function () {
        return [field("formula3", "Formula", { placeholder: "C6H12O6, Cl2" })];
      },
      run: function () {
        var peaks = calc().isotopicPattern(value("formula3", "C6H12O6"));
        var body = h("tbody");
        peaks.forEach(function (p) {
          var bar = h("div", { class: "calc-bar" });
          bar.appendChild(h("span", {
            style: "width:" + Math.max(1, p.relative) + "%"
          }));
          body.appendChild(h("tr", null, [
            h("th", { scope: "row", text: num(p.mass, 4) }),
            h("td", { text: num(p.relative, 2) + " %" }),
            h("td", { class: "calc-bar-cell" }, [bar])
          ]));
        });
        return h("div", null, [
          h("table", { class: "rows" }, [body]),
          h("p", {
            class: "example-caption",
            text: "Carbon contributes about 1.1 % per atom to the M+1 peak, "
                + "so counting carbons from the pattern is often possible. "
                + "Chlorine and bromine give M+2 peaks large enough to "
                + "recognise on sight."
          })
        ]);
      }
    },
    {
      id: "balance",
      label: "Balance an equation",
      group: "Reactions",
      relation: "Solved as a nullspace in exact fractions, so the "
              + "coefficients come out as integers with no rounding",
      fields: function () {
        return [field("equation", "Equation", {
          placeholder: "KMnO4 + HCl -> KCl + MnCl2 + H2O + Cl2"
        })];
      },
      run: function () {
        var r = calc().balance(value("equation", "CH4 + O2 -> CO2 + H2O"));
        var line = h("p", { class: "calc-answer calc-equation" });
        r.reactants.concat(r.products).forEach(function (species, i) {
          if (i === r.reactants.length) {
            line.appendChild(h("span", { class: "path-arrow", text: " \u2192 " }));
          } else if (i > 0) {
            line.appendChild(document.createTextNode(" + "));
          }
          var c = r.coefficients[i];
          if (c !== 1) {
            line.appendChild(h("b", { class: "calc-coefficient",
                                      text: String(c) }));
          }
          line.appendChild(document.createTextNode(species));
        });
        return h("div", null, [
          line,
          h("p", {
            class: "example-caption",
            text: "Balanced across " + r.elements.length + " element"
                + (r.elements.length === 1 ? "" : "s") + ": "
                + r.elements.join(", ") + "."
          })
        ]);
      }
    },
    {
      id: "limiting",
      label: "Limiting reagent",
      group: "Reactions",
      relation: "Whichever reagent gives the fewest moles divided by its "
              + "coefficient runs out first",
      fields: function () {
        return [
          field("r1name", "Reagent 1", { value: "H2" }),
          field("r1mass", "Mass (g)", { type: "number", value: "10" }),
          field("r1mm", "Molar mass", { type: "number", value: "2.016" }),
          field("r1coef", "Coefficient", { type: "number", value: "2" }),
          field("r2name", "Reagent 2", { value: "O2" }),
          field("r2mass", "Mass (g)", { type: "number", value: "64" }),
          field("r2mm", "Molar mass", { type: "number", value: "31.998" }),
          field("r2coef", "Coefficient", { type: "number", value: "1" })
        ];
      },
      run: function () {
        var r = calc().limitingReagent([
          { name: value("r1name", "H2"), mass: number("r1mass", 10),
            molarMass: number("r1mm", 2.016),
            coefficient: number("r1coef", 2) },
          { name: value("r2name", "O2"), mass: number("r2mass", 64),
            molarMass: number("r2mm", 31.998),
            coefficient: number("r2coef", 1) }
        ]);
        var body = h("tbody");
        r.rows.forEach(function (row) {
          body.appendChild(h("tr", { class: row.limiting ? "is-limiting" : null },
            [
              h("th", { scope: "row", text: row.name }),
              h("td", { text: num(row.moles, 4) + " mol" }),
              h("td", { text: row.limiting ? "limiting"
                                           : num(row.excess, 4) + " mol left" })
            ]));
        });
        return h("div", null, [
          h("p", { class: "calc-answer", text: r.limiting.name }),
          h("table", { class: "rows" }, [body])
        ]);
      }
    },
    {
      id: "green",
      label: "Atom economy and E factor",
      group: "Reactions",
      relation: "Atom economy counts only the reactants; the E factor "
              + "counts everything that leaves as waste",
      fields: function () {
        return [
          field("aeProduct", "Mass of wanted product (g)",
                { type: "number", value: "180" }),
          field("aeReactants", "Mass of all reactants (g)",
                { type: "number", value: "250" }),
          field("efWaste", "Mass of waste (g)",
                { type: "number", value: "45" }),
          field("efProduct", "Mass of product (g)",
                { type: "number", value: "15" })
        ];
      },
      run: function () {
        var ae = calc().atomEconomy(number("aeProduct", 180),
                                    number("aeReactants", 250));
        var ef = calc().eFactor(number("efWaste", 45),
                                number("efProduct", 15));
        return h("div", null, [
          resultRows([
            ["Atom economy", num(ae, 2) + " %"],
            ["E factor", num(ef, 3) + " kg waste per kg product"]
          ]),
          h("p", {
            class: "example-caption",
            text: "The two disagree for real processes, and the gap is the "
                + "solvent. A reaction can be near-perfect on paper and "
                + "still generate fifty times its own mass in waste."
          })
        ]);
      }
    },
    {
      id: "ph",
      label: "pH",
      group: "Solutions",
      relation: "Strong: pH = -log C. Weak: [H+] = sqrt(Ka x C), valid "
              + "while dissociation stays small",
      fields: function () {
        return [
          select("phKind", "Solution",
                 ["Strong acid", "Strong base", "Weak acid", "Weak base"],
                 "Weak acid"),
          field("phC", "Concentration (mol/L)",
                { type: "number", value: "0.1" }),
          field("phK", "pKa or pKb", { type: "number", value: "4.76" })
        ];
      },
      run: function () {
        var kind = value("phKind", "Weak acid");
        var c = number("phC", 0.1);
        var k = number("phK", 4.76);
        var p = calc().pH;

        if (kind === "Strong acid") {
          return h("p", { class: "calc-answer",
                          text: "pH " + num(p.strongAcid(c), 2) });
        }
        if (kind === "Strong base") {
          return h("p", { class: "calc-answer",
                          text: "pH " + num(p.strongBase(c), 2) });
        }
        var r = kind === "Weak acid" ? p.weakAcid(c, k) : p.weakBase(c, k);
        var warn = r.dissociated > 5;
        return h("div", null, [
          h("p", { class: "calc-answer", text: "pH " + num(r.pH, 2) }),
          resultRows([["Dissociated", num(r.dissociated, 2) + " %"]]),
          h("p", {
            class: warn ? "no-walkthrough" : "example-caption",
            text: warn
              ? "More than 5 % dissociated, so the approximation behind this "
                + "figure is no longer safe. Solve the quadratic instead of "
                + "trusting this number."
              : "Under 5 % dissociated, so the usual approximation holds."
          })
        ]);
      }
    },
    {
      id: "buffer",
      label: "Buffer",
      group: "Solutions",
      relation: "Henderson-Hasselbalch: pH = pKa + log([base]/[acid])",
      fields: function () {
        return [
          field("bufPka", "pKa", { type: "number", value: "4.76" }),
          field("bufBase", "[base]", { type: "number", value: "0.1" }),
          field("bufAcid", "[acid]", { type: "number", value: "0.1" })
        ];
      },
      run: function () {
        var pka = number("bufPka", 4.76);
        var base = number("bufBase", 0.1);
        var acid = number("bufAcid", 0.1);
        var ph = calc().pH.buffer(pka, base, acid);
        var ratio = base / acid;
        return h("div", null, [
          h("p", { class: "calc-answer", text: "pH " + num(ph, 2) }),
          resultRows([
            ["Ratio base to acid", num(ratio, 3)],
            ["Distance from pKa", num(ph - pka, 2) + " units"]
          ]),
          h("p", {
            class: "example-caption",
            text: "A buffer works best within about one pH unit of its pKa. "
                + "Beyond that the ratio has to be so lopsided that one "
                + "component runs out almost immediately."
          })
        ]);
      }
    },
    {
      id: "dilution",
      label: "Dilution",
      group: "Solutions",
      relation: "C1 x V1 = C2 x V2. Leave one box empty and it is solved "
              + "for",
      fields: function () {
        return [
          field("c1", "C1", { type: "number", value: "1" }),
          field("v1", "V1", { type: "number", placeholder: "leave blank" }),
          field("c2", "C2", { type: "number", value: "0.1" }),
          field("v2", "V2", { type: "number", value: "100" }),
          field("serialFactor", "Serial dilution factor",
                { type: "number", value: "10" }),
          field("serialSteps", "Steps", { type: "number", value: "5" })
        ];
      },
      run: function () {
        var d = calc().dilution({
          c1: value("c1", "1"), v1: value("v1", ""),
          c2: value("c2", "0.1"), v2: value("v2", "100")
        });
        var series = calc().serialDilution(
          number("c1", 1), number("serialFactor", 10),
          Math.min(20, Math.max(1, Math.round(number("serialSteps", 5)))));

        var body = h("tbody");
        series.forEach(function (s) {
          body.appendChild(h("tr", null, [
            h("th", { scope: "row", text: "Step " + s.step }),
            h("td", { text: s.concentration.toPrecision(4) }),
            h("td", { text: "1 in " + s.fold.toLocaleString("en") })
          ]));
        });

        return h("div", null, [
          h("p", { class: "calc-answer",
                   text: d.solvedFor.toUpperCase() + " = " + num(d.value, 4) }),
          h("p", { class: "label", text: "Serial dilution",
                   style: "margin-top:var(--gap-lg)" }),
          h("table", { class: "rows" }, [body])
        ]);
      }
    },
    {
      id: "units",
      label: "Temperature and pressure",
      group: "Units",
      relation: "Temperature through kelvin, pressure through the pascal",
      fields: function () {
        return [
          field("tVal", "Temperature", { type: "number", value: "25" }),
          select("tFrom", "From", ["C", "K", "F"], "C"),
          select("tTo", "To", ["C", "K", "F"], "K"),
          field("pVal", "Pressure", { type: "number", value: "1" }),
          select("pFrom", "From", calc().pressureUnits, "atm"),
          select("pTo", "To", calc().pressureUnits, "kPa")
        ];
      },
      run: function () {
        var t = calc().temperature.convert(
          number("tVal", 25), value("tFrom", "C"), value("tTo", "K"));
        var p = calc().convertPressure(
          number("pVal", 1), value("pFrom", "atm"), value("pTo", "kPa"));
        return resultRows([
          ["Temperature", num(t, 4) + " " + value("tTo", "K")],
          ["Pressure", num(p, 4) + " " + value("pTo", "kPa")]
        ]);
      }
    }
  ];

  function tool(id) {
    for (var i = 0; i < TOOLS.length; i++) {
      if (TOOLS[i].id === id) return TOOLS[i];
    }
    return TOOLS[0];
  }

  /* ---- rendering ------------------------------------------------------- */

  function recompute() {
    var host = document.getElementById("calc-output");
    if (!host) return;
    host.innerHTML = "";
    try {
      host.appendChild(tool(state.tool).run());
    } catch (err) {
      host.appendChild(h("p", { class: "disclaimer", text: say(err) }));
    }
  }

  function renderBrowser(onPick) {
    var wrap = h("div", { class: "browser" });
    var list = h("div", { class: "group-list" });
    var seen = null;

    TOOLS.forEach(function (t) {
      if (t.group !== seen) {
        seen = t.group;
        list.appendChild(h("p", { class: "label group-name", text: t.group }));
      }
      var ul = list.lastChild;
      if (!ul || ul.tagName !== "UL") {
        ul = h("ul", { class: "mol-list" });
        list.appendChild(ul);
      }
      var btn = h("button", {
        type: "button",
        text: t.label,
        "aria-current": t.id === state.tool ? "true" : null
      });
      btn.addEventListener("click", function () { onPick(t.id); });
      ul.appendChild(h("li", null, [btn]));
    });

    wrap.appendChild(list);
    return wrap;
  }

  function render() {
    var mount = document.getElementById("view");
    if (!mount) return;

    var t = tool(state.tool);

    var form = h("div", { class: "calc-form" });
    t.fields().forEach(function (f) { form.appendChild(f); });

    var detail = h("div", null, [
      h("div", { class: "section-head" }, [
        h("h2", { text: t.label }),
        h("p", { text: t.group })
      ]),
      h("p", { class: "calc-relation", text: t.relation }),
      form,
      h("div", { id: "calc-output", class: "calc-output" })
    ]);

    mount.innerHTML = "";
    mount.appendChild(h("div", { class: "explore" }, [
      renderBrowser(function (id) {
        state.tool = id;
        render();
        document.getElementById("main").focus();
      }),
      detail
    ]));

    recompute();
  }

  root.PYTHIA = root.PYTHIA || {};
  root.PYTHIA.views = root.PYTHIA.views || {};
  root.PYTHIA.views.calculators = {
    label: "Calculators",
    render: render
  };
})(typeof window !== "undefined" ? window : this);
