from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Address, Customer
from payment.models import Rental
from payment.serializers import RentalSerializer
from .serializers import AddressSerializer, CustomerAddressUpdateCreateSerializer
import time
from drf_spectacular.utils import extend_schema
from payment.models import Payment
from payment.serializers import PaymentSerializer
from utils.responses import CustomResponse


class CustomerAddressView(generics.CreateAPIView, generics.RetrieveAPIView,
                          generics.UpdateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['post', 'get', 'put', 'delete']

    @extend_schema(
        request=CustomerAddressUpdateCreateSerializer
    )
    def post(self, request, *args, **kwargs):
        if self.request.user.customer.address:
            return CustomResponse.bad_request('you have an address already')
        request_serializer = CustomerAddressUpdateCreateSerializer(data=request.data)
        if request_serializer.is_valid():
            if not Address.objects.filter(address_id=request_serializer.validated_data['address_id']).exists():
                return CustomResponse.not_found(
                    f'No address found with id: {request_serializer.validated_data["address_id"]}')
            customer = request.user.customer
            customer.address = Address.objects.get(address_id=request_serializer.validated_data['address_id'])
            customer.save()
            response_serializer = AddressSerializer(request.user.customer.address)
            return CustomResponse.successful_200(response_serializer.data)
        return CustomResponse.bad_request(request_serializer.errors)

    def get(self, request, *args, **kwargs):
        start_time = time.time()
        if not self.request.user.customer.address:
            return CustomResponse.not_found('No address found for you')
        serializer = AddressSerializer(instance=self.request.user.customer.address)
        end_time = time.time()
        print(f"Query executed in {end_time - start_time:.4f} seconds")
        return CustomResponse.successful_200(serializer.data)

    @extend_schema(
        request=CustomerAddressUpdateCreateSerializer
    )
    def put(self, request, *args, **kwargs):
        start_time = time.time()
        if not self.request.user.customer.address:
            return CustomResponse.not_found('No address found for you')
        request_serializer = CustomerAddressUpdateCreateSerializer(data=request.data)
        if request_serializer.is_valid():
            if not Address.objects.filter(address_id=request_serializer.validated_data['address_id']).exists():
                return CustomResponse.not_found(
                    f'No address found with id: {request_serializer.validated_data["address_id"]}')
            customer = request.user.customer
            customer.address = Address.objects.get(address_id=request_serializer.validated_data['address_id'])
            customer.save()
            response_serializer = AddressSerializer(request.user.customer.address)
            end_time = time.time()
            print(f"Query executed in {end_time - start_time:.4f} seconds")
            return CustomResponse.successful_200(response_serializer.data)
        return CustomResponse.bad_request(request_serializer.errors)

    def delete(self, request, *args, **kwargs):
        if not self.request.user.customer.address:
            return CustomResponse.not_found('No address found for you')
        customer = request.user.customer
        customer.address = None
        customer.save()
        return CustomResponse.successful_204_no_content()


class CustomerRentalView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RentalSerializer

    def get_queryset(self):
        return Rental.objects.filter(customer=self.request.user.customer)


class CustomerPaymentView(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get_queryset(self):
        customer = self.request.user.customer
        return Payment.objects.filter(customer=customer)
