from rest_framework import serializers


class QueriesRequestSerializer(serializers.Serializer):
    sort_by = serializers.ChoiceField(
        choices=["execution_duration", "execution_time", "row_affected"],
        required=False,
        error_messages={
            "invalid_choice": "Invalid choice. Allowed values are: execution_duration, execution_time, row_affected."
        }
    )
    limit = serializers.IntegerField(default=10)
    skip = serializers.IntegerField(default=0)


class MostSlowQueriesRequestSerializer(serializers.Serializer):
    limit = serializers.IntegerField(default=10)
    skip = serializers.IntegerField(default=0)


class QueriesSerializer(serializers.Serializer):
    queries = serializers.ListField()


class MostSlowQueriesSerializer(serializers.Serializer):
    total_duration = serializers.DecimalField(max_digits=20, decimal_places=20, coerce_to_string=False)
