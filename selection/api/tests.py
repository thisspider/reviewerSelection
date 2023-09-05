import requests

from selection.interface.main import DATA

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
