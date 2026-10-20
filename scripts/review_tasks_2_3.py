#!/usr/bin/env python3
"""Rebuild the Task 2/3 audit and graph analysis from documented sources.

Run from any directory: python3 scripts/review_tasks_2_3.py
Optional canonical rates: --rates path/to/industry_failure_rates.csv
No cloud writes, hand-entered risk priors, synthetic locations, or forced winners.
"""
import argparse
import csv
import hashlib
import json
import statistics
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.resilience_analysis import (CorridorGraph, industry_variety, model_supply_edges,
                                      rank_consequences, registry_nodes)


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def build(rates_path=None):
    source = ROOT / "data/verified_registry.json"
    records = json.loads(source.read_text())
    as_of = date.fromisoformat(max(r["data_as_of"][:10] for r in records))
    nodes = registry_nodes(records, as_of)
    coefficients = read_csv(ROOT / "data/bea_direct_requirements.csv")
    edges = model_supply_edges(nodes, coefficients)
    graph = CorridorGraph(nodes, edges)
    rates = read_csv(rates_path) if rates_path and rates_path.exists() else []
    if rates and not {"level", "code", "p_fail", "basis", "horizon_months"} <= set(rates[0]):
        raise ValueError("Use industry_failure_rates exported by Challenge3.ipynb; legacy priors are not accepted")
    ranking = rank_consequences(graph, rates)
    profiles = [graph.trace(n["business_id"], 8) for n in nodes]
    depth = [{"hop": h,
              "median_reach": statistics.median(p["profile"][h-1]["cumulative_businesses"] for p in profiles),
              "max_reach": max(p["profile"][h-1]["cumulative_businesses"] for p in profiles),
              "roots_gaining_new_nodes": sum(p["profile"][h-1]["new_businesses"] > 0 for p in profiles)}
             for h in range(1, 9)]
    starter_edges = model_supply_edges(nodes, coefficients, floor=0.005, max_metres=1200)
    starter = CorridorGraph(nodes, starter_edges)
    collisions = defaultdict(list)
    for n in nodes:
        collisions[n["name"].casefold()].append({k: n[k] for k in ("business_id", "name", "address")})
    collisions = [v for v in collisions.values() if len(v) > 1]
    legacy = read_csv(ROOT / "data/custom_bq_upload/business_sba_summary.csv")
    actual = {n["business_id"]: n for n in nodes}
    changes = []
    for row in legacy:
        n = actual.get(row["business_id"])
        if n:
            for old_key, new_key in [("naics4", "naics4"), ("registration_year", "registration_year")]:
                if str(row.get(old_key, "")) != str(n[new_key]):
                    changes.append({"business_id": n["business_id"], "name": n["name"], "field": old_key,
                                    "legacy": row.get(old_key), "registry": n[new_key]})
    kept_ids = {r["business_id"] for r in legacy}
    band_ids = {r["business_id"] for r in ranking if r["cascade_case"]}
    same_site = defaultdict(list)
    for n in nodes:
        key = tuple(" ".join(str(n[k]).casefold().split()) for k in ("name", "legal_name", "address"))
        same_site[key].append({k: n[k] for k in ("business_id", "name", "legal_name", "address")})
    same_site = [v for v in same_site.values() if len(v) > 1]
    report = {
        "as_of": as_of.isoformat(), "scope": "Registry matches for the local all-locations CSV; not a citywide census",
        "sources": {"registry_url": "https://data.sf.gov/resource/g8m3-pdis.json",
                    "registry_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                    "bea_sha256": hashlib.sha256((ROOT / "data/bea_direct_requirements.csv").read_bytes()).hexdigest(),
                    "rates": str(rates_path) if rates else None},
        "nodes": nodes, "edges": graph.edges,
        "model": {"coefficient_floor": 0.015, "max_supply_metres": 500, "max_suppliers_per_buyer": 5,
                  "decay_metres": 400, "alternative_metres": 500, "max_hops": 8, "decision_hops": 2,
                  "keystone_band": [5, 25], "supply_provenance": "MODELED, not verified transactions"},
        "industry_variety": industry_variety(nodes),
        "shortlist_variety": industry_variety(nodes, band_ids), "depth_sensitivity": depth,
        "model_sensitivity": {"starter_edges": len(starter_edges), "reviewed_edges": len(edges),
                              "starter_max_reach_2hop": max(starter.trace(n["business_id"], 2)["reach"] for n in nodes),
                              "reviewed_max_reach_2hop": max(r["reach_2hop"] for r in ranking)},
        "ranking": ranking,
        "audit": {"legacy_rows": len(legacy), "registry_locations": len(nodes),
                  "name_collisions_preserved": collisions, "source_corrections": changes,
                  "same_name_legal_address_candidates": same_site,
                  "counting_unit": "Registry location ID, not deduplicated firm or confirmed unique physical storefront. Co-located filings need source resolution.",
                  "graffeo_records_in_this_cohort": [n["business_id"] for n in nodes if "graffeo" in n["name"].casefold()],
                  "locations_missing_from_legacy_dedup": [n["business_id"] for n in nodes if n["business_id"] not in kept_ids],
                  "missing_registry_ids": sorted(kept_ids-set(actual)),
                  "rates_status": "canonical notebook export" if rates else "MISSING — legacy hand-entered rates excluded",
                  "non_specific_codes": [{"business_id": n["business_id"], "name": n["name"], "naics": n["naics"]}
                                         for n in nodes if n["naics_resolution"] != "four_digit"],
                  "loans_status": "Legacy matched-loan CSV is not address-verified source evidence; excluded from recommendations",
                  "footfall_status": "No local employer-block/footfall snapshot; anchor-shock query provided for BigQuery",
                  "grant_status": "No verified operating costs, current debt balances or causal grant effect; no awards certified"},
        "linked_problems": [
            {"problem": "Local input disruption", "mechanism": "Supplier → buyer → further buyers", "status": "modeled supply graph"},
            {"problem": "Lost upstream orders", "mechanism": "Storefront demand loss → suppliers", "status": "reverse supply traversal"},
            {"problem": "Loss of worker demand", "mechanism": "Employer block → storefront → upstream suppliers", "status": "requires cloud footfall data"},
            {"problem": "Debt pressure", "mechanism": "Exposed business → loan → lender", "status": "requires address-checked SBA matches; not a closure forecast"},
            {"problem": "Essential-service access", "mechanism": "Affected food, health and community-service locations → residents", "status": "industry exposure proxy; resident counts require catchment data"},
        ],
    }
    output = ROOT / "data/task_2_3_review.json"
    output.write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")
    band = [r for r in ranking if r["cascade_case"]]
    text = ["# Task 2 and 3 — reproducible review", "", f"Registry as of {as_of}; {len(nodes)} locations; {len(edges)} modeled supply edges.",
            "", "## Findings", "",
            f"- Legacy name-based dedup retained {len(legacy)} locations; this review preserves all {len(nodes)} matched registry locations.",
            f"- {len(changes)} tenure-year/NAICS differences from the legacy summary; see the JSON audit for each record.",
            f"- {len(collisions)} same-name groups retained with their different IDs and addresses.",
            f"- {len(same_site)} groups share the same name, legal name and address. These are flagged potential duplicate filings; distinct IDs are preserved pending source resolution. Counts are registry records, not proven unique firms/storefronts.",
            f"- {len(band)} suppliers are in the 5–25 unique-business, two-hop cascade band; this is a policy shortlist, not an award.",
            f"- Rates: {report['audit']['rates_status']}. No legacy prior is substituted.",
            "- The saved notebook's 8 'trusted' loans included one with no street number. Strict address matching retains only the 7 same-street-address rows in that saved run; rerun to refresh counts.",
            "- The saved SF holdout gives graph-feature AUC 0.695 vs 0.700 baseline (delta −0.005, 95% interval −0.018 to +0.007). No predictive improvement is established.",
            "- Hub reach versus charge-off risk: saved Spearman rho −0.14, p=0.33 across 47 industries. Failure likelihood and graph consequence remain separate.",
            "- The saved SBA population dropped 18,698 individual/sole-proprietor loans. Its priors do not establish risk for unbanked or excluded sole proprietors. Missing SBA history is unknown, not zero need.",
            "", "## Depth sensitivity", "", "| Hops | Median reach | Maximum reach | Roots gaining new nodes |", "|---:|---:|---:|---:|"]
    text += [f"| {d['hop']} | {d['median_reach']:g} | {d['max_reach']} | {d['roots_gaining_new_nodes']} |" for d in depth]
    text += ["", "Counts are distinct destinations excluding the seed; cycles and repeated paths do not create additional businesses. Hops 3–8 are sensitivity/exploration, not longer-range proof of failure.",
             "", "## Industry variety", "", "| Group | Locations |", "|---|---:|"]
    text += [f"| {k} | {v} |" for k,v in sorted(report["industry_variety"]["counts"].items(), key=lambda kv: -kv[1])]
    text += ["", "## Linked community problems", ""]
    text += [f"The cascade shortlist covers {report['shortlist_variety']['industry_groups']} groups. Food Services is {report['shortlist_variety']['shares'].get('Food Services',0):.1%} of the shortlist versus {report['industry_variety']['shares'].get('Food Services',0):.1%} of source records. Retail and health/access cases must be reviewed separately; this supply-only shortlist cannot represent the whole grant portfolio.", ""]
    text += [f"- **{p['problem']}**: {p['mechanism']}. Evidence: {p['status']}." for p in report["linked_problems"]]
    text += ["", "## Limits and next execution", "",
             "The raw registry snapshot is current, but the cohort is inherited from existing local files. It is not a fresh citywide sample. Supply links and buyer input options are modeled. No local employer/ACS tables or canonical 337-row failure-rate export are present. Run the updated notebook in the authenticated BigQuery environment, then rebuild this review with `--rates data/industry_failure_rates.csv`. Historical charge-off does not prove a business is currently insolvent. SBA median jobs are industry loan-cohort statistics, not measured jobs at these storefronts.",
             "", "Source: https://data.sf.gov/resource/g8m3-pdis.json; SF categories: https://sftreasurer.org/business-activities-naics-codes."]
    (ROOT / "data/TASK_2_3_REVIEW.md").write_text("\n".join(text)+"\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rates", type=Path, default=ROOT / "data/industry_failure_rates.csv")
    args = parser.parse_args()
    report = build(args.rates)
    print(json.dumps({"locations": len(report["nodes"]), "modeled_edges": len(report["edges"]),
                      "depth_sensitivity": report["depth_sensitivity"], "audit": {k:v for k,v in report["audit"].items()
                      if k not in ("source_corrections", "name_collisions_preserved", "non_specific_codes")}}, indent=2))
