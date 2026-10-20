"""
Supply & Provenance Agent (`agents/supply_provenance_agent.py`).

Evaluates B2B network topology, upstream parent/root suppliers (xi_i, mu_i, omega_parent),
local redundancy discount (r_j^-0.5), external distributor substitutability friction (theta_ext),
4-digit NAICS 81 B2B disaggregation, un-applied upstream corridor bottlenecks, and mandatory
1-invoice verification gates ([MODELED] vs. [VERIFIED]).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ADK.adk_context_loader import build_system_prompt_with_adk_docs, get_agent_rubric
from tools.bigquery_connector import (
    create_bigquery_mcp_toolset,
    ensure_bigquery_property_graph,
    execute_gql_anchor_closure_cascade,
    execute_gql_multihop_cascade,
)
from tools.scoring_engine import (
    PROVENANCE_MODELED,
    discover_unapplied_bottlenecks,
    filter_naics_81_b2b_links,
    get_canonical_applicants,
    piecewise_root_supplier_multiplier,
    supply_cascade_score,
    upstream_asymmetry_and_cascade_multiplier,
)


SUPPLY_AGENT_BASE_PROMPT = """You are the Supply & Provenance Agent for the Central Market Micro-Grant ADK.
You must NEVER calculate scores in prose. Always invoke your deterministic Python tools to evaluate:
1. Track 2 Commercial Network Contagion Score (S_cascade) with spatial decay, local redundancy (r_j^-0.5),
   and external distributor substitutability friction (theta_ext in [0.0, 0.80]).
2. Upstream Asymmetry Ratio (xi_i), Cascading Failure Multiplier (mu_i), and Piecewise Root Supplier
   Multiplier (omega_parent).
3. Vector 8 Mandatory 4-Digit NAICS Disaggregation (stripping false B2B edges from NAICS 8121/8129).
4. Vector 1 Provenance Tagging ([MODELED] vs [VERIFIED]), Zero-Cascade Lower-Bound Audit (alpha=0.0),
   and Pre-Disbursement 1-Invoice Gate triggers (cascade contribution > 30%).
