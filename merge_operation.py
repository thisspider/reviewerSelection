from openalex_matching import rapidfuzz_match, get_unique_ids
import pandas as pd
from rapidfuzz import fuzz
import time

# references_path = './raw_data/AJS_1_teeger2023.pdf.txt'
# oa_path = "./all_works_sociology.csv"

def get_references_from_path(references_path):
    extracted_references = pd.read_csv(references_path, delimiter='\t')
    return extracted_references

def get_openalex_from_path(oa_path):
    openalex_works = pd.read_csv(oa_path)
    return openalex_works

# openalex_works = get_openalex_from_path(oa_path)

def merge_references_oaworks(extracted_references: dataframe, openalex_works: dataframe, scorer=fuzz.token_sort_ratio):
    '''
    Take as an input two dataframes.
    '''

    start_time = time.time()

    openalex_works_list = list(openalex_works['concat_name_title'])
    extracted_references_list = list(extracted_references.iloc[:,0])
    matched_df = rapidfuzz_match(extracted_references=extracted_references_list, openalex_works = openalex_works_list, scorer=scorer)
    matched_df_oa = get_unique_ids(matched_df, openalex_works, 'id')
    end_time = time.time()

    print(f"Time taken: {end_time - start_time} seconds")
    return matched_df_oa['id']
