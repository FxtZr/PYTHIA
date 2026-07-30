"""Metabolic pathways.

Deliberately a different kind of object from the reaction mechanisms. There
are no curved arrows here and no electrons being pushed. A pathway step is
a transformation catalysed by a named enzyme, and what is worth knowing
about it is the cofactor it needs, whether it can run backwards, and
whether it is a point of control. Trying to serve both kinds of chemistry
with one viewer would have served neither.

On EC numbers
-------------
These are written from knowledge and cannot be verified by an offline
build. The build checks their shape -- four dot-separated numbers, the
first between 1 and 7 -- which catches a typo but not a wrong assignment.
Verify them against ExplorEnz in the same online pass that fixes the DOIs,
and record it in SOURCES.md. Until then, treat them as a pointer to look
something up, not as an authority.

On the data source
------------------
Reactome and Rhea are cited because both are CC BY 4.0 and can be checked
and, if needed, redistributed. KEGG is not used anywhere in this project:
it is the best known pathway database and its licence forbids
redistribution, which makes it unusable in an open repository.
"""

from collections import namedtuple

Pathway = namedtuple(
    "Pathway",
    "id name summary location purpose steps regulation sources")

Step = namedtuple(
    "Step",
    "substrate product enzyme ec cofactors reversible note key molecule",
    defaults=((), True, None, False, None))


REF = ("reactome", "rhea", "iubmb-enzyme", "lehninger")


