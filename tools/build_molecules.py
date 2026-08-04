#!/usr/bin/env python3
"""Build the PYTHIA molecule library.

Reads the curated molecule table below, and for each entry emits:

  * 2D depiction coordinates with wedge/hash bond directions
  * 3D coordinates with explicit hydrogens (MMFF-optimised)
  * CIP stereodescriptors from RDKit's full CIP labeller
  * a step-by-step substituent priority ranking for each stereocentre,
    derived independently and then cross-checked against RDKit

The cross-check is the point. The ranking engine here implements CIP
rules 1a and 1b (atomic number over a hierarchical digraph, with
duplicate atoms for multiple bonds and ring closures). It does not
implement rules 2-5. Rather than silently emit a ranking that might be
wrong, the script re-derives R/S from the 3D geometry using its own
ranking and compares that against RDKit's authoritative label. A centre
whose derived label disagrees is emitted with its label but WITHOUT a
walkthrough, and is reported at the end. Nothing unverified is shown to
the reader as an explanation.

Output: ../data/molecules.js  (a plain script assigning a global, so the
program runs from file:// without a server)

Usage: python3 build_molecules.py
"""

import json
import re
import math
import os
import sys

from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, Descriptors, rdCIPLabeler, rdMolDescriptors

RDLogger.DisableLog("rdApp.*")

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "molecules.js")

# --------------------------------------------------------------------------
# Curated library
# --------------------------------------------------------------------------
# group: which teaching section the molecule primarily serves
# note:  one sentence shown under the structure. Written for a reader who
#        is learning, not for someone who already knows the answer.

from library import LIBRARY, M  # noqa: E402
from library import DATASET_SOURCES  # noqa: E402
from sources import SOURCES, resolve  # noqa: E402


# --------------------------------------------------------------------------
# CIP priority ranking (rules 1a and 1b only, self-validated downstream)
# --------------------------------------------------------------------------

class Node:
    """A node in the hierarchical digraph rooted at a stereocentre."""
    __slots__ = ("z", "atom_idx", "dup", "kids", "_built")

    def __init__(self, z, atom_idx=None, dup=False):
        self.z = z
        self.atom_idx = atom_idx
        self.dup = dup          # duplicate (phantom) atom: no substituents
        self.kids = None
        self._built = False


MAX_DEPTH = 12


def build_branch(mol, start_idx, parent_idx):
    """Expand the CIP hierarchical digraph branch rooted at start_idx."""
    node = Node(mol.GetAtomWithIdx(start_idx).GetAtomicNum(), start_idx)
    _expand(mol, node, parent_idx, [parent_idx, start_idx], 0)
    return node


def _expand(mol, node, parent_idx, path, depth):
    """Attach node's substituents.

    Two details carry all the weight here, and both are easy to get wrong:

      * A multiple bond contributes (order - 1) duplicate atoms of the
        partner. This applies to the bond back to the parent as well, which
        is why a carbonyl oxygen carries a duplicate carbon. Omit it and
        every C=O ranks below every C-OH.
      * Re-entering an atom already on the path closes a ring. The branch
        terminates there with a duplicate whose own substituents are
        phantoms, so the digraph stays finite.
    """
    if node.dup or depth >= MAX_DEPTH:
        node.kids = []
        return node
    atom = mol.GetAtomWithIdx(node.atom_idx)
    kids = []
    for bond in atom.GetBonds():
        nbr = bond.GetOtherAtomIdx(node.atom_idx)
        z = mol.GetAtomWithIdx(nbr).GetAtomicNum()
        extra = int(round(bond.GetBondTypeAsDouble())) - 1
        if bond.GetBondType() == Chem.BondType.AROMATIC:
            extra = 0
        if nbr != parent_idx:
            if nbr in path:
                kids.append(Node(z, nbr, dup=True))
            else:
                child = Node(z, nbr)
                _expand(mol, child, node.atom_idx, path + [nbr], depth + 1)
                kids.append(child)
        for _ in range(extra):
            kids.append(Node(z, nbr, dup=True))
    for _ in range(atom.GetTotalNumHs()):
        kids.append(Node(1, None, dup=True))
    node.kids = kids
    return node


def cmp_nodes(a, b, depth=0):
    """Compare two branches. >0 if a outranks b, <0 if b outranks a, 0 if tied."""
    if a.z != b.z:
        return a.z - b.z
    if depth >= MAX_DEPTH:
        return 0
    ka = sorted(a.kids or [], key=lambda n: _key(n, depth + 1), reverse=True)
    kb = sorted(b.kids or [], key=lambda n: _key(n, depth + 1), reverse=True)
    for x, y in zip(ka, kb):
        c = cmp_nodes(x, y, depth + 1)
        if c:
            return c
    if len(ka) != len(kb):
        return len(ka) - len(kb)
    return 0


