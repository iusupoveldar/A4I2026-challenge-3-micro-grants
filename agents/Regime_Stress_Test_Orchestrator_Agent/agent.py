"""
ADK Entrypoint for `Regime_Stress_Test_Orchestrator_Agent`
(Regime Stress-Test & Orchestrator Agent — Chief Municipal Economist).
"""

from __future__ import annotations

import os

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
    root_agent = RegimeStressTestOrchestratorAgent()
