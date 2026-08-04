"""Reaction mechanisms.

Each step is a mapped SMILES. The map numbers are the anchors: an arrow
says "from atom 1 to atom 2" in map-number space, and the build resolves
those to whatever indices RDKit ends up using. Hand-written atom indices
would break the moment a structure changed.

    [OH-:1].[CH3:2][Br:3]
             ^      ^  ^
             1      2  3      map numbers, stable across rebuilds

Map numbers are stripped before drawing, so they never appear on screen.

What is deliberately not modelled
---------------------------------
Transition states. A SMILES string cannot express a partial bond, and
drawing a pentacoordinate carbon as though it were a real species would
teach something false. Where the transition state matters, it is described
in the step text and the reactant structure carries partial-charge labels
instead.

Arrow conventions
-----------------
A full arrowhead moves a pair of electrons. A half head, the fishhook,
moves one. Radical steps use "single" and nothing else does.
"""

from collections import namedtuple

Mech = namedtuple("Mech", "id name family summary attack steps sources")
Step = namedtuple("Step", "smiles title text arrows lone labels",
                  defaults=((), {}, ()))


def A(frm, to, bow=0.4, kind="pair"):
    """An electron-pushing arrow, in map-number space.

    frm, to   an int for an atom, a 2-tuple for the bond between two atoms
    bow       signed curvature; positive bows left of the source-to-target
              direction. Zero is straight.
    kind      "pair" or "single"
    """
    return {"from": frm, "to": to, "bow": bow, "kind": kind}


# Shared reference for the mechanistic reasoning throughout.
REF = ("clayden", "iupac-bluebook-2013")


