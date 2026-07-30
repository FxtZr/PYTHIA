#!/usr/bin/env python3
"""Build the PYTHIA mechanism data.

Turns the mapped SMILES in mechanisms.py into drawable structures with
their arrows resolved to atom indices.

Two checks make this safe to hand-author:

  * every map number an arrow refers to must exist in that step's
    structure, or the build fails. A typo in an arrow is otherwise
    invisible: it would silently draw nothing, or point somewhere wrong.
  * every step's structure must parse and sanitise. Radicals and charged
    species are accepted; nonsense is not.

Output: ../data/mechanisms.js
"""

import json
import os
import sys

from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, rdMolDescriptors
from rdkit.Geometry import Point3D

from mechanisms import MECHANISMS
from sources import SOURCES, resolve

RDLogger.DisableLog("rdApp.*")

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "mechanisms.js")

WEDGE = {Chem.BondDir.BEGINWEDGE: "wedge", Chem.BondDir.BEGINDASH: "dash"}

FRAGMENT_GAP = 2.4       # in RDKit layout units, roughly 1.6 bond lengths


def parse(smiles):
    """Parse a mapped SMILES, keeping standalone hydrogens.

    removeHs is off because a step may need to point an arrow at a specific
    hydrogen, as in the addition of H-Br. Hydrogens written inside brackets
    stay implicit and are not affected.
    """
    params = Chem.SmilesParserParams()
    params.removeHs = False
    mol = Chem.MolFromSmiles(smiles, params)
    if mol is None:
        raise ValueError("SMILES did not parse: %s" % smiles)
    return mol


def spread_fragments(mol, gap=FRAGMENT_GAP):
    """Lay separate molecules out in a row instead of on top of each other.

    RDKit's 2D layout treats a dot-separated SMILES as one drawing and can
    let the pieces overlap. Each fragment is measured and shifted so they
    sit side by side on a common centre line, which is how a reaction is
    written on paper.
    """
    conf = mol.GetConformer()
    cursor = 0.0
    for frag in Chem.GetMolFrags(mol):
        xs = [conf.GetAtomPosition(i).x for i in frag]
        ys = [conf.GetAtomPosition(i).y for i in frag]
        dx = cursor - min(xs)
        cy = (min(ys) + max(ys)) / 2.0
        for i in frag:
            p = conf.GetAtomPosition(i)
            conf.SetAtomPosition(i, Point3D(p.x + dx, p.y - cy, 0.0))
        cursor += (max(xs) - min(xs)) + gap


def depiction(mol):
    atoms = []
    conf = mol.GetConformer()
    for atom in mol.GetAtoms():
        p = conf.GetAtomPosition(atom.GetIdx())
        entry = {
            "el": atom.GetSymbol(),
            "x": round(p.x, 4),
            "y": round(p.y, 4),
            "nH": atom.GetTotalNumHs(),
            "q": atom.GetFormalCharge(),
        }
        if atom.GetNumRadicalElectrons():
            entry["rad"] = atom.GetNumRadicalElectrons()
        atoms.append(entry)

    bonds = []
    for bond in mol.GetBonds():
        order = 1 if bond.GetIsAromatic() else int(bond.GetBondTypeAsDouble())
        entry = {"a": bond.GetBeginAtomIdx(), "b": bond.GetEndAtomIdx(),
                 "o": order}
        d = WEDGE.get(bond.GetBondDir())
        if d:
            entry["w"] = d
        bonds.append(entry)

    return {"atoms": atoms, "bonds": bonds}


def resolve_ref(ref, mapping, where):
    """Turn a map-number reference into an index reference."""
    if isinstance(ref, (list, tuple)):
        missing = [m for m in ref if m not in mapping]
        if missing:
            raise KeyError("%s refers to map number(s) %s, which are not in "
                           "this step" % (where, missing))
        return {"bond": [mapping[m] for m in ref]}
    if ref not in mapping:
        raise KeyError("%s refers to map number %s, which is not in this step"
                       % (where, ref))
    return {"atom": mapping[ref]}


def build_step(step, mech_id, ordinal):
    where = "%s step %d" % (mech_id, ordinal)
    mol = parse(step.smiles)

    mapping = {}
    for atom in mol.GetAtoms():
        n = atom.GetAtomMapNum()
        if n:
            if n in mapping:
                raise ValueError("%s: map number %d used twice" % (where, n))
            mapping[n] = atom.GetIdx()
            atom.SetAtomMapNum(0)          # never drawn

    AllChem.Compute2DCoords(mol)
    spread_fragments(mol)

    arrows = []
    for arrow in step.arrows:
        arrows.append({
            "from": resolve_ref(arrow["from"], mapping, where + " arrow"),
            "to": resolve_ref(arrow["to"], mapping, where + " arrow"),
            "bow": arrow["bow"],
            "kind": arrow["kind"],
        })

    lone = {}
    for m, count in (step.lone or {}).items():
        lone[str(resolve_ref(m, mapping, where + " lone pair")["atom"])] = count

    labels = []
    for lab in (step.labels or ()):
        labels.append({
            "atom": resolve_ref(lab["atom"], mapping, where + " label")["atom"],
            "text": lab["text"],
        })

    return {
        "title": step.title,
        "text": step.text,
        "formula": rdMolDescriptors.CalcMolFormula(mol),
        "d2": depiction(mol),
        "arrows": arrows,
        "lonePairs": lone,
        "labels": labels,
    }


def main():
    out = []
    failures = []

    for mech in MECHANISMS:
        steps = []
        try:
            for i, step in enumerate(mech.steps, start=1):
                steps.append(build_step(step, mech.id, i))
        except (ValueError, KeyError) as exc:
            failures.append((mech.id, str(exc)))
            continue

        out.append({
            "id": mech.id,
            "name": mech.name,
            "family": mech.family,
            "summary": mech.summary,
            "attack": mech.attack,
            "steps": steps,
            "sources": resolve(mech.sources),
        })

    if failures:
        print("FAILED:")
        for mid, why in failures:
            print("  -", mid, ":", why)
        return 1

    payload = json.dumps(out, ensure_ascii=True, separators=(",", ":"))
    with open(OUT, "w", encoding="ascii") as fh:
        fh.write("/* PYTHIA reaction mechanisms.\n"
                 "   Generated by tools/build_mechanisms.py -- "
                 "do not edit by hand.\n"
                 "   %d mechanisms. */\n" % len(out))
        fh.write("window.PYTHIA_MECHANISMS = ")
        fh.write(payload)
        fh.write(";\n")

    total_steps = sum(len(m["steps"]) for m in out)
    total_arrows = sum(len(s["arrows"]) for m in out for s in m["steps"])
    print("built %d mechanisms, %d steps, %d arrows -> %s (%.0f kB)"
          % (len(out), total_steps, total_arrows, os.path.relpath(OUT),
             os.path.getsize(OUT) / 1024))

    fishhooks = sum(1 for m in out for s in m["steps"]
                    for a in s["arrows"] if a["kind"] == "single")
    print("arrow heads: %d full (electron pair), %d half (single electron)"
          % (total_arrows - fishhooks, fishhooks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
