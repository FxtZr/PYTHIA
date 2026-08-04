"""Stereochemistry lessons.

Prose, but built rather than hand-edited into a JS file, for two reasons
the build enforces:

  * every molecule id a lesson cites must exist in the library. A lesson
    referring to a molecule that was renamed would otherwise render an
    empty box and nobody would notice.
  * every source key must resolve.

Written for someone who has met the words before and not yet made them
mean anything. The order matters: what chirality is, how to spot it, how
to name it, then what it costs to get wrong.
"""

from collections import namedtuple

Lesson = namedtuple("Lesson", "id title blurb blocks sources")


def T(text):
    """A paragraph."""
    return {"kind": "text", "text": text}


def E(ids, caption=None):
    """A row of structures from the library."""
    return {"kind": "examples", "ids": list(ids), "caption": caption}


def P(a, b, caption):
    """Two structures side by side, meant to be read against each other."""
    return {"kind": "compare", "ids": [a, b], "caption": caption}


def C(title, text):
    """A trap worth naming before the reader falls into it."""
    return {"kind": "callout", "title": title, "text": text}


REF = ("clayden", "iupac-bluebook-2013")
CIP = ("cip-1966", "prelog-helmchen-1982", "iupac-bluebook-2013",
       "hanson-cip-2018")


