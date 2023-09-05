from enum import Enum
from pathlib import Path

from .pdf import PDF  # noqa

DATA = Path(__file__).parents[2] / "work_data"

OA_WORKS_FILE = DATA / "all_works_sociology_from_bq.csv"


class ModelName(str, Enum):
    """Models for matching references."""

    bertopic = "BERTopic"
    cosine = "Cosine-Similarity"
    fuzzymatch = "FuzzyMatching"
    spacy = "Spacy"
    tfidf_all = "Tfidf_all"
    spacy_all = "Spacy_all"
