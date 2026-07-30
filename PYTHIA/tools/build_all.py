#!/usr/bin/env python3
"""Run every generator, in order, and stop at the first failure.

Order matters: the molecule library has to exist before anything that
cites it can be checked against it.
"""

import os
import subprocess
import sys

SCRIPTS = [
    ("build_elements.py", "element table"),
    ("build_molecules.py", "molecule library"),
    ("build_mechanisms.py", "reaction mechanisms"),
    ("build_lessons.py", "stereochemistry lessons"),
    ("build_nomenclature.py", "nomenclature"),
    ("build_pathways.py", "metabolic pathways"),
    ("build_spectroscopy.py", "spectroscopy"),
    ("build_glossary.py", "glossary"),
    ("build_sources_md.py", "SOURCES.md"),
]


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    for script, label in SCRIPTS:
        print("\n=== %s" % label)
        result = subprocess.run([sys.executable, script], cwd=here)
        if result.returncode != 0:
            print("\nstopped: %s failed" % script)
            return result.returncode
    print("\nall generators completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
