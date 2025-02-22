import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator
from google.cloud import storage
from datetime import datetime, timedelta

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")
dataset_url_prefix = "https://d37ci6vzurychx.cloudfront.net/trip-data/"
path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")



def upload_to_gcs(bucket, object_name, local_file):
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB


    client = storage.Client()
    bucket = client.bucket(bucket)

    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)

def download_taxi_data(taxi_type, year, month, **kwargs):
    dataset_file = f"{taxi_type}_tripdata_{year}-{month:02d}.parquet"
    url = dataset_url_prefix + dataset_file
    local_path = os.path.join(path_to_local_home, dataset_file)
    os.system(f"curl -sSL {url} -o {local_path}")
    return local_path

############################################ DAG ################################################

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="data_ingestion_gcs",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31),
    schedule_interval="@monthly",
    catchup=True,
) as dag:

    for taxi_type in ["green", "yellow"]:
        for year in range(2024, 2025):
            for month in range(1, 13):
                download_dataset_task = PythonOperator(
                    task_id=f"download_{taxi_type}_data_{year}_{month:02d}",
                    python_callable=download_taxi_data,
                    op_kwargs={"taxi_type": taxi_type, "year": year, "month": month},
                    provide_context=True,
                )

                upload_to_gcs_task = PythonOperator(
                    task_id=f"upload_{taxi_type}_data_{year}_{month:02d}",
                    python_callable=upload_to_gcs,
                    op_kwargs={
                        "bucket": BUCKET,
                        "object_name": f"raw/{taxi_type}/{year}/{month:02d}/{taxi_type}_tripdata_{year}-{month:02d}.parquet",
                        "local_file": f"{path_to_local_home}/{taxi_type}_tripdata_{year}-{month:02d}.parquet",
                    },
                )

   

    download_dataset_task  >> upload_to_gcs_task 