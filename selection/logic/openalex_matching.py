from datetime import datetime

import pandas as pd
from rapidfuzz import fuzz, process
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# WARNING: `choices` and `extracted_references` subjected to change.
choices = ["Atlanta Falcons", "New York Jets", "New York Giants", "Dallas Cowboys"]
extracted_references = ["Cowboys", "Falcons"]


def rapidfuzz_match(
    extracted_references: list, openalex_works: list, scorer=fuzz.WRatio
):
    top_match = []
    second_match = []
    third_match = []
    top_names = []
    top_scores = []
    top_indexes = []
    second_scores = []
    second_indexes = []
    second_names = []
    choices = openalex_works
    for reference in extracted_references:
        # possible scorers are:
        # - fuzz.WRatio
        # - fuzz.partial_ratio
        # - fuzz.token_set_ratio
        # - fuzz.partial_token_set_ratio
        # - fuzz.token_sort_ratio
        top, second, third = process.extract(reference, choices, scorer=scorer, limit=3)
        top_score = top[1]
        top_index = top[2]
        top_name = top[0]
        top_names.append(top_name)
        top_scores.append(top_score)
        top_indexes.append(top_index)
        top_match.append(top)
        second_match.append(second)
        second_score = second[1]
        second_index = second[2]
        second_name = second[0]
        second_names.append(second_name)
        second_scores.append(second_score)
        second_indexes.append(second_index)
        third_match.append(third)
    matched_df = pd.DataFrame(
        list(
            zip(
                extracted_references,
                top_match,
                top_names,
                top_scores,
                top_indexes,
                second_match,
                second_names,
                second_scores,
                second_indexes,
                third_match,
            )
        ),
        columns=[
            "extracted_reference",
            "top_match",
            "top_names",
            "top_scores",
            "top_indexes",
            "second_match",
            "second_names",
            "second_scores",
            "second_indexes",
            "third_match",
        ],
    )
    return matched_df


def get_unique_ids(matched_df, openalex_works, openalex_id_col_name):
    """
    Optional: Can fold get_unique_ids into rapidfuzz_match if refactoring is
    neccessary Both return the same Dataframe
    """
    openalex_ids = []
    for top_match in matched_df["top_match"]:
        index = top_match[2]
        openalex_id = openalex_works[openalex_id_col_name][index]
        openalex_ids.append(openalex_id)
    matched_df["openalex_ids"] = openalex_ids
    return matched_df


test = rapidfuzz_match(
    extracted_references=extracted_references, openalex_works=choices
)
test.head()


def cosine_match(
    abstract: str, open_alex_works: pd.DataFrame, n_grams=(1, 1), use_idf=True
) -> pd.DataFrame:
    similarities = []
    open_alex_works["abstracts"] = open_alex_works["abstracts"].map(
        lambda x: x if type(x) == str else "No abstract"
    )
    vectorizer_idf = TfidfVectorizer(use_idf=True, ngram_range=n_grams)
    vectors_idf = vectorizer_idf.fit_transform(open_alex_works["abstracts"])
    target_vector_idf = vectorizer_idf.transform([abstract])
    vectorizer = TfidfVectorizer(use_idf=False, ngram_range=n_grams)
    vectors = vectorizer.fit_transform(open_alex_works["abstracts"])
    target_vector = vectorizer.transform([abstract])

    for i in range(len(open_alex_works)):
        similarity = [
            open_alex_works.iloc[i]["oa_id"],
            open_alex_works.iloc[i]["year"],
            open_alex_works.iloc[i]["journal_issnl"],
            open_alex_works.iloc[i]["authors"],
            open_alex_works.iloc[i]["abstracts"],
            cosine_similarity(target_vector, vectors[i]),
            cosine_similarity(target_vector_idf, vectors_idf[i]),
        ]

        similarities.append(similarity)
    similarities = pd.DataFrame(similarities)
    similarities.columns = [
        "oa_id",
        "year",
        "journal_issnl",
        "authors",
        "abstracts",
        "cos_sim_idf",
        "cos_sim",
    ]
    similarities = similarities.sort_values(by="cos_sim", ascending=False)

    return similarities


def get_n_years(oa_works: pd.DataFrame, n_years=10):
    """
    oa_works should be the resulting DataFrame outputted by cosine_match
    """
    result = oa_works[oa_works["year"] >= (datetime.now().year - n_years)]
    return result


def get_journals(oa_works: pd.DataFrame, journal_issnl: list[str]):
    """
    oa_works should be the resulting DataFrame outputted by cosine_match
    """
    results = [
        oa_work
        for i, oa_work in oa_works.iterrows()
        if str(oa_work["journal_issnl"]) in journal_issnl
    ]
    return pd.DataFrame(results)