import functools


def _key(node, depth):
    return functools.cmp_to_key(lambda p, q: cmp_nodes(p, q, depth))(node)


def branch_profile(node, spheres=4):
    """Atomic-number profile per sphere, for the human-readable explanation."""
    out = []
    level = [node]
    for _ in range(spheres):
        if not level:
            break
        out.append(sorted((n.z for n in level), reverse=True))
        nxt = []
        for n in level:
            nxt.extend(n.kids or [])
        level = nxt
    return out


SYM = {1: "H", 6: "C", 7: "N", 8: "O", 9: "F", 15: "P", 16: "S", 17: "Cl",
       35: "Br", 53: "I"}


def sym(z):
    return SYM.get(z, str(z))


def explain(a, b):
    """Say where two branches diverge, in the language a student would use."""
    pa, pb = branch_profile(a), branch_profile(b)
    if pa[0] != pb[0]:
        return "%s outranks %s at the first atom." % (sym(a.z), sym(b.z))
    for i in range(1, min(len(pa), len(pb))):
        if pa[i] != pb[i]:
            return "Both branches begin with %s. At sphere %d one carries (%s) and the other (%s)." % (
                sym(a.z), i + 1,
                ", ".join(sym(z) for z in pa[i]),
                ", ".join(sym(z) for z in pb[i]))
    return "The branches differ only further out than the fourth sphere."


def rank_substituents(mol, centre_idx):
    """Rank the neighbours of centre_idx highest priority first."""
    centre = mol.GetAtomWithIdx(centre_idx)
    branches = []
    for nbr in centre.GetNeighbors():
        branches.append((nbr.GetIdx(), build_branch(mol, nbr.GetIdx(), centre_idx)))
    for _ in range(centre.GetTotalNumHs()):
        branches.append((None, Node(1, None, dup=True)))
    if len(branches) != 4:
        return None
    ordered = sorted(branches, key=lambda t: _key(t[1], 0), reverse=True)
    # reject if any adjacent pair is indistinguishable to this engine
    for i in range(3):
        if cmp_nodes(ordered[i][1], ordered[i + 1][1]) == 0:
            return None
    return ordered


def derive_rs(mol3d, centre_idx, ordered):
    """Re-derive R/S from the 3D geometry using our own ranking.

    mol3d carries explicit hydrogens, and AddHs preserves heavy-atom
    indices, so a ranking entry of None (an implicit H on the kekulised
    molecule) resolves to the stereocentre's real hydrogen neighbour here.
    No position is guessed.
    """
    import numpy as np
    conf = mol3d.GetConformer()
    centre_atom = mol3d.GetAtomWithIdx(centre_idx)
    hydrogens = [n.GetIdx() for n in centre_atom.GetNeighbors()
                 if n.GetAtomicNum() == 1]
    c = conf.GetAtomPosition(centre_idx)
    centre = np.array([c.x, c.y, c.z])

    vecs = []
    for idx, _node in ordered:
        if idx is None:
            if len(hydrogens) != 1:
                return None
            idx = hydrogens[0]
        p = conf.GetAtomPosition(idx)
        vecs.append(np.array([p.x, p.y, p.z]) - centre)

    a, b, cc, d = vecs
    # Sight line runs from the viewer, past the centre, towards d: the lowest
    # priority substituent points away. Under that view a -> b -> c turning
    # anticlockwise is S, clockwise is R. The scalar triple product a.(b x c)
    # is positive exactly when (a, b, c) is right-handed, which for a roughly
    # tetrahedral centre is the anticlockwise case.
    trip = float(np.dot(a, np.cross(b, cc)))
    if abs(trip) < 1e-6:
        return None
    return "S" if trip > 0 else "R"


# --------------------------------------------------------------------------
# Geometry and depiction
# --------------------------------------------------------------------------

WEDGE = {Chem.BondDir.BEGINWEDGE: "wedge",
         Chem.BondDir.BEGINDASH: "dash",
         Chem.BondDir.EITHERDOUBLE: "either"}


