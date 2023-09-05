from time import time

import pandas as pd
from pyalex import Works

# oa_id_list = ["W2741809807", "W1560783210", "W2029057325", "W2160597895"]


def extract_refs(oa_id_list):
    """
    extracts references from manuscript (first layer) and references
    of those (second layer),
    based on OpenAlex ids retrieved from manuscript
    """

    # oa_id_list = temp

    start = time()
    print("Obtaining first layer of references from OpenAlex...")

    first_layer_full = []
    for ref in range(0, len(oa_id_list), 25):
        subset = "|".join(oa_id_list[ref : ref + 25])
        first_layer = Works().filter(openalex=subset).get()
        first_layer = [ref["referenced_works"] for ref in first_layer]
        first_layer = list(
            {i for lists in first_layer for i in lists}
        )  # list comprehension returning a set
        first_layer_full.append(first_layer)
        # print(len(first_layer_full))

    first_layer_full.append(oa_id_list)

    first_layer_full = list(
        {i for lists in first_layer_full for i in lists}
    )  # list comprehension returning a set

    print(f"Done. ({int(time() - start)}s)")

    ## second layer
    start = time()
    print("Obtaining second layer of references from OpenAlex...")
    second_layer = []
    for ref in range(0, len(first_layer_full), 25):
        subset = "|".join(first_layer_full[ref : ref + 25])
        second_layer.append(Works().filter(openalex=subset).get())

    final = [entry for lists in second_layer for entry in lists]

    print(f"Done. ({int(time() - start)}s)")

    return final


# refs = extract_refs(oa_id_list)


def create_ref_csv(refs):
    """
    From OpenAlex references, extracts OpenAlex ID, abstracts,
    journal ISSN-L and all authors in correct order.
    Returns a dataframe
    """

    start = time()
    print("Creating DataFrame for references...")

    breakpoint()
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

    result = pd.DataFrame(
        list(zip(ids, year, journal, authors, abstracts)),
        columns=["oa_id", "year", "journal_issnl", "authors", "abstracts"],
    )

    print(f"Done. ({int(time() - start)}s)")
    return result
