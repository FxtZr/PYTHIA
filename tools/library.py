"""The PYTHIA molecule library.

Adding a molecule means adding one entry here and re-running
build_molecules.py. Nothing else needs to change.

Fields
------
id       stable slug, used in URLs and cross-references
smiles   the structure. Mind the atom order inside a [C@@H]: swapping two
         neighbours inverts the configuration, so never trust a hand-typed
         descriptor. Declare `expect` and let the build check you.
name     preferred IUPAC name where one is short enough to be useful,
         otherwise the standard name in the literature
common   the name a reader is likely to have met, or None
group    which section of the program this entry primarily serves
note     one or two sentences for someone still learning. Say the thing
         that is not obvious from the picture.
expect   the multiset of stereodescriptors this structure must produce,
         sorted, e.g. "S", "RS", "ZZZ". The build fails on disagreement.
         Omit only where the configuration is genuinely not being asserted.
tags     free labels, used for filtering and for sourced claims
sources  keys into sources.SOURCES, for claims specific to this entry
"""

from collections import namedtuple

M = namedtuple(
    "M",
    "id smiles name common group note expect tags sources",
    defaults=(None, (), ()),
)

# Applied to every entry: the geometry pipeline and the naming authority.
DATASET_SOURCES = (
    "iupac-bluebook-2013",
    "rdkit",
    "etkdg-2015",
    "mmff94",
)

# The nine indispensable amino acids, and the six the body can make only
# under favourable conditions. Both lists follow the WHO/FAO/UNU expert
# consultation, not the older "essential/non-essential" split.
INDISPENSABLE = ("who-fao-unu-935",)

