# Load and verify BigQuery

Follow the [root reproducibility instructions](../README.md). Run the updated
load notebook, then the validation notebook to produce `industry_failure_rates`
and `corridor_loan_outcomes`, then [schema_and_queries.sql](custom_bq_upload/schema_and_queries.sql).

The SQL requires source tables; it is not a self-contained synthetic data load.
It preserves raw tables, checks duplicate keys and canonical priors, keeps
locations distinct and does not infer tenure from IDs or force short NAICS codes
into an industry. Only the notebook's prior table is consumed. The historical
`sba_industry_failure_rates` table/CSV is not an alternative source.

Review the graph's actual parameters and counts each run. `scripts/load.sh`
loads a separate starter snapshot; it can replace source tables and provision a
paid reservation, so it is an explicit setup action rather than automatic
validation recovery. No cloud deployment was executed by the local source review.
