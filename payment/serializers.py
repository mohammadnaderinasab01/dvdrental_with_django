from rest_framework import serializers
from .models import Rental, Payment
from store.serializers import StaffSerializer
from films.serializers import InventorySerializer
from customer.serializers import CustomerSerializer


class RentalSerializer(serializers.ModelSerializer):
    staff = StaffSerializer(many=False)
    inventory = InventorySerializer(many=False)
    customer = CustomerSerializer(many=False)

    class Meta:
        model = Rental
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(many=False)
    staff = StaffSerializer(many=False)
    rental = RentalSerializer(many=False)

    class Meta:
        model = Payment
        fields = '__all__'
