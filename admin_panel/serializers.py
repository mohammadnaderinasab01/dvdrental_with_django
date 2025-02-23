from rest_framework import serializers
from store.serializers import StoreSerializer


class TopPerformingStoresSerializer(StoreSerializer):
    total_rental_records = serializers.SerializerMethodField()

    def get_total_rental_records(self, object):
        try:
            return object.total_rental_records
        except:
            return None
