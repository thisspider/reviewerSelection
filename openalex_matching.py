from rapidfuzz import process, fuzz
import pandas as pd

'''
    Warning: choices and extracted_references subjected to change
'''
choices = ["Atlanta Falcons", "New York Jets", "New York Giants", "Dallas Cowboys"]
extracted_references = ["Cowboys", "Falcons"]

def rapidfuzz_match(extracted_references: list, openalex_works: list, scorer = fuzz.WRatio):
    top_match = []
    second_match = []
    third_match = []
    top_names = []
    top_scores = []
    top_indexes = []
    choices = openalex_works
    for reference in extracted_references:
        # possible scorers are fuzz.WRatio , fuzz.partial_ratio , fuzz.token_set_ratio , fuzz.partial_token_set_ratio , fuzz.token_sort_ratio
        top, second, third = process.extract(reference, choices, scorer=scorer, limit=3)
        top_score = top[1]
        top_index = top[2]
        top_name = top[0]
        top_names.append(top_name)
        top_scores.append(top_score)
        top_indexes.append(top_index)
        top_match.append(top)
        second_match.append(second)
        third_match.append(third)
    matched_df = pd.DataFrame(list(zip(extracted_references, top_match,top_names, top_scores, top_indexes, second_match, third_match)), columns=['extracted_reference', 'top_match', 'second_match', 'third_match'])
    return matched_df

'''
    Optional: Can fold get_unique_ids into rapidfuzz_match if refactoring is neccessary
    Both return the same Dataframe
'''
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
