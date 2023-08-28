#!/usr/bin/env python
"""Extract info from a PDF file using PDFQuery and refextract."""
import math
import re
import string
import tempfile
from pathlib import Path

import click
import pandas as pd
import pdfquery
import refextract
from pdfquery.cache import FileCache
from slugify import slugify as slugify_


def clean(value: str):
    """Return value without footnote markers and surrounding whitespace."""
    return value.strip().strip(string.digits)


def bbox(elements: list) -> dict:
    """Return bounding box containing all elements."""
    return (
        pd.DataFrame([el.attrib for el in elements])[["x0", "x1", "y0", "y1"]]
        .astype(float)
        .agg({"x0": "min", "x1": "min", "y0": "max", "y1": "max"})
        .to_dict()
    )


def has_text():
    return bool(this.text)  # type: ignore # noqa


class PDF:
    def __init__(self, pdf_path: Path, references: bool = True):
        """Open file using PDFQuery."""

        self._run_pdfquery(pdf_path)

        self.title = ""
        self.authors = []
        self.abstract = ""
        self.references = []
        self.references_slugified = []

        self.extract_title()
        self.extract_authors()
        self.extract_abstract()
        if references:
            self.extract_references()

    def _run_pdfquery(self, pdf_path: Path) -> None:
        self.pdf_path = pdf_path

        temp_dir = tempfile.gettempdir()

        # Workaround for https://github.com/jcushman/pdfquery/issues/74
        if not temp_dir.endswith("/"):
            temp_dir += "/"

        self.pdf = pdfquery.PDFQuery(
            str(pdf_path), parse_tree_cacher=FileCache(temp_dir)
        )

        # Only extract first page by default for faster processing.
        pages = [0]

        self.pdf.load(*pages)
        self.page_width = self.pdf.get_page(0).mediabox[2]

    def __str__(self):
        return f"PDF: {self.authors} {self.title}"

    def __repr__(self):
        return f"PDF({self.pdf_path}, references={bool(self.references)})"

    def summary(self):
        click.secho("Title: ", bold=True, fg="green", nl=False)
        click.echo(self.title)
        click.secho("Authors: ", bold=True, fg="green", nl=False)
        click.echo(",".join(self.authors))
        click.secho("Abstract: ", bold=True, fg="green", nl=False)
        click.echo(self.abstract)
        if self.references:
            click.secho("References: ", fg="green", bold=True)
            for ref in self.references:
                click.echo(f"* {ref[:70]}")

    def extract_title(self, max_length: int = 100) -> None:
        self.extract_title_from_metadata()
        self.extract_title_from_biggest_elements(max_length)
        self.title = clean(
            max([self.title_from_metadata, self.title_from_biggest_elements], key=len)
        )

    def extract_title_from_metadata(self) -> str:
        title = self.pdf.tree.attrib.get("Title")
        if not title:
            title = self.pdf.tree.attrib.get("title")
        self.title_from_metadata = title or ""

    def extract_title_from_biggest_elements(self, max_length: int):
        text_lines = self.pdf.pq("LTTextLineHorizontal,LTTextBoxHorizontal")
        elems_with_height = [
            (math.floor(float(el.attrib["height"])), el.text or "", el)
            for el in text_lines
        ]

        # Only consider elements up until 'Abstract' appears.
        relevant_elems = []
        for el in elems_with_height:
            if re.search(r"abstract", el[1], re.IGNORECASE):
                break
            relevant_elems.append(el)

        max_height = max([el[0] or 0 for el in relevant_elems if el[1]])

        title_elems = [el for el in relevant_elems if el[0] == max_height]

        self.title_bbox = bbox([el[2] for el in title_elems])
        self.title_from_biggest_elements = clean(
            "".join(el[1] for el in title_elems)[:max_length]
        )

    def extract_authors(self) -> list[str]:
        """Get authors from a PDFs document head.

        We assume that the authors are always listed below the title.
        We also assume that there will be a minimum spacing of `SPACING`
        between layout groups (i.e. title, authors and abstract/content).
        """

        def from_metadata():
            authors = [self.pdf.tree.attrib.get("Author", "")]
            if not authors:
                authors = [self.pdf.tree.attrib.get("author", "")]
            return authors

        authors_from_metadata = from_metadata()
        author_elements = self.get_element_group(y=self.title_bbox["y0"], spacing=36)

        if author_elements:
            self.authors_bbox = bbox(author_elements)
            authors_from_content = [clean(el.text) for el in author_elements]

        self.authors = max([authors_from_metadata, authors_from_content], key=len)

    def extract_abstract(self):
        abstract_elements = self.get_element_group(y=self.authors_bbox["y0"])
        self.abstract = "".join([re.sub(r"- $", "", e.text) for e in abstract_elements])

    def get_element_group(self, y: float, spacing: int = 26) -> list:
        """Return elements that are within a layout group.

        Return elements that have text and that are positioned below `y`
        up until a vertical whitespace of `spacing` occurs.
        """
        group = []
        elements = self.pdf.pq(f":in_bbox('0,0,{self.page_width},{y-spacing}')").filter(
            has_text
        )
        for prev, current in zip(elements, elements[1:]):
            y_current = float(current.attrib["y1"])
            y_prev = float(prev.attrib["y1"])

            diff = y_prev - y_current
            group.append(prev)

            if diff > spacing:
                break

        return group

    def extract_references(self, slugify: bool = False) -> list:
        """Return clenaed list of references using `refextract`."""
        references = refextract.extract_references_from_file(str(self.pdf_path))
        self.references = self._fill_authors(self._join_references(references))
        self.references_slugified = [slugify_(r) for r in self.references]

    def _join_references(self, references: list[dict]) -> list:
        """Join consecutive references if year is missing from the latter line."""
        references_ = references.copy()

        year_pattern = r"[12]\d\d\d"
        for i, ref in enumerate(references_):
            if i > 0 and not re.search(year_pattern, ref["raw_ref"][0]):
                references_[i - 1]["raw_ref"] += ref["raw_ref"]
                del references_[i]

        return [" ".join(ref["raw_ref"]) for ref in references_]

    def _fill_authors(self, references: list) -> list:
        """Take authors from previous entry if authors are omitted with dashes."""

        blank_author_pattern = r"[-–]{2,}"
        authors_pattern = r"(?P<names>.+?)[\s\.]+([12]\d\d\d)"

        references_ = []
        for i, ref in enumerate(references):
            if i > 0:
                try:
                    prev = re.search(authors_pattern, references_[i - 1]).group("names")
                except AttributeError:
                    prev = None

                if re.match(blank_author_pattern, ref):
                    ref = re.sub(blank_author_pattern, prev, ref)
            references_.append(ref)
        return references_


@click.command()
@click.argument("pdf_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--no-references",
    default=False,
    is_flag=True,
    help="Don't retrieve references (much faster)",
)
def main(pdf_file, no_references):
    """
    Extract information from a PDF file using PDFQuery and refextract.
    Supported outputs are: title, authors, abstract, references.
    """
    pdf = PDF(pdf_file, references=not no_references)
    pdf.summary()


if __name__ == "__main__":
    main()
