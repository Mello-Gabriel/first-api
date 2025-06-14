# Habilita as APIs necessárias para o Artifact Registry e Cloud Run
resource "google_project_service" "artifactregistry" {
  service = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloudrun" {
  service = "run.googleapis.com"
  disable_on_destroy = false
}

# Cria um repositório no Artifact Registry para armazenar as imagens Docker
resource "google_artifact_registry_repository" "repository" {
  location      = var.gcp_region
  repository_id = var.repository_id
  description   = "Repositório Docker para a first-api"
  format        = "DOCKER"
  depends_on = [google_project_service.artifactregistry]
}

# Cria o serviço no Cloud Run
resource "google_cloud_run_v2_service" "default" {
  name     = var.service_name
  location = var.gcp_region
  
  template {
    containers {
      image = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${google_artifact_registry_repository.repository.repository_id}/${var.service_name}:latest"
    }
  }

  depends_on = [google_project_service.cloudrun]
}

# Permite que o serviço do Cloud Run seja invocado publicamente
resource "google_cloud_run_v2_service_iam_member" "noauth" {
  project  = google_cloud_run_v2_service.default.project
  location = google_cloud_run_v2_service.default.location
  name     = google_cloud_run_v2_service.default.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Saída para exibir a URL do serviço após o deploy
output "service_url" {
  value = google_cloud_run_v2_service.default.uri
}