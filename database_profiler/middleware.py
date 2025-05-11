from django.db import connection
from pymongo_wrapper.model import Query
import time
from django.utils import timezone
from utils.helpers import convert_uuid_to_string
import sqlglot
from sqlglot import exp
import json


class DatabaseMonitoringMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.queries = []
        self.request_path = None
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
                # Get the table name (handles schema-qualified tables)
                table_name = table.name  # e.g., "user"
                tables.add(table_name)
        except Exception as e:
            print(f"Error parsing SQL: {e}")
        return list(tables)

    def _capture_queries(self, execute, sql, params, many, context):
        # Preprocess params to handle UUIDs
        processed_params = tuple(convert_uuid_to_string(param) for param in params)

        execution_time = timezone.now()

        # Start timing
        start_time = time.time()
        result = execute(sql, params, many, context)

        clean_sql_query = self.clean_sql(sql, processed_params)
        # Extract table names from the query
        tables = self.extract_tables(clean_sql_query)

        # Calculate execution time
        execution_duration = time.time() - start_time

        # Capture the SQL query and its parameters
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
            'tables': tables,
        })
        return result

    def __call__(self, request):
        self.request_path = request.path
        # Wrap the database execution to capture queries
        with connection.execute_wrapper(self._capture_queries):
            response = self.get_response(request)
            try:
                self.response_data = response.data
                json.dumps(self.response_data)  # Ensure it’s serializable
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
        Save captured queries to the database.
        """
        try:
            Query.create(
                queries=[query for query in self.queries],
                request_path=self.request_path,
                response_status_code=self.response_status_code,
                response_data=self.response_data
            )
        except Exception as e:
            print(str(e))
        finally:
            # Clear the captured queries and reset state
            self.queries = []
            self.request_path = None
            self.response_status_code = None
            self.response_data = None
