-- =============================================================================
-- Challenge 3: SBA 7(a) & 504 Clean BigQuery Schema & Analysis Queries
-- Dataset: a4i_econ
-- =============================================================================

-- 1. Create table: borrowed_from (Loan-level graph edge table)
CREATE OR REPLACE TABLE `a4i_econ.borrowed_from` (
  business_id STRING NOT NULL,
  business_name STRING,
  corridor STRING,
  bank_name STRING NOT NULL,
  program_type STRING,           -- '7(a)' or '504'
  loan_amount NUMERIC,          -- Original approved dollar amount
  approval_date DATE,
  term_months INT64,
  jobs_supported INT64,         -- Real borrower-reported employee count
  business_age STRING,          -- 'Existing Business', 'Startup', etc.
  is_franchise BOOL,
  loan_status STRING,           -- 'ACTIVE', 'PAID_IN_FULL', 'CHARGED_OFF'
  is_charged_off BOOL,          -- TRUE = Empirical business failure (Ground Truth)
  charge_off_amount NUMERIC,
  charge_off_date DATE,
  monthly_debt_est NUMERIC
);

-- 2. Create table: business_sba_summary (1-row-per-business Risk & Debt Profile)
CREATE OR REPLACE TABLE `a4i_econ.business_sba_summary` (
  business_id STRING NOT NULL,
  business_name STRING,
  legal_name STRING,
  corridor STRING,
  naics4 STRING,
  has_sba_history BOOL,
  loan_count INT64,
  total_borrowed_amount NUMERIC,
  has_historical_charge_off BOOL,
  total_charge_off_amount NUMERIC,
  reported_jobs_supported INT64,
  estimated_annual_debt_service NUMERIC,
  lenders_list STRING
);

-- =============================================================================
-- Ready-To-Run High-Impact Analysis Queries for Demos & Pitches
-- =============================================================================

-- Query 1: Empirical Ground-Truth Charge-Off Failure Audit
-- Shows which businesses actually failed vs their supply-chain cascade exposure
SELECT 
  b.business_id,
  b.business_name,
  b.naics4,
  s.has_historical_charge_off AS failed_in_real_life,
  s.total_charge_off_amount,
  s.estimated_annual_debt_service
FROM `a4i_econ.business_sba_summary` s
JOIN `a4i_econ.businesses` b ON b.business_id = s.business_id
WHERE s.has_sba_history = TRUE
ORDER BY s.has_historical_charge_off DESC, s.total_borrowed_amount DESC;

-- Query 2: High Debt-Service Fragility Hotspots
-- Identifies businesses carrying heavy debt burden that cannot afford supply shocks
SELECT 
  business_id,
  business_name,
  naics4,
  estimated_annual_debt_service,
  lenders_list
FROM `a4i_econ.business_sba_summary`
WHERE estimated_annual_debt_service > 10000
ORDER BY estimated_annual_debt_service DESC;

-- Query 3: Corridor Lender Concentration Risk
-- Identifies which banks are the critical credit anchors for the corridor
SELECT 
  bank_name,
  COUNT(DISTINCT business_id) AS corridor_clients,
  SUM(loan_amount) AS total_capital_deployed,
  COUNTIF(is_charged_off) AS defaulted_loans,
  SUM(charge_off_amount) AS total_chargeoff_loss
FROM `a4i_econ.borrowed_from`
GROUP BY bank_name
ORDER BY total_capital_deployed DESC;
