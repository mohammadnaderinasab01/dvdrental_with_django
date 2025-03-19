from django.db import connection
from pymongo_wrapper.model import Query
import time
from django.utils import timezone
from utils.helpers import convert_uuid_to_string
import sqlglot
from sqlglot import exp


class DatabaseMonitoringMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.queries = []
        self._current_path = None

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
        # print('context: ', type(context))
        result = execute(sql, params, many, context)
        clean_sql_query = self.clean_sql(sql, processed_params)
        # Extract table names from the query
        tables = self.extract_tables(clean_sql_query)

        # Calculate execution time
        execution_duration = time.time() - start_time

        # print("dir(context['cursor']): ", dir(context['connection']))
        # print("vars(context['cursor']): ", vars(context['connection']))

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
            'request_path': self._current_path,
            'tables': tables,
            # 'db_settings': context['connection'].settings_dict,
            # 'cursor': context['cursor']
        })
        return result

    def __call__(self, request):
        self._current_path = request.path
        # Wrap the database execution to capture queries
        with connection.execute_wrapper(self._capture_queries):
            response = self.get_response(request)

        # After the view is called
        # queries = connection.queries
        # print('self.queries: ', self.queries)
        # print('queries: ', queries)
        try:
            # Query.create(queries=[{
            #     "query": query.get('sql'),
            #     "params": query.get('params'),
            #     "execution_time": query.get('execution_time'),
            #     "execution_duration": query.get('execution_duration'),
            # } for query in self.queries])
            Query.create(queries=[query for query in self.queries])
            self.queries = []
            self._current_path = None
        except Exception as e:
            print(str(e))
        # print(f"Executed SQL Query: {query['sql']}")

        return response
