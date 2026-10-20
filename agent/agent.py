"""
Google ADK Root Agent Entrypoint (`agent/agent.py`) for `adk web` and CLI execution.

Supports selecting any of the 4 named ADK agents via:
  1. `adk web agents` -> Select directly from the dropdown:
     - `Regime_Stress_Test_Orchestrator_Agent` (Full 4-Agent Pipeline + Sub-Agents)
     - `Supply_Provenance_Agent` (B2B Supply Network & 1-Invoice Provenance)
     - `Runway_Sector_Purity_Agent` (Stage 0 Corporate Gate, Survival Lift & Purity)
     - `Spatial_Human_Impact_Agent` (200m Walkshed Critical Mass & Beneficiaries)
  2. `adk web` (from repo root) -> Automatically exposes all 4 named agents in the
     ADK Web UI dropdown and defaults `root_agent` to `Regime_Stress_Test_Orchestrator_Agent`
     (or whichever agent is specified in `ADK_AGENT_NAME`).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# Default to Vertex AI + Qwiklabs project when no Gemini Developer API key is set
if not os.environ.get("GOOGLE_API_KEY"):
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-486b161c6a8e")
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")

os.environ.setdefault("BQ_PROJECT_ID", os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-486b161c6a8e"))
os.environ.setdefault("BQ_DATASET", "a4i_econ")

from agents.regime_orchestrator_agent import (  # noqa: E402
    ADK_AGENTS_CATALOG,
    list_available_agents,
    select_adk_agent,
    select_deterministic_agent,
)


def _register_named_agents_in_adk_loader() -> None:
    """
    Ensures that running `adk web` from the repository root (`.`) also lists and loads
    the 4 named agents inside `agents/<Agent_Name>` in the ADK Web UI selector dropdown.
    """
    try:
        from google.adk.cli.utils.agent_loader import AgentLoader

        if getattr(AgentLoader, "_a4i_named_agents_patched", False):
            return

        orig_list_agents = AgentLoader.list_agents
        orig_perform_load = AgentLoader._perform_load
        orig_determine_lang = AgentLoader._determine_agent_language

        def _patched_list_agents(self: Any) -> list[str]:
            names = list(orig_list_agents(self))
            base_path = Path.cwd() / self.agents_dir
            nested_agents_dir = base_path / "agents"
            if nested_agents_dir.is_dir():
                for sub_name in ADK_AGENTS_CATALOG:
                    if (nested_agents_dir / sub_name / "agent.py").is_file() and sub_name not in names:
                        names.append(sub_name)
            names.sort()
            return names

        def _patched_perform_load(self: Any, agent_name: str) -> Any:
            if agent_name in ADK_AGENTS_CATALOG:
                return select_adk_agent(agent_name)
            return orig_perform_load(self, agent_name)

        def _patched_determine_lang(self: Any, agent_name: str) -> str:
            if agent_name in ADK_AGENTS_CATALOG:
                return "python"
            return orig_determine_lang(self, agent_name)

        AgentLoader.list_agents = _patched_list_agents  # type: ignore[method-assign]
        AgentLoader._perform_load = _patched_perform_load  # type: ignore[method-assign]
        AgentLoader._determine_agent_language = _patched_determine_lang  # type: ignore[method-assign]
        setattr(AgentLoader, "_a4i_named_agents_patched", True)
    except Exception:
        pass


_register_named_agents_in_adk_loader()

ACTIVE_AGENT_NAME = os.environ.get("ADK_AGENT_NAME", "Regime_Stress_Test_Orchestrator_Agent")

try:
    root_agent = select_adk_agent(ACTIVE_AGENT_NAME)
except Exception:
    root_agent = select_deterministic_agent(ACTIVE_AGENT_NAME)

__all__ = [
    "ACTIVE_AGENT_NAME",
    "ADK_AGENTS_CATALOG",
    "list_available_agents",
    "root_agent",
    "select_adk_agent",
    "select_deterministic_agent",
]
