from django.db import connection
from pymongo_wrapper.model import Query
import time
from django.utils import timezone
from utils.helpers import convert_uuid_to_string
import sqlglot
from sqlglot import exp
import json
from datetime import datetime as dt
from django.apps import apps
from .tasks import analyze_query_for_indexing


class DatabaseMonitoringMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.queries = []
        self.request_path = None
        self.request_execution_datetime = None
        self.response_status_code = None
        self.response_data = None

    def clean_sql(self, sql, params):
        """
        Replace placeholders like %s with dummy values to make the query parsable.
        Also handles named placeholders like %(key)s.
        """
        if isinstance(params, (list, tuple)):
            # Replace positional placeholders (%s) with dummy values
            sql = sql.replace("%s", "'dummy_value'")
        elif isinstance(params, dict):
            # Replace named placeholders (%(key)s) with dummy values
            for key in params.keys():
                sql = sql.replace(f"%({key})s", "'dummy_value'")
        return sql

    def extract_tables(self, sql):
        """
        Extract table names from a SQL query using sqlglot.
        """
        tables = set()
        try:
            # Parse the SQL query
            parsed = sqlglot.parse_one(sql)

            # Find all table references
            for table in parsed.find_all(exp.Table):
                table_name = table.name
                tables.add(table_name)
        except Exception as e:
            print(f"Error parsing SQL: {e}")
        return list(tables)

    def get_model_for_table(self, table_name):
        """
        Find the Django model associated with a table name.
        """
        for model in apps.get_models():
            if model._meta.db_table == table_name:
                return model
        return None

    def is_foreign_key_relationship(self, parent_table, related_table):
        """
        Check if there's a ForeignKey or OneToOneField from parent_table to related_table.
        """
        parent_model = self.get_model_for_table(parent_table)
        if not parent_model:
            return None
        for field in parent_model._meta.get_fields():
            if field.is_relation and (field.one_to_one or field.many_to_one):
                if field.related_model._meta.db_table == related_table:
                    return field.name
        return None

    def is_many_to_many_or_reverse_fk(self, parent_table, related_table):
        """
        Check if there's a ManyToManyField or reverse ForeignKey from parent_table to related_table.
        """
        parent_model = self.get_model_for_table(parent_table)
        related_model = self.get_model_for_table(related_table)
        if not parent_model or not related_model:
            return None
        for field in parent_model._meta.get_fields():
            if field.many_to_many and field.related_model._meta.db_table == related_table:
                return field.name
            if field.is_relation and field.one_to_many and field.related_model._meta.db_table == related_table:
                return field.name
        return None

    def detect_n_plus_one(self, queries):
        """
        Detect N+1 query patterns and suggest select_related or prefetch_related.
        Returns (is_n_plus_one, suggestion).
        """
        query_groups = {}
        for i, query in enumerate(queries):
            sql = query['sql']
            if not sql.strip().upper().startswith('SELECT'):
                continue
            tables = tuple(query['tables'])
            normalized_sql = self.clean_sql(sql, query['params'])
            key = (normalized_sql, tables)
            query_groups.setdefault(key, []).append(i)

        for key, indices in query_groups.items():
            if len(indices) > 1:  # Repeated queries
                tables = key[1]
                if len(tables) == 1:  # Single-table queries
                    related_table = tables[0]
                    for other_query in queries:
                        if other_query['sql'] == queries[indices[0]]['sql']:
                            continue  # Skip same query
                        other_tables = other_query['tables']
                        for parent_table in other_tables:
                            field_name = self.is_foreign_key_relationship(parent_table, related_table)
                            if field_name:
                                return True, f"Use select_related('{field_name}')"
                            field_name = self.is_many_to_many_or_reverse_fk(parent_table, related_table)
                            if field_name:
                                return True, f"Use prefetch_related('{field_name}')"
        return False, None

    def _capture_queries(self, execute, sql, params, many, context):
        # Preprocess params to handle UUIDs
        processed_params = tuple(convert_uuid_to_string(param) for param in params)
        execution_time = timezone.now()
        start_time = time.perf_counter()
        result = execute(sql, params, many, context)
        clean_sql_query = self.clean_sql(sql, processed_params)
        # Extract table names from the query
        tables = self.extract_tables(clean_sql_query)
        execution_duration = time.perf_counter() - start_time
        self.queries.append({
            'sql': sql,
            'params': processed_params,
            'execution_duration': execution_duration,
            'execution_time': execution_time,
            'is_in_transaction': context['connection'].in_atomic_block,
            'db_alias': context['connection'].alias,
            'rows_affected': context['cursor'].rowcount,
            'db_vendor': connection.vendor,
            'needs_rollback': context['connection'].needs_rollback,
            'tables': tables
        })
        return result

    def __call__(self, request):
        self.request_path = request.path
        self.request_execution_datetime = dt.now()
        # Wrap the database execution to capture queries
        with connection.execute_wrapper(self._capture_queries):
            response = self.get_response(request)
            try:
                # self.response_data = response.data
                # json.dumps(self.response_data)

                # Check if the response has a 'data' attribute (e.g., DRF responses)
                self.response_data = getattr(response, 'data', None)
                if self.response_data is not None:
                    json.dumps(self.response_data)  # Ensure it's JSON-serializable
            except (TypeError, ValueError):
                self.response_data = None
            self.response_status_code = response.status_code

        # After the view is called
        self.save_queries()
        return response

    def process_exception(self, request, exception):
        """
        Handle exceptions and save queries before re-raising the exception.
        """
        # Capture queries when an exception occurs
        self.save_queries()
        # Re-raise the exception to let Django handle it further
        raise exception

    def save_queries(self):
        """
        Save captured queries to the database and trigger indexing analysis.
        """
        try:
            is_n_plus_one, n_plus_one_suggestion = self.detect_n_plus_one(self.queries)
            query_doc = Query.create(
                queries=[query for query in self.queries],
                request_path=self.request_path,
                request_execution_datetime=self.request_execution_datetime,
                response_status_code=self.response_status_code,
                response_data=self.response_data,
                is_n_plus_one=is_n_plus_one,
                n_plus_one_suggestion=n_plus_one_suggestion
            )
            # Trigger Celery task
            # analyze_query_for_indexing.delay(str(query_doc["_id"]))
        except Exception as e:
            print(str(e))
        finally:
            # Clear the captured queries and reset state
            self.queries = []
            self.request_path = None
            self.request_execution_datetime = None
            self.response_status_code = None
            self.response_data = None
