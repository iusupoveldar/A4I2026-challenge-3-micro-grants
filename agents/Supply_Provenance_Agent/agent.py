"""
ADK Entrypoint for `Supply_Provenance_Agent`
(Supply & Provenance Agent — B2B Network Topology, Root Multipliers & 1-Invoice Gate).
"""

from __future__ import annotations

import os

if not os.environ.get("GOOGLE_API_KEY"):
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-486b161c6a8e")
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")

os.environ.setdefault("BQ_PROJECT_ID", os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-486b161c6a8e"))
os.environ.setdefault("BQ_DATASET", "a4i_econ")

from agents.supply_provenance_agent import (  # noqa: E402
    SupplyProvenanceAgent,
    create_supply_provenance_adk_agent,
)

try:
    root_agent = create_supply_provenance_adk_agent()
except Exception:
    root_agent = SupplyProvenanceAgent()
