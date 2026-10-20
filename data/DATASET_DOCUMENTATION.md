# Corridor Economic Resilience & SBA Dataset Guide
**Agents for Impact 2026 — Challenge 3: Community Economic Resilience & Micro-Grants**

This guide provides a comprehensive breakdown of the dataset, explaining what each table represents, which parts are **measured ground-truth** versus **modeled allocations**, and how to query the data to answer key policy, economic, and machine-learning questions.

---

## 1. Executive Summary & Graph Architecture

The dataset models a **hyper-local commercial corridor** (e.g., Central Market or Market/Castro in San Francisco) as a connected **property graph** in BigQuery (`a4i_econ`).

```
                    ┌────────────────────────┐
                    │  tract_demographics    │ (ACS Census Need & Poverty)
                    └───────────┬────────────┘
                                │ overlays
                                ▼
  ┌──────────────────┐    borrowed_from    ┌────────────────────────┐
  │   Lending Bank   │ ◄─────────────────  │       businesses       │ (SF Registry Nodes)
  └──────────────────┘                     └───────┬────────┬───────┘
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

| Table | Graph Role | Origin | Real vs. Modeled |
|---|---|---|---|
| [`businesses`](#businesses) | **Node** | SF Open Data (`data.sf.gov`) | **100% Real.** Real storefronts, addresses, coordinates, NAICS codes. Filtered to remove residential addresses and sole proprietors. |
| [`borrowed_from`](#borrowed_from) | **Edge** | SBA 7(a) & 504 FOIA (`data.sba.gov`) | **100% Real.** Verified bank-to-borrower loans, dollar amounts, and **loan charge-offs (defaults)**. |
| [`business_sba_summary`](#business_sba_summary) | **Summary** | Aggregated from SBA 7(a) / 504 | **100% Real.** 1-row-per-business summary table for easy SQL `JOIN`s without duplicates. |
| [`employer_blocks`](#employer_blocks) | **Node** | US Census LEHD (LODES 8) | **100% Real.** Real workplace census blocks and daytime worker headcounts (2023 release). |
| [`supplies`](#supplies) | **Edge** | BEA Input-Output + Proximity Model | **Modeled.** Inter-industry purchase intensities are real federal statistics; pairing *specific* shops is modeled via walking distance. |
| [`draws_footfall_from`](#draws_footfall_from) | **Edge** | LEHD + Distance Allocation | **Modeled.** Block worker headcounts are real; distributing those workers equally across local eateries is modeled. |
| [`tract_demographics`](#tract_demographics) | **Attributes** | US Census ACS 5-Year Estimates | **100% Real.** Census-tract level poverty, SNAP assistance, and zero-vehicle household rates. |

---

## 3. How This Dataset Answers Key Questions

### Question 1: "If Business X Closes, Who Else is in Danger?" (Cascading Ripple Effect)
* **Why it matters:** Traditional micro-grant programs evaluate businesses in isolation. If a bakery or hardware supplier closes, their failure triggers ripple effects down the supply chain.
* **Tables used:** `businesses`, `supplies`.
* **How to query it:** Follow outgoing `supplies` edges (1-hop and 2-hop) to identify dependent downstream buyers.
```sql
-- Count 1-hop and 2-hop downstream businesses affected if 'b_01' closes
SELECT 
  s1.src_id AS supplier_id,
  s1.dst_id AS direct_buyer_id,
  s2.dst_id AS secondary_buyer_id,
  s1.intensity AS direct_intensity,
  s2.intensity AS secondary_intensity
FROM `a4i_econ.supplies` s1
LEFT JOIN `a4i_econ.supplies` s2 
  ON s1.dst_id = s2.src_id
WHERE s1.src_id = 'TARGET_BUSINESS_ID';
```

---

### Question 2: "How Do We Prove Our Model Predicts Real Failure?" (Empirical Ground-Truth Validation)
* **Why it matters:** Judges will ask: *"How do you know your cascade scores mean anything in real life?"* The SBA charge-off records provide the **only verified empirical outcome of business failure**.
* **Tables used:** `businesses`, `business_sba_summary` (or `borrowed_from`).
* **How to answer it:** Compare businesses your graph model flagged as fragile against those that actually experienced a loan charge-off (`has_historical_charge_off = TRUE`).
```sql
SELECT 
  b.business_id,
  b.name,
  b.naics4,
  s.has_historical_charge_off AS failed_in_real_life,
  s.total_charge_off_amount,
  s.estimated_annual_debt_service
