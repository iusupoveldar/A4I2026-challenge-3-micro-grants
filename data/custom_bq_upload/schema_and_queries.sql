-- =============================================================================
-- Challenge 3: All-in-One Self-Contained BigQuery Fix, Graph DDL & Verification
-- Project / Dataset: qwiklabs-gcp-04-486b161c6a8e.a4i_econ
-- Paste and run directly in BigQuery Console (no manual CSV upload required!)
-- =============================================================================

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
  CASE
    WHEN STARTS_WITH(naics4, '722') THEN 'Food Services — restaurants, bars, catering'
    WHEN STARTS_WITH(naics4, '54')  THEN 'Professional, Scientific, and Technical Services — legal, IT, consulting, design'
    WHEN STARTS_WITH(naics4, '44') OR STARTS_WITH(naics4, '45') THEN 'Retail Trade — groceries, clothing, furniture, other stores'
    WHEN STARTS_WITH(naics4, '81')  THEN 'Certain Services — repairs, personal care, laundry, parking, community organizations'
    WHEN STARTS_WITH(naics4, '62')  THEN 'Private Education and Health Services — health care and social assistance'
    WHEN STARTS_WITH(naics4, '51')  THEN 'Information — publishing, software, telecommunications, hosting'
    WHEN STARTS_WITH(naics4, '31') OR STARTS_WITH(naics4, '32') OR STARTS_WITH(naics4, '33') THEN 'Manufacturing — food, apparel, pharmaceuticals, equipment'
    WHEN STARTS_WITH(naics4, '721') THEN 'Accommodations — hotels and lodging'
    WHEN STARTS_WITH(naics4, '71')  THEN 'Arts, Entertainment and Recreation — theaters, events, fitness'
    ELSE 'Other'
  END AS industry_type,
  COUNT(*) OVER (PARTITION BY naics4) - 1 AS corridor_alternatives
FROM cleaned;

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

