import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

app = FastAPI(
    title="Central Market Small Business Relief API Gateway",
    description="Cloud Run Frontend & Gateway routing to Vertex AI Agent Runtime"
)

# Optional remote Agent Runtime resource name or reasoning engine ID
AGENT_RUNTIME_RESOURCE = os.environ.get("AGENT_RUNTIME_RESOURCE") or os.environ.get("AGENT_RUNTIME_ID")
PROJECT_ID = os.environ.get("PROJECT_ID") or os.environ.get("GOOGLE_CLOUD_PROJECT", "local")
REGION = os.environ.get("REGION", "us-central1")

class AgentRunRequest(BaseModel):
    prompt: Optional[str] = "Evaluate Central Market relief grants under budget constraints"
    budget: float = 50000.0
    preferred_regime: str = "C"
    weights: Optional[Dict[str, float]] = None
    applicants: Optional[List[Dict[str, Any]]] = None

@app.get("/healthz")
def healthz():
    return {
        "status": "healthy",
        "service": "central-market-relief-gateway",
        "corridor": "central-market",
        "project": PROJECT_ID,
        "backend": "agent_runtime" if AGENT_RUNTIME_RESOURCE else "local_orchestrator"
    }

@app.post("/api/agent/run")
def run_agent(req: AgentRunRequest):
    """
    Main Gateway Endpoint:
    1. If AGENT_RUNTIME_RESOURCE is configured, forwards query to Google Agent Runtime.
    2. Otherwise, executes the multi-agent orchestrator in-process.
    """
    if AGENT_RUNTIME_RESOURCE:
        try:
            import vertexai
            from vertexai.preview import reasoning_engines
            vertexai.init(project=PROJECT_ID, location=REGION)
            remote_agent = reasoning_engines.ReasoningEngine(AGENT_RUNTIME_RESOURCE)
            response = remote_agent.query(
                prompt=req.prompt,
                budget=req.budget,
                preferred_regime=req.preferred_regime,
                weights=req.weights
            )
            return {"success": True, "source": "agent_runtime", "data": response}
        except Exception as e:
            # Fall back to local orchestrator if remote agent call fails
            print(f"[Warning] Agent Runtime query failed, falling back to local: {e}")

    # Local Multi-Agent Orchestrator execution
    try:
        from agents.regime_orchestrator_agent import RegimeStressTestOrchestratorAgent
        orchestrator = RegimeStressTestOrchestratorAgent()
        result = orchestrator.run_pipeline(
            applicants=req.applicants,
            budget=req.budget,
            preferred_regime=req.preferred_regime,
            weights=req.weights
        )
        return {"success": True, "source": "local_orchestrator", "data": result}
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Orchestrator pipeline exception during execution."
        }

@app.get("/api/corridor/applicants")
def get_corridor_applicants(mode: str = "canonical"):
    """
    Returns the loaded applicant pool for Central Market.
    """
    try:
        from tools.bigquery_connector import load_corridor_applicants
        applicants, source = load_corridor_applicants(
            mode=mode,
            project_id=PROJECT_ID if PROJECT_ID != "local" else None
        )
        return {
            "success": True,
            "source": str(source),
            "count": len(applicants),
            "applicants": applicants
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Mount static frontend from ADK/ directory
static_dir = BASE_DIR / "ADK"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