LESSONS = [

    Lesson(
        id="what-chirality-is",
        title="What chirality is",
        blurb="An object is chiral when it cannot be laid on top of its own "
              "mirror image. Your hands are the standard example, and they "
              "are a better one than they look.",
        sources=REF,
        blocks=[
            T("Hold your hands palm down side by side. Same fingers, same "
              "lengths, same joints. Now try to put one exactly on top of "
              "the other, both palms down. It cannot be done: the thumbs "
              "point opposite ways. Nothing is missing from either hand and "
              "nothing is out of order. The difference is entirely in the "
              "arrangement."),
            T("A molecule can be in the same position. Take a carbon with "
              "four different groups attached. There are two ways to arrange "
              "them in space, and the two are mirror images that cannot be "
              "superimposed however you turn them. They are called "
              "enantiomers."),
            P("bromochlorofluoromethane-r", "bromochlorofluoromethane-s",
              "The smallest possible pair. Rotate them in the 3D view and "
              "satisfy yourself that no orientation makes them match."),
            T("This is not a subtlety of notation. The two forms are "
              "genuinely different objects, and anything that is itself "
              "chiral, which includes almost every protein in your body, "
              "can tell them apart."),
            C("A test that always works",
              "If a molecule has an internal mirror plane, it is achiral, "
              "whatever else is true of it. Looking for that plane is often "
              "faster than counting stereocentres."),
        ],
    ),

    Lesson(
        id="finding-a-stereocentre",
        title="Finding a stereocentre",
        blurb="Four different groups on one carbon. The word different is "
              "doing more work than it appears to.",
        sources=REF,
        blocks=[
            T("A carbon is a stereocentre when swapping any two of its four "
              "substituents gives a different molecule. In practice that "
              "means all four have to be different from each other, and the "
              "comparison has to run all the way out, not just to the first "
              "atom."),
            E(["alanine-s", "lactic-acid-s", "butan-2-ol-r"],
              "Three straightforward cases. Each central carbon carries four "
              "genuinely distinct groups."),
            T("The traps are the near misses. Two groups that look different "
              "on the page can turn out to be the same substituent reached "
              "by a different route."),
            P("alanine-s", "glycine",
              "Alanine has a stereocentre. Glycine, one methyl group lighter, "
              "does not: its central carbon carries two hydrogens, so two of "
              "the four are identical."),
            E(["propan-2-ol"],
              "A classic false positive. The middle carbon has an OH and "
              "three other bonds, but two of those go to identical methyl "
              "groups."),
            C("Carbon is not the only option",
              "Nitrogen, phosphorus and sulfur can all be stereocentres. "
              "Amines usually are not useful ones, because the nitrogen "
              "flips through a flat arrangement millions of times a second "
              "and the two forms interconvert faster than they can be "
              "separated."),
        ],
    ),

    Lesson(
        id="cip-priority",
        title="Ranking the four groups",
        blurb="Before a centre can be called R or S, its four substituents "
              "have to be put in order. The rules are mechanical, and the "
              "first one settles most cases.",
        sources=CIP,
        blocks=[
            T("Rule one: compare the atoms attached directly to the centre "
              "and rank them by atomic number. Higher wins. Bromine beats "
              "chlorine beats oxygen beats nitrogen beats carbon beats "
              "hydrogen. Where the first atoms differ, you are finished."),
            E(["bromochlorofluoromethane-r"],
              "Decided entirely at the first atom: Br, Cl, F, H."),
            T("When two branches start with the same atom, move one step out "
              "along each and compare what you find there. List the atoms "
              "attached to each branch atom in descending order and compare "
              "the lists position by position. The first difference decides "
              "it, and you stop."),
            E(["glyceraldehyde-r"],
              "Both the CHO and the CH2OH branches start with carbon. One "
              "sphere out, the aldehyde carbon carries (O, O, H) against the "
              "alcohol's (O, H, H), and the aldehyde wins."),
            C("Where the O, O comes from",
              "A double bond counts twice. The carbon of a C=O is treated as "
              "carrying two oxygens: the real one, and a duplicate standing "
              "in for the second bond. The duplicate has no substituents of "
              "its own. Forget this and every carbonyl group gets ranked "
              "below every alcohol, which inverts the answer."),
            T("Two further rules exist for cases the first two cannot "
              "separate, covering isotopes and, at the end, the "
              "configuration of the branches themselves. They are rare in "
              "teaching examples and this program does not walk through "
              "them. Where a centre needs them, the walkthrough is withheld "
              "rather than guessed at."),
        ],
    ),

    Lesson(
        id="assigning-r-and-s",
        title="Assigning R and S",
        blurb="Point the lowest priority away from you and read the "
              "remaining three in order. Clockwise is R.",
        sources=CIP,
        blocks=[
            T("With the four groups ranked a, b, c, d from highest to "
              "lowest, turn the molecule so that d points directly away from "
              "you. Look at the other three. If going a to b to c turns "
              "clockwise, the centre is R, from rectus. Anticlockwise is S, "
              "from sinister."),
            T("On paper, d is usually the hydrogen and it is usually drawn "
              "on a hashed bond, which already means going away from you. "
              "When it is drawn on a wedge instead, work out the answer as "
              "though it were hashed and then reverse it. That shortcut "
              "saves more time than any other in this subject."),
            P("alanine-s", "alanine-r",
              "Same four groups, opposite arrangement, opposite letter. Open "
              "either one in Explore for the ranking step by step."),
            C("R and S say nothing about rotation",
              "R and S describe an arrangement in space. Whether a compound "
              "rotates polarised light to the left or the right is a "
              "measured physical property, and it cannot be predicted from "
              "the letter. The two are independent, and treating (+) as a "
              "synonym for R is a persistent and costly confusion."),
            C("D and L are a different system again",
              "The D and L labels come from an older convention based on "
              "glyceraldehyde, and they do not map onto R and S in any "
              "simple way. Natural tartaric acid is (2R,3R) and is written "
              "L-(+): an L that rotates light to the right."),
        ],
    ),

    Lesson(
        id="enantiomers-and-diastereomers",
        title="Enantiomers, diastereomers, and why the difference is not "
              "academic",
        blurb="Mirror images behave identically until something chiral "
              "meets them. Stereoisomers that are not mirror images behave "
              "differently from the start.",
        sources=REF,
        blocks=[
            T("Two enantiomers have the same melting point, the same "
              "solubility, the same infrared spectrum, the same NMR in an "
              "ordinary solvent. Nothing achiral can distinguish them. Put "
              "them in a chiral environment, though, and they part company "
              "immediately."),
            P("carvone-r", "carvone-s",
              "One stereocentre inverted. One smells of spearmint and the "
              "other of caraway, because the receptors doing the smelling "
              "are themselves chiral."),
            T("Once a molecule has two or more stereocentres, a second "
              "relationship appears. Stereoisomers that are not mirror "
              "images of each other are diastereomers, and they are simply "
              "different compounds: different melting points, different "
              "solubility, separable by ordinary means."),
            P("dimethylcyclohexane-cis", "dimethylcyclohexane-trans",
              "Not mirror images. These are two distinct substances that "
              "happen to share a formula."),
            E(["ephedrine", "pseudoephedrine"],
              "Diastereomers, different drugs, different clinical profiles. "
              "The names hide how closely related they are."),
        ],
    ),

    Lesson(
        id="meso",
        title="Two stereocentres and no chirality",
        blurb="A molecule can contain stereocentres and still be "
              "superimposable on its mirror image.",
        sources=REF,
        blocks=[
            T("Counting stereocentres is a useful habit and a poor test. If "
              "a molecule contains an internal mirror plane, the halves "
              "cancel: whatever handedness one side contributes, the other "
              "contributes in reverse. Such a compound is called meso, and "
              "it is achiral despite having stereocentres."),
            E(["tartaric-acid-rr", "tartaric-acid-ss", "tartaric-acid-meso"],
              "Two stereocentres allow four arrangements in principle. Here "
              "only three compounds exist, because the (2R,3S) and (2S,3R) "
              "forms are the same molecule viewed from two sides."),
            T("The meso form is a diastereomer of the other two, so it has "
              "its own melting point and its own solubility, and it does not "
              "rotate polarised light at all."),
            C("Why this matters historically",
              "Pasteur separated the two chiral forms of tartaric acid by "
              "hand under a microscope in 1848, having noticed that their "
              "crystals were mirror images. That observation is where the "
              "whole subject starts."),
        ],
    ),

    Lesson(
        id="e-and-z",
        title="Geometry at a double bond",
        blurb="A double bond cannot rotate, so the groups on it are fixed in "
              "place. Naming which arrangement you have needs the same "
              "priority rules.",
        sources=CIP,
        blocks=[
            T("Rotation about a single bond is nearly free. Rotation about a "
              "double bond is not: it would require breaking the pi bond, "
              "which costs far more energy than room temperature supplies. "
              "So the two ends stay as they are, and two distinct compounds "
              "exist."),
            P("but-2-ene-z", "but-2-ene-e",
              "Same connectivity, fixed and different geometry."),
            T("To name them, rank the two groups on each carbon by the same "
              "CIP rules. If the higher priority group on one carbon is on "
              "the same side as the higher priority group on the other, the "
              "double bond is Z, from zusammen. Opposite sides is E, from "
              "entgegen."),
            E(["but-2-ene-ambiguous"],
              "Why cis and trans are not enough. Each carbon here carries a "
              "methyl and a chlorine, so there is no answer to the question "
              "of which groups are on the same side. Only priority ranking "
              "resolves it."),
            P("maleic-acid", "fumaric-acid",
              "The Z and E forms of the same acid melt about 150 degrees "
              "apart. Geometry alone accounts for the difference."),
        ],
    ),

    Lesson(
        id="conformation-vs-configuration",
        title="Conformation is not configuration",
        blurb="One can be changed by turning a bond. The other cannot be "
              "changed without breaking one.",
        sources=REF,
        blocks=[
            T("Conformations are the arrangements a molecule passes through "
              "as its single bonds rotate. They interconvert billions of "
              "times a second at room temperature, so a sample is never in "
              "one of them; it is a population moving between all of them."),
            E(["ethane", "butane", "cyclohexane"],
              "Rotation about the central bond of butane costs a few "
              "kilojoules. Cyclohexane's ring flips between two chairs just "
              "as freely."),
            T("Configuration is different in kind. Turning an R centre into "
              "an S centre means breaking a bond and remaking it on the "
              "other side. Nothing a molecule does at room temperature "
              "achieves that."),
            C("The practical consequence",
              "Two conformations can never be separated and put in different "
              "bottles. Two configurations can, at least in principle. If "
              "you can draw a rotation that turns one drawing into the "
              "other, you were looking at one compound the whole time."),
        ],
    ),

    Lesson(
        id="why-it-matters",
        title="What this costs when it goes wrong",
        blurb="Biology is built out of single enantiomers, so it responds to "
              "the two forms of a drug as if they were different substances. "
              "Which they are.",
        sources=REF,
        blocks=[
            T("Almost every amino acid in your proteins is the S enantiomer. "
              "Every sugar in your DNA has one particular configuration. The "
              "receptors, enzymes and transporters built from those pieces "
              "are chiral throughout, and a chiral site fits one enantiomer "
              "and not the other, the way a left glove fits one hand."),
            P("ibuprofen-s", "ibuprofen-r",
              "Only the S form inhibits cyclooxygenase. Ordinary ibuprofen "
              "is sold as a mixture of both, and the body slowly converts "
              "some of the R form into the S."),
            E(["thalidomide-s", "thalidomide-r"],
              "One enantiomer is a sedative, the other is teratogenic. The "
              "drug was sold as a mixture in the late 1950s."),
            C("Separating them would not have been enough",
              "It is often said that the thalidomide disaster was a failure "
              "to separate the enantiomers. The two forms interconvert in "
              "the body, so administering the pure sedative form would still "
              "have produced the harmful one. The lesson is not that "
              "separation is sufficient, but that stereochemistry has to be "
              "understood rather than managed."),
            T("This is why the subject is worth the effort it takes. R and S "
              "are notation, and notation is boring, but what the notation "
              "describes is the difference between a drug and a poison."),
        ],
    ),
]
