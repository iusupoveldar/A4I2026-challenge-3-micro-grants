# Dataset documentation

The current local source cohort and generated model are documented in
[TASK_2_3_REVIEW.md](TASK_2_3_REVIEW.md). This supersedes earlier mixed-snapshot
claims about 218 businesses, 2,703 supply links or 30,455 footfall links.

## Observed versus modeled

| Input/result | Meaning | Evidence |
|---|---|---|
| Registry location ID, name, legal name, address, coordinates, start date | An active registered location as of the source snapshot | `verified_registry.json` |
| Same-name collision | Possibly multiple branches/entities; never silently merged | JSON audit includes each ID/address |
| NAICS | Self-reported source precision, with broad and questionable codes retained | Registry source; explicit sector fallback |
| Supply edge | Possible industry input relationship allocated by proximity | BEA coefficients plus declared model parameters |
| Buyer input alternatives | Other same-input modeled suppliers connected to that buyer within 500m | Graph proxy, not verified vendor substitutability |
| Unique reach | Distinct destinations excluding source within 1–8 hops | Cycle-safe BFS / GQL ANY SHORTEST |
| Weighted exposure | Maximum edge-product path per destination, summed once per destination | Decay and modeled-alternative assumptions; not probability |
| SBA prior | Industry loan charge-off rate at a stated horizon | Full notebook-generated `industry_failure_rates` only |
| Debt bridge | Assumed grant response using current applicant debt | Unknown until verified current inputs are supplied |
| Industry jobs median | Jobs reported by loans in an eligible industry cohort | Proxy; never measured jobs at a storefront |

The local graph does not contain employer, ACS, or verified loan-source tables.
It therefore does not measure lost workers, affected residents, current debt or
jobs saved. The review flags these connected mechanisms as evidence gaps.

## Cloud outputs

The notebook exports canonical rates, strictly checks matched loan addresses,
and produces `cascade_review`, `graph_depth_sensitivity`,
`chargeoff_confusion_matrix`, and (when sources exist) `cascade_equity_audit`.
The equity audit uses the nearest linked workplace block's tract as a labeled
proxy and reports its coverage; it is not unique resident reach.

The reviewed SQL creates `businesses_enriched`, `business_risk`,
`supplies_enriched`, `borrowed_from_enriched`, `lenders_enriched` and one
`LocalEconomy` property graph. It preserves source tables. It cannot restore
branches already deleted by an earlier migration; reload source records first.
