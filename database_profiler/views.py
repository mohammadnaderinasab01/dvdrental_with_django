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

        # Validate inputs
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer.")
        if not isinstance(skip, int) or skip < 0:
            raise ValueError("Skip must be a non-negative integer.")

        try:
            serializer = QueriesSerializer(
                Query.aggregate([
                    {
                        "$match": {
                            "$and": [
                                {
                                    "request_execution_datetime": {"$gte": from_date}
                                },
                                {
                                    "request_execution_datetime": {"$lte": to_date}
                                }
                            ]
                        }
                    },
                    {
                        "$set": {
                            "queries": {
                                "$sortArray": {
                                    "input": "$queries",
                                    "sortBy": {request_serializer.validated_data.get('sort_by') if request_serializer.validated_data.get('sort_by') is not None else 'execution_duration': -1}
                                }
                            }
                        }
                    },
                    {
                        "$sort": {f"queries.0.{request_serializer.validated_data.get('sort_by') if request_serializer.validated_data.get('sort_by') != None else 'execution_duration'}": -1}
                    },
                    {
                        "$limit": limit
                    },
                    {
                        "$skip": skip
                    }
                ]), many=True)

            return CustomResponse.successful_200(serializer.data)
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

        # Validate inputs
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer.")
        if not isinstance(skip, int) or skip < 0:
            raise ValueError("Skip must be a non-negative integer.")

        serializer = SlowQueriesSerializer(
            Query.aggregate([
                {
                    "$match": {
                        "$and": [
                            {
                                "request_execution_datetime": {"$gte": from_date}
                            },
                            {
                                "request_execution_datetime": {"$lte": to_date}
                            },
                            {
                                "total_duration": {
                                    "$gte": float(os.getenv('SLOW_QUERY_DURATION_THRESHOLD_SECONDS'))
                                }
                            }
                        ]
                    }
                },
                {
                    "$addFields": {
                        "total_duration": {
                            "$sum": "$queries.execution_duration"
                        }
                    }
                },
                {
                    "$sort": {"total_duration": -1}
                },
                {
                    "$limit": limit
                },
                {
                    "$skip": skip
                }
            ]), many=True)
        try:
            return CustomResponse.successful_200(serializer.data)
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

        # Validate inputs
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer.")
        if not isinstance(skip, int) or skip < 0:
            raise ValueError("Skip must be a non-negative integer.")

        serializer = MostSlowQueriesSerializer(
            Query.aggregate([
                {
                    "$match": {
                        "$and": [
                            {
                                "request_execution_datetime": {"$gte": from_date}
                            },
                            {
                                "request_execution_datetime": {"$lte": to_date}
                            }
                        ]
                    }
                },
                {
                    "$addFields": {
                        "total_duration": {
                            "$sum": "$queries.execution_duration"
                        }
                    }
                },
                {
                    "$sort": {"total_duration": -1}
                },
                {
                    "$limit": limit
                },
                {
                    "$skip": skip
                }
            ]), many=True)
        try:
            return CustomResponse.successful_200(serializer.data)
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

        # Validate inputs
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer.")
        if not isinstance(skip, int) or skip < 0:
            raise ValueError("Skip must be a non-negative integer.")

        serializer = MostUsedEndpointsSerializer(
            Query.aggregate([
                {
                    "$match": {
                        "$and": [
                            {
                                "request_execution_datetime": {"$gte": from_date}
                            },
                            {
                                "request_execution_datetime": {"$lte": to_date}
                            }
                        ]
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
                    "$sort": {"total_usage": -1}
                },
                {
                    "$limit": limit
                },
                {
                    "$skip": skip
                }
            ]), many=True)
        try:
            return CustomResponse.successful_200(serializer.data)
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

        # Validate inputs
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer.")
        if not isinstance(skip, int) or skip < 0:
            raise ValueError("Skip must be a non-negative integer.")

        serializer = MostUsedTablesSerializer(
            Query.aggregate(
                [
                    {
                        "$match": {
                            "$and": [
                                {
                                    "request_execution_datetime": {"$gte": from_date}
                                },
                                {
                                    "request_execution_datetime": {"$lte": to_date}
                                }
                            ]
                        }
                    },
                    {
                        "$unwind": "$queries"
                    },
                    {
                        "$unwind": "$queries.tables"
                    },
                    {
                        "$group": {
                            "_id": "$queries.tables", "total_usage": {"$sum": 1}
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
                        "$sort": {"total_usage": -1}
                    },
                    {
                        "$limit": limit
                    },
                    {
                        "$skip": skip
                    }
                ]
            ), many=True)
        try:
            return CustomResponse.successful_200(serializer.data)
        except Exception as e:
            print('e: ', str(e))
            return CustomResponse.server_error('')
