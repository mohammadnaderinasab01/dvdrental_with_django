from rest_framework import serializers


class QueriesRequestSerializer(serializers.Serializer):
    sort_by = serializers.ChoiceField(
        choices=["execution_duration", "execution_time", "row_affected"],
        required=False,
        error_messages={
            "invalid_choice": "Invalid choice. Allowed values are: execution_duration, execution_time, row_affected."
        }
    )


class QueriesSerializer(serializers.Serializer):
    queries = serializers.ListField()
