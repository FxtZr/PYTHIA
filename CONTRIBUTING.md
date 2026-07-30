# Contributing

Contributions are welcome, particularly corrections. If something here
teaches a student something false, that is the most serious kind of bug
this project can have, and a report costs you five minutes and saves
somebody an exam question.

## Before anything else

```
cd tools && python3 build_all.py
node tests/calc.test.js
```

Both must pass. The generators refuse to write output they cannot verify,
so a failing build is usually telling you something true.

## Where to edit

Nothing under `data/` — it is all generated, and every file there says so
in its header. Edit the corresponding file in `tools/` and rebuild.

| To change | Edit |
| --- | --- |
| A molecule | `tools/library.py` |
| A reaction mechanism | `tools/mechanisms.py` |
| A stereochemistry lesson | `tools/lessons.py` |
| A naming rule or worked name | `tools/nomenclature.py` |
| A metabolic pathway | `tools/pathways.py` |
| A glossary term | `tools/glossary.py` |
| A source citation | `tools/sources.py` |

## Adding a molecule

One entry in `tools/library.py`:

```python
M("lactic-acid-s", "C[C@H](O)C(=O)O",
  "(S)-lactic acid", "L-(+)-lactic acid", "chirality",
  "What your muscles accumulate under anaerobic effort.",
  expect="S"),
```

**Always declare `expect`.** It is the multiset of stereodescriptors the
structure must produce, sorted: `"S"`, `"RS"`, `"ZZZ"`, or `""` to assert
that there are none. The build compares it against what the structure
actually gives and fails on disagreement.

This is not bureaucracy. Inside `[C@@H]`, the configuration depends on the
order the neighbours are written, so `C[C@@H](N)C(=O)O` and
`C[C@@H](C(=O)O)N` are opposite compounds. Eight entries were wrong on the
first pass of this library, including both alanines and both ibuprofens,
and every one was caught by this check rather than by reading.

The `note` field is for the thing that is not obvious from the picture.
"An amino acid" is not worth writing; "the only R in the L series, purely
because sulfur outranks the carboxyl carbon" is.

## Adding a mechanism

Arrows are anchored to atom map numbers in the SMILES, never to atom
indices:

```python
Step(
    smiles="[OH-:1].[CH3:2][Br:3]",
    arrows=(A(1, 2, bow=0.45), A((2, 3), 3, bow=-0.35)),
    lone={1: 3},
    ...
)
```

An integer means an atom, a tuple means the bond between two atoms. The
build resolves map numbers to whatever indices RDKit assigns and fails if
one does not exist. Hand-written indices break silently the moment a
structure changes.

Use `kind="single"` for fishhooks and nothing else. A full head means a
pair moved; a half head means one electron did. Getting that wrong states
something false about the chemistry.

Do not try to draw a transition state. SMILES cannot express a partial
bond, and a five-coordinate carbon drawn as a real species teaches an
error. Describe it in the step text instead.

## Writing prose

English only, and plainly. The reader is someone who has met the word and
not yet got hold of it.

Say the thing that is not obvious. Where two ideas are routinely confused,
pair them and say what the difference is — that pairing is worth more than
either definition alone.

No claim of clinical or diagnostic use, anywhere. This is a tool for
studying chemistry.

## Sources

If you add a factual claim, add its source key to the relevant entry. If
the source is not in `tools/sources.py`, add it there first, with its
licence and whether data from it ships in the repository.

**Check the licence before adding a data source.** KEGG is the obvious
trap: it is the best known pathway database and its terms forbid
redistribution. Anything with comparable restrictions cannot be used here
regardless of how convenient it is.

No DOIs. A wrong DOI is worse than none, and they cannot be verified from
an offline build. There is one pass reserved for that, tracked in
`SOURCES.md`.

## Style

JavaScript: plain ES5-compatible scripts, no modules, no build step, no
framework. This is deliberate. Modules and `fetch()` are blocked under
`file://`, and the program must open by double-clicking `index.html`. That
constraint is also what should still make it work in ten years.

No `localStorage`, no cookies, no network calls, no analytics. The program
sends nothing anywhere and should stay that way.

CSS: colours and type sizes live in `css/tokens.css` and nowhere else. If
you need a value in two places, it belongs there.

Comments explain why, not what. A comment restating the code is noise; a
comment recording why an obvious-looking approach was rejected is the most
useful thing in the file.

## Reporting an error in the chemistry

Please include the molecule id, pathway or term, what the program says,
what it should say, and a source. Chemistry corrections take priority over
everything else here.
