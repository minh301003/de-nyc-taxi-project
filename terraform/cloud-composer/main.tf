
resource "google_project_service" "composer_api" {
  provider = google
  project = var.project_id
  service = "composer.googleapis.com"
  // Disabling Cloud Composer API might irreversibly break all other
  // environments in your project.
  disable_on_destroy = false
  // this flag is introduced in 5.39.0 version of Terraform. If set to true it will
  //prevent you from disabling composer_api through Terraform if any environment was
  //there in the last 30 days
  //check_if_service_has_usage_on_destroy = true
}

resource "google_service_account" "custom_service_account" {
  provider = google
  account_id   = "custom-service-account"
  display_name = "Composer Worker Service Account"
}

resource "google_project_iam_member" "custom_service_account" {
  provider = google
  project  = var.project_id
  member   = format("serviceAccount:%s", "cloud-composer-worker@de-nyc-taxi-project.iam.gserviceaccount.com")
  // Role for Public IP environments
  role     = "roles/composer.worker"
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

