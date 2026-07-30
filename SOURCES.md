# Sources

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


## Included here

### 3Dmol.js: molecular visualization with WebGL

- **Key** `3dmol`
- **Authors** N. Rego, D. Koes
- **Publisher** Bioinformatics
- **Year** 2015
- **Where** vol. 31, pp. 1322-1324
- **Licence** BSD 3-Clause
- **Link** <https://3dmol.csb.pitt.edu/>

### Standard Atomic Weights

- **Key** `ciaaw`
- **Authors** IUPAC Commission on Isotopic Abundances and Atomic Weights
- **Publisher** IUPAC
- **Year** 2021
- **Where** Current standard atomic weights table
- **Licence** Freely available reference data
- **Link** <https://ciaaw.org/atomic-weights.htm>

## Cited only

### Algorithmic Analysis of Cahn-Ingold-Prelog Rules of Stereochemistry: Proposals for Revised Rules and a Guide for Machine Implementation

- **Key** `hanson-cip-2018`
- **Authors** R. M. Hanson, S. Musacchio, J. W. Mayfield, M. J. Bull, E. L. Willighagen, N. E. Adams
- **Publisher** Journal of Chemical Information and Modeling
- **Year** 2018
- **Where** vol. 58, pp. 1755-1765
- **Licence** Copyright ACS
- **Link** <https://pubs.acs.org/journal/jcisd8>

### Basic Principles of the CIP-System and Proposals for a Revision

- **Key** `prelog-helmchen-1982`
- **Authors** V. Prelog, G. Helmchen
- **Publisher** Angewandte Chemie International Edition
- **Year** 1982
- **Where** vol. 21, pp. 567-583
- **Licence** Copyright Wiley
- **Link** <https://onlinelibrary.wiley.com/journal/15213773>

### Better Informed Distance Geometry: Using What We Know To Improve Conformation Generation

- **Key** `etkdg-2015`
- **Authors** S. Riniker, G. A. Landrum
- **Publisher** Journal of Chemical Information and Modeling
- **Year** 2015
- **Where** vol. 55, pp. 2562-2574
- **Licence** Copyright ACS
- **Link** <https://pubs.acs.org/journal/jcisd8>

### ChEBI: Chemical Entities of Biological Interest

- **Key** `chebi`
- **Authors** EMBL-EBI
- **Publisher** European Molecular Biology Laboratory
- **Year** 2026
- **Where** Ontology of small molecules of biological relevance
- **Licence** CC BY 4.0
- **Link** <https://www.ebi.ac.uk/chebi/>

### Enzyme Nomenclature

- **Key** `iubmb-enzyme`
- **Authors** IUBMB Nomenclature Committee
- **Publisher** International Union of Biochemistry and Molecular Biology
- **Year** 2026
- **Where** EC number assignments, served via ExplorEnz
- **Licence** Freely available reference nomenclature
- **Link** <https://iubmb.qmul.ac.uk/enzyme/>

### Introduction to Spectroscopy

- **Key** `pavia`
- **Authors** D. L. Pavia, G. M. Lampman, G. S. Kriz, J. R. Vyvyan
- **Publisher** Cengage Learning
- **Year** 2015
- **Where** 5th edition. ISBN 978-1-285-46012-3
- **Licence** Copyright Cengage
- **Link** <https://www.cengage.com/>

### Lehninger Principles of Biochemistry

- **Key** `lehninger`
- **Authors** D. L. Nelson, M. M. Cox
- **Publisher** W. H. Freeman / Macmillan Learning
- **Year** 2021
- **Where** 8th edition. ISBN 978-1-319-22800-2
- **Licence** Copyright Macmillan
- **Link** <https://www.macmillanlearning.com/>

### MassBank Europe

- **Key** `massbank`
- **Authors** MassBank consortium
- **Publisher** MassBank Europe / NORMAN network
- **Year** 2026
- **Where** Open repository of experimental mass spectra. Not used offline; the intended source if a network lookup layer is added
- **Licence** CC BY 4.0
- **Link** <https://massbank.eu/>

### Merck molecular force field. I. Basis, form, scope, parameterization, and performance of MMFF94

