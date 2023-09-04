from tempfile import NamedTemporaryFile

from fastapi import FastAPI, UploadFile

from selection.interface.main import (
    create_candidates_df,
    get_references_from_pdf,
    select_reviewers,
)

app = FastAPI()


@app.post("/select")
def select(uploaded_pdf: UploadFile):
    """
    Give x recommendations for reviewers for the article in the pdf.
    """
    # Save uploaded_pdf
    pdf = uploaded_pdf.file.read()

    # Create temporary file/path
    temp_pdf = NamedTemporaryFile(suffix=".pdf")
    temp_pdf.write(pdf)

    # Run functions
    openalex_ids, pdf = get_references_from_pdf(temp_pdf.name)
    print("Step1 done")
    candidates_df = create_candidates_df(openalex_ids)
    print("Step2 done")
    reviewers_df = select_reviewers(pdf.abstract, candidates_df)
    print("Step3 done")

    # Close temporary file
    temp_pdf.close()
    print("closed")

    # Turn DataFrame to json string
    json_string = reviewers_df.to_json()
    print("Turned to json")
    print(json_string)

    return json_string


# @app.post("/upload_select")
# def create_upload_file(uploaded_pdf: UploadFile):
#     pdf = uploaded_pdf.file.read()

#     temp_pdf = NamedTemporaryFile(suffix='.pdf')
#     #this will create a file with path:
#     #'<filename>.pdf'
#     #Get path with temp_pdf.name
#     temp_pdf.write(pdf)

#     return {"filename": temp_pdf.name}


@app.get("/")
def root():
    return {"Hello."}
