from rest_framework import serializers
from .models import Film, Language, Actor, Category, Inventory
from datetime import datetime


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'


class FilmSerializer(serializers.ModelSerializer):
    language = LanguageSerializer(many=False)

    class Meta:
        model = Film
        fields = '__all__'
        read_only_fields = ['film_id', 'last_update', 'rating']

    def create(self, validated_data):
        validated_data['last_update'] = datetime.now()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    film = FilmSerializer(many=False)

    class Meta:
        model = Inventory
        fields = '__all__'


class TopRentedFilmsSerializer(FilmSerializer):
    rental_count = serializers.SerializerMethodField()

    def get_rental_count(self, object):
        try:
            return object.rental_count
        except:
            return None


class MostPopularActorsSerializer(ActorSerializer):
    rental_count = serializers.SerializerMethodField()

    def get_rental_count(self, object):
        try:
            return object.rental_count
        except:
            return None


class FilmAvailabilityRequestSerializer(serializers.Serializer):
    store_id = serializers.CharField(max_length=255)
