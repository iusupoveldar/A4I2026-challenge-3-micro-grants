-- =============================================================================
-- Challenge 3: All-in-One Self-Contained BigQuery Fix, Graph DDL & Verification
-- Project / Dataset: qwiklabs-gcp-04-486b161c6a8e.a4i_econ
-- Paste and run directly in BigQuery Console (no manual CSV upload required!)
-- =============================================================================

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

-- 3. Create & populate `a4i_econ.lenders` (Lender node table for Property Graph)
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
    `a4i_econ.businesses`
      KEY (business_id)
      LABEL Business
      PROPERTIES ALL COLUMNS,
    `a4i_econ.employer_blocks`
      KEY (work_block)
      LABEL Employer
      PROPERTIES ALL COLUMNS,
    `a4i_econ.lenders`
      KEY (bank_name)
      LABEL Lender
      PROPERTIES ALL COLUMNS
  )
  EDGE TABLES (
    `a4i_econ.supplies`
      KEY (supplier_id, buyer_id)
      SOURCE KEY (supplier_id) REFERENCES `a4i_econ.businesses` (business_id)
      DESTINATION KEY (buyer_id) REFERENCES `a4i_econ.businesses` (business_id)
      LABEL Supplies
      PROPERTIES ALL COLUMNS,
    `a4i_econ.draws_footfall_from`
      KEY (business_id, work_block)
      SOURCE KEY (business_id) REFERENCES `a4i_econ.businesses` (business_id)
      DESTINATION KEY (work_block) REFERENCES `a4i_econ.employer_blocks` (work_block)
      LABEL DrawsFootfall
      PROPERTIES ALL COLUMNS,
    `a4i_econ.borrowed_from`
      KEY (edge_id)
      SOURCE KEY (business_id) REFERENCES `a4i_econ.businesses` (business_id)
      DESTINATION KEY (bank_name) REFERENCES `a4i_econ.lenders` (bank_name)
      LABEL BorrowedFrom
      PROPERTIES ALL COLUMNS
  );

CREATE OR REPLACE PROPERTY GRAPH `a4i_econ.ValidationGraph`
  NODE TABLES (
    `a4i_econ.businesses`
      KEY (business_id)
      LABEL Business
      PROPERTIES ALL COLUMNS,
    `a4i_econ.employer_blocks`
      KEY (work_block)
      LABEL Employer
      PROPERTIES ALL COLUMNS,
    `a4i_econ.lenders`
      KEY (bank_name)
      LABEL Lender
      PROPERTIES ALL COLUMNS
  )
  EDGE TABLES (
    `a4i_econ.supplies`
      KEY (supplier_id, buyer_id)
      SOURCE KEY (supplier_id) REFERENCES `a4i_econ.businesses` (business_id)
      DESTINATION KEY (buyer_id) REFERENCES `a4i_econ.businesses` (business_id)
      LABEL Supplies
      PROPERTIES ALL COLUMNS,
    `a4i_econ.draws_footfall_from`
      KEY (business_id, work_block)
      SOURCE KEY (business_id) REFERENCES `a4i_econ.businesses` (business_id)
      DESTINATION KEY (work_block) REFERENCES `a4i_econ.employer_blocks` (work_block)
      LABEL DrawsFootfall
      PROPERTIES ALL COLUMNS,
    `a4i_econ.borrowed_from`
      KEY (edge_id)
      SOURCE KEY (business_id) REFERENCES `a4i_econ.businesses` (business_id)
      DESTINATION KEY (bank_name) REFERENCES `a4i_econ.lenders` (bank_name)
      LABEL BorrowedFrom
      PROPERTIES ALL COLUMNS
  );

-- =============================================================================
-- 7. Verification & Analysis Queries
-- =============================================================================

-- Verification Query: Node & Edge Counts + NAICS Check
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

-- Property Graph GQL Query: SBA Borrowers & Their Downstream Buyers
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
