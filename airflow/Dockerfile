# First-time build can take upto 10 mins.

FROM apache/airflow:2.10.5

ENV AIRFLOW_HOME=/opt/airflow

USER root
RUN apt-get update -qq \
    && apt-get install vim -qqq

RUN apt-get update -qq \
    && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

ENV PATH="${JAVA_HOME}/bin/:${PATH}"

# Ref: https://airflow.apache.org/docs/docker-stack/recipes.html

SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

## GCP SDK files and Variables

ENV GCLOUD_HOME=/home/google-cloud-sdk

ENV PATH="${GCLOUD_HOME}/bin/:${PATH}"

RUN DOWNLOAD_URL="https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz" \
    && TMP_DIR="$(mktemp -d)" \
    && curl -fL "${DOWNLOAD_URL}" --output "${TMP_DIR}/google-cloud-sdk.tar.gz" \
    && mkdir -p "${GCLOUD_HOME}" \
    && tar xzf "${TMP_DIR}/google-cloud-sdk.tar.gz" -C "${GCLOUD_HOME}" --strip-components=1 \
    && "${GCLOUD_HOME}/install.sh" \
       --bash-completion=false \
       --path-update=false \
       --usage-reporting=false \
       --quiet \
    && rm -rf "${TMP_DIR}" \
    && gcloud --version

## Finish GCP SDK files and variables

## Spark files and Variables
ARG SPARK_VERSION=3.5.4
ENV SPARK_HOME=/opt/spark

ENV PATH="${SPARK_HOME}/bin/:${PATH}"

RUN DOWNLOAD_URL="https://dlcdn.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3-scala2.13.tgz" \
    && TMP_DIR="$(mktemp -d)" \
    && curl -fL "${DOWNLOAD_URL}" --output "${TMP_DIR}/spark.tgz" \
    && mkdir -p "${SPARK_HOME}" \
    && tar xzf "${TMP_DIR}/spark.tgz" -C "${SPARK_HOME}" --strip-components=1 \
    && rm -rf "${TMP_DIR}"

## Finish Spark files and Variables

## Start Python packages
COPY requirements.txt .
ENV PYTHONPATH="/usr/local/bin/python"
ENV PYTHONPATH="${SPARK_HOME}/python/:$PYTHONPATH"
ENV PYTHONPATH="${SPARK_HOME}/python/lib/py4j-0.10.9.3-src.zip:$PYTHONPATH"

USER $AIRFLOW_UID
RUN pip install --no-cache-dir -r requirements.txt

USER root

WORKDIR $AIRFLOW_HOME

USER $AIRFLOW_UID