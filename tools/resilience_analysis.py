"""Auditable corridor consequences. Reach is exposure, never predicted closure/jobs saved.

Supply links are modeled. Registry locations/dates are observed. SBA charge-off
priors must come from Challenge3.ipynb, never the legacy hand-entered CSV.
"""
from __future__ import annotations

import math
import re
from collections import Counter, defaultdict, deque
from datetime import date

MAX_HOPS = 8
NONSTANDARD_FOUR_DIGIT = {"4445", "5471", "5400", "3100", "4400", "7210", "7220"}


def industry_type(code):
    code = str(code or "")
    for prefixes, label in [
        (("721",), "Accommodations"), (("722",), "Food Services"),
        (("54",), "Professional, Scientific, and Technical Services"),
        (("44", "45"), "Retail Trade"), (("81",), "Certain Services"),
        (("61", "62"), "Private Education and Health Services"),
        (("51",), "Information"), (("31", "32", "33"), "Manufacturing"),
        (("71",), "Arts, Entertainment and Recreation"),
    ]:
        if code.startswith(prefixes):
            return label
    return "Unspecified / other"


def naics_detail(code):
    """Preserve source precision. Invalid-looking detail falls back only to its sector."""
    raw = str(code or "").strip()
    digits = raw if re.fullmatch(r"\d{2,6}", raw) else ""
    prefix = digits[:4]
    specific = len(prefix) == 4 and prefix not in NONSTANDARD_FOUR_DIGIT and not prefix.endswith("00")
    return {"naics": raw, "naics4": prefix, "naics2": digits[:2],
            "naics_resolution": "four_digit" if specific else "sector_or_unresolved",
            "model_naics": digits if specific else digits[:2],
            "industry_type": industry_type(digits)}


def registry_nodes(records, as_of):
    """Location IDs are keys; same-name branches remain separate nodes."""
    seen = set()
    nodes = []
    for record in sorted(records, key=lambda r: (r["ttxid"], r["uniqueid"])):
        bid = str(record["ttxid"])
        if bid in seen:
            raise ValueError(f"Duplicate registry location key {bid}; resolve ownership records explicitly")
        seen.add(bid)
        if record.get("location_end_date"):
            continue
        point = record.get("location", {}).get("coordinates", [])
        start = str(record.get("location_start_date", ""))[:10]
        start_date = date.fromisoformat(start) if start else None
        nodes.append({"business_id": bid, "name": record.get("dba_name") or record.get("ownership_name"),
                      "legal_name": record.get("ownership_name", ""),
                      "address": record.get("full_business_address", ""),
                      "corridor": record.get("business_corridor", ""),
                      "latitude": float(point[1]) if len(point) == 2 else None,
                      "longitude": float(point[0]) if len(point) == 2 else None,
                      "location_start_date": start or None,
                      "registration_year": start_date.year if start_date else None,
                      "tenure_years": round((as_of - start_date).days / 365.2425, 2) if start_date else None,
                      "tenure_source": "SF registry location_start_date",
                      "registry_as_of": record.get("data_as_of", "")[:10],
                      **naics_detail(record.get("self_reported_naics_code", ""))})
    return nodes


