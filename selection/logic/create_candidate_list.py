from polite_pyalex import Works
import pandas as pd

oa_id_list = ["W2741809807", "W1560783210", "W2029057325", "W2160597895"]

def extract_refs(oa_id_list):
    """
    extracts references from manuscript (first layer) and references
    of those (second layer),
    based on OpenAlex ids retrieved from manuscript
    """

    ## first layer
    first_layer = Works().filter(openalex="|".join(oa_id_list)).get()
    first_layer = [ref["referenced_works"] for ref in first_layer]
    first_layer = list(
        {i for lists in first_layer for i in lists}
    )  # list comprehension returning a set

    ## second layer
    second_layer = []
    for ref in range(0, len(first_layer), 25):
        subset = "|".join(first_layer[ref : ref + 25])
        second_layer.append(Works().filter(openalex=subset).get())

    return [entry for lists in second_layer for entry in lists]


refs = extract_refs(oa_id_list)


def create_ref_csv(refs):
    """
    From OpenAlex references, extracts OpenAlex ID, abstracts,
    journal ISSN-L and all authors in correct order.
    Returns a dataframe
    """

    ids = [w["id"].split("/")[-1] for w in refs]
    abstracts = [w["abstract"] for w in refs]
    journal = [
        w["primary_location"]["source"]["issn_l"]
        for w in refs
        if w["primary_location"]["source"]
    ]
    authorships = [w["authorships"] for w in refs]
    authors = []
    for papers in authorships:
        current_paper = [author["author"]["display_name"] for author in papers]
        authors.append(current_paper)

    return pd.DataFrame(
        list(zip(ids, journal, authors, abstracts)),
        columns=["oa_id", "journal_issnl", "authors", "abstracts"],
    )


ref_csv = create_ref_csv(refs)
