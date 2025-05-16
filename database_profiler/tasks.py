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

            if not sql.strip().upper().startswith("SELECT") or len(tables) > 1:
                continue

            with connection.cursor() as cursor:
                try:
                    cursor.execute(f"EXPLAIN (FORMAT JSON) {sql}", params)
                    plan = cursor.fetchall()
                    plan_data = plan[0][0]
                    if isinstance(plan_data, str):
                        plan_json = json.loads(plan_data)
                    elif isinstance(plan_data, list):
                        plan_json = plan_data
                    else:
                        print(f"Unexpected plan_data type: {type(plan_data)}")
                        continue

                    # Find Seq Scan nodes
                    seq_scan_nodes = find_seq_scan_nodes(plan_json[0]["Plan"])
                    print(f"Found {len(seq_scan_nodes)} Seq Scan nodes for query: {sql}")
                    for node in seq_scan_nodes:
                        table = node.get("Relation Name", tables[0])
                        cursor.execute(f"SELECT reltuples FROM pg_class WHERE relname = %s", [table])
                        total_rows = cursor.fetchone()[0] or 0

                        estimated_rows = node.get("Plan Rows", 0)
                        selectivity = estimated_rows / total_rows if total_rows > 0 else 1.0
                        print(
                            f"Table: {table}, Total Rows: {total_rows}, Estimated Rows: {estimated_rows}, Selectivity: {selectivity}")

                        if total_rows > 100000 and selectivity < 0.01 and execution_duration > 0.01:
                            parsed = sqlglot.parse_one(sql)
                            cols = set(
                                col.name for col in parsed.find_all(exp.Column)
                                if col.find_ancestor((exp.Where, exp.Join, exp.Order, exp.Group))
                            )
                            if cols:
                                existing_indexes = check_existing_indexes(cursor, table, cols)
                                missing_cols = cols - existing_indexes
                                if missing_cols:
                                    suggestion = f"CREATE INDEX ON {table}({', '.join(missing_cols)})"
                                    suggestions.append(suggestion)
                                    print(f"Suggested: {suggestion}")
                except Exception as e:
                    print(f"Error analyzing query {sql}: {e}")
                    continue

        query_record.update(index_suggestion="; ".join(suggestions) if suggestions else None)
        print(f"Updated query {query_id} with index_suggestion: {'; '.join(suggestions) if suggestions else None}")

    except Exception as e:
        print(f"Error in analyze_query_for_indexing: {e}")
        raise


def find_seq_scan_nodes(plan):
    """Recursively find all Seq Scan nodes in the query plan."""
    nodes = []
    if plan.get("Node Type") == "Seq Scan":
        nodes.append(plan)
    for subplan in plan.get("Plans", []):
        nodes.extend(find_seq_scan_nodes(subplan))
    return nodes


def check_existing_indexes(cursor, table, columns):
    """Check existing indexes on the table, return indexed columns."""
    cursor.execute("SELECT indexdef FROM pg_indexes WHERE tablename = %s", [table])
    indexed_cols = set()
    for row in cursor.fetchall():
        index_def = row[0].lower()
        for col in columns:
            if f" {col.lower()} " in index_def or f"({col.lower()})" in index_def:
                indexed_cols.add(col)
    return indexed_cols
