# Simple SKILL sharing in CoCo/Cortex Code

This folder contains the complete code for the Skills Hub blog series:
CoCo integration, Streamlit browser, and Marketplace sharing.

## What is new in SKILL files

The SKILL.md files now include:
- `version` — semver for tracking updates
- `author` — skill creator
- `category` — for filtering (governance, cost-optimization, analytics)
- `tags` — search/discovery labels
- `parameters` — input schema (name, type, required, description)
- `output` — return format and fields
- `requires` — Snowflake privileges needed

## Deploy

```bash
snow sql -f setup.sql --connection <your_connection>
```

## Cortex Code (CoCo) Usage

```bash
cortex skill add @SKILLS_HUB.PUBLIC.SKILL_STAGE/skills/
$data-quality-checker Check MY_DB.SCHEMA.TABLE
```

