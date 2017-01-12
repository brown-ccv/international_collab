## Description
This repo contains the necessary files for generating a .csv with Brown University researchers and their international collaborators. The work is done by the Python script file `parse_wos_bibtex.py`.

This script reads in data from .bib files (stored in `wos_bibtex/`) and returns a .csv where the rows correspond to "instances of collaboration" between a Brown researcher and an international researcher. Note that a single publication can have many of these instances, since and "instance" is defined to be any pair consisting of a Brown researcher and an international collaborator. So, in the case of a paper with a Brown researcher and two international collaborators, that single publication will count as two "instances of collaboration" for the Brown researcher because the Brown researcher is paired with each of the two collaborators.

## Execution
The script is executed from the command line, and requires a single command-line argument: the location of the directory containing the BibTex files to be parsed (e.g., `python parse_wos_bibtex.py ../wos_bibtex/`)

## Dependencies
This code was written and tested using Python 3.6, but it should also work with Python 2.7. The scipt requires the _pandas_, and _bibtexparser_ packages.
