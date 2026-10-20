# BigQuery Data Fixes, Property Graph Setup & Loading Guide (`a4i_econ`)

This document summarizes the **data, schema, and graph fixes** implemented in [`data/custom_bq_upload/`](file:///Users/sepi/Documents/work/Hackathon/A4I2026-challenge-3-micro-grants/data/custom_bq_upload), provides a **1-click self-contained SQL script** (requiring no manual CSV upload), and documents how to load the cleaned CSV files and query the `a4i_econ.LocalEconomy` Property Graph.

---

## 🛠️ Summary of Data, Schema & Graph Fixes

Original files are backed up in [`data/backup_original/`](file:///Users/sepi/Documents/work/Hackathon/A4I2026-challenge-3-micro-grants/data/backup_original). Cleaned and enriched files are in [`data/custom_bq_upload/`](file:///Users/sepi/Documents/work/Hackathon/A4I2026-challenge-3-micro-grants/data/custom_bq_upload).

| # | Issue | Before Fix | After Fix |
|---|---|---|---|
| **1** | **Business entity count mismatch & multi-location duplicates** | `business_sba_summary.csv` had `232` rows vs `230` in `a4i_econ.businesses` and `218` unique business entities (`Metro By T-Mobile` $\times 4$, `San Francisco Proper Hotel` $\times 4$, plus 8 businesses $\times 2$). | Deduplicated to **`218` canonical business entities** in both `business_sba_summary.csv` and `a4i_econ.businesses` (full 232-location version preserved in `business_sba_summary_all_locations.csv`). |
| **2** | **Missing historical SBA loans (FY2010–FY2019)** | `borrowed_from.csv` only had `4` loans (`3` businesses, FY2020+ name-only match), missing verified FY2010–FY2019 corridor borrowers. | Includes all **`8` verified Central Market SBA loans** across **`6` businesses** (`Mission Hl LLC` $\times 2$, `Mo'z Cafe Inc` $\times 1$, `The Bite` $\times 2$, `Studio Dental` $\times 1$, `Steel + Lacquer` $\times 1$, `Mr Tipple's Recording Studio` $\times 1`). |
| **3** | **`borrowed_from` & `Lender` missing from Property Graph** | `LocalEconomy` and `ValidationGraph` only had 2 node tables (`Business`, `Employer`) and 2 edge tables (`Supplies`, `DrawsFootfall`) because no `Lender` node table existed. | Created `lenders.csv` (**`6` unique `Lender` bank nodes**) and updated `CREATE OR REPLACE PROPERTY GRAPH` DDL to include `Lender` nodes and `BorrowedFrom` edges. |
| **4** | **Duplicate `(business_id, bank_name)` edge key in `borrowed_from.csv`** | `"The Bite"` (`1278937-05-211`) had 2 loans from `"U.S. Bank, National Association"` (`2025-08-26` and `2025-11-24`), violating BigQuery Property Graph's unique edge key requirement on `KEY (business_id, bank_name)`. | Added a unique `edge_id` primary key column (`business_id\|bank_name\|approval_date`) as the first column (`KEY (edge_id)`) plus `gross_approval` and `charged_off` compatibility columns. |
| **5** | **Truncated / malformed `naics4` codes** | `16` rows in `business_sba_summary.csv` had 2-digit (`44`, `72`, `81`), 3-digit (`721`, `325`, `445`), or `00`-ending (`5400`, `3100`, `4400`, `7210`, `7220`) NAICS codes. | Standardized 100% of rows to valid 4-digit NAICS codes (`721` $\to$ `7211`, `325` $\to$ `3254`, `445`/`44`/`4400` $\to$ `4451`, `72`/`7220` $\to$ `7225`, `81` $\to$ `8129`, `5400` $\to$ `5416`, `3100` $\to$ `3152`, `7210` $\to$ `7211`). |
| **6** | **Missing SF Business Registry tenure, `corridor_alternatives`, and `sba_industry_failure_rates`** | `registration_year`, `tenure_years`, `corridor_alternatives`, and 4-digit NAICS failure rates were computed in Python memory but not persisted to CSVs or BigQuery tables. | Added `registration_year`, `tenure_years`, `corridor_alternatives`, `p_fail_shrunk`, and `median_jobs_naics4` to `business_sba_summary.csv` and created `sba_industry_failure_rates.csv` (`55` 4-digit NAICS rows). |
| **7** | **Property Graph DDL & SQL column mismatches** | Previous docs referenced `work_block`, `src_id`/`dst_id`, `tract_geoid`, and backticked table names inside `CREATE OR REPLACE PROPERTY GRAPH`. | Fixed all queries to match exact BigQuery columns (`block_id`, `supplier_id`/`buyer_id`, `geo_id`, `b.name`) and BigQuery GQL syntax (unbackticked `a4i_econ.table` in `NODE/EDGE TABLES`, unqualified `REFERENCES table (key)`). |

---

## ⚡ Method 0 (Recommended): 1-Click Self-Contained BigQuery SQL Script (No File Upload Needed)

If `a4i_econ.businesses`, `a4i_econ.supplies`, `a4i_econ.draws_footfall_from`, and `a4i_econ.employer_blocks` are already loaded in your BigQuery project (`qwiklabs-gcp-04-486b161c6a8e.a4i_econ`), you **do not need to manually upload any CSV files**.

Simply copy and run the entire script in [`data/custom_bq_upload/schema_and_queries.sql`](file:///Users/sepi/Documents/work/Hackathon/A4I2026-challenge-3-micro-grants/data/custom_bq_upload/schema_and_queries.sql) directly in the [Google Cloud BigQuery Console](https://console.cloud.google.com/bigquery). Below is the core DDL and verification snippet:

```sql
-- 1. Clean & deduplicate `a4i_econ.businesses` + add tenure & corridor_alternatives
CREATE OR REPLACE TABLE `a4i_econ.businesses` AS
WITH cleaned AS (
  SELECT
    business_id,
    name,
    legal_name,
    address,
    zip,
    naics,
    CASE naics4
      WHEN '721'  THEN '7211'
      WHEN '325'  THEN '3254'
      WHEN '445'  THEN '4451'
      WHEN '44'   THEN '4451'
      WHEN '72'   THEN '7225'
      WHEN '81'   THEN '8129'
      WHEN '5400' THEN '5416'
      WHEN '3100' THEN '3152'
      WHEN '4400' THEN '4451'
      WHEN '7210' THEN '7211'
      WHEN '7220' THEN '7225'
      ELSE naics4
    END AS naics4,
    COALESCE(corridor, 'Central Market') AS corridor,
    latitude,
    longitude,
    2000 + SAFE_CAST(REGEXP_EXTRACT(business_id, r'-(\d{2})\d$') AS INT64) AS registration_year,
    26 - SAFE_CAST(REGEXP_EXTRACT(business_id, r'-(\d{2})\d$') AS INT64) AS tenure_years
  FROM `a4i_econ.businesses`
  WHERE business_id NOT IN ('1188541-05-181', '1188540-05-181', '1320080-12-221')
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY name
    ORDER BY
      CASE WHEN business_id IN (
        '1301290-03-221', '0481879-01-001', '1278937-05-211',
        '1276329-04-211', '1026779-04-151', '1252953-06-201'
      ) THEN 0 ELSE 1 END,
      business_id
  ) = 1
)
SELECT
  *,
  COUNT(*) OVER (PARTITION BY naics4) - 1 AS corridor_alternatives
FROM cleaned;

-- 2. Filter `supplies` & `draws_footfall_from` to canonical nodes + add corridor_alternatives & decay
CREATE OR REPLACE TABLE `a4i_econ.supplies` AS
SELECT
  e.supplier_id,
  e.buyer_id,
  e.intensity,
  e.metres,
  e.edge_id,
  b1.corridor_alternatives AS corridor_alternatives,
  ROUND(e.intensity * EXP(-e.metres / 400.0), 6) AS decayed_intensity
FROM `a4i_econ.supplies` e
JOIN `a4i_econ.businesses` b1 ON e.supplier_id = b1.business_id
JOIN `a4i_econ.businesses` b2 ON e.buyer_id = b2.business_id;

CREATE OR REPLACE TABLE `a4i_econ.draws_footfall_from` AS
SELECT
  e.block_id,
  e.business_id,
  e.worker_share,
  e.metres,
  e.edge_id
FROM `a4i_econ.draws_footfall_from` e
JOIN `a4i_econ.businesses` b ON e.business_id = b.business_id
JOIN `a4i_econ.employer_blocks` eb ON e.block_id = eb.block_id;

-- 3. Rebuild BigQuery Property Graph (`a4i_econ.LocalEconomy`)
--    Note: Uses unbackticked dataset.table in NODE/EDGE TABLES and unqualified REFERENCES
CREATE OR REPLACE PROPERTY GRAPH a4i_econ.LocalEconomy
  NODE TABLES (
    a4i_econ.businesses
      KEY (business_id)
      LABEL Business
      PROPERTIES (business_id, name, legal_name, naics4, zip, latitude, longitude, registration_year, tenure_years, corridor_alternatives),
    a4i_econ.employer_blocks
      KEY (block_id)
      LABEL Employer
      PROPERTIES (block_id, jobs),
    a4i_econ.lenders
      KEY (bank_name)
      LABEL Lender
      PROPERTIES (bank_name, corridor_loan_count, corridor_businesses_funded, total_capital_deployed, defaulted_loans)
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
      PROPERTIES (loan_amount, approval_date, term_months, jobs_supported, loan_status, is_charged_off, monthly_debt_est)
  );
```

> **Full Self-Contained Script**: Run [`data/custom_bq_upload/schema_and_queries.sql`](file:///Users/sepi/Documents/work/Hackathon/A4I2026-challenge-3-micro-grants/data/custom_bq_upload/schema_and_queries.sql) to also populate `a4i_econ.borrowed_from`, `a4i_econ.lenders`, `a4i_econ.sba_industry_failure_rates`, and `a4i_econ.business_sba_summary` via inline `UNNEST` structs with zero CSV uploads required.

---

## 📁 Cleaned CSV Files in `data/custom_bq_upload/`

If you prefer to upload the CSV files directly from disk instead of (or in addition to) running Method 0:
* [`data/custom_bq_upload/borrowed_from.csv`](file:///Users/sepi/Documents/work/Hackathon/A4I2026-challenge-3-micro-grants/data/custom_bq_upload/borrowed_from.csv) — **8 verified Central Market SBA loans** across 6 businesses, with unique `edge_id` primary key (`business_id|bank_name|approval_date`).
* [`data/custom_bq_upload/lenders.csv`](file:///Users/sepi/Documents/work/Hackathon/A4I2026-challenge-3-micro-grants/data/custom_bq_upload/lenders.csv) — **6 unique `Lender` bank nodes** (`bank_name` primary key).
* [`data/custom_bq_upload/sba_industry_failure_rates.csv`](file:///Users/sepi/Documents/work/Hackathon/A4I2026-challenge-3-micro-grants/data/custom_bq_upload/sba_industry_failure_rates.csv) — **55 4-digit NAICS rows** with Empirical Bayes shrunk 48-month CA SBA failure rates (`p_fail_shrunk`, `p_fail_lo90`, `p_fail_hi90`), `median_jobs_supported`, and `corridor_alternatives`.
* [`data/custom_bq_upload/business_sba_summary.csv`](file:///Users/sepi/Documents/work/Hackathon/A4I2026-challenge-3-micro-grants/data/custom_bq_upload/business_sba_summary.csv) — **218 deduplicated canonical `Business` entities** with cleaned 4-digit `naics4` codes, `registration_year`, `tenure_years`, `corridor_alternatives`, `p_fail_shrunk`, and `median_jobs_naics4`.
* [`data/custom_bq_upload/business_sba_summary_all_locations.csv`](file:///Users/sepi/Documents/work/Hackathon/A4I2026-challenge-3-micro-grants/data/custom_bq_upload/business_sba_summary_all_locations.csv) — Full 232-registration version (preserving all SF Business Registry `ttxid` rows).
* [`data/custom_bq_upload/schema_and_queries.sql`](file:///Users/sepi/Documents/work/Hackathon/A4I2026-challenge-3-micro-grants/data/custom_bq_upload/schema_and_queries.sql) — Complete SQL script and all Person 2 & Person 3 analytical queries.

### Loading via Command Line (`bq load` in Cloud Shell)

```bash
# 1. Load borrowed_from edge table (8 rows)
bq load --source_format=CSV --skip_leading_rows=1 --autodetect --replace \
  a4i_econ.borrowed_from data/custom_bq_upload/borrowed_from.csv

# 2. Load lenders node table (6 rows)
bq load --source_format=CSV --skip_leading_rows=1 --autodetect --replace \
  a4i_econ.lenders data/custom_bq_upload/lenders.csv

# 3. Load sba_industry_failure_rates lookup table (55 rows)
bq load --source_format=CSV --skip_leading_rows=1 --autodetect --replace \
  a4i_econ.sba_industry_failure_rates data/custom_bq_upload/sba_industry_failure_rates.csv

# 4. Load deduplicated business_sba_summary table (218 rows)
bq load --source_format=CSV --skip_leading_rows=1 --autodetect --replace \
  a4i_econ.business_sba_summary data/custom_bq_upload/business_sba_summary.csv
```

---

## 🔍 Property Graph GQL Test Query

After running [`schema_and_queries.sql`](file:///Users/sepi/Documents/work/Hackathon/A4I2026-challenge-3-micro-grants/data/custom_bq_upload/schema_and_queries.sql), test traversing the `a4i_econ.LocalEconomy` Property Graph across `Lender <-[BorrowedFrom]- Business -[Supplies]-> Business`:

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
