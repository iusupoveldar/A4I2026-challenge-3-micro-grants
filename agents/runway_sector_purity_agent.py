"""
Runway, Sector & Purity Agent (`agents/runway_sector_purity_agent.py`).

Evaluates Stage 0 Corporate Exclusion Gate (E_corp in {0, 1}), financial buffers,
consecutive bad-quarter logistic survival curves (Delta P(g_i | r_i), Phi_runway,
Theta_viable), sector volatility/margins (Omega_s, Psi_s, rho_s), and Small-Business
Purity rules (P_pure).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ADK.adk_context_loader import build_system_prompt_with_adk_docs, get_agent_rubric
from tools.scoring_engine import (
    compute_quarterly_runway,
    cyclical_viability_factor,
    evaluate_corporate_exclusion_gate,
    get_canonical_applicants,
    logistic_survival_probability,
    marginal_survival_lift,
    optimal_runway_inflection_point,
    runway_priority_score,
    sector_risk_multiplier,
    sector_volatility_index,
    small_business_purity_score,
    structural_viability_gate,
)


RUNWAY_AGENT_BASE_PROMPT = """You are the Runway, Sector & Purity Agent for the Central Market Micro-Grant ADK.
You must NEVER calculate scores in prose. Always invoke your deterministic Python tools to evaluate:
1. Stage 0 Hard Corporate Exclusion Gate (E_corp in (0, 1)) blocking enterprise tech, biotech,
   autonomous vehicle conglomerates, >50 FTE firms, >3 location chains, and >=25% institutional ownership.
2. Dimension 1 Financial Runway (r_i = C_i / kappa_i), Logistic Survival Lift Delta P(g_i | r_i),
   Theorem 1 inflection optimality (r_max = r* - Delta_r / 2), Non-Monotonic Survival Bell Curve
   Phi_runway(r_i), and Structural Viability Gate Theta_viable (insolvency floor 0.10).
