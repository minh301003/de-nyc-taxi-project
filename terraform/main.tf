terraform {
  required_version = ">= 1.0"
  backend "gcs" {
    bucket = "tf-state-de-nyc-taxi-project"
  }
  required_providers {
    google = {
      source = "hashicorp/google"
    }
  }
}

# Provider google
provider "google" {
  project = var.project_id
  region  = var.region
}



# Enable Required API services for the project
resource "google_project_service" "iamcredentials" {
  project                    = var.project_id
  service                    = "iamcredentials.googleapis.com"
  disable_dependent_services = true
  disable_on_destroy         = false
}


# Data Lake Bucket
resource "google_storage_bucket" "data-lake-bucket" {
  name     = local.data_lake_bucket
  location = var.region

  storage_class               = var.storage_class
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30 // days
    }
  }

  force_destroy = true
}

# Data ware house : DWH
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset
resource "google_bigquery_dataset" "dataset" {
  dataset_id                 = local.bigquery_dataset
  project                    = var.project_id
  location                   = var.region
  delete_contents_on_destroy = true
}

resource "google_project_service" "cloud-composer" {
  count                      = local.cloud_composer_enabled
  project                    = var.project_id
  service                    = "composer.googleapis.com"
  disable_dependent_services = true
  disable_on_destroy         = false
}

# Cloud Composer Environment

resource "google_project_service" "composer_api" {
  provider = google
  project  = var.project_id
  service  = "composer.googleapis.com"
  // Disabling Cloud Composer API might irreversibly break all other
  // environments in your project.
  disable_on_destroy = false
  // this flag is introduced in 5.39.0 version of Terraform. If set to true it will
  //prevent you from disabling composer_api through Terraform if any environment was
  //there in the last 30 days
  //check_if_service_has_usage_on_destroy = true
}

resource "google_service_account" "custom_service_account" {
  provider     = google
  account_id   = "custom-service-account"
  display_name = "Composer Worker Service Account"
}

resource "google_project_iam_member" "custom_service_account" {
  provider = google
  project  = var.project_id
  member   = format("serviceAccount:%s", "cloud-composer-worker@de-nyc-taxi-project.iam.gserviceaccount.com")
  // Role for Public IP environments
  role = "roles/composer.worker"
}

resource "google_service_account_iam_member" "composer_sa_user" {
  service_account_id = "projects/${var.project_id}/serviceAccounts/cloud-composer-worker@de-nyc-taxi-project.iam.gserviceaccount.com"
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:de-nyc-taxi-service-account@de-nyc-taxi-project.iam.gserviceaccount.com"
}

# Cloud Composer Environmet
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/composer_environment
# TODO: google_compute_network, google_compute_subnetwork
resource "google_composer_environment" "composer_environment" {
  name    = local.composer_name
  region  = var.region
  project = var.project_id

  config {

    software_config {
      image_version = "composer-3-airflow-2"
      airflow_config_overrides = {
        core-dags_are_paused_at_creation = "True"
      }
    }
    node_config {
      service_account = "cloud-composer-worker@de-nyc-taxi-project.iam.gserviceaccount.com"
    }
    environment_size = "ENVIRONMENT_SIZE_SMALL"
  }
}


# Dataproc cluster

resource "google_dataproc_cluster" "dataproc_cluster" {
  name   = "dataproc-cluster"
  region = var.region

  cluster_config {
    master_config {
      num_instances = 1
      machine_type  = "n1-standard-4"
      disk_config {
        boot_disk_size_gb = 30
      }
    }

    worker_config {
      num_instances = 1
      machine_type  = "n1-standard-4"
      disk_config {
        boot_disk_size_gb = 30
      }
    }

    software_config {
      image_version = "2.0.35-debian10"
      override_properties = {
        "dataproc:dataproc.allow.zero.workers" = "true"
      }
    }
  }
}

