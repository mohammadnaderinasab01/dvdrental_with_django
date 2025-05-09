from rest_framework import serializers
from store.serializers import StoreSerializer
from customer.serializers import CountrySerializer, CustomerSerializer
from films.serializers import FilmSerializer


class TopPerformingStoresSerializer(StoreSerializer):
    total_rental_records = serializers.SerializerMethodField()

    def get_total_rental_records(self, object):
        try:
            return object.total_rental_records
        except:
            return None


class CountriesHavingMostCustomersSerializer(CountrySerializer):
    total_customers = serializers.SerializerMethodField()

    def get_total_customers(self, object):
        try:
            return object.total_customers
        except:
            return None


class AddOrRemoveActorToOrFromFilmRequestSerializer(serializers.Serializer):
    actor_id = serializers.IntegerField()


class FilmScoreSerializer(FilmSerializer):
    total_film_score = serializers.SerializerMethodField()

    def get_total_film_score(self, object):
        try:
            return object.total_film_score
        except:
            return None


class MostRentalDurationAverageCustomersSerializer(CustomerSerializer):
    rental_duration_average = serializers.SerializerMethodField()

    def get_rental_duration_average(self, object):
        try:
            return object.rental_duration_average
        except:
            return None


class MostKeptFilmsListSerializer(FilmSerializer):
    total_rental_duration = serializers.SerializerMethodField()

    def get_total_rental_duration(self, object):
        try:
            return object.total_rental_duration
        except:
            return None


class MostWishedFilmsListSerializer(FilmSerializer):
    total_wished_count = serializers.SerializerMethodField()

    def get_total_wished_count(self, object):
        try:
            return object.total_wished_count
        except:
            return None
