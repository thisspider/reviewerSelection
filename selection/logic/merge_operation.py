import time

import pandas as pd
from rapidfuzz import fuzz

from selection.logic.openalex_matching import rapidfuzz_match


def merge_references_oaworks(
    extracted_references: list,
    openalex_works: pd.DataFrame,
    scorer=fuzz.token_sort_ratio,
):
    print("Fuzzy-matching references from PDF with known articles...")
    start_time = time.time()

    openalex_works_list = list(openalex_works["concat_name_title"])
    matched_df = rapidfuzz_match(
        extracted_references=extracted_references,
        openalex_works=openalex_works_list,
        scorer=scorer,
    )
    matched_df_oa = get_unique_ids(matched_df, openalex_works, "id")

    print(f"Done. ({int(time.time() - start_time)}s)")
    return matched_df_oa["openalex_ids"]


def get_unique_ids(matched_df, openalex_works, openalex_id_col_name):
    """
    Optional: Can fold get_unique_ids into rapidfuzz_match if refactoring is
    neccessary Both return the same Dataframe
    """
    openalex_ids = []
    for top_match in matched_df["top_match"]:
        index = top_match[2]
        openalex_id = openalex_works[openalex_id_col_name][index]
        openalex_ids.append(openalex_id)
    matched_df["openalex_ids"] = openalex_ids
    return matched_df
