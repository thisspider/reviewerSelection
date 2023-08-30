FROM python:3.10.6-buster

WORKDIR /prod

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY selection selection
COPY setup.py setup.py
RUN pip install .

CMD uvicorn selection.api.fast:app --host 0.0.0.0 --port $PORT
