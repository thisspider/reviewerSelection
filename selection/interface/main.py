import os
import time
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

DATA = Path(__file__).parents[2] / "work_data"


def get_references_from_pdf(
    manuscript_filepath: Path,
    articles_filepath: Path = DATA / "all_works_sociology.csv",
) -> tuple[list[str], PDF]:
    """
    Fuzzymatch the references extracted from the manuscript PDF
    with the articles from the articles CSV.

    Returns list of matched OpenAlex Work IDs.
    """
    start_time = time.time()
    print("Reading PDF... ")
    pdf = PDF(manuscript_filepath)
    print(f"Done ({int(time.time() - start_time)}s)")

    openalex_ids = merge_references_oaworks(
        extracted_references=pdf.references,
        openalex_works=pd.read_csv(articles_filepath),
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


def select_reviewers(abstract: str, candidate_df: pd.DataFrame) -> pd.DataFrame | None:
    """
    Return DataFrame with the top two matched abstracts.

    The manuscript's abstract is matched to works from the DataFrame containing
    all candidate works.
    """

    if MODEL == "fuzzymatch":
        # Turn candidate DataFrame into list of candidate abstracts
        candidate_abstract_list = candidate_df["abstracts"]

        # Match pdf abstract with candidate abstracts
        return rapidfuzz_match(abstract, candidate_abstract_list)

    elif MODEL == "cosine":
        # Match pdf abstract with candidate abstracts
        return cosine_match(abstract, candidate_df)

    print(f"{MODEL} has not been implemented yet.")