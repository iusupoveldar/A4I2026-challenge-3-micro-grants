# Agent entrypoint and evidence modes

`agent.py` constructs the Google ADK orchestrator and its supply, runway and spatial
specialists. The updated source rules are in
[04_SOURCE_EVIDENCE_AND_REVIEW.md](../ADK/docs/04_SOURCE_EVIDENCE_AND_REVIEW.md).

- Source records produce **EVIDENCE_ONLY** until current financial, eligibility
  and provenance inputs are supplied. No cash, worker/resident counts, ownership
  or invoices are inferred from NAICS, historical approval or charge-off.
- `analyze_corridor_impact` traverses the **local reviewed** graph through 1–8 hops
  in either direction, with unique reach, weighted exposure and explanation paths.
- `review_industry_variety` reports the local cohort and cascade-band composition.
- `BigQueryGraphConnector.query_gql_multihop_cascade(max_hops=1..8)` traverses the
  **cloud** LocalEconomy graph using GQL. Do not substitute local graph counts.
- Explicit `canonical` mode is an illustrative regression scenario; it is not a
  silent fallback for unavailable source data or proof of a real grant allocation.

Run `python3 run_adk_test.py --mode local_csv` to inspect source-mode behavior.
Run `python3 run_adk_test.py --mode canonical` only for the illustrative benchmark.
Cloud deployment and an actually consumed Google-managed MCP integration remain
separate deliverables; this local review does not claim they were deployed or tested.

## Named agents and deployment entrypoints

The newer runtime exposes all four specialists through `adk web agents`,
`select_adk_agent(name)` and `select_deterministic_agent(name)`:

- `Regime_Stress_Test_Orchestrator_Agent`
- `Supply_Provenance_Agent`
- `Runway_Sector_Purity_Agent`
- `Spatial_Human_Impact_Agent`

Use `python3 run_adk_test.py --list-agents` to inspect their descriptions, or
`python3 run_adk_test.py --agent Supply_Provenance_Agent --mode local_csv` to
inspect modeled source exposure. Python deterministic agents share `.evaluate()`.
`ADK_AGENT_NAME` selects the root package's agent; see [agent.py](agent.py).

The live connector also exposes named shortest-path queries, graph traversal,
comparison and funding-tool entrypoints. Source-mode comparison and funding tools
return **EVIDENCE_ONLY**; explicit canonical mode calculates illustrative awards.
A failed live query returns its error and no fabricated paths.

Google-managed BigQuery MCP/toolbox wiring is in
[tools/mcp_bigquery_toolset.py](../tools/mcp_bigquery_toolset.py) and
[tools.yaml](../tools.yaml). Configuration presence does not prove an authenticated
MCP call succeeded. Runtime deployment sources are in
[scripts/deploy_agent_runtime.py](../scripts/deploy_agent_runtime.py),
[scripts/deploy.sh](../scripts/deploy.sh) and
[server/app.py](../server/app.py). The refactor/verification guide is
[04_ADK_REFACTOR_AND_TEST_GUIDE.md](../ADK/docs/04_ADK_REFACTOR_AND_TEST_GUIDE.md).
Cloud deployment and live end-to-end validation have not been performed in this review.
