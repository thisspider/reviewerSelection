import json
from pathlib import Path

import pytest
from slugify import slugify
from tqdm import tqdm

from ..pdf import get_authors, get_references, get_title
from ..polite_pyalex import pyalex

EXAMPLE_MANUSCRIPT = (
    Path(__file__).resolve().parents[0]
    / "reviewerSelection-data"
    / "EXAMPLE_MANUSCRIPT"
)
OPENALEX_JSON = EXAMPLE_MANUSCRIPT / "OPENALEX_JSON"


@pytest.mark.parametrize(
    "pdf_path,json_path",
    [
        (
            EXAMPLE_MANUSCRIPT / "AJS_1_teeger2023.pdf",
            OPENALEX_JSON / "AJS_1_W4383896243.json",
        ),
        (
            EXAMPLE_MANUSCRIPT / "AJS_2_Sugie2023.pdf",
            OPENALEX_JSON / "AJS_2_W4383874036.json",
        ),
        (
            EXAMPLE_MANUSCRIPT / "AJS_3_flores2023.pdf",
            OPENALEX_JSON / "AJS_3_W4383896166.json",
        ),
    ],
)
def test_reference_count(pdf_path, json_path):
    with json_path.open() as f:
        data = json.load(f)
        num_references_openalex = len(data["referenced_works"])

    assert len(get_references(pdf_path)) == num_references_openalex


def get_references_from_openalex_json_file(json_path):
    with json_path.open() as f:
        data = json.load(f)

    references = []
    referenced_works = data["referenced_works"]

    for article in tqdm(referenced_works):
        article = pyalex.Works()[article]
        authors = [
            author["author"]["display_name"] for author in article["authorships"]
        ]
        year = article["publication_year"]
        title = article.get("title", "")
        references.append(f"{', '.join(authors)}. {year}. {title}")

    references_openalex = [slugify(ref) for ref in references]

    with Path("output.txt").open("w") as fh:
        for ref in references_openalex:
            fh.write(ref)


@pytest.mark.parametrize(
    "pdf_path,title",
    [
        (
            EXAMPLE_MANUSCRIPT / "AJS_1_teeger2023.pdf",
            "(Not) Feeling the Past: Boredom as a Racialized Emotion",
        ),
        (
            EXAMPLE_MANUSCRIPT / "AJS_2_Sugie2023.pdf",
            "Welfare Drug Bans and Criminal Legal Cycling",
        ),
        (
            EXAMPLE_MANUSCRIPT / "AJS_3_flores2023.pdf",
            "Transitory versus Durable Boundary Crossing: "
            "What Explains the Indigenous Population Boom in Mexico?",
        ),
        (
            EXAMPLE_MANUSCRIPT / "ARXIV_1.pdf",
            "Discrimination and Constraints: Evidence from The Voice",
        ),
        pytest.param(
            EXAMPLE_MANUSCRIPT / "FRONTIERS_1.pdf",
            "TREATING BACTERIAL INFECTIONS WITH A PROTEIN FROM A VIRUS",
            marks=pytest.mark.xfail(reason="Breaks pdfQuery due to weird char."),
        ),
        (
            EXAMPLE_MANUSCRIPT / "SOCARXIV_1.pdf",
            "Expectation and Hope. "
            "Experiences of Time by Ecuadorian Returnees Envisioning "
            "a ‘Life Worth Living’",
        ),
        (
            EXAMPLE_MANUSCRIPT / "SOCARXIV_2.pdf",
            "Cognitive Sociology’s three blindspots: decisions, implicit "
            "measures and groups",
        ),
        pytest.param(
            EXAMPLE_MANUSCRIPT / "SOCARXIV_3.pdf",
            "Global mobility of the recent STEM postdoctoral workforce "
            "registered in ORCID",
            marks=pytest.mark.xfail(reason="All elements have size 12pt"),
        ),
        (
            EXAMPLE_MANUSCRIPT / "SOCARXIV_4.pdf",
            "To make a difference: Responding to migration and its (im)possible "
            "demands in returns to Cuba",
        ),
    ],
)
def test_title(pdf_path: str, title: str):
    """Test that the title obtained via `get_title()` is the same as in the PDF."""
    assert get_title(pdf_path)[0] == title


@pytest.mark.parametrize(
    "pdf_path,authors",
    [
        (EXAMPLE_MANUSCRIPT / "AJS_1_teeger2023.pdf", ["Chana Teeger"]),
        (
            EXAMPLE_MANUSCRIPT / "AJS_2_Sugie2023.pdf",
            [
                "Naomi F. Sugie",
                "Carol Newark",
            ],
        ),
        (
            EXAMPLE_MANUSCRIPT / "AJS_3_flores2023.pdf",
            [
                "René D. Flores",
                "Regina Martínez Casas",
                "María Vignau Loría",
            ],
        ),
        (EXAMPLE_MANUSCRIPT / "ARXIV_1.pdf", ["Anuar Assamidanov"]),
        pytest.param(
            EXAMPLE_MANUSCRIPT / "FRONTIERS_1.pdf",
            [
                "Hugo Oliveira",
                "Joana Azeredo",
            ],
            marks=pytest.mark.xfail(reason="PDFQuery will not work with this"),
        ),
        (EXAMPLE_MANUSCRIPT / "SOCARXIV_1.pdf", ["Jérémie Voirol"]),
        (EXAMPLE_MANUSCRIPT / "SOCARXIV_2.pdf", ["Giuseppe A. Veltri"]),
        (EXAMPLE_MANUSCRIPT / "SOCARXIV_3.pdf", ["Hyunuk Kim"]),
        (EXAMPLE_MANUSCRIPT / "SOCARXIV_4.pdf", ["Valerio Simoni"]),
    ],
)
def test_authors(pdf_path: str, authors: list[str]):
    """Test that the title obtained via `get_title()` is the same as in the PDF."""
    assert get_authors(pdf_path) == authors
