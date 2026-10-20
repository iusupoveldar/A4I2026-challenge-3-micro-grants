import json
import math
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.resilience_analysis import (CorridorGraph, grant_scenario, industry_variety,
                                      lookup_failure_rate, naics_detail, rank_consequences)
from tools.bigquery_connector import get_gql_multihop_cascade_sql, load_corridor_applicants
from tools.scoring_engine import compute_applicant_utility
from tools.bigquery_connector import (BigQueryGraphConnector, _build_local_fallback_gql_rows,
                                     evaluate_gql_cascade_and_recommend_funding,
                                     trace_applicant_multihop_paths_and_compare,
                                     traverse_corridor_graph_gql)


def node(i, code="3118"):
    return {"business_id": str(i), "name": str(i), **naics_detail(code)}


def edge(a, b, weight=0.5, metres=0):
    return {"supplier_id": str(a), "buyer_id": str(b), "intensity": weight, "metres": metres}


class TraversalTests(unittest.TestCase):
    def test_long_chain_and_reverse_six_hops(self):
        g = CorridorGraph([node(i) for i in range(7)], [edge(i,i+1) for i in range(6)])
        self.assertEqual(g.trace("0",3)["reach"],3)
        self.assertEqual(g.trace("0",6)["reach"],6)
        self.assertEqual(g.trace("6",6,"upstream")["reach"],6)
        self.assertEqual(g.trace("6",6)["reach"],0)

    def test_cycles_and_diamond_count_destinations_once(self):
        g = CorridorGraph([node(i,str(3118+i)) for i in range(4)],
                          [edge(0,1),edge(0,2),edge(1,3),edge(2,3),edge(3,0)])
        result=g.trace("0",8)
        self.assertEqual(result["reach"],3)
        self.assertEqual([r["new_businesses"] for r in result["profile"]],[2,1,0,0,0,0,0,0])
        end=next(e for e in result["endpoints"] if e["business_id"]=="3")
        self.assertEqual(end["hop"],2)
        self.assertEqual(end["weighted_exposure"],.25)
        self.assertEqual(result["weighted_exposure"],1.25)

    def test_strongest_path_is_not_always_shortest(self):
        g=CorridorGraph([node(i,str(3118+i)) for i in range(3)],
                        [edge(0,2,.01),edge(0,1,.8),edge(1,2,.8)])
        end=next(e for e in g.trace("0",2)["endpoints"] if e["business_id"]=="2")
        self.assertEqual(end["path"],["0","2"])
        self.assertEqual(end["weight_path"],["0","1","2"])
        self.assertAlmostEqual(end["weighted_exposure"],.64)

    def test_buyer_side_options_not_corridor_peer_count(self):
        g=CorridorGraph([node(0),node(1),node(2,"7225"),node(3,"7225")],
                        [edge(0,2),edge(1,2),edge(0,3)])
        by_pair={(e["supplier_id"],e["buyer_id"]):e for e in g.edges}
        self.assertEqual(by_pair["0","2"]["buyer_input_alternatives"],1)
        self.assertEqual(by_pair["0","3"]["buyer_input_alternatives"],0)
        self.assertEqual(by_pair["0","2"]["adjusted_weight"],.25)

    def test_broad_codes_do_not_prove_same_input(self):
        g=CorridorGraph([node(0,"44"),node(1,"44"),node(2,"7225")],[edge(0,2),edge(1,2)])
        self.assertTrue(all(e["buyer_input_alternatives"]==0 for e in g.edges))

    def test_decay_reduces_exposure(self):
        g=CorridorGraph([node(0),node(1,"7225")],[edge(0,1,.5,400)])
        self.assertAlmostEqual(g.trace("0",1)["weighted_exposure"],.5/math.e)

    def test_invalid_graph_inputs_fail(self):
        for nodes,edges in [([node(0),node(0)],[]),([node(0)],[edge(0,1)]),
                            ([node(0),node(1)],[edge(0,1),edge(0,1)]),
                            ([node(0),node(1)],[edge(0,1,metres=-1)]),
                            ([node(0),node(1)],[edge(0,1,weight=float("nan"))])]:
            with self.subTest(edges=edges),self.assertRaises(ValueError):CorridorGraph(nodes,edges)

    def test_hop_bounds(self):
        g=CorridorGraph([node(0)],[])
        for h in (0,9,2.5):
            with self.assertRaises(ValueError):g.trace("0",h)

    def test_hub_can_lose_without_industry_exclusion(self):
        nodes=[node(i) for i in range(34)]
        g=CorridorGraph(nodes,[edge(0,i,.1) for i in range(2,34)]+[edge(1,i,.5) for i in range(2,7)])
        ranks=rank_consequences(g)
        self.assertEqual(ranks[0]["business_id"],"1")
        hub=next(r for r in ranks if r["business_id"]=="0")
        self.assertFalse(hub["cascade_case"])
        self.assertIsNotNone(hub["rank_before_decay"])
        self.assertIsNone(hub["p_fail"])


