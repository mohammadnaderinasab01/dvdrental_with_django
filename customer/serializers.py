from rest_framework import serializers
from users.serializers import UserSerializer
from .models import Customer, Address, Country, City


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
