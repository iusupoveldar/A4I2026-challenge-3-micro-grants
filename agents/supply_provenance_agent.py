"""
Supply & Provenance Agent (`agents/supply_provenance_agent.py`).

Evaluates B2B network topology, upstream parent/root suppliers (xi_i, mu_i, omega_parent),
local redundancy discount (r_j^-0.5), external distributor substitutability friction (theta_ext),
4-digit NAICS 81 B2B disaggregation, un-applied upstream corridor bottlenecks, mandatory
1-invoice verification gates ([MODELED] vs. [VERIFIED]), and live BigQuery GQL multi-hop
property graph traversals on `a4i_econ.LocalEconomy`.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ADK.adk_context_loader import build_system_prompt_with_adk_docs, get_agent_rubric
from tools.bigquery_connector import (
    ensure_bigquery_property_graph,
    evaluate_gql_cascade_and_recommend_funding,
    get_gql_multihop_cascade_sql,
    get_gql_shortest_path_trace_sql,
    get_property_graph_ddl,
    trace_applicant_multihop_paths_and_compare,
    trace_multihop_consequence_chains,
    traverse_corridor_graph_gql,
)
from tools.mcp_bigquery_toolset import (
    get_google_managed_bigquery_mcp_toolsets,
    get_mcp_bigquery_server_status,
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
from tools.resilience_analysis import analyze_corridor_impact, find_corridor_businesses, review_industry_variety


SUPPLY_AGENT_BASE_PROMPT = """You are the Supply & Provenance Agent for the Central Market Micro-Grant ADK.
Source evidence takes priority over illustrative benchmark narratives. Use analyze_corridor_impact
for local 1–8 hop paths in either direction; 2 hops is the decision baseline, deeper hops are sensitivity.
Use find_corridor_businesses first to select the registry location ID by name/address.
cm_* IDs are scenario IDs. Check tool status; on an unknown or ambiguous business,
use the returned candidates to select a location instead of inventing an ID or reach.
Use traverse_corridor_graph_gql for live BigQuery paths, and identify the graph in every result.
Never create edges from a degree count or call modeled options confirmed substitutability.
You must NEVER calculate scores in prose. Invoke deterministic Python and BigQuery MCP/GQL tools to evaluate:
1. Multi-hop BigQuery Property Graph traversal, with named ANY SHORTEST explanation paths.
2. Track 2 Commercial Network Contagion Score (S_cascade) with spatial decay, local redundancy (r_j^-0.5),
   and external distributor substitutability friction (theta_ext in [0.0, 0.80]).
3. Upstream Asymmetry Ratio (xi_i), Cascading Failure Multiplier (mu_i), and Piecewise Root Supplier
   Multiplier (omega_parent).
4. Vector 8 Mandatory 4-Digit NAICS Disaggregation (stripping false B2B edges from NAICS 8121/8129).
5. Vector 1 Provenance Tagging ([MODELED] vs [VERIFIED]), discounting modeled `Supplies` and `DrawsFootfall`
   edges relative to verified `borrowed_from` SBA loan records, Zero-Cascade Lower-Bound Audit (alpha=0.0),
   and Pre-Disbursement 1-Invoice Gate triggers (cascade contribution > 30%).
6. Vector 9 Bidirectional 2-Hop Scan for Un-Applied Corridor Bottlenecks (B_upstream(Q))."""


class SupplyProvenanceAgent:
    """
    Deterministic & ADK-compatible Supply & Provenance Agent grounded in `./ADK/DOCS/*.md`.
    """

    def __init__(self, adk_dir: Optional[str] = None) -> None:
        self.name = "Supply_Provenance_Agent"
        self.display_name = "Supply & Provenance Agent"
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
        max_hops: int = 2,
    ) -> Dict[str, Any]:
        """
        Executes deterministic B2B topology, root multiplier, NAICS 81 disaggregation,
        1-invoice gate, and un-applied bottleneck analysis across all applicants.
        """
        apps = applicants if applicants is not None else get_canonical_applicants()
        if any(app.get("data_mode") == "source_review" for app in apps):
            if any(str(app.get("data_source", "")).startswith("BIGQUERY:") for app in apps):
                return {"agent": self.agent_name, "status": "EVIDENCE_ONLY",
                        "note": "Use the BigQueryGraphConnector for this cloud graph. The local registry/BEA graph has different parameters and must not substitute for its paths."}
            traces = []
            for app in apps:
                result = analyze_corridor_impact(app["id"], max_hops)
                if result.get("status") != "OK":
                    traces.append(result)
                    continue
                traces.append({**{k:v for k,v in result.items() if k != "endpoints"},
                               "example_endpoints": sorted(result["endpoints"], key=lambda e:-e["hop"])[:3]})
            return {"agent": self.agent_name, "status": "EVIDENCE_ONLY",
                    "industry_variety": review_industry_variety(),
                    "traces": traces,
                    "note": "Supply exposure is modeled; SBA loan history is not a verified vendor invoice."}
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
            "agent": self.name,
            "agent_id": self.agent_name,
            "display_name": self.display_name,
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
    include_mcp_toolsets: bool = True,
) -> Any:
    """
    Constructs a `google.adk.agents.Agent` instance wired with the Supply & Provenance
    custom Python tools, multi-hop GQL Property Graph traversal tools, Google-managed
    BigQuery MCP toolsets, and `./ADK/DOCS/*.md` system instructions.
    """
    from google.adk.agents import Agent

    prompt = build_system_prompt_with_adk_docs(
        base_system_prompt=SUPPLY_AGENT_BASE_PROMPT,
        adk_dir=adk_dir,
        agent_name="supply_provenance_agent",
    )
    agent_tools: List[Any] = [
        trace_applicant_multihop_paths_and_compare,
        trace_multihop_consequence_chains,
        ensure_bigquery_property_graph,
        traverse_corridor_graph_gql,
        evaluate_gql_cascade_and_recommend_funding,
        get_property_graph_ddl,
        get_gql_multihop_cascade_sql,
        get_gql_shortest_path_trace_sql,
        get_mcp_bigquery_server_status,
        supply_cascade_score,
        upstream_asymmetry_and_cascade_multiplier,
        piecewise_root_supplier_multiplier,
        filter_naics_81_b2b_links,
        discover_unapplied_bottlenecks,
        analyze_corridor_impact,
        find_corridor_businesses,
        review_industry_variety,
    ]
    if include_mcp_toolsets:
        agent_tools.extend(get_google_managed_bigquery_mcp_toolsets())

    return Agent(
        name="Supply_Provenance_Agent",
        model=model,
        description=(
            "Supply & Provenance Agent: Traverses the BigQuery a4i_econ.LocalEconomy Property "
            "Graph via multi-hop GQL and Google-managed BigQuery MCP tools; evaluates B2B "
            "supply topology, upstream parent/root multipliers, substitutability friction, "
            "NAICS 81 disaggregation, un-applied bottlenecks, and 1-invoice provenance verification gates."
        ),
        instruction=prompt,
        tools=agent_tools,
    )
