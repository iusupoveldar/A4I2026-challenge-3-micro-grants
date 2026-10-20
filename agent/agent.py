"""
Google ADK Root Agent Entrypoint (`agent/agent.py`) for `adk web` and CLI execution.
Pre-configured for Vertex AI + BigQuery on `qwiklabs-gcp-04-486b161c6a8e` when no
`GOOGLE_API_KEY` is provided.
"""

from __future__ import annotations

import os

# Default to Vertex AI + Qwiklabs project when no Gemini Developer API key is set
if not os.environ.get("GOOGLE_API_KEY"):
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-486b161c6a8e")
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")

os.environ.setdefault("BQ_PROJECT_ID", os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-486b161c6a8e"))
os.environ.setdefault("BQ_DATASET", "a4i_econ")

from agents.regime_orchestrator_agent import (  # noqa: E402
    RegimeStressTestOrchestratorAgent,
    create_orchestrator_adk_pipeline,
)

try:
    root_agent = create_orchestrator_adk_pipeline()
except Exception:
    # Fallback deterministic orchestrator if google-adk is not installed in the active virtualenv
    root_agent = RegimeStressTestOrchestratorAgent()
