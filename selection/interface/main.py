from selection.logic.pdf import PDF
from selection.logic.create_candidate_list import *
from selection.logic.restricted_reviewer import *
# from selection.logic... import *


#1 Link pdf to openalex
# Extraction and matching

#2 Create candidate list

#3 Select reviewers from candidate list


def pdf_matching(path: str):

    # Extract the references out of the pdf
    pdf = PDF(path)
    extracted_references = pdf.references

    # Load the dataframe with all of the relevant works
    def load_data(path):
        return pd.read_csv(path)

    all_works_df = load_data('..../all_works_sociology.csv')

    # Fuzzymatch the works dataframe with the extracted references -> merge
    #merge...

    return merged_list


def candidate_list(id_list):
    curr_df = extract_refs(id_list)

    return curr_df

def select_reviewers():
    pass
