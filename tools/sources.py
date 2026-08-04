"""Source registry for PYTHIA.

Every factual claim the program displays resolves to a key in here. The
build refuses to emit a record that cites a key which is not defined, so
an unsourced fact cannot reach the interface by accident.

Fields
------
title, authors, publisher, year   bibliographic identity
where                             volume/pages, edition, or report number
url                               a stable landing page, not a deep link
licence                           what we are permitted to do with it
use                               "redistributed" if data from this source
                                  ships inside this repository,
                                  "cited" if we only reference it

On DOIs: they are deliberately absent. A wrong DOI is worse than no DOI,
and they cannot be verified from an offline build. Add them in a single
pass with network access before the first public release, and record that
pass in SOURCES.md.
"""

SOURCES = {

    # ---- nomenclature and stereochemistry -------------------------------
    "iupac-bluebook-2013": {
        "title": "Nomenclature of Organic Chemistry: Recommendations and "
                 "Preferred Names 2013",
        "authors": "H. A. Favre, W. H. Powell (eds.)",
        "publisher": "IUPAC / Royal Society of Chemistry",
        "year": 2013,
        "where": "ISBN 978-0-85404-182-4. CIP rules at P-91 and P-92",
        "url": "https://iupac.org/what-we-do/books/bluebook/",
        "licence": "Copyright IUPAC/RSC",
        "use": "cited",
    },
    "cip-1966": {
        "title": "Specification of Molecular Chirality",
        "authors": "R. S. Cahn, C. Ingold, V. Prelog",
        "publisher": "Angewandte Chemie International Edition",
        "year": 1966,
        "where": "vol. 5, pp. 385-415",
        "url": "https://onlinelibrary.wiley.com/journal/15213773",
        "licence": "Copyright Wiley",
        "use": "cited",
    },
    "prelog-helmchen-1982": {
        "title": "Basic Principles of the CIP-System and Proposals for a "
                 "Revision",
        "authors": "V. Prelog, G. Helmchen",
        "publisher": "Angewandte Chemie International Edition",
        "year": 1982,
        "where": "vol. 21, pp. 567-583",
        "url": "https://onlinelibrary.wiley.com/journal/15213773",
        "licence": "Copyright Wiley",
        "use": "cited",
    },
    "hanson-cip-2018": {
        "title": "Algorithmic Analysis of Cahn-Ingold-Prelog Rules of "
                 "Stereochemistry: Proposals for Revised Rules and a Guide "
                 "for Machine Implementation",
        "authors": "R. M. Hanson, S. Musacchio, J. W. Mayfield, M. J. Bull, "
                   "E. L. Willighagen, N. E. Adams",
        "publisher": "Journal of Chemical Information and Modeling",
        "year": 2018,
        "where": "vol. 58, pp. 1755-1765",
        "url": "https://pubs.acs.org/journal/jcisd8",
        "licence": "Copyright ACS",
        "use": "cited",
    },

    # ---- atomic and molecular reference data ----------------------------
    "ciaaw": {
        "title": "Standard Atomic Weights",
        "authors": "IUPAC Commission on Isotopic Abundances and Atomic Weights",
        "publisher": "IUPAC",
        "year": 2021,
        "where": "Current standard atomic weights table",
        "url": "https://ciaaw.org/atomic-weights.htm",
        "licence": "Freely available reference data",
        "use": "redistributed",
    },
    "chebi": {
        "title": "ChEBI: Chemical Entities of Biological Interest",
        "authors": "EMBL-EBI",
        "publisher": "European Molecular Biology Laboratory",
        "year": 2026,
        "where": "Ontology of small molecules of biological relevance",
        "url": "https://www.ebi.ac.uk/chebi/",
        "licence": "CC BY 4.0",
        "use": "cited",
    },
    "pubchem": {
        "title": "PubChem",
        "authors": "National Center for Biotechnology Information",
        "publisher": "U.S. National Library of Medicine, NIH",
        "year": 2026,
        "where": "Compound records and reference structures",
        "url": "https://pubchem.ncbi.nlm.nih.gov/",
        "licence": "Public domain (work of the U.S. Government)",
        "use": "cited",
    },

    # ---- nutrition ------------------------------------------------------
    "who-fao-unu-935": {
        "title": "Protein and amino acid requirements in human nutrition",
        "authors": "Joint WHO/FAO/UNU Expert Consultation",
        "publisher": "World Health Organization",
        "year": 2007,
        "where": "WHO Technical Report Series 935. "
                 "ISBN 978-92-4-120935-9",
        "url": "https://www.who.int/publications/i/item/9241209351",
        "licence": "WHO publication, reuse under WHO terms",
        "use": "cited",
    },

    # ---- biochemistry: pathways and enzymes ------------------------------
    # KEGG is deliberately absent. It is the best known pathway database and
    # its licence forbids redistribution without a commercial agreement, so
    # no KEGG-derived data may ship in this repository. Reactome and Rhea
    # cover the same ground under CC BY 4.0.
    "reactome": {
        "title": "Reactome Pathway Database",
        "authors": "Reactome Consortium",
        "publisher": "EMBL-EBI, OICR, NYU Langone, OHSU",
        "year": 2026,
        "where": "Curated human pathway reactions",
        "url": "https://reactome.org/",
        "licence": "CC BY 4.0",
        "use": "cited",
    },
    "rhea": {
        "title": "Rhea: an expert-curated resource of biochemical reactions",
        "authors": "EMBL-EBI / SIB Swiss Institute of Bioinformatics",
        "publisher": "European Molecular Biology Laboratory",
        "year": 2026,
        "where": "Balanced biochemical reaction equations",
        "url": "https://www.rhea-db.org/",
        "licence": "CC BY 4.0",
        "use": "cited",
    },
    "iubmb-enzyme": {
        "title": "Enzyme Nomenclature",
        "authors": "IUBMB Nomenclature Committee",
        "publisher": "International Union of Biochemistry and Molecular Biology",
        "year": 2026,
        "where": "EC number assignments, served via ExplorEnz",
        "url": "https://iubmb.qmul.ac.uk/enzyme/",
        "licence": "Freely available reference nomenclature",
        "use": "cited",
    },

    # ---- spectroscopy ----------------------------------------------------
    "silverstein": {
        "title": "Spectrometric Identification of Organic Compounds",
        "authors": "R. M. Silverstein, F. X. Webster, D. J. Kiemle, "
                   "D. L. Bryce",
        "publisher": "Wiley",
        "year": 2014,
        "where": "8th edition. ISBN 978-0-470-61637-6. The standard "
                 "correlation tables for IR, NMR and mass spectrometry",
        "url": "https://www.wiley.com/",
        "licence": "Copyright Wiley",
        "use": "cited",
    },
    "pavia": {
        "title": "Introduction to Spectroscopy",
        "authors": "D. L. Pavia, G. M. Lampman, G. S. Kriz, J. R. Vyvyan",
        "publisher": "Cengage Learning",
        "year": 2015,
        "where": "5th edition. ISBN 978-1-285-46012-3",
        "url": "https://www.cengage.com/",
        "licence": "Copyright Cengage",
        "use": "cited",
    },
    "nist-webbook": {
        "title": "NIST Chemistry WebBook, SRD 69",
        "authors": "P. J. Linstrom, W. G. Mallard (eds.)",
        "publisher": "National Institute of Standards and Technology",
        "year": 2026,
        "where": "Reference infrared and mass spectra. Consulted for "
                 "characteristic values; no spectra are reproduced here",
        "url": "https://webbook.nist.gov/chemistry/",
        "licence": "US Government work; the interface restricts systematic "
                   "retrieval",
        "use": "cited",
    },
    "massbank": {
        "title": "MassBank Europe",
        "authors": "MassBank consortium",
        "publisher": "MassBank Europe / NORMAN network",
        "year": 2026,
        "where": "Open repository of experimental mass spectra. Not used "
                 "offline; the intended source if a network lookup layer "
                 "is added",
        "url": "https://massbank.eu/",
        "licence": "CC BY 4.0",
        "use": "cited",
    },

    # ---- computational method -------------------------------------------
    "rdkit": {
        "title": "RDKit: Open-source cheminformatics",
        "authors": "G. Landrum and contributors",
        "publisher": "RDKit project",
        "year": 2026,
        "where": "Used at build time for depiction coordinates, embedding "
                 "and CIP labelling",
        "url": "https://www.rdkit.org/",
        "licence": "BSD 3-Clause",
        "use": "cited",
    },
    "etkdg-2015": {
        "title": "Better Informed Distance Geometry: Using What We Know To "
                 "Improve Conformation Generation",
        "authors": "S. Riniker, G. A. Landrum",
        "publisher": "Journal of Chemical Information and Modeling",
        "year": 2015,
        "where": "vol. 55, pp. 2562-2574",
        "url": "https://pubs.acs.org/journal/jcisd8",
        "licence": "Copyright ACS",
        "use": "cited",
    },
    "mmff94": {
        "title": "Merck molecular force field. I. Basis, form, scope, "
                 "parameterization, and performance of MMFF94",
        "authors": "T. A. Halgren",
        "publisher": "Journal of Computational Chemistry",
        "year": 1996,
        "where": "vol. 17, pp. 490-519",
        "url": "https://onlinelibrary.wiley.com/journal/1096987x",
        "licence": "Copyright Wiley",
        "use": "cited",
    },
    "3dmol": {
        "title": "3Dmol.js: molecular visualization with WebGL",
        "authors": "N. Rego, D. Koes",
        "publisher": "Bioinformatics",
        "year": 2015,
        "where": "vol. 31, pp. 1322-1324",
        "url": "https://3dmol.csb.pitt.edu/",
        "licence": "BSD 3-Clause",
        "use": "redistributed",
    },

    # ---- teaching references --------------------------------------------
    # Cited as the standard treatments a reader can go and check. No text,
    # figure or table from any of these is reproduced.
    "clayden": {
        "title": "Organic Chemistry",
        "authors": "J. Clayden, N. Greeves, S. Warren",
        "publisher": "Oxford University Press",
        "year": 2012,
        "where": "2nd edition. ISBN 978-0-19-927029-3",
        "url": "https://global.oup.com/",
        "licence": "Copyright OUP",
        "use": "cited",
    },
    "lehninger": {
        "title": "Lehninger Principles of Biochemistry",
        "authors": "D. L. Nelson, M. M. Cox",
        "publisher": "W. H. Freeman / Macmillan Learning",
        "year": 2021,
        "where": "8th edition. ISBN 978-1-319-22800-2",
        "url": "https://www.macmillanlearning.com/",
        "licence": "Copyright Macmillan",
        "use": "cited",
    },
}


def resolve(keys):
    """Raise if any key is unknown. Returns the keys unchanged."""
    unknown = [k for k in keys if k not in SOURCES]
    if unknown:
        raise KeyError("undefined source key(s): %s" % ", ".join(unknown))
    return list(keys)
