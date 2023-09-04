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

```shell
### Enable the Google Container Registry API for your project in GCP.
### https://console.cloud.google.com/flows/enableapi?apiid=containerregistry.googleapis.com&redirect=https://cloud.google.com/### container-registry/docs/quickstart

### Allow the docker command to push a repository
>>> gcloud auth configure-docker
### Build the docker image
>>> docker build -t $GCR_REGION/$GCP_PROJECT/$GCR_IMAGE:prod .
### Push the docker image to your Google Cloud Repository
>>> docker push $GCR_REGION/$GCP_PROJECT/$GCR_IMAGE:prod

### Deploy your container
>>> gcloud run deploy --image $GCR_REGION/$GCP_PROJECT/$GCR_IMAGE:prod --memory $GCR_MEMORY --region $GCP_REGION --env-vars-file .env.yaml

### Create a streamlit app
### 1. Input the given url into selection/frontend/app.py
### 2. Fork the Repository
### 3. Use forked repository to create app

### Voila!
```
