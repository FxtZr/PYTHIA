"""Spectroscopy: correlation tables and structure elucidation problems.

No spectra are reproduced here. What a student actually uses at the bench
is a correlation table -- where a band appears, how strong, what shape --
and the reasoning that turns three tables into one structure. All of that
is offline data and none of it needs a spectral database.

That was a deliberate choice. A real spectrum from a repository is noisy
and unannotated; a correlation table plus a worked problem with every
signal assigned teaches more. A network lookup of experimental spectra
(MassBank, CC BY 4.0) belongs on top of this, not underneath it.

SDBS is not used anywhere. Its terms forbid redistribution and automated
access, which makes it the KEGG of spectroscopy.

Values are the conventional teaching ranges. Real compounds fall outside
them, and where a substituent moves a band predictably the entry says so,
because that shift is usually the actual information.
"""

from collections import namedtuple

Band = namedtuple("Band", "group bond low high intensity shape note")
Region = namedtuple("Region", "environment low high note")
Loss = namedtuple("Loss", "mass fragment origin note")
Rule = namedtuple("Rule", "name requires gives note")
Problem = namedtuple("Problem", "id formula answer signals ir nmr ms reasoning")

SOURCES = ("silverstein", "pavia", "clayden", "nist-webbook")


# ---------------------------------------------------------------------------
# Infrared
# ---------------------------------------------------------------------------
# Ordered by wavenumber, descending, which is how a spectrum is read.

IR_BANDS = [
    Band("Alcohol", "O-H", 3200, 3600, "strong", "broad",
         "Broad because hydrogen bonding gives every molecule a slightly "
         "different bond strength. A dilute sample in a non-polar solvent "
         "sharpens it towards 3600, which is a good way to prove the "
         "breadth is hydrogen bonding and not something else."),
    Band("Carboxylic acid", "O-H", 2500, 3300, "strong", "very broad",
         "Unmistakable once seen: it sprawls across the C-H region and "
         "swallows it. Caused by the acid existing as a hydrogen-bonded "
         "dimer."),
    Band("Amine, primary", "N-H", 3300, 3500, "medium", "two bands",
         "Two bands, from symmetric and asymmetric stretching. A secondary "
         "amine gives one; a tertiary amine gives none, which is how the "
         "three are told apart."),
    Band("Amine, secondary", "N-H", 3300, 3500, "medium", "one band", None),
    Band("Amide", "N-H", 3100, 3500, "medium", "one or two bands",
         "Accompanied by the amide C=O near 1650, and the pair together is "
         "more diagnostic than either alone."),
    Band("Alkyne, terminal", "C-H", 3260, 3330, "strong", "sharp",
         "Sharp and sitting above the usual C-H region. Only a terminal "
         "alkyne puts a C-H there."),
    Band("Alkene", "=C-H", 3020, 3100, "medium", "sharp",
         "Just above 3000. The 3000 line is the most useful landmark in the "
         "whole spectrum: anything above it is attached to an sp2 or sp "
         "carbon."),
    Band("Aromatic", "C-H", 3000, 3100, "medium", "sharp", None),
    Band("Alkane", "C-H", 2850, 3000, "strong", "sharp",
         "Below 3000. Present in almost everything, so its absence is more "
         "informative than its presence."),
    Band("Aldehyde", "C-H", 2700, 2900, "weak", "two bands",
         "Two weak bands near 2720 and 2820. Easy to miss and worth "
         "hunting for: together with a carbonyl near 1725 they identify an "
         "aldehyde rather than a ketone."),
    Band("Nitrile", "C\u2261N", 2220, 2260, "medium", "sharp",
         "In a region where almost nothing else absorbs, so a sharp band "
         "here is close to conclusive."),
    Band("Alkyne", "C\u2261C", 2100, 2260, "weak", "sharp",
         "Weak, and absent altogether in a symmetrical alkyne where the "
         "stretch causes no change in dipole moment."),
    Band("Anhydride", "C=O", 1740, 1830, "strong", "two bands",
         "Two carbonyl bands, roughly 60 apart. Two C=O groups coupling "
         "with each other."),
    Band("Acid chloride", "C=O", 1780, 1815, "strong", "sharp",
         "The highest ordinary carbonyl. Chlorine pulls electron density "
         "away, strengthening the C=O bond and raising its frequency."),
    Band("Ester", "C=O", 1735, 1750, "strong", "sharp",
         "Confirm with the strong C-O stretch between 1000 and 1300; a "
         "carbonyl without it is not an ester."),
    Band("Aldehyde", "C=O", 1720, 1740, "strong", "sharp", None),
    Band("Ketone", "C=O", 1705, 1725, "strong", "sharp",
         "The reference point for every other carbonyl. Conjugation lowers "
         "it by 20 to 30; ring strain raises it, so cyclopentanone is near "
         "1745 and cyclobutanone near 1780."),
    Band("Carboxylic acid", "C=O", 1700, 1725, "strong", "sharp", None),
    Band("Amide", "C=O", 1630, 1690, "strong", "sharp",
         "The lowest common carbonyl, because nitrogen donates electron "
         "density into it and weakens the bond."),
    Band("Alkene", "C=C", 1620, 1680, "weak", "sharp",
         "Often weak, and invisible in a symmetrical alkene."),
    Band("Aromatic", "C=C", 1450, 1600, "medium", "several bands",
         "Usually two to four bands. Their pattern says little; their "
         "presence with C-H above 3000 says aromatic."),
    Band("Nitro", "N-O", 1345, 1560, "strong", "two bands",
         "Two strong bands, near 1520 and 1350. Hard to miss and hard to "
         "confuse."),
    Band("Alcohol, ester, ether", "C-O", 1000, 1300, "strong", "sharp",
         "Strong but not specific on its own. Its value is confirming what "
         "a carbonyl or an O-H has already suggested."),
    Band("Amine", "C-N", 1020, 1250, "medium", "sharp", None),
    Band("Alkyl chloride", "C-Cl", 600, 800, "strong", "sharp",
         "Down in the fingerprint region, where assignment stops being "
         "reliable. Mass spectrometry identifies halogens far better."),
]

