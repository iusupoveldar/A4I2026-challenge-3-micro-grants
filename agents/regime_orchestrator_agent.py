"""
Regime Stress-Test & Orchestrator Agent (`agents/regime_orchestrator_agent.py`).

Coordinates the 3 specialized evaluation agents:
  1. Supply & Provenance Agent (`supply_provenance_agent`)
  2. Runway, Sector & Purity Agent (`runway_sector_purity_agent`)
  3. Spatial Foot-Traffic & Human-Impact Agent (`spatial_human_impact_agent`)

Executes Submodular Multi-Choice Knapsack Portfolio Optimization across Regimes A, B, and C,
computes Parameter Invariance Intervals and the Simplex Robust Awardee Set S_robust,
and generates the decision-grade Red-Team Compliance Report.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ADK.adk_context_loader import (
    build_system_prompt_with_adk_docs,
    get_agent_rubric,
    get_context_audit_summary,
    get_red_team_defenses,
    get_scoring_formulas,
)
from agents.runway_sector_purity_agent import (
    RunwaySectorPurityAgent,
    create_runway_sector_purity_adk_agent,
)
from agents.spatial_human_impact_agent import (
    SpatialHumanImpactAgent,
    create_spatial_human_impact_adk_agent,
)
from agents.supply_provenance_agent import (
    SupplyProvenanceAgent,
    create_supply_provenance_adk_agent,
)
from tools.compliance_reporter import (
    evaluate_red_team_compliance,
    format_red_team_compliance_report_markdown,
)
from tools.bigquery_connector import (
    get_gql_multihop_cascade_sql,
    get_property_graph_ddl,
    load_corridor_applicants,
)
from tools.scoring_engine import (
    compute_applicant_utility,
    compute_sensitivity_and_robust_awardees,
    evaluate_all_applicants,
    get_canonical_applicants,
    jaccard_similarity,
    optimize_portfolio_knapsack,
    run_all_regimes_comparison,
)


ORCHESTRATOR_BASE_PROMPT = """You are the Regime Stress-Test & Orchestrator Agent (Chief Municipal Economist)
for the San Francisco Central Market Micro-Grant ADK.
You must NEVER perform arithmetic in prose. You orchestrate:
1. Supply & Provenance Agent (`supply_provenance_agent`)
2. Runway, Sector & Purity Agent (`runway_sector_purity_agent`)
3. Spatial Foot-Traffic & Human-Impact Agent (`spatial_human_impact_agent`)
and invoke deterministic optimization tools to compare Regimes A, B, and C under a $50,000 budget,
prevent partial-grant dilution on Indivisible Capital Cliffs, enforce 200m spatial critical mass,
compute parameter invariance intervals [alpha_min, alpha_max] and S_robust, and produce the
Red-Team Compliance & Determination Report."""


class RegimeStressTestOrchestratorAgent:
    """
    End-to-end multi-agent pipeline orchestrator combining all 4 ADK modules and
    dynamically referencing `./ADK/DOCS/*.md` as its single source of truth.
    """

    def __init__(self, adk_dir: Optional[str] = None) -> None:
        self.agent_name = "regime_orchestrator_agent"
        self.adk_dir = adk_dir
        self.rubric = get_agent_rubric(self.agent_name, adk_dir=adk_dir)
        self.system_prompt = build_system_prompt_with_adk_docs(
            base_system_prompt=ORCHESTRATOR_BASE_PROMPT,
            adk_dir=adk_dir,
            agent_name=self.agent_name,
        )
        self.supply_agent = SupplyProvenanceAgent(adk_dir=adk_dir)
        self.runway_agent = RunwaySectorPurityAgent(adk_dir=adk_dir)
        self.spatial_agent = SpatialHumanImpactAgent(adk_dir=adk_dir)

    def run_pipeline(
        self,
        applicants: Optional[List[Dict[str, Any]]] = None,
        budget: float = 50000.0,
        preferred_regime: str = "C",
        weights: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Executes the complete 4-agent decision pipeline:
          Step 1: Dynamic Context Audit of `./ADK/DOCS/*.md`
          Step 2: Supply & Provenance Agent Evaluation
          Step 3: Runway, Sector & Purity Agent Evaluation
          Step 4: Multi-Regime (A, B, C) Submodular Knapsack Optimization
          Step 5: Spatial Foot-Traffic & Human-Impact Agent Cluster Verification
          Step 6: Parameter Invariance & Simplex Robustness Stress-Test
          Step 7: 10-Vector Red-Team Compliance Report Generation
        """
        apps = applicants if applicants is not None else get_canonical_applicants()

        context_audit = get_context_audit_summary(adk_dir=self.adk_dir)
        supply_output = self.supply_agent.evaluate(applicants=apps)
        runway_output = self.runway_agent.evaluate(applicants=apps)

        regimes_comparison = run_all_regimes_comparison(applicants=apps, budget=budget)
        selected_portfolio = optimize_portfolio_knapsack(
            applicants=apps,
            budget=budget,
            regime=preferred_regime,
            weights=weights,
        )

        spatial_output = self.spatial_agent.evaluate(
            applicants=apps,
            funded_ids=selected_portfolio["funded_ids"],
        )
        sensitivity_output = compute_sensitivity_and_robust_awardees(
            applicants=apps,
            budget=budget,
        )
        compliance_audit = evaluate_red_team_compliance(
            portfolio_result=selected_portfolio,
            applicants=apps,
            adk_dir=self.adk_dir,
        )
        compliance_markdown = format_red_team_compliance_report_markdown(
            portfolio_result=selected_portfolio,
            applicants=apps,
            adk_dir=self.adk_dir,
        )

        return {
            "orchestrator": self.agent_name,
            "context_audit": context_audit,
            "supply_agent_output": supply_output,
            "runway_agent_output": runway_output,
            "spatial_agent_output": spatial_output,
            "regimes_comparison": regimes_comparison,
            "selected_portfolio": selected_portfolio,
            "sensitivity_analysis": sensitivity_output,
            "red_team_compliance_audit": compliance_audit,
            "red_team_compliance_report_markdown": compliance_markdown,
        }


