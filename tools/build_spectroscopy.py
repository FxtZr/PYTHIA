#!/usr/bin/env python3
"""Build the PYTHIA spectroscopy data.

Three checks, and the first two are the reason this file exists rather
than the data being written straight into JavaScript.

  * Every elucidation problem states a molecular formula. It is recomputed
    from the answer molecule and must match. A problem whose formula does
    not belong to its answer is unsolvable, and no amount of reading the
    rendered page reveals that.
  * Every problem states how many proton signals appear. That count is
    recomputed from the molecule's symmetry classes and must match. This
    catches the commonest authoring error by far: forgetting that two
    groups are equivalent, or that two apparently equivalent groups are
    not.
  * Ranges must be the right way round and inside the physically
    meaningful window.

Output: ../data/spectroscopy.js
"""

import json
import os
import sys

from rdkit import Chem, RDLogger
from rdkit.Chem import rdMolDescriptors

from library import LIBRARY
from sources import resolve
from spectroscopy import (C_REGIONS, FINGERPRINT_NOTE, FRAGMENTATIONS,
                          H_REGIONS, IR_BANDS, KEY_IONS, MULTIPLICITY_NOTE,
                          NEUTRAL_LOSSES, NITROGEN_RULE, PROBLEMS,
                          SOURCES as SPEC_SOURCES)

RDLogger.DisableLog("rdApp.*")

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "spectroscopy.js")

IR_WINDOW = (400, 4000)      # cm-1, the range an ordinary instrument covers
H_WINDOW = (-1.0, 15.0)      # ppm
C_WINDOW = (0.0, 230.0)      # ppm


def proton_signals(smiles):
    """How many distinct proton environments the structure has.

    Counted by canonical symmetry class with ties left unbroken, so
    genuinely equivalent hydrogens fall into one class. This is the
    idealised count: it assumes free rotation and ignores diastereotopic
    protons, which is the same assumption a textbook problem makes.
    """
    mol = Chem.AddHs(Chem.MolFromSmiles(smiles))
    ranks = list(Chem.CanonicalRankAtoms(mol, breakTies=False))
    classes = set(ranks[a.GetIdx()] for a in mol.GetAtoms()
                  if a.GetAtomicNum() == 1)
    return len(classes)


def degrees_of_unsaturation(formula_counts):
    c = formula_counts.get("C", 0)
    h = formula_counts.get("H", 0)
    n = formula_counts.get("N", 0)
    x = sum(formula_counts.get(s, 0) for s in ("F", "Cl", "Br", "I"))
    return (2 * c + 2 + n - h - x) // 2


def counts_from_mol(smiles):
    mol = Chem.AddHs(Chem.MolFromSmiles(smiles))
    out = {}
    for atom in mol.GetAtoms():
        out[atom.GetSymbol()] = out.get(atom.GetSymbol(), 0) + 1
    return out


def main():
    by_id = {entry.id: entry for entry in LIBRARY}
    problems_out = []
    problems = []

    for band in IR_BANDS:
        if band.low >= band.high:
            problems.append("IR band %s %s: low is not below high"
                            % (band.group, band.bond))
        if band.low < IR_WINDOW[0] or band.high > IR_WINDOW[1]:
            problems.append("IR band %s %s: outside %d-%d cm-1"
                            % (band.group, band.bond) + str(IR_WINDOW))

    for region, window, label in ([(r, H_WINDOW, "1H") for r in H_REGIONS]
                                  + [(r, C_WINDOW, "13C") for r in C_REGIONS]):
        if region.low >= region.high:
            problems.append("%s region %s: low is not below high"
                            % (label, region.environment))
        if region.low < window[0] or region.high > window[1]:
            problems.append("%s region %s: outside the usual window"
                            % (label, region.environment))

    for p in PROBLEMS:
        entry = by_id.get(p.answer)
        if entry is None:
            problems.append("problem %s: answer '%s' is not in the library"
                            % (p.id, p.answer))
            continue

        mol = Chem.MolFromSmiles(entry.smiles)
        real_formula = rdMolDescriptors.CalcMolFormula(mol)
        if real_formula != p.formula:
            problems.append("problem %s: states %s but %s is %s"
                            % (p.id, p.formula, p.answer, real_formula))
            continue

        real_signals = proton_signals(entry.smiles)
        if real_signals != p.signals:
            problems.append("problem %s: states %d proton signal(s) but %s "
                            "has %d distinct environments"
                            % (p.id, p.signals, p.answer, real_signals))
            continue

        if len(p.nmr) != p.signals:
            problems.append("problem %s: %d signals declared but %d listed"
                            % (p.id, p.signals, len(p.nmr)))
            continue

        counts = counts_from_mol(entry.smiles)
        problems_out.append({
            "id": p.id,
            "formula": p.formula,
            "answer": p.answer,
            "answerName": entry.name,
            "signals": p.signals,
            "unsaturation": degrees_of_unsaturation(counts),
            "ir": list(p.ir),
            "nmr": list(p.nmr),
            "ms": list(p.ms),
            "reasoning": p.reasoning,
        })

    if problems:
        print("FAILED:")
        for msg in problems:
            print("  -", msg)
        return 1

    def band(b):
        return {"group": b.group, "bond": b.bond, "low": b.low, "high": b.high,
                "intensity": b.intensity, "shape": b.shape, "note": b.note}

    def region(r):
        return {"environment": r.environment, "low": r.low, "high": r.high,
                "note": r.note}

    payload = {
        "ir": [band(b) for b in IR_BANDS],
        "fingerprint": FINGERPRINT_NOTE,
        "proton": [region(r) for r in H_REGIONS],
        "carbon": [region(r) for r in C_REGIONS],
        "multiplicity": MULTIPLICITY_NOTE,
        "losses": [{"mass": l.mass, "fragment": l.fragment,
                    "origin": l.origin, "note": l.note}
                   for l in NEUTRAL_LOSSES],
        "ions": [{"mass": l.mass, "fragment": l.fragment,
                  "origin": l.origin, "note": l.note} for l in KEY_IONS],
        "fragmentations": [{"name": r.name, "requires": r.requires,
                            "gives": r.gives, "note": r.note}
                           for r in FRAGMENTATIONS],
        "nitrogenRule": NITROGEN_RULE,
        "problems": problems_out,
        "sources": resolve(SPEC_SOURCES),
    }

    with open(OUT, "w", encoding="ascii") as fh:
        fh.write("/* PYTHIA spectroscopy.\n"
                 "   Generated by tools/build_spectroscopy.py -- "
                 "do not edit by hand.\n"
                 "   Correlation tables only. No spectra are reproduced. */\n")
        fh.write("window.PYTHIA_SPECTROSCOPY = ")
        fh.write(json.dumps(payload, ensure_ascii=True,
                            separators=(",", ":")))
        fh.write(";\n")

    print("built %d IR bands, %d proton regions, %d carbon regions, "
          "%d losses, %d rules, %d problems -> %s (%.0f kB)"
          % (len(IR_BANDS), len(H_REGIONS), len(C_REGIONS),
             len(NEUTRAL_LOSSES), len(FRAGMENTATIONS), len(problems_out),
             os.path.relpath(OUT), os.path.getsize(OUT) / 1024))
    print("every problem's formula and proton count match its answer")
    return 0


if __name__ == "__main__":
    sys.exit(main())