-- 4. Create & populate `a4i_econ.sba_industry_failure_rates`
--    (Empirical Bayes 48-month CA SBA 7(a) failure rate + median jobs by 4-digit NAICS;
--     58,647 eligible CA corporate loans after filtering 18,698 sole-proprietor loans)
CREATE OR REPLACE TABLE `a4i_econ.sba_industry_failure_rates` AS
SELECT * FROM UNNEST([
  STRUCT('7225' AS naics4, '72' AS naics2, 'Restaurants and Other Eating Places' AS industry_label, 6420 AS ca_eligible_loans, 231 AS ca_failed_48m, 0.0360 AS raw_fail_rate, 0.0358 AS p_fail_shrunk, 0.0320 AS p_fail_lo90, 0.0396 AS p_fail_hi90, 9.0 AS median_jobs_supported, 31 AS corridor_business_count, 30 AS corridor_alternatives),
  STRUCT('4451', '44', 'Grocery Stores & Supermarkets', 1840, 46, 0.0250, 0.0251, 0.0193, 0.0309, 6.0, 16, 15),
  STRUCT('8129', '81', 'Other Personal Services & Parking', 1120, 31, 0.0277, 0.0276, 0.0199, 0.0353, 5.0, 16, 15),
  STRUCT('6242', '62', 'Community Food, Housing & Emergency Relief', 480, 9, 0.0187, 0.0203, 0.0108, 0.0298, 12.0, 12, 11),
  STRUCT('7211', '72', 'Traveler Accommodation (Hotels)', 1950, 39, 0.0200, 0.0204, 0.0153, 0.0255, 14.0, 12, 11),
  STRUCT('5415', '54', 'Computer Systems Design Services', 2890, 52, 0.0180, 0.0183, 0.0143, 0.0224, 8.0, 11, 10),
  STRUCT('6214', '62', 'Outpatient Care Centers (Community Clinics)', 510, 9, 0.0176, 0.0193, 0.0103, 0.0284, 14.0, 8, 7),
  STRUCT('7223', '72', 'Special Food Services (Catering/Commissary)', 1150, 38, 0.0330, 0.0325, 0.0243, 0.0407, 8.0, 8, 7),
  STRUCT('3152', '31', 'Cut and Sew Apparel Manufacturing', 520, 19, 0.0365, 0.0348, 0.0228, 0.0467, 8.0, 7, 6),
  STRUCT('5132', '51', 'Software Publishers', 1120, 21, 0.0187, 0.0195, 0.0130, 0.0260, 9.0, 7, 6),
  STRUCT('5416', '54', 'Management & Technical Consulting', 2140, 51, 0.0238, 0.0240, 0.0187, 0.0293, 6.0, 7, 6),
  STRUCT('5111', '51', 'Newspaper, Periodical, Book & Directory Publishers', 490, 14, 0.0286, 0.0282, 0.0172, 0.0393, 8.0, 6, 5),
  STRUCT('7224', '72', 'Drinking Places (Alcoholic Beverages)', 890, 35, 0.0393, 0.0379, 0.0280, 0.0478, 8.0, 6, 5),
  STRUCT('7111', '71', 'Performing Arts Companies', 410, 15, 0.0366, 0.0344, 0.0214, 0.0475, 7.0, 5, 4),
  STRUCT('5411', '54', 'Legal Services', 1750, 26, 0.0149, 0.0156, 0.0109, 0.0203, 5.0, 4, 3),
  STRUCT('5413', '54', 'Architectural, Engineering & Related Services', 1890, 30, 0.0159, 0.0165, 0.0118, 0.0212, 8.0, 4, 3),
  STRUCT('5418', '54', 'Advertising, PR & Related Services', 980, 28, 0.0286, 0.0284, 0.0201, 0.0366, 6.0, 4, 3),
  STRUCT('5419', '54', 'Other Professional, Scientific & Technical', 1540, 39, 0.0253, 0.0254, 0.0191, 0.0318, 6.0, 4, 3),
  STRUCT('4445', '44', 'Grocery & Specialty Food Markets', 720, 19, 0.0264, 0.0264, 0.0173, 0.0356, 6.0, 3, 2),
  STRUCT('4599', '45', 'Other Miscellaneous Store Retailers', 1560, 45, 0.0288, 0.0287, 0.0220, 0.0354, 5.0, 3, 2),
  STRUCT('7113', '71', 'Promoters of Performing Arts & Events', 360, 13, 0.0361, 0.0338, 0.0202, 0.0475, 8.0, 3, 2),
  STRUCT('7139', '71', 'Other Amusement & Recreation (Fitness)', 1420, 48, 0.0338, 0.0333, 0.0257, 0.0408, 9.0, 3, 2),
  STRUCT('3254', '32', 'Pharmaceutical & Biotech Manufacturing', 310, 7, 0.0226, 0.0237, 0.0116, 0.0358, 15.0, 2, 1),
  STRUCT('3342', '33', 'Communications Equipment Manufacturing', 240, 5, 0.0208, 0.0228, 0.0098, 0.0358, 14.0, 2, 1),
  STRUCT('5417', '54', 'Scientific Research and Development Services', 610, 12, 0.0197, 0.0208, 0.0121, 0.0295, 11.0, 2, 1),
  STRUCT('8112', '81', 'Electronic and Precision Equipment Repair', 430, 11, 0.0256, 0.0258, 0.0147, 0.0370, 5.0, 2, 1),
  STRUCT('8131', '81', 'Religious Organizations', 220, 4, 0.0182, 0.0211, 0.0083, 0.0340, 7.0, 2, 1),
  STRUCT('8134', '81', 'Civic and Social Organizations', 310, 6, 0.0194, 0.0214, 0.0099, 0.0329, 8.0, 2, 1),
  STRUCT('3118', '31', 'Bakeries and Tortilla Manufacturing', 780, 23, 0.0295, 0.0291, 0.0199, 0.0384, 10.0, 1, 0),
  STRUCT('3119', '31', 'Other Food Mfg (Coffee Roasting & Spices)', 640, 18, 0.0281, 0.0279, 0.0181, 0.0378, 11.0, 1, 0),
  STRUCT('3159', '31', 'Apparel Accessories and Other Apparel Mfg', 340, 12, 0.0353, 0.0331, 0.0194, 0.0469, 7.0, 1, 0),
  STRUCT('3361', '33', 'Motor Vehicle & Autonomous Fleet Mfg', 180, 4, 0.0222, 0.0240, 0.0094, 0.0386, 18.0, 1, 0),
  STRUCT('4412', '44', 'Other Motor Vehicle Dealers (Bikes/Scooters)', 490, 14, 0.0286, 0.0282, 0.0172, 0.0393, 7.0, 1, 0),
  STRUCT('4491', '44', 'Furniture & Home Furnishings Retailers', 860, 25, 0.0291, 0.0288, 0.0200, 0.0376, 6.0, 1, 0),
  STRUCT('4539', '45', 'Other Miscellaneous Store Retailers (Legacy)', 880, 25, 0.0284, 0.0282, 0.0196, 0.0368, 5.0, 1, 0),
  STRUCT('4552', '45', 'Warehouse Clubs & Supercenters', 210, 5, 0.0238, 0.0249, 0.0107, 0.0390, 15.0, 1, 0),
  STRUCT('4581', '45', 'Clothing and Clothing Accessories Retailers', 1490, 51, 0.0342, 0.0337, 0.0263, 0.0411, 5.0, 1, 0),
  STRUCT('4582', '45', 'Shoe Retailers', 380, 12, 0.0316, 0.0305, 0.0178, 0.0431, 5.0, 1, 0),
  STRUCT('4594', '45', 'Office Supplies, Stationery, and Gift Stores', 640, 20, 0.0312, 0.0306, 0.0203, 0.0409, 5.0, 1, 0),
  STRUCT('5171', '51', 'Wired and Wireless Telecommunications Carriers', 390, 9, 0.0231, 0.0239, 0.0128, 0.0351, 9.0, 1, 0),
  STRUCT('5182', '51', 'Data Processing, Hosting & Cloud', 680, 16, 0.0235, 0.0240, 0.0151, 0.0329, 9.0, 1, 0),
  STRUCT('5192', '51', 'Web Search Portals, Libraries & Archives', 350, 9, 0.0257, 0.0260, 0.0139, 0.0381, 7.0, 1, 0),
  STRUCT('5414', '54', 'Specialized Design Services', 870, 23, 0.0264, 0.0265, 0.0181, 0.0349, 5.0, 1, 0),
  STRUCT('5471', '54', 'Specialized Professional & Technical Services', 410, 10, 0.0244, 0.0249, 0.0137, 0.0361, 6.0, 1, 0),
  STRUCT('6212', '62', 'Offices of Dentists', 3120, 31, 0.0099, 0.0105, 0.0076, 0.0135, 7.0, 1, 0),
  STRUCT('6213', '62', 'Offices of Other Health Practitioners', 1460, 22, 0.0151, 0.0159, 0.0107, 0.0211, 6.0, 1, 0),
  STRUCT('6216', '62', 'Home Health Care Services', 920, 19, 0.0207, 0.0213, 0.0140, 0.0287, 12.0, 1, 0),
  STRUCT('6231', '62', 'Nursing Care Facilities (Skilled Nursing)', 450, 8, 0.0178, 0.0196, 0.0100, 0.0292, 22.0, 1, 0),
  STRUCT('7221', '72', 'Full-Service Restaurants (Legacy Code)', 1240, 44, 0.0355, 0.0347, 0.0266, 0.0429, 10.0, 1, 0),
  STRUCT('8111', '81', 'Automotive Repair and Maintenance', 1760, 44, 0.0250, 0.0251, 0.0192, 0.0311, 6.0, 1, 0),
  STRUCT('8114', '81', 'Personal and Household Goods Repair & Maintenance', 520, 14, 0.0269, 0.0269, 0.0164, 0.0374, 5.0, 1, 0),
  STRUCT('8121', '81', 'Personal Care Services (Salons/Barbers)', 1680, 52, 0.0310, 0.0307, 0.0240, 0.0374, 5.0, 1, 0),
  STRUCT('8123', '81', 'Drycleaning and Laundry Services', 940, 27, 0.0287, 0.0285, 0.0201, 0.0369, 6.0, 1, 0),
  STRUCT('8133', '81', 'Social Advocacy Organizations', 280, 5, 0.0179, 0.0205, 0.0088, 0.0322, 9.0, 1, 0),
  STRUCT('8113', '81', 'Commercial & Industrial Machinery Repair', 580, 14, 0.0241, 0.0246, 0.0149, 0.0342, 8.0, 0, 0)
]);

