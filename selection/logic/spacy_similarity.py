# from pdf_extraction.pdf import PDF
import spacy
import pandas as pd
import seaborn as sns

nlp = spacy.load("en_core_web_md")


def load_csv(path):
    return pd.read_csv(path)


abstracts = load_csv(
    "/Users/claralouisa/code/thisspider/reviewerSelection/abstracts_from_W4383896166.csv"
)

# pdf = PDF("article.pdf")
pdf = """ Ethnic boundary crossing takes two different forms that have distinct
triggers,
traits, and potential outcomes: transitory crossing, which is typically short-term,
reversible, and triggered by microcontextual cues, and durable crossing, which is a
longer-lasting, gradual process motivated by macropolitical forces such as social
movements and government policies. This theoretical distinction helps explain the
unexpected growth in the long stigmatized self-identified indigenous population in
Mexico, which has tripled since 2000. Using a demographic projection model, the authors
find that natural demographic processes contributed little to this sudden growth.
Instead, using experimental and census data, they find that transitory crossing into
the indigenous category was activated by phrasing changes to the 2010 census
identification question. The authors theorize that durable crossing is being
simultaneously activated by the growing salience of the indigenous movement and the
Mexican government’s embrace of multiculturalism. These political factors appear to
be shaping the social meaning of indigeneity itself."""


def convert_target_to_nlp(pdf):
    return nlp(
        " ".join([token.text for token in nlp(pdf.abstract) if not token.is_stop])
    )


target_abstract = convert_target_to_nlp(pdf)


def create_df_abstracts_nlp_stop(abstracts):
    abstracts["abstracts_nlp"] = abstracts["abstracts"].apply(
        lambda x: nlp(" ".join([token.text for token in nlp(x) if not token.is_stop]))
        if type(x) == str
        else x
    )
    return abstracts


nlp_abstracts = create_df_abstracts_nlp_stop(abstracts)


def calculate_similarites(abstracts):
    abstracts["spacy_sim"] = abstracts["abstracts_nlp"].apply(
        lambda x: target_abstract.similarity(x) if not type(x) == float else x
    )
    return abstracts


similarities = calculate_similarites(nlp_abstracts)


def plot_similarities(similarities):
    sns.histplot(similarities["spacy_sim"])


plot_similarities(similarities)


def save_similarity_df(similarities_df, path):
    similarities_df.to_csv(index=False, path_or_buf=path)


save_similarity_df(similarities, "/Users/claralouisa/Desktop/spacy_simiarities.csv")
