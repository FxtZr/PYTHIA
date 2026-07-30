"""IUPAC nomenclature: the rules, the seniority table, and worked names.

The worked names are decompositions: a name cut into the pieces it is
actually made of, each with an explanation of why that piece is there.
Concatenating the pieces has to reproduce the molecule's name exactly, and
the build checks that. A decomposition that does not spell the name is a
decomposition that teaches the wrong construction.

Everything here follows the 2013 recommendations. Where an older form is
still in wide use, it is named as such rather than silently corrected: a
reader will meet "1-butene" in the literature and needs to recognise it.
"""

from collections import namedtuple

Rule = namedtuple("Rule", "id title blocks")
Named = namedtuple("Named", "molecule parts commentary")
Group = namedtuple("Group", "rank name suffix prefix example")


def T(text):
    return {"kind": "text", "text": text}


def C(title, text):
    return {"kind": "callout", "title": title, "text": text}


def E(ids, caption=None):
    return {"kind": "examples", "ids": list(ids), "caption": caption}


def p(text, kind, why=None):
    """One piece of a name."""
    return {"text": text, "kind": kind, "why": why}


def sep(text="-"):
    return {"text": text, "kind": "sep", "why": None}


SOURCES = ("iupac-bluebook-2013", "clayden")


# ---------------------------------------------------------------------------
# The order of seniority
# ---------------------------------------------------------------------------
# Only the most senior group present gets the suffix. Everything else is
# demoted to a prefix. This single table settles most of the questions
# beginners find hardest, which is why it comes before the rules.

SENIORITY = [
    Group(1, "Carboxylic acid", "-oic acid", "carboxy-", "benzoic-acid"),
    Group(2, "Ester", "-oate", "(alkoxycarbonyl)-", "ethyl-acetate"),
    Group(3, "Amide", "-amide", "carbamoyl-", "acetamide"),
    Group(4, "Nitrile", "-nitrile", "cyano-", "acetonitrile"),
    Group(5, "Aldehyde", "-al", "oxo-", "4-hydroxybenzaldehyde"),
    Group(6, "Ketone", "-one", "oxo-", "cyclohexanone"),
    Group(7, "Alcohol", "-ol", "hydroxy-", "cyclohexanol"),
    Group(8, "Amine", "-amine", "amino-", None),
    Group(9, "Ether", "none", "alkoxy-", None),
]


# ---------------------------------------------------------------------------
# The rules, in the order they are applied
# ---------------------------------------------------------------------------

