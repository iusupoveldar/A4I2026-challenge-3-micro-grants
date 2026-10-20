"""
Google ADK Root Agent Entrypoint (`agent/agent.py`) for `adk web` and CLI execution.
"""

from __future__ import annotations

from agents.regime_orchestrator_agent import (
    RegimeStressTestOrchestratorAgent,
    create_orchestrator_adk_pipeline,
)

try:
    root_agent = create_orchestrator_adk_pipeline()
except Exception:
    # Fallback deterministic orchestrator if google-adk is not installed in the active virtualenv
    root_agent = RegimeStressTestOrchestratorAgent()
