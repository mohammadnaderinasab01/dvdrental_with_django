from rest_framework import serializers
from .models import Staff, Store
from customer.serializers import AddressSerializer, CustomerSerializer
from users.serializers import UserSerializer


class StaffSerializer(serializers.ModelSerializer):
    address = AddressSerializer(many=False)
    user = UserSerializer(many=False)

    class Meta:
        model = Staff
        fields = '__all__'


class StoreSerializer(serializers.ModelSerializer):
    address = AddressSerializer(many=False)
    manager_staff = StaffSerializer(many=False)

    class Meta:
        model = Store
        fields = '__all__'


class StoreForUnAuthenticatedUserSerializer(StoreSerializer):
    manager_staff = serializers.CharField()


class MostRentingCustomerSerializer(CustomerSerializer):
    films_taken_count = serializers.SerializerMethodField()

    def get_films_taken_count(self, object):
        try:
            return object.films_taken_count
        except:
            return None
