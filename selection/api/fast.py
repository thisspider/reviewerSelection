from enum import Enum
from tempfile import NamedTemporaryFile

import pandas as pd
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import RedirectResponse

from selection.interface.main import (
    OA_WORKS_FILE,
    create_candidates_df,
    get_references_from_pdf,
    select_reviewers,
)
from selection.logic.merge_operation import merge_references_oaworks
from selection.logic.pdf import PDF

app = FastAPI()


class ModelName(str, Enum):
    """Models for matching references."""

    bertopic = "BERTopic"
    cosine = "Cosine-Similarity"
    fuzzymatch = "FuzzyMatching"
    spacy = "Spacy"


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
    assert pdf_file.content_type == "application/pdf"

    temp_file = NamedTemporaryFile(suffix=".pdf")
    temp_file.write(pdf_file.file.read())

    pdf = PDF(temp_file.name, references=extract_references)

    return {
        "title": pdf.title,
        "authors": pdf.authors,
        "abstract": pdf.abstract,
        "references": pdf.references,
    }


@app.post("/openalex_references")
def openalex_references(
    references: list[str],
    works_csv_file: UploadFile = File(None),
) -> list[str]:
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

    # Choose whether to use the uploaded CSV or our local version.
    if not works_csv_file:
        works_csv_file = OA_WORKS_FILE
    else:
        temp_file = NamedTemporaryFile(suffix=".csv")
        temp_file.write(works_csv_file.file.read())
        works_csv_file = temp_file.name

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
    return create_candidates_df(pd.Series(openalex_works)).to_dict(orient="records")


@app.post("/reviewers")
def reviewers(abstract: str, candidate_works: list[str], model: ModelName = "cosine"):
    """
    Given a manuscript's abstract,
    return a list of top-matching OpenAlex Work IDs for candidate works,
    using the specified model.
    """
    if model == ModelName.bertopic:
        ...
    elif model == ModelName.cosine:
        ...
    elif model == ModelName.spacy:
        ...
    elif model == ModelName.fuzzymatch:
        ...
    return model


@app.post("/select")
def select(uploaded_pdf: UploadFile):
    """
    Give x recommendations for reviewers for the article in the pdf.
    """
    # Save uploaded_pdf
    pdf = uploaded_pdf.file.read()

    # Create temporary file/path
    temp_pdf = NamedTemporaryFile(suffix=".pdf")
    temp_pdf.write(pdf)

    # Run functions
    openalex_ids, pdf = get_references_from_pdf(temp_pdf.name)
    print("Step1 done")
    candidates_df = create_candidates_df(openalex_ids)
    print("Step2 done")
    reviewers_df = select_reviewers(pdf.abstract, candidates_df)
    print("Step3 done")

    # Close temporary file
    temp_pdf.close()
    print("closed")

    # Turn DataFrame to json string
    json_string = reviewers_df.to_json()
    print("Turned to json")
    print(json_string)

    return json_string
