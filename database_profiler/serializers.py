from rest_framework import serializers
from datetime import datetime as dt


class QueriesRequestBaseSerializer(serializers.Serializer):
    limit = serializers.IntegerField(default=10)
    skip = serializers.IntegerField(default=0)
    from_date = serializers.DateTimeField(default=dt(1900, 1, 1))
    to_date = serializers.DateTimeField(default=dt.now())

    def validate_limit(self, value):
        if not isinstance(value, int) or value <= 0:
            raise serializers.ValidationError("Limit must be a positive integer.")
        return value

    def validate_skip(self, value):
        if not isinstance(value, int) or value < 0:
            raise serializers.ValidationError("Skip must be a non-negative integer.")
        return value


class QueriesRequestSerializer(QueriesRequestBaseSerializer):
    sort_by = serializers.ChoiceField(
        choices=["execution_duration", "execution_time", "row_affected"],
        required=False,
        error_messages={
            "invalid_choice": "Invalid choice. Allowed values are: execution_duration, execution_time, row_affected."
        }
    )


class QueriesSerializer(serializers.Serializer):
    queries = serializers.ListField()
    request_path = serializers.CharField()
    request_execution_datetime = serializers.DateTimeField()
    response_status_code = serializers.IntegerField()
    response_data = serializers.JSONField()
    is_n_plus_one = serializers.BooleanField()
    n_plus_one_suggestion = serializers.CharField()


class SlowQueriesSerializer(QueriesSerializer):
    total_duration = serializers.DecimalField(max_digits=20, decimal_places=20, coerce_to_string=False)


class MostSlowQueriesSerializer(QueriesSerializer):
    total_duration = serializers.DecimalField(max_digits=20, decimal_places=20, coerce_to_string=False)


class MostUsedEndpointsSerializer(serializers.Serializer):
    total_usage = serializers.IntegerField()
    request_path = serializers.CharField()


class MostUsedTablesSerializer(serializers.Serializer):
    total_usage = serializers.IntegerField()
    table_name = serializers.CharField()


class MostUsedQueriesSerializer(serializers.Serializer):
    total_usage = serializers.IntegerField()
    query = serializers.CharField()
