import streamlit as st
import requests


#PDF input
uploaded_file = st.file_uploader('Choose your .pdf file', type="pdf")


#URL
url = 'http://localhost:8000/upload_select'

files = {
    'file': uploaded_file.getvalue()
}

###Can be deleted
st.write(uploaded_file)


#API request
res = requests.post(url=url, files=files)


###Output has to be changed
if res:
    st.write(res.json())