RULES = [
    Rule(
        id="parent-chain",
        title="Find the parent",
        blocks=[
            T("Naming starts by deciding what the molecule is a version of. "
              "Find the longest continuous chain of carbon atoms and let it "
              "give the stem: one carbon is meth, then eth, prop, but, pent, "
              "hex, hept, oct, non, dec."),
            T("Longest means longest, not the one drawn horizontally. A "
              "structure drawn as a straight line with a branch may well "
              "have its longest chain running through the branch."),
            E(["2-methylbutane", "3-ethyl-2-methylhexane"],
              "Four carbons and six carbons respectively, whatever the "
              "drawing suggests at first glance."),
            C("When the principal group decides for you",
              "If the molecule carries a functional group that takes a "
              "suffix, the parent chain must contain that group, even when a "
              "longer chain exists elsewhere. The group outranks length."),
        ],
    ),

    Rule(
        id="principal-group",
        title="Choose the suffix",
        blocks=[
            T("A molecule may carry several functional groups, but only one "
              "of them gets to be the suffix. The order of seniority decides "
              "which. Everything below it in the table becomes a prefix."),
            E(["3-oxobutanoic-acid", "4-hydroxybenzaldehyde"],
              "In each of these two groups compete, and the more senior one "
              "takes the ending while the other is demoted."),
            C("Why oxo and not one",
              "A ketone names itself -one when it wins, and oxo- when it "
              "loses. Learning both forms of each group is what makes the "
              "seniority table usable rather than decorative."),
        ],
    ),

    Rule(
        id="numbering",
        title="Number the chain",
        blocks=[
            T("Number from whichever end gives the principal group the lower "
              "locant. If there is no principal group, number to give the "
              "lower locant to the first point of difference across the whole "
              "set of substituents."),
            T("Locants are placed immediately in front of the part of the "
              "name they refer to. This is the change most often met in "
              "older texts: but-1-ene, not 1-butene. Both name the same "
              "compound, and the newer form is the one to write."),
            E(["but-1-ene", "but-1-yne"],
              "The locant sits next to the ending it qualifies."),
            C("Rings number themselves",
              "On a ring, the carbon carrying the principal group is C1 by "
              "definition, so no locant is needed for it. Cyclohexanol needs "
              "no number; 1-cyclohexanol would be redundant."),
        ],
    ),

    Rule(
        id="substituents",
        title="Cite the substituents",
        blocks=[
            T("Substituent prefixes are cited in alphabetical order, "
              "regardless of their locants. Ethyl comes before methyl "
              "whatever numbers they carry."),
            T("Multiplying prefixes -- di, tri, tetra -- are not counted for "
              "alphabetical order. Triethyl files under E, not under T. The "
              "multiplier is bookkeeping, not part of the substituent's "
              "name."),
            E(["3-ethyl-2-methylhexane", "2-2-4-trimethylpentane"],
              "Alphabetical order in the first, a multiplying prefix in the "
              "second."),
        ],
    ),

    Rule(
        id="stereodescriptors",
        title="Add the stereochemistry",
        blocks=[
            T("Stereodescriptors are cited at the very front of the name, in "
              "brackets, with their locants. They come before everything "
              "else, including the alphabetical substituent list."),
            E(["2-amino-4-methylpentanoic-acid"],
              "The descriptor leads, then the substituent prefixes, then the "
              "parent and its suffix."),
            C("Retained names still exist",
              "The 2013 recommendations keep a short list of traditional "
              "names that are too entrenched to replace: benzoic acid, "
              "acetic acid, formic acid and a handful of others. They are "
              "permitted, not merely tolerated."),
        ],
    ),
]


# ---------------------------------------------------------------------------
# Worked names
# ---------------------------------------------------------------------------

