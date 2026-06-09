import streamlit as st
from snowflake.snowpark.context import get_active_session

session = get_active_session()

st.set_page_config(page_title="Skills Hub", page_icon="🧠", layout="wide")
st.title("🧠 Skills Hub")
st.caption("Browse and explore available AI agent skills")

db = session.get_current_database()
schema = session.get_current_schema()
STAGE = f"@{db}.{schema}.SKILL_STAGE"


@st.cache_data(ttl=60)
def list_skills():
    files = session.sql(f"LS {STAGE} PATTERN='.*SKILL\\\\.md'").collect()
    skills = []
    for f in files:
        path = f["name"]
        folder = path.split("/")[-2]
        skills.append({"name": folder, "path": path, "size": f["size"]})
    return skills


@st.cache_data(ttl=60)
def read_skill_md(skill_name):
    try:
        session.sql(f"""
            CREATE FILE FORMAT IF NOT EXISTS {db}.{schema}.LINE_FORMAT
            TYPE = 'CSV' FIELD_DELIMITER = NONE RECORD_DELIMITER = '\\n'
            SKIP_HEADER = 0
        """).collect()
        query = f"""
            SELECT $1 as content
            FROM '{STAGE}/skills/{skill_name}/SKILL.md'
            (FILE_FORMAT => '{db}.{schema}.LINE_FORMAT')
        """
        rows = session.sql(query).collect()
        raw = "\n".join(r["CONTENT"] or "" for r in rows)
        return parse_skill_content(raw)
    except Exception as e:
        return {"name": skill_name, "description": f"Error: {e}",
                "category": "", "version": "", "tags": [], "instructions": ""}


def parse_skill_content(raw: str) -> dict:
    parts = raw.split("---")
    metadata = {"name": "", "description": "", "category": "", "version": "",
                "author": "", "tags": [], "instructions": ""}
    if len(parts) >= 3:
        frontmatter = parts[1]
        for line in frontmatter.strip().split("\n"):
            if line.startswith("name:"):
                metadata["name"] = line.split(":", 1)[1].strip()
            elif line.startswith("description:"):
                metadata["description"] = line.split(":", 1)[1].strip()
            elif line.startswith("category:"):
                metadata["category"] = line.split(":", 1)[1].strip()
            elif line.startswith("version:"):
                metadata["version"] = line.split(":", 1)[1].strip().strip('"')
            elif line.startswith("author:"):
                metadata["author"] = line.split(":", 1)[1].strip()
            elif line.startswith("tags:"):
                tag_str = line.split(":", 1)[1].strip()
                metadata["tags"] = [t.strip().strip("[]") for t in tag_str.split(",")]
        metadata["instructions"] = "---".join(parts[2:]).strip()
    else:
        metadata["instructions"] = raw
    return metadata


@st.cache_data(ttl=60)
def count_skill_files(skill_name):
    files = session.sql(f"LS {STAGE}/skills/{skill_name}/").collect()
    return len(files)


skills = list_skills()
skill_metadata = {s["name"]: read_skill_md(s["name"]) for s in skills}
categories = set(m["category"] for m in skill_metadata.values() if m["category"])

col1, col2, col3 = st.columns(3)
col1.metric("Total Skills", len(skills))
col2.metric("Categories", len(categories))
col3.metric("Last Updated", "Today")

st.divider()

search_col, cat_col = st.columns([2, 1])
with search_col:
    search_query = st.text_input("Search skills", placeholder="e.g. cost, monitoring, nlp...")
with cat_col:
    if categories:
        selected_category = st.selectbox(
            "Filter by category", ["All"] + sorted(categories))
    else:
        selected_category = "All"


def matches_search(meta, query):
    if not query:
        return True
    q = query.lower()
    searchable = " ".join([
        meta["name"], meta["description"], meta["category"],
        " ".join(meta["tags"])
    ]).lower()
    return q in searchable


filtered_skills = [
    s for s in skills
    if (selected_category == "All"
        or skill_metadata[s["name"]]["category"] == selected_category)
    and matches_search(skill_metadata[s["name"]], search_query)
]

cols = st.columns(3)
for i, skill in enumerate(filtered_skills):
    meta = skill_metadata[skill["name"]]
    with cols[i % 3]:
        file_count = count_skill_files(skill["name"])
        with st.container(border=True):
            st.subheader(skill["name"])
            if meta["category"]:
                st.caption(f"📂 {meta['category']}  •  v{meta['version']}")
            st.write(meta["description"])
            if meta["tags"]:
                st.caption(" ".join(f"`{t}`" for t in meta["tags"]))
            if st.button("View Details", key=skill["name"]):
                st.session_state["selected_skill"] = skill["name"]

if "selected_skill" in st.session_state:
    st.divider()
    meta = skill_metadata[st.session_state["selected_skill"]]

    st.subheader(f"📄 {st.session_state['selected_skill']}")
    if meta["description"]:
        st.caption(meta["description"])

    detail_cols = st.columns(4)
    detail_cols[0].write(f"**Category:** {meta['category'] or '—'}")
    detail_cols[1].write(f"**Version:** {meta['version'] or '—'}")
    detail_cols[2].write(f"**Author:** {meta['author'] or '—'}")
    detail_cols[3].write(f"**Tags:** {', '.join(meta['tags']) or '—'}")

    st.markdown(meta["instructions"])

    st.divider()
    st.subheader("Install")

    st.markdown("**For Cortex Code CLI:**")
    st.code(
        f'cortex skill add {STAGE}/skills/{st.session_state["selected_skill"]}/',
        language="bash"
    )

    st.markdown("**For Cortex Agent (SQL):**")
    st.code(
        f"""ALTER AGENT my_agent
  MODIFY LIVE VERSION
  SET SPECIFICATION = $$
    skills:
      - name: {st.session_state["selected_skill"]}
        source:
          type: STAGE
          path: "{STAGE}/skills/{st.session_state["selected_skill"]}"
  $$;""",
        language="sql"
    )