MECHANISMS = [

    # ======================================================================
    Mech(
        id="sn2",
        name="Nucleophilic substitution, SN2",
        family="substitution",
        summary="One step. The nucleophile arrives as the leaving group "
                "departs, and the carbon is turned inside out in the "
                "process.",
        attack="The nucleophile attacks the carbon on the face directly "
               "opposite the leaving group, because that is the only "
               "approach that does not run into the electrons of the bond "
               "being broken. Everything else about SN2 follows from that "
               "one geometric constraint: the rate collapses as the carbon "
               "gets more crowded, and a stereocentre always comes out "
               "inverted.",
        sources=REF,
        steps=[
            Step(
                smiles="[OH-:1].[CH3:2][Br:3]",
                title="Attack and departure, together",
                text="Bromine is more electronegative than carbon, so the "
                     "carbon carries a partial positive charge and is the "
                     "electrophilic site. Hydroxide brings a lone pair to "
                     "it. There is no intermediate: as the new bond forms "
                     "the old one breaks, which is why the rate depends on "
                     "both concentrations.",
                arrows=(A(1, 2, bow=0.45), A((2, 3), 3, bow=-0.35)),
                lone={1: 3},
                labels=({"atom": 2, "text": "\u03b4+"},
                        {"atom": 3, "text": "\u03b4\u2212"}),
            ),
            Step(
                smiles="[CH3:2][OH:1].[Br-:3]",
                title="Products",
                text="At the halfway point the carbon is briefly bonded to "
                     "five things and flat. That arrangement is a transition "
                     "state, not a species you can isolate, so it is not "
                     "drawn here. If the carbon had been a stereocentre it "
                     "would now have the opposite configuration, the way an "
                     "umbrella turns out in the wind.",
                lone={1: 2, 3: 4},
            ),
        ],
    ),

    # ======================================================================
    Mech(
        id="sn1",
        name="Nucleophilic substitution, SN1",
        family="substitution",
        summary="Two steps. The leaving group goes first, on its own, and "
                "whatever is left has to cope with a positively charged "
                "carbon.",
        attack="Nothing attacks anything in the slow step. The molecule "
               "simply falls apart, and the rate depends only on the "
               "substrate. Because the carbocation is flat, the nucleophile "
               "can then arrive from either face with equal ease, which is "
               "why a single enantiomer goes in and a mixture comes out.",
        sources=REF,
        steps=[
            Step(
                smiles="[CH3:1][C:2]([CH3:3])([CH3:4])[Br:5]",
                title="Ionisation, the slow step",
                text="The carbon-bromine bond breaks by itself, both "
                     "electrons leaving with the bromine. This costs energy "
                     "and sets the rate. It is only feasible here because "
                     "three methyl groups can stabilise the positive charge "
                     "that results.",
                arrows=(A((2, 5), 5, bow=0.4),),
            ),
            Step(
                smiles="[CH3:1][C+:2]([CH3:3])[CH3:4].[OH2:6]",
                title="Capture of the carbocation",
                text="The carbon has only three bonds and an empty orbital, "
                     "so it is flat and trigonal. Water attacks with a lone "
                     "pair. It can come from above or below with no "
                     "preference at all, and that is the whole reason SN1 "
                     "scrambles stereochemistry.",
                arrows=(A(6, 2, bow=0.45),),
                lone={6: 2},
                labels=({"atom": 2, "text": "+"},),
            ),
            Step(
                smiles="[CH3:1][C:2]([CH3:3])([CH3:4])[OH2+:6]",
                title="Loss of a proton",
                text="The oxygen is now positively charged and holding a "
                     "proton it does not want. Another water molecule takes "
                     "it, giving the neutral alcohol.",
                arrows=(A(6, 2, bow=0.0),),
                labels=({"atom": 6, "text": "+"},),
            ),
        ],
    ),

    # ======================================================================
    Mech(
        id="e2",
        name="Elimination, E2",
        family="elimination",
        summary="One step. A base removes a proton while the leaving group "
                "departs from the neighbouring carbon, and a double bond "
                "appears between them.",
        attack="The base takes a hydrogen from the carbon next door, not "
               "from the carbon bearing the leaving group. For the new pi "
               "bond to form, that hydrogen and the leaving group must lie "
               "in the same plane and point in opposite directions. In a "
               "ring this requirement decides which product is even "
               "possible.",
        sources=REF,
        steps=[
            Step(
                smiles="[CH3:7][CH2:8][O-:1].[CH3:2][CH2:3][CH:4]"
                       "([CH3:5])[Br:6]",
                title="Three bonds move at once",
                text="Ethoxide removes a proton from the carbon adjacent to "
                     "the one carrying bromine. Those electrons swing down "
                     "to form the pi bond, and the bromine leaves with the "
                     "electrons of its own bond. All of it happens in one "
                     "motion.",
                arrows=(A(1, 3, bow=0.45),
                        A((3, 4), (3, 4), bow=0.0),
                        A((4, 6), 6, bow=-0.4)),
                lone={1: 3},
            ),
            Step(
                smiles="[CH3:2][CH:3]=[CH:4][CH3:5].[Br-:6]",
                title="The more substituted alkene wins",
                text="Where two different protons could have been removed, "
                     "the one giving the more substituted double bond is "
                     "usually preferred, because that alkene is the more "
                     "stable. A bulky base reverses the preference by being "
                     "unable to reach the crowded proton.",
                lone={6: 4},
            ),
        ],
    ),

    # ======================================================================
    Mech(
        id="markovnikov",
        name="Electrophilic addition of HBr",
        family="addition",
        summary="The double bond attacks the acid, not the other way round. "
                "Which carbon ends up with the bromine is decided by which "
                "carbocation is more stable.",
        attack="An alkene is electron-rich: the pi electrons sit above and "
               "below the plane and are loosely held. They act as the "
               "nucleophile. The proton adds to whichever carbon leaves the "
               "positive charge on the better-substituted neighbour, and "
               "that, rather than any rule about counting hydrogens, is "
               "what Markovnikov's observation really reflects.",
        sources=REF,
        steps=[
            Step(
                smiles="[CH3:1][CH:2]=[CH2:3].[H:4][Br:5]",
                title="The pi bond attacks the proton",
                text="Hydrogen bromide is polarised, with the hydrogen "
                     "partly positive. The alkene's pi electrons reach out "
                     "to it. They go to the terminal carbon, which leaves "
                     "the positive charge on the middle carbon where two "
                     "alkyl groups can stabilise it.",
                arrows=(A((2, 3), 4, bow=0.4), A((4, 5), 5, bow=-0.35)),
                labels=({"atom": 4, "text": "\u03b4+"},
                        {"atom": 5, "text": "\u03b4\u2212"}),
            ),
            Step(
                smiles="[CH3:1][CH+:2][CH3:3].[Br-:5]",
                title="The bromide closes in",
                text="A secondary carbocation, stabilised by the two carbons "
                     "attached to it. Bromide adds to it. Had the proton "
                     "gone the other way, the charge would have sat on a "
                     "primary carbon with far less help, and that path is "
                     "correspondingly slower.",
                arrows=(A(5, 2, bow=0.4),),
                lone={5: 4},
                labels=({"atom": 2, "text": "+"},),
            ),
            Step(
                smiles="[CH3:1][CH:2]([CH3:3])[Br:5]",
                title="Product",
                text="Bromine sits on the more substituted carbon. Note that "
                     "the carbocation was flat, so if this carbon were a "
                     "stereocentre both configurations would form.",
                lone={5: 3},
            ),
        ],
    ),

    # ======================================================================
    Mech(
        id="carbonyl-addition",
        name="Nucleophilic addition to a carbonyl",
        family="addition",
        summary="The carbonyl carbon is short of electrons and flat. A "
                "nucleophile adds to it and the carbon becomes tetrahedral.",
        attack="Oxygen pulls electron density away from the carbon, so the "
               "carbon is the electrophilic site and the oxygen the "
               "nucleophilic one. The nucleophile does not approach in the "
               "plane of the molecule but at roughly 107 degrees to it, "
               "coming down onto the face of the flat carbon.",
        sources=REF,
        steps=[
            Step(
                smiles="[CH3:1][CH:2]=[O:3].[C-:4]#[N:5]",
                title="Addition",
                text="Cyanide brings its lone pair to the carbonyl carbon. "
                     "The pi electrons are pushed up onto the oxygen, which "
                     "can hold a negative charge comfortably.",
                arrows=(A(4, 2, bow=0.45), A((2, 3), 3, bow=-0.35)),
                lone={4: 1, 3: 2},
                labels=({"atom": 2, "text": "\u03b4+"},
                        {"atom": 3, "text": "\u03b4\u2212"}),
            ),
            Step(
                smiles="[CH3:1][CH:2]([O-:3])[C:4]#[N:5]",
                title="The alkoxide",
                text="The carbon is now tetrahedral and the charge sits on "
                     "oxygen. If the starting carbonyl had two different "
                     "groups, this carbon is a new stereocentre, and since "
                     "the nucleophile could approach either face, both "
                     "configurations form in equal amount.",
                lone={3: 3},
            ),
            Step(
                smiles="[CH3:1][CH:2]([OH:3])[C:4]#[N:5]",
                title="Protonation",
                text="A proton source gives the cyanohydrin. The nitrile can "
                     "then be hydrolysed to a carboxylic acid, which is why "
                     "this reaction is useful for lengthening a chain by one "
                     "carbon.",
                lone={3: 2},
            ),
        ],
    ),

    # ======================================================================
    Mech(
        id="radical-chlorination",
        name="Radical chlorination of methane",
        family="radical",
        summary="Single electrons move, not pairs. Every arrow here has "
                "half a head.",
        attack="Nothing here is a nucleophile or an electrophile. A chlorine "
               "atom with an unpaired electron abstracts a hydrogen, and the "
               "resulting carbon radical attacks chlorine in turn, "
               "regenerating a chlorine atom. Because each step makes a new "
               "radical, one initiation event can consume thousands of "
               "molecules.",
        sources=REF,
        steps=[
            Step(
                smiles="[Cl:1][Cl:2]",
                title="Initiation",
                text="Ultraviolet light breaks the chlorine-chlorine bond "
                     "evenly, one electron going each way. Two half-headed "
                     "arrows, because two single electrons move "
                     "independently. This is the only step that needs an "
                     "outside energy source.",
                arrows=(A((1, 2), 1, bow=0.45, kind="single"),
                        A((1, 2), 2, bow=-0.45, kind="single")),
            ),
            Step(
                smiles="[CH4:3].[Cl:1]",
                title="Propagation, first half",
                text="The chlorine atom takes a hydrogen from methane. One "
                     "electron from the C-H bond goes to the hydrogen, the "
                     "other stays on the carbon, which becomes a methyl "
                     "radical.",
                arrows=(A(3, 1, bow=0.4, kind="single"),),
            ),
            Step(
                smiles="[CH3:3].[Cl:1][Cl:2]",
                title="Propagation, second half",
                text="The methyl radical attacks chlorine, taking one atom "
                     "and releasing a new chlorine atom. That atom goes back "
                     "to the previous step, and the chain continues. Stopping "
                     "it requires two radicals to meet, which is rare.",
                arrows=(A(3, 1, bow=0.4, kind="single"),
                        A((1, 2), 2, bow=-0.4, kind="single")),
            ),
        ],
    ),

    # ======================================================================
    Mech(
        id="ester-hydrolysis-base",
        name="Base hydrolysis of an ester",
        family="substitution",
        summary="Addition first, elimination second. The carbonyl is "
                "attacked, becomes tetrahedral, then collapses back and "
                "expels the alcohol.",
        attack="Substitution at a carbonyl does not happen the way it does "
               "at a saturated carbon. There is no backside attack, because "
               "the carbonyl offers a much easier route: the pi bond can "
               "absorb the incoming pair temporarily and hand it back. The "
               "leaving group departs in a separate step, from a "
               "tetrahedral intermediate that genuinely exists.",
        sources=REF,
        steps=[
            Step(
                smiles="[CH3:1][C:2](=[O:3])[O:4][CH2:5][CH3:6].[OH-:7]",
                title="Hydroxide adds",
                text="Hydroxide attacks the carbonyl carbon. The pi "
                     "electrons move up onto the oxygen.",
                arrows=(A(7, 2, bow=0.45), A((2, 3), 3, bow=-0.35)),
                lone={7: 3},
                labels=({"atom": 2, "text": "\u03b4+"},),
            ),
            Step(
                smiles="[CH3:1][C:2]([O-:3])([OH:7])[O:4][CH2:5][CH3:6]",
                title="The tetrahedral intermediate",
                text="Unlike the SN2 transition state, this is a real "
                     "species with a normal set of bonds. It is unstable and "
                     "short-lived, but it exists, and that difference "
                     "matters for how the reaction responds to conditions.",
                arrows=(A(3, (2, 3), bow=0.4), A((2, 4), 4, bow=-0.4)),
                lone={3: 3},
            ),
            Step(
                smiles="[CH3:1][C:2](=[O:3])[OH:7].[O-:4][CH2:5][CH3:6]",
                title="Collapse and expulsion",
                text="The oxygen pushes its electrons back down to reform "
                     "the double bond, and the alkoxide is expelled. It "
                     "immediately takes the proton from the acid, which is "
                     "why base hydrolysis consumes the base rather than "
                     "catalysing the reaction, and why it cannot be "
                     "reversed.",
                lone={4: 3},
            ),
        ],
    ),
]