NAMES = [
    Named("2-methylbutane", [
        p("2", "locant",
          "Which carbon carries the branch. Numbering runs from the end "
          "that makes this number as small as possible."),
        sep(),
        p("Methyl", "substituent", "A one-carbon branch."),
        p("butane", "parent",
          "The longest continuous chain is four carbons, and every bond in "
          "it is single."),
    ], "The whole name in three decisions: how long, what is attached, and "
       "where."),

    Named("2-2-4-trimethylpentane", [
        p("2,2,4", "locant",
          "Three branches, so three locants. Two of them are on the same "
          "carbon, which is allowed and common."),
        sep(),
        p("Tri", "multiplier",
          "Three identical substituents. This prefix is ignored when "
          "putting substituents in alphabetical order."),
        p("methyl", "substituent", "Each branch is a single carbon."),
        p("pentane", "parent", "Five carbons in the longest chain."),
    ], "Known industrially as isooctane, and the reference point for 100 on "
       "the octane scale, which is why a five-carbon parent ended up "
       "defining an eight-carbon standard."),

    Named("3-ethyl-2-methylhexane", [
        p("3", "locant", "Position of the ethyl branch."),
        sep(),
        p("Ethyl", "substituent",
          "A two-carbon branch. Cited first because E precedes M, not "
          "because its locant is higher."),
        sep(),
        p("2", "locant", "Position of the methyl branch."),
        sep(),
        p("methyl", "substituent", "A one-carbon branch."),
        p("hexane", "parent", "Six carbons in the longest chain."),
    ], "The example that separates alphabetical order from numerical order. "
       "Ethyl has the higher locant and is still cited first."),

    Named("but-1-ene", [
        p("But", "parent", "Four carbons."),
        sep(),
        p("1", "locant",
          "Where the double bond starts. Placed immediately before the "
          "ending it qualifies."),
        sep(),
        p("ene", "suffix", "A carbon-carbon double bond."),
    ], "Older literature writes this 1-butene. Same compound; the modern "
       "placement of the locant is the one to use."),

    Named("but-1-yne", [
        p("But", "parent", "Four carbons."),
        sep(),
        p("1", "locant", "Where the triple bond starts."),
        sep(),
        p("yne", "suffix", "A carbon-carbon triple bond."),
    ], "The same construction as the alkene, one ending along."),

    Named("cyclohexanol", [
        p("Cyclo", "parent", "The chain closes into a ring."),
        p("hexan", "parent", "Six carbons in that ring."),
        p("ol", "suffix", "An alcohol, the principal group here."),
    ], "No locant appears because the carbon carrying the principal group "
       "is C1 by definition on a ring."),

    Named("cyclohexanone", [
        p("Cyclo", "parent", "A ring."),
        p("hexan", "parent", "Of six carbons."),
        p("one", "suffix", "A ketone."),
    ], "One letter apart from cyclohexanol and a different class of "
       "compound entirely."),

    Named("ethyl-acetate", [
        p("Ethyl", "substituent",
          "The group that came from the alcohol. Esters name that part "
          "first, as a separate word."),
        sep(" "),
        p("acetate", "suffix",
          "The acid part, with its ending changed from -ic acid to -ate."),
    ], "Systematically this is ethyl ethanoate. Acetate is a retained name "
       "and both are correct."),

    Named("acetamide", [
        p("Acet", "parent",
          "Two carbons, using the retained stem from acetic acid."),
        p("amide", "suffix", "The amide group, which is senior to most."),
    ], "Systematically ethanamide."),

    Named("acetonitrile", [
        p("Aceto", "parent", "Two carbons, including the nitrile carbon."),
        p("nitrile", "suffix", "A carbon-nitrogen triple bond."),
    ], "The nitrile carbon counts as part of the chain, which catches "
       "people out when they number it."),

    Named("benzoic-acid", [
        p("Benzo", "parent", "A benzene ring bearing the acid group."),
        p("ic acid", "suffix",
          "The carboxylic acid, the most senior group in the table."),
    ], "A retained name, explicitly permitted by the 2013 recommendations."),

    Named("4-hydroxybenzaldehyde", [
        p("4", "locant", "Position of the hydroxyl relative to the aldehyde."),
        sep(),
        p("Hydroxy", "substituent",
          "The alcohol, demoted to a prefix because the aldehyde outranks "
          "it."),
        p("benz", "parent", "The benzene ring."),
        p("aldehyde", "suffix", "The senior group, so it takes the ending."),
    ], "Two functional groups, one suffix. The seniority table decides which "
       "and the loser becomes a prefix."),

    Named("3-oxobutanoic-acid", [
        p("3", "locant", "Position of the ketone."),
        sep(),
        p("Oxo", "substituent",
          "A ketone in its prefix form, because the carboxylic acid is more "
          "senior."),
        p("butan", "parent", "Four carbons, the acid carbon counted as C1."),
        p("oic acid", "suffix", "The carboxylic acid."),
    ], "Known as acetoacetic acid, and one of the ketone bodies the liver "
       "produces during fasting."),

    Named("2-amino-4-methylpentanoic-acid", [
        p("(S)", "stereo",
          "The configuration at the stereocentre. Stereodescriptors are "
          "cited at the very front of the name."),
        sep(),
        p("2", "locant", "Position of the amino group."),
        sep(),
        p("Amino", "substituent",
          "The amine, demoted to a prefix by the acid."),
        sep(),
        p("4", "locant", "Position of the methyl."),
        sep(),
        p("methyl", "substituent", "A one-carbon branch."),
        p("pentan", "parent", "Five carbons, counting the acid carbon."),
        p("oic acid", "suffix", "The carboxylic acid, most senior."),
    ], "The full construction with everything in play. Known to every "
       "biochemist as leucine, which is considerably shorter."),
]
