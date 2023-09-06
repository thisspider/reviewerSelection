import pandas as pd

from selection.logic import OA_WORKS_FILE, ModelName
from selection.logic.openalex_matching import (
    cosine_match,
    load_tfidf_cosine_match,
    rapidfuzz_match,
)
from selection.logic.spacy_similarity import calculate_spacy_similarity



def select_reviewers(
    abstract: str, candidate_df: pd.DataFrame, model: ModelName
) -> pd.DataFrame | None:
    """
    Return DataFrame with the top two matched abstracts.

    The manuscript's abstract is matched to works from the DataFrame containing
    all candidate works.
    """

    print(f"Calculating candidates using {model}...")

    if model == ModelName.fuzzymatch:
        # Turn candidate DataFrame into list of candidate abstracts
        candidate_abstract_list = candidate_df["abstracts"]

        # Match pdf abstract with candidate abstracts
        return rapidfuzz_match(abstract, candidate_abstract_list)

    elif model == ModelName.cosine:
        # Match pdf abstract with candidate abstracts
        return cosine_match(abstract, candidate_df)

    elif model == ModelName.tfidf_all:
        # Match pdf abstract with all abstracts from relevant journals
        return load_tfidf_cosine_match(
            pd.read_csv(OA_WORKS_FILE), abstract, "finalized_tfidf_model.sav"
        )

    elif model == ModelName.spacy:
        # Match pdf abstract with all abstracts from relevant journals
        return calculate_spacy_similarity(abstract, candidate_df)

    elif model == ModelName.spacy_all:
        # Match pdf abstract with all abstracts from relevant journals
        candidate_df = pd.read_csv(OA_WORKS_FILE)
        return calculate_spacy_similarity(abstract, candidate_df)

    print(f"{model} has not been implemented yet.")
