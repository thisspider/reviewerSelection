import json
import os

import pandas as pd
import requests
import streamlit as st

from selection.logic.restricted_reviewer import extract_matches

MODEL = os.getenv("MODEL")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def process_pdf(pdf_file, csv_file=None):
    res = requests.post(
        url=BACKEND_URL + "/select",
        files={"uploaded_pdf": pdf_file.getvalue()},
    )

    st.write()
    potential_reviewers_dict = json.loads(res.json())
    potential_reviewers_df = pd.DataFrame.from_dict(potential_reviewers_dict)

    if MODEL == "fuzzymatch":
        # Apply fixes to make st.dataframe() not choke on our dataframe object.
        potential_reviewers_df["top_match"] = potential_reviewers_df["top_match"].apply(
            lambda x: x[0]
        )
        potential_reviewers_df["second_match"] = potential_reviewers_df[
            "second_match"
        ].apply(lambda x: x[0])
        potential_reviewers_df["third_match"] = potential_reviewers_df[
            "third_match"
        ].apply(lambda x: x[0])
    if csv_file is not None:
        matches = extract_matches(potential_reviewers_df, list(restricted_reviewer_df))

        st.dataframe(pd.DataFrame(matches))
    else:
        st.dataframe(potential_reviewers_df)


csv_file = st.file_uploader("Choose your csv file", type="csv")
pdf_file = st.file_uploader("Choose your .pdf file", type="pdf")


if pdf_file:
    if csv_file:
        restricted_reviewer_df = pd.read_csv(csv_file)

        restricted_reviewer_df["Full Name"] = (
            restricted_reviewer_df["First Name"]
            + " "
            + restricted_reviewer_df["Last Name"]
        )
        restricted_reviewer_df = restricted_reviewer_df["Full Name"]

        with st.spinner(text="Processing files"):
            process_pdf(pdf_file, restricted_reviewer_df)
            st.success("Done")
    else:
        with st.spinner(text="Processing PDF"):
            process_pdf(pdf_file)
            st.success("Done!")
