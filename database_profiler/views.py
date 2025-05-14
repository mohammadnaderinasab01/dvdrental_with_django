from rest_framework import views
from utils.responses import CustomResponse
from pymongo_wrapper.model import Query
from .serializers import QueriesSerializer, QueriesRequestSerializer, QueriesRequestBaseSerializer, \
    MostSlowQueriesSerializer, SlowQueriesSerializer, MostUsedEndpointsSerializer, MostUsedTablesSerializer
from drf_spectacular.utils import extend_schema
import os
from dotenv import load_dotenv

load_dotenv()


class QueriesView(views.APIView):
    @extend_schema(parameters=[QueriesRequestSerializer])
    def get(self, request):
        request_serializer = QueriesRequestSerializer(data=request.query_params)
        if not request_serializer.is_valid():
            return CustomResponse.bad_request(request_serializer.errors)

        limit = request_serializer.validated_data.get('limit')
        skip = request_serializer.validated_data.get('skip')
        from_date = request_serializer.validated_data.get('from_date')
        to_date = request_serializer.validated_data.get('to_date')
        sort_by = request_serializer.validated_data.get('sort_by') or 'execution_duration'

        result = list(
            Query.aggregate([
                {
                    "$match": {
                        "request_execution_datetime": {"$gte": from_date, "$lte": to_date}
                    }
                },
                {
                    "$set": {
                        "queries": {
                            "$sortArray": {
                                "input": "$queries",
                                "sortBy": {sort_by: -1}
                            }
                        }
                    }
                },
                {
                    "$facet": {
                        "results": [
                            {"$sort": {f"queries.0.{sort_by}": -1}},
                            {"$skip": skip},
                            {"$limit": limit}
                        ],
                        "count": [{"$count": "total"}]
                    }
                },
                {
                    "$project": {
                        "results": 1,
                        "count": {"$arrayElemAt": ["$count.total", 0]}
                    }
                }
            ])
        )[0]

        try:
            serializer = QueriesSerializer(result["results"], many=True)
            response_data = {"count": result["count"], "results": serializer.data}
            return CustomResponse.successful_200(response_data)
        except Exception as e:
            print('e: ', str(e))
            return CustomResponse.server_error('')


class SlowQueriesView(views.APIView):
    @extend_schema(parameters=[QueriesRequestBaseSerializer])
    def get(self, request):
        request_serializer = QueriesRequestBaseSerializer(data=request.query_params)
        if not request_serializer.is_valid():
            return CustomResponse.bad_request(request_serializer.errors)

        limit = request_serializer.validated_data.get('limit')
        skip = request_serializer.validated_data.get('skip')
        from_date = request_serializer.validated_data.get('from_date')
        to_date = request_serializer.validated_data.get('to_date')

        result = list(
            Query.aggregate([
                {
                    "$match": {
                        "request_execution_datetime": {"$gte": from_date, "$lte": to_date}
                    }
                },
                {
                    "$addFields": {
                        "total_duration": {"$sum": "$queries.execution_duration"}
                    }
                },
                {
                    "$match": {
                        "total_duration": {"$gte": float(os.getenv('SLOW_QUERY_DURATION_THRESHOLD_SECONDS'))}
                    }
                },
                {
                    "$facet": {
                        "results": [
                            {"$sort": {"total_duration": -1}},
                            {"$skip": skip},
                            {"$limit": limit}
                        ],
                        "count": [{"$count": "total"}]
                    }
                },
                {
                    "$project": {
                        "results": 1,
                        "count": {"$arrayElemAt": ["$count.total", 0]}
                    }
                }
            ])
        )[0]

        try:
            serializer = SlowQueriesSerializer(result["results"], many=True)
            response_data = {"count": result["count"], "results": serializer.data}
            return CustomResponse.successful_200(response_data)
        except Exception as e:
            print('e: ', str(e))
            return CustomResponse.server_error('')


class MostSlowQueriesView(views.APIView):
    @extend_schema(parameters=[QueriesRequestBaseSerializer])
    def get(self, request):
        request_serializer = QueriesRequestBaseSerializer(data=request.query_params)
        if not request_serializer.is_valid():
            return CustomResponse.bad_request(request_serializer.errors)

        limit = request_serializer.validated_data.get('limit')
        skip = request_serializer.validated_data.get('skip')
        from_date = request_serializer.validated_data.get('from_date')
        to_date = request_serializer.validated_data.get('to_date')

        result = list(
            Query.aggregate([
                {
                    "$match": {
                        "request_execution_datetime": {"$gte": from_date, "$lte": to_date}
                    }
                },
                {
                    "$addFields": {
                        "total_duration": {"$sum": "$queries.execution_duration"}
                    }
                },
                {
                    "$facet": {
                        "results": [
                            {"$sort": {"total_duration": -1}},
                            {"$skip": skip},
                            {"$limit": limit}
                        ],
                        "count": [{"$count": "total"}]
                    }
                },
                {
                    "$project": {
                        "results": 1,
                        "count": {"$arrayElemAt": ["$count.total", 0]}
                    }
                }
            ])
        )[0]

        try:
            serializer = MostSlowQueriesSerializer(result["results"], many=True)
            response_data = {"count": result["count"], "results": serializer.data}
            return CustomResponse.successful_200(response_data)
        except Exception as e:
            print('e: ', str(e))
            return CustomResponse.server_error('')


