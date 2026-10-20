# Task 2 and 3 — reproducible review

Registry as of 2026-10-20; 232 locations; 293 modeled supply edges.

## Findings

- Legacy name-based dedup retained 218 locations; this review preserves all 232 matched registry locations.
- 102 tenure-year/NAICS differences from the legacy summary; see the JSON audit for each record.
- 9 same-name groups retained with their different IDs and addresses.
- 4 groups share the same name, legal name and address. These are flagged potential duplicate filings; distinct IDs are preserved pending source resolution. Counts are registry records, not proven unique firms/storefronts.
- 20 suppliers are in the 5–25 unique-business, two-hop cascade band; this is a policy shortlist, not an award.
- Rates: MISSING — legacy hand-entered rates excluded. No legacy prior is substituted.
- The saved notebook's 8 'trusted' loans included one with no street number. Strict address matching retains only the 7 same-street-address rows in that saved run; rerun to refresh counts.
- The saved SF holdout gives graph-feature AUC 0.695 vs 0.700 baseline (delta −0.005, 95% interval −0.018 to +0.007). No predictive improvement is established.
- Hub reach versus charge-off risk: saved Spearman rho −0.14, p=0.33 across 47 industries. Failure likelihood and graph consequence remain separate.
- The saved SBA population dropped 18,698 individual/sole-proprietor loans. Its priors do not establish risk for unbanked or excluded sole proprietors. Missing SBA history is unknown, not zero need.

## Depth sensitivity

| Hops | Median reach | Maximum reach | Roots gaining new nodes |
|---:|---:|---:|---:|
| 1 | 0 | 35 | 62 |
| 2 | 0 | 55 | 18 |
| 3 | 0 | 55 | 7 |
| 4 | 0 | 55 | 0 |
| 5 | 0 | 55 | 0 |
| 6 | 0 | 55 | 0 |
| 7 | 0 | 55 | 0 |
| 8 | 0 | 55 | 0 |

Counts are distinct destinations excluding the seed; cycles and repeated paths do not create additional businesses. Hops 3–8 are sensitivity/exploration, not longer-range proof of failure.

## Industry variety

| Group | Locations |
|---|---:|
| Food Services | 50 |
| Professional, Scientific, and Technical Services | 38 |
| Retail Trade | 29 |
| Certain Services | 28 |
| Private Education and Health Services | 25 |
| Information | 19 |
| Accommodations | 16 |
| Manufacturing | 15 |
| Arts, Entertainment and Recreation | 11 |
| Unspecified / other | 1 |

## Linked community problems

The cascade shortlist covers 3 groups. Food Services is 70.0% of the shortlist versus 21.6% of source records. Retail and health/access cases must be reviewed separately; this supply-only shortlist cannot represent the whole grant portfolio.

- **Local input disruption**: Supplier → buyer → further buyers. Evidence: modeled supply graph.
- **Lost upstream orders**: Storefront demand loss → suppliers. Evidence: reverse supply traversal.
- **Loss of worker demand**: Employer block → storefront → upstream suppliers. Evidence: requires cloud footfall data.
- **Debt pressure**: Exposed business → loan → lender. Evidence: requires address-checked SBA matches; not a closure forecast.
- **Essential-service access**: Affected food, health and community-service locations → residents. Evidence: industry exposure proxy; resident counts require catchment data.

## Limits and next execution

The raw registry snapshot is current, but the cohort is inherited from existing local files. It is not a fresh citywide sample. Supply links and buyer input options are modeled. No local employer/ACS tables or canonical 337-row failure-rate export are present. Run the updated notebook in the authenticated BigQuery environment, then rebuild this review with `--rates data/industry_failure_rates.csv`. Historical charge-off does not prove a business is currently insolvent. SBA median jobs are industry loan-cohort statistics, not measured jobs at these storefronts.

Source: https://data.sf.gov/resource/g8m3-pdis.json; SF categories: https://sftreasurer.org/business-activities-naics-codes.
