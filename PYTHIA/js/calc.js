/* PYTHIA -- chemical calculators.
 *
 * Pure functions over numbers and strings. Nothing here touches the DOM,
 * so every one of these can be tested on its own, and that is the point:
 * an arithmetic error in a teaching tool is worse than a missing feature.
 *
 * Element data comes from data/elements.js.
 *
 * Errors are thrown as CalcError with a machine-readable code, so the
 * interface can phrase the message and the engine does not have to know
 * what language the reader speaks.
 */
(function (root) {
  "use strict";

  function CalcError(code, detail) {
    this.name = "CalcError";
    this.code = code;
    this.detail = detail;
    this.message = code + (detail ? ": " + detail : "");
  }
  CalcError.prototype = Object.create(Error.prototype);

  function elements() {
    var table = root.PYTHIA_ELEMENTS;
    if (!table) throw new CalcError("NO_ELEMENT_DATA");
    return table;
  }

  /* ---------------------------------------------------------------------
   * Formula parsing
   * ------------------------------------------------------------------- */

  /* Handles nesting and hydrate dots: Fe2(SO4)3, Ca(OH)2, CuSO4.5H2O.
   *
   * A trailing charge is accepted and ignored for mass purposes, because
   * the mass of an electron is four orders of magnitude below the
   * precision anyone reads off this. Written as a rejection would be
   * unhelpful; written as a silent success would be wrong; so it is
   * reported back and the caller can say so.
   */
  function parseFormula(formula) {
    if (typeof formula !== "string" || !formula.trim()) {
      throw new CalcError("EMPTY_FORMULA");
    }

    var text = formula.replace(/\s+/g, "");
    var charge = 0;

    var chargeMatch = text.match(/([+-]\d*|\d*[+-])$/);
    if (chargeMatch && /[+-]/.test(chargeMatch[0])) {
      var token = chargeMatch[0];
      var sign = token.indexOf("-") >= 0 ? -1 : 1;
      var digits = token.replace(/[+-]/g, "");
      charge = sign * (digits ? parseInt(digits, 10) : 1);
      text = text.slice(0, text.length - token.length);
    }

    // hydrate notation: everything after a dot is a separate unit
    var units = text.split(/[.\u00b7\u2022]/).filter(function (u) {
      return u.length;
    });
    if (!units.length) throw new CalcError("EMPTY_FORMULA");

    var counts = {};

    units.forEach(function (unit) {
      var lead = unit.match(/^(\d+)/);
      var multiple = 1;
      if (lead) {
        multiple = parseInt(lead[1], 10);
        unit = unit.slice(lead[1].length);
      }
      var part = parseUnit(unit);
      for (var symbol in part) {
        counts[symbol] = (counts[symbol] || 0) + part[symbol] * multiple;
      }
    });

    if (!Object.keys(counts).length) throw new CalcError("EMPTY_FORMULA");
    return { counts: counts, charge: charge };
  }

  function parseUnit(text) {
    var table = elements();
    var stack = [{}];
    var i = 0;

    function multiplyTop(factor) {
      var top = stack[stack.length - 1];
      for (var s in top) top[s] *= factor;
    }

    while (i < text.length) {
      var ch = text[i];

      if (ch === "(" || ch === "[") {
        stack.push({});
        i++;
        continue;
      }

      if (ch === ")" || ch === "]") {
        if (stack.length < 2) throw new CalcError("UNBALANCED_BRACKET");
        i++;
        var digits = text.slice(i).match(/^\d+/);
        var factor = 1;
        if (digits) {
          factor = parseInt(digits[0], 10);
          i += digits[0].length;
        }
        var group = stack.pop();
        var into = stack[stack.length - 1];
        for (var g in group) {
          into[g] = (into[g] || 0) + group[g] * factor;
        }
        continue;
      }

      var symbolMatch = text.slice(i).match(/^([A-Z][a-z]{0,2})/);
      if (!symbolMatch) throw new CalcError("BAD_CHARACTER", ch);

      var symbol = symbolMatch[1];
      // greedy match may over-read: Cu vs C followed by u
      while (symbol.length > 1 && !table[symbol]) {
        symbol = symbol.slice(0, symbol.length - 1);
      }
      if (!table[symbol]) throw new CalcError("UNKNOWN_ELEMENT", symbolMatch[1]);
      i += symbol.length;

      var num = text.slice(i).match(/^\d+/);
      var count = 1;
      if (num) {
        count = parseInt(num[0], 10);
        i += num[0].length;
      }
      var top = stack[stack.length - 1];
      top[symbol] = (top[symbol] || 0) + count;
    }

    if (stack.length !== 1) throw new CalcError("UNBALANCED_BRACKET");
    return stack[0];
  }

  /* ---------------------------------------------------------------------
   * Masses
   * ------------------------------------------------------------------- */

  /* Rings plus pi bonds, from the formula alone.
   *
   * (2C + 2 + N - H - X) / 2. Oxygen and sulfur are absent from the
   * expression because divalent atoms insert into a chain without changing
   * how many hydrogens it can hold. Worth computing before anything else
   * in a structure problem: zero rules out every carbonyl at a stroke, and
   * four or more usually means a benzene ring.
   */
  function degreesOfUnsaturation(formula) {
    var counts = parseFormula(formula).counts;
    var c = counts.C || 0;
    var hyd = counts.H || 0;
    var n = counts.N || 0;
    var x = (counts.F || 0) + (counts.Cl || 0) + (counts.Br || 0)
          + (counts.I || 0);
    var value = (2 * c + 2 + n - hyd - x) / 2;
    return { value: value, whole: value >= 0 && value % 1 === 0 };
  }

  function molarMass(formula) {
    var table = elements();
    var parsed = parseFormula(formula);
    var total = 0;
    var breakdown = [];

    Object.keys(parsed.counts).forEach(function (symbol) {
      var n = parsed.counts[symbol];
      var contribution = table[symbol].weight * n;
      total += contribution;
      breakdown.push({
        symbol: symbol,
        count: n,
        weight: table[symbol].weight,
        contribution: contribution
      });
    });

    breakdown.sort(function (a, b) { return b.contribution - a.contribution; });
    breakdown.forEach(function (row) {
      row.percent = total ? (row.contribution / total) * 100 : 0;
    });

    return {
      total: total,
      breakdown: breakdown,
      counts: parsed.counts,
      charge: parsed.charge
    };
  }

  /* The mass of the single most abundant isotopic species, which is what a
   * mass spectrometer reports as the monoisotopic peak. Distinct from
   * molar mass, which averages over natural abundance, and the difference
   * is not small: glucose is 180.16 by molar mass and 180.063 exact. */
  function monoisotopicMass(formula) {
    var table = elements();
    var parsed = parseFormula(formula);
    var total = 0;

    Object.keys(parsed.counts).forEach(function (symbol) {
      var entry = table[symbol];
      if (!entry.mono) throw new CalcError("NO_STABLE_ISOTOPE", symbol);
      total += entry.mono * parsed.counts[symbol];
    });
    return total;
  }

  /* Isotopic pattern by convolution.
   *
   * Each element contributes a small distribution; the pattern for the
   * whole molecule is those distributions convolved together, once per
   * atom. Peaks below the threshold are dropped at every stage, which
   * keeps the work bounded on large molecules without changing anything
   * the reader would see.
   */
  function isotopicPattern(formula, options) {
    options = options || {};
    var threshold = options.threshold || 1e-4;
    var limit = options.limit || 12;

    var table = elements();
    var parsed = parseFormula(formula);
    var pattern = [[0, 1]];

    Object.keys(parsed.counts).forEach(function (symbol) {
      var entry = table[symbol];
      if (!entry.isotopes) throw new CalcError("NO_STABLE_ISOTOPE", symbol);
      for (var n = 0; n < parsed.counts[symbol]; n++) {
        pattern = prune(convolve(pattern, entry.isotopes), threshold);
      }
    });

    var top = 0;
    pattern.forEach(function (peak) { if (peak[1] > top) top = peak[1]; });

    return pattern
      .map(function (peak) {
        return {
          mass: peak[0],
          abundance: peak[1],
          relative: top ? (peak[1] / top) * 100 : 0
        };
      })
      .filter(function (peak) { return peak.relative >= 0.1; })
      .sort(function (a, b) { return a.mass - b.mass; })
      .slice(0, limit);
  }

  function convolve(a, b) {
    var merged = {};
    a.forEach(function (p) {
      b.forEach(function (q) {
        var mass = p[0] + q[0];
        var key = mass.toFixed(4);
        if (!merged[key]) merged[key] = [mass, 0];
        merged[key][1] += p[1] * q[1];
      });
    });
    return Object.keys(merged).map(function (k) { return merged[k]; });
  }

  function prune(pattern, threshold) {
    var top = 0;
    pattern.forEach(function (p) { if (p[1] > top) top = p[1]; });
    return pattern.filter(function (p) { return p[1] >= top * threshold; });
  }

  /* ---------------------------------------------------------------------
   * Exact rational arithmetic, for balancing
   * ------------------------------------------------------------------- */

  function gcd(a, b) {
    a = Math.abs(a); b = Math.abs(b);
    while (b) { var t = a % b; a = b; b = t; }
    return a || 1;
  }

  function rat(n, d) {
    if (d === 0) throw new CalcError("DIVIDE_BY_ZERO");
    if (d < 0) { n = -n; d = -d; }
    var g = gcd(n, d);
    return { n: n / g, d: d / g };
  }

  function rAdd(a, b) { return rat(a.n * b.d + b.n * a.d, a.d * b.d); }
  function rSub(a, b) { return rat(a.n * b.d - b.n * a.d, a.d * b.d); }
  function rMul(a, b) { return rat(a.n * b.n, a.d * b.d); }
  function rDiv(a, b) {
    if (b.n === 0) throw new CalcError("DIVIDE_BY_ZERO");
    return rat(a.n * b.d, a.d * b.n);
  }

  /* ---------------------------------------------------------------------
   * Equation balancing
   * ------------------------------------------------------------------- */

  /* Balancing is a nullspace problem, and doing it in exact fractions
   * rather than floating point matters: the answer is a set of small
   * integers, and floating point elimination turns those into 2.9999998,
   * which then has to be guessed back into 3. Integers in, integers out,
   * no rounding step anywhere.
   */
  function balance(equation) {
    var sides = equation.split(/->|=>|\u2192|=/);
    if (sides.length !== 2) throw new CalcError("NEEDS_TWO_SIDES");

    var left = splitSide(sides[0]);
    var right = splitSide(sides[1]);
    if (!left.length || !right.length) throw new CalcError("EMPTY_SIDE");

    var species = left.concat(right);
    if (species.length > 12) throw new CalcError("TOO_MANY_SPECIES");

    var parsed = species.map(function (s) { return parseFormula(s).counts; });

    var symbols = [];
    parsed.forEach(function (counts) {
      Object.keys(counts).forEach(function (s) {
        if (symbols.indexOf(s) < 0) symbols.push(s);
      });
    });

    // rows: one per element. Products enter negative.
    var matrix = symbols.map(function (symbol) {
      return parsed.map(function (counts, j) {
        var v = counts[symbol] || 0;
        return rat(j < left.length ? v : -v, 1);
      });
    });

    var coefficients = nullspace(matrix, species.length);

    return {
      reactants: left,
      products: right,
      coefficients: coefficients,
      elements: symbols
    };
  }

  function splitSide(text) {
    return text.split("+").map(function (s) { return s.trim(); })
               .filter(function (s) { return s.length; });
  }

  function nullspace(matrix, width) {
    var rows = matrix.length;
    var pivots = [];
    var r = 0;

    for (var c = 0; c < width && r < rows; c++) {
      var pivot = -1;
      for (var i = r; i < rows; i++) {
        if (matrix[i][c].n !== 0) { pivot = i; break; }
      }
      if (pivot < 0) continue;

      var swap = matrix[r]; matrix[r] = matrix[pivot]; matrix[pivot] = swap;

      var lead = matrix[r][c];
      for (var j = 0; j < width; j++) matrix[r][j] = rDiv(matrix[r][j], lead);

      for (var k = 0; k < rows; k++) {
        if (k === r || matrix[k][c].n === 0) continue;
        var factor = matrix[k][c];
        for (var m = 0; m < width; m++) {
          matrix[k][m] = rSub(matrix[k][m], rMul(factor, matrix[r][m]));
        }
      }
      pivots.push(c);
      r++;
    }

    var free = [];
    for (var col = 0; col < width; col++) {
      if (pivots.indexOf(col) < 0) free.push(col);
    }
    if (free.length === 0) throw new CalcError("NO_SOLUTION");
    if (free.length > 1) throw new CalcError("UNDERDETERMINED");

    var freeCol = free[0];
    var solution = new Array(width);
    solution[freeCol] = rat(1, 1);
    pivots.forEach(function (col, index) {
      solution[col] = rat(-matrix[index][freeCol].n, matrix[index][freeCol].d);
    });

    // scale to the smallest positive integers
    var denominators = solution.map(function (s) { return s.d; });
    var multiplier = denominators.reduce(function (a, b) {
      return a * b / gcd(a, b);
    }, 1);
    var integers = solution.map(function (s) { return s.n * multiplier / s.d; });

    var common = integers.reduce(function (a, b) { return gcd(a, b); },
                                 Math.abs(integers[0]));
    integers = integers.map(function (v) { return v / common; });

    if (integers.some(function (v) { return v < 0; })) {
      integers = integers.map(function (v) { return -v; });
    }
    if (integers.some(function (v) { return v <= 0 || !isFinite(v); })) {
      throw new CalcError("NO_SOLUTION");
    }
    return integers;
  }

  /* ---------------------------------------------------------------------
   * Acids, bases, buffers
   * ------------------------------------------------------------------- */

  function requirePositive(value, what) {
    if (!(value > 0)) throw new CalcError("MUST_BE_POSITIVE", what);
    return value;
  }

  var pH = {
    strongAcid: function (c) {
      return -Math.log10(requirePositive(c, "concentration"));
    },
    strongBase: function (c) {
      return 14 + Math.log10(requirePositive(c, "concentration"));
    },
    /* The usual approximation, valid while dissociation stays small. It
     * is reported alongside the fraction dissociated so the reader can see
     * when it has stopped being valid rather than trusting it blindly. */
    weakAcid: function (c, pKa) {
      requirePositive(c, "concentration");
      var ka = Math.pow(10, -pKa);
      var h = Math.sqrt(ka * c);
      return { pH: -Math.log10(h), dissociated: (h / c) * 100 };
    },
    weakBase: function (c, pKb) {
      requirePositive(c, "concentration");
      var kb = Math.pow(10, -pKb);
      var oh = Math.sqrt(kb * c);
      return { pH: 14 + Math.log10(oh), dissociated: (oh / c) * 100 };
    },
    buffer: function (pKa, base, acid) {
      requirePositive(base, "base");
      requirePositive(acid, "acid");
      return pKa + Math.log10(base / acid);
    }
  };

  /* ---------------------------------------------------------------------
   * Stoichiometry
   * ------------------------------------------------------------------- */

  /* Each reagent supplies mass, molar mass and its stoichiometric
   * coefficient. Whichever gives the fewest equivalents runs out first. */
  function limitingReagent(reagents) {
    if (!reagents || reagents.length < 2) throw new CalcError("NEED_TWO_REAGENTS");

    var rows = reagents.map(function (r) {
      requirePositive(r.mass, "mass");
      requirePositive(r.molarMass, "molar mass");
      var coefficient = r.coefficient || 1;
      requirePositive(coefficient, "coefficient");
      var moles = r.mass / r.molarMass;
      return {
        name: r.name,
        moles: moles,
        coefficient: coefficient,
        equivalents: moles / coefficient
      };
    });

    var least = rows[0];
    rows.forEach(function (row) {
      if (row.equivalents < least.equivalents) least = row;
    });
    rows.forEach(function (row) {
      row.limiting = row === least;
      row.excess = (row.equivalents - least.equivalents) * row.coefficient;
    });

    return { rows: rows, limiting: least, extent: least.equivalents };
  }

  function atomEconomy(massOfDesiredProduct, massOfAllReactants) {
    requirePositive(massOfDesiredProduct, "product mass");
    requirePositive(massOfAllReactants, "reactant mass");
    return (massOfDesiredProduct / massOfAllReactants) * 100;
  }

  /* Waste per unit product. Unlike atom economy it counts solvent and
   * everything else that leaves the plant, which is why the two numbers
   * disagree so sharply for real processes. */
  function eFactor(massOfWaste, massOfProduct) {
    requirePositive(massOfProduct, "product mass");
    if (massOfWaste < 0) throw new CalcError("MUST_BE_POSITIVE", "waste mass");
    return massOfWaste / massOfProduct;
  }

  /* ---------------------------------------------------------------------
   * Dilution
   * ------------------------------------------------------------------- */

  /* C1.V1 = C2.V2, solved for whichever term is left out. Exactly one of
   * the four must be missing. */
  function dilution(values) {
    var keys = ["c1", "v1", "c2", "v2"];
    var missing = keys.filter(function (k) {
      return values[k] === null || values[k] === undefined || values[k] === "";
    });
    if (missing.length !== 1) throw new CalcError("LEAVE_ONE_BLANK");

    var v = {};
    keys.forEach(function (k) {
      if (missing.indexOf(k) < 0) v[k] = requirePositive(Number(values[k]), k);
    });

    var answer;
    switch (missing[0]) {
      case "c1": answer = v.c2 * v.v2 / v.v1; break;
      case "v1": answer = v.c2 * v.v2 / v.c1; break;
      case "c2": answer = v.c1 * v.v1 / v.v2; break;
      default: answer = v.c1 * v.v1 / v.c2; break;
    }
    return { solvedFor: missing[0], value: answer };
  }

  function serialDilution(startConcentration, factor, steps) {
    requirePositive(startConcentration, "concentration");
    if (!(factor > 1)) throw new CalcError("FACTOR_ABOVE_ONE");
    if (!(steps >= 1)) throw new CalcError("NEED_ONE_STEP");

    var out = [];
    var c = startConcentration;
    for (var i = 0; i <= steps; i++) {
      out.push({ step: i, concentration: c, fold: Math.pow(factor, i) });
      c = c / factor;
    }
    return out;
  }

  /* ---------------------------------------------------------------------
   * Units
   * ------------------------------------------------------------------- */

  var temperature = {
    toKelvin: function (value, from) {
      if (from === "K") return value;
      if (from === "C") return value + 273.15;
      if (from === "F") return (value - 32) * 5 / 9 + 273.15;
      throw new CalcError("UNKNOWN_UNIT", from);
    },
    fromKelvin: function (kelvin, to) {
      if (to === "K") return kelvin;
      if (to === "C") return kelvin - 273.15;
      if (to === "F") return (kelvin - 273.15) * 9 / 5 + 32;
      throw new CalcError("UNKNOWN_UNIT", to);
    },
    convert: function (value, from, to) {
      var k = temperature.toKelvin(value, from);
      if (k < 0) throw new CalcError("BELOW_ABSOLUTE_ZERO");
      return temperature.fromKelvin(k, to);
    }
  };

  // relative to the pascal
  var PRESSURE = {
    Pa: 1, kPa: 1e3, bar: 1e5, atm: 101325,
    mmHg: 133.322387415, torr: 133.322368421, psi: 6894.757293168
  };

  function convertPressure(value, from, to) {
    if (!PRESSURE[from]) throw new CalcError("UNKNOWN_UNIT", from);
    if (!PRESSURE[to]) throw new CalcError("UNKNOWN_UNIT", to);
    return value * PRESSURE[from] / PRESSURE[to];
  }

  root.PYTHIA = root.PYTHIA || {};
  root.PYTHIA.calc = {
    CalcError: CalcError,
    parseFormula: parseFormula,
    molarMass: molarMass,
    degreesOfUnsaturation: degreesOfUnsaturation,
    monoisotopicMass: monoisotopicMass,
    isotopicPattern: isotopicPattern,
    balance: balance,
    pH: pH,
    limitingReagent: limitingReagent,
    atomEconomy: atomEconomy,
    eFactor: eFactor,
    dilution: dilution,
    serialDilution: serialDilution,
    temperature: temperature,
    convertPressure: convertPressure,
    pressureUnits: Object.keys(PRESSURE)
  };
})(typeof window !== "undefined" ? window : this);
