#!/usr/bin/env/ python

import bibtexparser
import os
import pandas as pd
import re
import sys
import numpy as np

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


def get_brown_authors(affiliation_str, doi = None):
    '''
    Given the value of the `affiliation` entry from a Web-of-Science BibTex
    entry, this function returns the authors affiliated with Brown University.
    '''
    str_list = affiliation_str.split('\n')      # split by affilations
    authors = []
    found_one = False                           # for sanity check
    for s in str_list:
        idx = s.find('Brown Univ')
        if idx != -1:
            found_one = True
            brown_authors_tmp = s[0:idx].split('; ')
            brown_authors = [a.strip(', ') for a in brown_authors_tmp if \
              a != '' and '(Reprint Author)' not in a]
            authors += brown_authors

    if not found_one:
        print("WARNING: no Brown authors found in {0}".format(doi))

    df = pd.DataFrame()
    df['brown_author'] = list(set(authors))
    df['doi'] = doi
    return df

# get_brown_authors2(d[1]["affiliation"], '123')


def get_international_authors(affiliation_str, doi):
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
        if '(Reprint Author)' in a:
            continue

        # When we only have one author,
        if a.find('; ') == -1:
            # The regex below matches from the beginning
            # of the string until the second comma
            second_comma = re.match('^[^,]*,[^,]*', a).end()

            # Note that we only include an author once, which
            # means that authors with multiple affiliations will
            # only appear once; the affiliation that appears for
            # that author is simply the first one listed.
            if i == 0:
                df.loc[i, 'intl_author'] = a[0:second_comma].strip()
                df.loc[i, 'institution'] = a[second_comma+1:].strip()
                i += 1
            elif a[0:second_comma].strip() not in df['intl_author'].values:
                df.loc[i, 'intl_author'] = a[0:second_comma].strip()
                df.loc[i, 'institution'] = a[second_comma+1:].strip()
                i += 1

        # When we have multiple authors in same affiliation line
        else:
            last_semicolon = a.rfind('; ')
            second_comma = re.match('^[^,]*,[^,]*', a[last_semicolon+1:]).end()
            last_author = a[(last_semicolon + 1):(last_semicolon + 1 + second_comma)]

            authors = a[0:last_semicolon].split('; ')
            authors.append(last_author)
            idx = last_semicolon + 1 + second_comma + 2
            institution = a[idx:]

            for athr in authors:
                if i == 0:
                    df.loc[i, 'intl_author'] = athr.strip()
                    df.loc[i, 'institution'] = institution.strip()
                    i += 1
                elif athr.strip() not in df['intl_author'].values:
                    df.loc[i, 'intl_author'] = athr.strip()
                    df.loc[i, 'institution'] = institution.strip()
                    i += 1

    # We will pd.merge() with the Brown authors table
    # using the publication ID
    df['doi'] = doi
    return df

## example use:
# get_international_authors(d[1]["affiliation"], '123')




def get_all_authors(affiliation_str, doi = None):
    '''
    Given the value of the `affiliation` entry from a Web-of-Science
    BibTex entry, this function returns the authors.
    '''
    affiliation_list = affiliation_str.split('\n')

    df = pd.DataFrame()
    i = 0                           # row counter we'll increment
    for a in affiliation_list:
        if '(Reprint Author)' in a:
            continue

        # When we only have one author,
        if a.find('; ') == -1:
            # The regex below matches from the beginning
            # of the string until the second comma
            second_comma = re.match('^[^,]*,[^,]*', a).end()

            # Note that we only include an author once, which
            # means that authors with multiple affiliations will
            # only appear once; the affiliation that appears for
            # that author is simply the first one listed.
            if i == 0:
                df.loc[i, 'author'] = a[0:second_comma].strip()
                df.loc[i, 'institution'] = a[second_comma+1:]
                i += 1
            elif a[0:second_comma].strip() not in df['author'].values:
                df.loc[i, 'author'] = a[0:second_comma].strip()
                df.loc[i, 'institution'] = a[second_comma+1:]
                i += 1

        # When we have multiple authors in same affiliation line
        else:
            last_semicolon = a.rfind('; ')
            second_comma = re.match('^[^,]*,[^,]*', a[last_semicolon+1:]).end()
            last_author = a[(last_semicolon + 1):(last_semicolon + 1 + second_comma)]

            authors = a[0:last_semicolon].split('; ')
            authors.append(last_author)
            idx = last_semicolon + 1 + second_comma + 2
            institution = a[idx:]

            for athr in authors:
                if i == 0:
                    df.loc[i, 'author'] = athr.strip()
                    df.loc[i, 'institution'] = institution
                    i += 1
                elif athr.strip() not in df['author'].values:
                    df.loc[i, 'author'] = athr.strip()
                    df.loc[i, 'institution'] = institution
                    i += 1

    df['doi'] = doi
    return df

# get_all_authors(d[0]['affiliation'], 123)

