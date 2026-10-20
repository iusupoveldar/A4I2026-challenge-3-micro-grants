#!/usr/bin/env bash
# ==============================================================================
# Google Cloud Deployment Script (`deploy_cloud_run.sh`)
# ==============================================================================
# Supports:
#   Option A: `adk deploy cloud_run` (ADK CLI native Cloud Run deployment)
#   Option B: `gcloud run deploy` from source with `--min-instances=1` (prevents
#             cold starts during live multi-hop GQL graph traversal demos)
#   Option C: `adk deploy agent_engine` (Vertex AI Agent Engine / Agent Runtime)
# ==============================================================================
set -euo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-qwiklabs-gcp-04-486b161c6a8e}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-central-market-micro-grant-adk}"
BQ_DATASET="${BQ_DATASET:-a4i_econ}"
DEPLOY_TARGET="${1:-cloud_run}"

echo "=================================================================="
echo " Deploying Central Market Micro-Grant ADK to Google Cloud"
echo " Project : ${PROJECT_ID}"
echo " Region  : ${REGION}"
echo " Dataset : ${PROJECT_ID}.${BQ_DATASET} (Graph: LocalEconomy)"
echo " Target  : ${DEPLOY_TARGET}"
echo "=================================================================="

gcloud config set project "${PROJECT_ID}"

if [[ "${DEPLOY_TARGET}" == "adk_cli" ]]; then
  # Option A: Native ADK CLI Cloud Run deploy
  adk deploy cloud_run \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --service_name="${SERVICE_NAME}" \
    --with_ui \
    agent
elif [[ "${DEPLOY_TARGET}" == "agent_engine" ]]; then
  # Option C: Vertex AI Agent Engine (Agent Runtime)
  STAGING_BUCKET="${STAGING_BUCKET:-gs://${PROJECT_ID}-adk-staging}"
  adk deploy agent_engine \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --staging_bucket="${STAGING_BUCKET}" \
    --display_name="${SERVICE_NAME}" \
    agent
else
  # Option B (Default & Recommended by README): gcloud run deploy with --min-instances=1
  gcloud run deploy "${SERVICE_NAME}" \
    --source . \
    --project "${PROJECT_ID}" \
    --region "${REGION}" \
    --allow-unauthenticated \
    --min-instances=1 \
    --memory=2Gi \
    --cpu=2 \
    --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},BQ_PROJECT_ID=${PROJECT_ID},BQ_DATASET=${BQ_DATASET},BIGQUERY_MCP_MODE=auto"
fi
