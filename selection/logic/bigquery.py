import os
from pathlib import Path

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

GCP_PROJECT = os.getenv("GCP_PROJECT")
GCP_SERVICE_ACCOUNT_JSON = os.getenv(
    "GCP_SERVICE_ACCOUNT_JSON",
    str((Path(__file__).parents[2] / ".gcp_service_account.json").resolve()),
)


def get_client() -> bigquery.Client:
    credentials = service_account.Credentials.from_service_account_file(
        GCP_SERVICE_ACCOUNT_JSON,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    return bigquery.Client(
        credentials=credentials,
        project=credentials.project_id,
    )


def save_data_to_bq(data: pd.DataFrame, gcp_project: str, bq_dataset: str, table: str):
    """
    - Save the DataFrame to BigQuery
    - Empty the table beforehand
    """
    full_table_name = f"{gcp_project}.{bq_dataset}.{table}"

    client = bigquery.Client()

    # Set write_mode to truncate -> delete old data before loading the data
    write_mode = "WRITE_TRUNCATE"

    job_config = bigquery.LoadJobConfig(write_disposition=write_mode)

    job = client.load_table_from_dataframe(data, full_table_name, job_config=job_config)

    result = job.result()  # Noqa


def load_data_from_bigquery(
    path: Path,
    query: str = "SELECT * FROM united-park-392410.all_works.sociology",
) -> pd.DataFrame:
    """
    Retrieve `query` data from BigQuery and save it to `path`.
    """
    if path.exists():
        df = pd.read_csv(path)
    else:
        query_job = get_client().query(query)
        result = query_job.result()
        df = result.to_dataframe()

        df.to_csv(path)

    return df


if __name__ == "__main__":
    data = pd.read_csv("raw_data/all_sociology_works_morecols.csv")
    save_data_to_bq(
        data=data, gcp_project=GCP_PROJECT, bq_dataset="all_works", table="sociology"
    )
    path = (
        Path(__file__).parents[2]
        / "work_data"
        / "final_all_works_sociology_from_bq.csv"
    )
    data = load_data_from_bigquery(
        path=path,
    )
    print(data)
