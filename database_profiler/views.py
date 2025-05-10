from rest_framework import views
from utils.responses import CustomResponse
from pymongo_wrapper.model import Query
from .serializers import QueriesSerializer, QueriesRequestSerializer, SlowQueriesRequestSerializer, \
    MostSlowQueriesSerializer, SlowQueriesSerializer
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

        # Validate inputs
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer.")
        if not isinstance(skip, int) or skip < 0:
            raise ValueError("Skip must be a non-negative integer.")

        serializer = QueriesSerializer(
            Query.aggregate([
                {
                    "$set": {
                        "queries": {
                            "$sortArray": {
                                "input": "$queries",
                                "sortBy": {request_serializer.validated_data.get('sort_by'): -1}
                            }
                        }
                    }
                },
                {
                    "$sort": {f"queries.0.{request_serializer.validated_data.get('sort_by')}": -1}
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


class SlowQueriesView(views.APIView):
    @extend_schema(parameters=[SlowQueriesRequestSerializer])
    def get(self, request):
        request_serializer = SlowQueriesRequestSerializer(data=request.query_params)
        if not request_serializer.is_valid():
            return CustomResponse.bad_request(request_serializer.errors)

        limit = request_serializer.validated_data.get('limit')
        skip = request_serializer.validated_data.get('skip')

        # Validate inputs
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer.")
        if not isinstance(skip, int) or skip < 0:
            raise ValueError("Skip must be a non-negative integer.")

        serializer = SlowQueriesSerializer(
            Query.aggregate([
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
                },
                {
                    "$match": {
                        "total_duration": {
                            "$gte": float(os.getenv('SLOW_QUERY_DURATION_THRESHOLD_SECONDS'))
                        }
                    }
                }
            ]), many=True)
        try:
            return CustomResponse.successful_200(serializer.data)
        except Exception as e:
            print('e: ', str(e))
            return CustomResponse.server_error('')


class MostSlowQueriesView(views.APIView):
    @extend_schema(parameters=[SlowQueriesRequestSerializer])
    def get(self, request):
        request_serializer = SlowQueriesRequestSerializer(data=request.query_params)
        if not request_serializer.is_valid():
            return CustomResponse.bad_request(request_serializer.errors)

        limit = request_serializer.validated_data.get('limit')
        skip = request_serializer.validated_data.get('skip')

        # Validate inputs
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer.")
        if not isinstance(skip, int) or skip < 0:
            raise ValueError("Skip must be a non-negative integer.")

        serializer = MostSlowQueriesSerializer(
            Query.aggregate([
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
                },
                {
                    "$project": {
                        "_id": 0,
                        "queries": 0
                    }
                }
            ]), many=True)
        try:
            return CustomResponse.successful_200(serializer.data)
        except Exception as e:
            print('e: ', str(e))
            return CustomResponse.server_error('')
