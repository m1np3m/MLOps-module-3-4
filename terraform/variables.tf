variable "project_id" {
  description = "The project ID to host the cluster in"
  default     = "gcp-playground-406614"
}

variable "region" {
  description = "The region the cluster in"
  default     = "us-central1-f"
}

variable "k8s" {
  description = "GKE for llm RAG"
  default     = "llm-rag"
}
