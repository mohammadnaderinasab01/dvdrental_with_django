from rest_framework import serializers


class RentFilmSerializer(serializers.Serializer):
    customer_id = serializers.CharField(max_length=255)
    film_id = serializers.CharField(max_length=255)
