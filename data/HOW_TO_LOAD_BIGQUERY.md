# Loading SBA Clean Data into BigQuery (`a4i_econ`)

This guide explains how to load the cleaned and transformed SBA loan files into BigQuery.

---

## 📁 Source Files Generated
The cleaned files are located in:
* `data/bq_upload/borrowed_from.csv` (Loan-level edge table)
* `data/bq_upload/business_sba_summary.csv` (1-row-per-business summary table)
* `data/bq_upload/schema_and_queries.sql` (Reference DDL and analysis queries)

---

## Method 1: Google Cloud Web Console (Fastest Point-and-Click)

1. Open the [Google Cloud BigQuery Console](https://console.cloud.google.com/bigquery).
2. In the **Explorer** panel, expand your project and locate the dataset **`a4i_econ`**.
3. Click the **three vertical dots `⋮`** next to `a4i_econ` and select **Create table**.

### Table 1: `borrowed_from`
* **Source:**
  * *Create table from:* **Upload**
  * *Select file:* Browse and pick `data/bq_upload/borrowed_from.csv`
  * *File format:* **CSV**
* **Destination:**
  * *Dataset:* `a4i_econ`
  * *Table:* `borrowed_from`
* **Schema:**
  * Check **Auto-detect** ✅
* **Advanced options** (click to expand):
  * *Header rows to skip:* **`1`**
  * *Write preference:* **Overwrite table**
* Click **Create table**.

### Table 2: `business_sba_summary`
* **Source:**
  * *Create table from:* **Upload**
  * *Select file:* Browse and pick `data/bq_upload/business_sba_summary.csv`
  * *File format:* **CSV**
* **Destination:**
  * *Dataset:* `a4i_econ`
  * *Table:* `business_sba_summary`
* **Schema:**
  * Check **Auto-detect** ✅
* **Advanced options**:
  * *Header rows to skip:* **`1`**
  * *Write preference:* **Overwrite table**
* Click **Create table**.

---

## Method 2: Command Line (`bq load` in Cloud Shell or Terminal)

Run from the root of the repository:

```bash
# 1. Load borrowed_from table
bq load \
  --source_format=CSV \
  --skip_leading_rows=1 \
  --autodetect \
  --replace \
  a4i_econ.borrowed_from \
  data/bq_upload/borrowed_from.csv

# 2. Load business_sba_summary table
bq load \
  --source_format=CSV \
  --skip_leading_rows=1 \
  --autodetect \
  --replace \
  a4i_econ.business_sba_summary \
  data/bq_upload/business_sba_summary.csv
```

---

## 🔍 Verification Query

Run this in BigQuery to verify rows and ground-truth defaults:

```sql
SELECT 
  'borrowed_from' AS tbl, 
  COUNT(*) AS total_rows, 
  COUNTIF(is_charged_off) AS failed_loans 
FROM `a4i_econ.borrowed_from`
UNION ALL
SELECT 
  'business_sba_summary' AS tbl, 
  COUNT(*) AS total_rows, 
  COUNTIF(has_sba_history) AS businesses_with_loans 
FROM `a4i_econ.business_sba_summary`;
```
