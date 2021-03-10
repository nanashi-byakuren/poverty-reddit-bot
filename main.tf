variable "GCP_PROJECT_ID" {}
variable "GCP_SERVICE_ACCOUNT_FILE" {}
variable "GCP_ACCOUNT" {}

provider "google" {
  credentials = file("~/.gcp/reddit-cred.json")
  project = var.GCP_PROJECT_ID
  region = "asia-northeast1"
}

resource "google_storage_bucket" "bucket" {
  name = "reddit-bot-bucket"
  location = "ASIA-NORTHEAST1"
  force_destroy = true
}

data "archive_file" "query_runner_archive" {
  type = "zip"
  source_dir = "./slack-to-reddit"
  output_path = "./slack-to-reddit.zip"
}

resource "google_storage_bucket_object" "archive" {
  name = "source.zip"
  bucket = google_storage_bucket.bucket.name
  source = "./slack-to-reddit.zip"
}

resource "google_cloudfunctions_function" "function" {
  name = "reddit-bot-function"
  description = "My function"
  runtime = "python38"

  available_memory_mb = 128
  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.archive.name
  trigger_http = true
  timeout = 60
  entry_point = "hello_world"
  //  labels = {
  //    my-label = "my-label-value"
  //  }
  //  environment_variables = {
  //    MY_ENV_VAR = "my-env-var-value"
  //  }
}

# IAM entry for a single user to invoke the function
resource "google_cloudfunctions_function_iam_member" "invoker" {
  project = google_cloudfunctions_function.function.project
  region = google_cloudfunctions_function.function.region
  cloud_function = google_cloudfunctions_function.function.name

  role = "roles/cloudfunctions.invoker"
  //member = "user:myFunctionInvoker@example.com"
  member = var.GCP_ACCOUNT
}