def depiction_2d(mol):
    flat = Chem.Mol(mol)
    AllChem.Compute2DCoords(flat)
    Chem.WedgeMolBonds(flat, flat.GetConformer())
    conf = flat.GetConformer()
    atoms = []
    for atom in flat.GetAtoms():
        p = conf.GetAtomPosition(atom.GetIdx())
        atoms.append({
            "el": atom.GetSymbol(),
            "x": round(p.x, 4),
            "y": round(p.y, 4),
            "nH": atom.GetTotalNumHs(),
            "q": atom.GetFormalCharge(),
            "ar": atom.GetIsAromatic(),
        })
    bonds = []
    for bond in flat.GetBonds():
        order = 4 if bond.GetIsAromatic() else int(bond.GetBondTypeAsDouble())
        entry = {
            "a": bond.GetBeginAtomIdx(),
            "b": bond.GetEndAtomIdx(),
            "o": order,
        }
        d = WEDGE.get(bond.GetBondDir())
        if d:
            entry["w"] = d
        bonds.append(entry)
    return {"atoms": atoms, "bonds": bonds}


def geometry_3d(mol):
    h = Chem.AddHs(Chem.Mol(mol))
    params = AllChem.ETKDGv3()
    params.randomSeed = 20260729          # deterministic output across builds
    if AllChem.EmbedMolecule(h, params) != 0:
        params.useRandomCoords = True
        if AllChem.EmbedMolecule(h, params) != 0:
            return None, None
    try:
        AllChem.MMFFOptimizeMolecule(h, maxIters=2000)
    except Exception:
        AllChem.UFFOptimizeMolecule(h, maxIters=2000)
    conf = h.GetConformer()
    lines = ["", "  PYTHIA", ""]
    lines.append("%3d%3d  0  0  0  0  0  0  0  0999 V2000"
                 % (h.GetNumAtoms(), h.GetNumBonds()))
    for atom in h.GetAtoms():
        p = conf.GetAtomPosition(atom.GetIdx())
        lines.append("%10.4f%10.4f%10.4f %-3s 0  0  0  0  0  0  0  0  0  0  0  0"
                     % (p.x, p.y, p.z, atom.GetSymbol()))
    for bond in h.GetBonds():
        order = 1 if bond.GetIsAromatic() else int(bond.GetBondTypeAsDouble())
        lines.append("%3d%3d%3d  0"
                     % (bond.GetBeginAtomIdx() + 1, bond.GetEndAtomIdx() + 1, order))
    lines.append("M  END")
    return "\n".join(lines), h



# --------------------------------------------------------------------------
# Name/structure agreement check
# --------------------------------------------------------------------------

def declared_descriptors(name):
    """Pull the stereodescriptors out of a name.

    "(2R,3S)-tartaric acid" -> (["R", "S"], [])
    "(E)-but-2-ene"         -> ([], ["E"])

    Returns (centres, bonds) as sorted lists, or (None, None) if the name
    declares nothing. Only the leading parenthesised block is read, so a
    common name later in the string cannot contribute a false match.
    """
    m = re.match(r"\(([^)]*)\)", name.strip())
    if not m:
        return None, None
    inside = m.group(1)
    centres, bonds = [], []
    for tok in re.findall(r"\d*([RSEZrs])(?![a-z])", inside):
        if tok in ("R", "S", "r", "s"):
            centres.append(tok.upper())
        else:
            bonds.append(tok)
    return sorted(centres), sorted(bonds)


