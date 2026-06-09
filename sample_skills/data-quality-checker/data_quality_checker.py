import sys
import json
from snowflake.snowpark import Session


def check_data_quality(session: Session, table_name: str) -> dict:
    results = {"table": table_name, "checks": []}

    cols = session.sql(f"DESCRIBE TABLE {table_name}").collect()
    for col in cols:
        col_name = col["name"]
        null_query = f"""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN {col_name} IS NULL THEN 1 ELSE 0 END) as nulls
            FROM {table_name}
        """
        r = session.sql(null_query).collect()[0]
        null_rate = r["NULLS"] / r["TOTAL"] if r["TOTAL"] > 0 else 0
        if null_rate > 0.05:
            results["checks"].append({
                "type": "null_rate",
                "column": col_name,
                "rate": round(null_rate * 100, 1),
                "status": "WARNING"
            })

    count_query = f"""
        SELECT COUNT(*) as current_count,
               (SELECT AVG(row_count)
                FROM SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS
                WHERE TABLE_NAME = SPLIT_PART('{table_name}', '.', 3)
                  AND CATALOG_DROPPED IS NULL) as avg_count
        FROM {table_name}
    """
    r = session.sql(count_query).collect()[0]
    if r["AVG_COUNT"] and r["AVG_COUNT"] > 0:
        deviation = abs(r["CURRENT_COUNT"] - r["AVG_COUNT"]) / r["AVG_COUNT"]
        results["checks"].append({
            "type": "row_count",
            "current": r["CURRENT_COUNT"],
            "average": int(r["AVG_COUNT"]),
            "deviation_pct": round(deviation * 100, 1),
            "status": "WARNING" if deviation > 0.2 else "OK"
        })

    freshness_query = f"""
        SELECT TIMESTAMPDIFF('hour', MAX(LAST_ALTERED), CURRENT_TIMESTAMP()) as hours_stale
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_NAME = SPLIT_PART('{table_name}', '.', 3)
    """
    r = session.sql(freshness_query).collect()[0]
    results["checks"].append({
        "type": "freshness",
        "hours_since_update": r["HOURS_STALE"],
        "status": "WARNING" if r["HOURS_STALE"] and r["HOURS_STALE"] > 24 else "OK"
    })

    return results


if __name__ == "__main__":
    table = sys.argv[1] if len(sys.argv) > 1 else "UNKNOWN"
    session = Session.builder.getOrCreate()
    result = check_data_quality(session, table)
    print(json.dumps(result, indent=2))
