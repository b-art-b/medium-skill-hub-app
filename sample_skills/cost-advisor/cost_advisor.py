import sys
import json
from snowflake.snowpark import Session


def analyze_costs(session: Session) -> dict:
    results = {"warehouses": [], "anomalies": [], "recommendations": []}

    top_wh_query = """
        SELECT WAREHOUSE_NAME,
               SUM(CREDITS_USED) as TOTAL_CREDITS,
               AVG(CREDITS_USED) as AVG_DAILY
        FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
        WHERE START_TIME >= DATEADD('day', -30, CURRENT_TIMESTAMP())
        GROUP BY WAREHOUSE_NAME
        ORDER BY TOTAL_CREDITS DESC
        LIMIT 5
    """
    for row in session.sql(top_wh_query).collect():
        results["warehouses"].append({
            "name": row["WAREHOUSE_NAME"],
            "credits_30d": round(row["TOTAL_CREDITS"], 2),
            "avg_daily": round(row["AVG_DAILY"], 2)
        })

    wow_query = """
        WITH this_week AS (
            SELECT WAREHOUSE_NAME, SUM(CREDITS_USED) as credits
            FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
            WHERE START_TIME >= DATEADD('day', -7, CURRENT_TIMESTAMP())
            GROUP BY WAREHOUSE_NAME
        ),
        last_week AS (
            SELECT WAREHOUSE_NAME, SUM(CREDITS_USED) as credits
            FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
            WHERE START_TIME BETWEEN DATEADD('day', -14, CURRENT_TIMESTAMP())
                                AND DATEADD('day', -7, CURRENT_TIMESTAMP())
            GROUP BY WAREHOUSE_NAME
        )
        SELECT t.WAREHOUSE_NAME,
               t.credits as this_week,
               l.credits as last_week,
               ((t.credits - l.credits) / NULLIF(l.credits, 0)) * 100 as pct_change
        FROM this_week t
        JOIN last_week l ON t.WAREHOUSE_NAME = l.WAREHOUSE_NAME
        WHERE ((t.credits - l.credits) / NULLIF(l.credits, 0)) > 0.5
    """
    for row in session.sql(wow_query).collect():
        results["anomalies"].append({
            "warehouse": row["WAREHOUSE_NAME"],
            "this_week_credits": round(row["THIS_WEEK"], 2),
            "last_week_credits": round(row["LAST_WEEK"], 2),
            "increase_pct": round(row["PCT_CHANGE"], 1)
        })

    idle_query = """
        SELECT WAREHOUSE_NAME
        FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
        WHERE START_TIME >= DATEADD('day', -7, CURRENT_TIMESTAMP())
        GROUP BY WAREHOUSE_NAME
        HAVING SUM(CREDITS_USED) < 0.1
    """
    for row in session.sql(idle_query).collect():
        results["recommendations"].append({
            "warehouse": row["WAREHOUSE_NAME"],
            "action": "Consider suspending or removing — near-zero usage last 7 days"
        })

    return results


if __name__ == "__main__":
    session = Session.builder.getOrCreate()
    result = analyze_costs(session)
    print(json.dumps(result, indent=2))
