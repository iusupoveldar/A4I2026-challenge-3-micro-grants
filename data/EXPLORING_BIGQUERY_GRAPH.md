# Explore the canonical graph

Use `a4i_econ.LocalEconomy` after running the reviewed SQL. See
[the query suite](custom_bq_upload/schema_and_queries.sql) for executable examples:

- A: one to eight hops with `ANY SHORTEST`, excluding the seed and counting each
  destination once. Report new versus cumulative destinations at each depth.
- B: `NEXT ... FILTER` restricts the two-hop cascade shortlist to 5–25 exposed
  destinations. Other businesses still need a separate direct-relief/access review.
- C: old reach baseline versus strongest weighted exposure per endpoint; every
  industry remains in the distance-decay comparison and ranks are shown before/after.
- D: employer demand loss propagates to storefronts and then upstream suppliers.
  Aggregate footfall before joining suppliers so each worker share is counted once.
- E: downstream loan and lender exposure, preserving businesses without matched
  SBA history. No matched loan means unknown debt, not no need.
- F: industry variety with denominators. Compare source, exposed and shortlisted
  businesses; broad unknown codes stay visible.
- G: same-name collision audit with all location IDs and both addresses retained.

Depth is not severity. A fourth edge is not a fourth independently verified social
problem. Supply disruption, lost upstream orders, worker-demand loss, debt pressure,
and essential-service access are distinct connected mechanisms with different
source requirements. The [review](TASK_2_3_REVIEW.md) documents their evidence status.

The local review uses a separately labeled model built from current registry locations
and pinned BEA coefficients. Do not copy its 293-edge counts onto the cloud snapshot.
