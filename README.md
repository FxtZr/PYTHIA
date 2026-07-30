# PYTHIA

**Chemistry that shows its working.**

Molecular structure in three dimensions, stereochemistry, IUPAC naming,
reaction mechanisms, metabolic pathways and spectroscopy — entirely
offline.

Nothing is displayed here that the build could not verify. Where something
could not be checked, the program says so instead of guessing.

Open `index.html` in a browser. That is the whole installation. No server,
no build step, no accounts, no network. Nothing leaves the machine because
nothing in it can send anything anywhere.

---

## What it contains

**Explore** — 94 molecules, each drawn twice: flat on the left, in space on
the right. Point at an atom in either view and it lights up in the other.
That link is the point of the section, because the thing a student has to
build is the habit of reading a wedge as depth.

**Stereochemistry** — nine lessons: what chirality is, how to find a
stereocentre, how to rank substituents, how to assign R and S, enantiomers
against diastereomers, meso compounds, geometry at a double bond,
conformation against configuration, and what this costs when it goes wrong.
Every molecule mentioned is drawn where it is mentioned.

**Naming** — the IUPAC rules in the order they are applied, the seniority
table that settles most hard cases, and fourteen names taken apart piece by
piece. Each piece carries its own explanation.

**Mechanisms** — seven reactions with electron-pushing arrows. A full
arrowhead moves a pair, a half head moves one. The rule governing the
attack is stated before the structures, because twenty mechanisms learned
as twenty separate stories is nothing learned at all.

**Pathways** — six metabolic pathways, step by step, with enzymes, EC
numbers, cofactors, reversibility and control points. Deliberately a
different kind of object from the mechanisms: no arrows are pushed here.

**Spectroscopy** — infrared, proton and carbon-13 NMR, and mass
spectrometry, as correlation tables with the ranges drawn on a scale rather
than listed. Then six structure elucidation problems: a molecular formula
and three sets of data, with every signal accounted for in the reasoning.
Two of the six share a formula and a proton count and resolve to different
compounds, which is the exercise worth doing twice.

**Calculators** — ten tools: molar mass, monoisotopic mass, isotope
pattern, equation balancing, limiting reagent, atom economy and E factor,
pH, buffers, dilution, and unit conversion.

**Glossary** — 69 terms with live cross-references, pairing the ones that
are routinely confused with each other.

---

## What it does not do

**The library is fixed.** Structures are computed when the data files are
built, not in the browser, so a molecule that is not in `data/molecules.js`
cannot be shown. Adding one means adding a line to `tools/library.py` and
rebuilding. There is no way to type in an arbitrary structure and see it
drawn; doing that would need a cheminformatics engine in the browser, which
is a deliberate future option rather than an oversight. See *Extending*.

**Seven stereocentres have no priority walkthrough.** All 97 stereocentres
carry a computed R or S descriptor. Eighty-eight of them also get a
step-by-step account of how the four substituents were ranked. The
remaining nine sit in rings and need CIP rules beyond atomic number, which
the ranking engine here does not implement. Rather than print an
explanation that might be wrong, it prints none and says so.

**Transition states are not drawn.** A SMILES string cannot express a
partial bond, and rendering a five-coordinate carbon as though it were a
real species would teach something false. Where the transition state
matters it is described in the step text and the reactant structure carries
partial-charge labels instead.

**No spectra are reproduced.** The spectroscopy section is correlation
tables and reasoning, not a spectral library. That was a choice, not a
limitation: a real spectrum pulled from a repository is noisy and
unannotated, and teaches less than a table with every band explained. If a
network lookup layer is ever added, MassBank Europe is the source to use —
it is CC BY 4.0. SDBS is not, and its terms forbid both redistribution and
automated access.

**Geometry is computed, not measured.** Three-dimensional coordinates come
from distance-geometry embedding followed by force-field optimisation. They
are good enough to see that two enantiomers do not superimpose. They are
not crystallographic data.

This is a tool for studying chemistry. It is not a substitute for a primary
source or for a supervisor's judgement.

---

## Repository layout

