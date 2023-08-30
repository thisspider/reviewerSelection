from fastapi import FastAPI
from selection.interface.main import pdf_matching, candidate_df, select_reviewers

app = FastAPI()

@app.get("/select")
def select(pdf_path: str):
    '''
    Give x recommendations for reviewers for the article in the pdf.
    '''

    #Somehow able to put in file instead of path
    id_list, pdf = pdf_matching(pdf_path)

    candidates_df = candidate_df(id_list)

    reviewers_df = select_reviewers(pdf, candidates_df)

    return reviewers_df
