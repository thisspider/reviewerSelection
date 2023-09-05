import os
import subprocess
from pathlib import Path

import pytest
from attr import dataclass

from .pdf import PDF, bbox

EXAMPLE_MANUSCRIPT = Path(os.getenv("EXAMPLE_MANUSCRIPT_PATH"))


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
