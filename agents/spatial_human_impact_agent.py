"""
Spatial Foot-Traffic & Human-Impact Agent (`agents/spatial_human_impact_agent.py`).

Enforces 200m spatial critical-mass cluster rules (requiring >= 3 co-located storefronts
when cluster vacancy > 35% to preserve pedestrian trip chaining and street vitality),
evaluates Track 1 Community Anchor scores (S_anchor) and Census Tract Equity Multipliers
(M_equity), and calculates Total People Helped per Grant Dollar (H_i, eta_i, S_people).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ADK.adk_context_loader import build_system_prompt_with_adk_docs, get_agent_rubric
from tools.scoring_engine import (
    calculate_total_people_helped,
    calculate_vulnerable_resident_reach,
    census_equity_multiplier,
    community_anchor_score,
    evaluate_spatial_cluster_critical_mass,
    get_canonical_applicants,
    haversine_distance_meters,
    people_helped_score,
)


SPATIAL_AGENT_BASE_PROMPT = """You are the Spatial Foot-Traffic & Human-Impact Agent for the Central Market Micro-Grant ADK.
You must NEVER calculate scores in prose. Always invoke your deterministic Python tools to evaluate:
1. Vector 6 200m Walkshed Spatial Clustering & Critical Mass Policy Rule (requiring >= 3 co-located
   storefronts in any cluster where retail vacancy risk exceeds 35% to protect pedestrian trip chaining).
2. Track 1 Community Anchor & Essential Access Score (S_anchor), including sole essential provider
   scarcity bonus (C_scarcity = 2.0) and SNAP/EBT/WIC/Medi-Cal verification.
3. Dimension 3 Total People Helped (H_i = w_W*W_i + w_net*W_net + w_C*C_i + w_R*R_i), Grant Efficiency
   per Dollar (eta_i), and 0-100 People Helped Score (S_people).
4. Census Tract Equity Multiplier (M_equity in [1.00, 1.50]) from ACS poverty and zero-vehicle shares."""


class SpatialHumanImpactAgent:
    """
    Deterministic & ADK-compatible Spatial Foot-Traffic & Human-Impact Agent grounded in `./ADK/DOCS/*.md`.
    """

    def __init__(self, adk_dir: Optional[str] = None) -> None:
        self.name = "Spatial_Human_Impact_Agent"
        self.display_name = "Spatial Foot-Traffic & Human-Impact Agent"
        self.agent_name = "spatial_human_impact_agent"
        self.adk_dir = adk_dir
        self.rubric = get_agent_rubric(self.agent_name, adk_dir=adk_dir)
        self.system_prompt = build_system_prompt_with_adk_docs(
            base_system_prompt=SPATIAL_AGENT_BASE_PROMPT,
            adk_dir=adk_dir,
            agent_name=self.agent_name,
        )

    def evaluate(
        self,
        applicants: Optional[List[Dict[str, Any]]] = None,
        funded_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Executes deterministic human beneficiary, equity multiplier, community anchor,
        and 200m spatial cluster critical-mass evaluations across all applicants.
        """
        apps = applicants if applicants is not None else get_canonical_applicants()
        if any(app.get("data_mode") == "source_review" for app in apps):
            return {"agent": self.agent_name, "status": "EVIDENCE_ONLY",
                    "note": "Registry locations support spatial display; jobs saved, residents served, sole-provider status and vacancy prevention require additional measured evidence."}
        impact_reports: Dict[str, Dict[str, Any]] = {}

        for app in apps:
            people_breakdown = calculate_total_people_helped(
                direct_employees_fte=float(app["direct_employees"]),
                network_workers=float(app["network_workers"]),
                daily_commuters=float(app["daily_commuters"]),
                vulnerable_residents=float(app["vulnerable_residents"]),
            )
            eff_breakdown = people_helped_score(
                total_people_helped=people_breakdown["total_people_helped_H_i"],
                grant_amount=float(app.get("requested_amount", 10000.0)),
            )
            acs_equity = census_equity_multiplier(
                poverty_rate=float(app.get("tract_poverty_rate", 0.30)),
                zero_vehicle_share=float(app.get("tract_zero_vehicle_share", 0.60)),
                mode="normalized",
            )

            impact_reports[app["id"]] = {
                "id": app["id"],
                "name": app["name"],
                "address": app.get("address", ""),
                "cluster_id": app.get("cluster_id", ""),
                "cluster_name": app.get("cluster_name", ""),
                "cluster_vacancy_rate": float(app.get("cluster_vacancy_rate", 0.35)),
                "anchor_score": float(app["anchor_score"]),
                "is_sole_essential_within_400m": bool(app.get("is_sole_essential_within_400m", False)),
                "canonical_equity_multiplier": float(app.get("equity_multiplier", 1.0)),
                "computed_acs_equity_multiplier": round(acs_equity, 3),
                "people_breakdown": people_breakdown,
                "efficiency_breakdown": eff_breakdown,
            }

        spatial_cluster_audit = evaluate_spatial_cluster_critical_mass(
            applicants=apps,
            funded_ids=funded_ids,
        )

        return {
            "agent": self.name,
            "agent_id": self.agent_name,
            "display_name": self.display_name,
            "role": "Spatial Foot-Traffic & Human-Impact Agent",
            "applicant_human_impact_reports": impact_reports,
            "spatial_cluster_audit": spatial_cluster_audit,
        }


def create_spatial_human_impact_adk_agent(
    model: str = "gemini-2.5-flash",
    adk_dir: Optional[str] = None,
) -> Any:
    """
    Constructs a `google.adk.agents.Agent` instance wired with the Spatial Foot-Traffic &
    Human-Impact deterministic tools and `./ADK/DOCS/*.md` system instructions.
    """
    from google.adk.agents import Agent

    prompt = build_system_prompt_with_adk_docs(
        base_system_prompt=SPATIAL_AGENT_BASE_PROMPT,
        adk_dir=adk_dir,
        agent_name="spatial_human_impact_agent",
    )
    return Agent(
        name="Spatial_Human_Impact_Agent",
        model=model,
        description=(
            "Spatial Foot-Traffic & Human-Impact Agent: Enforces 200m spatial critical-mass "
            "cluster rules, evaluates Track 1 Community Anchor scores and Census Tract Equity "
            "Multipliers, and computes Total People Helped per Dollar."
        ),
        instruction=prompt,
        tools=[
            calculate_total_people_helped,
            calculate_vulnerable_resident_reach,
            people_helped_score,
            census_equity_multiplier,
            community_anchor_score,
            haversine_distance_meters,
            evaluate_spatial_cluster_critical_mass,
        ],
    )
