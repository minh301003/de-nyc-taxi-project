# Project Overview

In this project, I am aiming to practice different tool sets that we have learned as part of Data Talks Clubs Data Engieering Zoomcamp course.

To practice that, the **NYC taxi data**(https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) is selected as *dataset*. Therefore as final output, the project is aiming to create a report of both green and yellow nyc taxi information which is store in the DataWarehouse (Big Query)

In the project includes following subfolders for respective capabilities.

| SubFolder                         | Capabilty                                                                                     |
| ----------------------------------|----------------------------------------------------------                                     |
| [.google](./.google/)             | Expected to store the google service account keys (not pushed to GitHub for security reasons) |
| [.github](./.github/workflows)    | CI/CD with GitHub Actions workflows                      |
| [terraform](./terraform/)         | Infrastructure as Code for creating GCP resources        |
| [aiflow](./airflow/)              | ETL pipeline  with Airflow and Spark                     |


---
## Infrastructure as Code (Terrafrom and Google Cloud)

To setup the required GCP resources, please follow the [IaC README](./terraform/README.md)
At the end of successfully completing the steps, you will be able to see the GCP resources in GCP console including: GSC bucket,BigQuery dataset, CloudComposer, IAM access rights, etc.


## Data Ingestion and Transformation with Airflow and Spark

To initiate ETL pipeline that is responsible with:
    - Ingesting Raw Data to GCS Data Lake
    - Transforming Data with Spark
    - Ingesting Transformed Data to Google Cloud Storage
    - Ingesting Data from GCS to Google BigQuery


