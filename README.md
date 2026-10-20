# Community Economic Resilience & Micro-Grants

A research prototype for reviewing connected shocks to San Francisco businesses.
The current source review covers the **232 registry locations** matched from the
local all-locations cohort. It preserves same-name branches and does not certify
real grant awards, jobs saved or avoided closures.

Read the [source review](data/TASK_2_3_REVIEW.md) and use the notebook and agent
tools below to inspect the graph. The 11-applicant benchmark is an illustrative
policy scenario; its financial inputs and beneficiary totals are assumptions.

## What was corrected in Tasks 2 and 3

See the [reproducible review](data/TASK_2_3_REVIEW.md) and
[record-level audit](data/task_2_3_review.json).

- **Depth:** cycle-safe distinct destination counts at hops 1–8, default 2 for
  the decision baseline. The reviewed local model gains no new destinations
  after hop 3. This is a finding about this graph, not a universal cutoff.
- **Consequence:** distance-decayed edge products, buyer-specific modeled input
  alternatives, and one strongest exposure per destination. Raw reach is shown
  as a baseline; repeated paths do not multiply businesses or direct intensity.
- **Variety:** cohort, exposed businesses and the cascade shortlist are compared
  by industry. The source has nine named activity groups plus one unspecified
  `72` record. The earlier 218-business counts described a name-deduplicated
  artifact, not the complete set of registered locations.
- **Connected problems:** local supply disruption, lost upstream orders, lost
  worker demand, debt pressure and essential-service access. The analysis distinguishes
  traversable modeled supply links from mechanisms needing additional evidence.
- **Keystone band:** 5–25 distinct businesses within 2 hops is an explicit policy
  shortlist. It is not an empirical proof or an automatic denial outside the band.
- **Sources:** registry coordinates and location start dates replace invented
  positions and account-number tenure. Short NAICS codes remain broad. Branches
  are retained; duplicate keys fail with an actionable audit.
- **Priors:** only the notebook's `industry_failure_rates` is accepted. The legacy
  hand-entered `sba_industry_failure_rates.csv` is excluded from runtime consumers.
- **Loans:** same-street-address matches only. The saved notebook's eight
  previously 'trusted' loans included one with no street number; seven had an
  actual same-street-address check. No corridor default is established in that run.
- **Grant sensitivity:** an $8,000 debt-bridge scenario can vary by verified current
  debt; absent debt and causal effectiveness remain unknown. A flat 25% assumption
  cannot change rank, and no fixed winner is forced by the revised analysis.

## Reproduce locally

No third-party Python dependency or cloud credential is needed for the source review:

```sh
python3 scripts/review_tasks_2_3.py
python3 -m unittest discover -s tests -v
```

The generated Markdown review and JSON audit include source coordinates, both
traversal directions, depth through eight hops, industry concentration and missing
evidence. Agent tools return the paths explaining each business's exposure.

The local reviewed supply model uses the pinned BEA coefficients, a **0.015**
coefficient floor, **500m** maximum distance, **five** suppliers per buyer and
**400m** exponential decay. These are declared modeling choices. The report also
rebuilds the starter's **0.005 / 1200m** variant for sensitivity; the two graphs'
counts must never be combined. Neither contains observed vendor contracts.

Registry snapshot: [public source](https://data.sf.gov/resource/g8m3-pdis.json),
as of 2026-10-20. [Activity groups](https://sftreasurer.org/business-activities-naics-codes)
follow the SF Treasurer's page. Source hashes and every changed NAICS/year value
are in the audit. The inherited cohort is not a fresh citywide sample.

## Reproduce in the authenticated BigQuery environment

1. Run [the load notebook](notebooks/c3_01_load_explore.ipynb) from this checkout.
   Review duplicate IDs and both addresses before resolving any collision.
   It now retains `location_start_date` and distinct same-name locations.
2. Run [the validation notebook](notebooks/Challenge3.ipynb). It publishes the
   canonical `industry_failure_rates`, exports its CSV, applies strict address
   checks, and adds depth, weighted exposure, industry variety, a held-out
   confusion matrix and an equity audit with a labeled workplace-tract proxy.
   Revised cells have no saved output until rerun. Earlier saved model validation
   outputs are historical evidence, not a fresh execution of the revised pipeline.
3. Run [the reviewed SQL](data/custom_bq_upload/schema_and_queries.sql) after
   those source tables exist. It preserves base tables and creates reviewed
   tables plus **one canonical graph, `a4i_econ.LocalEconomy`**. Duplicate keys,
   rate horizons and source metadata are checked before traversal. No loan or
   prior is synthesized through an `UNNEST` list.
4. Copy the notebook's full `data/industry_failure_rates.csv` into this checkout
   and run `python3 scripts/review_tasks_2_3.py --rates data/industry_failure_rates.csv`.
   Never reconstruct the full table from the few displayed notebook rows.

No cloud migration or paid reservation was executed during this local review.
The public cloud snapshot requires credentials unavailable in this environment.
The SQL and revised cloud notebook cells require execution in the authenticated
project before their new results can be cited.

## Evidence for failure likelihood

The saved notebook analyzed 58,647 eligible California SBA 7(a) loans with a
48-month horizon (1,570 charge-offs), holding out 1,490 SF loans with 34 failures.
Loan terms alone had AUC **0.700**; adding graph structure gave **0.695**, change
**−0.005** with interval **−0.018 to +0.007**. No predictive gain is established.
The underlying SBA population excluded 18,698 individual/sole-proprietor loans;
its results cannot establish outcomes for excluded or unbanked businesses.
Industry history also had an interval spanning zero for its incremental AUC.
Across 47 industries, hub reach versus charge-off risk gave **rho −0.14, p=0.33**:
no positive association is established. This does not prove the true effect is zero.

Use graph structure for modeled consequence and SBA history as an industry
charge-off prior. Charge-off is not a storefront closure. SBA industry median
jobs are loan-cohort proxies, not measured employment at each business. Historical
charge-off does not demonstrate current insolvency. Current cash, burn, debt,
ownership, invoices and service catchments need applicant evidence.

## Agent behavior

`analyze_corridor_impact(business_id, max_hops=1..8, direction='downstream'|'upstream')`
returns evidence paths, unique reach and industry exposure. `review_industry_variety()`
compares the cohort and cascade shortlist. Source-based records return
`EVIDENCE_ONLY` from the orchestrator until financial/eligibility evidence exists.
The named 11-applicant benchmark remains available explicitly as an illustrative
scenario; it is never a silent fallback for real data.
