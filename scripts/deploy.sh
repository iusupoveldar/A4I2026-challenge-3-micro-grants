#!/usr/bin/env bash
#
# Deploy Cloud Run Web Gateway fronting the Vertex AI Agent Runtime
# Usage:
#   bash scripts/deploy.sh
#   (or: AGENT_RUNTIME_RESOURCE="projects/.../reasoningEngines/..." bash scripts/deploy.sh)
#

set -euo pipefail

# Ensure we run from repo root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Ensure gcloud is found
if ! command -v gcloud &>/dev/null; then
  if [ -x "/Users/gauravrai/Downloads/google-cloud-sdk/bin/gcloud" ]; then
    export PATH="/Users/gauravrai/Downloads/google-cloud-sdk/bin:$PATH"
  else
    echo "Error: gcloud CLI not found in PATH."
    exit 1
  fi
fi

SERVICE_NAME="central-market-relief"
REGION="${REGION:-us-central1}"
PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || echo "")}"
AGENT_RUNTIME_RESOURCE="${AGENT_RUNTIME_RESOURCE:-}"

if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "(unset)" ]; then
  PROJECT_ID="qwiklabs-gcp-04-486b161c6a8e"
  gcloud config set project "$PROJECT_ID" --quiet
fi

# Auto-detect the latest deployed ReasoningEngine if AGENT_RUNTIME_RESOURCE is not explicitly set
if [ -z "$AGENT_RUNTIME_RESOURCE" ] && [ -f "server/.agent_runtime_resource" ]; then
  AGENT_RUNTIME_RESOURCE="$(cat server/.agent_runtime_resource | tr -d '[:space:]')"
fi

if [ -z "$AGENT_RUNTIME_RESOURCE" ]; then
  echo "[1/4] Auto-discovering deployed Vertex AI Agent Runtime in ${PROJECT_ID} (${REGION})..."
  AGENT_RUNTIME_RESOURCE="$(python3 -c "
import vertexai
from vertexai.preview import reasoning_engines
vertexai.init(project='${PROJECT_ID}', location='${REGION}')
engines = reasoning_engines.ReasoningEngine.list()
if engines:
    print(engines[0].resource_name)
" 2>/dev/null | tail -n 1 || echo "")"
fi

echo "=========================================================="
echo " Deploying Cloud Run Gateway: $SERVICE_NAME ($REGION)"
echo " Project: $PROJECT_ID"
if [ -n "$AGENT_RUNTIME_RESOURCE" ]; then
  echo " Agent Runtime Backend: $AGENT_RUNTIME_RESOURCE"
  echo "$AGENT_RUNTIME_RESOURCE" > server/.agent_runtime_resource
else
  echo " Agent Execution: In-Container Multi-Agent Pipeline (Fallback)"
fi
echo "=========================================================="

echo "[2/4] Ensuring Cloud Run & Cloud Build APIs are enabled..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com \
  bigquery.googleapis.com \
  --project "$PROJECT_ID" --quiet

echo "[3/4] Granting Cloud Run service account access to Vertex AI Agent Runtime & BigQuery..."
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)' 2>/dev/null || echo "")"
if [ -n "$PROJECT_NUMBER" ]; then
  COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
  for ROLE in "roles/aiplatform.user" "roles/bigquery.user" "roles/bigquery.dataViewer"; do
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
      --member="serviceAccount:${COMPUTE_SA}" \
      --role="$ROLE" \
      --condition=None \
      --quiet >/dev/null 2>&1 || true
  done
fi

# Temporarily stage server/Dockerfile at root for gcloud run deploy --source .
cp server/Dockerfile ./Dockerfile
trap 'rm -f ./Dockerfile' EXIT

echo "[4/4] Building and deploying Cloud Run service..."
gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --allow-unauthenticated \
  --min-instances 1 \
  --memory 2Gi \
  --cpu 1 \
  --set-env-vars "PROJECT_ID=${PROJECT_ID},BQ_DATASET=a4i_econ,REGION=${REGION},AGENT_RUNTIME_RESOURCE=${AGENT_RUNTIME_RESOURCE}"

SERVICE_URL="$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --project "$PROJECT_ID" --format='value(status.url)')"

echo ""
echo "=========================================================="
echo " Cloud Run Gateway Deployed Successfully!"
echo " Live Showcase URL : ${SERVICE_URL}"
echo " Health Check URL  : ${SERVICE_URL}/healthz"
echo " Agent API Endpoint: ${SERVICE_URL}/api/agent/run"
echo "=========================================================="
