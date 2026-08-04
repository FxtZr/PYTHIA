#!/usr/bin/env python3
"""Write SOURCES.md from the registry in sources.py.

Generated rather than hand-maintained so the file cannot drift away from
what the program actually cites. Editing SOURCES.md directly will be
overwritten; edit sources.py.
"""

import os
import sys

from sources import SOURCES

OUT = os.path.join(os.path.dirname(__file__), "..", "SOURCES.md")

HEADER = """# Sources

Generated from `tools/sources.py` by `tools/build_sources_md.py`. Edit the
registry, not this file.

Every factual claim the program displays resolves to a key in that
registry, and the build refuses to emit a record citing a key that is not
defined. An unsourced fact therefore cannot reach the interface by
accident.

**Included here** means data from that source ships inside this
repository. **Cited only** means the source is referenced so a reader can
go and check, and nothing from it is reproduced.

## Not used

**KEGG.** It is the best known pathway database and its licence forbids
redistribution without a commercial agreement, which makes it unusable in
an open repository. Reactome and Rhea cover the same ground under CC BY
4.0 and are used instead.

## Still to verify

- **DOIs** are deliberately absent. A wrong DOI is worse than no DOI, and
  they cannot be confirmed from an offline build. Add them in one pass
  with network access and record the date below.
- **EC numbers** in `tools/pathways.py` are checked for shape only. Confirm
  them against ExplorEnz and record the date below.

| Check | Date | By |
| --- | --- | --- |
| DOIs confirmed | not yet | |
| EC numbers confirmed | not yet | |

"""


def main():
    included, cited = [], []
    for key in sorted(SOURCES, key=lambda k: SOURCES[k]["title"].lower()):
        (included if SOURCES[key].get("use") == "redistributed"
         else cited).append((key, SOURCES[key]))

    lines = [HEADER]
    for title, group in (("Included here", included), ("Cited only", cited)):
        if not group:
            continue
        lines.append("## %s\n" % title)
        for key, s in group:
            lines.append("### %s\n" % s["title"])
            lines.append("- **Key** `%s`" % key)
            if s.get("authors"):
                lines.append("- **Authors** %s" % s["authors"])
            if s.get("publisher"):
                lines.append("- **Publisher** %s" % s["publisher"])
            if s.get("year"):
                lines.append("- **Year** %s" % s["year"])
            if s.get("where"):
                lines.append("- **Where** %s" % s["where"])
            if s.get("licence"):
                lines.append("- **Licence** %s" % s["licence"])
            if s.get("url"):
                lines.append("- **Link** <%s>" % s["url"])
            lines.append("")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines).rstrip() + "\n")

    print("wrote %s (%d included, %d cited only)"
          % (os.path.relpath(OUT), len(included), len(cited)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
