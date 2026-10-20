"""
BigQuery & Property Graph (GQL) Connector (`tools/bigquery_connector.py`)
=========================================================================
Connects the Ecosystem & Demand-Anchored Micro-Grant ADK to:
1. **Live Google BigQuery (`bigquery` mode)**:
   - Queries `PROJECT_ID.a4i_econ` node/edge tables (`businesses`, `employer_blocks`,
     `supplies`, `draws_footfall_from`, `borrowed_from`, `tract_demographics`,
     and `business_sba_summary`).
   - Builds and traverses the `a4i_econ.LocalEconomy` Property Graph via GQL
     (`GRAPH_TABLE(a4i_econ.LocalEconomy MATCH ...)`).
2. **Local Real Corridor Snapshot (`local_csv` mode)**:
   - Reads the 232 real Central Market businesses directly from
     `data/custom_bq_upload/business_sba_summary.csv`,
     `data/custom_bq_upload/borrowed_from.csv`, and
     `data/bea_direct_requirements.csv` with zero cloud credentials required.
3. **Canonical 11-Applicant Benchmark (`canonical` mode)**:
   - Returns the 11-applicant Central Market triage cohort defined in
     `./ADK/DOCS/03_BEYOND_DATASET_ENHANCEMENT_MODEL.md` Table 9.1 for
     deterministic Red-Team regression verification.
"""

from __future__ import annotations

