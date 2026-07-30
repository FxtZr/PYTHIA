"""The glossary.

Definitions written for someone who has met the word and not yet got hold
of it. Where two terms are routinely confused, the entry says so and says
what the difference is: that pairing is most of the value here.

The build checks that every cross-reference names a term that exists and
that every molecule cited is in the library. A glossary with a dead
cross-reference is worse than one without it, because the reader assumes
they have missed something.
"""

from collections import namedtuple

Term = namedtuple("Term", "term aka definition section see molecules",
                  defaults=(None, (), ()))

S_STEREO = "Stereochemistry"
S_NAME = "Nomenclature"
S_MECH = "Mechanisms"
S_BIO = "Biochemistry"
S_CALC = "Calculation"
S_SPEC = "Spectroscopy"

SOURCES = ("iupac-bluebook-2013", "cip-1966", "clayden", "lehninger",
           "silverstein")


GLOSSARY = [

    # ---- stereochemistry -------------------------------------------------
    Term("Chirality", "handedness",
         "The property of not being superimposable on your own mirror "
         "image. A chiral object and its reflection are distinct objects, "
         "however you turn them.",
         S_STEREO, see=("Enantiomer", "Stereocentre", "Achiral"),
         molecules=("bromochlorofluoromethane-r",)),

    Term("Achiral", None,
         "Superimposable on its own mirror image. The quickest test is to "
         "look for an internal mirror plane: if one exists, the molecule is "
         "achiral no matter how many stereocentres it has.",
         S_STEREO, see=("Chirality", "Meso compound")),

    Term("Stereocentre", "stereogenic centre, chiral centre",
         "An atom at which swapping two substituents gives a different "
         "stereoisomer. For carbon this means four different groups, where "
         "different is judged by exploring each branch outward, not by the "
         "first atom alone.",
         S_STEREO, see=("Chirality", "CIP rules"),
         molecules=("alanine-s", "glycine")),

    Term("Enantiomer", None,
         "One of a pair of stereoisomers that are mirror images of each "
         "other. They share every physical property measurable in an "
         "achiral environment and differ only when something chiral "
         "encounters them.",
         S_STEREO, see=("Diastereomer", "Racemate", "Chirality"),
         molecules=("carvone-r", "carvone-s")),

    Term("Diastereomer", None,
         "A stereoisomer that is not a mirror image of the one it is "
         "compared with. Diastereomers are simply different compounds: "
         "different melting points, different solubility, separable by "
         "ordinary means.",
         S_STEREO, see=("Enantiomer", "Epimer"),
         molecules=("ephedrine", "pseudoephedrine")),

    Term("Epimer", None,
         "A diastereomer differing at exactly one stereocentre out of "
         "several. Common in sugar chemistry, where it is often the only "
         "difference between two named sugars.",
         S_STEREO, see=("Diastereomer", "Anomeric carbon")),

    Term("Meso compound", None,
         "A molecule containing stereocentres that is nevertheless achiral, "
         "because an internal mirror plane makes one half cancel the other. "
         "The standard demonstration that counting stereocentres is not a "
         "test for chirality.",
         S_STEREO, see=("Achiral", "Stereocentre"),
         molecules=("tartaric-acid-meso",)),

    Term("Racemate", "racemic mixture",
         "An equal mixture of two enantiomers. It does not rotate polarised "
         "light, because the two halves cancel, and it is what an ordinary "
         "synthesis produces unless something chiral steers it.",
         S_STEREO, see=("Enantiomer", "Optical rotation")),

    Term("CIP rules", "Cahn-Ingold-Prelog rules",
         "The procedure for ranking the substituents at a stereocentre. "
         "Compare atomic numbers at the first atom; where those tie, move "
         "one sphere out and compare the sets found there. Multiple bonds "
         "contribute duplicate atoms.",
         S_STEREO, see=("R and S", "E and Z", "Duplicate atom"),
         molecules=("glyceraldehyde-r",)),

    Term("Duplicate atom", "phantom atom",
         "In CIP ranking, a double bond is treated as though the atom were "
         "bonded to two copies of its partner, and a triple bond to three. "
         "The duplicate carries no substituents of its own. Omit this and "
         "every carbonyl ranks below every alcohol.",
         S_STEREO, see=("CIP rules",)),

    Term("R and S", None,
         "The labels for configuration at a stereocentre. With the lowest "
         "priority substituent pointing away, a clockwise reading of the "
         "other three is R and anticlockwise is S. They describe an "
         "arrangement, and predict nothing about optical rotation.",
         S_STEREO, see=("CIP rules", "Optical rotation", "D and L"),
         molecules=("alanine-s", "alanine-r")),

    Term("E and Z", None,
         "The labels for geometry at a double bond, from the German "
         "entgegen and zusammen. The higher priority group on each carbon "
         "is compared: same side is Z, opposite sides is E. They replace "
         "cis and trans, which have no defined answer when all four groups "
         "differ.",
         S_STEREO, see=("CIP rules", "Cis and trans"),
         molecules=("but-2-ene-z", "but-2-ene-ambiguous")),

    Term("Cis and trans", None,
         "An older pair of labels for double bond geometry, meaning same "
         "side and opposite sides. Adequate when each carbon carries one "
         "substituent and a hydrogen, undefined otherwise.",
         S_STEREO, see=("E and Z",)),

    Term("D and L", None,
         "A historical classification of sugars and amino acids, based on "
         "comparison with glyceraldehyde rather than on any direct "
         "measurement. It does not map onto R and S in any simple way, and "
         "it says nothing about the direction of optical rotation.",
         S_STEREO, see=("R and S", "Optical rotation")),

    Term("Optical rotation", None,
         "The angle by which a substance turns the plane of polarised "
         "light, written (+) for clockwise and (-) for anticlockwise. A "
         "measured physical property, not derivable from the R or S label.",
         S_STEREO, see=("R and S", "Racemate")),

    Term("Configuration", None,
         "The fixed spatial arrangement at a stereocentre or double bond. "
         "Changing it requires breaking a bond.",
         S_STEREO, see=("Conformation", "R and S", "Wedge and hash",
                        "Stereospecific and stereoselective")),

    Term("Conformation", None,
         "An arrangement reached by rotating single bonds. Conformations "
         "interconvert billions of times a second at room temperature and "
         "can never be separated into different bottles. The distinction "
         "from configuration is the one most often blurred.",
         S_STEREO, see=("Configuration",),
         molecules=("butane", "cyclohexane")),

    Term("Wedge and hash", "bold and dashed bonds",
         "The convention for depth in a flat drawing. A solid wedge comes "
         "towards the reader, a hashed bond recedes. The wide end of the "
         "wedge is the end nearer to you.",
         S_STEREO, see=("Configuration",)),

    Term("Anomeric carbon", None,
         "The carbon that becomes a new stereocentre when a sugar closes "
         "into a ring, carrying the hydroxyl derived from the original "
         "carbonyl. Its two configurations are called alpha and beta.",
         S_STEREO, see=("Stereocentre",), molecules=("glucose-beta",)),

    Term("Stereospecific and stereoselective", None,
         "A stereospecific reaction gives a different stereochemical "
         "outcome from different stereoisomeric starting materials, because "
         "the mechanism demands it. A stereoselective one favours a "
         "particular outcome without being forced to. The words are not "
         "interchangeable.",
         S_STEREO, see=("Configuration",)),

    # ---- nomenclature ---------------------------------------------------
    Term("Parent chain", "parent hydride",
         "The chain of carbons chosen as the backbone of a name. Normally "
         "the longest, but it must contain the principal characteristic "
         "group even where a longer chain exists elsewhere.",
         S_NAME, see=("Principal characteristic group", "Locant"),
         molecules=("3-ethyl-2-methylhexane",)),

    Term("Principal characteristic group", None,
         "The one functional group that takes the suffix. Chosen by the "
         "order of seniority; every other group in the molecule is demoted "
         "to its prefix form.",
         S_NAME, see=("Suffix and prefix", "Parent chain"),
         molecules=("3-oxobutanoic-acid",)),

    Term("Suffix and prefix", None,
         "Most functional groups have two written forms: a suffix for when "
         "they win the seniority contest, and a prefix for when they lose. "
         "A ketone is -one or oxo-, an alcohol is -ol or hydroxy-. Knowing "
         "only one form of each makes the seniority table unusable.",
         S_NAME, see=("Principal characteristic group",),
         molecules=("4-hydroxybenzaldehyde",)),

    Term("Locant", None,
         "The number giving the position of something on the parent chain. "
         "Placed immediately before the part of the name it qualifies, "
         "which is why current usage is but-1-ene rather than 1-butene.",
         S_NAME, see=("Parent chain", "Multiplying prefix"),
         molecules=("but-1-ene",)),

    Term("Multiplying prefix", None,
         "Di, tri, tetra and the rest, marking how many identical "
         "substituents there are. Not counted when substituents are put in "
         "alphabetical order: triethyl files under E.",
         S_NAME, see=("Suffix and prefix",),
         molecules=("2-2-4-trimethylpentane",)),

    Term("Retained name", None,
         "A traditional name that the current recommendations explicitly "
         "permit rather than merely tolerate: benzoic acid, acetic acid and "
         "a short list of others.",
         S_NAME, see=("Preferred IUPAC name",),
         molecules=("benzoic-acid",)),

    Term("Preferred IUPAC name", "PIN",
         "The single name selected by the 2013 recommendations where "
         "several correct names exist. Intended for contexts needing one "
         "unambiguous form, such as legislation and patents, rather than to "
         "outlaw the alternatives.",
         S_NAME, see=("Retained name",)),

    # ---- mechanisms ------------------------------------------------------
    Term("Nucleophile", None,
         "A species that donates a pair of electrons to form a bond. "
         "Nucleophiles are electron-rich: anions, lone pairs, and pi bonds "
         "all qualify.",
         S_MECH, see=("Electrophile", "Leaving group", "Curly arrow")),

    Term("Electrophile", None,
         "A species that accepts a pair of electrons. Electron-poor: a "
         "positively charged centre, or an atom made partly positive by a "
         "more electronegative neighbour.",
         S_MECH, see=("Nucleophile", "Carbocation")),

    Term("Leaving group", None,
         "The fragment that departs taking a bonding pair with it. Good "
         "leaving groups are stable as anions, which usually means they are "
         "the conjugate bases of strong acids.",
         S_MECH, see=("Nucleophile",)),

    Term("Curly arrow", "curved arrow",
         "The notation for electron movement. A full head moves a pair, a "
         "half head, called a fishhook, moves one. The arrow starts where "
         "the electrons are and ends where they go.",
         S_MECH, see=("Nucleophile", "Radical")),

    Term("Homolysis and heterolysis", None,
         "Two ways a bond can break. Homolysis splits the pair evenly and "
         "gives two radicals; heterolysis gives both electrons to one side "
         "and produces ions. Fishhook arrows go with the first, full arrows "
         "with the second.",
         S_MECH, see=("Radical", "Curly arrow")),

    Term("Carbocation", None,
         "A carbon with only three bonds and a positive charge. Flat and "
         "trigonal, which is why a nucleophile can approach either face and "
         "why reactions passing through one lose stereochemical "
         "information.",
         S_MECH, see=("Electrophile", "Intermediate", "Markovnikov's rule")),

    Term("Radical", None,
         "A species with an unpaired electron. Drawn with a single dot, and "
         "its reactions are drawn with fishhook arrows.",
         S_MECH, see=("Homolysis and heterolysis", "Curly arrow")),

    Term("Intermediate", None,
         "A real species with a normal set of bonds that exists between two "
         "steps. Short-lived, but it sits in an energy well and could in "
         "principle be detected.",
         S_MECH, see=("Transition state",)),

    Term("Transition state", None,
         "The highest point on the path between two species. It has partial "
         "bonds, exists for a single vibration, and cannot be isolated or "
         "written as a structural formula. Not the same thing as an "
         "intermediate.",
         S_MECH, see=("Intermediate",)),

    Term("Rate-determining step", None,
         "The slowest step in a sequence, which sets the overall rate. Only "
         "species involved up to and including it appear in the rate "
         "equation, which is how SN1 and SN2 are told apart "
         "experimentally.",
         S_MECH, see=("Intermediate", "Zaitsev's rule")),

    Term("Markovnikov's rule", None,
         "In adding H-X across an alkene, the hydrogen goes to the carbon "
         "that leaves the positive charge on the better-stabilised "
         "neighbour. Usually stated as a rule about counting hydrogens; "
         "better understood as a statement about carbocation stability.",
         S_MECH, see=("Carbocation",)),

    Term("Zaitsev's rule", None,
         "In elimination, the more substituted alkene is usually favoured, "
         "being the more stable. A bulky base reverses the preference by "
         "being unable to reach the crowded proton.",
         S_MECH, see=("Rate-determining step",)),

    # ---- biochemistry ----------------------------------------------------
    Term("Cofactor", None,
         "A non-protein component an enzyme needs in order to work. A metal "
         "ion is a cofactor; an organic one is usually called a coenzyme.",
         S_BIO, see=("Coenzyme", "EC number", "Substrate-level phosphorylation")),

    Term("Coenzyme", None,
         "An organic cofactor, often derived from a vitamin. NAD comes from "
         "niacin, FAD from riboflavin, coenzyme A from pantothenate. This "
         "is why vitamin deficiencies show up as metabolic failures.",
         S_BIO, see=("Cofactor", "Indispensable amino acid"),
         molecules=("riboflavin", "thiamine")),

    Term("EC number", None,
         "The four-part code assigned to an enzyme by the IUBMB, "
         "classifying it by the reaction it catalyses. The first digit is "
         "the class: 1 oxidoreductase, 2 transferase, 3 hydrolase, 4 lyase, "
         "5 isomerase, 6 ligase, 7 translocase.",
         S_BIO, see=("Cofactor",)),

    Term("Committed step", None,
         "The first step after which the intermediate has no route out of "
         "the pathway. Almost always where regulation is applied, because "
         "controlling anything earlier would affect other pathways too.",
         S_BIO, see=("Rate-limiting step", "Allosteric regulation")),

    Term("Rate-limiting step", None,
         "The slowest step of a pathway, which sets the overall flux. Often "
         "but not always the committed step.",
         S_BIO, see=("Committed step",)),

    Term("Allosteric regulation", None,
         "Control of an enzyme by a molecule binding somewhere other than "
         "the active site, changing the enzyme's shape and so its activity. "
         "The mechanism behind most feedback inhibition.",
         S_BIO, see=("Committed step",)),

    Term("Substrate-level phosphorylation", None,
         "Making ATP by transferring a phosphate directly from a "
         "high-energy intermediate, rather than through the respiratory "
         "chain. The only route available without oxygen.",
         S_BIO, see=("Cofactor",)),

    Term("Indispensable amino acid", "essential amino acid",
         "One of the nine amino acids humans cannot synthesise and must "
         "obtain from food. A further six are conditionally indispensable: "
         "the body can make them, but only from a precursor that must "
         "itself be supplied.",
         S_BIO, see=("Coenzyme",),
         molecules=("leucine-aa", "tyrosine-aa")),

    # ---- calculation -----------------------------------------------------
    Term("Molar mass", None,
         "The mass of one mole, obtained by summing standard atomic "
         "weights. Those weights are averages over natural isotope "
         "abundance, so molar mass is an average too.",
         S_CALC, see=("Monoisotopic mass",)),

    Term("Monoisotopic mass", "exact mass",
         "The mass of the single most abundant isotopic species. What a "
         "high-resolution mass spectrometer reports. Glucose is 180.156 by "
         "molar mass and 180.063 monoisotopic, and the gap grows with "
         "size.",
         S_CALC, see=("Molar mass",)),

    Term("Limiting reagent", None,
         "The reactant that runs out first, found by dividing each "
         "reactant's moles by its stoichiometric coefficient and taking the "
         "smallest. It sets how much product can form.",
         S_CALC, see=("Atom economy",)),

    Term("Atom economy", None,
         "The proportion of reactant mass that ends up in the wanted "
         "product, as a percentage. A measure of the reaction on paper, "
         "counting no solvent and no workup.",
         S_CALC, see=("E factor", "Limiting reagent")),

    Term("E factor", None,
         "Kilograms of waste per kilogram of product, counting everything "
         "that leaves the process. Usually far worse than atom economy "
         "suggests, and the difference is mostly solvent.",
         S_CALC, see=("Atom economy",)),

    Term("pKa", None,
         "The negative logarithm of the acid dissociation constant. A lower "
         "pKa means a stronger acid. At a pH equal to the pKa, the acid and "
         "its conjugate base are present in equal amounts.",
         S_CALC, see=("Buffer",)),

    Term("Buffer", None,
         "A solution resisting change in pH, made from a weak acid and its "
         "conjugate base. Works well within about one pH unit of the pKa; "
         "outside that range one component is too scarce to absorb "
         "anything.",
         S_CALC, see=("pKa",)),

    # ---- spectroscopy ----------------------------------------------------
    Term("Chemical shift", "delta",
         "Where a signal appears, in parts per million relative to a "
         "reference. Quoted in ppm rather than hertz so the number is the "
         "same on any instrument, whatever its field strength.",
         S_SPEC, see=("Shielding", "Coupling constant", "Exchangeable proton")),

    Term("Shielding", "deshielding",
         "Electrons around a nucleus generate a small opposing field, so a "
         "nucleus with more electron density around it needs a stronger "
         "applied field and appears upfield. Pull that density away with an "
         "electronegative neighbour and the signal moves downfield. Almost "
         "every entry in a shift table is this one idea.",
         S_SPEC, see=("Chemical shift", "Ring current")),

    Term("Ring current", None,
         "Pi electrons circulating around an aromatic ring generate a field "
         "that adds to the applied one outside the ring and opposes it "
         "inside. This is why aromatic protons sit near 7 ppm rather than "
         "near 5, and it is a different effect from ordinary "
         "electronegativity.",
         S_SPEC, see=("Shielding",)),

    Term("Coupling constant", "J",
         "The separation between the lines of a split signal, in hertz. "
         "Coupling is mutual: if one proton splits another, the second "
         "splits the first by exactly the same amount, and matching those "
         "values is how coupled partners are identified. Unlike chemical "
         "shift, J does not change with field strength.",
         S_SPEC, see=("Multiplicity", "Chemical shift")),

    Term("Multiplicity", "the n+1 rule",
         "A signal split by n equivalent neighbours gives n+1 lines, with "
         "intensities from Pascal's triangle. The rule assumes those "
         "neighbours are equivalent to each other; when they are not, the "
         "splittings multiply rather than add, and two different neighbours "
         "give four lines instead of three.",
         S_SPEC, see=("Coupling constant", "Equivalent protons")),

    Term("Integration", None,
         "The area under a signal, proportional to how many protons produce "
         "it. It gives ratios, not absolute counts: a 2:3 integration could "
         "be two and three protons or four and six, and the molecular "
         "formula settles which.",
         S_SPEC, see=("Equivalent protons",)),

    Term("Equivalent protons", None,
         "Protons in identical environments, which give one signal between "
         "them. Equivalence follows from symmetry, and spotting it is what "
         "turns a count of signals into structural information: three "
         "signals for eight protons says far more than eight protons does.",
         S_SPEC, see=("Integration", "Multiplicity")),

    Term("Exchangeable proton", None,
         "A proton on oxygen or nitrogen, which swaps with the solvent fast "
         "enough that its signal is broad and its position unreliable. "
         "Shaking the sample with heavy water replaces it and the signal "
         "vanishes, which is the standard way to confirm an O-H or N-H.",
         S_SPEC, see=("Chemical shift",)),

    Term("Wavenumber", None,
         "The unit of the infrared axis, in reciprocal centimetres. "
         "Proportional to energy, unlike wavelength, which is why infrared "
         "spectra are plotted this way and conventionally run from high to "
         "low across the page.",
         S_SPEC, see=("Fingerprint region",)),

    Term("Fingerprint region", None,
         "Below about 1400 cm-1, where absorptions come from whole-molecule "
         "vibrations rather than individual bonds. Peaks there cannot "
         "usually be assigned, but the pattern is characteristic enough to "
         "match a compound against a reference spectrum.",
         S_SPEC, see=("Wavenumber",)),

    Term("Molecular ion", "M",
         "The peak from the intact molecule having lost one electron. Its "
         "mass gives the molecular mass, and its absence is itself "
         "informative: alcohols often fragment so readily that no molecular "
         "ion survives.",
         S_SPEC, see=("Base peak", "Neutral loss", "Nitrogen rule")),

    Term("Base peak", None,
         "The tallest peak in a mass spectrum, set to 100 % and used to "
         "scale the rest. It marks the most stable fragment, not the "
         "molecule, and the two are rarely the same.",
         S_SPEC, see=("Molecular ion",)),

    Term("Neutral loss", None,
         "The difference between two peaks, corresponding to an uncharged "
         "fragment that left. Reading the gaps is usually more informative "
         "than reading the peaks: a gap of 18 is water, 28 is carbon "
         "monoxide or ethene, 31 is methoxy.",
         S_SPEC, see=("Molecular ion", "Base peak")),

    Term("Nitrogen rule", None,
         "An even nominal molecular mass means an even number of nitrogen "
         "atoms, including none; an odd mass means an odd number. Nitrogen "
         "is the only common element whose usual valence and mass have "
         "opposite parity, which is where the rule comes from.",
         S_SPEC, see=("Molecular ion", "Degrees of unsaturation")),

    Term("Degrees of unsaturation", "double bond equivalents",
         "How many rings and pi bonds a formula must contain, from "
         "(2C + 2 + N - H - X) / 2. Computed before anything else is "
         "looked at: four or more usually means a benzene ring, and zero "
         "rules out every carbonyl at a stroke.",
         S_SPEC, see=("Nitrogen rule", "Molecular ion")),
]