def check_name(entry, centres, double_bonds):
    """Return an error string if the declared configuration is contradicted.

    `expect` is the assertion that matters: a sorted multiset of the
    descriptors this structure must produce. An empty string asserts that
    there are none, which is what catches an accidental stereocentre. None
    means the entry declares nothing, and we fall back to whatever the name
    itself claims in its leading parenthesised block.
    """
    got = sorted(c["label"].upper() for c in centres) + \
          sorted(b["label"] for b in double_bonds)
    got_s = "".join(got)

    if entry.expect is not None:
        want_s = "".join(sorted(entry.expect))
        if want_s != "".join(sorted(got_s)):
            return ("declares %s, structure gives %s"
                    % (entry.expect or "no stereocentres", got_s or "none"))
        return None

    want_c, want_b = declared_descriptors(entry.name)
    if want_c is None:
        return None
    got_c = sorted(c["label"].upper() for c in centres)
    got_b = sorted(b["label"] for b in double_bonds)
    if want_c and want_c != got_c:
        return ("name declares stereocentres %s, structure gives %s"
                % ("".join(want_c), "".join(got_c) or "none"))
    if want_b and want_b != got_b:
        return ("name declares double bond geometry %s, structure gives %s"
                % ("".join(want_b), "".join(got_b) or "none"))
    return None


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    out = []
    unverified = []
    failures = []

    for entry in LIBRARY:
        mol = Chem.MolFromSmiles(entry.smiles)
        if mol is None:
            failures.append((entry.id, "SMILES did not parse"))
            continue
        Chem.AssignStereochemistry(mol, cleanIt=True, force=True)
        try:
            rdCIPLabeler.AssignCIPLabels(mol)
        except Exception as exc:
            failures.append((entry.id, "CIP labeller: %s" % exc))
            continue

        kek = Chem.Mol(mol)
        Chem.Kekulize(kek, clearAromaticFlags=True)

        sdf, mol3d = geometry_3d(mol)
        if sdf is None:
            failures.append((entry.id, "3D embedding failed"))
            continue

        # --- stereocentres ------------------------------------------------
        centres = []
        for atom in mol.GetAtoms():
            if not atom.HasProp("_CIPCode"):
                continue
            idx = atom.GetIdx()
            label = atom.GetProp("_CIPCode")
            record = {"atom": idx, "label": label}

            ordered = rank_substituents(kek, idx)
            if ordered:
                derived = derive_rs(mol3d, idx, ordered)
                if derived == label:
                    steps = []
                    for i in range(3):
                        steps.append({
                            "high": ordered[i][0],
                            "low": ordered[i + 1][0],
                            "why": explain(ordered[i][1], ordered[i + 1][1]),
                        })
                    record["ranking"] = [t[0] for t in ordered]
                    record["steps"] = steps
                else:
                    unverified.append("%s / atom %d (engine said %s, RDKit says %s)"
                                      % (entry.id, idx, derived, label))
            else:
                unverified.append("%s / atom %d (ranking undecidable at rules 1a-1b)"
                                  % (entry.id, idx))
            centres.append(record)

        # --- double bond geometry ----------------------------------------
        double_bonds = []
        for bond in mol.GetBonds():
            if bond.GetStereo() in (Chem.BondStereo.STEREOE, Chem.BondStereo.STEREOZ,
                                    Chem.BondStereo.STEREOCIS, Chem.BondStereo.STEREOTRANS):
                st = str(bond.GetStereo()).replace("STEREO", "")
                lab = {"E": "E", "Z": "Z", "TRANS": "E", "CIS": "Z"}.get(st)
                if lab:
                    double_bonds.append({
                        "a": bond.GetBeginAtomIdx(),
                        "b": bond.GetEndAtomIdx(),
                        "label": lab,
                    })

        problem = check_name(entry, centres, double_bonds)
        if problem:
            failures.append((entry.id, problem))
            continue

        out.append({
            "id": entry.id,
            "name": entry.name,
            "common": entry.common,
            "group": entry.group,
            "note": entry.note,
            "smiles": Chem.MolToSmiles(mol),
            "formula": rdMolDescriptors.CalcMolFormula(mol),
            "mw": round(Descriptors.MolWt(mol), 3),
            "exact": round(Descriptors.ExactMolWt(mol), 5),
            "heavy": mol.GetNumHeavyAtoms(),
            "rings": rdMolDescriptors.CalcNumRings(mol),
            "d2": depiction_2d(kek),
            "sdf": sdf,
            "centres": centres,
            "doubleBonds": double_bonds,
            "tags": list(entry.tags),
            "sources": resolve(tuple(DATASET_SOURCES) + tuple(entry.sources)),
        })

    payload = json.dumps(out, ensure_ascii=True, separators=(",", ":"))
    header = (
        "/* PYTHIA molecule library.\n"
        "   Generated by tools/build_molecules.py -- do not edit by hand.\n"
        "   Geometry from RDKit (ETKDGv3 embedding, MMFF94 optimisation).\n"
        "   Stereodescriptors from RDKit's CIP labeller.\n"
        "   %d molecules. */\n" % len(out)
    )
    with open(OUT, "w", encoding="ascii") as fh:
        fh.write(header)
        fh.write("window.PYTHIA_SOURCES = ")
        fh.write(json.dumps(SOURCES, ensure_ascii=True, separators=(",", ":"),
                            sort_keys=True))
        fh.write(";\n")
        fh.write("window.PYTHIA_MOLECULES = ")
        fh.write(payload)
        fh.write(";\n")

    print("built %d molecules -> %s (%.0f kB)"
          % (len(out), os.path.relpath(OUT), os.path.getsize(OUT) / 1024))

    centres_total = sum(len(m["centres"]) for m in out)
    with_walk = sum(1 for m in out for c in m["centres"] if "steps" in c)
    print("stereocentres: %d total, %d with a verified walkthrough"
          % (centres_total, with_walk))

    if unverified:
        print("\nno walkthrough emitted for %d centre(s):" % len(unverified))
        for u in unverified:
            print("  -", u)
    if failures:
        print("\nFAILED:")
        for fid, why in failures:
            print("  -", fid, ":", why)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