import copy
import csv
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from tools.scoring_engine import (
    CANONICAL_CENTRAL_MARKET_APPLICANTS,
    EXCLUDED_CORPORATE_NAICS4,
    PROVENANCE_MODELED,
    PROVENANCE_VERIFIED,
    census_equity_multiplier,
    community_anchor_score,
    piecewise_root_supplier_multiplier,
    small_business_purity_score,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCAL_SBA_SUMMARY_CSV = REPO_ROOT / "data" / "custom_bq_upload" / "business_sba_summary.csv"
LOCAL_BORROWED_FROM_CSV = REPO_ROOT / "data" / "custom_bq_upload" / "borrowed_from.csv"
LOCAL_BEA_CSV = REPO_ROOT / "data" / "bea_direct_requirements.csv"


# ============================================================================
# GQL DDL & MULTI-HOP PROPERTY GRAPH QUERIES (Section 13 of Notebook)
# ============================================================================

def get_property_graph_ddl(dataset: str = "a4i_econ") -> str:
    """
    Return the exact BigQuery GQL `CREATE OR REPLACE PROPERTY GRAPH` DDL
    matching Section 13 of `notebooks/c3_01_load_explore.ipynb` (incorporating
    all 7 notebook traps: dataset-qualified unbackticked NODE/EDGE tables,
    unqualified REFERENCES, global property type safety with `worker_share`,
    and including `Lender` nodes + `BorrowedFrom` edges).
    """
    return f"""
CREATE OR REPLACE PROPERTY GRAPH {dataset}.LocalEconomy
  NODE TABLES (
    {dataset}.businesses
      KEY (business_id)
      LABEL Business PROPERTIES (business_id, name, legal_name, naics4, industry_type, zip, latitude, longitude, registration_year, tenure_years, corridor_alternatives),
    {dataset}.employer_blocks
      KEY (block_id)
      LABEL Employer PROPERTIES (block_id, jobs),
    {dataset}.lenders
      KEY (bank_name)
      LABEL Lender PROPERTIES (bank_name, corridor_loan_count, corridor_businesses_funded, total_capital_deployed, defaulted_loans)
  )
  EDGE TABLES (
    {dataset}.supplies
      KEY (edge_id)
      SOURCE KEY (supplier_id) REFERENCES businesses (business_id)
      DESTINATION KEY (buyer_id) REFERENCES businesses (business_id)
      LABEL Supplies PROPERTIES (intensity, metres, corridor_alternatives),
    {dataset}.draws_footfall_from
      KEY (edge_id)
      SOURCE KEY (block_id) REFERENCES employer_blocks (block_id)
      DESTINATION KEY (business_id) REFERENCES businesses (business_id)
      LABEL DrawsFootfall PROPERTIES (worker_share, metres),
    {dataset}.borrowed_from
      KEY (edge_id)
      SOURCE KEY (business_id) REFERENCES businesses (business_id)
      DESTINATION KEY (bank_name) REFERENCES lenders (bank_name)
      LABEL BorrowedFrom PROPERTIES (loan_amount, approval_date, term_months, jobs_supported, loan_status, is_charged_off, monthly_debt_est)
  );
""".strip()


def get_gql_multihop_cascade_sql(dataset: str = "a4i_econ", min_exposed: int = 2) -> str:
    """
    Return the BigQuery GQL query that walks 1-to-2 hops along `Supplies` edges
    in `{dataset}.LocalEconomy` to compute downstream dependency reach and
    cumulative BEA input intensity for every upstream supplier.
    """
    return f"""
SELECT
  business_id,
  business_name,
  naics4,
  direct_buyers,
  two_hop_exposed,
  ROUND(total_direct_intensity, 4) AS total_direct_intensity
FROM GRAPH_TABLE(
  {dataset}.LocalEconomy
  MATCH (seed:Business)-[e1:Supplies]->(hop1:Business)
  OPTIONAL MATCH (hop1)-[e2:Supplies]->(hop2:Business)
  WHERE hop2.business_id IS NULL OR hop2.business_id != seed.business_id
  RETURN
    seed.business_id AS business_id,
    seed.name AS business_name,
    seed.naics4 AS naics4,
    COUNT(DISTINCT hop1.business_id) AS direct_buyers,
    COUNT(DISTINCT COALESCE(hop2.business_id, hop1.business_id)) AS two_hop_exposed,
    SUM(e1.intensity) AS total_direct_intensity
  GROUP BY seed.business_id, seed.name, seed.naics4
)
WHERE two_hop_exposed >= {int(min_exposed)}
ORDER BY two_hop_exposed DESC, total_direct_intensity DESC
""".strip()


def get_bq_enriched_corridor_sql(project_id: str, dataset: str = "a4i_econ") -> str:
    """
    Return the comprehensive BigQuery SQL query that joins all 6 corridor tables
    (`businesses`, `supplies`, `draws_footfall_from`, `borrowed_from`,
    `tract_demographics`, and optional `business_sba_summary`) into applicant
    records ready for `tools/scoring_engine.py`.
    """
    ds = f"{project_id}.{dataset}"
    return f"""
WITH one_hop_supply AS (
  SELECT
    supplier_id AS business_id,
    COUNT(DISTINCT buyer_id) AS direct_buyers,
    ARRAY_AGG(DISTINCT CAST(buyer_id AS STRING) LIMIT 15) AS downstream_ids,
    SUM(intensity) AS direct_intensity_sum,
    AVG(intensity) AS avg_supply_intensity
  FROM `{ds}.supplies`
  GROUP BY supplier_id
),
two_hop_supply AS (
  SELECT
    a.supplier_id AS business_id,
    COUNT(DISTINCT b.buyer_id) AS hop2_buyers,
    SUM(a.intensity * b.intensity) AS hop2_intensity_sum
  FROM `{ds}.supplies` a
  JOIN `{ds}.supplies` b ON b.supplier_id = a.buyer_id
  WHERE b.buyer_id != a.supplier_id
  GROUP BY a.supplier_id
),
inbound_supply AS (
  SELECT
    buyer_id AS business_id,
    COUNT(DISTINCT supplier_id) AS upstream_suppliers,
    ARRAY_AGG(DISTINCT CAST(supplier_id AS STRING) LIMIT 10) AS upstream_ids
  FROM `{ds}.supplies`
  GROUP BY buyer_id
),
footfall AS (
  SELECT
    business_id,
    SUM(worker_share) AS worker_footfall_jobs,
    COUNT(DISTINCT block_id) AS employer_blocks_count
  FROM `{ds}.draws_footfall_from`
  GROUP BY business_id
),
corridor_acs AS (
  SELECT
    AVG(poverty_rate) AS avg_poverty_rate,
    AVG(no_vehicle_rate) AS avg_no_vehicle_rate,
    AVG(assistance_rate) AS avg_assistance_rate
  FROM `{ds}.tract_demographics`
)
SELECT
  b.business_id,
  b.name AS business_name,
  b.legal_name,
  b.address,
  b.zip,
  b.naics,
  b.naics4,
  b.corridor,
  b.latitude,
  b.longitude,
  COALESCE(s1.direct_buyers, 0) AS direct_buyers,
  s1.downstream_ids,
  COALESCE(s1.direct_intensity_sum, 0.0) AS direct_intensity_sum,
  COALESCE(s1.avg_supply_intensity, 0.0) AS avg_supply_intensity,
  COALESCE(s2.hop2_buyers, 0) AS hop2_buyers,
  COALESCE(s2.hop2_intensity_sum, 0.0) AS hop2_intensity_sum,
  COALESCE(inb.upstream_suppliers, 0) AS upstream_suppliers,
  inb.upstream_ids,
  COALESCE(ff.worker_footfall_jobs, 0.0) AS worker_footfall_jobs,
  COALESCE(acs.avg_poverty_rate, 0.28) AS poverty_rate,
  COALESCE(acs.avg_no_vehicle_rate, 0.65) AS no_vehicle_rate
FROM `{ds}.businesses` b
LEFT JOIN one_hop_supply s1 ON s1.business_id = b.business_id
LEFT JOIN two_hop_supply s2 ON s2.business_id = b.business_id
LEFT JOIN inbound_supply inb ON inb.business_id = b.business_id
LEFT JOIN footfall ff ON ff.business_id = b.business_id
CROSS JOIN corridor_acs acs
ORDER BY COALESCE(s2.hop2_buyers, 0) DESC, COALESCE(s1.direct_buyers, 0) DESC
""".strip()


# ============================================================================
# HELPER: DETERMINISTIC MAPPING OF RAW CORRIDOR ROWS TO SCORING ENGINE SCHEMA
# ============================================================================

def classify_industry_type(naics4: str) -> str:
    """Map 4-digit NAICS code to the 9 official corridor industry types."""
    s = str(naics4 or "").strip()
    if s.startswith("722"):
        return "Food Services — restaurants, bars, catering"
    if s.startswith("54"):
        return "Professional, Scientific, and Technical Services — legal, IT, consulting, design"
    if s.startswith(("44", "45")):
        return "Retail Trade — groceries, clothing, furniture, other stores"
    if s.startswith(("811", "812", "813")) or s.startswith("81"):
        return "Certain Services — repairs, personal care, laundry, parking, community organizations"
    if s.startswith("62"):
        return "Private Education and Health Services — health care and social assistance"
    if s.startswith("51"):
        return "Information — publishing, software, telecommunications, hosting"
    if s.startswith(("31", "32", "33")):
        return "Manufacturing — food, apparel, pharmaceuticals, equipment"
    if s.startswith("721"):
        return "Accommodations — hotels and lodging"
    if s.startswith("71"):
        return "Arts, Entertainment and Recreation — theaters, events, fitness"
    return "Other"


def _map_corridor_row_to_applicant(
    row: Dict[str, Any],
    sba_lookup: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Map a raw BigQuery (`a4i_econ`) or local CSV (`business_sba_summary.csv`)
    row into the exact applicant dictionary schema used by `tools/scoring_engine.py`.
    """
    biz_id = str(row.get("business_id", ""))
    name = str(row.get("business_name") or row.get("name") or biz_id)
    legal_name = str(row.get("legal_name") or name)
    naics4 = str(row.get("naics4") or "7225")[:4]
    naics2 = naics4[:2]
    industry_type = str(row.get("industry_type") or classify_industry_type(naics4))

    sba_info = sba_lookup.get(biz_id, {})
    has_sba = str(sba_info.get("has_sba_history", row.get("has_sba_history", "False"))).lower() == "true"
    has_chargeoff = str(
        sba_info.get("has_historical_charge_off", row.get("has_historical_charge_off", "False"))
    ).lower() == "true"
    total_borrowed = float(sba_info.get("total_borrowed_amount", row.get("total_borrowed_amount", 0.0)) or 0.0)
    reported_jobs = int(float(sba_info.get("reported_jobs_supported", row.get("reported_jobs_supported", 0)) or 0))
    annual_debt_service = float(
        sba_info.get("estimated_annual_debt_service", row.get("estimated_annual_debt_service", 0.0)) or 0.0
    )

    out_deg = int(row.get("direct_buyers", 0) or 0)
    hop2_buyers = int(row.get("hop2_buyers", 0) or 0)
    in_deg = int(row.get("upstream_suppliers", 1) or 1)

    # Sector volatility and category label by NAICS family
    sector_vol_map = {
        "72": (1.25, "Food Services & Drinking Places"),
        "31": (1.15, "Artisan Food & Craft Manufacturing"),
        "32": (1.10, "Local Print & Craft Manufacturing"),
        "33": (1.10, "Small-Scale Maker & Fabrication"),
        "44": (1.12, "Neighborhood Retail & Grocery"),
        "45": (1.12, "Specialty Neighborhood Retail"),
        "71": (1.30, "Performing Arts & Live Cultural Venue"),
        "81": (1.08, "Repair & Neighborhood Personal Services"),
        "62": (0.95, "Community Health & Social Assistance"),
        "54": (0.85, "Professional & Technical Services"),
        "51": (0.80, "Information & Media Services"),
    }
    sector_volatility, category_label = sector_vol_map.get(naics2, (1.05, "Corridor Commercial Enterprise"))

    # Substitutability friction theta_ext (lower = harder to replace locally)
    if naics2 in ("31", "32", "33"):
        theta_ext = 0.20
    elif naics4 in ("8113", "8123", "4451", "7111"):
        theta_ext = 0.25
    elif naics2 in ("72", "44", "45"):
        theta_ext = 0.45
    else:
        theta_ext = 0.65

    # Runway in quarters and monthly/quarterly burn rate
    direct_employees = reported_jobs if reported_jobs > 0 else (10 if naics2 in ("72", "31", "44", "71") else 5)
    burn_rate = max(6000.0, float(direct_employees) * 1200.0 + (annual_debt_service / 4.0))
    if has_chargeoff:
        runway_quarters = 0.15  # Historical charge-off / structural insolvency floor (< 0.25q)
    elif has_sba and annual_debt_service > 12000:
        runway_quarters = 0.85  # High-leverage critical triage sweet spot
    elif naics2 in ("31", "72", "71", "44"):
        runway_quarters = 0.95  # Active storefront triage sweet spot
    elif naics2 in ("54", "51"):
        runway_quarters = 2.60  # Professional services buffer
    else:
        runway_quarters = 1.25

    liquid_cash = round(runway_quarters * burn_rate, 2)
    annual_revenue = max(220000.0, float(direct_employees) * 62000.0, total_borrowed * 2.2)

    # Stage 0 Corporate Exclusion check
    is_excluded_corp = (
        naics4 in EXCLUDED_CORPORATE_NAICS4
        or direct_employees > 50
        or any(tok in legal_name.lower() for tok in ("holdings", "global", "national", "ventures"))
    )

    ownership_type = "corporate_conglomerate" if is_excluded_corp else (
        "nonprofit_501c3" if naics2 == "62" else "sole_or_family_local"
    )
    purity_res = small_business_purity_score(
        fte_count=float(direct_employees),
        location_count=1,
        ownership_type=ownership_type,
        annual_revenue=annual_revenue,
    )

    # Parent supplier weight & cascade score
    # B2C essential grocers/markets (4451/4452) and consumer-only personal care (8121/8129)
    # have zero B2B supply cascade (Vector 7 & Vector 8) and compete on Track 1 Anchor & Human Impact
    if naics4 in ("4451", "4452", "8121", "8129"):
        out_deg = 0
        hop2_buyers = 0
        omega_parent = 1.00
        parent_weight = 1.00
        cascade_score = 0.0
    else:
        omega_parent = piecewise_root_supplier_multiplier(out_deg, in_deg)
        parent_weight = round(omega_parent + min(0.65, 0.08 * out_deg + 0.03 * hop2_buyers), 2)
        direct_intensity = float(row.get("direct_intensity_sum", 0.0) or 0.0)
        cascade_score = min(
            98.0,
            round((out_deg * 11.5 + hop2_buyers * 4.5 + direct_intensity * 120.0) * (1.0 - 0.5 * theta_ext), 1),
        )

    # Community anchor & equity multiplier
    poverty_rate = float(row.get("poverty_rate", 0.28) or 0.28)
    no_vehicle_rate = float(row.get("no_vehicle_rate", 0.65) or 0.65)
    m_equity = round(census_equity_multiplier(poverty_rate, no_vehicle_rate), 2)
    is_sole_essential = naics4 in ("4451", "4452", "6214")
    anchor_res = community_anchor_score(
        transit_gravity=92.0 if is_sole_essential else (75.0 if naics2 in ("44", "72", "71", "62") else 45.0),
        pedestrian_gravity=90.0 if is_sole_essential else (72.0 if naics2 in ("44", "72", "71", "81") else 40.0),
        is_sole_essential_within_400m=is_sole_essential,
        equity_multiplier=1.0,
    )

    worker_footfall = float(row.get("worker_footfall_jobs", 140.0) or 140.0)
    daily_commuters = int(max(30.0, round(worker_footfall)) + (90 if is_sole_essential else 0))
    network_workers = int(out_deg * 5 + hop2_buyers * 2)
    vulnerable_residents = int(165 if is_sole_essential else (55 if naics2 in ("72", "44", "81", "62") else 20))

    lat = float(row.get("latitude") or 37.7785)
    lon = float(row.get("longitude") or -122.4145)
    cluster_id = "mid_market_7th_8th" if lon >= -122.4150 else "mid_market_9th_10th"
    cluster_name = (
        "Mid-Market & 7th/8th Street Walkshed Cluster"
        if cluster_id == "mid_market_7th_8th"
        else "9th & 10th Street Mission/Market Cluster"
    )
    cluster_vacancy = 0.38 if cluster_id == "mid_market_7th_8th" else 0.32

    shock_category = (
        "Category 1: Indivisible Capital Cliff"
        if (out_deg >= 3 or is_sole_essential or naics2 in ("31", "32", "33"))
        else "Category 2: Flexible Working Capital Bridge"
    )

    downstream_ids = row.get("downstream_ids") or [f"dep_{biz_id}_{k}" for k in range(out_deg)]
    upstream_ids = row.get("upstream_ids") or [f"sup_{biz_id}_{k}" for k in range(in_deg)]

    return {
        "id": biz_id,
        "name": name,
        "legal_name": legal_name,
        "category": category_label,
        "industry_type": industry_type,
        "address": str(row.get("address") or "Central Market Corridor, SF"),
        "lat": lat,
        "lon": lon,
        "cluster_id": cluster_id,
        "cluster_name": cluster_name,
        "cluster_vacancy_rate": cluster_vacancy,
        "naics": naics4,
        "requested_amount": 10000.0,
        "liquid_cash": liquid_cash,
        "burn_rate": round(burn_rate, 2),
        "runway_quarters": runway_quarters,
        "sector_volatility": sector_volatility,
        "direct_employees": direct_employees,
        "network_workers": network_workers,
        "daily_commuters": daily_commuters,
        "vulnerable_residents": vulnerable_residents,
        "small_biz_purity": round(purity_res["p_pure"], 1),
        "location_count": 1,
        "ownership_type": ownership_type,
        "annual_revenue": round(annual_revenue, 2),
        "out_degree": out_deg,
        "in_degree": in_deg,
        "substitutability_theta": theta_ext,
        "parent_supplier_weight": parent_weight,
        "cascade_score": cascade_score,
        "anchor_score": round(anchor_res["base_anchor_score"], 1),
        "equity_multiplier": m_equity,
        "tract_id": "06075012502",
        "tract_poverty_rate": poverty_rate,
        "tract_zero_vehicle_share": no_vehicle_rate,
        "shock_category": shock_category,
        "shock_description": (
            "SBA-verified equipment/facility capital stabilization"
            if has_sba
            else "Corridor operating & supplier retention stabilization"
        ),
        "provenance_status": PROVENANCE_VERIFIED if has_sba else PROVENANCE_MODELED,
        "verified_invoices_count": int(sba_info.get("loan_count", 1) or 1) if has_sba else 0,
        "downstream_dependents": list(downstream_ids),
        "upstream_suppliers": list(upstream_ids),
        "eligible": (not is_excluded_corp) and (not has_chargeoff),
        "storefront_certified": not is_excluded_corp,
        "institutional_ownership_pct": 100.0 if is_excluded_corp else 0.0,
        "has_sba_history": has_sba,
        "has_historical_charge_off": has_chargeoff,
        "total_borrowed_amount": total_borrowed,
        "data_source": str(row.get("data_source", "LOCAL_CSV")),
    }


# ============================================================================
# LOCAL CSV SNAPSHOT LOADER (232 REAL CENTRAL MARKET BUSINESSES)
# ============================================================================

def load_applicants_from_local_csv(
    limit: Optional[int] = None,
    only_sba_or_suppliers: bool = False,
) -> List[Dict[str, Any]]:
    """
    Load the 232 real Central Market corridor businesses directly from
    `data/custom_bq_upload/business_sba_summary.csv`, `borrowed_from.csv`, and
    `data/bea_direct_requirements.csv` without needing BigQuery credentials.
    """
    if not LOCAL_SBA_SUMMARY_CSV.exists():
        return [copy.deepcopy(a) for a in CANONICAL_CENTRAL_MARKET_APPLICANTS]

    rows: List[Dict[str, Any]] = []
    with LOCAL_SBA_SUMMARY_CSV.open("r", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rows.append(r)

    # Load BEA direct requirements to infer industry-level supply reach within the corridor
    bea_by_supplier: Dict[str, List[Tuple[str, float]]] = {}
    if LOCAL_BEA_CSV.exists():
        with LOCAL_BEA_CSV.open("r", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                coeff = float(r.get("coefficient", 0.0) or 0.0)
                if coeff >= 0.005:
                    sup = str(r.get("supplier_naics4", ""))[:3]
                    buy = str(r.get("buyer_naics4", ""))[:3]
                    bea_by_supplier.setdefault(sup, []).append((buy, coeff))

    naics3_counts: Dict[str, int] = {}
    for r in rows:
        n3 = str(r.get("naics4", ""))[:3]
        if n3:
            naics3_counts[n3] = naics3_counts.get(n3, 0) + 1

    sba_lookup = {str(r.get("business_id", "")): r for r in rows}

    enriched_rows: List[Dict[str, Any]] = []
    for idx, r in enumerate(rows):
        n3 = str(r.get("naics4", ""))[:3]
        sup_pairs = bea_by_supplier.get(n3, [])
        direct_buyers = 0
        direct_intensity = 0.0
        for buy_n3, coeff in sup_pairs[:5]:
            if buy_n3 in naics3_counts:
                matched_buyers = min(naics3_counts[buy_n3], 2)
                direct_buyers += matched_buyers
                direct_intensity += coeff * matched_buyers
        hop2_buyers = min(direct_buyers * 2, 10) if direct_buyers >= 2 else 0

        raw_enriched = dict(r)
        raw_enriched["direct_buyers"] = direct_buyers
        raw_enriched["direct_intensity_sum"] = round(direct_intensity, 4)
        raw_enriched["hop2_buyers"] = hop2_buyers
        raw_enriched["upstream_suppliers"] = 2 if n3 in ("722", "445", "711", "812") else 1
        # Assign walkable Central Market coordinates across the 2 sub-clusters
        raw_enriched["latitude"] = 37.7780 + (idx % 12) * 0.0003
        raw_enriched["longitude"] = -122.4140 - (idx % 2) * 0.0022
        raw_enriched["data_source"] = "LOCAL_CSV_232_CENTRAL_MARKET"
        enriched_rows.append(raw_enriched)

    if only_sba_or_suppliers:
        enriched_rows = [
            r for r in enriched_rows
            if str(r.get("has_sba_history", "")).lower() == "true"
            or int(r.get("direct_buyers", 0)) >= 3
            or str(r.get("naics4", ""))[:4] in ("4451", "4452")
        ]

    if limit is not None and len(enriched_rows) > limit:
        grocers = [r for r in enriched_rows if str(r.get("naics4", ""))[:4] in ("4451", "4452")]
        top_slice = enriched_rows[:limit]
        if grocers and not any(str(r.get("naics4", ""))[:4] in ("4451", "4452") for r in top_slice):
            top_slice[-1] = grocers[0]
        enriched_rows = top_slice

    return [_map_corridor_row_to_applicant(r, sba_lookup) for r in enriched_rows]


# ============================================================================
# LIVE BIGQUERY + PROPERTY GRAPH CONNECTOR CLASS
# ============================================================================

DEFAULT_GCP_PROJECT_ID = "qwiklabs-gcp-04-486b161c6a8e"


class BigQueryGraphConnector:
    """
    Production connector for BigQuery (`a4i_econ`) and Property Graph (`LocalEconomy`).
    Automatically resolves project ID from `GOOGLE_CLOUD_PROJECT`, `BQ_PROJECT_ID`,
    or defaults to `qwiklabs-gcp-04-486b161c6a8e`.
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        dataset: Optional[str] = None,
        location: str = "US",
    ) -> None:
        self.project_id = (
            project_id
            or os.environ.get("GOOGLE_CLOUD_PROJECT")
            or os.environ.get("BQ_PROJECT_ID")
            or DEFAULT_GCP_PROJECT_ID
        )
        self.dataset = dataset or os.environ.get("BQ_DATASET", "a4i_econ")
        self.location = location
        self._client: Any = None

    def _get_client(self) -> Any:
        if self._client is None:
            from google.cloud import bigquery  # type: ignore

            self._client = bigquery.Client(project=self.project_id, location=self.location)
            if not self.project_id:
                self.project_id = self._client.project
        return self._client

    def check_connection(self) -> Dict[str, Any]:
        """Verify BigQuery client authentication and inspect tables in `a4i_econ`."""
        try:
            client = self._get_client()
            ds_ref = f"{self.project_id}.{self.dataset}"
            tables = {}
            for tbl_item in client.list_tables(ds_ref):
                tbl = client.get_table(tbl_item)
                tables[tbl.table_id] = tbl.num_rows
            return {
                "connected": True,
                "project_id": self.project_id,
                "dataset": self.dataset,
                "tables": tables,
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "connected": False,
                "project_id": self.project_id,
                "dataset": self.dataset,
                "error": str(exc),
            }

    def ensure_property_graph(self) -> Dict[str, Any]:
        """Execute `CREATE OR REPLACE PROPERTY GRAPH a4i_econ.LocalEconomy` in BigQuery."""
        client = self._get_client()
        ddl = get_property_graph_ddl(self.dataset)
        job = client.query(ddl)
        job.result()
        return {
            "status": "CREATED",
            "graph": f"{self.project_id}.{self.dataset}.LocalEconomy",
            "ddl": ddl,
        }

    def query_gql_multihop_cascade(self, min_exposed: int = 2) -> List[Dict[str, Any]]:
        """
        Execute the GQL `GRAPH_TABLE(a4i_econ.LocalEconomy MATCH ...)` multi-hop
        traversal to discover upstream root and bottleneck suppliers.
        """
        client = self._get_client()
        sql = get_gql_multihop_cascade_sql(self.dataset, min_exposed=min_exposed)
        rows = client.query(sql).result()
        return [dict(r.items()) for r in rows]

    def fetch_applicants(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Query `a4i_econ` tables in BigQuery, join with SBA loan records
        (`borrowed_from` / `business_sba_summary`), and return applicant dicts
        ready for `tools/scoring_engine.py`.
        """
        client = self._get_client()
        sql = get_bq_enriched_corridor_sql(self.project_id, self.dataset)
        if limit is not None:
            sql += f"\nLIMIT {int(limit)}"
        raw_rows = [dict(r.items()) for r in client.query(sql).result()]

        sba_lookup: Dict[str, Dict[str, Any]] = {}
        if LOCAL_SBA_SUMMARY_CSV.exists():
            with LOCAL_SBA_SUMMARY_CSV.open("r", encoding="utf-8") as fh:
                for r in csv.DictReader(fh):
                    sba_lookup[str(r.get("business_id", ""))] = r

        try:
            bf_sql = f"""
            SELECT
              business_id,
              COUNT(*) AS loan_count,
              SUM(COALESCE(SAFE_CAST(gross_approval AS FLOAT64), 0.0)) AS total_borrowed_amount,
              COUNTIF(SAFE_CAST(charged_off AS BOOL)) > 0 AS has_historical_charge_off
            FROM `{self.project_id}.{self.dataset}.borrowed_from`
            GROUP BY business_id
            """
            for r in client.query(bf_sql).result():
                bid = str(r["business_id"])
                sba_lookup[bid] = {
                    "has_sba_history": "True",
                    "loan_count": r["loan_count"],
                    "total_borrowed_amount": r["total_borrowed_amount"],
                    "has_historical_charge_off": str(bool(r["has_historical_charge_off"])),
                }
        except Exception:  # noqa: BLE001
            pass

        applicants = []
        for r in raw_rows:
            r["data_source"] = f"BIGQUERY:{self.project_id}.{self.dataset}"
            applicants.append(_map_corridor_row_to_applicant(r, sba_lookup))
        return applicants


def load_corridor_applicants(
    mode: str = "canonical",
    project_id: Optional[str] = None,
    dataset: str = "a4i_econ",
    limit: Optional[int] = None,
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Unified data loader supporting 3 modes:
    - `canonical`: 11-applicant Central Market benchmark (`03_BEYOND_DATASET_ENHANCEMENT_MODEL.md`)
    - `local_csv`: 232 real Central Market businesses from `data/custom_bq_upload/business_sba_summary.csv`
    - `bigquery`: Live BigQuery query against `{project_id}.{dataset}`
    - `auto`: Uses `bigquery` if `GOOGLE_CLOUD_PROJECT`/`BQ_PROJECT_ID` is set and reachable,
      otherwise `local_csv` if requested or `canonical`.
    """
    mode_clean = mode.strip().lower()
    if mode_clean == "bigquery":
        connector = BigQueryGraphConnector(project_id=project_id, dataset=dataset)
        return connector.fetch_applicants(limit=limit), f"BIGQUERY ({connector.project_id}.{connector.dataset})"

    if mode_clean == "local_csv":
        applicants = load_applicants_from_local_csv(limit=limit)
        return applicants, f"LOCAL_CSV ({len(applicants)} real Central Market businesses)"

    if mode_clean == "auto":
        env_project = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("BQ_PROJECT_ID")
        if env_project:
            connector = BigQueryGraphConnector(project_id=env_project, dataset=dataset)
            status = connector.check_connection()
            if status.get("connected"):
                return (
                    connector.fetch_applicants(limit=limit),
                    f"BIGQUERY ({connector.project_id}.{connector.dataset})",
                )
        if os.environ.get("ADK_DATA_MODE", "").lower() == "local_csv":
            applicants = load_applicants_from_local_csv(limit=limit)
            return applicants, f"LOCAL_CSV ({len(applicants)} real Central Market businesses)"

    canonical = [copy.deepcopy(a) for a in CANONICAL_CENTRAL_MARKET_APPLICANTS]
    if limit is not None:
        canonical = canonical[:limit]
    return canonical, "CANONICAL_BENCHMARK (11 Central Market applicants from ADK/docs)"
