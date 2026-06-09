---
name: data-quality-checker
description: Validates data quality of Snowflake tables — checks null rates, duplicate keys, row count trends, and data freshness.
version: 1.2.0
author: skills-hub-team
category: governance
tags: data-quality, monitoring, validation, dq
---

# Instructions

When the user asks about data quality, table health, or data validation:

1. Ask which table(s) to check (fully qualified name) if not provided
2. Run `data_quality_checker.py` with the table name as argument
3. Report findings: null rates per column, duplicate primary keys, row count vs 7-day average, last update timestamp
4. Flag any issues exceeding thresholds:
   - Nulls > 5% in any column (or custom threshold if provided)
   - Any duplicate primary keys
   - Row count deviation > 20% from 7-day average
   - Data staleness > 24 hours (or custom threshold)
5. Provide actionable recommendations for each flagged issue
6. End with a summary: total checks run, pass/fail count, overall health score (Good/Warning/Critical)

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| table_name | string | yes | Fully qualified table name (e.g. DB.SCHEMA.TABLE) |
| threshold_null_pct | number | no | Null percentage threshold for warnings (default 5) |
| threshold_freshness_hours | number | no | Max acceptable hours since last update (default 24) |

## Output

Returns JSON with fields: `table`, `checks`, `summary`

## Requires

- IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE
- SELECT on target table
