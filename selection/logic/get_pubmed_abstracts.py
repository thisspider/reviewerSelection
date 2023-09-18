import os
import requests
import xml.etree.ElementTree as ET
import pandas as pd


pmids = "19008416,18927361,18787170,18487186,18239126,18239125"
api_key = os.environ.get("NCBI_API_KEY", None)
base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def query_eutils(pmids):
    """Query pubmed API for pmids, returns XML as default.
    For over 200 IDs, the request should be made using the HTTP POST method"""
    params = {
        "api_key": api_key,
        "db": "pubmed",
        "id": pmids,
    }
    return requests.get(base_url, params).text


def text_or_none(field):
    """Return the text of an xml element or empty string if the element is None."""
    return field.text if field is not None else None


def get_title(article):
    """Return article title"""
    return text_or_none(article.find(".//ArticleTitle"))


def get_pubyear(article):
    """Return publication year (in journal)"""
    return text_or_none(article.find(".//PubDate/Year"))


def get_authors(article):
    """Return article authors in format 'LastName, ForeName, Affiliaton'"""
    return [
        ", ".join(
            filter(
                None,
                [
                    text_or_none(author.find("LastName")),
                    text_or_none(author.find("ForeName")),
                    text_or_none(author.find("AffiliationInfo/Affiliation")),
                ],
            )
        )
        for author in article.find(".//AuthorList")
    ]


def get_journal_name(article):
    """Return journal name"""
    return text_or_none(article.find(".//Article/Journal/ISOAbbreviation"))


def get_journal_issn(article):
    """Return journal ISSN"""
    return text_or_none(article.find(".//Article/Journal/ISSN"))


def get_abstract(article):
    """Return article abstract.
    Check: are multiple abstracts possible?"""
    return text_or_none(article.find(".//AbstractText"))


def get_ref_pmids(article):
    """Return pubmed IDs of references"""
    refs = []
    if article.find(".//ReferenceList") is not None:
        for ref in article.find(".//ReferenceList"):
            if ref.find(".//ArticleId") is not None:
                if ref.find(".//ArticleId").attrib["IdType"] == "pubmed":
                    refs.append(ref.find(".//ArticleId").text)
    return refs


def create_ref_df(root):
    """Return dataframe with information on all cited references including abstracts"""

    root = ET.fromstring(query_eutils(pmids))

    return pd.DataFrame(
        {
            "title": [get_title(article) for article in root],
            "year": [get_pubyear(article) for article in root],
            "authors": [get_authors(article) for article in root],
            "journal_name": [get_journal_name(article) for article in root],
            "journal_issn": [get_journal_issn(article) for article in root],
            "abstract": [get_abstract(article) for article in root],
            "references": [get_ref_pmids(article) for article in root],
        }
    )
