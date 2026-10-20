# Corridor Economic Resilience & SBA Dataset Guide
**Agents for Impact 2026 — Challenge 3: Community Economic Resilience & Micro-Grants**

This guide provides a comprehensive breakdown of the BigQuery dataset (`a4i_econ`), explaining what each table represents, which parts are **measured ground-truth** versus **modeled allocations**, how to query the data with SQL and GQL, and the empirical findings from our graph and statistical validation.

---

## 1. Executive Summary & Graph Architecture

The dataset models two hyper-local San Francisco commercial corridors (**Central Market** and **Market / Castro**, 218 deduplicated businesses across 232 registered branches) as a connected **property graph** in BigQuery (`a4i_econ.LocalEconomy` and `a4i_econ.ValidationGraph`).

```
                    ┌────────────────────────┐
                    │  tract_demographics    │ (ACS Census Need & Poverty)
                    └───────────┬────────────┘
                                │ spatial / tract join
                                ▼
  ┌──────────────────┐    borrowed_from    ┌────────────────────────┐
  │     lenders      │ ◄─────────────────  │       businesses       │ (SF Registry Nodes)
  └──────────────────┘    (BorrowedFrom)   └───────┬────────┬───────┘
                                                   │        ▲
                                  Supplies (1-hop) │        │ Supplies (2-hop)
                                                   ▼        │
                                           ┌────────────────────────┐
                                           │   Downstream Buyers    │
                                           └────────────────────────┘
                                                    ▲
                                                    │ DrawsFootfall
                                           ┌────────────────────────┐
                                           │    employer_blocks     │ (LEHD Workplace Jobs)
                                           └────────────────────────┘
```

---

## 2. Table-by-Table Reference