- **Key** `mmff94`
- **Authors** T. A. Halgren
- **Publisher** Journal of Computational Chemistry
- **Year** 1996
- **Where** vol. 17, pp. 490-519
- **Licence** Copyright Wiley
- **Link** <https://onlinelibrary.wiley.com/journal/1096987x>

### NIST Chemistry WebBook, SRD 69

- **Key** `nist-webbook`
- **Authors** P. J. Linstrom, W. G. Mallard (eds.)
- **Publisher** National Institute of Standards and Technology
- **Year** 2026
- **Where** Reference infrared and mass spectra. Consulted for characteristic values; no spectra are reproduced here
- **Licence** US Government work; the interface restricts systematic retrieval
- **Link** <https://webbook.nist.gov/chemistry/>

### Nomenclature of Organic Chemistry: Recommendations and Preferred Names 2013

- **Key** `iupac-bluebook-2013`
- **Authors** H. A. Favre, W. H. Powell (eds.)
- **Publisher** IUPAC / Royal Society of Chemistry
- **Year** 2013
- **Where** ISBN 978-0-85404-182-4. CIP rules at P-91 and P-92
- **Licence** Copyright IUPAC/RSC
- **Link** <https://iupac.org/what-we-do/books/bluebook/>

### Organic Chemistry

- **Key** `clayden`
- **Authors** J. Clayden, N. Greeves, S. Warren
- **Publisher** Oxford University Press
- **Year** 2012
- **Where** 2nd edition. ISBN 978-0-19-927029-3
- **Licence** Copyright OUP
- **Link** <https://global.oup.com/>

### Protein and amino acid requirements in human nutrition

- **Key** `who-fao-unu-935`
- **Authors** Joint WHO/FAO/UNU Expert Consultation
- **Publisher** World Health Organization
- **Year** 2007
- **Where** WHO Technical Report Series 935. ISBN 978-92-4-120935-9
- **Licence** WHO publication, reuse under WHO terms
- **Link** <https://www.who.int/publications/i/item/9241209351>

### PubChem

- **Key** `pubchem`
- **Authors** National Center for Biotechnology Information
- **Publisher** U.S. National Library of Medicine, NIH
- **Year** 2026
- **Where** Compound records and reference structures
- **Licence** Public domain (work of the U.S. Government)
- **Link** <https://pubchem.ncbi.nlm.nih.gov/>

### RDKit: Open-source cheminformatics

- **Key** `rdkit`
- **Authors** G. Landrum and contributors
- **Publisher** RDKit project
- **Year** 2026
- **Where** Used at build time for depiction coordinates, embedding and CIP labelling
- **Licence** BSD 3-Clause
- **Link** <https://www.rdkit.org/>

### Reactome Pathway Database

- **Key** `reactome`
- **Authors** Reactome Consortium
- **Publisher** EMBL-EBI, OICR, NYU Langone, OHSU
- **Year** 2026
- **Where** Curated human pathway reactions
- **Licence** CC BY 4.0
- **Link** <https://reactome.org/>

### Rhea: an expert-curated resource of biochemical reactions

- **Key** `rhea`
- **Authors** EMBL-EBI / SIB Swiss Institute of Bioinformatics
- **Publisher** European Molecular Biology Laboratory
- **Year** 2026
- **Where** Balanced biochemical reaction equations
- **Licence** CC BY 4.0
- **Link** <https://www.rhea-db.org/>

### Specification of Molecular Chirality

- **Key** `cip-1966`
- **Authors** R. S. Cahn, C. Ingold, V. Prelog
- **Publisher** Angewandte Chemie International Edition
- **Year** 1966
- **Where** vol. 5, pp. 385-415
- **Licence** Copyright Wiley
- **Link** <https://onlinelibrary.wiley.com/journal/15213773>

### Spectrometric Identification of Organic Compounds

- **Key** `silverstein`
- **Authors** R. M. Silverstein, F. X. Webster, D. J. Kiemle, D. L. Bryce
- **Publisher** Wiley
- **Year** 2014
- **Where** 8th edition. ISBN 978-0-470-61637-6. The standard correlation tables for IR, NMR and mass spectrometry
- **Licence** Copyright Wiley
- **Link** <https://www.wiley.com/>