PATHWAYS = [

    # ======================================================================
    Pathway(
        id="glycolysis",
        name="Glycolysis",
        summary="Glucose to two pyruvate, with a net gain of two ATP and two "
                "NADH. Ten steps, present in nearly every cell alive.",
        location="Cytosol",
        purpose="The first half spends two ATP to trap and destabilise the "
                "sugar. The second half recovers four. Reading it as one "
                "long sequence hides that structure; reading it as an "
                "investment followed by a return makes the whole thing "
                "obvious.",
        regulation="Phosphofructokinase-1 is the real control point. It is "
                   "inhibited by ATP and citrate, which signal that energy "
                   "is already plentiful, and activated by AMP and by "
                   "fructose-2,6-bisphosphate. Hexokinase and pyruvate "
                   "kinase are also regulated, but the committed step is "
                   "the third.",
        sources=REF,
        steps=[
            Step("Glucose", "Glucose 6-phosphate",
                 "Hexokinase (glucokinase in liver)", "2.7.1.1",
                 cofactors=("ATP", "Mg2+"), reversible=False, key=True,
                 molecule="glucose-open",
                 note="Phosphorylation traps the sugar inside the cell: the "
                      "charged phosphate cannot cross the membrane. The "
                      "liver isoform has a much higher Km, so it only "
                      "engages when blood glucose is high."),
            Step("Glucose 6-phosphate", "Fructose 6-phosphate",
                 "Glucose-6-phosphate isomerase", "5.3.1.9",
                 molecule="fructose",
                 note="An aldose becomes a ketose. This moves the carbonyl "
                      "from C1 to C2, which is what makes the next "
                      "phosphorylation and the later cleavage possible."),
            Step("Fructose 6-phosphate", "Fructose 1,6-bisphosphate",
                 "Phosphofructokinase-1", "2.7.1.11",
                 cofactors=("ATP", "Mg2+"), reversible=False, key=True,
                 note="The committed step. Once this phosphate is on, the "
                      "molecule has no route back out of glycolysis, and "
                      "this is where the pathway is controlled."),
            Step("Fructose 1,6-bisphosphate",
                 "Dihydroxyacetone phosphate + Glyceraldehyde 3-phosphate",
                 "Aldolase", "4.1.2.13",
                 note="A six-carbon sugar is cut into two three-carbon "
                      "pieces. Everything downstream therefore happens "
                      "twice per glucose."),
            Step("Dihydroxyacetone phosphate", "Glyceraldehyde 3-phosphate",
                 "Triose phosphate isomerase", "5.3.1.1",
                 note="Only one of the two halves can continue, so the other "
                      "is converted into it. This enzyme is close to "
                      "catalytically perfect: it works as fast as diffusion "
                      "delivers its substrate."),
            Step("Glyceraldehyde 3-phosphate", "1,3-Bisphosphoglycerate",
                 "Glyceraldehyde-3-phosphate dehydrogenase", "1.2.1.12",
                 cofactors=("NAD+", "Pi"),
                 note="The oxidation step. An aldehyde becomes an acyl "
                      "phosphate, and the energy released is captured in "
                      "that high-energy bond rather than lost as heat."),
            Step("1,3-Bisphosphoglycerate", "3-Phosphoglycerate",
                 "Phosphoglycerate kinase", "2.7.2.3",
                 cofactors=("ADP", "Mg2+"),
                 note="The first ATP comes back here, made directly by "
                      "transferring a phosphate rather than through the "
                      "respiratory chain. Twice per glucose, so the "
                      "investment is now repaid."),
            Step("3-Phosphoglycerate", "2-Phosphoglycerate",
                 "Phosphoglycerate mutase", "5.4.2.11",
                 note="The phosphate moves one carbon along, setting up the "
                      "dehydration that follows."),
            Step("2-Phosphoglycerate", "Phosphoenolpyruvate",
                 "Enolase", "4.2.1.11",
                 note="Losing water redistributes the electrons and makes "
                      "the remaining phosphate bond far easier to break. "
                      "The molecule has not gained energy; it has been "
                      "made unstable."),
            Step("Phosphoenolpyruvate", "Pyruvate",
                 "Pyruvate kinase", "2.7.1.40",
                 cofactors=("ADP", "Mg2+", "K+"), reversible=False, key=True,
                 note="The second ATP per triose. Strongly exergonic and "
                      "effectively irreversible, which is why "
                      "gluconeogenesis has to go around it."),
        ],
    ),

    # ======================================================================
    Pathway(
        id="glycogenesis",
        name="Glycogenesis",
        summary="Storing glucose as glycogen. Four enzymes, and the one that "
                "makes branches matters more than it looks.",
        location="Cytosol, mainly liver and skeletal muscle",
        purpose="Glucose cannot simply be stockpiled: thousands of free "
                "molecules would wreck the cell's osmotic balance. Linking "
                "them into one large branched polymer stores the same "
                "carbon at almost no osmotic cost.",
        regulation="Glycogen synthase is the controlled step. Insulin "
                   "activates it by triggering its dephosphorylation; "
                   "glucagon and adrenaline switch it off. The same signals "
                   "act in the opposite direction on glycogen "
                   "phosphorylase, so the two pathways are never running "
                   "hard at the same time.",
        sources=REF,
        steps=[
            Step("Glucose 6-phosphate", "Glucose 1-phosphate",
                 "Phosphoglucomutase", "5.4.2.2",
                 note="The phosphate is moved to C1, where it can later be "
                      "displaced. Freely reversible, and shared with "
                      "glycogen breakdown."),
            Step("Glucose 1-phosphate", "UDP-glucose",
                 "UDP-glucose pyrophosphorylase", "2.7.7.9",
                 cofactors=("UTP",), reversible=False,
                 note="Activation. The reaction itself is near equilibrium, "
                      "but the pyrophosphate released is immediately "
                      "hydrolysed, and that hydrolysis is what pulls the "
                      "step forward. A common trick in biosynthesis."),
            Step("UDP-glucose + glycogen (n residues)",
                 "Glycogen (n+1 residues)",
                 "Glycogen synthase", "2.4.1.11",
                 reversible=False, key=True,
                 note="Adds glucose to the growing chain through an alpha "
                      "1,4 link. This is the regulated step, and it cannot "
                      "start from nothing: it needs an existing chain, "
                      "which glycogenin provides by making the first few "
                      "residues on itself."),
            Step("Linear glycogen chain", "Branched glycogen",
                 "Glycogen branching enzyme", "2.4.1.18",
                 reversible=False,
                 note="Moves a block of about seven residues to an alpha "
                      "1,6 position. Branching is not tidiness: it "
                      "multiplies the number of chain ends, and since both "
                      "synthesis and breakdown work only at the ends, it "
                      "sets how fast glycogen can be mobilised."),
        ],
    ),

    # ======================================================================
    Pathway(
        id="glycogenolysis",
        name="Glycogenolysis",
        summary="Releasing glucose from glycogen. Nearly the reverse of "
                "storage, and the last step is where liver and muscle part "
                "company.",
        location="Cytosol, liver and skeletal muscle",
        purpose="Liver breaks down glycogen to keep blood glucose steady for "
                "the rest of the body. Muscle breaks it down for its own "
                "use only. The difference is one enzyme.",
        regulation="Glycogen phosphorylase is activated by phosphorylation, "
                   "downstream of glucagon in liver and adrenaline in "
                   "muscle. Muscle phosphorylase also responds directly to "
                   "AMP and to calcium, so contraction itself mobilises "
                   "fuel without waiting for a hormone.",
        sources=REF,
        steps=[
            Step("Glycogen (n residues)",
                 "Glucose 1-phosphate + glycogen (n-1)",
                 "Glycogen phosphorylase", "2.4.1.1",
                 cofactors=("Pi", "Pyridoxal phosphate"),
                 reversible=False, key=True,
                 note="Cleaves with phosphate rather than water, so the "
                      "product comes out already phosphorylated and no ATP "
                      "is spent trapping it. Stops four residues short of "
                      "each branch point."),
            Step("Branched residues", "Linear chain + free glucose",
                 "Glycogen debranching enzyme", "2.4.1.25",
                 reversible=False,
                 note="One protein with two activities: it transfers three "
                      "residues to a nearby chain end, then hydrolyses the "
                      "remaining alpha 1,6 link. That last one comes off as "
                      "free glucose, which is why a small fraction of the "
                      "yield is not phosphorylated."),
            Step("Glucose 1-phosphate", "Glucose 6-phosphate",
                 "Phosphoglucomutase", "5.4.2.2",
                 note="The same reversible step as in storage, running the "
                      "other way."),
            Step("Glucose 6-phosphate", "Glucose",
                 "Glucose-6-phosphatase", "3.1.3.9",
                 reversible=False, key=True,
                 note="Liver and kidney only. Muscle lacks this enzyme "
                      "entirely, so muscle glycogen can never leave the "
                      "muscle: the phosphate keeps it inside. This single "
                      "absence is why muscle cannot contribute to blood "
                      "glucose."),
        ],
    ),

    # ======================================================================
    Pathway(
        id="citric-acid-cycle",
        name="Citric acid cycle",
        summary="Acetyl-CoA is oxidised to two CO2, and the reducing power "
                "is carried away as three NADH and one FADH2 per turn.",
        location="Mitochondrial matrix",
        purpose="Not a route from A to B but a loop: oxaloacetate is "
                "consumed at the start and regenerated at the end, so a "
                "single molecule of it can process acetyl groups "
                "indefinitely. What the cycle actually produces is reduced "
                "carriers, and the ATP comes later, in the respiratory "
                "chain.",
        regulation="Controlled by supply and demand rather than by one "
                   "master switch. NADH inhibits citrate synthase, "
                   "isocitrate dehydrogenase and the alpha-ketoglutarate "
                   "complex; ADP and calcium activate them. When the cell "
                   "is not spending energy, NADH accumulates and the cycle "
                   "slows itself.",
        sources=REF,
        steps=[
            Step("Acetyl-CoA + Oxaloacetate", "Citrate",
                 "Citrate synthase", "2.3.3.1",
                 reversible=False, key=True,
                 note="Two carbons enter. The reaction is strongly "
                      "favourable and sets the pace of the whole cycle."),
            Step("Citrate", "Isocitrate", "Aconitase", "4.2.1.3",
                 note="A hydroxyl is moved from a carbon that cannot be "
                      "oxidised to one that can. Dehydration then "
                      "rehydration, with cis-aconitate in between."),
            Step("Isocitrate", "Alpha-ketoglutarate",
                 "Isocitrate dehydrogenase", "1.1.1.41",
                 cofactors=("NAD+",), reversible=False, key=True,
                 note="The first CO2 leaves and the first NADH is made. "
                      "Usually the rate-limiting step."),
            Step("Alpha-ketoglutarate", "Succinyl-CoA",
                 "Alpha-ketoglutarate dehydrogenase complex", "1.2.4.2",
                 cofactors=("NAD+", "CoA", "Thiamine pyrophosphate", "FAD",
                            "Lipoamide"),
                 reversible=False, key=True,
                 note="The second CO2 and the second NADH. A large complex "
                      "of three enzymes, closely related to the pyruvate "
                      "dehydrogenase complex and needing the same five "
                      "cofactors, which is why thiamine deficiency hits "
                      "energy metabolism so hard."),
            Step("Succinyl-CoA", "Succinate",
                 "Succinyl-CoA synthetase", "6.2.1.4",
                 cofactors=("GDP", "Pi"),
                 note="The only step of the cycle that makes a nucleoside "
                      "triphosphate directly. GTP here, readily converted "
                      "to ATP."),
            Step("Succinate", "Fumarate",
                 "Succinate dehydrogenase", "1.3.5.1",
                 cofactors=("FAD",),
                 note="The one enzyme of the cycle embedded in the inner "
                      "membrane, where it is also Complex II of the "
                      "respiratory chain. Its FADH2 hands electrons "
                      "straight into the chain."),
            Step("Fumarate", "Malate", "Fumarase", "4.2.1.2",
                 cofactors=("H2O",),
                 note="Water adds across the double bond, and it adds to "
                      "one face only, giving a single stereoisomer."),
            Step("Malate", "Oxaloacetate", "Malate dehydrogenase", "1.1.1.37",
                 cofactors=("NAD+",),
                 note="The third NADH, and oxaloacetate is back. "
                      "Thermodynamically unfavourable on its own; it runs "
                      "because citrate synthase immediately consumes the "
                      "product."),
        ],
    ),

    # ======================================================================
    Pathway(
        id="beta-oxidation",
        name="Beta-oxidation",
        summary="Fatty acids are shortened two carbons at a time. Four steps "
                "per cycle, repeated until nothing is left but acetyl-CoA.",
        location="Mitochondrial matrix",
        purpose="Each turn removes an acetyl-CoA and yields one FADH2 and "
                "one NADH. Fat carries more energy per gram than "
                "carbohydrate because its carbons start out more reduced, "
                "and this is the sequence that collects on that.",
        regulation="Control is at entry rather than within the cycle. "
                   "Malonyl-CoA, the first committed intermediate of fatty "
                   "acid synthesis, inhibits the carnitine shuttle that "
                   "carries fatty acids into the mitochondrion. A cell "
                   "building fat therefore cannot simultaneously burn it.",
        sources=REF,
        steps=[
            Step("Acyl-CoA", "trans-Delta-2-Enoyl-CoA",
                 "Acyl-CoA dehydrogenase", "1.3.8.7",
                 cofactors=("FAD",),
                 note="Oxidation to a double bond, with E geometry. "
                      "Different isoforms handle short, medium, long and "
                      "very long chains; a deficiency in the medium-chain "
                      "enzyme is one of the commonest inherited metabolic "
                      "disorders."),
            Step("trans-Delta-2-Enoyl-CoA", "3-Hydroxyacyl-CoA",
                 "Enoyl-CoA hydratase", "4.2.1.17",
                 cofactors=("H2O",),
                 note="Water adds across the double bond, placing a hydroxyl "
                      "on the beta carbon. Hence the name of the pathway."),
            Step("3-Hydroxyacyl-CoA", "3-Ketoacyl-CoA",
                 "3-Hydroxyacyl-CoA dehydrogenase", "1.1.1.35",
                 cofactors=("NAD+",),
                 note="The hydroxyl becomes a ketone. The carbon between the "
                      "two carbonyls is now weak enough to be cut."),
            Step("3-Ketoacyl-CoA", "Acetyl-CoA + Acyl-CoA (two carbons "
                                   "shorter)",
                 "Thiolase", "2.3.1.16",
                 cofactors=("CoA",), reversible=False, key=True,
                 note="Coenzyme A attacks and the chain is severed. The "
                      "shortened acyl-CoA re-enters at step one, and the "
                      "cycle repeats. Palmitate, at sixteen carbons, goes "
                      "round seven times."),
        ],
    ),

    # ======================================================================
    Pathway(
        id="urea-cycle",
        name="Urea cycle",
        summary="Ammonia, which is toxic, is converted into urea, which is "
                "not. Five enzymes across two compartments.",
        location="Mitochondrial matrix and cytosol, liver",
        purpose="Breaking down amino acids releases nitrogen as ammonia, and "
                "ammonia interferes with brain metabolism at low "
                "concentrations. Urea is neutral, soluble, and safe to "
                "carry in blood to the kidney.",
        regulation="Carbamoyl phosphate synthetase I requires "
                   "N-acetylglutamate as an obligatory activator, and "
                   "N-acetylglutamate is made in proportion to available "
                   "glutamate. A high-protein diet therefore raises urea "
                   "cycle capacity within days.",
        sources=REF,
        steps=[
            Step("Ammonia + Bicarbonate", "Carbamoyl phosphate",
                 "Carbamoyl phosphate synthetase I", "6.3.4.16",
                 cofactors=("2 ATP", "N-acetylglutamate"),
                 reversible=False, key=True,
                 note="Mitochondrial, and the committed step. Two ATP are "
                      "spent here, which is most of the cost of disposing "
                      "of nitrogen safely."),
            Step("Carbamoyl phosphate + Ornithine", "Citrulline",
                 "Ornithine transcarbamylase", "2.1.3.3",
                 reversible=False,
                 note="Still in the mitochondrion. Deficiency of this "
                      "enzyme is the commonest urea cycle disorder and is "
                      "X-linked, which makes its inheritance pattern "
                      "distinctive."),
            Step("Citrulline + Aspartate", "Argininosuccinate",
                 "Argininosuccinate synthetase", "6.3.4.5",
                 cofactors=("ATP",), reversible=False,
                 note="Now in the cytosol. The second nitrogen of urea "
                      "arrives here, carried in by aspartate rather than as "
                      "free ammonia."),
            Step("Argininosuccinate", "Arginine + Fumarate",
                 "Argininosuccinate lyase", "4.3.2.1",
                 note="The fumarate released feeds straight into the citric "
                      "acid cycle, which is how nitrogen disposal and "
                      "energy metabolism are linked."),
            Step("Arginine", "Urea + Ornithine", "Arginase", "3.5.3.1",
                 cofactors=("H2O", "Mn2+"), reversible=False,
                 note="Urea is released and ornithine returns to the "
                      "mitochondrion to start again. Like the citric acid "
                      "cycle, the carrier is regenerated rather than "
                      "consumed."),
        ],
    ),
]
