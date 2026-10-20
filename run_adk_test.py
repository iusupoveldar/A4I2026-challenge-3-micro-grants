"""
One-Command ADK Test & Verification Runner (`run_adk_test.py`)
==============================================================
Run from the repository root:
  1. Test Canonical 11-Applicant Benchmark + Red-Team Compliance Gates:
     python run_adk_test.py

  2. Test Local Real CSV Snapshot (232 Central Market Businesses, zero cloud setup):
     python run_adk_test.py --mode local_csv

  3. Test Live Google BigQuery (`a4i_econ` + `LocalEconomy` Property Graph):
     python run_adk_test.py --mode bigquery --project YOUR_GCP_PROJECT_ID
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from adk_context_loader import get_context_audit_summary
from agents.regime_orchestrator_agent import (
    RegimeStressTestOrchestratorAgent,
    list_available_agents,
    select_deterministic_agent,
)
from tools.bigquery_connector import (
    BigQueryGraphConnector,
    get_gql_multihop_cascade_sql,
    get_property_graph_ddl,
    load_corridor_applicants,
)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Test the Ecosystem & Demand-Anchored Micro-Grant ADK Pipeline"
    )
    parser.add_argument(
        "--agent",
        default="Regime_Stress_Test_Orchestrator_Agent",
        help=(
            "Select which named ADK agent to run: "
            "'Regime_Stress_Test_Orchestrator_Agent' (default, runs full 4-agent pipeline), "
            "'Supply_Provenance_Agent', 'Runway_Sector_Purity_Agent', or 'Spatial_Human_Impact_Agent'."
        ),
    )
    parser.add_argument(
        "--list-agents",
        action="store_true",
        help="List all 4 selectable named ADK agents and exit.",
    )
    parser.add_argument(
        "--mode",
        choices=["canonical", "local_csv", "bigquery", "auto"],
        default="canonical",
        help="Data source mode: 'canonical' (11 benchmark applicants), 'local_csv' (232 real Central Market businesses), or 'bigquery' (live GCP BigQuery).",
    )
    parser.add_argument(
        "--project",
        default=None,
        help="Google Cloud Project ID for BigQuery mode (or set GOOGLE_CLOUD_PROJECT env var).",
    )
    parser.add_argument(
        "--dataset",
        default="a4i_econ",
        help="BigQuery dataset name (default: a4i_econ).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional max number of businesses to score.",
    )
    parser.add_argument(
        "--print-gql",
        action="store_true",
        help="Print the BigQuery Property Graph DDL and GQL traversal SQL.",
    )
    args = parser.parse_args(argv)

    if args.list_agents:
        print("Available Named ADK Agents:")
        for spec in list_available_agents():
            print(f"  - {spec['name']} ({spec['display_name']}): {spec['role']}")
        return 0

    print("=" * 80)
    print("A4I 2026 MICRO-GRANT ADK — END-TO-END VERIFICATION SUITE")
    print("=" * 80)

    # 1. Test Module 1: Dynamic Context Loader
    audit = get_context_audit_summary()
    print(f"\n[MODULE 1] Dynamic Context Loader (`adk_context_loader.py`)")
    print(f"  Docs Dir        : {audit['docs_directory']}")
    print(f"  Indexed Files   : {audit['total_markdown_files']} Markdown specification files")
    print(f"  Red-Team Vectors: {audit['red_team_vector_count']} vectors extracted")
    for fname, meta in audit["files"].items():
        print(
            f"    - {fname:<42} | {meta['section_count']:>2} sections | {meta['display_equation_count']:>2} LaTeX eqs | {meta['line_count']:>3} lines"
        )

    if args.print_gql:
        print("\n[BIGQUERY GQL] Property Graph DDL:")
        print(get_property_graph_ddl(args.dataset))
        print("\n[BIGQUERY GQL] Multi-Hop Cascade Traversal:")
        print(get_gql_multihop_cascade_sql(args.dataset))

    # 2. Load Applicants from selected data mode
    print(f"\n[DATA CONNECTOR] Loading applicants in mode='{args.mode}'...")
    if args.mode == "bigquery":
        connector = BigQueryGraphConnector(project_id=args.project, dataset=args.dataset)
        conn_status = connector.check_connection()
        if not conn_status.get("connected"):
            print(f"  [!] BigQuery connection check failed: {conn_status.get('error')}")
            print("  [!] Make sure GOOGLE_CLOUD_PROJECT is set and `gcloud auth application-default login` has been run.")
            return 1
        print(f"  Connected to BigQuery `{conn_status['project_id']}.{conn_status['dataset']}`:")
        for tbl_name, row_count in conn_status.get("tables", {}).items():
            print(f"    - {tbl_name:<24} : {row_count:,} rows")

    applicants, source_label = load_corridor_applicants(
        mode=args.mode,
        project_id=args.project,
        dataset=args.dataset,
        limit=args.limit,
    )
    print(f"  Source    : {source_label}")
    print(f"  Loaded    : {len(applicants)} applicant records")

    # 3. Run Selected Named Agent or Full 4-Agent Pipeline
    selected_agent = select_deterministic_agent(args.agent)
    print(f"\n[SELECTED AGENT] {selected_agent.name} ({selected_agent.display_name})")

    if isinstance(selected_agent, RegimeStressTestOrchestratorAgent):
        print("[MODULES 2-4] Running 4-Agent Pipeline + Knapsack Optimizer + Red-Team Auditor...")
        pipeline_output = selected_agent.run_pipeline(applicants=applicants)
        print("\n" + pipeline_output["red_team_compliance_report_markdown"])
    else:
        print(f"[SPECIALIST AGENT EVALUATION] Executing {selected_agent.display_name}...")
        agent_output = selected_agent.evaluate(applicants=applicants)
        print(json.dumps(agent_output, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
