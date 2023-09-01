# The Reviewer Selection Problem

See the [pitch slides](docs/pitch_2023-08-25_compressed.pdf), or the [design document](https://docs.google.com/document/d/1ocwSxH7IyCKm36r_Uikc48kuuEatFRlw-YKkACBHjuY/edit#heading=h.5gw87w9koxxk) on Google Docs.

## Setup for development

```shell
mkdir $PROJECT_NAME
cd $PROJECT_NAME
pyenv virtualenv $PROJECT_NAME
pip install -r requirements.txt
pre-commit install
```

Make sure that `pdftotext` is available on your system (it is required by refextract).

## Extract infos from PDF

The class `pdf_extraction.PDF` will read the following from a given PDF file:

-   title
-   authors
-   abstract
-   references

References are extracted by [refextract](https://github.com/inspirehep/refextract/), the other three are obtained using [PDFQuery](https://github.com/jcushman/pdfquery).
If you want to skip the overhead of `refextract` to get title, author, abstract quickly, add the `--no-references` flag.

In the shell:

```shell
./pdf_extraction/pdf.py PDF_FILE [--no-references]
```

From within Python:

```python
>>> from pdf_extraction.pdf import PDF
>>> pdf = PDF("article.pdf")
>>> pdf.title
"(Not) Feeling the Past: Boredom as a Racialized Emotion"
>>> pdf.authors
["Chana Teeger"]
>>> pdf.abstract
"This article centers boredom as a racialized emotion by analyzing how it can come ..."
```

## Run uvicorn and streamlit locally

```shell
uvicorn selection.api.fast:app --host 0.0.0.0 --reload
# In a different window:
streamlit run selection/frontend/app.py
# Open your browser and upload a PDF file.
```
