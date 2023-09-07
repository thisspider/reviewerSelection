import os

import pandas as pd
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "https://reviewer-selection.streamlit.app")

st.set_page_config(page_title="Reviewer Selection")

finished = False
do_continue = None


@st.cache_data(show_spinner="Processing PDF")
def process_pdf(pdf_file):
    """Take uploaded PDF from the user and store extracted data in session."""
    try:
        response = requests.post(
            url=BACKEND_URL + "/pdf", files={"pdf_file": pdf_file.getvalue()}
        )
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as exc:
        st.exception(exc)


with st.sidebar:
    pdf_file = st.file_uploader("Choose your .pdf file", type="pdf")
    if pdf_file:
        st.session_state.pdf = process_pdf(pdf_file)

        if "pdf" in st.session_state and st.session_state.pdf:
            options = [
                "(All)",
                "bertopic",
                "cosine",
                "fuzzymatch",
                "spacy",
                "tfidf_all",
            ]
            st.write("")
            st.write("")
            model = st.selectbox(
                "Please select the model to use for reviewer selection?",
                options,
                index=2,
            )

            do_continue = st.button(
                "Continue", help="Match references in PDF with OpenAlex works."
            )


if not pdf_file:
    st.title("Reviewer Selection")
    st.write(
        "**This service finds possible peer reviewers for a manuscript "
        "based on similar publications derived from the website "
        "[openalex.org](https://explore.openalex.org/).**"
    )
    st.divider()
    st.write("Start by adding a manuscript PDF in the sidebar.")
else:
    if do_continue:
        with st.spinner(
            text="Matching references from PDF with works from OpenAlex..."
        ):
            response = requests.post(
                BACKEND_URL + "/openalex_references",
                json=st.session_state.pdf_references,
            )
            try:
                response.raise_for_status()
            except Exception:
                st.exception(response.json())
            openalex_works = response.json()
        st.write(
            "Matching references from PDF with works from OpenAlex.  :heavy_check_mark:"
        )

        with st.spinner(text="Generating candidate works..."):
            response = requests.post(
                BACKEND_URL + "/candidate_works", json=openalex_works
            )
            try:
                response.raise_for_status()
            except Exception:
                st.exception(response.json())
            candidate_works = response.json()

        st.write("Generating candidate work done.  :heavy_check_mark:")

        with st.spinner(text="Generating results..."):
            response = requests.post(
                BACKEND_URL + "/reviewers",
                json={
                    "abstract": st.session_state.pdf_abstract,
                    "candidate_works": candidate_works,
                    "model": model,
                },
            )
            try:
                response.raise_for_status()
            except Exception:
                st.exception(response.json())
            st.write("Generating results.  :heavy_check_mark:")
            st.session_state.results = response.json()
            st.dataframe(st.session_state.results)
            finished = True

    if finished:
        st.stop()

    st.markdown("#### Your PDF")
    st.markdown(
        "This is the title, authors and abstract extracted from your PDF. "
        "Please double-check the information below "
        "in order to ensure the model to work correctly. "
        "You can input and/or change the information in each field. "
        "If everything is correct, "
        "please select a model in the sidebar and click **Continue**."
    )

    pdf_title = st.text_input(
        "Title",
        value=st.session_state.pdf.get("title"),
        help="The title we extracted from your PDF",
    )
    pdf_authors = st.text_input(
        "Authors",
        value=", ".join(st.session_state.pdf.get("authors")),
        help="The authors we extracted from your PDF",
    )
    st.session_state.pdf_abstract = st.text_area(
        "Abstract",
        value=st.session_state.pdf.get("abstract"),
        help="The abstract we extracted from your PDF",
    )

    st.session_state.pdf_references = list(
        st.data_editor(
            pd.Series(st.session_state.pdf.get("references"), name="References"),
            use_container_width=True,
        )
    )