FINGERPRINT_NOTE = (
    "Below about 1400 the bands come from whole-molecule vibrations rather "
    "than single bonds. Individual peaks cannot usually be assigned, but the "
    "pattern is characteristic enough to match a compound against a "
    "reference spectrum, which is where the name comes from. Do not try to "
    "reason your way through it."
)


# ---------------------------------------------------------------------------
# Proton NMR
# ---------------------------------------------------------------------------

H_REGIONS = [
    Region("Alkyl, C-H with nothing nearby", 0.7, 1.8,
           "The baseline. Everything else in this table is this, moved by "
           "something pulling electron density away."),
    Region("Adjacent to a carbonyl", 2.0, 2.6,
           "Alpha protons. Deshielded by the carbonyl next door."),
    Region("Benzylic, next to a ring", 2.2, 2.9, None),
    Region("Adjacent to nitrogen", 2.5, 3.5, None),
    Region("Adjacent to oxygen", 3.3, 4.5,
           "Oxygen is the strongest common deshielder. A signal here nearly "
           "always means the proton sits on a carbon bonded to oxygen."),
    Region("Alkene, vinyl", 4.5, 6.5, None),
    Region("Aromatic", 6.5, 8.5,
           "Pushed far downfield by the ring current, not merely by "
           "electronegativity. The circulating pi electrons generate a "
           "field that adds to the applied one outside the ring."),
    Region("Aldehyde", 9.5, 10.5,
           "Almost diagnostic on its own. Very little else appears here."),
    Region("Carboxylic acid", 10.0, 13.0,
           "Broad, and it disappears on shaking with D2O, which is the "
           "standard way to confirm an exchangeable proton."),
    Region("Alcohol or amine O-H, N-H", 0.5, 5.5,
           "Anywhere in this range depending on concentration, solvent and "
           "temperature, usually broad, and exchangeable. Its position "
           "carries no information; its disappearance with D2O does."),
]

C_REGIONS = [
    Region("Alkyl carbon", 0, 50, None),
    Region("Carbon bonded to nitrogen", 20, 60, None),
    Region("Carbon bonded to oxygen", 50, 90, None),
    Region("Alkyne carbon", 65, 90, None),
    Region("Alkene carbon", 100, 150, None),
    Region("Aromatic carbon", 110, 160,
           "Overlaps the alkene range. Counting signals against the "
           "expected symmetry usually separates them."),
    Region("Ester, amide or acid carbonyl", 160, 185, None),
    Region("Ketone or aldehyde carbonyl", 190, 220,
           "The furthest downfield carbon in ordinary organic chemistry, "
           "and well clear of everything else."),
]

MULTIPLICITY_NOTE = (
    "A signal split by n equivalent neighbours appears as n+1 lines, with "
    "intensities following Pascal's triangle. The rule assumes the "
    "neighbours are equivalent to each other; when they are not, the "
    "splittings multiply instead of adding, and a proton with two different "
    "neighbours gives four lines rather than three. Coupling is mutual: if A "
    "splits B, then B splits A by exactly the same constant, and matching "
    "those constants is how coupled partners are identified."
)