| Table | Rows | Graph Role | Origin | Real vs. Modeled & Key Columns |
|---|---:|---|---|---|
| [`businesses`](#businesses) | **218** | **Node (`Business`)** | SF Open Data (`data.sf.gov`, `g8m3-pdis`) | **100% Real.** Deduplicated storefronts (`business_id`), `name`, `legal_name`, `address`, `zip`, `naics4`, `industry_type`, `corridor`, `latitude`, `longitude`, `registration_year`, `tenure_years`, `corridor_alternatives`. |
| [`employer_blocks`](#employer_blocks) | **186** | **Node (`Employer`)** | US Census LEHD (LODES 8, 2023) | **100% Real.** Workplace census blocks (`block_id`), `tract`, daytime worker headcounts (`jobs`), `lat`, `lon`. |
| [`lenders`](#lenders) | **6** | **Node (`Lender`)** | SBA 7(a) & 504 FOIA (`data.sba.gov`) | **100% Real.** Verified SBA lending institutions (`bank_name`), `corridor_loan_count`, `corridor_businesses_funded`, `total_capital_deployed`, `defaulted_loans`. |
| [`supplies`](#supplies) | **2,703** | **Edge (`Supplies`)** | BEA Use Table + Proximity ($\le 500\text{m}$) | **Modeled.** `supplier_id`, `buyer_id`, BEA input-output `intensity` ($\ge 0.015$), walking distance `metres`, `corridor_alternatives`, and `decayed_intensity = intensity * EXP(-metres / 400.0)`. |
| [`draws_footfall_from`](#draws_footfall_from) | **30,455** | **Edge (`DrawsFootfall`)** | LEHD LODES 8 + Distance ($\le 800\text{m}$) | **Modeled.** `block_id`, `business_id`, `worker_share` (`jobs / nearby_businesses`), `metres`, `edge_id`. |
| [`borrowed_from`](#borrowed_from) | **8** | **Edge (`BorrowedFrom`)** | SBA 7(a) & 504 FOIA (`data.sba.gov`) | **100% Real.** Verified bank-to-borrower loans (`edge_id`, `business_id`, `bank_name`, `program_type`, `loan_amount`, `approval_date`, `term_months`, `jobs_supported`, `is_charged_off`, `charge_off_amount`, `monthly_debt_est`). |
| [`business_sba_summary`](#business_sba_summary) | **218** | **Summary (1-to-1)** | Aggregated SBA + Registry + EB Priors | **100% Real.** 1 row per deduplicated `business_id` with `naics4`, `industry_type`, SBA loan totals, `registration_year`, `tenure_years`, `corridor_alternatives`, `p_fail_shrunk`, and `median_jobs_naics4`. |
| [`business_sba_summary_all_locations`](#business_sba_summary_all_locations) | **232** | **Backup (All Branches)** | Pre-deduplication branch records | **100% Real.** Preserves all 232 physical branch rows (including multi-location entities such as 14 `Philz Coffee` branches and 2 `Cumaica Coffee` branches). |
| [`sba_industry_failure_rates`](#sba_industry_failure_rates) | **55** | **Prior Lookup** | 113,270 CA SBA 7(a) Loans (1991–2024) | **100% Real.** `naics4`, `industry_type`, Empirical Bayes shrunk 48-month failure rate (`p_fail_shrunk`), 90% credible interval (`p_fail_lo90`, `p_fail_hi90`), and `median_jobs_supported` across all 55 4-digit NAICS sectors. |
| [`tract_demographics`](#tract_demographics) | **243** | **Attributes** | US Census ACS 5-Year (`2024`) | **100% Real.** Census tract `geo_id`, `total_pop`, `median_income`, `poverty_rate`, `no_vehicle_rate`, `assistance_rate`, `lat`, `lon`. |

### 2.1 Industry Type Breakdown Across the 218 Corridor Businesses (`industry_type`)

Every business in `businesses`, `business_sba_summary`, and `sba_industry_failure_rates` is mapped to its official NAICS sector category (`industry_type`):

| Industry type (`industry_type`) | NAICS prefixes represented | Businesses |
|---|---|---:|
| Food Services — restaurants, bars, catering | 722 | **46** |
| Professional, Scientific, and Technical Services — legal, IT, consulting, design | 54 | **38** |
| Retail Trade — groceries, clothing, furniture, other stores | 44–45 | **29** |
| Certain Services — repairs, personal care, laundry, parking, community organizations | 811, 812, 813 | **27** |
| Private Education and Health Services — our records cover health care and social assistance | 62 | **24** |
| Information — publishing, software, telecommunications, hosting | 51 | **16** |
| Manufacturing — food, apparel, pharmaceuticals, equipment | 31–33 | **15** |
| Accommodations — hotels and lodging | 721 | **12** |
| Arts, Entertainment and Recreation — theaters, events, fitness | 71 | **11** |
| **Total** | | **218** |

---

## 3. How This Dataset Answers Key Questions (Verified BigQuery SQL)

### Question 1: "If Business X Closes, Who Else is in Danger?" (1-Hop & 2-Hop Cascade)
* **Why it matters:** Traditional micro-grant programs evaluate businesses in isolation. If a keystone bakery or coffee roaster closes, its failure triggers ripple effects down the local supply chain.
* **Tables used:** `businesses`, `supplies`.
```sql
-- Count 1-hop and 2-hop downstream businesses affected if each supplier closes
SELECT 
  b.business_id,
  b.name,
  b.naics4,
  b.tenure_years,
  b.corridor_alternatives,
  COUNT(DISTINCT s1.buyer_id) AS reach_1hop,
  COUNT(DISTINCT s2.buyer_id) AS reach_2hop,
  ROUND(SUM(DISTINCT s1.intensity), 3) AS direct_intensity_sum,
  ROUND(SUM(DISTINCT s1.decayed_intensity), 3) AS decayed_intensity_sum
FROM `a4i_econ.businesses` b
LEFT JOIN `a4i_econ.supplies` s1
  ON b.business_id = s1.supplier_id
LEFT JOIN `a4i_econ.supplies` s2
  ON s1.buyer_id = s2.supplier_id
  AND s2.buyer_id != b.business_id
GROUP BY 1, 2, 3, 4, 5
ORDER BY reach_1hop DESC, reach_2hop DESC
LIMIT 15;
```

---

### Question 2: "How Do We Prove Our Model Predicts Real Failure?" (Empirical Ground-Truth Validation)
* **Why it matters:** SBA charge-off records and California-wide 48-month failure priors (`p_fail_shrunk`) provide verified empirical outcomes of business distress.
* **Tables used:** `businesses`, `business_sba_summary`, `sba_industry_failure_rates`.
```sql
SELECT 
  b.business_id,
  b.name,
  b.naics4,
  r.industry_label,
  s.has_sba_history,
  s.has_historical_charge_off AS failed_in_real_life,
  s.total_charge_off_amount,
  s.estimated_annual_debt_service,
  s.p_fail_shrunk AS sector_48m_fail_rate
FROM `a4i_econ.businesses` b
JOIN `a4i_econ.business_sba_summary` s
  ON b.business_id = s.business_id
LEFT JOIN `a4i_econ.sba_industry_failure_rates` r
  ON b.naics4 = r.naics4
WHERE s.has_sba_history = TRUE
ORDER BY s.has_historical_charge_off DESC, s.estimated_annual_debt_service DESC;
```

---

### Question 3: "Which Businesses Are On the Financial Brink?" (Debt Burden vs. Shock Absorption)
* **Why it matters:** A business carrying \$16,000–\$114,000 in annual debt service cannot survive a 10% dip in daytime footfall, whereas an unencumbered shop has greater shock absorption.
* **Tables used:** `business_sba_summary`, `draws_footfall_from`.
```sql
SELECT 
  s.business_id,
  s.business_name,
  s.estimated_annual_debt_service,
  COUNT(f.block_id) AS employer_blocks_drawing_from,
  ROUND(SUM(f.worker_share), 1) AS total_dependent_workers
FROM `a4i_econ.business_sba_summary` s
LEFT JOIN `a4i_econ.draws_footfall_from` f 
  ON s.business_id = f.business_id
WHERE s.estimated_annual_debt_service > 0
GROUP BY 1, 2, 3
ORDER BY s.estimated_annual_debt_service DESC;
```

---

### Question 4: "What Happens in an Anchor Closure Shock?" (Two-Direction Simulation)
* **Why it matters:** Corridor shocks happen in **two directions**:
  1. **Direction A (Office Employer Vacates):** A major office block downsizes, starving nearby eateries of daytime footfall.
  2. **Direction B (Anchor Supplier Closes):** A sole corridor producer (`corridor_alternatives = 0`) fails, severing wholesale inputs to 85+ downstream buyers.
* **Tables used:** `employer_blocks`, `draws_footfall_from`, `businesses`, `supplies`.
```sql
-- Direction A: Simulate the loss of the largest employer block in the corridor
WITH top_employer AS (
  SELECT block_id, jobs
  FROM `a4i_econ.employer_blocks`
  ORDER BY jobs DESC
  LIMIT 1
)
SELECT 
  b.business_id,
  b.name AS exposed_business,
  b.naics4,
  ROUND(f.worker_share, 2) AS lost_worker_footfall,
  e.jobs AS employer_original_jobs
FROM `a4i_econ.draws_footfall_from` f
JOIN top_employer e ON f.block_id = e.block_id
JOIN `a4i_econ.businesses` b ON f.business_id = b.business_id
ORDER BY f.worker_share DESC
LIMIT 15;
```

---

### Question 5: "Are Micro-Grants Going Where the Need Is?" (Equity & Need Audit)
* **Why it matters:** Supply-chain algorithms naturally favor input-heavy sectors. Cross-referencing against Census ACS poverty, SNAP assistance, and zero-vehicle rates ensures grants reach high-need communities.
* **Tables used:** `businesses`, `employer_blocks`, `draws_footfall_from`, `tract_demographics`.
```sql
WITH biz_tract AS (
  SELECT
    f.business_id,
    ARRAY_AGG(e.tract ORDER BY f.metres ASC LIMIT 1)[OFFSET(0)] AS primary_tract
  FROM `a4i_econ.draws_footfall_from` f
  JOIN `a4i_econ.employer_blocks` e
    ON f.block_id = e.block_id
  GROUP BY f.business_id
)
SELECT 
  t.geo_id AS tract_geoid,
  ROUND(t.poverty_rate * 100, 1) AS poverty_pct,
  ROUND(t.assistance_rate * 100, 1) AS public_assistance_pct,
  ROUND(t.no_vehicle_rate * 100, 1) AS zero_vehicle_pct,
  t.median_income,
  COUNT(b.business_id) AS total_businesses_in_tract
FROM `a4i_econ.businesses` b
JOIN biz_tract bt ON b.business_id = bt.business_id
JOIN `a4i_econ.tract_demographics` t ON bt.primary_tract = t.geo_id
GROUP BY 1, 2, 3, 4, 5
ORDER BY poverty_pct DESC;
```

---

### Question 6: "Which Banks & CDFIs Hold the Corridor's Financial Risk?" (Lender Concentration)
* **Why it matters:** Identifies how small-business credit and default exposure are distributed across regional banks and SBA lenders.
* **Tables used:** `borrowed_from` (or `lenders`).
```sql
SELECT 
  bank_name,
  COUNT(DISTINCT business_id) AS active_corridor_borrowers,
  COUNT(*) AS total_loans,
  SUM(loan_amount) AS total_capital_lent,
  COUNTIF(is_charged_off) AS defaulted_loans,
  SUM(charge_off_amount) AS total_chargeoff_loss
FROM `a4i_econ.borrowed_from`
GROUP BY bank_name
ORDER BY total_capital_lent DESC;
```

---

## 4. Empirical Validation & Graph Analysis Summary (Person 2 & Person 3 Findings)

### 4.1 2-Hop Cascade Ranking & Hub Rejection (`corridor_alternatives`)
In the raw BEA `Supplies` graph, three IT consulting firms (`Convergeone, Inc.`, `Wpengine, Inc.`, `Tray.Io, Inc`, NAICS `5415`) achieve `reach_2hop = 121` despite having only `reach_1hop = 3`, because all three supply `Tradespace` (`5182`, Data Processing), which connects to `114` downstream buyers.
- **How `corridor_alternatives` prevents false hubs:** There are **11 IT consulting firms** (`5415`) in Central Market (`corridor_alternatives = 10`). If one closes, 10 nearby peers can absorb its clients.
- **True keystone makers:** By contrast, **`Sour Flour`** (`b_213`, NAICS `3118`, `tenure_years = 10`) and **`Cumaica Coffee`** (`b_217`, NAICS `3119`, `tenure_years = 10`) each supply **85 direct buyers** (`reach_1hop = 85`, `reach_2hop = 145`) and have **`corridor_alternatives = 0`** (zero substitutes in the corridor).

| Business ID | Name | NAICS4 | Tenure (Yrs) | 1-Hop Buyers | 2-Hop Buyers | `corridor_alternatives` | Resilience Role |
|---|---|---|---:|---:|---:|---:|---|
| `b_213` | **Sour Flour** | `3118` (Bakeries) | 10 | **85** | **145** | **0** | **#1 Keystone Maker (Funded \$10k)** |
| `b_217` | **Cumaica Coffee** | `3119` (Coffee/Food Mfg) | 10 | **85** | **145** | **0** | **#2 Keystone Maker (Funded \$10k)** |
| `b_79` | **Tradespace** | `5182` (Data/Hosting) | 4 | 114 | 85 | 0 | B2B Tech Utility Hub (Corporate-backed) |
| `b_76` | **Convergeone, Inc.** | `5415` (IT Services) | 9 | 3 | 121 | **10** | **Rejected** (10 local IT substitutes + corporate) |

---

### 4.2 Distance-Decay Sensitivity Experiment (`intensity` vs. `decayed_intensity`)
We tested replacing the flat BEA `intensity` edge weight with an exponential walking-distance decay:
$$\text{decayed\_intensity} = \text{intensity} \times \exp(-d / 400\text{m})$$
- **Result:** Across all 2,703 `Supplies` edges (mean distance $d \approx 380\text{m}$), distance decay reduces cross-corridor edge weights by an average factor of $0.39$ (`Sour Flour` sum of intensity changes from `2.595` to `0.625`; `Cumaica Coffee` from `2.595` to `0.858`), rewarding tight block-level clusters.
- **Did the top pick change?** **No.** Both `Sour Flour` (#1) and `Cumaica Coffee` (#2) remain the #1 and #2 non-corporate suppliers before and after distance decay because their 85-buyer reach and `corridor_alternatives = 0` dominate.

---

### 4.3 SBA Sole-Proprietor Filter & Selection Bias Audit
When building the California SBA 7(a) ground-truth dataset (`113,270` total CA loans):
1. **Why 18,698 Sole-Proprietor Loans Were Filtered:** `18,698` loans (`16.5%`) were filed under `BusinessType = 'INDIVIDUAL'` / personal legal names rather than storefront DBAs, yielding a **`0.0%` deterministic match rate** against public city storefront registries. Filtering to corporate/LLC filings left **`94,572` corporate loans** (`58,647` watched $\ge 48$ months, with `1,570` defaults = **`2.68%` statewide 48-month failure base rate**).
2. **Who Gets Excluded & How We Compensate:** Filtering out sole-proprietor loans means **unbanked sole proprietors and family storefronts never appear in SBA loan edges (`borrowed_from`)**. If a grant model required SBA history to prove financial need, it would systematically exclude sole proprietors. Our scoring engine explicitly corrects this bias via the **Small-Business Purity Score ($P_{\text{pure}}$)** and **Ownership Multiplier ($f_{\text{own}} = 1.00$ for Sole Proprietors vs. $0.70$ for Corporations)**, ensuring independent storefronts like **`Sour Flour`**, **`Central Market Corner Grocer`**, and **`Chico's Pizza`** receive top priority.

---

### 4.4 Empirical Bayes Failure Priors (`p_fail_shrunk`) & Expected Value Saved per \$10k
Using Beta-Binomial Empirical Bayes shrinkage ($k = 50$ pseudocounts toward the `2.68%` CA base rate across `58,647` loans), each business's expected value saved per \$10,000 micro-grant is:
$$\Delta P(\text{survive}) = p_{\text{fail,shrunk}} \cdot \eta_{\text{grant}} \quad (\eta_{\text{grant}} = 0.25), \qquad E[\text{Jobs Saved}] = \Delta P(\text{survive}) \times (\text{DirectJobs} + 0.5 \times \text{CascadeJobs})$$

| NAICS4 | Industry Label | CA Eligible Loans | 48m Failures | `p_fail_shrunk` (90% CI) | Median Jobs |
|---|---|---:|---:|---|---:|
| `7224` | Drinking Places (Bars) | 401 | 16 | **3.79%** (`2.37%–5.48%`) | 7.0 |
| `7225` | Restaurants & Eating Places | 5,976 | 215 | **3.58%** (`3.20%–3.99%`) | 9.0 |
| `4451` | Grocery & Corner Stores | 965 | 31 | **3.18%** (`2.32%–4.15%`) | 5.0 |
| `3118` | Bakeries & Tortilla Mfg | 334 | 10 | **2.92%** (`1.63%–4.52%`) | 8.0 |
| `3119` | Other Food Mfg (Coffee/Spices) | 124 | 4 | **2.88%** (`1.26%–5.08%`) | 9.0 |
| `5415` | Computer Systems Design | 946 | 17 | **1.83%** (`1.18%–2.60%`) | 6.0 |
| `6212` | Offices of Dentists | 2,340 | 24 | **1.04%** (`0.72%–1.41%`) | 6.0 |

---

### 4.5 Charge-Off Validation & 2×2 Confusion Matrix
Evaluating sector failure risk (`p_fail_shrunk >= 3.0%` high-risk flag) against verified 48-month loan defaults across the `58,647` CA SBA 7(a) loans:

| Classification Cutoff (`p_fail_shrunk >= 3.0%`) | Actual Default (`CHGOFF` within 48m) | Actual Survival (`PIF` / Active $\ge 48\text{m}$) | Row Total | Empirical Failure Rate |
|---|---:|---:|---:|---:|
| **Predicted High-Risk Sector** (`7224`, `7225`, `4451`, `4481`, etc.) | **712 (TP)** | **19,108 (FP)** | 19,820 | **3.59%** ($1.62\times$ lift vs. low-risk) |
| **Predicted Lower-Risk Sector** (`6212`, `6211`, `5415`, `5411`, etc.) | **858 (FN)** | **37,969 (TN)** | 38,827 | **2.21%** |
| **Total (CA 48m Cohort)** | **1,570** | **57,077** | **58,647** | **2.68% Base Rate** |

* **Corridor Loan Level (`borrowed_from`, 8 loans across 4 borrowers):** `1` verified charge-off (`b_153` / `The Detour`, \$60,645 loss on Loan #2 after surviving Loan #1) and `3` active/performing SBA borrowers (`b_25` `5418`, `b_72` `7225`, `b_197` `6212`).
* **Policy Takeaway:** Because small-business default has a `2.68%` 48-month base rate, any hard binary classifier produces a high false-positive count (`19,108 FP`). Therefore, `p_fail_shrunk` **should not be used as a binary pass/fail gate**; instead, using it as a **continuous expected-value weight** ($E[\text{Jobs Saved}]$) captures the $1.62\times–3.6\times$ risk differential across sectors without falsely disqualifying resilient businesses.

---

### 4.6 Equity & Demographic Need Audit (Census ACS Tracts)
Cross-referencing the 218 corridor businesses and our \$50,000 funded micro-grant portfolio (`7` businesses) against US Census ACS (`tract_demographics`):

| Census Tract (`geo_id`) | Corridor Area | Poverty Rate | Zero-Vehicle Rate | Public Assistance | Median Income | Equity Multiplier ($M_{\text{equity}}$) | Funded Grants in Tract |
|---|---|---:|---:|---:|---:|---:|---:|
| `06075012502` | Central Market (6th–7th St) | **34.2%** | **78.5%** | **14.8%** | **\$32,400** | **1.46×** | **4 grants (\$25,000)** |
| `06075017601` / `06075017802` | Central Market (8th–10th St / SoMa) | **26.8%–35.0%** | **62.0%–69.0%** | **11.2%–13.5%** | **\$41,200** | **1.35×–1.42×** | **3 grants (\$25,000)** |
| `06075016900` / `06075020600` | Market / Castro | 7.4%–9.2% | 24.1%–31.0% | 2.8%–4.1% | \$138,500 | 0.94×–1.02× | 0 grants (\$0) |
| **SF Citywide Baseline** | All 243 Tracts | **10.8%** | **28.5%** | **5.4%** | **\$126,000** | **1.00×** | **Total: 7 grants (\$50,000)** |

* **100% High-Need Targeting:** **100% of the \$50,000 micro-grant portfolio (\$50,000 / \$50,000 across all 7 funded businesses)** is deployed in Central Market tracts where poverty (`26.8%–34.2%`) is **$2.5\times–3.2\times$ the San Francisco average** and zero-vehicle household dependency (`62.0%–78.5%`) is **$2.2\times–2.8\times$ the citywide average**.
