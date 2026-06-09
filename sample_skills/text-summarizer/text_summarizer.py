import sys
import json
from snowflake.snowpark import Session


def summarize_documents(session: Session, stage_path: str) -> dict:
    results = {"stage": stage_path, "documents": [], "synthesis": ""}

    files = session.sql(f"LS {stage_path}").collect()

    summaries = []
    for f in files:
        file_name = f["name"].split("/")[-1]
        if not file_name.endswith(('.txt', '.md', '.csv', '.json')):
            continue

        summary_query = f"""
            SELECT SNOWFLAKE.CORTEX.SUMMARIZE(
                (SELECT $1 FROM {stage_path}/{file_name})
            ) as summary
        """
        try:
            r = session.sql(summary_query).collect()[0]
            doc_summary = {
                "file": file_name,
                "summary": r["SUMMARY"]
            }
            results["documents"].append(doc_summary)
            summaries.append(r["SUMMARY"])
        except Exception as e:
            results["documents"].append({
                "file": file_name,
                "error": str(e)
            })

    if len(summaries) > 1:
        all_text = " ".join(summaries)
        synth_query = f"""
            SELECT SNOWFLAKE.CORTEX.SUMMARIZE('{all_text}') as synthesis
        """
        r = session.sql(synth_query).collect()[0]
        results["synthesis"] = r["SYNTHESIS"]

    return results


if __name__ == "__main__":
    stage_path = sys.argv[1] if len(sys.argv) > 1 else "@MY_STAGE"
    session = Session.builder.getOrCreate()
    result = summarize_documents(session, stage_path)
    print(json.dumps(result, indent=2))
