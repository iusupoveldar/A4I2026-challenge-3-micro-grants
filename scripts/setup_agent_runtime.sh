#!/usr/bin/env bash
#
# Step 1: Environment Setup for Google Agent Runtime (Vertex AI)
# Run from repository root in Cloud Shell:
#   bash scripts/setup_agent_runtime.sh
#

set -euo pipefail

REGION="${REGION:-us-central1}"
PROJECT_ID="$(gcloud config get-value project 2>/dev/null || echo "")"

if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "(unset)" ]; then
  echo "Error: No active GCP project configured. Run: gcloud config set project <PROJECT_ID>"
  exit 1
fi

echo "=========================================================="
echo " Setting up Google Agent Runtime for project: $PROJECT_ID"
echo " Region: $REGION"
echo "=========================================================="

echo "[1/3] Enabling required Google Cloud APIs & BigQuery MCP Server..."
gcloud services enable \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  bigquery.googleapis.com \
  --project="$PROJECT_ID"
gcloud beta services mcp enable bigquery.googleapis.com --project="$PROJECT_ID" --quiet >/dev/null 2>&1 || true

echo "[2/3] Creating Cloud Storage Staging Bucket for Agent Runtime artifacts..."
STAGING_BUCKET="gs://${PROJECT_ID}-agent-runtime-staging"
if ! gcloud storage buckets describe "$STAGING_BUCKET" >/dev/null 2>&1; then
  gcloud storage buckets create "$STAGING_BUCKET" --location="$REGION" --project="$PROJECT_ID"
  echo "Created staging bucket: $STAGING_BUCKET"
else
  echo "Staging bucket already exists: $STAGING_BUCKET"
fi

echo "[3/3] Setting IAM bindings for Vertex AI default service agent..."
PROJECT_NUM="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
VERTEX_SA="service-${PROJECT_NUM}@gcp-sa-aiplatform.iam.gserviceaccount.com"

# Grant BigQuery data viewing and job user to Vertex AI agent
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${VERTEX_SA}" \
  --role="roles/bigquery.jobUser" \
  --condition=None --quiet >/dev/null 2>&1 || true

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${VERTEX_SA}" \
  --role="roles/bigquery.dataViewer" \
  --condition=None --quiet >/dev/null 2>&1 || true

echo ""
echo "=========================================================="
echo " Agent Runtime Pre-requisites Ready!"
echo " Staging Bucket : $STAGING_BUCKET"
echo " Vertex SA       : $VERTEX_SA"
echo "=========================================================="
