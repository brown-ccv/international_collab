import bibtexparser
import os
import pandas as pd
import re

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
            pubs = read_bibtex(folder + f)
            publications += pubs.entries
    return publications

d = read_all_bibtex('../wos_bibtex/')


def get_brown_authors(affiliation_str):
    '''
    Given the value of the `affiliation` entry from a Web-of-Science BibTex
    entry, this function returns the authors affiliated with Brown University.
    '''
    str_list = affiliation_str.split('Brown Univ')
    out = []

    for s in str_list[0:-1]:            # ignore last element
        last_newline = s.rfind('\n')
        if last_newline != -1:
            brown_authors_tmp = s[last_newline+1:].split('; ')
            brown_authors = [a.strip(', ') for a in brown_authors_tmp]

            out += brown_authors
    return list(set(out))


def get_international_authors(affiliation_str):
    affiliation_list = affiliation_str.split('\n')
    print(affiliation_list)

    for affiliation in affiliation_list:
        if affiliation[-4:] == 'USA.':
            print("hit this")
            affiliation_list.remove(affiliation)
    print(affiliation_list)
    df = pd.DataFrame()
    i = 0
    for a in affiliation_list:

        # When we only have one author,
        if a.find('; ') == -1:
            # The regex below matches from the beginning
            # of the string until the second comma
            second_comma = re.match('^[^,]*,[^,]*', a).end()
            df.loc[i, 'author'] = a[0:second_comma]
            df.loc[i, 'institution'] = a[second_comma+1:]
            i += 1
        # When we have multiple authors in same affiliation line
        else:
            last_semicolon = a.rfind('; ')
            institution = a[last_semicolon+1:]
            authors = a[0:last_semicolon].split('; ')
            for athr in authors:
                df.loc[i, 'author'] = athr
                df.loc[i, 'institution'] = institution
                i += 1
    return df

get_international_authors(d[1]["affiliation"])


r = '^[^,]*,[^,]*'
s = 'Liang, Xin, Changzhou Univ, Sch Mat Sci \\& Engn, Changzhou 213164, Jiangsu, Peoples R China.'
m = re.match(r, s)
