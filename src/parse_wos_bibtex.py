import bibtexparser
import os


def read_bibtex(filename):
    with open(filename) as bibtex_file:
        bibtex_str = bibtex_file.read()
    bib_data = bibtexparser.loads(bibtex_str)
    return bib_data


# bib_data = read_bibtex('./wos_bibtex/savedrecs1.bib')
#
# print(bib_data.entries)

def is_bibtex_file(filename):
    if filename[-4:] == '.bib':
        res = True
    else:
        res = False
    return res


def read_all_bibtex(folder):
    publications = []
    files = os.listdir(folder)
    for f in files:
        if is_bibtex_file(f):
            pubs = read_bibtex(f)
            publications.append(pubs)
    return publications


def get_brown_authors(affiliation_str):
    str_list = affiliation_str.split('Brown Univ')
    out = []

    for s in str_list[0:-1]:            # ignore last element
        last_newline = s.rfind('\n')
        if last_newline != -1:
            brown_authors_tmp = s[last_newline+1:].split('; ')
            brown_authors = [a.strip(', ') for a in brown_authors_tmp]

            out += brown_authors
    return list(set(out))
