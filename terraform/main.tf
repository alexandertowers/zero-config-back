terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

variable "gcp_project_id" {
  description = "GCP Project ID"
}

variable "gcp_region" {
  description = "GCP Region"
  default     = "us-central1"
}

variable "message" {
  description = "Message to display"
  default     = "Hello World"
}

resource "google_cloudfunctions_function" "hello_world" {
  name        = "hello-world-function"
  runtime     = "python39"
  entry_point = "hello_world"
  source_archive_bucket = google_storage_bucket.source_bucket.name
  source_archive_object = google_storage_bucket_object.source_object.name
  trigger_http         = true
  available_memory_mb  = 128
}

resource "google_storage_bucket" "source_bucket" {
  name     = "${var.gcp_project_id}-hello-world-source"
  location = var.gcp_region
}

resource "google_storage_bucket_object" "source_object" {
  name   = "function-source.zip"
  bucket = google_storage_bucket.source_bucket.name
  source = "${path.module}/function-source.zip"
}

output "function_url" {
  value = google_cloudfunctions_function.hello_world.https_trigger_url
}