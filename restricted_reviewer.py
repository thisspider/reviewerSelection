import pandas as pd
import requests
from fuzzywuzzy import fuzz, process

source_id = 'S4210172581'
api_uri = f'https://api.openalex.org/works?filter=primary_location.source.id:{source_id}'
resp = requests.get(api_uri).json()
results = resp['results']
results_df = pd.DataFrame(results)
restricted = ['Edward Witten']

def get_authors(restrictions=False):
    authors = []
    for result in results:
        for authorship in result['authorships']:
            #    for author in authorship['author']:
                    # print(id)
            author = {
                'display_name': authorship['author']['display_name'],
                'id': authorship['author']['id']
            }
            authors.append(author)
    for author in authors:
        first_last = author['display_name'].split(' ')
        author['display_name'] = first_last[0] + ' ' + first_last[-1]
        print(author['display_name'])
    if restrictions:
        authors = [a['display_name'] for a in authors if a['display_name'] not in restricted]

    return authors
"""
Steps to extract and consolidate names: (probably no longer needed)
    restricted_general = pd.read_csv('./consolidated restricted/RESTRICTED GENERAL-Table 1.csv')
    restricted_consulting = pd.read_csv('./consolidated restricted/RESTRICTED CONSULTING-Table 1.csv')
    unavailable = pd.read_csv('./consolidated restricted/RESTRICTED CONSULTING-Table 1.csv')
    restricted_general = restricted_general.drop(columns=['Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4'])
    restricted_general['Full Name'] = restricted_general['Reviewer First Name'] + ' ' + restricted_general['Reviewer Last Name']
    reviewer_names = restricted_general[['Full Name']]
    restricted_consulting = restricted_consulting.drop(columns=['Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4'])
    reviewer_names
    restricted_consulting = restricted_consulting[['Full Name']]
    unavailable = unavailable[['Full Name']]
    reviewer_names = pd.concat([restricted_consulting, reviewer_names])
    reviewer_names = pd.concat([reviewer_names, unavailable], ignore_index=True)
    reviewer_names
    reviewer_names.to_csv('./reviewer_names.csv', encoding='utf-8', index=False)
"""

'''
    Using fuzzywuzzy to iterate through list of author names and checking against list of restricted names
    Input:
       arr[str]: ['Ariela Schachter', 'Regina Baker', 'Peter Catron', Leisy Abrego','Pete Aceves', 'Amy Adamczyk'....]

    Output:
        arr[dict]:
            [{'Edward Witten': ('Caitlin Ahearn', 49, 7)},
            {'Richard Hamilton': ('Richard Arum', 71, 15)},
            {'James Sparks': ('Asad Asad', 48, 16)},
            {'Charles Boyer': ('Regina Baker', 48, 1)},
            {'Krzysztof Galicki': ('Abigail Andrews', 36, 11)},
            {"Giuseppina D'Ambra": ('Asad Asad', 50, 16)}...]
'''
def extract_matches(author_names: list, restrict_authors: list, extract_one=False):
    matches = []
    for author in author_names:
        res = ''
        if extract_one:
            res = {
                    author: process.extractOne(author, restrict_authors)
                }
        else:
            res = {
                    author: process.extract(author, restrict_authors)
                }
            print(res)
        matches.append(res)
    return matches
