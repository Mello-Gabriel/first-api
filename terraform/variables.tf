variable "gcp_project_id" {
  description = "O ID do seu projeto no Google Cloud."
  type        = string
}

variable "gcp_region" {
  description = "A região onde os recursos serão criados."
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "O nome do serviço no Cloud Run."
  type        = string
  default     = "first-api"
}

variable "repository_id" {
  description = "O ID do repositório no Artifact Registry."
  type        = string
  default     = "first-api-repo"
}