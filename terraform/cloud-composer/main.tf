
# Enable API Services
resource "google_project_service" "cloud-composer" {
  project                    = var.project_id
  service                    = "composer.googleapis.com"
  disable_dependent_services = true
}

resource "google_project_service" "iam" {
  project                    = var.project_id
  service                    = "iam.googleapis.com"
  disable_dependent_services = true
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

