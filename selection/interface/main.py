import os
from pathlib import Path

import pandas as pd

from selection.logic.create_candidate_list import create_ref_csv, extract_refs
from selection.logic.merge_operation import merge_references_oaworks
from selection.logic.openalex_matching import cosine_match, rapidfuzz_match
from selection.logic.pdf import PDF

MODEL = os.getenv("MODEL", "cosine")

print(f"Model set to '{MODEL}'.")

# 1 Link pdf to openalex
# Extraction and matching

# 2 Create candidate list

# 3 Select reviewers from candidate list


def get_references_from_pdf(path: str):
    """
    Input: Path to pdf file.
    Output: List of ids for each reference that was extracted out of the pdf
            and the pdf.
    -> ids (list), pdf (class object)
    """
    # Extract the references out of the pdf
    pdf = PDF(path)
    extracted_references = pdf.references

    # Load the dataframe with all of the relevant works
    def load_data(path):
        return pd.read_csv(path)

    start_path = Path(__file__).parents[2] / "work_data" / "all_works_sociology.csv"
    all_works_df = load_data(str(start_path))

    # Fuzzymatch the works dataframe with the extracted references -> merge
    openalex_ids = merge_references_oaworks(
        extracted_references=extracted_references,
        openalex_works=all_works_df,
    )

    return openalex_ids, pdf


def create_candidates_df(openalex_ids: list):
    """
    Input: Id list of the references.
    Output: Dataframe of works that are candidates for being reviewers.
    -> Every work in references + every cited work inside of the referenced work
    """

    # Get a list of dictionaries
    # Each dictionary represents on work
    extracted_works = extract_refs(openalex_ids)

    # Turn list of dictionaries into DataFrame
    # columns=["oa_id", "journal_issnl", "authors", "abstracts"]
    candidate_df = create_ref_csv(extracted_works)

    return candidate_df


def select_reviewers(pdf: object, candidate_df: pd.DataFrame):
    """
    Input: pdf class object and DataFrame with all the candidates
    Output: DataFrame with the top two matched abstracts
    """

    # Get abstract of pdf
    pdf_abstract = pdf.abstract

    # Turn candidate DataFrame into list of candidate abstracts
    # candidate_abstract_list = candidate_df["abstracts"]

    if MODEL == "fuzzymatch":
        # Turn candidate DataFrame into list of candidate abstracts
        candidate_abstract_list = candidate_df["abstracts"]
        # Match pdf abstract with candidate abstracts
        match_df = rapidfuzz_match(pdf_abstract, candidate_abstract_list)

    elif MODEL == "cosine":
        # Match pdf abstract with candidate abstracts
        match_df = cosine_match(pdf, candidate_df)

    elif MODEL == "spacy":
        pass

    elif MODEL == "berttopics":
        print("Berttopics has not been created yet.")

    else:
        print("No model was defined!")

    return match_df
