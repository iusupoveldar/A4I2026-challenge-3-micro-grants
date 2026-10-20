# Exploring BigQuery Property Graphs (`a4i_econ.LocalEconomy`)
**Agents for Impact 2026 — Challenge 3: Community Economic Resilience & Micro-Grants**

This document explains how to set up, query, and visualize the **BigQuery Property Graph** (`a4i_econ.LocalEconomy`) over your corridor dataset.

---

## 1. Troubleshooting: `Not found: Property graph ...:a4i_econ.LocalEconomy`

If you encounter this error:
```
Not found: Property graph <project-id>:a4i_econ.LocalEconomy
```
**Why it happens:**  
A Property Graph is not a physical table; it is a **virtual schema declaration** layered over your existing BigQuery tables (`businesses`, `employer_blocks`, `supplies`, `draws_footfall_from`). If you try to run a `GRAPH a4i_econ.LocalEconomy MATCH ...` query before executing the DDL declaration, BigQuery will report that the graph does not exist.

### The Fix: Create the Property Graph
Open the [BigQuery Query Editor](https://console.cloud.google.com/bigquery) and run this DDL statement once:

```sql
CREATE OR REPLACE PROPERTY GRAPH a4i_econ.LocalEconomy
  NODE TABLES (
    a4i_econ.businesses
      KEY (business_id)
      LABEL Business PROPERTIES (
        business_id, name, legal_name, address, naics, naics4, zip, latitude, longitude
      ),
    a4i_econ.employer_blocks
      KEY (block_id)
      LABEL Employer PROPERTIES (
        block_id, tract, jobs, lat, lon
      )
  )
  EDGE TABLES (
    a4i_econ.supplies
      KEY (edge_id)
      SOURCE KEY (supplier_id) REFERENCES businesses (business_id)
      DESTINATION KEY (buyer_id) REFERENCES businesses (business_id)
      LABEL Supplies PROPERTIES (intensity, metres),
    a4i_econ.draws_footfall_from
      KEY (edge_id)
      SOURCE KEY (block_id) REFERENCES employer_blocks (block_id)
      DESTINATION KEY (business_id) REFERENCES businesses (business_id)
      LABEL DrawsFootfall PROPERTIES (worker_share, metres)
  );
```

*(Takes ~2 seconds to complete).*

---

## 2. How to Visualize the Graph

### Method A: Colab Enterprise / Jupyter Notebook (Interactive Force-Directed Visualizer)
In a notebook environment with `bigquery-magics`:

```python
%%bigquery --graph
GRAPH a4i_econ.LocalEconomy
MATCH p = ANY SHORTEST (seed:Business WHERE seed.name = 'Merchant Roots')
      -[:Supplies]->{1,2}(exposed:Business)
RETURN TO_JSON(p) AS paths
```

#### ⚠️ The Two Golden Rules for Notebook Visualization:
1. **You MUST wrap the path in `TO_JSON(p) AS paths`**:  
   If you return plain columns (`RETURN seed.name, exposed.name`), BigQuery returns a flat table with no error. Returning `TO_JSON(p)` activates the interactive graph canvas.
2. **Always use `ANY SHORTEST`**:  
   Without `ANY SHORTEST`, BigQuery returns every redundant multi-hop permutation, creating an unreadable hairball and quickly hitting the **2 MB notebook data limit**.

---

### Method B: BigQuery Web Console / BigQuery Studio
In the standard BigQuery Console SQL editor:

```sql
GRAPH a4i_econ.LocalEconomy
MATCH p = ANY SHORTEST (seed:Business)-[:Supplies]->{1,2}(exposed:Business)
RETURN TO_JSON(p) AS paths
LIMIT 25;
```

BigQuery returns the structured JSON path elements (including `nodes`, `edges`, and attached properties) which can be inspected directly in the JSON viewer or loaded into D3.js / front-end dashboards.

---

## 3. Core Graph Exploration Queries

### Query 1: Discovering Keystone Suppliers (Avoiding the Hub Trap)
In GQL, there is no `HAVING` clause. To filter on aggregations, chain statements with `NEXT` and `FILTER`. This query discovers the **keystone businesses** whose downstream reach is between 5 and 25 businesses (avoiding giant mega-hubs):

```sql
GRAPH a4i_econ.LocalEconomy
MATCH (seed:Business)-[:Supplies]->{1,2}(exposed:Business)
RETURN seed.name AS business, 
       seed.naics4 AS industry,
       COUNT(DISTINCT exposed.business_id) AS exposed_2hop
NEXT
FILTER exposed_2hop >= 5 AND exposed_2hop <= 25
RETURN business, industry, exposed_2hop
ORDER BY exposed_2hop DESC;
```

---

### Query 2: Single-Business Downstream Cascade Trace
Traces every 1-hop and 2-hop buyer exposed to a potential closure:

```sql
GRAPH a4i_econ.LocalEconomy
MATCH p = ANY SHORTEST (seed:Business WHERE seed.name = 'Castro Hearth & Wholesale Bakery LLC')
      -[:Supplies]->{1,2}(exposed:Business)
RETURN TO_JSON(p) AS paths;
```

---

### Query 3: Workplace Commuter Footfall Exposure
Traces footfall dependencies from major office/healthcare employer blocks into local restaurants and retail:

```sql
GRAPH a4i_econ.LocalEconomy
MATCH p = (e:Employer)-[:DrawsFootfall]->(b:Business)
RETURN e.jobs AS block_worker_count,
       b.name AS business_name,
       b.naics4 AS business_industry,
       TO_JSON(p) AS paths
ORDER BY e.jobs DESC
LIMIT 20;
```

---

### Query 4: Validating Graph Cascades with Real SBA Charge-Offs
Combines the `LocalEconomy` property graph with `borrowed_from` to cross-examine theoretical network fragility against real historical loan failures:

```sql
WITH cascade_summary AS (
  SELECT 
    seed_id,
    COUNT(DISTINCT exposed_id) AS downstream_exposed_count
  FROM GRAPH_TABLE(
    a4i_econ.LocalEconomy
    MATCH (seed:Business)-[:Supplies]->{1,2}(exposed:Business)
    COLUMNS (seed.business_id AS seed_id, exposed.business_id AS exposed_id)
  )
  GROUP BY seed_id
)
SELECT 
  b.business_id,
  b.name,
  b.naics4,
  COALESCE(cs.downstream_exposed_count, 0) AS downstream_exposure,
  sba.loan_status,
  sba.is_charged_off,
  sba.charge_off_amount,
  sba.bank_name
FROM `a4i_econ.businesses` b
LEFT JOIN cascade_summary cs 
  ON b.business_id = cs.seed_id
JOIN `a4i_econ.borrowed_from` sba 
  ON b.business_id = sba.business_id
ORDER BY sba.is_charged_off DESC, cs.downstream_exposed_count DESC;
```

---

## 4. The Seven BigQuery GQL Traps to Watch Out For

1. **Table Naming Syntax Trap:**  
   In `NODE TABLES` and `EDGE TABLES`, write `a4i_econ.businesses` (unbackticked). In `REFERENCES`, write only the table name: `REFERENCES businesses (business_id)`.
2. **`TO_JSON` Requirement:**  
   The visual force-graph canvas requires `RETURN TO_JSON(p) AS paths`. Without `TO_JSON`, BigQuery outputs tabular rows.
3. **The 2 MB Cap:**  
   Notebook graph rendering limits results to 2 MB. Always use `ANY SHORTEST` and `LIMIT`.
4. **Depth Saturation (`{1,3}` is too deep):**  
   At 3 hops, over 80% of businesses connect to each other on a commercial street. Stick to `{1,2}` hops for meaningful analysis.
5. **No `HAVING` in GQL:**  
   Use `NEXT` followed by `FILTER` to filter on aggregate counts.
6. **Property Name Conflicts:**  
   Property names are global across labels. If two tables declare a property named `jobs`, their data types (`INT64` vs `FLOAT64`) must agree.
7. **Spanner Graph vs BigQuery Graph:**  
   Ensure you consult `/bigquery/` documentation. Spanner Graph functions like `IS_ACYCLIC` or `PROPERTY_EXISTS` are unsupported in BigQuery GQL.