5. Vector 9 Bidirectional 2-Hop Scan for Un-Applied Corridor Bottlenecks (B_upstream(Q))."""


class SupplyProvenanceAgent:
    """
    Deterministic & ADK-compatible Supply & Provenance Agent grounded in `./ADK/DOCS/*.md`.
    """

    def __init__(self, adk_dir: Optional[str] = None) -> None:
        self.agent_name = "supply_provenance_agent"
        self.adk_dir = adk_dir
        self.rubric = get_agent_rubric(self.agent_name, adk_dir=adk_dir)
        self.system_prompt = build_system_prompt_with_adk_docs(
            base_system_prompt=SUPPLY_AGENT_BASE_PROMPT,
            adk_dir=adk_dir,
            agent_name=self.agent_name,
        )

    def evaluate(
        self,
        applicants: Optional[List[Dict[str, Any]]] = None,
        w_cascade: float = 0.30,
        w_anchor: float = 0.25,
    ) -> Dict[str, Any]:
        """
        Executes deterministic B2B topology, root multiplier, NAICS 81 disaggregation,
        1-invoice gate, and un-applied bottleneck analysis across all applicants.
        """
        apps = applicants if applicants is not None else get_canonical_applicants()
        applicant_reports: Dict[str, Dict[str, Any]] = {}

        for app in apps:
            naics_check = filter_naics_81_b2b_links(
                naics_4=str(app.get("naics", "0000")),
                raw_outgoing_b2b_weight=float(app.get("cascade_score", 0.0)),
            )
            effective_cascade = naics_check["adjusted_b2b_weight"]
            out_deg = int(app.get("out_degree", len(app.get("downstream_dependents", []))))
            in_deg = int(app.get("in_degree", len(app.get("upstream_suppliers", []))))

            first_hop_edges = [
                {"alpha_ij": 0.35, "redundancy_r": 1.0}
                for _ in range(out_deg)
            ]
            hierarchy = upstream_asymmetry_and_cascade_multiplier(
                out_degree=out_deg,
                in_degree=in_deg,
                first_hop_edges=first_hop_edges,
            )
            omega_parent = piecewise_root_supplier_multiplier(out_deg, in_deg)

            anchor_val = float(app.get("anchor_score", 0.0))
            weighted_cascade = w_cascade * effective_cascade
            weighted_anchor = w_anchor * anchor_val
            cascade_share = (
                weighted_cascade / max(weighted_cascade + weighted_anchor, 1e-6)
                if (weighted_cascade + weighted_anchor) > 0
                else 0.0
            )
            requires_1_invoice = cascade_share > 0.30 and app.get("eligible", True)

            applicant_reports[app["id"]] = {
                "id": app["id"],
                "name": app["name"],
                "naics": str(app.get("naics", "")),
                "raw_cascade_score": float(app.get("cascade_score", 0.0)),
                "effective_cascade_score": effective_cascade,
                "naics_81_b2b_stripped": naics_check["b2b_stripped"],
                "naics_81_rule_note": naics_check["rule_applied"],
                "out_degree": out_deg,
                "in_degree": in_deg,
                "substitutability_theta_ext": float(app.get("substitutability_theta", 0.50)),
                "parent_supplier_weight": float(app.get("parent_supplier_weight", 1.00)),
                "computed_upstream_asymmetry_xi": round(hierarchy["upstream_asymmetry_xi_i"], 4),
                "computed_cascading_multiplier_mu": round(hierarchy["cascading_multiplier_mu_i"], 4),
                "piecewise_omega_parent": omega_parent,
                "zero_cascade_lower_bound_alpha_0": anchor_val,
                "cascade_vs_anchor_share": round(cascade_share, 4),
                "requires_pre_disbursement_1_invoice_gate": requires_1_invoice,
                "provenance_tag": app.get("provenance_status", PROVENANCE_MODELED),
                "verified_invoices_count": int(app.get("verified_invoices_count", 0)),
                "downstream_dependents": app.get("downstream_dependents", []),
            }

        bottleneck_alerts = discover_unapplied_bottlenecks(applicants=apps)

        return {
            "agent": self.agent_name,
            "role": "Supply & Provenance Agent",
            "applicant_supply_reports": applicant_reports,
            "unapplied_bottleneck_alerts": bottleneck_alerts,
            "invoice_gated_applicants": [
                r["name"]
                for r in applicant_reports.values()
                if r["requires_pre_disbursement_1_invoice_gate"]
            ],
        }


def create_supply_provenance_adk_agent(
    model: str = "gemini-2.5-flash",
    adk_dir: Optional[str] = None,
) -> Any:
    """
    Constructs a `google.adk.agents.Agent` instance wired with the Supply & Provenance
    tools and `./ADK/DOCS/*.md` system instructions.
    """
    from google.adk.agents import Agent

    prompt = build_system_prompt_with_adk_docs(
        base_system_prompt=SUPPLY_AGENT_BASE_PROMPT,
        adk_dir=adk_dir,
        agent_name="supply_provenance_agent",
    )
    supply_tools: List[Any] = [
        supply_cascade_score,
        upstream_asymmetry_and_cascade_multiplier,
        piecewise_root_supplier_multiplier,
        filter_naics_81_b2b_links,
        discover_unapplied_bottlenecks,
        ensure_bigquery_property_graph,
        execute_gql_multihop_cascade,
        execute_gql_anchor_closure_cascade,
    ]
    bq_mcp = create_bigquery_mcp_toolset()
    if bq_mcp is not None:
        supply_tools.append(bq_mcp)

    return Agent(
        name="supply_provenance_agent",
        model=model,
        description=(
            "Evaluates B2B supply topology, upstream parent/root multipliers, "
            "substitutability friction, NAICS 81 disaggregation, un-applied bottlenecks, "
            "and 1-invoice provenance verification gates."
        ),
        instruction=prompt,
        tools=supply_tools,
    )
