import spacy

model_name = "en_core_web_md"
if not spacy.util.is_package(model_name):
    print(f"Downloading {model_name} for Spacy...")
    spacy.cli.download(model_name)

nlp = spacy.load("en_core_web_md")


def calculate_spacy_similarity(target_pdf_abstract, candidate_df):
    abstracts = candidate_df[candidate_df["abstracts"].notnull()]

    target_abstract = nlp(
        " ".join(
            [token.text for token in nlp(target_pdf_abstract) if not token.is_stop]
        )
    )

    abstracts["abstracts_nlp"] = abstracts["abstracts"].apply(
        lambda x: nlp(" ".join([token.text for token in nlp(x) if not token.is_stop]))
        if isinstance(x, str)
        else x
    )

    abstracts["spacy_sim"] = abstracts["abstracts_nlp"].apply(
        lambda x: target_abstract.similarity(x) if not isinstance(x, float) else x
    )

    abstracts.sort_values("spacy_sim", inplace=True, ascending=False)

    return abstracts
