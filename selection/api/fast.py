from tempfile import NamedTemporaryFile
from time import time
from typing import Annotated

import pandas as pd
from fastapi import Body, FastAPI, HTTPException, UploadFile
from fastapi.responses import ORJSONResponse, RedirectResponse

from selection.logic import OA_WORKS_FILE, ModelName
from selection.logic.bigquery import load_data_from_bigquery
from selection.logic.create_candidate_list_from_csv import extract_works_cited_by_target
from selection.logic.merge_operation import merge_references_oaworks
from selection.logic.openalex_matching import (
    cosine_match,
    load_tfidf_cosine_match,
    rapidfuzz_match,
)
from selection.logic.pdf import PDF
from selection.logic.spacy_similarity import calculate_spacy_similarity

app = FastAPI(default_response_class=ORJSONResponse)

load_data_from_bigquery(path=OA_WORKS_FILE)


@app.get("/", include_in_schema=False)
def root():
    """Redirect users to the documentation."""
    return RedirectResponse("/docs/")


@app.post("/pdf")
def pdf(pdf_file: UploadFile, extract_references: bool = True):
    """Return the data extracted from a manuscript file.

    The data is extracted using our own parser which is built on top of
    [PDFQuery](https://github.com/jcushman/pdfquery) and
    [refextract](https://github.com/inspirehep/refextract/).
    The data returned is:

    - title
    - list of authors
    - abstract
    - list of references

    The most time is spent extracting the list of references. If you don't
    care for them and just want the base information,
    pass `extract_references=False` for a quicker response.
    """
    temp_file = NamedTemporaryFile(suffix=".pdf")
    temp_file.write(pdf_file.file.read())

    start = time()
    print("Reading PDF...")

    try:
        pdf = PDF(temp_file.name, references=extract_references)
    except Exception as exc:
        return {
            "title": "",
            "authors": [],
            "abstract": "",
            "references": [],
            "_error_": str(exc),
        }

    duration = time() - start
    print(f"Done. ({int(duration)}s)")

    return {
        "title": pdf.title,
        "authors": pdf.authors,
        "abstract": pdf.abstract,
        "references": pdf.references,
    }


@app.post("/openalex_references")
def openalex_references(references: list[str]) -> list[str]:
    """
    Match the given list of references
    (obtained by extracting them from a PDF manuscript)
    to the list of [OpenAlex](https://openalex.org) works.
    The OpenAlex works are either taken from the default data that this app
    has been started with,
    or from a given CSV file.

    The response is a JSON formatted Pandas DataFrame with OpenAlex Work ID
    for each matched reference input.
    """

    works_csv_file = OA_WORKS_FILE
    result = merge_references_oaworks(
        extracted_references=references,
        openalex_works=pd.read_csv(works_csv_file),
    )
    return list(result)


@app.post("/candidate_works")
def candidate_works(openalex_works: list[str]) -> list[dict]:
    """Return list of OpenAlex Works that are candidates for being reviewers.

    The list of related works is extracted from citations of citations
    of the input manuscript in OpenAlex.
    """
    return extract_works_cited_by_target(openalex_works).to_dict(orient="records")


@app.post("/reviewers")
def reviewers(
    abstract: Annotated[str, Body()],
    candidate_works: list[dict],
    model: ModelName = Body(ModelName.tfidf_all),
):
    """
    Given a manuscript's abstract,
    return a list of top-matching OpenAlex Work IDs for candidate works,
    using the specified model.
    """

    print(f"Calculating candidates using {model}...")

    candidate_df = pd.DataFrame(candidate_works)

    if model == ModelName.fuzzymatch:
        # Match pdf abstract with candidate abstracts
        result = rapidfuzz_match(abstract, candidate_df["abstracts"])
    elif model == ModelName.cosine:
        # Match pdf abstract with candidate abstracts
        result = cosine_match(abstract, candidate_df)
    elif model == ModelName.tfidf_all:
        # Match pdf abstract with all abstracts from relevant journals
        result = load_tfidf_cosine_match(pd.read_csv(OA_WORKS_FILE), abstract)
    elif model == ModelName.spacy:
        # Match pdf abstract with all abstracts from relevant journals
        result = calculate_spacy_similarity(abstract, candidate_df)
    elif model == ModelName.spacy_all:
        # Match pdf abstract with all abstracts from relevant journals
        candidate_df = pd.read_csv(OA_WORKS_FILE)
        result = calculate_spacy_similarity(abstract, candidate_df)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"{model} has not been implemented.",
        )

    return result.to_dict(orient="records")
