from rest_framework import serializers
from users.serializers import UserSerializer
from .models import Customer, Address, Country, City, WishList
from films.serializers import FilmSerializer
from films.models import Film
from datetime import datetime
from django.db import IntegrityError


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    country = CountrySerializer(many=False)

    class Meta:
        model = City
        fields = '__all__'


class AddressSerializer(serializers.ModelSerializer):
    city = CitySerializer(many=False)

    class Meta:
        model = Address
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    address = AddressSerializer(many=False)

    class Meta:
        model = Customer
        fields = '__all__'


class CustomerAddressUpdateCreateSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()


class RecommendedFilmsSerializer(FilmSerializer):
    actors_films_count_sum = serializers.SerializerMethodField()

    def get_actors_films_count_sum(self, object):
        return object.actors_films_count_sum


class WishListSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True, many=False)
    film = FilmSerializer(read_only=True, many=False)
    film_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = WishList
        fields = '__all__'
        read_only_fields = ['id', 'customer', 'film', 'last_update']

    def create(self, validated_data):
        # Extract film_id from validated_data
        film_id = validated_data.pop('film_id')

        customer = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            customer = user.customer

        # Fetch the Customer and Film instances
        try:
            customer = Customer.objects.get(pk=customer.customer_id)
            film = Film.objects.get(pk=film_id)
        except Customer.DoesNotExist:
            raise serializers.ValidationError({'customer': 'no customer found.'})
        except Film.DoesNotExist:
            raise serializers.ValidationError({'film_id': 'Invalid Film ID.'})

        validated_data['last_update'] = datetime.now()

        # Create the Film instance with the assigned language
        try:
            wishlist = WishList.objects.create(customer=customer, film=film, **validated_data)
        except IntegrityError:
            raise serializers.ValidationError(f'film with id: {film_id} already exists in the customer\'s wishlist.')
        return wishlist