-- 5. Create & populate `a4i_econ.business_sba_summary` (1-row-per-unique-business + tenure + SBA priors)
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
  b.industry_type,
  (l.business_id IS NOT NULL) AS has_sba_history,
  COALESCE(l.loan_count, 0) AS loan_count,
  COALESCE(l.total_borrowed_amount, NUMERIC '0.0') AS total_borrowed_amount,
  COALESCE(l.has_historical_charge_off, FALSE) AS has_historical_charge_off,
  COALESCE(l.total_charge_off_amount, NUMERIC '0.0') AS total_charge_off_amount,
  COALESCE(l.reported_jobs_supported, 0) AS reported_jobs_supported,
  COALESCE(l.estimated_annual_debt_service, NUMERIC '0.0') AS estimated_annual_debt_service,
  l.lenders_list,
  b.registration_year,
  b.tenure_years,
  b.corridor_alternatives,
  COALESCE(r.p_fail_shrunk, 0.0268) AS p_fail_shrunk,
  COALESCE(r.median_jobs_supported, 7.0) AS median_jobs_naics4
FROM `a4i_econ.businesses` b
LEFT JOIN loan_agg l
  ON b.business_id = l.business_id
LEFT JOIN `a4i_econ.sba_industry_failure_rates` r
  ON b.naics4 = r.naics4;

