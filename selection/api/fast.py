from fastapi import FastAPI, UploadFile
from selection.interface.main import pdf_matching, candidate_df, select_reviewers
from tempfile import NamedTemporaryFile

app = FastAPI()

@app.post("/select")
def select(uploaded_pdf: UploadFile):
    '''
    Give x recommendations for reviewers for the article in the pdf.
    '''

    #Save uploaded_pdf
    pdf = uploaded_pdf.file.read()

    #Create temporary file/path
    temp_pdf = NamedTemporaryFile(suffix='.pdf')
    temp_pdf.write(pdf)

    #Run functions
    id_list, pdf = pdf_matching(temp_pdf.name)
    candidates_df = candidate_df(id_list)
    reviewers_df = select_reviewers(pdf, candidates_df)

    #Close temporary file
    temp_pdf.close()

    return reviewers_df

@app.post("/upload_select")
def create_upload_file(file: UploadFile):
    pdf = file.file.read()
    # with open('test.pdf', 'w') as file:
    #     file.write(pdf)

    temp_pdf = NamedTemporaryFile(suffix='.pdf')
    #this will create a file with path:
    #'curr_pdf\<filename>.pdf'
    #Get filename with temp_pdf.name
    temp_pdf.write(pdf)

    return {"filename": temp_pdf.name}

@app.get("/")
def root():
    return {'Hello.'}
