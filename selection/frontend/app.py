import json

import pandas as pd
import requests
import streamlit as st

# PDF input
uploaded_file = st.file_uploader("Choose your .pdf file", type="pdf")


# URL
url = "http://localhost:8000/select"

files = {"uploaded_pdf": uploaded_file.getvalue()}

###Can be deleted
st.write(uploaded_file)


# API request
res = requests.get(url=url, files=files)

print("Done")
print(res)
print(type(res))
###Output has to be changed
# st.dataframe(res)
potential_reviewers_dict = json.loads(res.json())
potential_reviewers_df = pd.DataFrame.from_dict(potential_reviewers_dict)

potential_reviewers_df["top_match"] = potential_reviewers_df["top_match"].apply(
    lambda x: x[0]
)
potential_reviewers_df["second_match"] = potential_reviewers_df["second_match"].apply(
    lambda x: x[0]
)
potential_reviewers_df["third_match"] = potential_reviewers_df["third_match"].apply(
    lambda x: x[0]
)


st.dataframe(potential_reviewers_df)
