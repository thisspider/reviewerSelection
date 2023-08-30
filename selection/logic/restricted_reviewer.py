import pandas as pd
import requests
from fuzzywuzzy import fuzz, process

source_id = 'S4210172581'
api_uri = f'https://api.openalex.org/works?filter=primary_location.source.id:{source_id}'
resp = requests.get(api_uri).json()
results = resp['results']
results_df = pd.DataFrame(results)

"""
Steps to extract and consolidate names:
    Input: string of url/path for csv
        restricted_general = './consolidated restricted/RESTRICTED GENERAL-Table 1.csv'
        restricted_consulting = './consolidated restricted/RESTRICTED CONSULTING-Table 1.csv'
        unavailable = './consolidated restricted/RESTRICTED CONSULTING-Table 1.csv'
    Output:
        arr[str]
        ['Ariela Schachter', 'Regina Baker', 'Peter Catron', 'Leisy Abrego','Pete Aceves'...]
"""
def retrieve_restricted_names(restricted_general: str, restricted_consulting: str, unavailable:str):
    restricted_general = pd.read_csv(restricted_general)
    restricted_consulting = pd.read_csv(restricted_consulting, header=None)
    unavailable = pd.read_csv(unavailable, header=None)
    restricted_general = restricted_general.drop(columns=['Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4'])
    restricted_consulting = restricted_consulting.drop(columns=[1, 2, 3, 4])
    restricted_general['Full Name'] = restricted_general['Reviewer First Name'] + ' ' + restricted_general['Reviewer Last Name']
    restricted_consulting.columns = ['Full Name']
    restricted_general = restricted_general[['Full Name']]
    unavailable['Full Name'] = unavailable[0]
    unavailable = unavailable[['Full Name']]
    restricted_names = pd.concat([restricted_consulting,restricted_general, unavailable],ignore_index=True)
    return restricted_names['Full Name'].array
'''
    Warning: Paths may be subjected to change and retrieving restricted names will depend on folder architecture
'''
restricted_general = './consolidated restricted/RESTRICTED GENERAL-Table 1.csv'
restricted_consulting = './consolidated restricted/RESTRICTED CONSULTING-Table 1.csv'
unavailable = './consolidated restricted/RESTRICTED CONSULTING-Table 1.csv'
restricted_names = retrieve_restricted_names(restricted_general, restricted_consulting, unavailable)

def get_authors(restrictions=False):
    authors = []
    for result in results:
        for authorship in result['authorships']:

            author = {
                'display_name': authorship['author']['display_name'],
                'id': authorship['author']['id']
            }
            authors.append(author)
    for author in authors:
        first_last = author['display_name'].split(' ')
        author['display_name'] = first_last[0] + ' ' + first_last[-1]
    if restrictions:
        authors = [a['display_name'] for a in authors if a['display_name'] not in restricted_names]

    return authors
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
        matches.append(res)
    return matches
