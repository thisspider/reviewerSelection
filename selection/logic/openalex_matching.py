from datetime import datetime

import pandas as pd
from rapidfuzz import fuzz, process
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

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


def save_tfidf_model(all_works_sociology: pd.DataFrame, n_grams=(1, 1)) -> pd.DataFrame:
    """
    - Train the tfidf_model on the whole sociology works dataframe.
    - Save the tfidf_model to google
    """
    all_works_sociology["abstracts"] = all_works_sociology["abstracts"].map(
        lambda x: x if type(x) == str else "No abstract"
    )
    tfidf_model = TfidfVectorizer(use_idf=True, ngram_range=n_grams)
    tfidf_model.fit(all_works_sociology["abstracts"])

    filename = "finalized_tfidf_model.sav"
    pickle.dump(tfidf_model, open(filename, "wb"))


def load_tfidf_cosine_match(
    all_works_df: pd.DataFrame, pdf_abstract: str, tfidf_pickel_filename: str
):
    """
    - load tfidf_model trained on all_works_sociology
    - transform pdf_abstract and all_works_sociology['abstracts'] with loaded model
    - use cosine_similarity on vectorized abstracts of pdf and dataframe
    - return dataframe with added cosine_similarity
    """
    all_works_df["abstracts"] = all_works_df["abstracts"].map(
        lambda x: x if type(x) == str else "No abstract"
    )
    loaded_model = pickle.load(open(tfidf_pickel_filename, "rb"))
    print(loaded_model)
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


if __name__ == "__main__":
    final_all_works_sociology_data = pd.read_csv(
        "work_data/final_all_works_sociology_from_bq.csv"
    )
    save_tfidf_model(final_all_works_sociology_data)
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
    # test_pdf_abstract = PDF("work_data/test.pdf").abstract
    print("Got test_pdf_abstract!")
    end_df = load_tfidf_cosine_match(
        final_all_works_sociology_data, test_pdf_abstract, "finalized_tfidf_model.sav"
    )
    end_df.to_csv("test_pdf_tfidf_all_works.csv")