```
index.html            open this
css/tokens.css        design tokens, shared with sibling projects
css/pythia.css        layout specific to this program
js/depict.js          2D structure renderer, no dependencies
js/viewer3d.js        wrapper over 3Dmol.js
js/calc.js            calculation engine, no DOM
js/app.js             shell and routing
js/views/             one file per section
data/                 generated; do not edit by hand
tools/                the generators and the source data they read
tests/                run with node, no dependencies
assets/vendor/        3Dmol.js, vendored with its licence
assets/fonts/         IBM Plex Mono, vendored with its licence
```

Everything under `data/` is generated. Every file there carries a header
saying so and naming the script that wrote it.

---

## Building the data

Requires Python 3 with RDKit.

```
pip install rdkit
cd tools
python3 build_all.py
```

Each generator refuses to write output it cannot verify. That is the design
principle the whole project rests on, and it is worth stating plainly
because it explains a number of decisions that would otherwise look
fussy:

- **Molecules.** A name that declares a configuration is checked against the
  configuration the structure actually produces. Writing `[C@@H]` where
  `[C@H]` was meant is invisible to review and inverts the compound; this
  check catches it. The priority ranking is derived independently and used
  to re-derive R or S from the geometry; where that disagrees with the
  reference implementation, the walkthrough is withheld.
- **Mechanisms.** Arrows are anchored to atom map numbers in the SMILES, not
  to atom indices. Every map number an arrow refers to must exist, or the
  build fails. A mistyped arrow index would otherwise draw nothing, or
  point somewhere wrong, in silence.
- **Nomenclature.** The pieces of a decomposed name, concatenated, must
  reproduce the molecule's name character for character.
- **Lessons and glossary.** Every molecule cited must exist; every
  cross-reference must resolve.
- **Spectroscopy.** Each elucidation problem states a molecular formula
  and a number of proton signals. Both are recomputed from the answer
  molecule — the formula by counting atoms, the signal count from the
  molecule's symmetry classes — and must match. A problem whose formula
  does not belong to its answer is unsolvable, and reading the rendered
  page will never reveal it.
- **Elements.** Isotope abundances must sum to 1 within 5e-4.

## Running the tests

```
node tests/calc.test.js
```

No framework and no dependencies. Expected values come from standard
references and worked examples, not from a previous run of this code, which
would only prove it consistent with itself. Exits non-zero on failure.

---

## Extending

**Adding a molecule** is one entry in `tools/library.py` and a rebuild.
Declare `expect` — the stereodescriptors the structure must produce — and
let the build check you rather than trusting what you typed. Around 2.5 kB
per molecule, so the library can grow by an order of magnitude without any
change in architecture.

**Adding a mechanism, lesson, pathway or glossary term** works the same
way: edit the corresponding file in `tools/`, rebuild, and the checks run.

**Arbitrary structure input** would mean vendoring RDKit compiled to
WebAssembly, roughly 8 MB. It is worth doing as an optional layer: present
the file and a structure-input mode appears, omit it and everything else
behaves identically. Nobody should pay 8 MB to read a lesson. What is not
worth doing is hand-writing a SMILES parser and stereo perception in
JavaScript. Correctness matters most exactly there, and the checks
described above exist because that is precisely where mistakes were made
during development, twice, with a reference implementation available for
comparison.

---

## Still to verify

Two classes of data in this repository are correct as far as the author
knows and have not been checked against an authority:

- **DOIs** are deliberately absent from `tools/sources.py`. A wrong DOI is
  worse than no DOI. Add them in one pass with network access.
- **EC numbers** in `tools/pathways.py` are checked for shape — four
  dot-separated fields, first between 1 and 7 — which catches a typo but
  not a wrong assignment. Confirm them against ExplorEnz.

Record either pass in `SOURCES.md` when done.

---

## Contact

- Site — <https://FxtZr.com/>
- GitHub — <https://github.com/FxtZr/>
- YouTube — <https://www.youtube.com/@Fxtzr>
- X — <https://x.com/Fxt_Zr>

Corrections to the chemistry are the most welcome kind of message. Open an
issue on GitHub rather than sending them elsewhere, so the discussion and
the fix stay attached to the code.

## Licence

MIT, see `LICENSE`.

Bundled third-party components keep their own licences:

- **3Dmol.js** — BSD 3-Clause, `assets/vendor/3Dmol-LICENSE.txt`
- **IBM Plex Mono** — SIL Open Font Licence 1.1, `assets/fonts/OFL.txt`

Sources for the chemistry are listed in `SOURCES.md` and in the footer of
the program itself.