# ---------------------------------------------------------------------------
# Mass spectrometry
# ---------------------------------------------------------------------------

NEUTRAL_LOSSES = [
    Loss(15, "CH3", "Methyl", "Loss from a branch point, giving the more "
                              "stable cation."),
    Loss(17, "OH", "Hydroxyl", None),
    Loss(18, "H2O", "Water",
         "Common in alcohols, and often so complete that the molecular ion "
         "is barely visible. An apparent M of 18 less than expected is "
         "worth suspecting."),
    Loss(28, "CO or C2H4", "Carbon monoxide or ethene",
         "Ambiguous at unit resolution. High resolution separates them: CO "
         "is 27.9949 and C2H4 is 28.0313."),
    Loss(29, "CHO or C2H5", "Formyl or ethyl", None),
    Loss(31, "OCH3", "Methoxy", "Characteristic of methyl esters."),
    Loss(43, "C3H7 or CH3CO", "Propyl or acetyl", None),
    Loss(45, "COOH or OC2H5", "Carboxyl or ethoxy", None),
    Loss(46, "H2O + CO", "Water then carbon monoxide",
         "Sequential, and typical of carboxylic acids."),
]

KEY_IONS = [
    Loss(77, "C6H5+", "Phenyl", "A monosubstituted benzene ring."),
    Loss(91, "C7H7+", "Tropylium",
         "Benzylic cleavage gives a cation that rearranges to a "
         "seven-membered aromatic ring. Unusually stable, so this peak is "
         "often the base peak, and it is strong evidence for a benzyl "
         "group."),
    Loss(105, "C6H5CO+", "Benzoyl", "A benzoyl group."),
]

FRAGMENTATIONS = [
    Rule("Alpha cleavage",
         "A heteroatom or a carbonyl",
         "A cation stabilised by the lone pair or the carbonyl",
         "The bond that breaks is the one next to the functional group, not "
         "the one to it. The charge stays where it can be shared."),
    Rule("McLafferty rearrangement",
         "A carbonyl and a hydrogen on the gamma carbon",
         "An even-electron fragment and a neutral alkene",
         "The hydrogen transfers through a six-membered ring, so the chain "
         "must be long enough to reach. An even-mass fragment from a "
         "compound with no nitrogen usually means this has happened."),
    Rule("Benzylic cleavage",
         "A benzyl group",
         "The tropylium ion at m/z 91",
         "So favourable that it frequently dominates the spectrum."),
    Rule("Loss of water",
         "An alcohol",
         "M minus 18",
         "Often leaves the molecular ion too weak to see, which is a "
         "recognisable pattern in itself."),
    Rule("Halogen isotope pattern",
         "Chlorine or bromine",
         "A large M+2 peak",
         "Chlorine gives M+2 at about a third of M; bromine gives M+2 "
         "almost equal to M. Visible at a glance and quantitative enough to "
         "count the halogens."),
]

NITROGEN_RULE = (
    "A molecule with an even nominal molecular mass contains an even number "
    "of nitrogen atoms, including none. An odd mass means an odd number. "
    "This follows from nitrogen being the only common element whose usual "
    "valence and mass have opposite parity, and it settles the question of "
    "whether nitrogen is present before any other reasoning starts."
)


# ---------------------------------------------------------------------------
# Structure elucidation
# ---------------------------------------------------------------------------
# formula and signals are checked against the answer molecule at build time.