class EvidenceTests(unittest.TestCase):
    def test_short_and_nonstandard_naics_not_forced(self):
        self.assertEqual(naics_detail("72")["naics4"],"72")
        self.assertEqual(naics_detail("44")["naics4"],"44")
        self.assertEqual(naics_detail("547115")["model_naics"],"54")

    def test_prior_fallback_and_missing(self):
        rates=[{"level":"naics2","code":"72","p_fail":"0.03","basis":"notebook","horizon_months":"48"}]
        self.assertEqual(lookup_failure_rate(node(0,"72"),rates)["p_fail_level"],"naics2")
        self.assertIsNone(lookup_failure_rate(node(0),[])["p_fail"])
        with self.assertRaises(ValueError):lookup_failure_rate(node(0,"72"),rates*2)

    def test_grant_response_differs_by_known_debt_and_absent_stays_unknown(self):
        small=grant_scenario(.05,8000,1000)
        large=grant_scenario(.05,8000,8000)
        self.assertGreater(small["risk_reduction"],large["risk_reduction"])
        self.assertIsNone(grant_scenario(.05,8000,None)["risk_reduction"])
        self.assertEqual(grant_scenario(.05,0,1000)["risk_reduction"],0)

    def test_selected_industry_denominators(self):
        nodes=[node(0,"7225"),node(1,"7225"),node(2,"5415")]
        self.assertEqual(industry_variety(nodes)["businesses"],3)
        self.assertEqual(industry_variety(nodes,{"2"})["industry_groups"],1)

    def test_agent_real_data_cannot_fabricate_grant_inputs(self):
        apps,source=load_corridor_applicants("local_csv",limit=2)
        self.assertEqual(apps[0]["data_mode"],"source_review")
        self.assertNotIn("liquid_cash",apps[0])
        self.assertNotIn("verified_invoices_count",apps[0]["missing_decision_inputs"])
        with self.assertRaises(ValueError):compute_applicant_utility(apps[0])

    def test_gql_supports_eight_hops_and_distinct_union(self):
        sql=get_gql_multihop_cascade_sql(max_hops=8)
        self.assertIn("ANY SHORTEST",sql)
        self.assertIn("{1,8}",sql)
        self.assertNotIn("COALESCE(hop2",sql)
        with self.assertRaises(ValueError):get_gql_multihop_cascade_sql(max_hops=9)

    def test_generated_review_reconciles(self):
        root=Path(__file__).resolve().parents[1]
        d=json.loads((root/"data/task_2_3_review.json").read_text())
        self.assertEqual(len(d["nodes"]),len({n["business_id"] for n in d["nodes"]}))
        self.assertEqual(sum(d["industry_variety"]["counts"].values()),len(d["nodes"]))
        self.assertTrue(all(n["latitude"] and n["location_start_date"] for n in d["nodes"]))
        self.assertTrue(all(r["p_fail"] is None for r in d["ranking"]) if not d["sources"]["rates"] else True)


class ConnectorIntegrationTests(unittest.TestCase):
    def test_failed_live_query_does_not_manufacture_snapshot_results(self):
        with patch.object(BigQueryGraphConnector, "query_gql_multihop_cascade", side_effect=RuntimeError("unavailable")):
            result = traverse_corridor_graph_gql(max_hops=8)
        self.assertEqual(result["execution_mode"], "BIGQUERY_QUERY_FAILED")
        self.assertFalse(result["gql_executed"])
        self.assertEqual(result["multihop_cascade_rows"], [])
        self.assertEqual(result["shortest_paths_sample"], [])

    def test_timeout_and_eight_hop_query_are_both_preserved(self):
        from unittest.mock import Mock
        connector = BigQueryGraphConnector()
        connector._client = Mock()
        connector._client.query.return_value.result.return_value = []
        connector.query_gql_multihop_cascade(max_hops=8, timeout=5.0)
        self.assertIn("{1,8}", connector._client.query.call_args.args[0])
        connector._client.query.return_value.result.assert_called_once_with(timeout=5.0)

    def test_explicit_local_traversal_matches_reviewed_edges(self):
        from tools.bigquery_connector import _load_local_review_graph
        graph = _load_local_review_graph()
        rows = _build_local_fallback_gql_rows(min_exposed=0, max_hops=6)
        self.assertEqual(len(rows), len(graph.nodes))
        for row in rows:
            self.assertEqual(row["exposed_businesses"], graph.trace(row["business_id"], 6)["reach"])
            self.assertNotIn("runway_quarters", row)

    def test_source_funding_tool_does_not_call_portfolio_optimizer(self):
        with patch("tools.scoring_engine.optimize_portfolio_knapsack") as optimize:
            result = evaluate_gql_cascade_and_recommend_funding(mode="local_csv")
        optimize.assert_not_called()
        self.assertEqual(result["status"], "EVIDENCE_ONLY")
        self.assertEqual(result["funding_recommendations"], [])
        self.assertFalse(result["traversal"]["gql_executed"])

    def test_named_source_comparison_has_real_paths_without_fixture_finances(self):
        rows = _build_local_fallback_gql_rows(min_exposed=1)
        selected = [r["business_id"] for r in rows[:2]]
        result = trace_applicant_multihop_paths_and_compare(*selected, mode="local_csv", max_hops=6)
        self.assertEqual(result["status"], "EVIDENCE_ONLY")
        for selected_id, trace in zip(selected, result["comparison"]):
            self.assertEqual(trace["root"], selected_id)
            self.assertEqual(trace["max_hops"], 6)
            for endpoint in trace["endpoints"]:
                self.assertEqual(endpoint["named_path"][0]["business_id"], selected_id)
                self.assertEqual(endpoint["named_path"][-1]["business_id"], endpoint["business_id"])
        with self.assertRaises(ValueError):
            trace_applicant_multihop_paths_and_compare("unknown applicant", selected[0], mode="local_csv")

    def test_all_selectable_agents_keep_source_evidence_gate(self):
        from agents.regime_orchestrator_agent import list_available_agents, select_deterministic_agent
        apps, _ = load_corridor_applicants("local_csv", limit=2)
        catalog = list_available_agents()
        self.assertEqual(len(catalog), 4)
        for spec in catalog:
            result = select_deterministic_agent(spec["name"]).evaluate(applicants=apps)
            self.assertEqual(result["status"], "EVIDENCE_ONLY")


if __name__ == "__main__":unittest.main()
