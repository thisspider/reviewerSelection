# The Reviewer Selection Problem

See the [pitch slides](docs/pitch_2023-08-25_compressed.pdf), or the [design document](https://docs.google.com/document/d/1ocwSxH7IyCKm36r_Uikc48kuuEatFRlw-YKkACBHjuY/edit#heading=h.5gw87w9koxxk) on Google Docs.

## Setup for development

```shell
mkdir $PROJECT_NAME
cd $PROJECT_NAME
pyenv virtualenv $PROJECT_NAME
pip install -r requirements.txt
pre-commit install
cp .env.sample .env
cp .env.yaml.sample .env.yaml
```

Make sure that `pdftotext` is available on your system (it is required by refextract).

-   On Linux (i.e. Debian/Ubuntu) you need the `libmagic1` package.
-   On MacOs, when using Homebrew: `brew install libmagic`.
    When using macports: `port install file`
-   On Windows, run `pip install python-magic-bin`.

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

## Run web interface locally

Run both commands in two different terminal windows simultaneously to start
the [FastAPI](https://fastapi.tiangolo.com) backend and the [Streamlit](https://streamlit.io) frontend.

```shell
make run_fastapi
make run_streamlit
```

## Build and run docker and streamlit locally

```shell
### Open docker desktop
### If you don't have a .env-file:
### Rename the .env.sample to .env
>>> docker build --tag=$GCR_IMAGE:dev .
### Edit the your/path/to/.env
>>> docker run -e PORT=8000 -p 8000:8000 --env-file your/path/to/.env $GCR_IMAGE:dev
### In a different window:
>>> streamlit run selection/frontend/app.py
### Run the given link in your browser
```

## Deploy the API and Streamlit Cloud

The Streamlit frontend is deployed from pushes to the `streamlit` branch
automatically by the Streamlit Cloud service.

Our FastAPI backend that's used by the Streamlit frontend
is deployed by building a Docker image,
pushing it to Google Cloud Compute and running it.

1. Check the evironment variables in `.env`
   (if it doesn't exist, create it from `.env.sample`),
1. Enable the Google Container Registry API for your project in [GCP](https://console.cloud.google.com/flows/enableapi?apiid=containerregistry.googleapis.com),
1. Allow the Docker command to push to a repository
    ```shell
    gcloud auth configure-docker
    ```
1. Run `make deploy`