PROBLEMS = [
    Problem(
        id="c4h8o2-ester",
        formula="C4H8O2",
        answer="ethyl-acetate",
        signals=3,
        ir=["Strong sharp band at 1740",
            "Strong band near 1240",
            "No absorption above 3100"],
        nmr=["4.12 ppm, quartet, 2H",
             "2.04 ppm, singlet, 3H",
             "1.26 ppm, triplet, 3H"],
        ms=["M at 88", "Base peak at 43", "Fragment at 61"],
        reasoning=(
            "One degree of unsaturation, and nothing above 3100 rules out "
            "O-H and N-H, so the oxygen is not in an alcohol or an acid. A "
            "carbonyl at 1740 with a strong C-O near 1240 is an ester. The "
            "quartet and triplet integrating 2:3 are an ethyl group, and "
            "the quartet at 4.12 puts it on the oxygen rather than the "
            "carbonyl. The remaining singlet at 2.04 is a methyl next to "
            "the carbonyl. Loss of 45 from 88 is loss of the ethoxy group."
        ),
    ),
    Problem(
        id="c7h6o2-acid",
        formula="C7H6O2",
        answer="benzoic-acid",
        signals=4,
        ir=["Very broad absorption from 2500 to 3300",
            "Strong band at 1690",
            "Bands between 1450 and 1600"],
        nmr=["12.4 ppm, singlet, 1H, broad, disappears with D2O",
             "8.10 ppm, doublet, 2H",
             "7.60 ppm, triplet, 1H",
             "7.48 ppm, triplet, 2H"],
        ms=["M at 122", "Strong peak at 105", "Peak at 77"],
        reasoning=(
            "Five degrees of unsaturation, which a benzene ring plus a "
            "carbonyl accounts for exactly. The sprawling absorption from "
            "2500 to 3300 is an acid O-H dimer and nothing else looks like "
            "it. Four proton signals in a 1:2:1:2 pattern is a "
            "monosubstituted ring plus one exchangeable proton. Loss of 17 "
            "gives the benzoyl ion at 105 and loss of a further 28 gives "
            "phenyl at 77."
        ),
    ),
    Problem(
        id="c7h6o2-aldehyde",
        formula="C7H6O2",
        answer="4-hydroxybenzaldehyde",
        signals=4,
        ir=["Broad band centred near 3200",
            "Strong band at 1660",
            "Weak bands at 2730 and 2830"],
        nmr=["9.85 ppm, singlet, 1H",
             "7.82 ppm, doublet, 2H",
             "6.98 ppm, doublet, 2H",
             "6.20 ppm, singlet, 1H, broad"],
        ms=["M at 122", "Strong peak at 121", "Peak at 93"],
        reasoning=(
            "The same molecular formula as the previous problem and the "
            "same number of proton signals, which is the point. The "
            "difference is entirely in the shifts and the infrared. A "
            "singlet at 9.85 is an aldehyde and nothing else; the two weak "
            "infrared bands near 2730 and 2830 confirm it. The O-H is broad "
            "but not the acid sprawl, so it is a phenol. Two doublets of 2H "
            "each is a para-disubstituted ring. The carbonyl at 1660 rather "
            "than 1725 is conjugation with the ring pulling it down."
        ),
    ),
    Problem(
        id="c2h3n-nitrile",
        formula="C2H3N",
        answer="acetonitrile",
        signals=1,
        ir=["Sharp medium band at 2250",
            "Bands just below 3000",
            "Nothing between 1600 and 2200"],
        nmr=["1.98 ppm, singlet, 3H"],
        ms=["M at 41", "Peak at 40", "Peak at 26"],
        reasoning=(
            "An odd molecular mass means an odd number of nitrogens, so "
            "there is one. Three degrees of unsaturation with only two "
            "carbons has to be a triple bond to nitrogen counting twice "
            "plus the nitrogen itself. A sharp band at 2250 sits in a "
            "region almost nothing else occupies. One proton signal for "
            "three hydrogens leaves only a methyl."
        ),
    ),
    Problem(
        id="c6h10o-ketone",
        formula="C6H10O",
        answer="cyclohexanone",
        signals=3,
        ir=["Strong sharp band at 1715",
            "Bands below 3000 only"],
        nmr=["2.33 ppm, triplet, 4H",
             "1.86 ppm, quintet, 4H",
             "1.72 ppm, quintet, 2H"],
        ms=["M at 98", "Base peak at 55", "Peak at 42"],
        reasoning=(
            "Two degrees of unsaturation and only one carbonyl, so the "
            "second must be a ring. Nothing above 3000 rules out both "
            "unsaturation of the C-H sort and any O-H. A carbonyl at 1715 "
            "with no aldehyde bands near 2720 is a ketone. Three signals "
            "integrating 4:4:2 for ten hydrogens on six carbons is a "
            "symmetrical ring with the carbonyl at the mirror plane."
        ),
    ),
    Problem(
        id="c5h12-alkane",
        formula="C5H12",
        answer="2-methylbutane",
        signals=4,
        ir=["Bands between 2850 and 3000 only",
            "No carbonyl", "Nothing above 3000"],
        nmr=["1.45 ppm, multiplet, 1H",
             "1.15 ppm, quintet, 2H",
             "0.88 ppm, doublet, 6H",
             "0.85 ppm, triplet, 3H"],
        ms=["M at 72", "Base peak at 57", "Peak at 43"],
        reasoning=(
            "No degrees of unsaturation and an infrared spectrum with "
            "nothing but alkane C-H, so this is a saturated hydrocarbon "
            "with no functional group at all. The doublet integrating 6H is "
            "two equivalent methyls on the same carbon, which forces a "
            "branch. Loss of 15 to give the base peak at 57 is loss of a "
            "methyl from that branch point."
        ),
    ),
]
