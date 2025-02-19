locals {
  composer_name = "${var.project_id}-composer-test"
}

variable "project_id" {
  description = "Your GCP Project ID"
  default     = "de-nyc-taxi-project"
  type        = string
}

variable "region" {
  description = "Region for GCP resources. Choose as per your location: https://cloud.google.com/about/locations"
  default     = "asia-southeast1"
  type        = string
}