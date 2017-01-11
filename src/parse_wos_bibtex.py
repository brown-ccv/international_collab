#!/usr/bin/env/ python

import bibtexparser
import os
import pandas as pd
import re
import sys

from time import time


def read_bibtex(filename):
    with open(filename) as bibtex_file:
        bibtex_str = bibtex_file.read()
    bib_data = bibtexparser.loads(bibtex_str)
    return bib_data

## example use:
# bib_data = read_bibtex('./wos_bibtex/savedrecs1.bib')
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

## example use:
# d = read_all_bibtex('../wos_bibtex/')


def get_brown_authors(affiliation_str, isi_id):
    '''
    Given the value of the `affiliation` entry from a Web-of-Science BibTex
    entry, this function returns the authors affiliated with Brown University.
    '''
    str_list = affiliation_str.split('Brown Univ')
    authors = []

    for s in str_list[0:-1]:            # ignore last element
        last_newline = s.rfind('\n')
        if last_newline != -1:
            brown_authors_tmp = s[last_newline+1:].split('; ')
            brown_authors = [a.strip(', ') for a in brown_authors_tmp if \
              a != '' and '(Reprint Author)' not in a]


            authors += brown_authors

    df = pd.DataFrame()
    df['brown_author'] = list(set(authors))
    df['isi_id'] = isi_id
    return df

## example use:
# get_brown_authors(d[1]["affiliation"], '123')


def get_international_authors(affiliation_str, isi_id):
    '''
    Given the value of the `affiliation` entry from a Web-of-Science BibTex
    entry, this function returns the authors affiliated with non-US institutions.
    '''
    affiliation_list = affiliation_str.split('\n')

    usa_authors = []
    for affiliation in affiliation_list:
        if affiliation[-4:] == 'USA.':
            usa_authors.append(affiliation)

    # strip out the authors from the USA
    for athr in usa_authors:
        affiliation_list.remove(athr)

    df = pd.DataFrame()
    i = 0                           # row counter we'll increment
    for a in affiliation_list:

        # When we only have one author,
        if a.find('; ') == -1:
            # The regex below matches from the beginning
            # of the string until the second comma
            second_comma = re.match('^[^,]*,[^,]*', a).end()
            df.loc[i, 'intl_author'] = a[0:second_comma]
            df.loc[i, 'institution'] = a[second_comma+1:]
            i += 1
        # When we have multiple authors in same affiliation line
        else:
            last_semicolon = a.rfind('; ')
            institution = a[last_semicolon+1:]
            authors = a[0:last_semicolon].split('; ')
            for athr in authors:
                df.loc[i, 'intl_author'] = athr
                df.loc[i, 'institution'] = institution
                i += 1

    # We will pd.merge() with the Brown authors table
    # using the publication ID
    df['isi_id'] = isi_id

    # FIXME: note that this returns duplicates if a given author
    # has multiple affiliations, which is not uncommon
    return df

## example use:
# get_international_authors(d[1]["affiliation"], '123')


def extract_publication_data(pub_dict):
    '''
    Given a publication's data in dict form, as we get from bibtex, this
    function returns a dataframe with the Brown authors in one column and
    their respective collaborators in the other column. The institution and
    publication ID are also in the dataframe.
    '''
    isi_id = pub_dict["ID"]
    brown_authors = get_brown_authors(pub_dict["affiliation"], isi_id)
    intl_authors = get_international_authors(pub_dict["affiliation"], isi_id)

    authors = pd.merge(brown_authors, intl_authors, how = 'left', on = 'isi_id')
    n = authors.shape[0]

    # There are duplicate rows because the Reprint Author is listed twice,
    # so we remove the duplication before returning the dataframe
    keep_col = ['(Reprint Author)' not in x for x in authors['intl_author']]

    return authors.loc[keep_col, :]

## example use:
# extract_publication_data(d[6])


def parse_all_publication_data(dict_list):
    n = len(dict_list)
    df = extract_publication_data(dict_list[0])

    for i in range(1, n):
        newdata = extract_publication_data(dict_list[i])
        df = df.append(newdata, ignore_index = True)

    # Count instances of collaboration for each Brown author. And
    # note that a single publication for a Brown author will have as
    # many "instances" of collaboration as there are international
    # authors on that paper.
    collab_cnt = df.groupby('brown_author').size().reset_index()
    collab_cnt.columns = ['brown_author', 'collab_instances']
    df = pd.merge(df, collab_cnt, how = 'left', on = 'brown_author')

    col_order = ['brown_author', 'intl_author', 'institution', 'isi_id', 'collab_instances']

    return df[col_order].sort_values('brown_author', ascending = True).reset_index(drop = True)

## example use:
# res = parse_all_publication_data(d[0:20])


if __name__ == '__main__':
    t0 = time()
    folder = sys.argv[1]
    print('Reading BibTex data...')

    d = read_all_bibtex(folder)
    print('Extracting publication information...')

    df = parse_all_publication_data(d)
    print('Writing results to .csv file...')
    df.to_csv('results.csv', index = False)
    elapsed = time() - t0
    print('Done! Total run time was {0} seconds.'.format(elapsed))
