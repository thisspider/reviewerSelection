FROM python:3.10.13-slim

RUN apt-get update
RUN apt-get -y install poppler-utils libmagic1 gcc python3-dev
WORKDIR /prod

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY work_data work_data
COPY selection selection
COPY setup.py setup.py
RUN pip install .

CMD uvicorn selection.api.fast:app --host 0.0.0.0 --port $PORT
