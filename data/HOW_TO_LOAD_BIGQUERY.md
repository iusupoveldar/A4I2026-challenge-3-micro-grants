# BigQuery Data Fixes, Property Graph Setup & Loading Guide (`a4i_econ`)

This document summarizes the **6 data and graph issues** identified and fixed in `data/custom_bq_upload/`, provides a **1-click self-contained SQL script** (requiring no manual CSV upload), and documents how to load the cleaned CSV files and query the `a4i_econ.LocalEconomy` Property Graph.

---

## 🛠️ Summary of the 6 Data & Graph Issues Fixed

Original files are backed up in [`data/backup_original/`](file:///Users/sepi/Documents/work/Hackathon/A4I2026-challenge-3-micro-grants/data/backup_original). Cleaned files are in [`data/custom_bq_upload/`](file:///Users/sepi/Documents/work/Hackathon/A4I2026-challenge-3-micro-grants/data/custom_bq_upload).

| # | Issue | Before Fix | After Fix |
|---|---|---|---|
| **1** | **Business entity count mismatch & multi-location duplicates** | `business_sba_summary.csv` had `232` rows vs `230` in `a4i_econ.businesses` and `218` unique business entities (`Metro By T-Mobile` $\times 4$, `San Francisco Proper Hotel` $\times 4$, plus 8 businesses $\times 2$). | Deduplicated to **`218` canonical business entities** in both `business_sba_summary.csv` and `a4i_econ.businesses` (full 232-location version preserved in `business_sba_summary_all_locations.csv`). |
| **2** | **Missing historical SBA loans (FY2010–FY2019)** | `borrowed_from.csv` only had `4` loans (`3` businesses, FY2020+ name-only match), missing verified FY2010–FY2019 corridor borrowers. | Includes all **`8` verified Central Market SBA loans** across **`6` businesses** (`Mission Hl LLC` $\times 2$, `Mo'z Cafe Inc` $\times 1$, `The Bite` $\times 2$, `Studio Dental` $\times 1$, `Steel + Lacquer` $\times 1$, `Mr Tipple's Recording Studio` $\times 1$). |
| **3** | **`borrowed_from` & `Lender` missing from Property Graph** | `LocalEconomy` and `ValidationGraph` only had 2 node tables (`Business`, `Employer`) and 2 edge tables (`Supplies`, `DrawsFootfall`) because no `Lender` node table existed. | Created `lenders.csv` (**`6` unique `Lender` bank nodes**) and updated `CREATE OR REPLACE PROPERTY GRAPH` DDL to include `Lender` nodes and `BorrowedFrom` edges. |
| **4** | **Duplicate `(business_id, bank_name)` edge key in `borrowed_from.csv`** | `"The Bite"` (`1278937-05-211`) had 2 loans from `"U.S. Bank, National Association"` (`2025-08-26` and `2025-11-24`), violating BigQuery Property Graph's unique edge key requirement on `KEY (business_id, bank_name)`. | Added a unique `edge_id` primary key column (`business_id\|bank_name\|approval_date`) as the first column (`KEY (edge_id)`) plus `gross_approval` and `charged_off` compatibility columns. |
| **5** | **Truncated / malformed `naics4` codes** | `16` rows in `business_sba_summary.csv` had 2-digit (`44`, `72`, `81`), 3-digit (`721`, `325`, `445`), or `00`-ending (`5400`, `3100`, `4400`, `7210`, `7220`) NAICS codes. | Standardized 100% of rows to valid 4-digit NAICS codes (`721` $\to$ `7211`, `325` $\to$ `3254`, `445`/`44`/`4400` $\to$ `4451`, `72`/`7220` $\to$ `7225`, `81` $\to$ `8129`, `5400` $\to$ `5416`, `3100` $\to$ `3152`, `7210` $\to$ `7211`). |
| **6** | **Broken SQL column reference & wrong directory path in docs** | `schema_and_queries.sql` referenced non-existent `b.business_name` on `a4i_econ.businesses` (actual column is `b.name`), and `HOW_TO_LOAD_BIGQUERY.md` referenced `data/bq_upload/` instead of `data/custom_bq_upload/`. | Fixed SQL to `COALESCE(b.name, s.business_name) AS business_name` and updated all file paths to `data/custom_bq_upload/`. |

---

## ⚡ Method 0 (Recommended): 1-Click Self-Contained BigQuery SQL Script (No File Upload Needed)

If `a4i_econ.businesses`, `a4i_econ.supplies`, `a4i_econ.draws_footfall_from`, and `a4i_econ.employer_blocks` are already loaded in your BigQuery project (`qwiklabs-gcp-04-486b161c6a8e.a4i_econ`), you **do not need to manually upload any CSV files**.

Simply copy and run the entire script below in the [Google Cloud BigQuery Console](https://console.cloud.google.com/bigquery) (also saved in [`data/custom_bq_upload/schema_and_queries.sql`](file:///Users/sepi/Documents/work/Hackathon/A4I2026-challenge-3-micro-grants/data/custom_bq_upload/schema_and_queries.sql)):

```sql
-- 1. Clean & deduplicate `a4i_econ.businesses` (fixes malformed naics4 & duplicate nodes)
CREATE OR REPLACE TABLE `a4i_econ.businesses` AS
SELECT
  * REPLACE (
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
    END AS naics4
  )
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
) = 1;

-- 2. Create & populate `a4i_econ.borrowed_from` (All 8 verified corridor SBA loans + unique edge_id)
CREATE OR REPLACE TABLE `a4i_econ.borrowed_from` AS
SELECT * FROM UNNEST([
  STRUCT(
    '1301290-03-221|GBC International Bank|2022-03-21' AS edge_id,
    '1301290-03-221' AS business_id,
    'Mission Hl LLC' AS business_name,
    'Central Market' AS corridor,
    'GBC International Bank' AS bank_name,
    '7(a)' AS program_type,
    NUMERIC '1572000.0' AS loan_amount,
    NUMERIC '1572000.0' AS gross_approval,
    DATE '2022-03-21' AS approval_date,
    300 AS term_months,
    12 AS jobs_supported,
    'Existing or more than 2 years old' AS business_age,
    FALSE AS is_franchise,
    'ACTIVE' AS loan_status,
    FALSE AS is_charged_off,
    FALSE AS charged_off,
    NUMERIC '0.0' AS charge_off_amount,
    CAST(NULL AS DATE) AS charge_off_date,
    NUMERIC '5240.00' AS monthly_debt_est
  ),
  STRUCT(
    '1301290-03-221|GBC International Bank|2016-08-18',
    '1301290-03-221', 'Mission Hl LLC', 'Central Market',
    'GBC International Bank', '7(a)',
    NUMERIC '250000.0', NUMERIC '250000.0', DATE '2016-08-18',
    120, 8, 'Existing or more than 2 years old', FALSE,
    'PAID_IN_FULL', FALSE, FALSE, NUMERIC '0.0', CAST(NULL AS DATE), NUMERIC '0.0'
  ),
  STRUCT(
    '0481879-01-001|Lendistry SBLC, LLC|2023-12-15',
    '0481879-01-001', "Mo'z Cafe Inc", 'Central Market',
    'Lendistry SBLC, LLC', '7(a)',
    NUMERIC '102700.0', NUMERIC '102700.0', DATE '2023-12-15',
    120, 7, 'Existing or more than 2 years old', FALSE,
    'ACTIVE', FALSE, FALSE, NUMERIC '0.0', CAST(NULL AS DATE), NUMERIC '855.83'
  ),
  STRUCT(
    '1278937-05-211|U.S. Bank, National Association|2025-08-26',
    '1278937-05-211', 'The Bite', 'Central Market',
    'U.S. Bank, National Association', '7(a)',
    NUMERIC '50000.0', NUMERIC '50000.0', DATE '2025-08-26',
    60, 14, 'Existing or more than 2 years old', FALSE,
    'ACTIVE', FALSE, FALSE, NUMERIC '0.0', CAST(NULL AS DATE), NUMERIC '833.33'
  ),
  STRUCT(
    '1278937-05-211|U.S. Bank, National Association|2025-11-24',
    '1278937-05-211', 'The Bite', 'Central Market',
    'U.S. Bank, National Association', '7(a)',
    NUMERIC '10000.0', NUMERIC '10000.0', DATE '2025-11-24',
    60, 14, 'Existing or more than 2 years old', FALSE,
    'ACTIVE', FALSE, FALSE, NUMERIC '0.0', CAST(NULL AS DATE), NUMERIC '166.67'
  ),
  STRUCT(
    '1276329-04-211|Wells Fargo Bank, National Association|2016-09-13',
    '1276329-04-211', 'Studio Dental', 'Central Market',
    'Wells Fargo Bank, National Association', '7(a)',
    NUMERIC '350000.0', NUMERIC '350000.0', DATE '2016-09-13',
    120, 10, 'Existing or more than 2 years old', FALSE,
    'PAID_IN_FULL', FALSE, FALSE, NUMERIC '0.0', CAST(NULL AS DATE), NUMERIC '0.0'
  ),
  STRUCT(
    '1026779-04-151|Redwood Credit Union|2015-02-03',
    '1026779-04-151', 'Steel + Lacquer', 'Central Market',
    'Redwood Credit Union', '7(a)',
    NUMERIC '150000.0', NUMERIC '150000.0', DATE '2015-02-03',
    120, 8, 'Startup, Loan Funds will Open Business', FALSE,
    'PAID_IN_FULL', FALSE, FALSE, NUMERIC '0.0', CAST(NULL AS DATE), NUMERIC '0.0'
  ),
  STRUCT(
    '1252953-06-201|Live Oak Banking Company|2015-06-15',
    '1252953-06-201', "Mr Tipple's Recording Studio", 'Central Market',
    'Live Oak Banking Company', '7(a)',
    NUMERIC '200000.0', NUMERIC '200000.0', DATE '2015-06-15',
    120, 12, 'Startup, Loan Funds will Open Business', FALSE,
    'PAID_IN_FULL', FALSE, FALSE, NUMERIC '0.0', CAST(NULL AS DATE), NUMERIC '0.0'
  )
]);

-- 3. Create & populate `a4i_econ.lenders` (Lender node table)
CREATE OR REPLACE TABLE `a4i_econ.lenders` AS
SELECT
  bank_name,
  COUNT(*) AS corridor_loan_count,
  COUNT(DISTINCT business_id) AS corridor_businesses_funded,
  SUM(loan_amount) AS total_capital_deployed,
  COUNTIF(is_charged_off) AS defaulted_loans
FROM `a4i_econ.borrowed_from`
GROUP BY bank_name;

-- 4. Create & populate `a4i_econ.business_sba_summary` (1-row-per-unique-business)
CREATE OR REPLACE TABLE `a4i_econ.business_sba_summary` AS
WITH loan_agg AS (
  SELECT
    business_id,
    COUNT(*) AS loan_count,
    SUM(loan_amount) AS total_borrowed_amount,
    LOGICAL_OR(is_charged_off) AS has_historical_charge_off,
    SUM(charge_off_amount) AS total_charge_off_amount,
    MAX(jobs_supported) AS reported_jobs_supported,
    ROUND(SUM(monthly_debt_est) * 12, 2) AS estimated_annual_debt_service,
    STRING_AGG(DISTINCT bank_name, '; ') AS lenders_list
  FROM `a4i_econ.borrowed_from`
  GROUP BY business_id
)
SELECT
  b.business_id,
  b.name AS business_name,
  b.legal_name,
  COALESCE(b.corridor, 'Central Market') AS corridor,
  b.naics4,
  (l.business_id IS NOT NULL) AS has_sba_history,
  COALESCE(l.loan_count, 0) AS loan_count,
  COALESCE(l.total_borrowed_amount, NUMERIC '0.0') AS total_borrowed_amount,
  COALESCE(l.has_historical_charge_off, FALSE) AS has_historical_charge_off,
  COALESCE(l.total_charge_off_amount, NUMERIC '0.0') AS total_charge_off_amount,
  COALESCE(l.reported_jobs_supported, 0) AS reported_jobs_supported,
  COALESCE(l.estimated_annual_debt_service, NUMERIC '0.0') AS estimated_annual_debt_service,
  l.lenders_list
FROM `a4i_econ.businesses` b
LEFT JOIN loan_agg l
  ON b.business_id = l.business_id;

-- 5. Filter `supplies` and `draws_footfall_from` to canonical `businesses` nodes
CREATE OR REPLACE TABLE `a4i_econ.supplies` AS
SELECT e.*
FROM `a4i_econ.supplies` e
JOIN `a4i_econ.businesses` b1 ON e.supplier_id = b1.business_id
JOIN `a4i_econ.businesses` b2 ON e.buyer_id = b2.business_id;

CREATE OR REPLACE TABLE `a4i_econ.draws_footfall_from` AS
SELECT e.*
FROM `a4i_econ.draws_footfall_from` e
JOIN `a4i_econ.businesses` b ON e.business_id = b.business_id
JOIN `a4i_econ.employer_blocks` eb ON e.work_block = eb.work_block;

-- 6. Rebuild BigQuery Property Graphs with Business, Employer, and Lender nodes
CREATE OR REPLACE PROPERTY GRAPH `a4i_econ.LocalEconomy`
  NODE TABLES (
    `a4i_econ.businesses` KEY (business_id) LABEL Business PROPERTIES ALL COLUMNS,
    `a4i_econ.employer_blocks` KEY (work_block) LABEL Employer PROPERTIES ALL COLUMNS,
    `a4i_econ.lenders` KEY (bank_name) LABEL Lender PROPERTIES ALL COLUMNS
  )
  EDGE TABLES (
    `a4i_econ.supplies`
      KEY (supplier_id, buyer_id)
      SOURCE KEY (supplier_id) REFERENCES `a4i_econ.businesses` (business_id)
      DESTINATION KEY (buyer_id) REFERENCES `a4i_econ.businesses` (business_id)
      LABEL Supplies PROPERTIES ALL COLUMNS,
    `a4i_econ.draws_footfall_from`
      KEY (business_id, work_block)
      SOURCE KEY (business_id) REFERENCES `a4i_econ.businesses` (business_id)
      DESTINATION KEY (work_block) REFERENCES `a4i_econ.employer_blocks` (work_block)
      LABEL DrawsFootfall PROPERTIES ALL COLUMNS,
    `a4i_econ.borrowed_from`
      KEY (edge_id)
      SOURCE KEY (business_id) REFERENCES `a4i_econ.businesses` (business_id)
      DESTINATION KEY (bank_name) REFERENCES `a4i_econ.lenders` (bank_name)
      LABEL BorrowedFrom PROPERTIES ALL COLUMNS
  );

CREATE OR REPLACE PROPERTY GRAPH `a4i_econ.ValidationGraph`
  NODE TABLES (
    `a4i_econ.businesses` KEY (business_id) LABEL Business PROPERTIES ALL COLUMNS,
    `a4i_econ.employer_blocks` KEY (work_block) LABEL Employer PROPERTIES ALL COLUMNS,
    `a4i_econ.lenders` KEY (bank_name) LABEL Lender PROPERTIES ALL COLUMNS
  )
  EDGE TABLES (
    `a4i_econ.supplies`
      KEY (supplier_id, buyer_id)
      SOURCE KEY (supplier_id) REFERENCES `a4i_econ.businesses` (business_id)
      DESTINATION KEY (buyer_id) REFERENCES `a4i_econ.businesses` (business_id)
      LABEL Supplies PROPERTIES ALL COLUMNS,
    `a4i_econ.draws_footfall_from`
      KEY (business_id, work_block)
      SOURCE KEY (business_id) REFERENCES `a4i_econ.businesses` (business_id)
      DESTINATION KEY (work_block) REFERENCES `a4i_econ.employer_blocks` (work_block)
      LABEL DrawsFootfall PROPERTIES ALL COLUMNS,
    `a4i_econ.borrowed_from`
      KEY (edge_id)
      SOURCE KEY (business_id) REFERENCES `a4i_econ.businesses` (business_id)
      DESTINATION KEY (bank_name) REFERENCES `a4i_econ.lenders` (bank_name)
      LABEL BorrowedFrom PROPERTIES ALL COLUMNS
  );

-- 7. Test Query: Verify Counts, Unique Keys, NAICS4, and SBA Borrowers
SELECT
  'businesses (Node: Business)' AS table_name,
  COUNT(*) AS total_rows,
  COUNT(DISTINCT business_id) AS unique_keys,
  0 AS sba_borrowers,
  COUNTIF(LENGTH(naics4) != 4 OR ENDS_WITH(naics4, '00')) AS bad_naics_count
FROM `a4i_econ.businesses`
UNION ALL
SELECT
  'business_sba_summary',
  COUNT(*),
  COUNT(DISTINCT business_id),
  COUNTIF(has_sba_history),
  COUNTIF(LENGTH(naics4) != 4 OR ENDS_WITH(naics4, '00'))
FROM `a4i_econ.business_sba_summary`
UNION ALL
SELECT
  'borrowed_from (Edge: BorrowedFrom)',
  COUNT(*),
  COUNT(DISTINCT edge_id),
  COUNT(DISTINCT business_id),
  0
FROM `a4i_econ.borrowed_from`
UNION ALL
SELECT
  'lenders (Node: Lender)',
  COUNT(*),
  COUNT(DISTINCT bank_name),
  SUM(corridor_businesses_funded),
  0
FROM `a4i_econ.lenders`;
```

---

## 📁 Cleaned CSV Files in `data/custom_bq_upload/`

If you prefer to upload the CSV files directly from disk instead of (or in addition to) running Method 0:
* `data/custom_bq_upload/borrowed_from.csv` — **8 verified Central Market SBA loans** across 6 businesses, with unique `edge_id` primary key (`business_id|bank_name|approval_date`).
* `data/custom_bq_upload/lenders.csv` — **6 unique `Lender` bank nodes** (`bank_name` primary key).
* `data/custom_bq_upload/business_sba_summary.csv` — **218 deduplicated canonical `Business` entities** with cleaned 4-digit `naics4` codes.
* `data/custom_bq_upload/business_sba_summary_all_locations.csv` — Full 232-registration version (preserving all SF Business Registry `ttxid` rows).
* `data/custom_bq_upload/schema_and_queries.sql` — Complete SQL script and analysis queries.

### Loading via Command Line (`bq load` in Cloud Shell)

```bash
# 1. Load borrowed_from edge table (8 rows)
bq load --source_format=CSV --skip_leading_rows=1 --autodetect --replace \
  a4i_econ.borrowed_from data/custom_bq_upload/borrowed_from.csv

# 2. Load lenders node table (6 rows)
bq load --source_format=CSV --skip_leading_rows=1 --autodetect --replace \
  a4i_econ.lenders data/custom_bq_upload/lenders.csv

# 3. Load deduplicated business_sba_summary table (218 rows)
bq load --source_format=CSV --skip_leading_rows=1 --autodetect --replace \
  a4i_econ.business_sba_summary data/custom_bq_upload/business_sba_summary.csv
```

---

## 🔍 Property Graph GQL Test Query

After running Method 0, test traversing the `a4i_econ.LocalEconomy` Property Graph across `Lender <-[BorrowedFrom]- Business -[Supplies]-> Business`:

```sql
SELECT
  borrower_id,
  borrower_name,
  lender_bank,
  loan_amount,
  loan_status,
  COUNT(DISTINCT downstream_id) AS direct_downstream_buyers
FROM GRAPH_TABLE(
  `a4i_econ.LocalEconomy`
  MATCH (lender:Lender)<-[loan:BorrowedFrom]-(b:Business)
  OPTIONAL MATCH (b)-[:Supplies]->(d:Business)
  RETURN
    b.business_id AS borrower_id,
    b.name AS borrower_name,
    lender.bank_name AS lender_bank,
    loan.loan_amount AS loan_amount,
    loan.loan_status AS loan_status,
    d.business_id AS downstream_id
)
GROUP BY borrower_id, borrower_name, lender_bank, loan_amount, loan_status
ORDER BY loan_amount DESC;
```
