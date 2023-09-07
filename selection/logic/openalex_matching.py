import pickle

import pandas as pd
from rapidfuzz import fuzz, process
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from selection.logic import DATA


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


def cosine_match(
    abstract: str, open_alex_works: pd.DataFrame, n_grams=(1, 1), use_idf=True
) -> pd.DataFrame:
    similarities = []
    open_alex_works["abstracts"] = open_alex_works["abstracts"].map(
        lambda x: x if isinstance(x, str) else "No abstract"
    )
    vectorizer_idf = TfidfVectorizer(use_idf=True, ngram_range=n_grams)
    vectors_idf = vectorizer_idf.fit_transform(open_alex_works["abstracts"])
    target_vector_idf = vectorizer_idf.transform([abstract])

    vectorizer = TfidfVectorizer(use_idf=False, ngram_range=n_grams)
    vectors = vectorizer.fit_transform(open_alex_works["abstracts"])
    target_vector = vectorizer.transform([abstract])

    def flatten_to_list(value):
        # Allow JSON serialization of numpy.ndarray
        return value.flatten().flatten().tolist()

    for i in range(len(open_alex_works)):
        similarity = [
            open_alex_works.iloc[i]["id"],
            open_alex_works.iloc[i]["publication_year"],
            open_alex_works.iloc[i]["journal_issnl"],
            open_alex_works.iloc[i]["authors"],
            open_alex_works.iloc[i]["abstracts"],
            flatten_to_list(cosine_similarity(target_vector, vectors[i])),
            flatten_to_list(cosine_similarity(target_vector_idf, vectors_idf[i])),
        ]

        similarities.append(similarity)
    similarities = pd.DataFrame(similarities)
    similarities.columns = [
        "id",
        "year",
        "journal_issnl",
        "authors",
        "abstracts",
        "cos_sim_idf",
        "cos_sim",
    ]
    similarities = similarities.sort_values(by="cos_sim", ascending=False)

    return similarities


TF_IDF_MODEL_PICKLE = DATA / "finalized_tfidf_model.pickle"


def save_tfidf_model(all_works_sociology: pd.DataFrame, n_grams=(1, 1)) -> pd.DataFrame:
    """
    - Train the tfidf_model on the whole sociology works dataframe.
    - Save the tfidf_model to google
    """
    all_works_sociology["abstracts"] = all_works_sociology["abstracts"].map(
        lambda x: x if isinstance(x, str) else "No abstract"
    )
    tfidf_model = TfidfVectorizer(use_idf=True, ngram_range=n_grams)
    tfidf_model.fit(all_works_sociology["abstracts"])

    pickle.dump(tfidf_model, TF_IDF_MODEL_PICKLE.open("wb"))


def load_tfidf_cosine_match(all_works_df: pd.DataFrame, pdf_abstract: str):
    """
    - load tfidf_model trained on all_works_sociology
    - transform pdf_abstract and all_works_sociology['abstracts'] with loaded model
    - use cosine_similarity on vectorized abstracts of pdf and dataframe
    - return dataframe with added cosine_similarity
    """
    all_works_df["abstracts"] = all_works_df["abstracts"].map(
        lambda x: x if isinstance(x, str) else "No abstract"
    )
    loaded_model = pickle.load(TF_IDF_MODEL_PICKLE.open("rb"))
    pdf_abstract_vector = loaded_model.transform([pdf_abstract])
    print(pdf_abstract_vector)
    all_works_abstracts_vectors = loaded_model.transform(all_works_df["abstracts"])
    similarities = []
    for i in range(all_works_abstracts_vectors.shape[0]):
        similarities.append(
            cosine_similarity(pdf_abstract_vector, all_works_abstracts_vectors[i])
        )
    all_works_df["all_works_sociology_tfidf"] = similarities

    return all_works_df
