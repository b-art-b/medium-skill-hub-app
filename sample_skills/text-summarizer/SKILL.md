---
name: text-summarizer
description: Summarizes documents stored on Snowflake stages using Cortex AI SUMMARIZE function.
version: 1.0.0
author: skills-hub-team
category: analytics
tags: summarization, documents, cortex-ai, nlp
---

# Instructions

When the user asks to summarize documents, files, or text content:

1. Ask for the stage path containing the documents if not provided
2. Run `text_summarizer.py` with the stage path
3. Return a concise summary of each document found
4. If multiple documents, provide individual summaries + an overall synthesis
5. Mention the number of documents processed and their names
6. Skip binary files (images, executables) — only process text-based formats

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| stage_path | string | yes | Stage path containing documents (e.g. @MY_DB.MY_SCHEMA.DOCS_STAGE) |
| file_types | string | no | Comma-separated extensions to process (default: txt,md,csv,json) |

## Output

Returns JSON with fields: `stage`, `documents`, `synthesis`

## Requires

- READ on target stage
- USAGE on SNOWFLAKE.CORTEX functions
