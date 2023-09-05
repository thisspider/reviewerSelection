from enum import Enum

from .pdf import PDF  # noqa


class ModelName(str, Enum):
    """Models for matching references."""

    bertopic = "BERTopic"
    cosine = "Cosine-Similarity"
    fuzzymatch = "FuzzyMatching"
    spacy = "Spacy"
    tfidf_all = "Tfidf_all"
