from rapidfuzz import process, fuzz
import pandas as pd

choices = ["Atlanta Falcons", "New York Jets", "New York Giants", "Dallas Cowboys"]
extracted_references = ["Cowboys", "Falcons"]

def rapidfuzz_match(extracted_references: list, openalex_works: list, scorer = fuzz.WRatio):
    top_match = []
    second_match = []
    third_match = []
    choices = openalex_works
    for reference in extracted_references:
        # possible scorers are fuzz.WRatio , fuzz.partial_ratio , fuzz.token_set_ratio , fuzz.partial_token_set_ratio , fuzz.token_sort_ratio
        top, second, third = process.extract(reference, choices, scorer=scorer, limit=3)
        top_match.append(top)
        second_match.append(second)
        third_match.append(third)
    matched_df = pd.DataFrame(list(zip(extracted_references, top_match, second_match, third_match)), columns=['extracted_reference', 'top_match', 'second_match', 'third_match'])
    return matched_df

def get_unique_ids(matched_df, openalex_works, openalex_id_col_name):
    openalex_ids = []
    for top_match in matched_df['top_match']:
        index = top_match[2]
        openalex_id = openalex_works[openalex_id_col_name].iloc[index,:]
        openalex_ids.append(openalex_id)
    matched_df["openalex_ids"] = openalex_ids
    return matched_df


test = rapidfuzz_match(extracted_references=extracted_references, openalex_works=choices)
test.head()
