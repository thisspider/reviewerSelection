import pandas as pd
from google.cloud import bigquery
from pathlib import Path
import os


def load_data_to_bq(data: pd.DataFrame, gcp_project: str, bq_dataset: str, table: str):
    """
    - Save the DataFrame to BigQuery
    - Empty the table beforehand
    """
    full_table_name = f"{gcp_project}.{bq_dataset}.{table}"

    data["index"] = data["Unnamed: 0"]
    data = data.drop(columns=["Unnamed: 0.1", "Unnamed: 0"]).copy()

    # Load data onto full_table_name

    # Construct a BigQuery client object.
    client = bigquery.Client()

    # Set write_mode to truncate -> delete old data before loading the data
    write_mode = "WRITE_TRUNCATE"

    job_config = bigquery.LoadJobConfig(write_disposition=write_mode)

    job = client.load_table_from_dataframe(data, full_table_name, job_config=job_config)

    result = job.result()  # Noqa


def get_data_from_bigquery(gcp_project: str, path: Path, query: str = None):
    """
    Retrieve `query` data from BigQuery
    """
    if query is None:
        query = """
        SELECT *
        FROM united-park-392410.all_works.sociology
        """

    client = bigquery.Client(project=gcp_project)
    query_job = client.query(query)
    result = query_job.result()
    df = result.to_dataframe()

    df.to_csv(path)

    return df


if __name__ == "__main__":
    data = pd.read_csv("work_data/all_works_sociology.csv")
    GCP_PROJECT = os.getenv("GCP_PROJECT")
    load_data_to_bq(
        data=data, gcp_project=GCP_PROJECT, bq_dataset="all_works", table="sociology"
    )
    print("Step1 Done")
    data = get_data_from_bigquery(
        gcp_project=GCP_PROJECT, path="all_works_sociology_from_bg.csv"
    )
    print(data)
