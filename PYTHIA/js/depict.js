/* PYTHIA -- 2D structure renderer.
 *
 * Draws a skeletal formula as SVG from the coordinates the build step
 * produced. No dependencies.
 *
 * Structures render in a single ink colour, the way a journal or a textbook
 * prints them. Colour is reserved for meaning: a highlighted stereocentre, a
 * priority rank, an atom the reader is pointing at. Element colouring is
 * available but off by default, because once oxygen is always red the reader
 * stops reading the letter.
 *
 * PYTHIA.depict(spec, options) -> SVGElement
 *
 *   spec      { atoms: [{el, x, y, nH, q}], bonds: [{a, b, o, w}] }
 *             w is "wedge", "dash" or "either" where stereochemistry is drawn
 *   options   see DEFAULTS
 */
(function (root) {
  "use strict";

  var NS = "http://www.w3.org/2000/svg";

  var DEFAULTS = {
    bondLength: 34,       // px between two bonded atoms
    lineWidth: 1.5,
    padding: 18,
    fontSize: 13,
    doubleGap: 4.4,       // separation between the lines of a double bond
    wedgeWidth: 7,
    hashCount: 6,
    elementColour: false, // monochrome unless asked otherwise
    highlight: null,      // Set or array of atom indices to emphasise
    ranks: null,          // { atomIndex: "a" } priority badges
    dim: null,            // atom indices to push back visually
    interactive: false,   // attach hover and click handlers
    onAtomEnter: null,
    onAtomLeave: null,
    onAtomClick: null,

    /* Mechanism layer.
     *
     * arrows: [{ from, to, kind, bow }]
     *   from / to   { atom: i } or { bond: [i, j] }
     *   kind        "pair" for a full arrowhead, two electrons moving
     *               "single" for a half head, one electron (a fishhook)
     *   bow         how far the curve bulges, signed. Positive bows to the
     *               left of the source-to-target direction. Around 0.3 to
     *               0.6 reads well; 0 gives a straight arrow.
     *
     * lonePairs: { atomIndex: count }  dots placed where no bond is
     * annotations: [{ atom: i, text: "\u03b4+" }]  partial charges and labels
     */
    arrows: null,
    lonePairs: null,
    annotations: null
  };

  /* Heteroatom colouring is done in CSS, not here.
   *
   * The obvious approach -- setting fill="var(--el-o)" on the text -- does
   * not work, for two separate reasons that stack. Browsers do not
   * substitute custom properties inside SVG presentation attributes, so the
   * value is simply ignored; and even a literal colour there would lose to
   * the .depict-label rule in the stylesheet, because any CSS rule outranks
   * a presentation attribute. So the element goes on a data attribute and
   * the stylesheet decides, gated by a class on the root.
   */

  function el(name, attrs) {
    var node = document.createElementNS(NS, name);
    if (attrs) {
      for (var k in attrs) {
        if (attrs[k] !== null && attrs[k] !== undefined) {
          node.setAttribute(k, attrs[k]);
        }
      }
    }
    return node;
  }

  function toSet(v) {
    if (!v) return null;
    if (v instanceof Set) return v;
    return new Set(v);
  }

  /* ---------------------------------------------------------------------
   * Layout
   * ------------------------------------------------------------------- */

  /* Bring the build-time coordinates into pixel space.
   *
   * RDKit lays out on a grid whose natural bond length is about 1.5 units,
   * but that is not guaranteed, so the scale is taken from the median bond
   * length actually present. Median rather than mean: a single stretched
   * bond in a strained ring should not shrink the whole drawing.
   */
  function layout(spec, opt) {
    var lengths = [];
    spec.bonds.forEach(function (b) {
      var A = spec.atoms[b.a], B = spec.atoms[b.b];
      lengths.push(Math.hypot(B.x - A.x, B.y - A.y));
    });
    lengths.sort(function (p, q) { return p - q; });
    var unit = lengths.length ? lengths[Math.floor(lengths.length / 2)] : 1.5;
    if (!unit) unit = 1.5;
    var k = opt.bondLength / unit;

    var pts = spec.atoms.map(function (a) {
      return { x: a.x * k, y: -a.y * k };   // SVG y grows downward
    });

    var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;

    function include(x, y, margin) {
      margin = margin || 0;
      if (x - margin < minX) minX = x - margin;
      if (y - margin < minY) minY = y - margin;
      if (x + margin > maxX) maxX = x + margin;
      if (y + margin > maxY) maxY = y + margin;
    }

    /* Atoms, allowing for the width of any written label. A bare vertex
     * needs almost nothing; "NH2" sticks out on both sides. */
    spec.atoms.forEach(function (a, i) {
      var margin = opt.lineWidth;
      if (a.el !== "C" || a.q) {
        var chars = a.el.length
          + (a.nH > 1 ? String(a.nH).length + 1 : (a.nH === 1 ? 1 : 0))
          + (a.q ? 1 : 0);
        margin = opt.fontSize * 0.62 * chars * 0.5 + 2;
      }
      include(pts[i].x, pts[i].y, margin);
    });

    /* Everything in the mechanism layer sits outside the structure, so it
     * has to be measured too or it gets cut off. A quadratic curve never
     * leaves the triangle formed by its two ends and its control point, so
     * including those three points bounds the arrow safely. */
    var reach = opt.fontSize * 1.35;

    spec.atoms.forEach(function (a, i) {
      if (a.rad) include(pts[i].x, pts[i].y, reach);
    });
    if (opt.lonePairs) {
      Object.keys(opt.lonePairs).forEach(function (key) {
        var i = parseInt(key, 10);
        if (pts[i]) include(pts[i].x, pts[i].y, reach);
      });
    }
    if (opt.annotations) {
      opt.annotations.forEach(function (an) {
        if (pts[an.atom]) {
          include(pts[an.atom].x, pts[an.atom].y, opt.fontSize * 2.3);
        }
      });
    }
    if (opt.ranks) {
      Object.keys(opt.ranks).forEach(function (key) {
        var i = parseInt(key, 10);
        if (pts[i]) include(pts[i].x, pts[i].y, opt.fontSize * 1.9);
      });
    }
    if (opt.arrows) {
      opt.arrows.forEach(function (arrow) {
        var geo = arrowGeometry(pts, arrow, opt);
        var head = 9;
        include(geo.start.x, geo.start.y, head);
        include(geo.ctrl.x, geo.ctrl.y, head);
        include(geo.end.x, geo.end.y, head);
      });
    }

    if (!isFinite(minX)) { minX = minY = maxX = maxY = 0; }

    var pad = opt.padding;
    pts.forEach(function (p) { p.x += pad - minX; p.y += pad - minY; });

    return {
      pts: pts,
      width: (maxX - minX) + pad * 2,
      height: (maxY - minY) + pad * 2
    };
  }

  /* Which atoms get a written label.
   *
   * Skeletal convention: carbon is a bare vertex. Everything else is
   * written out, as is any carbon carrying a charge, and any atom with no
   * bonds at all (otherwise it would be invisible).
   */
  function needsLabel(atom, degree) {
    if (atom.el !== "C") return true;
    if (atom.q) return true;
    if (degree === 0) return true;
    return false;
  }

  function labelText(atom) {
    var s = atom.el;
    if (atom.nH === 1) s += "H";
    else if (atom.nH > 1) s += "H" + atom.nH;
    return s;
  }

  /* Put the hydrogens on whichever side is emptier, so "HO-" reads correctly
   * when the rest of the molecule sits to the right. */
  function hydrogensLeadLeft(spec, pts, i) {
    var atom = spec.atoms[i];
    if (!atom.nH) return false;
    var sum = 0, n = 0;
    spec.bonds.forEach(function (b) {
      var other = b.a === i ? b.b : (b.b === i ? b.a : -1);
      if (other < 0) return;
      sum += pts[other].x - pts[i].x;
      n++;
    });
    return n > 0 && sum > 0.5;
  }

  function chargeText(q) {
    if (!q) return "";
    var sign = q > 0 ? "+" : "\u2212";
    var mag = Math.abs(q);
    return mag > 1 ? String(mag) + sign : sign;
  }

  /* ---------------------------------------------------------------------
   * Bond geometry
   * ------------------------------------------------------------------- */

  /* Trim a bond so it stops short of a written label instead of running
   * through the letters. */
  function trim(from, to, amount) {
    var dx = to.x - from.x, dy = to.y - from.y;
    var len = Math.hypot(dx, dy) || 1;
    return { x: from.x + dx / len * amount, y: from.y + dy / len * amount };
  }

  /* Which side of a double bond the second line should sit on.
   *
   * Offsetting towards whichever side carries more substituents puts the
   * inner line inside a ring without needing to know the ring exists, and
   * leaves a lone alkene symmetric.
   */
  function offsetSide(spec, pts, b) {
    var A = pts[b.a], B = pts[b.b];
    var dx = B.x - A.x, dy = B.y - A.y;
    var len = Math.hypot(dx, dy) || 1;
    var px = -dy / len, py = dx / len;
    var net = 0;
    spec.bonds.forEach(function (o) {
      if (o === b) return;
      [[o.a, o.b], [o.b, o.a]].forEach(function (pair) {
        if (pair[0] !== b.a && pair[0] !== b.b) return;
        if (pair[1] === b.a || pair[1] === b.b) return;
        var v = pts[pair[1]], base = pts[pair[0]];
        net += (v.x - base.x) * px + (v.y - base.y) * py;
      });
    });
    return net === 0 ? 0 : (net > 0 ? 1 : -1);
  }

  /* ---------------------------------------------------------------------
   * Main
   * ------------------------------------------------------------------- */

  function depict(spec, options) {
    var opt = {};
    for (var k in DEFAULTS) opt[k] = DEFAULTS[k];
    for (var j in (options || {})) opt[j] = options[j];

    var highlight = toSet(opt.highlight);
    var dim = toSet(opt.dim);

    var geo = layout(spec, opt);
    var pts = geo.pts;

    var degree = spec.atoms.map(function () { return 0; });
    spec.bonds.forEach(function (b) { degree[b.a]++; degree[b.b]++; });

    var labelled = spec.atoms.map(function (a, i) {
      return needsLabel(a, degree[i]);
    });

    var svg = el("svg", {
      xmlns: NS,
      viewBox: "0 0 " + geo.width.toFixed(1) + " " + geo.height.toFixed(1),
      width: geo.width.toFixed(1),
      height: geo.height.toFixed(1),
      class: "depict" + (opt.elementColour ? " is-coloured" : ""),
      role: "img"
    });

    var gBonds = el("g", { class: "depict-bonds" });
    var gAtoms = el("g", { class: "depict-atoms" });
    svg.appendChild(gBonds);
    svg.appendChild(gAtoms);

    // how far to pull a bond back from each end
    var clearance = spec.atoms.map(function (a, i) {
      if (!labelled[i]) return 0;
      return opt.fontSize * 0.62;
    });

    spec.bonds.forEach(function (b) {
      var A = pts[b.a], B = pts[b.b];
      var a1 = trim(A, B, clearance[b.a]);
      var b1 = trim(B, A, clearance[b.b]);
      var faded = dim && (dim.has(b.a) || dim.has(b.b));
      var cls = "depict-bond" + (faded ? " is-dim" : "");

      if (b.w === "wedge" || b.w === "dash") {
        gBonds.appendChild(stereoBond(a1, b1, b.w, opt, cls));
        return;
      }
      if (b.w === "either") {
        gBonds.appendChild(wavyBond(a1, b1, opt, cls));
        return;
      }

      var dx = b1.x - a1.x, dy = b1.y - a1.y;
      var len = Math.hypot(dx, dy) || 1;
      var px = -dy / len * opt.doubleGap, py = dx / len * opt.doubleGap;

      if (b.o === 2) {
        var side = offsetSide(spec, pts, b);
        if (side === 0) {
          gBonds.appendChild(line(a1.x + px / 2, a1.y + py / 2,
                                  b1.x + px / 2, b1.y + py / 2, opt, cls));
          gBonds.appendChild(line(a1.x - px / 2, a1.y - py / 2,
                                  b1.x - px / 2, b1.y - py / 2, opt, cls));
        } else {
          gBonds.appendChild(line(a1.x, a1.y, b1.x, b1.y, opt, cls));
          // the inner line is shortened at both ends so the ring reads cleanly
          var s = side, inset = 0.16;
          var ax = a1.x + dx * inset + px * s, ay = a1.y + dy * inset + py * s;
          var bx = b1.x - dx * inset + px * s, by = b1.y - dy * inset + py * s;
          gBonds.appendChild(line(ax, ay, bx, by, opt, cls));
        }
      } else if (b.o === 3) {
        gBonds.appendChild(line(a1.x, a1.y, b1.x, b1.y, opt, cls));
        gBonds.appendChild(line(a1.x + px, a1.y + py, b1.x + px, b1.y + py,
                                opt, cls));
        gBonds.appendChild(line(a1.x - px, a1.y - py, b1.x - px, b1.y - py,
                                opt, cls));
      } else {
        gBonds.appendChild(line(a1.x, a1.y, b1.x, b1.y, opt, cls));
      }
    });

    spec.atoms.forEach(function (atom, i) {
      var p = pts[i];
      var group = el("g", {
        class: "depict-atom"
          + (highlight && highlight.has(i) ? " is-highlight" : "")
          + (dim && dim.has(i) ? " is-dim" : ""),
        "data-atom": i
      });

      if (highlight && highlight.has(i)) {
        group.appendChild(el("circle", {
          cx: p.x.toFixed(1), cy: p.y.toFixed(1),
          r: (opt.fontSize * 0.95).toFixed(1),
          class: "depict-halo"
        }));
      }

      if (labelled[i]) {
        var lead = hydrogensLeadLeft(spec, pts, i);
        var text = lead
          ? (atom.nH === 1 ? "H" : "H" + atom.nH) + atom.el
          : labelText(atom);
        var t = el("text", {
          x: p.x.toFixed(1),
          y: p.y.toFixed(1),
          "text-anchor": "middle",
          "dominant-baseline": "central",
          "font-size": opt.fontSize,
          class: "depict-label",
          "data-el": atom.el
        });
        t.textContent = text;
        group.appendChild(t);

        if (atom.q) {
          var c = el("text", {
            x: (p.x + opt.fontSize * (0.30 + 0.30 * text.length)).toFixed(1),
            y: (p.y - opt.fontSize * 0.46).toFixed(1),
            "text-anchor": "middle",
            "dominant-baseline": "central",
            "font-size": (opt.fontSize * 0.72).toFixed(1),
            class: "depict-charge"
          });
          c.textContent = chargeText(atom.q);
          group.appendChild(c);
        }
      }

      if (opt.ranks && opt.ranks[i]) {
        /* Placed away from the bonds rather than at a fixed offset. A
         * priority letter sitting on top of a bond is worse than no letter,
         * because the reader has to decode the picture before they can read
         * the chemistry. */
        var ang = freeDirections(spec, pts, i, 1)[0];
        var out = opt.fontSize * (labelled[i] ? 1.45 : 1.0);
        var badge = el("text", {
          x: (p.x + Math.cos(ang) * out).toFixed(1),
          y: (p.y + Math.sin(ang) * out).toFixed(1),
          "text-anchor": "middle",
          "dominant-baseline": "central",
          "font-size": (opt.fontSize * 0.82).toFixed(1),
          class: "depict-rank"
        });
        badge.textContent = opt.ranks[i];
        group.appendChild(badge);
      }

      if (opt.interactive) {
        // an invisible disc, so pointing at a bare vertex works too
        var hit = el("circle", {
          cx: p.x.toFixed(1), cy: p.y.toFixed(1),
          r: (opt.bondLength * 0.38).toFixed(1),
          class: "depict-hit"
        });
        group.appendChild(hit);
        group.style.cursor = "pointer";
        if (opt.onAtomEnter) {
          group.addEventListener("mouseenter", function () { opt.onAtomEnter(i); });
        }
        if (opt.onAtomLeave) {
          group.addEventListener("mouseleave", function () { opt.onAtomLeave(i); });
        }
        if (opt.onAtomClick) {
          group.addEventListener("click", function () { opt.onAtomClick(i); });
        }
      }

      gAtoms.appendChild(group);
    });

    /* ---- mechanism layer, drawn above the structure ------------------ */

    var hasRadicals = spec.atoms.some(function (a) { return a.rad; });

    if (opt.lonePairs || opt.annotations || opt.arrows || hasRadicals) {
      var gMech = el("g", { class: "depict-mech" });
      svg.appendChild(gMech);

      /* An unpaired electron is one dot, a lone pair is two. Drawing them
       * the same way would erase the distinction the whole of radical
       * chemistry turns on. */
      if (hasRadicals) {
        spec.atoms.forEach(function (atom, i) {
          if (!atom.rad) return;
          var reach = labelled[i] ? opt.fontSize * 0.95 : opt.fontSize * 0.5;
          freeDirections(spec, pts, i, atom.rad).forEach(function (ang) {
            gMech.appendChild(el("circle", {
              cx: (pts[i].x + Math.cos(ang) * reach).toFixed(1),
              cy: (pts[i].y + Math.sin(ang) * reach).toFixed(1),
              r: 1.9,
              class: "depict-radical"
            }));
          });
        });
      }

      if (opt.lonePairs) {
        Object.keys(opt.lonePairs).forEach(function (key) {
          var i = parseInt(key, 10);
          var count = opt.lonePairs[key];
          var slots = freeDirections(spec, pts, i, count);
          var reach = labelled[i] ? opt.fontSize * 0.95 : opt.fontSize * 0.5;
          slots.forEach(function (ang) {
            var cx = pts[i].x + Math.cos(ang) * reach;
            var cy = pts[i].y + Math.sin(ang) * reach;
            var px = -Math.sin(ang) * 2.4, py = Math.cos(ang) * 2.4;
            [[cx + px, cy + py], [cx - px, cy - py]].forEach(function (d) {
              gMech.appendChild(el("circle", {
                cx: d[0].toFixed(1), cy: d[1].toFixed(1), r: 1.5,
                class: "depict-lonepair"
              }));
            });
          });
        });
      }

      if (opt.annotations) {
        opt.annotations.forEach(function (an) {
          var ang = freeDirections(spec, pts, an.atom, 1)[0];
          var reach = opt.fontSize * (labelled[an.atom] ? 1.5 : 1.15);
          var t = el("text", {
            x: (pts[an.atom].x + Math.cos(ang) * reach).toFixed(1),
            y: (pts[an.atom].y + Math.sin(ang) * reach).toFixed(1),
            "text-anchor": "middle",
            "dominant-baseline": "central",
            "font-size": (opt.fontSize * 0.8).toFixed(1),
            class: "depict-annotation"
          });
          t.textContent = an.text;
          gMech.appendChild(t);
        });
      }

      if (opt.arrows) {
        opt.arrows.forEach(function (arrow, n) {
          gMech.appendChild(curvedArrow(spec, pts, arrow, opt, n));
        });
      }
    }

    return svg;
  }

  function line(x1, y1, x2, y2, opt, cls) {
    return el("line", {
      x1: x1.toFixed(1), y1: y1.toFixed(1),
      x2: x2.toFixed(1), y2: y2.toFixed(1),
      "stroke-width": opt.lineWidth,
      class: cls
    });
  }

  /* ---------------------------------------------------------------------
   * Mechanism layer
   * ------------------------------------------------------------------- */

  /* Directions around an atom that no bond already occupies.
   *
   * Lone pairs and charge labels have to go somewhere, and putting them on
   * top of a bond makes a diagram unreadable. Candidate angles are scored
   * by how far they sit from the nearest bond, then taken greedily with a
   * minimum separation so two lone pairs do not land on each other.
   */
  function freeDirections(spec, pts, i, count) {
    var occupied = [];
    spec.bonds.forEach(function (b) {
      var other = b.a === i ? b.b : (b.b === i ? b.a : -1);
      if (other < 0) return;
      occupied.push(Math.atan2(pts[other].y - pts[i].y,
                               pts[other].x - pts[i].x));
    });

    if (!occupied.length) {
      var out = [];
      for (var k = 0; k < count; k++) {
        out.push(-Math.PI / 2 + k * (2 * Math.PI / Math.max(count, 1)));
      }
      return out;
    }

    var candidates = [];
    for (var s = 0; s < 72; s++) {
      var ang = -Math.PI + s * (2 * Math.PI / 72);
      var worst = Infinity;
      occupied.forEach(function (o) {
        var d = Math.abs(Math.atan2(Math.sin(ang - o), Math.cos(ang - o)));
        if (d < worst) worst = d;
      });
      candidates.push({ ang: ang, score: worst });
    }
    candidates.sort(function (p, q) { return q.score - p.score; });

    var picked = [];
    var minSep = Math.PI / 4;
    for (var c = 0; c < candidates.length && picked.length < count; c++) {
      var ok = true;
      for (var p = 0; p < picked.length; p++) {
        var diff = candidates[c].ang - picked[p];
        if (Math.abs(Math.atan2(Math.sin(diff), Math.cos(diff))) < minSep) {
          ok = false;
          break;
        }
      }
      if (ok) picked.push(candidates[c].ang);
    }
    while (picked.length < count) picked.push(candidates[0].ang);
    return picked;
  }

  function refPoint(pts, ref) {
    if (ref.atom !== undefined && ref.atom !== null) {
      return { x: pts[ref.atom].x, y: pts[ref.atom].y };
    }
    var a = pts[ref.bond[0]], b = pts[ref.bond[1]];
    return { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
  }

  /* Where an arrow actually goes.
   *
   * Shared by the drawing code and by the code that sizes the canvas. They
   * have to agree: an arrow computed one way and measured another is an
   * arrow that gets clipped, and a clipped arrow in a mechanism is a
   * missing piece of the explanation rather than a cosmetic flaw.
   */
  function arrowGeometry(pts, arrow, opt) {
    var A = refPoint(pts, arrow.from);
    var B = refPoint(pts, arrow.to);

    var dx = B.x - A.x, dy = B.y - A.y;
    var chord = Math.hypot(dx, dy) || 1;
    var standoff = Math.min(opt.fontSize * 0.85, chord * 0.28);

    var start = { x: A.x + dx / chord * standoff,
                  y: A.y + dy / chord * standoff };
    var end = { x: B.x - dx / chord * standoff,
                y: B.y - dy / chord * standoff };

    var bow = arrow.bow === undefined ? 0.4 : arrow.bow;
    var ux = end.x - start.x, uy = end.y - start.y;
    var ul = Math.hypot(ux, uy) || 1;

    /* Bow is a fraction of the chord, which works until the chord is short.
     * An arrow from a bond to one of its own atoms -- a leaving group
     * departing, say -- spans half a bond length, and a percentage of that
     * is a bump rather than an arc. Below a floor tied to bond length the
     * curve stops reading as a curve, so the arc is held at that floor.
     * A bow of exactly zero still means a straight arrow, deliberately. */
    var arc = bow * ul;
    if (bow !== 0) {
      var floor = opt.bondLength * 0.42;
      if (Math.abs(arc) < floor) arc = (arc < 0 ? -1 : 1) * floor;
    }

    var ctrl = {
      x: (start.x + end.x) / 2 + (-uy / ul) * arc,
      y: (start.y + end.y) / 2 + (ux / ul) * arc
    };
    return { start: start, ctrl: ctrl, end: end };
  }

  /* A curved electron-pushing arrow.
   *
   * The convention it has to respect: a full head means a pair of electrons
   * moved together, a half head means a single electron went that way. Get
   * that wrong and the diagram says something false about the chemistry, so
   * the two are drawn as distinctly as possible rather than as variations
   * on a theme.
   */
  function curvedArrow(spec, pts, arrow, opt, n) {
    var geo = arrowGeometry(pts, arrow, opt);
    var start = geo.start, ctrl = geo.ctrl, end = geo.end;

    var g = el("g", {
      class: "depict-arrow" + (arrow.kind === "single" ? " is-single" : ""),
      "data-arrow": n
    });

    g.appendChild(el("path", {
      d: "M " + start.x.toFixed(1) + " " + start.y.toFixed(1)
       + " Q " + ctrl.x.toFixed(1) + " " + ctrl.y.toFixed(1)
       + " " + end.x.toFixed(1) + " " + end.y.toFixed(1),
      fill: "none",
      "stroke-width": opt.lineWidth,
      class: "depict-arrow-line"
    }));

    // tangent at the end of a quadratic curve points away from the control
    var tx = end.x - ctrl.x, ty = end.y - ctrl.y;
    var tl = Math.hypot(tx, ty) || 1;
    tx /= tl; ty /= tl;
    var px = -ty, py = tx;
    var headLen = 7.5, headHalf = 3.2;
    var base = { x: end.x - tx * headLen, y: end.y - ty * headLen };

    var head;
    if (arrow.kind === "single") {
      // one barb only: a single electron moved
      head = "M " + end.x.toFixed(1) + " " + end.y.toFixed(1)
           + " L " + (base.x + px * headHalf * 1.5).toFixed(1)
           + " " + (base.y + py * headHalf * 1.5).toFixed(1);
      g.appendChild(el("path", {
        d: head, fill: "none", "stroke-width": opt.lineWidth,
        class: "depict-arrow-line"
      }));
    } else {
      head = "M " + end.x.toFixed(1) + " " + end.y.toFixed(1)
           + " L " + (base.x + px * headHalf).toFixed(1)
           + " " + (base.y + py * headHalf).toFixed(1)
           + " L " + (base.x - px * headHalf).toFixed(1)
           + " " + (base.y - py * headHalf).toFixed(1)
           + " Z";
      g.appendChild(el("path", { d: head, class: "depict-arrow-head" }));
    }
    return g;
  }

  /* A wedge is a filled triangle: narrow at the stereocentre, wide at the
   * atom coming towards the reader. A hash is the same triangle cut into
   * bars, widening as it recedes. */
  function stereoBond(a, b, kind, opt, cls) {
    var dx = b.x - a.x, dy = b.y - a.y;
    var len = Math.hypot(dx, dy) || 1;
    var px = -dy / len, py = dx / len;
    var w = opt.wedgeWidth / 2;

    if (kind === "wedge") {
      var pathData = "M " + a.x.toFixed(1) + " " + a.y.toFixed(1)
        + " L " + (b.x + px * w).toFixed(1) + " " + (b.y + py * w).toFixed(1)
        + " L " + (b.x - px * w).toFixed(1) + " " + (b.y - py * w).toFixed(1)
        + " Z";
      return el("path", { d: pathData, class: cls + " depict-wedge" });
    }

    var g = el("g", { class: cls + " depict-hash" });
    for (var i = 1; i <= opt.hashCount; i++) {
      var f = i / opt.hashCount;
      var cx = a.x + dx * f, cy = a.y + dy * f;
      var hw = w * f;
      g.appendChild(el("line", {
        x1: (cx + px * hw).toFixed(1), y1: (cy + py * hw).toFixed(1),
        x2: (cx - px * hw).toFixed(1), y2: (cy - py * hw).toFixed(1),
        "stroke-width": opt.lineWidth
      }));
    }
    return g;
  }

  /* Undefined configuration. Drawn wavy, which is the convention, and it
   * should look unmistakably different from a hash. */
  function wavyBond(a, b, opt, cls) {
    var dx = b.x - a.x, dy = b.y - a.y;
    var len = Math.hypot(dx, dy) || 1;
    var px = -dy / len, py = dx / len;
    var steps = 8, amp = 2.6, d = "M " + a.x.toFixed(1) + " " + a.y.toFixed(1);
    for (var i = 1; i <= steps; i++) {
      var f = i / steps;
      var s = (i % 2 === 0 ? -1 : 1) * amp;
      d += " Q " + (a.x + dx * (f - 0.5 / steps) + px * s).toFixed(1)
        + " " + (a.y + dy * (f - 0.5 / steps) + py * s).toFixed(1)
        + " " + (a.x + dx * f).toFixed(1)
        + " " + (a.y + dy * f).toFixed(1);
    }
    return el("path", {
      d: d, fill: "none", "stroke-width": opt.lineWidth,
      class: cls + " depict-wavy"
    });
  }

  root.PYTHIA = root.PYTHIA || {};
  root.PYTHIA.depict = depict;
})(typeof window !== "undefined" ? window : this);
