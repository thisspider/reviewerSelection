import pandas as pd


def create_ref_csv(refs):
    """
    From OpenAlex references, extracts OpenAlex ID, abstracts,
    journal ISSN-L and all authors in correct order.
    Returns a dataframe
    """

    ids = [w["id"].split("/")[-1] for w in refs]
    abstracts = [w["abstract"] for w in refs]
    year = [w["publication_year"] for w in refs]

    journal = []
    for w in refs:
        if w["primary_location"]:
            if w["primary_location"]["source"]:
                if w["primary_location"]["source"]["issn_l"]:
                    journal.append(w["primary_location"]["source"]["issn_l"])

    authorships = [w["authorships"] for w in refs]
    authors = []
    for paper in authorships:
        authors_per_paper = []
        for w in paper:
            if w["author"]:
                if w["author"]["display_name"]:
                    authors_per_paper.append(w["author"]["display_name"])
        authors.append(authors_per_paper)

    return pd.DataFrame(
        list(zip(ids, year, journal, authors, abstracts)),
        columns=["oa_id", "year", "journal_issnl", "authors", "abstracts"],
    )
