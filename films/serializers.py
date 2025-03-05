from rest_framework import serializers
from .models import Film, Language, Actor, Category, Inventory
from datetime import datetime


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'


class FilmSerializer(serializers.ModelSerializer):
    language_id = serializers.IntegerField(write_only=True)
    language = LanguageSerializer(read_only=True, many=False)

    class Meta:
        model = Film
        fields = '__all__'
        read_only_fields = ['film_id', 'last_update', 'rating']

    def create(self, validated_data):
        # Extract language_id from validated_data
        language_id = validated_data.pop('language_id')

        # Fetch the Language instance
        try:
            language = Language.objects.get(pk=language_id)
        except Language.DoesNotExist:
            raise serializers.ValidationError({'language_id': 'Invalid language ID.'})

        validated_data['last_update'] = datetime.now()

        # Create the Film instance with the assigned language
        film = Film.objects.create(language=language, **validated_data)
        return film

    def update(self, instance, validated_data):
        validated_data['last_update'] = datetime.now()
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


class MostPaidForFilmsSerializer(FilmSerializer):
    total_paid_amount = serializers.SerializerMethodField()

    def get_total_paid_amount(self, object):
        try:
            return object.total_paid_amount
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


class MostInUsedLanguagesSerializer(LanguageSerializer):
    total_films_usage = serializers.SerializerMethodField()

    def get_total_films_usage(self, object):
        try:
            return object.total_films_usage
        except:
            return None