def extract_publication_data(pub_dict):
    '''
    Given a publication's data in dict form, as we get from bibtex, this
    function returns a dataframe with the Brown authors in one column and
    their respective collaborators in the other column. The institution and
    publication ID are also in the dataframe.
    '''

    if 'doi' in pub_dict:
        doi = pub_dict['doi']
    else:
        doi = pub_dict['ID']

    brown_authors = get_brown_authors(pub_dict["affiliation"], doi)
    intl_authors = get_international_authors(pub_dict["affiliation"], doi)

    # There are rare cases where we get no international authors. This
    # occurs when the Brown author has an affiliation with a non-US school.
    # In these cases we just return an empty dataframe.
    if intl_authors.shape[0] == 0:
        return pd.DataFrame()

    authors = pd.merge(brown_authors, intl_authors, how = 'left', on = 'doi')
    # n = authors.shape[0]
    if 'author-email' in pub_dict:
        authors['contact_email'] = pub_dict['author-email']
    else:
        authors['contact_email'] = ''

    # # There is a chance that on a given paper an author could be counted
    # # as both an international author and a Brown author because of
    # # dual appointments. We remove all instances of collaboration where
    # # the Brown author is the international author.
    # keep_row = authors['intl_author'] != authors['brown_author']

    return authors #.loc[keep_row, :]

## example use:
# extract_publication_data(d[6])


def count_authors(pub_dict):
    '''
    Given a publication, this function returns a tuple with the
    number of Brown authors, and the number of total authors.
    '''
    affiliation_str = pub_dict['affiliation']
    affils_list = affiliation_str.split('\n')
    cnt_brown = get_brown_authors(affiliation_str).shape[0]
    cnt_authors = get_all_authors(affiliation_str).shape[0]
    return (cnt_brown, cnt_authors)


def keep_publication(pub_dict, min_ratio, team_size):
    n_brown_authors, n_authors = count_authors(pub_dict)
    ratio = n_brown_authors/n_authors
    keep_pub = (n_authors < team_size) or (ratio > min_ratio)
    return keep_pub


def clean_contact_email(s):
    tmp = s.replace('\n', ' ')
    out = tmp.replace('\_', '_')
    return out


def parse_all_publication_data(dict_list, min_ratio = 0.2, team_size = 20):
    n = len(dict_list)
    df = extract_publication_data(dict_list[0])

    for i in range(1, n):
        if keep_publication(dict_list[i], min_ratio, team_size):
            newdata = extract_publication_data(dict_list[i])
            if newdata.shape[0] != 0:
                df = df.append(newdata, ignore_index = True)

    df['has_brown_affil'] = False
    for i in range(df.shape[0]):
        df.loc[i, 'has_brown_affil'] = df.loc[i, 'intl_author'] in df['brown_author'].values
        df.loc[i, 'contact_email'] = clean_contact_email(df.loc[i, 'contact_email'])

    # Here we drop rows where an instance of collaboration is an author
    # with themself. This can happen when a given author has both a Brown
    # and international affiliation.
    keep_row = df['intl_author'] != df['brown_author']
    df = df.loc[keep_row, :]

    # Count instances of collaboration for each international author.
    # Note that a single publication for an author will have as
    # many "instances" of collaboration as there are Brown
    # authors on that paper.
    collab_cnt = df.groupby('intl_author').size().reset_index()
    collab_cnt.columns = ['intl_author', 'collab_instances']
    df = pd.merge(df, collab_cnt, how = 'left', on = 'intl_author')

    col_order = ['intl_author', 'brown_author', 'institution', 'has_brown_affil', 'doi', 'contact_email', 'collab_instances']

    return df[col_order].sort_values(['collab_instances', 'intl_author'], ascending = False).reset_index(drop = True)

## example use:
# res = parse_all_publication_data(d[0:1250])


def find_pub(dict_list, doi):
    '''
    This is a quick function to find a publication in the list given its DOI.
    '''
    n = len(dict_list)
    res = None
    for i in range(n):
        if 'doi' in dict_list[i]:
            if dict_list[i]['doi'] == doi:
                res = dict_list[i]
        else:
            if dict_list[i]['ID'] == doi:
                res = dict_list[i]
    return res

# pub = find_pub(d, '10.1249/MSS.0000000000001054')


def not_in_prior_years(authors, prior_authors):
    n = authors.shape[0]
    keep = pd.Series(np.ones(n, bool))

    for i in range(n):
        if authors[i] in prior_authors.values:
            keep[i] = False
    return list(keep)


def concat_str(x):
    x_uniq = np.unique(x)
    res = '; '.join(v for v in x_uniq)
    return res


def aggregate_intl_author(instances, prior_years):
    intl_authors = instances.loc[:, ['intl_author', \
                                 'has_brown_affil', \
                                 'collab_instances']].drop_duplicates(inplace = False)
    keep_row = not_in_prior_years(intl_authors['intl_author'].values, prior_years['prior_intl_author'])
    intl_authors = intl_authors.loc[keep_row, :]
    agg = instances.pivot_table(values = ['institution', 'brown_author', 'contact_email', 'doi'],
                                             index = 'intl_author',
                                             aggfunc = concat_str).reset_index(drop = False)
    print(intl_authors.columns)
    print(agg.columns)
    res = pd.merge(intl_authors, agg, how = 'left', on = 'intl_author')
    return res


if __name__ == '__main__':
    t0 = time()
    folder = sys.argv[1]
    print('Reading BibTex data...')

    d = read_all_bibtex(folder)
    print('Extracting publication information...')

    instances = parse_all_publication_data(d, 0.2, 20)
    prior_years = pd.read_csv('intl_authors_2014-2015.csv')

    intl_authors = aggregate_intl_author(instances, prior_years)
    intl_authors.to_csv('intl_authors.csv', index = False)

    print('Writing results to .csv file...')
    instances.to_csv('instances.csv', index = False)
    elapsed = time() - t0
    print('Done! Total run time was {0:.2f} seconds.'.format(elapsed))
