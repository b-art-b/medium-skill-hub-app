-- Skills Hub Part 2: Deploy enriched skills + Streamlit browser
-- Prerequisites: Part 1 infrastructure (SKILLS_HUB database, SKILL_STAGE, roles)

USE DATABASE SKILLS_HUB;
USE SCHEMA PUBLIC;

-- Upload enriched skills (run from repo root with snow CLI):
-- snow sql -q "PUT file://sample_skills/data-quality-checker/SKILL.md @SKILL_STAGE/skills/data-quality-checker/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"
-- snow sql -q "PUT file://sample_skills/data-quality-checker/data_quality_checker.py @SKILL_STAGE/skills/data-quality-checker/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"
-- snow sql -q "PUT file://sample_skills/cost-advisor/SKILL.md @SKILL_STAGE/skills/cost-advisor/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"
-- snow sql -q "PUT file://sample_skills/cost-advisor/cost_advisor.py @SKILL_STAGE/skills/cost-advisor/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"
-- snow sql -q "PUT file://sample_skills/text-summarizer/SKILL.md @SKILL_STAGE/skills/text-summarizer/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"
-- snow sql -q "PUT file://sample_skills/text-summarizer/text_summarizer.py @SKILL_STAGE/skills/text-summarizer/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"

-- File format for reading SKILL.md line by line
CREATE FILE FORMAT IF NOT EXISTS LINE_FORMAT
  TYPE = 'CSV'
  FIELD_DELIMITER = NONE
  RECORD_DELIMITER = '\n'
  SKIP_HEADER = 0;

-- Create Streamlit stage and upload app
CREATE STAGE IF NOT EXISTS STREAMLIT_STAGE
  DIRECTORY = (ENABLE = TRUE);

-- Upload Streamlit files (run from repo root):
-- snow sql -q "PUT file://streamlit/app.py @STREAMLIT_STAGE/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"
-- snow sql -q "PUT file://streamlit/environment.yml @STREAMLIT_STAGE/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"

-- Create Streamlit app
DROP STREAMLIT IF EXISTS SKILLS_BROWSER;

CREATE STREAMLIT SKILLS_BROWSER
  FROM '@STREAMLIT_STAGE'
  MAIN_FILE = 'app.py'
  QUERY_WAREHOUSE = COMPUTE_WH
  TITLE = 'Skills Hub Browser';

ALTER STREAMLIT SKILLS_BROWSER ADD LIVE VERSION FROM LAST;

-- Grant access to consumers
GRANT USAGE ON STREAMLIT SKILLS_BROWSER TO ROLE SKILL_CONSUMER;
