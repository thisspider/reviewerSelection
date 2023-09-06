import requests

from selection.logic import DATA

BACKEND_URL = "http://localhost:8000"


def test_api():
    # Step 1
    files = {"pdf_file": (DATA / "test.pdf").open("rb")}
    response = requests.post(
        BACKEND_URL + "/pdf", params={"extract_references": True}, files=files
    )
    pdf_data = response.json()
    assert "title" in pdf_data
    assert "abstract" in pdf_data
    assert "authors" in pdf_data
    assert "references" in pdf_data

    # Step 2
    response = requests.post(
        BACKEND_URL + "/openalex_references",
        json={
            "references": pdf_data["references"],
        },
    )
    openalex_works = response.json()

    # Step 3
    response = requests.post(BACKEND_URL + "/candidate_works", json=openalex_works)
    candidate_works = response.json()

    # Step 4
    response = requests.post(
        BACKEND_URL + "/reviewers",
        json={
            "abstract": pdf_data["abstract"],
            "candidate_works": candidate_works,
        },
    )
    reviewers = response.json()
    print(reviewers)


def test_openalex_references():
    references = [
        "Abdelal, Rawi, Yoshiko M. Herrera, Alastair Iain Johnston, and Rose "
        "McDermott. 2006. “Identity as a Variable.” Perspectives on Politics "
        "4 (4): 695–711.",
        "Alba, Richard, and Victor Nee. 2003. Remaking the American Mainstream: "
        "Assimilation and Contemporary Immigration. Cambridge, Mass.: "
        "Harvard University Press.",
    ]
    response = requests.post(BACKEND_URL + "/openalex_references", json=references)
    assert response.json() == [
        "https://openalex.org/W2859186085",
        "https://openalex.org/W1964398892",
    ]


def test_candidate_works():
    target_oa_ids = [
        "W2859186085",
        "W2511126224",
        "W2962890699",
        "W1552443447",
        "W2956796797",
        "W2892323740",
        "W4245727781",
        "W2134702882",
        "W4247628946",
        "W2011366791",
    ]
    response = requests.post(BACKEND_URL + "/candidate_works", json=target_oa_ids)
    assert list(response.json()[0].keys()) == [
        "id",
        "publication_year",
        "language",
        "journal_issnl",
        "journal_name",
        "authors",
        "author_institutions",
        "title",
        "concepts_name",
        "concepts_level",
        "concepts_score",
        "cited_by_count",
        "referenced_works",
        "related_works",
        "abstracts",
        "works_referenced_related",
        "authors_first_lastname",
        "title_slugified",
        "concat_name_title",
    ]
