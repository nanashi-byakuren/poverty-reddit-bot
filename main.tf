variable "GCP_PROJECT_ID" {}
variable "GCP_SERVICE_ACCOUNT_FILE" {}
variable "GCP_ACCOUNT" {}
variable "SLACK_BOT_TOKEN" {}
variable "SUBSCRIBE_CHANNEL_IDS" {}
variable "GOOGLE_NEWS_CHANNEL_ID" {}

variable "CLIENT_ID" {}
variable "CLIENT_SECRET" {}
variable "USER_AGENT" {}
variable "USERNAME" {}
variable "PASSWORD" {}
variable "SUBREDDIT" {}

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

# https://cloud.google.com/functions/docs/writing/specifying-dependencies-python?hl=ja
resource "null_resource" "pip_install" {
  triggers = {
    always_run = timestamp()
  }
  provisioner "local-exec" {
    command = "pip install -t ./slack_to_reddit/localpackage -r ./slack_to_reddit/requirements.txt"
  }
}

data "archive_file" "slack_to_reddit" {
  depends_on = [ null_resource.pip_install ]
  type = "zip"
  source_dir = "./slack_to_reddit"
  output_path = "./slack_to_reddit.zip"
}

resource "google_storage_bucket_object" "archive" {
  # ソースが変更されたらmd5値が変更され、アップロードのトリガーになる
  # https://qiita.com/nii_yan/items/c03871ec252b12fb238d
  name = "${data.archive_file.slack_to_reddit.output_md5}.zip"
  bucket = google_storage_bucket.bucket.name
  source = data.archive_file.slack_to_reddit.output_path
}

resource "google_cloudfunctions_function" "function" {
  name = "reddit-bot-function"
  description = "Receive slack notification, and convert to reddit link post"
  runtime = "python38"

  available_memory_mb = 128
  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.archive.name
  trigger_http = true
  timeout = 60
  entry_point = "slack_to_reddit"
  environment_variables = {
    # Slack
    SLACK_BOT_TOKEN = var.SLACK_BOT_TOKEN
    SUBSCRIBE_CHANNEL_IDS = var.SUBSCRIBE_CHANNEL_IDS
    GOOGLE_NEWS_CHANNEL_ID = var.GOOGLE_NEWS_CHANNEL_ID
    # Reddit
    CLIENT_ID = var.CLIENT_ID
    CLIENT_SECRET = var.CLIENT_SECRET
    USER_AGENT = var.USER_AGENT
    USERNAME = var.USERNAME
    PASSWORD = var.PASSWORD
    SUBREDDIT = var.SUBREDDIT
  }
}

# IAM entry for a single user to invoke the function
resource "google_cloudfunctions_function_iam_member" "invoker" {
  project = google_cloudfunctions_function.function.project
  region = google_cloudfunctions_function.function.region
  cloud_function = google_cloudfunctions_function.function.name

  role = "roles/cloudfunctions.invoker"
  #member = var.GCP_ACCOUNT
  member = "allUsers"
}