import os
import subprocess
from pathlib import Path
import pandas as pd

import pytest
from attr import dataclass
from selection.logic import DATA

from selection.logic.openalex_matching import load_tfidf_cosine_match

from .pdf import PDF, bbox

EXAMPLE_MANUSCRIPT = Path(os.getenv("EXAMPLE_MANUSCRIPT_PATH", "."))


def test_python_api():
    """Make sure that the extraction can be run from within Python."""

    pdf_file = EXAMPLE_MANUSCRIPT / "AJS_1_teeger2023.pdf"
    pdf = PDF(pdf_file, references=False)

    assert pdf.title
    assert pdf.abstract
    assert pdf.authors
    assert pdf.references == []
    assert pdf.references_slugified == []


def test_cli_api():
    """Make sure that the extraction can be run from the command line."""
    pdf_file = EXAMPLE_MANUSCRIPT / "AJS_1_teeger2023.pdf"
    script_file = (Path(__file__) / ".." / "pdf.py").resolve()
    res = subprocess.run(
        [script_file, pdf_file, "--no-references"], stdout=subprocess.PIPE
    )
    assert (
        "Title: (Not) Feeling the Past: Boredom as a Racialized Emotion"
        in res.stdout.strip().decode()
    )


@pytest.mark.parametrize(
    "pdf_path, expected_count",
    [
        (
            EXAMPLE_MANUSCRIPT / "AJS_1_teeger2023.pdf",
            (11 + 22 + 21 + 23 + 23 + 23 + 4),
        ),
        (
            EXAMPLE_MANUSCRIPT / "AJS_2_Sugie2023.pdf",
            (22 + 21 + 22 + 20 + 16),
        ),
        (
            EXAMPLE_MANUSCRIPT / "AJS_3_flores2023.pdf",
            (19 + 24 + 24 + 25 + 2),
        ),
    ],
)
def test_reference_count(pdf_path, expected_count):
    assert len(PDF(pdf_path).references) == expected_count


@pytest.mark.parametrize(
    "pdf_path,start, end",
    [
        (
            EXAMPLE_MANUSCRIPT / "AJS_1_teeger2023.pdf",
            "This article centers boredom",
            "and history education.",
        ),
        (
            EXAMPLE_MANUSCRIPT / "AJS_2_Sugie2023.pdf",
            "Punitive policies of welfare",
            "criminal legal system.",
        ),
        (
            EXAMPLE_MANUSCRIPT / "AJS_3_flores2023.pdf",
            "Ethnic boundary crossing",
            "social meaning of indigeneity itself.",
        ),
        (
            EXAMPLE_MANUSCRIPT / "ARXIV_1.pdf",
            "Gender discrimination in the hiring process",
            "team gender composition.",
        ),
        pytest.param(
            EXAMPLE_MANUSCRIPT / "FRONTIERS_1.pdf",
            "Harmful bacteria are microscopic",
            "treat bacterial diseases.",
            marks=pytest.mark.xfail(reason="Breaks pdfQuery due to weird char."),
        ),
        (
            EXAMPLE_MANUSCRIPT / "MANUSCRIPT.pdf",
            "Abstract: This study empirically investigated",
            "males born between 1978-1994.",
        ),
        (
            EXAMPLE_MANUSCRIPT / "SOCARXIV_1.pdf",
            "This article contributes to anthropological",
            "hoping versus expecting.",
        ),
        (
            EXAMPLE_MANUSCRIPT / "SOCARXIV_2.pdf",
            "Cognitive sociology has",
            "heterogeneity in group detection.",
        ),
        (
            EXAMPLE_MANUSCRIPT / "SOCARXIV_3.pdf",
            "Postdoctoral researchers contribute",
            "such as culture and language.",
        ),
        (
            EXAMPLE_MANUSCRIPT / "SOCARXIV_4.pdf",
            "The article focuses on the experiences",
            "and anthropological research.",
        ),
    ],
)
def test_abstract(pdf_path: Path, start: str, end: str):
    abstract = PDF(pdf_path, references=False).abstract
    assert abstract.startswith(start)
    assert abstract.endswith(end)


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
    assert PDF(pdf_path, references=False).title == title


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
    assert PDF(pdf_path, references=False).authors == authors


@pytest.mark.parametrize(
    "pdf_path",
    [
        EXAMPLE_MANUSCRIPT / "SOCARXIV_2.pdf",
    ],
)
def test_layout_groups(pdf_path: str):
    PDF(pdf_path, references=False).get_layout_groups()


def test_bbox():
    @dataclass
    class Element:
        attrib: dict

    elements = [
        Element(attrib={"x0": 127, "y0": 646, "x1": 465, "y1": 663}),
        Element(attrib={"x0": 195, "y0": 609, "x1": 397, "y1": 626}),
    ]
    assert bbox(elements) == {"x0": 127, "y0": 609, "x1": 465, "y1": 663}


def test_idf_model():
    csv_path = DATA / "all_works_sociology_from_bq.csv"
    assert csv_path.exists()
    breakpoint()
    final_all_works_sociology_data = pd.read_csv(csv_path)
    test_pdf_abstract = """
    This article centers boredom as a racialized emotion by analyzing how it can
    come to characterize encounters with histories of racial oppression. Drawing
    on data collected in two racially diverse South African high schools, I
    document how and why students framed the history of apartheid as boring. To
    do so, I capitalize on the comparative interest shown in the Holocaust,
    which they studied the same year. Whereas the Holocaust was told as a
    psychosocial causal narrative, apartheid was presented primarily through
    lists of laws and events. A lack of causal narrative hindered students’
    ability to carry the story into the present and created a sense of
    disengagement. Boredom muted discussions of the ongoing legacies of the past
    and functioned as an emotional defense of the status quo. I discuss the
    implications for literatures on racialized emotions, collective memory, and
    history education
    """

    end_df = load_tfidf_cosine_match(
        final_all_works_sociology_data,
        test_pdf_abstract,
        str(DATA / "finalized_tfidf_model.sav"),
    )
    assert list(end_df.columns) == [
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
        "all_works_sociology_tfidf",
    ]
