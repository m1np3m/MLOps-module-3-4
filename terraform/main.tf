terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.51.0"
    }
  }
}

provider "google" {
  credentials = file("./credentials/gcp-playground-406614-c59ac672a01a.json")

  project = "	gcp-playground-406614"
  region  = "us-central1"
  zone    = "us-central1-c"
}

