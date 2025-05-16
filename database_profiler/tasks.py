from celery import shared_task
from django.db import connection
from pymongo_wrapper.model import Query
import sqlglot
from sqlglot import exp
from bson.objectid import ObjectId
from datetime import datetime
import json


@shared_task
def analyze_query_for_indexing(query_id):
    try:
        query_record = Query.find_one({"_id": ObjectId(query_id)})
        if not query_record:
            print(f"No query record found for ID: {query_id}")
            return

        suggestions = []
        for query in query_record["queries"]:
            sql = query["sql"]
            params = query["params"]
            tables = query["tables"]
            execution_duration = query["execution_duration"]
            rows_affected = query["rows_affected"]

            if not sql.strip().upper().startswith("SELECT") or len(tables) > 1:
                continue

            with connection.cursor() as cursor:
                try:
                    cursor.execute(f"EXPLAIN (FORMAT JSON) {sql}", params)
                    plan = cursor.fetchall()
                except Exception as e:
                    print(f"EXPLAIN failed for SQL: {sql}, Error: {str(e)}")
                    continue

                # Parse EXPLAIN output
                for row in plan:
                    # Handle row[0] as list or JSON string
                    plan_data = row[0]
                    if isinstance(plan_data, str):
                        plan_json = json.loads(plan_data)  # Parse JSON string
                        plan_data = plan_json[0]["Plan"]  # Access main plan
                    elif isinstance(plan_data, list):
                        plan_data = plan_data[0]["Plan"]  # Already parsed list
                    else:
                        print(f"Unexpected plan_data type: {type(plan_data)}")
                        continue

                    if "Seq Scan" in plan_data.get("Node Type", ""):
                        table = tables[0]
                        cursor.execute(f"SELECT reltuples FROM pg_class WHERE relname = %s", [table])
                        reltuples = cursor.fetchone()
                        total_rows = reltuples[0] if reltuples else 0

                        estimated_rows = plan_data.get("Plan Rows", 0)
                        selectivity = estimated_rows / total_rows if total_rows > 0 else 1.0

                        if total_rows > 100000 and selectivity < 0.01 and execution_duration > 0.01:
                            parsed = sqlglot.parse_one(sql)
                            where_cols = [
                                col.name for col in parsed.find_all(exp.Column)
                                if parsed.find(exp.Where) and col.find_ancestor(exp.Where)
                            ]
                            if where_cols:
                                suggestion = f"Add index on {table}({', '.join(where_cols)})"
                                suggestions.append(suggestion)

        Query.update_one(
            {"_id": ObjectId(query_id)},
            {"$set": {"index_suggestion": "; ".join(suggestions) if suggestions else None}}
        )

    except Exception as e:
        print(f"Error in analyze_query_for_indexing: {str(e)}")
        raise
