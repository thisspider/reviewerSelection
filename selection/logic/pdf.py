#!/usr/bin/env python
"""Extract info from a PDF file using PDFQuery and refextract."""
import re
import string
import tempfile
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path
from typing import Callable, Optional

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
    return BBox(
        **(
            pd.DataFrame([el.attrib for el in elements])[["x0", "x1", "y0", "y1"]]
            .astype(float)
            .agg(
                {
                    "x0": "min",
                    "x1": "max",
                    "y0": "min",
                    "y1": "max",
                }
            )
            .to_dict()
        )
    )


def has_text():
    return bool(this.text)  # type: ignore # noqa


def is_centered(page_width: float) -> Callable:
    def func() -> bool:
        offset = (
            page_width
            - float(this.attrib["x1"])  # type: ignore # noqa
            - float(this.attrib["x0"])  # type: ignore # noqa
        )
        return abs(offset) < 10

    return func


@dataclass
class BBox:
    x0: float
    y0: float
    x1: float
    y1: float

    def __str__(self):
        return f"{self.x0},{self.y0},{self.x1},{self.y1}"


class PDF:
    def __init__(self, pdf_path: Path, references: bool = True):
        """Open file using PDFQuery."""

        self._run_pdfquery(pdf_path)

        self.title = ""
        self.authors = []
        self.abstract = ""
        self.references = []
        self.references_slugified = []

        self.frontmatter = self.extract_frontmatter()
        self.has_frontmatter = bool(
            self.frontmatter["title"] and self.frontmatter["authors"]
        )
        page_index = 0
        if self.has_frontmatter:
            page_index = 1
            self.title = self.frontmatter["title"]
            self.authors = self.frontmatter["authors"]

        self.pq = self.pdf.pq(f"LTPage[page_index='{page_index}']")

        # Order of execution is important because we obtain later objects
        # in relationship to the layout of prior ones.
        self.extract_title()
        self.extract_abstract()
        self.extract_authors()
        if references:
            self.extract_references()

    def __str__(self):
        return f"PDF: {self.authors} {self.title}"

    def __repr__(self):
        return f"PDF({self.pdf_path}, references={bool(self.references)})"

    def __dict__(self):
        return {
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "references": self.references,
        }

    def _run_pdfquery(self, pdf_path: Path) -> None:
        self.pdf_path = pdf_path

        temp_dir = tempfile.gettempdir()

        # Workaround for https://github.com/jcushman/pdfquery/issues/74
        if not temp_dir.endswith("/"):
            temp_dir += "/"

        self.pdf = pdfquery.PDFQuery(
            str(pdf_path),
            parse_tree_cacher=FileCache(temp_dir),
            round_digits=1,
        )

        # Only extract first two pages by default for faster processing.
        pages = [0, 1]

        self.pdf.load(*pages)
        self.page_width, self.page_height = self.pdf.get_page(0).mediabox[2:]

    def extract_frontmatter(self):
        def next_column(match):
            return match.parents("LTRect").next().children().text()

        return self.pdf.extract(
            [
                ("with_parent", 'LTPage[page_index="0"]'),
                ("title", 'LTTextLineHorizontal:contains("Title")', next_column),
                ("authors", 'LTTextLineHorizontal:contains("Authors")', next_column),
            ]
        )

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

    def get_text_from_bbox(self, bbox: BBox) -> Optional[str]:
        if not bbox:
            return
        return clean(
            "".join(
                e.text for e in self.pq.find(f":in_bbox('{bbox}')").filter(has_text)
            )
        )

    def extract_title(self, max_length: int = 100) -> None:
        self.title_bbox = self.get_title_bbox_for_biggest_elements()

        if not self.has_frontmatter:
            self.title = self.get_text_from_bbox(self.title_bbox)

            if not self.title or len(self.title) > 100:
                self.title_bbox = self.get_title_bbox_by_distance()
                self.title = self.get_text_from_bbox(self.title_bbox)

    def get_title_bbox_for_biggest_elements(self):
        elements = self.pq.find("LTTextLineHorizontal,LTTextBoxHorizontal").filter(
            has_text
        )
        font_sizes = list({int(float(e.attrib["height"])) for e in elements})

        if len(font_sizes) == 1:
            return

        def biggest_font():
            height = int(float(this.get("height")))  # type: ignore # noqa
            return height == font_sizes[-1]

        title_elems = elements.filter(biggest_font)
        return bbox(title_elems)

    def get_title_bbox_by_distance(self) -> Optional[BBox]:
        upper_third = f"0,{self.page_height * 2/3},{self.page_width},{self.page_height}"
        elements = (
            self.pq(f":in_bbox('{upper_third}')")
            .filter(has_text)
            .filter(is_centered(self.page_width))
        )
        if not elements:
            return

        title_elements = []
        for el_1, el_2 in pairwise(elements):
            # TODO: User upper and lower bound.
            y0_el_1 = float(el_1.attrib["y0"])
            y1_el_2 = float(el_2.attrib["y1"])
            distance = round(y0_el_1 - y1_el_2, 1)
            if distance < min(
                [float(el_1.attrib["height"]), float(el_2.attrib["height"])]
            ):
                title_elements.append(el_1)
                title_elements.append(el_2)
            else:
                break

        if title_elements:
            return bbox(title_elements)
        else:
            return bbox(elements[:1])

    def extract_abstract(self):
        self.extract_abstract_by_cue_element()
        if not self.abstract:
            self.extract_abstract_by_line_spacing()

    def extract_abstract_by_cue_element(self):
        # pp [(r[0], r[1].text[:15], r[2].text[:15]) for r in results]

        try:
            cue_elem = self.pq.find(":contains('bstract')").filter(has_text)[0]
        except IndexError:
            return

        y1_abstr = cue_elem.attrib["y1"]
        query = f":in_bbox('0,0,{self.page_width},{y1_abstr}')"
        elements = self.pq(query).filter(has_text)

        results = []
        for el_1, el_2 in zip(elements, elements[1:]):
            y0_el_1 = float(el_1.attrib["y0"])
            y1_el_2 = float(el_2.attrib["y1"])
            # We need to round to a rough value because layouts are not always
            # perfect.
            distance = round(y0_el_1 - y1_el_2, 0)
            results.append((distance, el_1, el_2))

        abstract_elements = []
        for a, b in pairwise(results):
            if a[0] == b[0]:
                abstract_elements.append(a[1])
            elif abstract_elements:
                abstract_elements.append(a[2])
                break

        self.abstract_bbox = bbox(abstract_elements)
        self.abstract = clean(
            "".join([re.sub(r"- $", "", e.text) for e in abstract_elements])
        )

    def extract_abstract_by_indentation(self):
        """Assume abstract is indented differently than the rest of the page."""
        ...

    def extract_abstract_by_line_spacing(self, tolerance: int = 2):
        """Assume text with equidistant line spacing after title is the abstract.

        ``tolerance`` defines the difference whithin elements are still
        considered having the same distance.
        """

        y0_title = self.title_bbox.y0
        query = f":in_bbox('0,0,{self.page_width},{y0_title}')"
        elements = self.pq(query).filter(has_text)

        results = []
        for el_1, el_2 in pairwise(elements):
            # Use upper bound of higher element and lower bound of lower element
            # to take their height into account. Oftentimes inconsistent line
            # *spacing* is compensated by different line *heights* to create
            # a symmetrical layout.
            el_1_y1 = float(el_1.get("y1"))  # Upper bound.
            el_2_y0 = float(el_2.get("y0"))  # Lower bound.
            distance = round(el_1_y1 - el_2_y0, 0)
            results.append((distance, el_1, el_2))

        groups = [[]]
        for a, b in pairwise(results):
            if abs(a[0] - b[0]) <= tolerance:
                groups[-1].append(a[1])
            elif groups[-1]:
                groups[-1].append(a[2])
                groups.append([])

        abstract_elements = max(groups, key=len)

        self.abstract_bbox = bbox(abstract_elements)
        self.abstract = clean(
            "".join([re.sub(r"- $", "", e.text) for e in abstract_elements])
        )

    def extract_authors(self) -> list[str]:
        """Get authors from a PDFs document head.

        We assume that the authors are always listed below the title.
        We also assume that there will be a minimum spacing of `SPACING`
        between layout groups (i.e. title, authors and abstract/content).
        """

        assert self.abstract_bbox

        def from_metadata():
            authors = [self.pdf.tree.attrib.get("Author", "")]
            if not authors:
                authors = [self.pdf.tree.attrib.get("author", "")]
            return authors

        x1, y1 = self.page_width, self.title_bbox.y0
        x0, y0 = 0, self.abstract_bbox.y1

        elements = self.pdf.pq(f":in_bbox('{x0},{y0},{x1},{y1}')").filter(has_text)

        # We don't expect author names to contain digits or the word 'abstract'.
        elements = [
            e
            for e in elements
            if not re.search(r"\d|(abstract)", e.text, re.IGNORECASE)
        ]

        if elements:
            self.authors_bbox = bbox(elements)
            self.authors = [clean(el.text) for el in elements]
        else:
            self.authors = from_metadata()

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
