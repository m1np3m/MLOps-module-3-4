terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.51.0"
    }
  }
}

provider "google" {
  credentials = "./credentials/gcp-playground-406614-c59ac672a01a.json"

  project = var.project_id
  region  = var.region
}

// Google Kubernetes Engine
resource "google_container_cluster" "primary" {
  name                     = "${var.k8s}-gke"
  location                 = var.region
  remove_default_node_pool = true
  initial_node_count       = 1
}

resource "google_container_node_pool" "primary_preemptible_nodes" {
  name       = "my-node-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = 1

  node_config {
    preemptible  = true
    machine_type = "n2-standard-2" # 2 CPU and 8 GB RAM
  }
}

