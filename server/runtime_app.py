"""
Vertex AI Agent Runtime (Reasoning Engine) wrapper module (`server/runtime_app.py`).

IMPORTANT: This class MUST reside in an importable module (not `__main__`) so that
`cloudpickle` serializes it by module reference (`server.runtime_app.CentralMarketReliefAgentRuntime`)
rather than embedding host-specific Python bytecode by value.
"""

from typing import Any, Dict, List, Optional


class CentralMarketReliefAgentRuntime:
    """
    Vertex AI Reasoning Engine / Agent Runtime compliant wrapper.
    Exposes the required callable `query` interface.
    """

    def __init__(self, project_id: Optional[str] = None, dataset_id: str = "a4i_econ"):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self._orchestrator = None

    def set_up(self) -> None:
        """Called inside the remote Vertex AI container during initialization."""
        import os

        if self.project_id:
            os.environ["PROJECT_ID"] = self.project_id
            os.environ["GOOGLE_CLOUD_PROJECT"] = self.project_id
        os.environ["BQ_DATASET"] = self.dataset_id

        from agents.regime_orchestrator_agent import RegimeStressTestOrchestratorAgent
        self._orchestrator = RegimeStressTestOrchestratorAgent()

    def query(
        self,
        prompt: str = "Evaluate Central Market relief grants",
        budget: float = 50000.0,
        preferred_regime: str = "C",
        applicants: Optional[List[Dict[str, Any]]] = None,
        weights: Optional[Dict[str, float]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Required query entrypoint invoked by Vertex AI Reasoning Engine callers.
        """
        if self._orchestrator is None:
            self.set_up()

        return self._orchestrator.run_pipeline(
            applicants=applicants,
            budget=float(budget),
            preferred_regime=str(preferred_regime),
            weights=weights,
        )
