import json
import os
import pandas as pd
import requests
import streamlit as st

MODEL = os.getenv("MODEL")


def process_pdf(pdf_file):
    res = requests.get(
        url="http://0.0.0.0:8000/select",
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

    st.dataframe(potential_reviewers_df)


pdf_file = st.file_uploader("Choose your .pdf file", type="pdf")
if pdf_file:
    with st.spinner(text="Processing PDF"):
        process_pdf(pdf_file)
        st.success("Done")
