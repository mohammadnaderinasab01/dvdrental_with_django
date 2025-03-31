from rest_framework import serializers


class QueriesSerializer(serializers.Serializer):
    queries = serializers.ListField()
