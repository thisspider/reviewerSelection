from rapidfuzz import process, fuzz
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

"""
    Warning: choices and extracted_references subjected to change
"""
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
        # possible scorers are fuzz.WRatio , fuzz.partial_ratio , fuzz.token_set_ratio
        # fuzz.partial_token_set_ratio , fuzz.token_sort_ratio
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


"""
    Optional: Can fold get_unique_ids into rapidfuzz_match if refactoring is neccessary
    Both return the same Dataframe
"""


def get_unique_ids(matched_df, openalex_works, openalex_id_col_name):
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


def text_similarity(text1, text2):
    # Tokenize and lemmatize the texts
    tokens1 = word_tokenize(text1)
    tokens2 = word_tokenize(text2)
    lemmatizer = WordNetLemmatizer()
    tokens1 = [lemmatizer.lemmatize(token) for token in tokens1]
    tokens2 = [lemmatizer.lemmatize(token) for token in tokens2]

    # Remove stopwords
    stop_words = stopwords.words("english")
    tokens1 = [token for token in tokens1 if token not in stop_words]
    tokens2 = [token for token in tokens2 if token not in stop_words]

    # Create the TF-IDF vectors
    vectorizer = TfidfVectorizer()
    vector1 = vectorizer.fit_transform(tokens1)
    vector2 = vectorizer.transform(tokens2)

    # Calculate the cosine similarity
    similarity = cosine_similarity(vector1, vector2)

    return similarity


def cosine_match(target_ref: str, open_alex_works: list, n_grams=(1, 2), use_idf=False):
    similarities = []
    vectorizer = TfidfVectorizer(use_idf=use_idf, ngram_range=n_grams)
    vectors = vectorizer.fit_transform(open_alex_works["abstracts"])
    target_vector = vectorizer.transform(target_ref["abstracts"])

    for i in range(len(open_alex_works)):
        similarity = [
            open_alex_works.iloc[i]["oa_id"],
            open_alex_works.iloc[i]["abstracts"],
            cosine_similarity(target_vector, vectors[i]),
        ]
        similarities.append(similarity)
    return similarities


def get_cosine_similarity(full_df: list, target_ref: str, use_idf=True):
    open_alex_works = full_df[["work_id", "abstract_content"]]
    similarities = cosine_match(target_ref, open_alex_works, use_idf=use_idf)
    full_df.merge(similarities[[cosine_similarity]], how="inner", on="work_id")

    return full_df
