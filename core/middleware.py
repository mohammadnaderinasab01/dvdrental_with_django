from django.db import connection
from pymongo_wrapper.model import Query


class DatabaseMonitoringMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.queries = []

    def _capture_queries(self, execute, sql, params, many, context):
        # Capture the SQL query and its parameters
        self.queries.append({
            'sql': sql,
            'params': params,
        })
        return execute(sql, params, many, context)

    def __call__(self, request):
        # Wrap the database execution to capture queries
        with connection.execute_wrapper(self._capture_queries):
            response = self.get_response(request)

        # After the view is called
        # queries = connection.queries
        # print('self.queries: ', self.queries)
        # print('queries: ', queries)
        try:
            Query.create(queries=[query.get('sql') for query in self.queries])
            self.queries = []
        except Exception as e:
            print(str(e))
        # print(f"Executed SQL Query: {query['sql']}")

        return response