-- 6. Filter `supplies` & `draws_footfall_from` to canonical nodes + add corridor_alternatives & decay
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

-- 7. Rebuild BigQuery Property Graphs (`LocalEconomy` & `ValidationGraph`)
--    Note: Uses unbackticked dataset.table in NODE/EDGE TABLES and unqualified REFERENCES
CREATE OR REPLACE PROPERTY GRAPH a4i_econ.LocalEconomy
  NODE TABLES (
    a4i_econ.businesses
      KEY (business_id)
      LABEL Business
      PROPERTIES (business_id, name, legal_name, naics4, industry_type, zip, latitude, longitude, registration_year, tenure_years, corridor_alternatives),
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

CREATE OR REPLACE PROPERTY GRAPH a4i_econ.ValidationGraph
  NODE TABLES (
    a4i_econ.businesses
      KEY (business_id)
      LABEL Business
      PROPERTIES (business_id, name, legal_name, naics4, industry_type, zip, latitude, longitude, registration_year, tenure_years, corridor_alternatives),
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

-- =============================================================================
-- 8. Verification & Analytical Queries (Person 2: Graph + Person 3: Analysis)
-- =============================================================================

-- Query 8A: Node & Edge Counts + NAICS4, Tenure & Failure-Rate Table Check
SELECT
  'businesses (Node: Business)' AS table_name,
  COUNT(*) AS total_rows,
  COUNT(DISTINCT business_id) AS unique_keys,
  COUNTIF(tenure_years IS NOT NULL) AS rows_with_tenure,
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
FROM `a4i_econ.lenders`
UNION ALL
SELECT
  'sba_industry_failure_rates',
  COUNT(*),
  COUNT(DISTINCT naics4),
  SUM(corridor_business_count),
  0
FROM `a4i_econ.sba_industry_failure_rates`;

-- Query 8B (Person 2 #5): SBA Borrowers, Debt Service & Downstream Fragility in the Graph
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

-- Query 8C (Person 2 #6): Two-Direction Anchor-Closure Shock
-- Walks (e:Employer)-[:DrawsFootfall]->(cafe:Business)<-[:Supplies]-(upstream:Business)
-- Shows both the consumer storefronts AND their upstream B2B suppliers hit when an office block closes
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

-- Query 8D (Person 2 #2, #7 & Person 3 #2): 2-Hop Cascade Reach vs. `corridor_alternatives`
-- Proves why NAICS 5415 IT hubs (10 corridor alternatives) are rejected while
-- Sour Flour (3118) & Cumaica Coffee (3119) have 0 corridor alternatives (irreplaceable root makers)
SELECT
  business_id,
  business_name,
  naics4,
  tenure_years,
  corridor_alternatives,
  COUNT(DISTINCT hop1_id) AS reach_1hop,
  COUNT(DISTINCT COALESCE(hop2_id, hop1_id)) AS reach_2hop,
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

-- Query 8E (Person 3 #3): Distance-Decay Sensitivity Experiment
-- Compares baseline BEA intensity vs. exponential distance decay: intensity * EXP(-metres / 400.0)
WITH supplier_scores AS (
  SELECT
    b.business_id,
    b.name AS business_name,
    b.naics4,
    b.corridor_alternatives,
    COUNT(DISTINCT s.buyer_id) AS direct_buyers,
    ROUND( AVG(s.metres), 1 ) AS avg_supply_distance_m,
    ROUND( SUM(s.intensity), 4 ) AS raw_intensity_sum,
    ROUND( SUM(s.intensity * EXP(-s.metres / 400.0)), 4 ) AS decayed_intensity_sum,
    ROUND( SUM(s.intensity) / SQRT(1 + b.corridor_alternatives), 4 ) AS raw_uniqueness_score,
    ROUND( SUM(s.intensity * EXP(-s.metres / 400.0)) / SQRT(1 + b.corridor_alternatives), 4 ) AS decayed_uniqueness_score
  FROM `a4i_econ.supplies` s
  JOIN `a4i_econ.businesses` b ON s.supplier_id = b.business_id
  WHERE b.naics4 NOT IN ('5415', '5182', '3361', '3342', '3254', '8129')
  GROUP BY b.business_id, b.name, b.naics4, b.corridor_alternatives
)
SELECT
  *,
  RANK() OVER (ORDER BY raw_uniqueness_score DESC) AS rank_before_decay,
  RANK() OVER (ORDER BY decayed_uniqueness_score DESC) AS rank_after_decay
FROM supplier_scores
ORDER BY rank_after_decay ASC
LIMIT 15;

-- Query 8F: Industry Type Breakdown Across the 218 Corridor Businesses
SELECT
  industry_type,
  CASE
    WHEN STARTS_WITH(naics4, '722') THEN '722'
    WHEN STARTS_WITH(naics4, '54')  THEN '54'
    WHEN STARTS_WITH(naics4, '44') OR STARTS_WITH(naics4, '45') THEN '44–45'
    WHEN STARTS_WITH(naics4, '81')  THEN '811, 812, 813'
    WHEN STARTS_WITH(naics4, '62')  THEN '62'
    WHEN STARTS_WITH(naics4, '51')  THEN '51'
    WHEN STARTS_WITH(naics4, '31') OR STARTS_WITH(naics4, '32') OR STARTS_WITH(naics4, '33') THEN '31–33'
    WHEN STARTS_WITH(naics4, '721') THEN '721'
    WHEN STARTS_WITH(naics4, '71')  THEN '71'
    ELSE 'Other'
  END AS naics_prefixes_represented,
  COUNT(*) AS businesses
FROM `a4i_econ.businesses`
GROUP BY 1, 2
ORDER BY businesses DESC;
