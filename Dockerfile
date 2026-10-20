# ==============================================================================
# Cloud Run Dockerfile for Central Market Micro-Grant ADK Agent
# ==============================================================================
# Deploys the multi-agent ADK pipeline (`agent/agent.py` + `agents/*` + `tools/*`)
# with BigQuery Property Graph (`a4i_econ.LocalEconomy`) GQL traversal and
# Google-managed BigQuery MCP toolsets.
# ==============================================================================

FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    GOOGLE_GENAI_USE_VERTEXAI=TRUE \
    GOOGLE_CLOUD_PROJECT=qwiklabs-gcp-04-486b161c6a8e \
    GOOGLE_CLOUD_LOCATION=us-central1 \
    BQ_PROJECT_ID=qwiklabs-gcp-04-486b161c6a8e \
    BQ_DATASET=a4i_econ \
    BIGQUERY_MCP_MODE=auto

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# Launch the ADK Web UI + API server on $PORT (8080) for Cloud Run
CMD ["sh", "-c", "adk web . --host 0.0.0.0 --port ${PORT:-8080}"]
