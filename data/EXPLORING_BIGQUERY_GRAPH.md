# 🚀 Exploring & Visualizing the BigQuery Property Graph (`a4i_econ.LocalEconomy`)

Google BigQuery supports **GQL (Graph Query Language)** over relational tables using the `CREATE OR REPLACE PROPERTY GRAPH` DDL and `GRAPH_TABLE(...)` syntax.

---

## 🛠️ Step 1: Create the Complete 3-Node, 3-Edge Property Graph

> **⚠️ Why did `Not found: Property graph a4i_econ.LocalEconomy` happen?**
> BigQuery Property Graphs are schema metadata definitions over base tables (`businesses`, `employer_blocks`, `lenders`, `supplies`, `draws_footfall_from`, `borrowed_from`).
>
> **Important BigQuery GQL Syntax Rules:**
> 1. In `NODE TABLES` and `EDGE TABLES`, write `a4i_econ.table_name` **without backticks**.
> 2. In `REFERENCES`, write **only the unqualified table name** (`REFERENCES businesses (business_id)`, `REFERENCES employer_blocks (block_id)`, `REFERENCES lenders (bank_name)`).
> 3. Explicitly list `PROPERTIES (...)` on each node and edge table so property names never collide across labels.

Run [`data/custom_bq_upload/schema_and_queries.sql`](file:///Users/sepi/Documents/work/Hackathon/A4I2026-challenge-3-micro-grants/data/custom_bq_upload/schema_and_queries.sql) first (or run the DDL below in the **BigQuery SQL Workspace**):

```sql
CREATE OR REPLACE PROPERTY GRAPH a4i_econ.LocalEconomy
  NODE TABLES (
    a4i_econ.businesses
      KEY (business_id)
      LABEL Business
      PROPERTIES (
        business_id, name, legal_name, naics4, industry_type, zip,
        latitude, longitude, registration_year, tenure_years, corridor_alternatives
      ),
    a4i_econ.employer_blocks
      KEY (block_id)
      LABEL Employer
      PROPERTIES (block_id, jobs),
    a4i_econ.lenders
      KEY (bank_name)
      LABEL Lender
      PROPERTIES (
        bank_name, corridor_loan_count, corridor_businesses_funded,
        total_capital_deployed, defaulted_loans
      )
  )
  EDGE TABLES (
    a4i_econ.supplies
      KEY (edge_id)
      SOURCE KEY (supplier_id) REFERENCES businesses (business_id)
      DESTINATION KEY (buyer_id) REFERENCES businesses (business_id)
      LABEL Supplies
      PROPERTIES (intensity, metres, corridor_alternatives, decayed_intensity),
    a4i_econ.draws_footfall_from
      KEY (edge_id)
      SOURCE KEY (block_id) REFERENCES employer_blocks (block_id)
      DESTINATION KEY (business_id) REFERENCES businesses (business_id)
      LABEL DrawsFootfall
      PROPERTIES (worker_share, metres),
    a4i_econ.borrowed_from
      KEY (edge_id)
      SOURCE KEY (business_id) REFERENCES businesses (business_id)
      DESTINATION KEY (bank_name) REFERENCES lenders (bank_name)
      LABEL BorrowedFrom
      PROPERTIES (
        loan_amount, approval_date, term_months, jobs_supported,
        loan_status, is_charged_off, monthly_debt_est
      )
  );
```

---

## 🔍 Step 2: 5 Copy-Paste GQL Graph Queries

### Query 1: 2-Hop Cascade Reach & `corridor_alternatives` Hub Rejection Proof
*(Covers **Person 2 #2, #7** & **Person 3 #2**)*

Walks 1-to-2 hops along `Supplies` edges (`(seed:Business)-[:Supplies]->(hop1:Business)-[:Supplies]->(hop2:Business)`) and discounts raw BEA supply intensity by same-NAICS4 local redundancy (`1 / SQRT(1 + corridor_alternatives)`):

```sql
SELECT
  business_id,
  business_name,
  naics4,
  tenure_years,
  corridor_alternatives,
  COUNT(DISTINCT hop1_id) AS reach_1hop,
  COUNT(DISTINCT COALESCE(hop2_id, hop1_id)) AS reach_2hop,
  ROUND(SUM(e1_intensity), 4) AS raw_intensity_sum,
  ROUND(SUM(e1_intensity) / SQRT(1 + corridor_alternatives), 4) AS redundancy_adjusted_intensity
FROM GRAPH_TABLE(
  a4i_econ.LocalEconomy
  MATCH (seed:Business)-[e1:Supplies]->(hop1:Business)
  OPTIONAL MATCH (hop1)-[e2:Supplies]->(hop2:Business)
  WHERE hop2.business_id IS NULL OR hop2.business_id != seed.business_id
  RETURN
    seed.business_id AS business_id,
    seed.name AS business_name,
    seed.naics4 AS naics4,
    seed.tenure_years AS tenure_years,
    seed.corridor_alternatives AS corridor_alternatives,
    hop1.business_id AS hop1_id,
    hop2.business_id AS hop2_id,
    e1.intensity AS e1_intensity
)
GROUP BY business_id, business_name, naics4, tenure_years, corridor_alternatives
ORDER BY reach_2hop DESC, redundancy_adjusted_intensity DESC
LIMIT 20;
```

**Why this query proves the Hub Rejection:**
* Corporate IT firms (`Convergeone, Inc.`, `Wpengine, Inc.`, `Tray.Io, Inc` in NAICS `5415`) have `corridor_alternatives = 10` (11 IT offices in the corridor) and reach `121` nodes only via a single 1-hop bridge into `Tradespace` (`5182`, which fans out to `114` buyers).
* Conversely, foundational makers **`Sour Flour`** (`3118`, `tenure_years = 10`, `reach_1hop = 85`, `reach_2hop = 145`) and **`Cumaica Coffee`** (`3119`, `tenure_years = 10`, `reach_1hop = 85`, `reach_2hop = 145`) have **`corridor_alternatives = 0`**—zero local substitutes in Central Market!

---

### Query 2: SBA Debt Exposure & Downstream Fragility (`BorrowedFrom` + `Supplies`)
*(Covers **Person 2 #5**)*

Traverses `(lender:Lender)<-[loan:BorrowedFrom]-(b:Business)` and walks downstream `-[:Supplies]->(d:Business)` to identify corridor borrowers whose SBA debt service compounds downstream supply-chain risk:

```sql
SELECT
  borrower_id,
  borrower_name,
  naics4,
  tenure_years,
  lender_bank,
  loan_amount,
  loan_status,
  monthly_debt_est,
  COUNT(DISTINCT downstream_id) AS direct_downstream_buyers
FROM GRAPH_TABLE(
  a4i_econ.LocalEconomy
  MATCH (lender:Lender)<-[loan:BorrowedFrom]-(b:Business)
  OPTIONAL MATCH (b)-[:Supplies]->(d:Business)
  RETURN
    b.business_id AS borrower_id,
    b.name AS borrower_name,
    b.naics4 AS naics4,
    b.tenure_years AS tenure_years,
    lender.bank_name AS lender_bank,
    loan.loan_amount AS loan_amount,
    loan.loan_status AS loan_status,
    loan.monthly_debt_est AS monthly_debt_est,
    d.business_id AS downstream_id
)
GROUP BY borrower_id, borrower_name, naics4, tenure_years, lender_bank, loan_amount, loan_status, monthly_debt_est
ORDER BY loan_amount DESC;
```

---

### Query 3: Two-Direction Anchor-Closure Shock (`Employer -> Storefront <- Upstream Supplier`)
*(Covers **Person 2 #6**)*

Runs in **two directions** from consumer storefronts (`cafe:Business`):
1. **Inbound footfall**: `(e:Employer)-[df:DrawsFootfall]->(cafe:Business)` measures daytime worker footfall lost if an office block (`e`) closes or shifts to remote work.
2. **Inbound B2B supply**: `(upstream:Business)-[s:Supplies]->(cafe:Business)` identifies the upstream wholesale makers that lose B2B orders when those commuter-dependent storefronts contract.

```sql
SELECT
  employer_block_id,
  block_jobs,
  COUNT(DISTINCT impacted_storefront_id) AS storefronts_losing_footfall,
  ROUND(SUM(worker_share), 1) AS total_worker_footfall_at_risk,
  COUNT(DISTINCT upstream_supplier_id) AS upstream_suppliers_losing_orders,
  ARRAY_AGG(DISTINCT upstream_supplier_name IGNORE NULLS LIMIT 8) AS sample_upstream_suppliers_hit
FROM GRAPH_TABLE(
  a4i_econ.LocalEconomy
  MATCH (e:Employer)-[df:DrawsFootfall]->(cafe:Business)
  OPTIONAL MATCH (upstream:Business)-[s:Supplies]->(cafe)
  RETURN
    e.block_id AS employer_block_id,
    e.jobs AS block_jobs,
    cafe.business_id AS impacted_storefront_id,
    df.worker_share AS worker_share,
    upstream.business_id AS upstream_supplier_id,
    upstream.name AS upstream_supplier_name
)
GROUP BY employer_block_id, block_jobs
ORDER BY total_worker_footfall_at_risk DESC
LIMIT 15;
```

---

### Query 4: Essential Consumer Anchors by Foot-Traffic Gravity & Registry Tenure
*(Covers **Person 2 #4**)*

Finds long-tenured retail, dining, and grocery storefronts (`tenure_years` extracted from SF Business Registry `ttxid`) that capture the highest daytime worker footfall across nearby `Employer` census blocks:

```sql
SELECT
  business_id,
  business_name,
  naics4,
  registration_year,
  tenure_years,
  corridor_alternatives,
  COUNT(DISTINCT block_id) AS feeding_employer_blocks,
  SUM(employer_jobs) AS total_nearby_office_jobs,
  ROUND(SUM(worker_share), 1) AS total_worker_footfall_captured
FROM GRAPH_TABLE(
  a4i_econ.LocalEconomy
  MATCH (e:Employer)-[df:DrawsFootfall]->(b:Business)
  RETURN
    b.business_id AS business_id,
    b.name AS business_name,
    b.naics4 AS naics4,
    b.registration_year AS registration_year,
    b.tenure_years AS tenure_years,
    b.corridor_alternatives AS corridor_alternatives,
    e.block_id AS block_id,
    e.jobs AS employer_jobs,
    df.worker_share AS worker_share
)
GROUP BY business_id, business_name, naics4, registration_year, tenure_years, corridor_alternatives
ORDER BY total_worker_footfall_captured DESC
LIMIT 20;
```

---

### Query 5: Export Full Subgraph as JSON for Interactive Visualization

```sql
SELECT
  TO_JSON_STRING(STRUCT(
    supplier_id AS source,
    supplier_name AS source_label,
    supplier_naics AS source_naics,
    supplier_alts AS source_corridor_alternatives,
    buyer_id AS target,
    buyer_name AS target_label,
    buyer_naics AS target_naics,
    intensity AS weight,
    decayed_intensity AS decayed_weight,
    metres AS distance_m
  )) AS edge_json
FROM GRAPH_TABLE(
  a4i_econ.LocalEconomy
  MATCH (a:Business)-[e:Supplies]->(b:Business)
  WHERE e.intensity >= 0.02
  RETURN
    a.business_id AS supplier_id,
    a.name AS supplier_name,
    a.naics4 AS supplier_naics,
    a.corridor_alternatives AS supplier_alts,
    b.business_id AS buyer_id,
    b.name AS buyer_name,
    b.naics4 AS buyer_naics,
    e.intensity AS intensity,
    e.decayed_intensity AS decayed_intensity,
    e.metres AS metres
)
ORDER BY decayed_intensity DESC
LIMIT 200;
```

---

## 🎨 Step 3: How to Visualize the Property Graph

1. **Looker Studio (Zero-Code from BigQuery Console)**:
   * Run **Query 1**, **Query 3**, or **Query 4** in the BigQuery Console.
   * Click **Explore Data** $\to$ **Explore with Looker Studio** and add a **Google Maps Bubble Layer** using `latitude` / `longitude`, sizing bubbles by `redundancy_adjusted_intensity` or `total_worker_footfall_captured`.
2. **Cosmograph / Gephi Lite (Interactive Force-Directed Network)**:
   * Run `SELECT supplier_id AS source, buyer_id AS target, intensity, decayed_intensity, metres, corridor_alternatives FROM a4i_econ.supplies` and export as CSV, then drop into [cosmograph.app](https://cosmograph.app).