class MostUsedEndpointsView(views.APIView):
    @extend_schema(parameters=[QueriesRequestBaseSerializer])
    def get(self, request):
        request_serializer = QueriesRequestBaseSerializer(data=request.query_params)
        if not request_serializer.is_valid():
            return CustomResponse.bad_request(request_serializer.errors)

        limit = request_serializer.validated_data.get('limit')
        skip = request_serializer.validated_data.get('skip')
        from_date = request_serializer.validated_data.get('from_date')
        to_date = request_serializer.validated_data.get('to_date')

        result = list(
            Query.aggregate([
                {
                    "$match": {
                        "request_execution_datetime": {"$gte": from_date, "$lte": to_date}
                    }
                },
                {
                    "$group": {
                        "_id": "$request_path",
                        "total_usage": {"$sum": 1}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "request_path": "$_id",
                        "total_usage": 1
                    }
                },
                {
                    "$facet": {
                        "results": [
                            {"$sort": {"total_usage": -1}},
                            {"$skip": skip},
                            {"$limit": limit}
                        ],
                        "count": [{"$count": "total"}]
                    }
                },
                {
                    "$project": {
                        "results": 1,
                        "count": {"$arrayElemAt": ["$count.total", 0]}
                    }
                }
            ])
        )[0]

        try:
            serializer = MostUsedEndpointsSerializer(result["results"], many=True)
            response_data = {"count": result["count"], "results": serializer.data}
            return CustomResponse.successful_200(response_data)
        except Exception as e:
            print('e: ', str(e))
            return CustomResponse.server_error('')


class MostUsedTablesView(views.APIView):
    @extend_schema(parameters=[QueriesRequestBaseSerializer])
    def get(self, request):
        request_serializer = QueriesRequestBaseSerializer(data=request.query_params)
        if not request_serializer.is_valid():
            return CustomResponse.bad_request(request_serializer.errors)

        limit = request_serializer.validated_data.get('limit')
        skip = request_serializer.validated_data.get('skip')
        from_date = request_serializer.validated_data.get('from_date')
        to_date = request_serializer.validated_data.get('to_date')

        result = list(
            Query.aggregate([
                {
                    "$match": {
                        "request_execution_datetime": {"$gte": from_date, "$lte": to_date}
                    }
                },
                {"$unwind": "$queries"},
                {"$unwind": "$queries.tables"},
                {
                    "$group": {
                        "_id": "$queries.tables",
                        "total_usage": {"$sum": 1}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "table_name": "$_id",
                        "total_usage": 1
                    }
                },
                {
                    "$facet": {
                        "results": [
                            {"$sort": {"total_usage": -1}},
                            {"$skip": skip},
                            {"$limit": limit}
                        ],
                        "count": [{"$count": "total"}]
                    }
                },
                {
                    "$project": {
                        "results": 1,
                        "count": {"$arrayElemAt": ["$count.total", 0]}
                    }
                }
            ])
        )[0]

        try:
            serializer = MostUsedTablesSerializer(result["results"], many=True)
            response_data = {"count": result["count"], "results": serializer.data}
            return CustomResponse.successful_200(response_data)
        except Exception as e:
            print('e: ', str(e))
            return CustomResponse.server_error('')


class SelectOrPrefetchRelatedPotentialCandidateEndpointsView(views.APIView):
    @extend_schema(parameters=[QueriesRequestBaseSerializer])
    def get(self, request):
        request_serializer = QueriesRequestBaseSerializer(data=request.query_params)
        if not request_serializer.is_valid():
            return CustomResponse.bad_request(request_serializer.errors)

        limit = request_serializer.validated_data.get('limit')
        skip = request_serializer.validated_data.get('skip')
        from_date = request_serializer.validated_data.get('from_date')
        to_date = request_serializer.validated_data.get('to_date')

        result = list(
            Query.aggregate([
                {
                    "$match": {
                        "request_execution_datetime": {"$gte": from_date, "$lte": to_date},
                        "is_n_plus_one": True
                    }
                },
                {
                    "$facet": {
                        "results": [
                            {"$skip": skip},
                            {"$limit": limit}
                        ],
                        "count": [{"$count": "total"}]
                    }
                },
                {
                    "$project": {
                        "results": 1,
                        "count": {"$arrayElemAt": ["$count.total", 0]}
                    }
                }
            ])
        )[0]

        try:
            serializer = QueriesSerializer(result["results"], many=True)
            response_data = {"count": result["count"], "results": serializer.data}
            return CustomResponse.successful_200(response_data)
        except Exception as e:
            print('e: ', str(e))
            return CustomResponse.server_error('')
