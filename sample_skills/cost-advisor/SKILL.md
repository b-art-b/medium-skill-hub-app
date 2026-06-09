---
name: cost-advisor
description: Analyzes Snowflake warehouse credit consumption, identifies cost anomalies, and recommends optimization actions.
version: 1.1.0
author: skills-hub-team
category: cost-optimization
tags: cost, credits, warehouse, finops, optimization
---

# Instructions

When the user asks about costs, credits, warehouse spend, or optimization:

1. Run `cost_advisor.py` to analyze recent consumption
2. Report: top 5 warehouses by credits (last 30 days), week-over-week trend
3. Flag anomalies: any warehouse with >50% WoW credit increase (or custom threshold)
4. Recommend actions:
   - Warehouses with low utilization: suggest downsizing or auto-suspend
   - Warehouses with spikes: identify time windows and suggest investigation
   - Idle warehouses: recommend suspension or removal
5. Always show totals and projected monthly spend
6. If the user asks about a specific warehouse, drill down into that warehouse's hourly pattern

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| days_lookback | number | no | Number of days to analyze (default 30) |
| anomaly_threshold_pct | number | no | Week-over-week increase percentage to flag as anomaly (default 50) |

## Output

Returns JSON with fields: `warehouses`, `anomalies`, `recommendations`, `total_credits`, `projected_monthly`

## Requires

- IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE
