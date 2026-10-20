# Data sources and review

Read [TASK_2_3_REVIEW.md](TASK_2_3_REVIEW.md) for current counts, depth sensitivity,
industry variety, source corrections and limitations. Inspect
[task_2_3_review.json](task_2_3_review.json) for the complete reproducible payload.

- `verified_registry.json`: 232 public SF location records retrieved as of
  2026-10-20, limited to IDs in the inherited cohort plus the three previously
  manually excluded IDs. Coordinates and location start dates are observed.
- `bea_direct_requirements.csv` and `bea_naics_concordance.csv`: pinned national
  input-output coefficients/crosswalk. They model industry inputs, not contracts.
- `industry_failure_rates.csv`: generated only by the validation notebook; absent
  until exported from a real run. Four-digit → two-digit → state fallback.
- `custom_bq_upload/*.csv`: **legacy derived artifacts, not authoritative sources**.
  The 218-row summary has name-based dedup, rewritten NAICS, inferred tenure and
  manually entered priors. Its 232-row all-locations version is used only to
  identify the inherited registry cohort, not to establish financial facts.
  The matched-loan CSV is not an independently address-verified ledger.
- `backup_original/`: historical copies, not current analytical inputs.

The reviewed model has 293 links under 0.015/500m/top-five assumptions. The
starter's 0.005/1200m model is separate and reproduced in the sensitivity report.
Do not combine counts from different graphs or call branch counts unique firms.

Run `python3 scripts/review_tasks_2_3.py` to rebuild all review outputs without
cloud access. The JSON contains source hashes and model parameters. A missing
rate, debt balance or resident catchment stays unknown; no placeholder is inserted.