FROM `a4i_econ.businesses` b
JOIN `a4i_econ.business_sba_summary` s ON b.business_id = s.business_id
WHERE s.has_sba_history = TRUE
ORDER BY s.has_historical_charge_off DESC;
```

---

### Question 3: "Which Businesses Are On the Financial Brink?" (Debt Burden vs. Shock Absorption)
* **Why it matters:** A business carrying \$25,000 in annual debt service cannot survive a 10% dip in customer footfall, whereas an unencumbered shop can absorb the shock.
* **Tables used:** `business_sba_summary`, `draws_footfall_from`.
* **How to answer it:** Calculate the ratio between fixed debt obligations (`estimated_annual_debt_service`) and daytime footfall dependency.
```sql
SELECT 
  s.business_id,
  s.business_name,
  s.estimated_annual_debt_service,
  COUNT(f.src_id) AS employer_blocks_drawing_from,
  SUM(f.worker_share) AS total_dependent_workers
FROM `a4i_econ.business_sba_summary` s
LEFT JOIN `a4i_econ.draws_footfall_from` f 
  ON s.business_id = f.dst_id
WHERE s.estimated_annual_debt_service > 0
GROUP BY 1, 2, 3
ORDER BY s.estimated_annual_debt_service DESC;
```

---

### Question 4: "What Happens If a Major Office Employer Vacates or Cuts Staff?" (Anchor Closure Shock)
* **Why it matters:** When a corporate employer or hospital downsizes, daytime spending collapses for local lunch counters, dry cleaners, and convenience stores.
* **Tables used:** `employer_blocks`, `draws_footfall_from`, `businesses`.
* **How to answer it:** Simulate closing an employer block and measure which retail storefronts lose the largest share of their customer base.
```sql
-- Simulate the loss of the largest employer block in the corridor
WITH top_employer AS (
  SELECT block_id, total_jobs
  FROM `a4i_econ.employer_blocks`
  ORDER BY total_jobs DESC
  LIMIT 1
)
SELECT 
  b.name AS exposed_business,
  b.naics4,
  f.worker_share AS lost_worker_footfall,
  e.total_jobs AS employer_original_jobs
FROM `a4i_econ.draws_footfall_from` f
JOIN top_employer e ON f.src_id = e.block_id
JOIN `a4i_econ.businesses` b ON f.dst_id = b.business_id
ORDER BY f.worker_share DESC;
```

---

### Question 5: "Are Micro-Grants Going Where the Need Is, or Where Data is Dense?" (Equity & Need Audit)
* **Why it matters:** Supply chain edge algorithms naturally favor input-heavy businesses like restaurants over personal services like barbershops. An equity audit verifies whether relief reaches low-income tracts.
* **Tables used:** `businesses`, `tract_demographics`.
* **How to answer it:** Cross-reference grant candidates against tract poverty rates and vehicle access.
```sql
SELECT 
  t.tract_geoid,
  t.poverty_rate,
  t.snap_assistance_rate,
  t.zero_vehicle_household_rate,
  COUNT(b.business_id) AS total_businesses_in_tract
FROM `a4i_econ.tract_demographics` t
JOIN `a4i_econ.businesses` b ON b.tract = t.tract_geoid
GROUP BY 1, 2, 3, 4
ORDER BY t.poverty_rate DESC;
```

---

### Question 6: "Which Banks & CDFIs Hold the Corridor's Financial Risk?" (Lender Concentration)
* **Why it matters:** Identifies whether small businesses on the street are heavily concentrated under a single regional bank or Community Development Financial Institution (CDFI).
* **Tables used:** `borrowed_from`.
* **How to query it:** Aggregate loan volume and default rates by lender.
```sql
SELECT 
  bank_name,
  COUNT(DISTINCT business_id) AS active_corridor_borrowers,
  SUM(loan_amount) AS total_capital_lent,
  COUNTIF(is_charged_off) AS defaulted_loans,
  SUM(charge_off_amount) AS total_chargeoff_loss
FROM `a4i_econ.borrowed_from`
GROUP BY bank_name
ORDER BY total_capital_lent DESC;
```

---

## 4. Key Takeaways & Judge Talking Points

1. **Be upfront about what is measured vs. modeled:**
   > *"Every business, loan charge-off, worker count, and demographic rate is measured public government data. The specific pairings of suppliers and lunch footfall are modeled using federal averages and walking distance."*
2. **Explain sparsity with pride:**
   > *"Only 4 businesses in our corridor took SBA loans, and only a fraction have two-hop cascades. That is real economic geography, not a data defect. Our system isolates the rare critical hubs that actually hold the corridor up."*
3. **Address algorithmic bias:**
   > *"Our cascade model naturally highlights restaurants because they buy ingredients. To prevent neglect of service businesses, our agent cross-references ACS tract poverty rates and SBA debt service burdens."*