def create_orchestrator_adk_pipeline(
    model: str = "gemini-2.5-flash",
    adk_dir: Optional[str] = None,
) -> Any:
    """
    Constructs the root Google ADK `Agent` coordinating the 3 sub-agents and all
    deterministic scoring, regime stress-testing, and Red-Team compliance tools.
    """
    from google.adk.agents import Agent

    supply_sub = create_supply_provenance_adk_agent(model=model, adk_dir=adk_dir)
    runway_sub = create_runway_sector_purity_adk_agent(model=model, adk_dir=adk_dir)
    spatial_sub = create_spatial_human_impact_adk_agent(model=model, adk_dir=adk_dir)

    prompt = build_system_prompt_with_adk_docs(
        base_system_prompt=ORCHESTRATOR_BASE_PROMPT,
        adk_dir=adk_dir,
        agent_name="regime_orchestrator_agent",
    )

    return Agent(
        name="central_market_micro_grant_orchestrator",
        model=model,
        description=(
            "Chief Municipal Economist & Multi-Agent Orchestrator for the Central Market "
            "Ecosystem & Demand-Anchored Micro-Grant ADK."
        ),
        instruction=prompt,
        sub_agents=[supply_sub, runway_sub, spatial_sub],
        tools=[
            compute_applicant_utility,
            evaluate_all_applicants,
            jaccard_similarity,
            optimize_portfolio_knapsack,
            run_all_regimes_comparison,
            compute_sensitivity_and_robust_awardees,
            evaluate_red_team_compliance,
            format_red_team_compliance_report_markdown,
            get_red_team_defenses,
            get_scoring_formulas,
            load_corridor_applicants,
            get_property_graph_ddl,
            get_gql_multihop_cascade_sql,
        ],
    )