LIBRARY = [

    # ---- a single stereocentre, nothing else going on --------------------
    M("bromochlorofluoromethane-r", "F[C@H](Cl)Br",
      "(R)-bromochlorofluoromethane", None, "chirality",
      "The smallest possible chiral carbon: four different atoms, no rings, "
      "no double bonds. Priority is decided entirely at the first sphere."),
    M("bromochlorofluoromethane-s", "F[C@@H](Cl)Br",
      "(S)-bromochlorofluoromethane", None, "chirality",
      "The mirror image of the R form. Same connectivity, same bond lengths, "
      "not superimposable."),
    M("glyceraldehyde-r", "OC[C@@H](O)C=O",
      "(R)-glyceraldehyde", "D-glyceraldehyde", "chirality",
      "The historical reference for sugar configuration. Here the ranking is "
      "settled one sphere out, not at the first atom."),
    M("glyceraldehyde-s", "OC[C@H](O)C=O",
      "(S)-glyceraldehyde", "L-glyceraldehyde", "chirality",
      "The enantiomer of D-glyceraldehyde."),
    M("alanine-s", "C[C@H](N)C(=O)O",
      "(S)-alanine", "L-alanine", "chirality",
      "Nearly every amino acid in your proteins is the S enantiomer. Cysteine "
      "is the exception, and only because sulfur outranks the carboxyl carbon."),
    M("alanine-r", "C[C@@H](N)C(=O)O",
      "(R)-alanine", "D-alanine", "chirality",
      "Found in bacterial cell walls, which is part of why some antibiotics "
      "can target bacteria and leave us alone."),
    M("glycine", "NCC(=O)O",
      "Glycine", None, "chirality",
      "Achiral, and worth staring at. The central carbon carries two "
      "hydrogens, so two of its four substituents are identical."),
    M("propan-2-ol", "CC(O)C",
      "Propan-2-ol", "Isopropanol", "chirality",
      "A common trap. C2 has four bonds and an OH, but two of those bonds go "
      "to identical methyl groups, so there is no stereocentre."),
    M("lactic-acid-s", "C[C@H](O)C(=O)O",
      "(S)-lactic acid", "L-(+)-lactic acid", "chirality",
      "What your muscles accumulate under anaerobic effort."),
    M("lactic-acid-r", "C[C@@H](O)C(=O)O",
      "(R)-lactic acid", "D-(-)-lactic acid", "chirality",
      "Produced by many bacteria, including the ones that sour milk."),
    M("butan-2-ol-r", "CC[C@@H](C)O",
      "(R)-butan-2-ol", None, "chirality",
      "A four-carbon alcohol. Deciding between the ethyl and methyl branches "
      "needs one step past the first atom."),
    M("butan-2-ol-s", "CC[C@H](C)O",
      "(S)-butan-2-ol", None, "chirality",
      "The enantiomer. Identical melting point, identical NMR in an achiral "
      "solvent, opposite rotation of polarised light."),

    # ---- chirality you can smell or feel ---------------------------------
    M("limonene-r", "CC(=C)[C@@H]1CCC(C)=CC1",
      "(R)-limonene", None, "chirality",
      "Smells of oranges. Same atoms as its mirror image, different smell, "
      "because your olfactory receptors are themselves chiral."),
    M("limonene-s", "CC(=C)[C@H]1CCC(C)=CC1",
      "(S)-limonene", None, "chirality",
      "Smells of pine and turpentine. This pair is the easiest way to make "
      "chirality feel physical rather than notational."),
    M("carvone-r", "CC1=CC[C@@H](C(=C)C)CC1=O",
      "(R)-carvone", None, "chirality",
      "Spearmint."),
    M("carvone-s", "CC1=CC[C@H](C(=C)C)CC1=O",
      "(S)-carvone", None, "chirality",
      "Caraway. One stereocentre inverted, and the smell is unrecognisable."),
    M("ibuprofen-s", "CC(C)Cc1ccc(cc1)[C@H](C)C(=O)O",
      "(S)-ibuprofen", "Dexibuprofen", "chirality",
      "The enantiomer that inhibits cyclooxygenase. Ordinary ibuprofen is "
      "sold as a mixture of both."),
    M("ibuprofen-r", "CC(C)Cc1ccc(cc1)[C@@H](C)C(=O)O",
      "(R)-ibuprofen", None, "chirality",
      "Largely inactive on the target, though the body slowly converts some "
      "of it to the S form."),
    M("thalidomide-s", "O=C1CC[C@H](N2C(=O)c3ccccc3C2=O)C(=O)N1",
      "(S)-thalidomide", None, "chirality",
      "The teratogenic enantiomer. The drug was sold as a mixture, and the "
      "two forms interconvert in the body, which is why separating them "
      "would not have made it safe."),
    M("thalidomide-r", "O=C1CC[C@@H](N2C(=O)c3ccccc3C2=O)C(=O)N1",
      "(R)-thalidomide", None, "chirality",
      "The sedative enantiomer. Racemises in vivo."),

    # ---- more than one stereocentre --------------------------------------
    M("tartaric-acid-rr", "O[C@@H](C(=O)O)[C@@H](O)C(=O)O",
      "(2R,3R)-tartaric acid", None, "diastereomers",
      "Two stereocentres, so up to four stereoisomers exist. This is the "
      "form found in grapes. It is often written L-(+), which is a trap: "
      "the L comes from an older sugar-based convention while the (+) is "
      "the measured rotation, and the two labels have no reason to agree."),
    M("tartaric-acid-ss", "O[C@H](C(=O)O)[C@H](O)C(=O)O",
      "(2S,3S)-tartaric acid", None, "diastereomers",
      "The enantiomer of the (2R,3R) form. Pasteur separated the two by hand "
      "under a microscope in 1848, which is how chirality was discovered."),
    M("tartaric-acid-meso", "O[C@H](C(=O)O)[C@@H](O)C(=O)O",
      "(2R,3S)-tartaric acid", "meso-tartaric acid", "diastereomers",
      "Two stereocentres and yet achiral. An internal mirror plane maps R "
      "onto S, so the molecule is superimposable on its own reflection."),
    M("dimethylcyclohexane-cis", "C[C@H]1CCCC[C@@H]1C",
      "cis-1,2-dimethylcyclohexane", None, "diastereomers",
      "Both methyls on the same face of the ring."),
    M("dimethylcyclohexane-trans", "C[C@H]1CCCC[C@H]1C",
      "trans-1,2-dimethylcyclohexane", None, "diastereomers",
      "Opposite faces. A diastereomer of the cis form, not an enantiomer, "
      "so it has genuinely different physical properties."),
    M("ephedrine", "CN[C@@H](C)[C@H](O)c1ccccc1",
      "(1R,2S)-ephedrine", None, "diastereomers",
      "Two adjacent stereocentres."),
    M("pseudoephedrine", "CN[C@@H](C)[C@@H](O)c1ccccc1",
      "(1S,2S)-pseudoephedrine", None, "diastereomers",
      "A diastereomer of ephedrine, and a different drug with a different "
      "profile. Stereochemistry is not a detail here."),
    M("glucose-open", "OC[C@@H](O)[C@H](O)[C@@H](O)[C@H](O)C=O",
      "D-glucose (open chain)", None, "diastereomers",
      "Four stereocentres, so sixteen possible stereoisomers. Only a few "
      "occur in nature."),
    M("glucose-beta", "OC[C@H]1O[C@@H](O)[C@H](O)[C@@H](O)[C@@H]1O",
      "beta-D-glucopyranose", None, "diastereomers",
      "The ring form, which is what glucose mostly is in water. Closing the "
      "ring creates a fifth stereocentre at the anomeric carbon."),

    # ---- double bond geometry -------------------------------------------
    M("but-2-ene-e", "C/C=C/C",
      "(E)-but-2-ene", "trans-2-butene", "alkene-geometry",
      "The two methyls sit on opposite sides. E and Z are defined by CIP "
      "priority on each carbon, which is why they are preferred over cis "
      "and trans."),
    M("but-2-ene-z", "C/C=C\\C",
      "(Z)-but-2-ene", "cis-2-butene", "alkene-geometry",
      "Same side. Slightly less stable than E because the methyls crowd "
      "each other."),
    M("fumaric-acid", "OC(=O)/C=C/C(=O)O",
      "(E)-butenedioic acid", "Fumaric acid", "alkene-geometry",
      "An intermediate in the citric acid cycle. Melts near 287 C."),
    M("maleic-acid", "OC(=O)/C=C\\C(=O)O",
      "(Z)-butenedioic acid", "Maleic acid", "alkene-geometry",
      "The Z isomer of the same acid, and it melts near 135 C. Geometry "
      "alone accounts for a 150-degree difference."),
    M("cinnamic-acid-e", "OC(=O)/C=C/c1ccccc1",
      "(E)-cinnamic acid", None, "alkene-geometry",
      "The form found in cinnamon bark."),
    M("cinnamic-acid-z", "OC(=O)/C=C\\c1ccccc1",
      "(Z)-cinnamic acid", None, "alkene-geometry",
      "Less stable, and it cyclises far more readily, which is a useful "
      "reminder that geometry controls reactivity."),
    M("but-2-ene-ambiguous", "CC(Cl)=C(Cl)C",
      "2,3-dichlorobut-2-ene", None, "alkene-geometry",
      "Here cis and trans are genuinely ambiguous, because each carbon "
      "carries a methyl and a chlorine. Only E/Z with CIP priority is "
      "well defined."),

    # ---- conformation, not configuration --------------------------------
    M("ethane", "CC",
      "Ethane", None, "conformation",
      "Rotation about the single bond costs about 12 kJ/mol. Staggered and "
      "eclipsed are conformations, interconverting billions of times a "
      "second at room temperature."),
    M("butane", "CCCC",
      "Butane", None, "conformation",
      "Rotating the central bond gives anti and gauche arrangements. Anti "
      "is the more stable by roughly 3.8 kJ/mol."),
    M("cyclohexane", "C1CCCCC1",
      "Cyclohexane", None, "conformation",
      "The ring is not flat. The chair form keeps every bond angle near "
      "111 degrees and every neighbouring pair staggered."),

    # ---- nomenclature ---------------------------------------------------
    M("2-methylbutane", "CC(C)CC",
      "2-Methylbutane", "Isopentane", "nomenclature",
      "Longest chain is four carbons, so butane. The methyl gets the lowest "
      "possible locant."),
    M("2-2-4-trimethylpentane", "CC(C)CC(C)(C)C",
      "2,2,4-Trimethylpentane", "Isooctane", "nomenclature",
      "The reference point for the 100 mark on the octane scale."),
    M("3-ethyl-2-methylhexane", "CCCC(CC)C(C)C",
      "3-Ethyl-2-methylhexane", None, "nomenclature",
      "Two different substituents, cited alphabetically: ethyl before "
      "methyl, regardless of their locants."),
    M("but-1-ene", "C=CCC",
      "But-1-ene", None, "nomenclature",
      "The locant goes immediately before the part of the name it applies "
      "to, which is why modern usage is but-1-ene rather than 1-butene."),
    M("but-1-yne", "C#CCC",
      "But-1-yne", None, "nomenclature",
      "A triple bond takes the -yne suffix."),
    M("cyclohexanol", "OC1CCCCC1",
      "Cyclohexanol", None, "nomenclature",
      "On a ring, the carbon carrying the principal group is C1 by "
      "definition, so no locant is needed."),
    M("cyclohexanone", "O=C1CCCCC1",
      "Cyclohexanone", None, "nomenclature",
      "A ketone on a ring."),
    M("ethyl-acetate", "CCOC(C)=O",
      "Ethyl acetate", "Ethyl ethanoate", "nomenclature",
      "Esters are named alkyl first, then the acid part with -oate. The "
      "systematic name is ethyl ethanoate."),
    M("acetamide", "CC(N)=O",
      "Acetamide", "Ethanamide", "nomenclature",
      "The amide suffix outranks almost everything else."),
    M("acetonitrile", "CC#N",
      "Acetonitrile", "Ethanenitrile", "nomenclature",
      "The nitrile carbon counts as part of the parent chain."),
    M("benzoic-acid", "OC(=O)c1ccccc1",
      "Benzoic acid", None, "nomenclature",
      "A retained name. Systematic nomenclature permits several such."),
    M("4-hydroxybenzaldehyde", "O=Cc1ccc(O)cc1",
      "4-Hydroxybenzaldehyde", None, "nomenclature",
      "Two groups compete. The aldehyde outranks the alcohol, so it takes "
      "the suffix and the alcohol becomes a hydroxy prefix."),
    M("3-oxobutanoic-acid", "CC(=O)CC(=O)O",
      "3-Oxobutanoic acid", "Acetoacetic acid", "nomenclature",
      "The acid wins the suffix; the ketone is demoted to an oxo prefix. "
      "One of the ketone bodies produced in fasting."),
    M("2-amino-4-methylpentanoic-acid", "CC(C)C[C@H](N)C(=O)O",
      "(S)-2-Amino-4-methylpentanoic acid", "L-leucine", "nomenclature",
      "A full systematic name including the stereodescriptor, which is "
      "cited at the very front of the name."),
    # ======================================================================
    # Molecules of the living world
    # ======================================================================

    # ---- the twenty proteinogenic amino acids ----------------------------
    # All are S except cysteine, which is R. Not because cysteine is built
    # differently, but because sulfur outranks the carboxyl carbon under
    # CIP rule 1, so the same spatial arrangement earns the opposite letter.
    # A good reminder that R/S is a naming convention, not a shape.

    M("glycine-aa", "NCC(=O)O",
      "Glycine", "Gly, G", "amino-acids",
      "The only proteinogenic amino acid with no stereocentre: two hydrogens "
      "on the alpha carbon. Small enough to fit where nothing else does, "
      "which is why collagen repeats it every third residue.",
      expect="", tags=("conditionally-indispensable",), sources=INDISPENSABLE),
    M("alanine-aa", "N[C@@H](C)C(=O)O",
      "(S)-2-Aminopropanoic acid", "Ala, A", "amino-acids",
      "The simplest chiral amino acid. Everything about the L series can be "
      "read off this one structure.",
      expect="S", tags=("dispensable",), sources=INDISPENSABLE),
    M("valine-aa", "N[C@@H](C(C)C)C(=O)O",
      "(S)-2-Amino-3-methylbutanoic acid", "Val, V", "amino-acids",
      "Branched immediately next to the backbone, which stiffens a peptide "
      "chain. One of the nine the body cannot make.",
      expect="S", tags=("indispensable",), sources=INDISPENSABLE),
    M("leucine-aa", "N[C@@H](CC(C)C)C(=O)O",
      "(S)-2-Amino-4-methylpentanoic acid", "Leu, L", "amino-acids",
      "The most abundant amino acid in most proteins, and the one that "
      "triggers the mTOR pathway most strongly.",
      expect="S", tags=("indispensable",), sources=INDISPENSABLE),
    M("isoleucine-aa", "N[C@@H]([C@@H](C)CC)C(=O)O",
      "(2S,3S)-2-Amino-3-methylpentanoic acid", "Ile, I", "amino-acids",
      "Two stereocentres, so four stereoisomers exist and only this one is "
      "built into protein. The other three are collectively the reason the "
      "L/D shorthand is not enough here.",
      expect="SS", tags=("indispensable",), sources=INDISPENSABLE),
    M("proline-aa", "OC(=O)[C@@H]1CCCN1",
      "(S)-Pyrrolidine-2-carboxylic acid", "Pro, P", "amino-acids",
      "Its nitrogen sits inside a ring, so it cannot donate the hydrogen "
      "bond the peptide backbone relies on. This is why proline breaks "
      "helices and forces kinks.",
      expect="S", tags=("conditionally-indispensable",), sources=INDISPENSABLE),
    M("phenylalanine-aa", "N[C@@H](Cc1ccccc1)C(=O)O",
      "(S)-2-Amino-3-phenylpropanoic acid", "Phe, F", "amino-acids",
      "Indispensable, and the reason phenylketonuria is dangerous: without "
      "the enzyme that converts it to tyrosine, it accumulates.",
      expect="S", tags=("indispensable",), sources=INDISPENSABLE),
    M("tyrosine-aa", "N[C@@H](Cc1ccc(O)cc1)C(=O)O",
      "(S)-2-Amino-3-(4-hydroxyphenyl)propanoic acid", "Tyr, Y", "amino-acids",
      "Phenylalanine plus one hydroxyl. The body can make it, but only from "
      "phenylalanine, which is what conditionally indispensable means.",
      expect="S", tags=("conditionally-indispensable",), sources=INDISPENSABLE),
    M("tryptophan-aa", "N[C@@H](Cc1c[nH]c2ccccc12)C(=O)O",
      "(S)-2-Amino-3-(1H-indol-3-yl)propanoic acid", "Trp, W", "amino-acids",
      "The largest of the twenty, and the precursor of serotonin and "
      "melatonin. Its indole ring dominates protein UV absorbance at 280 nm.",
      expect="S", tags=("indispensable",), sources=INDISPENSABLE),
    M("methionine-aa", "N[C@@H](CCSC)C(=O)O",
      "(S)-2-Amino-4-(methylsulfanyl)butanoic acid", "Met, M", "amino-acids",
      "Every protein starts here: it is the residue the initiator tRNA "
      "carries. Also the sulfur donor for S-adenosylmethionine.",
      expect="S", tags=("indispensable",), sources=INDISPENSABLE),
    M("cysteine-aa", "N[C@@H](CS)C(=O)O",
      "(R)-2-Amino-3-sulfanylpropanoic acid", "Cys, C", "amino-acids",
      "The single R in the L series, purely because sulfur outranks the "
      "carboxyl carbon. Its thiol forms the disulfide bridges that hold "
      "protein folds together.",
      expect="R", tags=("conditionally-indispensable",), sources=INDISPENSABLE),
    M("serine-aa", "N[C@@H](CO)C(=O)O",
      "(S)-2-Amino-3-hydroxypropanoic acid", "Ser, S", "amino-acids",
      "A small hydroxyl that enzymes phosphorylate constantly. Much of "
      "cell signalling is serine being switched on and off.",
      expect="S", tags=("dispensable",), sources=INDISPENSABLE),
    M("threonine-aa", "N[C@@H]([C@H](O)C)C(=O)O",
      "(2S,3R)-2-Amino-3-hydroxybutanoic acid", "Thr, T", "amino-acids",
      "Two stereocentres, and note they are not both S. Indispensable.",
      expect="RS", tags=("indispensable",), sources=INDISPENSABLE),
    M("asparagine-aa", "N[C@@H](CC(N)=O)C(=O)O",
      "(S)-2,4-Diamino-4-oxobutanoic acid", "Asn, N", "amino-acids",
      "First isolated from asparagus in 1806, the first amino acid ever "
      "obtained pure. The usual attachment point for N-linked glycans.",
      expect="S", tags=("dispensable",), sources=INDISPENSABLE),
    M("glutamine-aa", "N[C@@H](CCC(N)=O)C(=O)O",
      "(S)-2,5-Diamino-5-oxopentanoic acid", "Gln, Q", "amino-acids",
      "The most abundant free amino acid in blood, and the body's way of "
      "moving nitrogen around without releasing ammonia.",
      expect="S", tags=("conditionally-indispensable",), sources=INDISPENSABLE),
    M("aspartic-acid-aa", "N[C@@H](CC(=O)O)C(=O)O",
      "(S)-2-Aminobutanedioic acid", "Asp, D", "amino-acids",
      "Negatively charged at physiological pH. Sits in enzyme active sites "
      "wherever a proton needs shuttling.",
      expect="S", tags=("dispensable",), sources=INDISPENSABLE),
    M("glutamic-acid-aa", "N[C@@H](CCC(=O)O)C(=O)O",
      "(S)-2-Aminopentanedioic acid", "Glu, E", "amino-acids",
      "The main excitatory neurotransmitter in the brain, and the taste "
      "of umami.",
      expect="S", tags=("dispensable",), sources=INDISPENSABLE),
    M("lysine-aa", "N[C@@H](CCCCN)C(=O)O",
      "(S)-2,6-Diaminohexanoic acid", "Lys, L is taken; K", "amino-acids",
      "A long positively charged arm. Acetylating it is how histones "
      "loosen their grip on DNA.",
      expect="S", tags=("indispensable",), sources=INDISPENSABLE),
    M("arginine-aa", "N[C@@H](CCCNC(N)=N)C(=O)O",
      "(S)-2-Amino-5-carbamimidamidopentanoic acid", "Arg, R", "amino-acids",
      "Its guanidinium group stays charged across the whole physiological "
      "pH range. The substrate from which nitric oxide is made.",
      expect="S", tags=("conditionally-indispensable",), sources=INDISPENSABLE),
    M("histidine-aa", "N[C@@H](Cc1c[nH]cn1)C(=O)O",
      "(S)-2-Amino-3-(1H-imidazol-4-yl)propanoic acid", "His, H", "amino-acids",
      "Its imidazole has a pKa near 6, the only side chain that can gain or "
      "lose a proton at physiological pH. That is why it does the catalysis.",
      expect="S", tags=("indispensable",), sources=INDISPENSABLE),

    # ---- nucleobases -----------------------------------------------------
    M("adenine", "Nc1ncnc2[nH]cnc12",
      "9H-Purin-6-amine", "Adenine", "nucleobases",
      "A purine: two fused rings. Pairs with thymine through two hydrogen "
      "bonds, and turns up again in ATP, NAD and coenzyme A.",
      expect=""),
    M("guanine", "Nc1nc2[nH]cnc2c(=O)[nH]1",
      "2-Amino-1,9-dihydro-6H-purin-6-one", "Guanine", "nucleobases",
      "The other purine. Three hydrogen bonds to cytosine, which is why "
      "GC-rich DNA needs more heat to separate.",
      expect=""),
    M("cytosine", "Nc1cc[nH]c(=O)n1",
      "4-Amino-1,2-dihydropyrimidin-2-one", "Cytosine", "nucleobases",
      "A pyrimidine: one ring. Spontaneously deaminates to uracil, which is "
      "a steady source of mutation and the reason DNA repair exists.",
      expect=""),
    M("thymine", "Cc1c[nH]c(=O)[nH]c1=O",
      "5-Methyl-1,2,3,4-tetrahydropyrimidine-2,4-dione", "Thymine",
      "nucleobases",
      "Uracil plus a methyl group. DNA uses thymine rather than uracil "
      "precisely so that deaminated cytosine can be recognised as damage.",
      expect=""),
    M("uracil", "O=c1cc[nH]c(=O)[nH]1",
      "1,2,3,4-Tetrahydropyrimidine-2,4-dione", "Uracil", "nucleobases",
      "RNA's stand-in for thymine. Cheaper to make, and RNA is disposable "
      "enough not to need the extra proofreading signal.",
      expect=""),

    # ---- sugars ----------------------------------------------------------
    M("fructose", "OC[C@@H]1O[C@](O)(CO)[C@@H](O)[C@@H]1O",
      "D-Fructose (furanose form)", "Fruit sugar", "sugars",
      "Same formula as glucose, different connectivity: a ketone rather "
      "than an aldehyde. It closes into a five-membered ring, not six.",
      expect="RSSS"),
    M("ribose", "OC[C@H]1O[C@H](O)[C@H](O)[C@H]1O",
      "D-Ribose (furanose form)", None, "sugars",
      "The backbone sugar of RNA. Three hydroxyls on the ring.",
      expect="RRRS"),
    M("deoxyribose", "OC[C@H]1O[C@H](O)C[C@H]1O",
      "2-Deoxy-D-ribose (furanose form)", None, "sugars",
      "Ribose minus one oxygen at position 2. That single missing hydroxyl "
      "is the whole difference between RNA and DNA, and it is what makes "
      "DNA the more chemically durable of the two.",
      expect="RRS"),
    M("sucrose", "OC[C@H]1O[C@@H](O[C@]2(CO)O[C@H](CO)[C@@H](O)[C@@H]2O)"
                 "[C@H](O)[C@@H](O)[C@@H]1O",
      "Sucrose", "Table sugar", "sugars",
      "Glucose joined to fructose. The link consumes both anomeric carbons, "
      "so neither ring can open: sucrose is a non-reducing sugar and gives "
      "no Fehling reaction until it is hydrolysed.",
      expect="RRRSSSSSS"),

    # ---- fatty acids -----------------------------------------------------
    M("palmitic-acid", "CCCCCCCCCCCCCCCC(=O)O",
      "Hexadecanoic acid", "Palmitic acid", "lipids",
      "Sixteen carbons, fully saturated, 16:0. The default product of "
      "fatty acid synthase, and solid at room temperature.",
      expect=""),
    M("stearic-acid", "CCCCCCCCCCCCCCCCCC(=O)O",
      "Octadecanoic acid", "Stearic acid", "lipids",
      "18:0. Two carbons longer than palmitic and melts 7 degrees higher: "
      "chain length alone shifts the melting point steadily upward.",
      expect=""),
    M("oleic-acid", "CCCCCCCC/C=C\\CCCCCCCC(=O)O",
      "(9Z)-Octadec-9-enoic acid", "Oleic acid", "lipids",
      "18:1 with one Z double bond. That single cis kink stops the chains "
      "packing, which is why olive oil is liquid and stearic acid is not.",
      expect="Z"),
    M("linoleic-acid", "CCCCC/C=C\\C/C=C\\CCCCCCCC(=O)O",
      "(9Z,12Z)-Octadeca-9,12-dienoic acid", "Linoleic acid", "lipids",
      "18:2 n-6. Genuinely essential: humans cannot place a double bond "
      "beyond carbon 9, so this one has to be eaten.",
      expect="ZZ", tags=("essential-fatty-acid",)),
    M("alpha-linolenic-acid", "CC/C=C\\C/C=C\\C/C=C\\CCCCCCCC(=O)O",
      "(9Z,12Z,15Z)-Octadeca-9,12,15-trienoic acid", "Alpha-linolenic acid",
      "lipids",
      "18:3 n-3, the other truly essential fatty acid. The n-3 and n-6 "
      "families cannot be interconverted, which is why both must be eaten.",
      expect="ZZZ", tags=("essential-fatty-acid",)),
    M("arachidonic-acid", "CCCCC/C=C\\C/C=C\\C/C=C\\C/C=C\\CCCC(=O)O",
      "(5Z,8Z,11Z,14Z)-Icosa-5,8,11,14-tetraenoic acid", "Arachidonic acid",
      "lipids",
      "20:4 n-6, built from linoleic acid. The substrate cyclooxygenase "
      "acts on, which is where aspirin and ibuprofen intervene.",
      expect="ZZZZ"),

    # ---- cofactors -------------------------------------------------------
    M("atp", "Nc1ncnc2c1ncn2[C@@H]1O[C@H](COP(=O)(O)OP(=O)(O)OP(=O)(O)O)"
             "[C@@H](O)[C@H]1O",
      "Adenosine 5'-triphosphate", "ATP", "cofactors",
      "Adenine, ribose, three phosphates. The energy is not stored in the "
      "bonds so much as released by relieving the electrostatic strain of "
      "three adjacent negative charges.",
      expect="RRRS"),
    M("sam", "C[S+](CC[C@H](N)C(=O)O)C[C@H]1O[C@@H](n2cnc3c(N)ncnc32)"
             "[C@H](O)[C@@H]1O",
      "S-Adenosyl-L-methionine", "SAM, AdoMet", "cofactors",
      "A positively charged sulfur with three substituents, which makes the "
      "attached methyl group unusually easy to hand off. The cell's "
      "universal methyl donor.",
      expect="RRSSS"),

    # ---- vitamins --------------------------------------------------------
    M("ascorbic-acid", "OC[C@H](O)[C@H]1OC(=O)C(O)=C1O",
      "L-Ascorbic acid", "Vitamin C", "vitamins",
      "Most mammals make their own. Primates, guinea pigs and a few others "
      "carry a broken copy of the last enzyme in the pathway, so for us it "
      "is a vitamin rather than a metabolite.",
      expect="RS"),
    M("retinol", "CC1=C(/C=C/C(C)=C/C=C/C(C)=C/CO)C(C)(C)CCC1",
      "all-trans-Retinol", "Vitamin A", "vitamins",
      "A conjugated chain of alternating double bonds. Oxidised to retinal, "
      "where one of those bonds flips from trans to cis on absorbing a "
      "photon. That flip is the first step of seeing.",
      expect="EEEE"),
    M("thiamine", "Cc1ncc(C[n+]2csc(CCO)c2C)c(N)n1",
      "Thiamine", "Vitamin B1", "vitamins",
      "Its thiazolium ring carries a carbon acidic enough to lose a proton, "
      "giving a carbanion that attacks keto acids. Deficiency causes "
      "beriberi and Wernicke encephalopathy.",
      expect=""),
    M("riboflavin", "Cc1cc2nc3c(=O)[nH]c(=O)nc-3n(C[C@H](O)[C@H](O)[C@H](O)CO)"
                    "c2cc1C",
      "Riboflavin", "Vitamin B2", "vitamins",
      "The yellow in a multivitamin, and the reason urine turns bright "
      "yellow afterwards. Becomes FAD, which carries electrons in pairs.",
      expect="RSS"),
]