3. Dimension 2 Sector Volatility & Margin Dynamics (Omega_s, Psi_s, rho_s).
4. Dimension 4 Continuous Small-Business Purity Score P_pure(i) across employee headcount,
   locations, ownership structure, and revenue decay."""


class RunwaySectorPurityAgent:
    """
    Deterministic & ADK-compatible Runway, Sector & Purity Agent grounded in `./ADK/DOCS/*.md`.
    """

    def __init__(self, adk_dir: Optional[str] = None) -> None:
        self.name = "Runway_Sector_Purity_Agent"
        self.display_name = "Runway, Sector & Purity Agent"
        self.agent_name = "runway_sector_purity_agent"
        self.adk_dir = adk_dir
        self.rubric = get_agent_rubric(self.agent_name, adk_dir=adk_dir)
        self.system_prompt = build_system_prompt_with_adk_docs(
            base_system_prompt=RUNWAY_AGENT_BASE_PROMPT,
            adk_dir=adk_dir,
            agent_name=self.agent_name,
        )

    def evaluate(
        self,
        applicants: Optional[List[Dict[str, Any]]] = None,
        volatility_weight: float = 0.25,
    ) -> Dict[str, Any]:
        """
        Executes deterministic Stage 0 corporate gate, runway survival lift, sector volatility,
        and small-business purity evaluations across all applicants.
        """
        apps = applicants if applicants is not None else get_canonical_applicants()
        reports: Dict[str, Dict[str, Any]] = {}

        for app in apps:
            gate = evaluate_corporate_exclusion_gate(
                naics_4=str(app.get("naics", "0000")),
                fte_count=float(app.get("direct_employees", 0)),
                location_count=int(app.get("location_count", 1)),
                storefront_certified=bool(app.get("storefront_certified", app.get("eligible", True))),
                institutional_ownership_pct=float(app.get("institutional_ownership_pct", 0.0)),
                explicit_eligible_flag=app.get("eligible", True),
            )

            runway_q = float(app["runway_quarters"])
            burn_rate = float(app["burn_rate"])
            req_amt = float(app.get("requested_amount", 10000.0))

            runway_eval = runway_priority_score(
                runway_quarters=runway_q,
                quarterly_burn_rate=burn_rate,
                requested_amount=req_amt,
            )
            r_opt = optimal_runway_inflection_point(grant_amount=req_amt, quarterly_burn_rate=burn_rate)

            rho_s = sector_risk_multiplier(
                sector_volatility=float(app["sector_volatility"]),
                volatility_weight=volatility_weight,
            )

            purity_calc = small_business_purity_score(
                fte_count=float(app.get("direct_employees", 5)),
                location_count=int(app.get("location_count", 1)),
                ownership_type=str(app.get("ownership_type", "sole_or_family_local")),
                annual_revenue=float(app.get("annual_revenue", 350000.0)),
            )

            reports[app["id"]] = {
                "id": app["id"],
                "name": app["name"],
                "e_corp": gate["e_corp"],
                "eligible": gate["eligible"],
                "disqualification_reasons": gate["disqualification_reasons"],
                "runway_quarters": runway_q,
                "burn_rate": burn_rate,
                "optimal_inflection_runway_r_max": round(r_opt, 3),
                "p0_survival": round(runway_eval["p0_survival"], 4),
                "marginal_survival_lift_delta_p": round(runway_eval["marginal_survival_lift_delta_p"], 4),
                "phi_runway_bell_score": round(runway_eval["phi_runway_score"], 2),
                "theta_viable_gate": runway_eval["theta_viable"],
                "triage_zone": runway_eval["triage_zone"],
                "burn_rate_audit_flag_2_5_sigma": runway_eval["burn_rate_audit_flag_2_5_sigma"],
                "two_party_warrant_required": runway_eval["two_party_warrant_required"],
                "sector_volatility": float(app["sector_volatility"]),
                "sector_risk_multiplier_rho_s": round(rho_s, 4),
                "canonical_small_biz_purity": float(app["small_biz_purity"]),
                "formula_purity_breakdown": purity_calc,
            }

        return {
            "agent": self.name,
            "agent_id": self.agent_name,
            "display_name": self.display_name,
            "role": "Runway, Sector & Purity Agent",
            "applicant_financial_purity_reports": reports,
            "disqualified_corporate_entities": [
                r["name"] for r in reports.values() if not r["eligible"]
            ],
            "critical_sweet_spot_applicants": [
                r["name"]
                for r in reports.values()
                if r["eligible"] and r["triage_zone"] == "CRITICAL_TRIAGE_SWEET_SPOT"
            ],
        }


def create_runway_sector_purity_adk_agent(
    model: str = "gemini-2.5-flash",
    adk_dir: Optional[str] = None,
) -> Any:
    """
    Constructs a `google.adk.agents.Agent` instance wired with the Runway, Sector & Purity
    deterministic tools and `./ADK/DOCS/*.md` system instructions.
    """
    from google.adk.agents import Agent

    prompt = build_system_prompt_with_adk_docs(
        base_system_prompt=RUNWAY_AGENT_BASE_PROMPT,
        adk_dir=adk_dir,
        agent_name="runway_sector_purity_agent",
    )
    return Agent(
        name="Runway_Sector_Purity_Agent",
        model=model,
        description=(
            "Runway, Sector & Purity Agent: Enforces Stage 0 Corporate Exclusion Gate, "
            "evaluates financial runway survival lift, structural viability gates, "
            "sector volatility multipliers, and small-business purity."
        ),
        instruction=prompt,
        tools=[
            evaluate_corporate_exclusion_gate,
            compute_quarterly_runway,
            logistic_survival_probability,
            marginal_survival_lift,
            optimal_runway_inflection_point,
            structural_viability_gate,
            runway_priority_score,
            sector_volatility_index,
            cyclical_viability_factor,
            sector_risk_multiplier,
            small_business_purity_score,
        ],
    )
