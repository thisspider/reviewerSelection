from enum import Enum
from pathlib import Path

from .pdf import PDF  # noqa

DATA = Path(__file__).parents[2] / "work_data"

OA_WORKS_FILE = DATA / "all_works_sociology_from_bq.csv"


class ModelName(str, Enum):
    """Models for matching references."""

    bertopic = "bertopic"
    cosine = "cosine"
    fuzzymatch = "fuzzymatch"
    spacy = "spacy"
    tfidf_all = "tfidf_all"
    spacy_all = "spacy_all"
