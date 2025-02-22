import os
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator
from datetime import datetime

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
REGION = "asia-southeast1"
CLUSTER_NAME = "de-nyc-taxi-cluster"
BUCKET = os.environ.get("GCP_GCS_BUCKET")
TRANSFORM_SCRIPT = "gs://de_nyc_taxi_project_data-lake/code/transform_spark_bigquery.py"
REPARTITION_SCRIPT = "gs://de_nyc_taxi_project_data-lake/code/repartition_spark.py"
JAR_FILE = "gs://spark-lib/bigquery/spark-3.5-bigquery-0.42.0.jar"
GCP_SERVICE_ACCOUNT = os.environ.get("GCP_SERVICE_ACCOUNT")
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="data_transform_spark",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31),
    schedule_interval="@yearly",
    catchup=True,
) as dag:

    # gcloud_auth = BashOperator(
    #     task_id="gcloud_auth",
    #     bash_command=f"gcloud auth activate-service-account --key-file={GOOGLE_APPLICATION_CREDENTIALS} --project={PROJECT_ID}",
    # )

    # start_cluster = BashOperator(
    #     task_id="start_cluster",
    #     bash_command=f"gcloud dataproc clusters start {CLUSTER_NAME} --region={REGION} --project={PROJECT_ID}",
    # )


    repartition_job = {
        "reference": {"project_id": PROJECT_ID},
        "placement": {"cluster_name": CLUSTER_NAME},
        "pyspark_job": {
            "main_python_file_uri": REPARTITION_SCRIPT,
            "args": [
                "--input_green", f"gs://{BUCKET}/raw/green/{{{{ execution_date.strftime('%Y') }}}}",
                "--input_yellow", f"gs://{BUCKET}/raw/yellow/{{{{ execution_date.strftime('%Y') }}}}",
                "--output_green", f"gs://{BUCKET}/pq/green/{{{{ execution_date.strftime('%Y') }}}}",
                "--output_yellow", f"gs://{BUCKET}/pq/yellow/{{{{ execution_date.strftime('%Y') }}}}"
            ],
            "jar_file_uris": [JAR_FILE]
        },
    }
    
    transform_job = {
        "reference": {"project_id": PROJECT_ID},
        "placement": {"cluster_name": CLUSTER_NAME},
        "pyspark_job": {
            "main_python_file_uri": TRANSFORM_SCRIPT,
            "args": [
                "--input_green", f"gs://{BUCKET}/pq/green/{{{{ execution_date.strftime('%Y') }}}}/*/*",
                "--input_yellow", f"gs://{BUCKET}/pq/yellow/{{{{ execution_date.strftime('%Y') }}}}/*/*",
                "--output", f"de_nyc_taxi_project_all_data.reports_{{{{ execution_date.strftime('%Y') }}}}"
            ],
            "jar_file_uris": [JAR_FILE]
        },
    }

    submit_repartition_dataproc_job = DataprocSubmitJobOperator(
        task_id="repartition_job",
        job=repartition_job,
        region=REGION,
        project_id=PROJECT_ID,
    )
    submit_transform_dataproc_job = DataprocSubmitJobOperator(
        task_id="transform_job",
        job=transform_job,
        region=REGION,
        project_id=PROJECT_ID,
    )

    # stop_cluster = BashOperator(
    #     task_id="stop_cluster",
    #     bash_command=f"gcloud dataproc clusters stop {CLUSTER_NAME} --region={REGION} --project={PROJECT_ID}",
    # )

    #gcloud_auth >> start_cluster >> submit_dataproc_job >> stop_cluster
    submit_repartition_dataproc_job >> submit_transform_dataproc_job