def distance_m(a, b):
    p1, p2 = math.radians(float(a["latitude"])), math.radians(float(b["latitude"]))
    h = math.sin((p2-p1)/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(
        math.radians(float(b["longitude"])-float(a["longitude"]))/2)**2
    return 12742000 * math.asin(math.sqrt(min(1, h)))


def model_supply_edges(nodes, coefficients, floor=0.015, max_metres=500, max_suppliers=5):
    """BEA prefix match, strongest pair, walking cutoff, top-k per buyer.

    Parameters deliberately differ from the starter's 0.005 / 1200m. Report both
    variants; neither is an observed vendor relationship. Broad NAICS values are
    matched only at their reported sector precision.
    """
    pairs = {}
    reach = defaultdict(set)
    for r in coefficients:
        value = float(r["coefficient"])
        if value >= floor:
            key = (r["supplier_naics4"], r["buyer_naics4"])
            pairs[key] = max(value, pairs.get(key, 0))
            reach[key[0]].add(key[1])
    sizes = sorted(len(v) for v in reach.values())
    pos = (len(sizes)-1)*0.90
    cutoff = sizes[int(pos)] + (sizes[math.ceil(pos)]-sizes[int(pos)])*(pos-int(pos)) if sizes else 0
    generic = {k for k, v in reach.items() if len(v) > cutoff}
    keys = {n["business_id"]: [n["model_naics"][:k] for k in range(2, len(n["model_naics"])+1)] for n in nodes}
    edges = []
    for buyer in nodes:
        candidates = []
        for supplier in nodes:
            if buyer["business_id"] == supplier["business_id"]:
                continue
            value = max((pairs.get((s, b), 0) for s in keys[supplier["business_id"]]
                         if s not in generic for b in keys[buyer["business_id"]]), default=0)
            if value <= 0 or any(n["latitude"] is None or n["longitude"] is None for n in (supplier, buyer)):
                continue
            metres = distance_m(supplier, buyer)
            if metres <= max_metres:
                candidates.append({"supplier_id": supplier["business_id"], "buyer_id": buyer["business_id"],
                                   "intensity": value, "metres": metres, "provenance": "MODELED: BEA + distance"})
        candidates.sort(key=lambda e: (-e["intensity"], e["metres"], e["supplier_id"]))
        edges.extend(candidates[:max_suppliers])
    return edges


class CorridorGraph:
    def __init__(self, nodes, edges, decay_metres=400, alternative_metres=500):
        self.nodes = {str(n["business_id"]): n for n in nodes}
        if len(self.nodes) != len(nodes):
            raise ValueError("Duplicate business IDs multiply paths")
        self.edges, self.adj, self.reverse = [], defaultdict(list), defaultdict(list)
        seen = set()
        for raw in edges:
            e = dict(raw)
            a, b = str(e["supplier_id"]), str(e["buyer_id"])
            if a not in self.nodes or b not in self.nodes:
                raise ValueError(f"Orphan edge {a} -> {b}")
            if (a, b) in seen or a == b:
                raise ValueError(f"Duplicate/self supply edge {a} -> {b}")
            seen.add((a, b))
            w, metres = float(e["intensity"]), float(e["metres"])
            if not math.isfinite(w) or not 0 < w <= 1 or not math.isfinite(metres) or metres < 0:
                raise ValueError("Edge intensity must be in (0,1], distance finite and nonnegative")
            e.update(supplier_id=a, buyer_id=b, intensity=w, metres=metres,
                     decayed_intensity=w*math.exp(-metres/decay_metres))
            self.edges.append(e)
            self.adj[a].append(e)
            self.reverse[b].append(e)
        self.edges.sort(key=lambda e: (e["supplier_id"], e["buyer_id"]))
        for adjacency in (self.adj, self.reverse):
            for values in adjacency.values():
                values.sort(key=lambda e: (e["supplier_id"], e["buyer_id"]))
        # Buyer-side modeled options for the same input industry. A corridor-wide
        # peer count is reported separately and is never called substitutability.
        for e in self.edges:
            supplier = self.nodes[e["supplier_id"]]
            precise = supplier.get("naics_resolution", "four_digit") == "four_digit"
            options = {x["supplier_id"] for x in self.reverse[e["buyer_id"]]
                       if x["supplier_id"] != e["supplier_id"] and precise
                       and self.nodes[x["supplier_id"]].get("naics4") == supplier.get("naics4")
                       and x["metres"] <= alternative_metres}
            e["buyer_input_alternatives"] = len(options)
            e["adjusted_weight"] = e["decayed_intensity"]/(1+len(options))

    def trace(self, root, max_hops=2, direction="downstream", decay=True):
        if root not in self.nodes:
            raise ValueError("Unknown root business")
        if not isinstance(max_hops, int) or not 1 <= max_hops <= MAX_HOPS:
            raise ValueError(f"max_hops must be an integer in 1..{MAX_HOPS}")
        if direction not in ("downstream", "upstream"):
            raise ValueError("direction must be downstream or upstream")
        adjacency = self.adj if direction == "downstream" else self.reverse
        target_key = "buyer_id" if direction == "downstream" else "supplier_id"
        depths, paths, queue = {root: 0}, {root: [root]}, deque([root])
        while queue:
            current = queue.popleft()
            if depths[current] >= max_hops:
                continue
            for e in adjacency[current]:
                nxt = e[target_key]
                if nxt not in depths:
                    depths[nxt] = depths[current]+1
                    paths[nxt] = paths[current]+[nxt]
                    queue.append(nxt)
        # Bounded maximum-product propagation. Keep the strongest exposure per
        # destination, rather than summing repeated paths or treating it as a risk.
        best = {(root, 0): 1.0}
        evidence = {(root, 0): [root]}
        for hop in range(1, max_hops+1):
            for (current, depth), weight in list(best.items()):
                if depth != hop-1:
                    continue
                for e in adjacency[current]:
                    nxt = e[target_key]
                    if nxt == root:
                        continue
                    ew = (e["decayed_intensity"] if decay else e["intensity"])/(1+e["buyer_input_alternatives"])
                    candidate = weight*ew
                    if candidate > best.get((nxt, hop), -1):
                        best[nxt, hop] = candidate
                        evidence[nxt, hop] = evidence[current, depth]+[nxt]
        endpoints = []
        for bid, hop in sorted(depths.items(), key=lambda x: (x[1], x[0])):
            if bid == root:
                continue
            states = [(v, d) for (n, d), v in best.items() if n == bid]
            weight, d = max(states, key=lambda x: (x[0], -x[1]))
            endpoints.append({"business_id": bid, "hop": hop, "path": paths[bid],
                              "weighted_exposure": weight, "weight_path": evidence[bid, d],
                              "industry_type": self.nodes[bid]["industry_type"]})
        profile = [{"hop": h, "new_businesses": sum(e["hop"] == h for e in endpoints),
                    "cumulative_businesses": sum(e["hop"] <= h for e in endpoints)} for h in range(1, max_hops+1)]
        return {"root": root, "max_hops": max_hops, "direction": direction,
                "counting_unit": "Distinct registry location IDs; potential co-located duplicate filings require source review",
                "reach": len(endpoints), "weighted_exposure": sum(e["weighted_exposure"] for e in endpoints),
                "industries": dict(Counter(e["industry_type"] for e in endpoints)),
                "profile": profile, "endpoints": endpoints,
                "saturated": len(endpoints) >= 0.8*max(1, len(self.nodes)-1)}


def industry_variety(nodes, selected_ids=None):
    selected = nodes if selected_ids is None else [n for n in nodes if n["business_id"] in set(selected_ids)]
    counts = Counter(n["industry_type"] for n in selected)
    n = len(selected)
    shares = {k: v/n for k, v in counts.items()} if n else {}
    return {"businesses": n, "industry_groups": len(counts), "counts": dict(counts),
            "shares": shares, "hhi": sum(v*v for v in shares.values()),
            "largest_share": max(shares.values(), default=0)}


def lookup_failure_rate(node, rates):
    for level, code in [("naics4", node["naics4"]), ("naics2", node["naics4"][:2]), ("state", "CA")]:
        if level == "naics4" and node.get("naics_resolution") != "four_digit":
            continue
        matches = [r for r in rates if r["level"] == level and str(r["code"]) == code]
        if len(matches) > 1:
            raise ValueError(f"Duplicate canonical rate {level}/{code}")
        if matches:
            r = matches[0]
            if not r.get("basis") or not r.get("horizon_months"):
                raise ValueError("Canonical rates require notebook basis and horizon")
            probability = float(r["p_fail"])
            if not math.isfinite(probability) or not 0 <= probability <= 1:
                raise ValueError("Canonical charge-off probability must be finite and in [0,1]")
            return {"p_fail": probability, "p_fail_level": level, "basis": r["basis"]}
    return {"p_fail": None, "p_fail_level": "missing", "basis": "Run Challenge3.ipynb to export canonical rates"}


def grant_scenario(p_fail, grant, monthly_debt, max_reduction=0.25, bridge_months=3):
    """Debt bridge sensitivity, not estimated causal effectiveness or total cash runway."""
    if grant < 0 or not 0 <= max_reduction <= 1 or bridge_months <= 0:
        raise ValueError("Invalid grant scenario")
    if p_fail is None or monthly_debt is None or monthly_debt <= 0:
        return {"risk_reduction": None, "months_of_debt_covered": None, "status": "insufficient verified debt/risk data"}
    coverage = grant/monthly_debt
    return {"risk_reduction": p_fail*max_reduction*min(coverage/bridge_months, 1),
            "months_of_debt_covered": coverage, "status": "ASSUMED debt-service bridge; excludes operating costs"}


def rank_consequences(graph, rates=(), grant=8000, debt_by_id=None):
    rows = []
    for bid, node in graph.nodes.items():
        raw, adjusted = graph.trace(bid, 2, decay=False), graph.trace(bid, 2)
        rate = lookup_failure_rate(node, rates)
        p = rate["p_fail"]
        band = 5 <= adjusted["reach"] <= 25
        scenario = grant_scenario(p, grant, (debt_by_id or {}).get(bid))
        rows.append({"business_id": bid, "name": node["name"], "industry_type": node["industry_type"],
                     "reach_2hop": adjusted["reach"], "cascade_case": band,
                     "weighted_before_decay": raw["weighted_exposure"],
                     "weighted_after_decay": adjusted["weighted_exposure"], **rate,
                     "old_expected_exposed": None if p is None else p*adjusted["reach"],
                     "new_expected_exposure": None if p is None else p*adjusted["weighted_exposure"],
                     "grant_scenario": scenario,
                     "scenario_protected_exposure": None if scenario["risk_reduction"] is None else
                        scenario["risk_reduction"]*adjusted["weighted_exposure"]})
    # All businesses participate in distance sensitivity; keystone selection is a separate column.
    for field, rank in [("weighted_before_decay", "rank_before_decay"), ("weighted_after_decay", "rank_after_decay")]:
        for pos, row in enumerate(sorted(rows, key=lambda r: (-r[field], r["business_id"])), 1):
            row[rank] = pos
    return sorted(rows, key=lambda r: (not r["cascade_case"], -r["weighted_after_decay"], r["business_id"]))


def _load_corridor_review():
    import json
    from pathlib import Path
    path = Path(__file__).resolve().parents[1]/"data/task_2_3_review.json"
    return json.loads(path.read_text())


def _normalize_business_name(value):
    import unicodedata
    return re.sub(r"[^\w]+", "", unicodedata.normalize("NFKC", value).casefold())


def _business_identity(node):
    return {key: node.get(key) for key in ("business_id", "name", "legal_name", "address", "naics4")}


def _find_registry_businesses(nodes, query):
    """Exact IDs/names first; partial matches are suggestions, never selected roots."""
    query = query.strip()
    exact_ids = [n for n in nodes if str(n["business_id"]).casefold() == query.casefold()]
    if exact_ids:
        return exact_ids, "business_id"
    normalized = _normalize_business_name(query)
    if not normalized:
        return [], None
    for field in ("name", "legal_name"):
        matches = [n for n in nodes if _normalize_business_name(n.get(field) or "") == normalized]
        if matches:
            return matches, field
    matches = [n for n in nodes if any(
        normalized in _normalize_business_name(str(n.get(field) or ""))
        for field in ("business_id", "name", "legal_name", "address"))]
    return matches, "partial" if matches else None


def _scenario_business(query):
    """Identify fixture IDs to explain their namespace, without treating them as registry keys."""
    if not re.fullmatch(r"cm_\d+", query.strip(), re.I):
        return None
    from tools.scoring_engine import CANONICAL_CENTRAL_MARKET_APPLICANTS
    return next((a for a in CANONICAL_CENTRAL_MARKET_APPLICANTS
                 if a["id"].casefold() == query.strip().casefold()), None)


def find_corridor_businesses(query: str = "", limit: int = 10) -> dict:
    """Find real local registry IDs before tracing a business.

    Search by ID, business/legal name, or address. Empty query lists available
    locations. Return separate candidates for same-name branches; use their
    business_id to select a location. cm_* IDs belong to an illustrative scenario,
    not this registry graph; any same-name registry results require explicit selection.
    """
    if not isinstance(query, str) or type(limit) is not int or not 1 <= limit <= 50:
        return {"status": "INVALID_ARGUMENT", "message": "query must be text and limit an integer in 1..50."}
    data = _load_corridor_review()
    scenario = _scenario_business(query)
    search = scenario["name"] if scenario else query
    matches, matched_by = _find_registry_businesses(data["nodes"], search) if search.strip() else (data["nodes"], "list")
    matches = sorted(matches, key=lambda n: (n["name"].casefold(), n["business_id"]))
    result = {"status": "SCENARIO_ID" if scenario else "OK" if matches else "UNKNOWN_BUSINESS",
              "query": query, "data_source": "LOCAL_REVIEW", "matched_by": matched_by,
              "total_matches": len(matches), "matches": [_business_identity(n) for n in matches[:limit]],
              "truncated": len(matches) > limit,
              "message": "Select a registry business_id and call analyze_corridor_impact. Same-name locations remain separate."}
    if scenario:
        result.update(scenario_business={k: scenario.get(k) for k in ("id", "name", "address")},
                      message="This is an illustrative scenario ID, not a registry ID. Same-name matches are candidates only; choose a registry business_id explicitly for source analysis.")
    return result


def analyze_corridor_impact(business_id: str, max_hops: int = 2, direction: str = "downstream") -> dict:
    """Trace a local registry location through 1–8 modeled supply hops.

    business_id should be a registry location ID from find_corridor_businesses;
    a unique exact business/legal name also works. cm_* scenario IDs, unknown IDs,
    partial names and ambiguous branches return a status/message and candidates,
    without tracing a guessed business. Check status == OK before using reach.
    Returns distinct exposure, paths, industry variety and gaps, never job savings.
    """
    if not isinstance(business_id, str) or not business_id.strip():
        return {"status": "INVALID_ARGUMENT", "message": "business_id must be a nonempty registry ID or exact business name. Use find_corridor_businesses to look it up."}
    if type(max_hops) is not int or not 1 <= max_hops <= MAX_HOPS:
        return {"status": "INVALID_ARGUMENT", "message": f"max_hops must be an integer in 1..{MAX_HOPS}."}
    if not isinstance(direction, str) or direction.strip().casefold() not in ("downstream", "upstream"):
        return {"status": "INVALID_ARGUMENT", "message": "direction must be downstream or upstream."}
    direction = direction.strip().casefold()
    lookup = find_corridor_businesses(business_id)
    matches = lookup["matches"]
    if lookup["status"] == "SCENARIO_ID" or lookup["matched_by"] == "partial" or lookup["total_matches"] != 1:
        status = ("SCENARIO_ID" if lookup["status"] == "SCENARIO_ID" else
                  "AMBIGUOUS_BUSINESS" if lookup["matched_by"] != "partial" and lookup["total_matches"] > 1 else
                  "UNKNOWN_BUSINESS")
        message = (lookup["message"] if status == "SCENARIO_ID" else
                   "Multiple registry locations share that name. Choose a business_id using its address." if status == "AMBIGUOUS_BUSINESS" else
                   "No exact registry ID or name matched. Use find_corridor_businesses, then select a registry business_id; partial matches below are suggestions only.")
        return {**lookup, "status": status, "requested_business": business_id,
                "message": message, "max_hops": max_hops, "direction": direction}
    data = _load_corridor_review()
    graph = CorridorGraph(data["nodes"], data["edges"])
    root = matches[0]["business_id"]
    return {**graph.trace(root, max_hops, direction), "status": "OK",
            "requested_business": business_id, "root_business": matches[0],
            "matched_by": lookup["matched_by"], "data_source": "LOCAL_REVIEW", "provenance": data["model"],
            "linked_problems": data["linked_problems"],
            "evidence_gaps": {k:data["audit"][k] for k in ("rates_status", "loans_status", "footfall_status", "grant_status", "counting_unit")}}


def review_industry_variety() -> dict:
    """Agent tool: compare source cohort and the 5–25 two-hop cascade shortlist."""
    import json
    from pathlib import Path
    data = json.loads((Path(__file__).resolve().parents[1]/"data/task_2_3_review.json").read_text())
    ids = [r["business_id"] for r in data["ranking"] if r["cascade_case"]]
    return {"cohort": industry_variety(data["nodes"]),
            "cascade_shortlist": industry_variety(data["nodes"], ids),
            "selection": "Policy scenario: 5–25 unique destinations at two hops; not funded portfolio"}
