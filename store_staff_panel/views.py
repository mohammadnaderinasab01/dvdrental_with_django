from rest_framework import views, viewsets, generics
from payment.models import Rental, Payment
from utils.responses import CustomResponse
from utils.permissions import HasStoreStaffAccessRental, IsStoreStaff
from django.utils import timezone
from customer.models import Customer
from store.models import Staff
from films.models import Film, Inventory
from django.db import transaction
from .serializers import RentFilmSerializer
from drf_spectacular.utils import extend_schema
from django.db.models import Q, Sum
from drf_spectacular.utils import OpenApiParameter, extend_schema
from drf_spectacular.types import OpenApiTypes
import time
from payment.serializers import PaymentSerializer
from django.core.exceptions import ValidationError
from films.serializers import InventorySerializer


class ReturnRentalView(views.APIView):
    permission_classes = [HasStoreStaffAccessRental]

    def post(self, request, pk):
        try:
            rental = Rental.objects.get(rental_id=pk)
            if rental.return_date:
                return CustomResponse.bad_request(f"you've returned rental with id: {pk} before")
            rental.return_date = timezone.now()
            rental.save()
            return CustomResponse.successful_200(f"rental with id: {pk} returned successful")
        except Rental.DoesNotExist:
            return CustomResponse.not_found(f"rental with id: {pk} not found.")


class RentFilmView(views.APIView):
    permission_classes = [IsStoreStaff]

    @extend_schema(request=RentFilmSerializer)
    def post(self, request):
        serializer = RentFilmSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse.bad_request(serializer.errors)

        customer_id = serializer.validated_data.get('customer_id')
        film_id = serializer.validated_data.get('film_id')

        try:
            start_time = time.time()

            customer = Customer.objects.get(customer_id=customer_id)
            staff = Staff.objects.get(user=request.user)
            film = Film.objects.get(film_id=film_id)

            available_inventories = Inventory.objects.filter(
                film_id=film_id, store_id=staff.store_id
            ).filter(
                Q(rental__isnull=True) | Q(rental__return_date__isnull=False)
            ).exclude(
                rental__return_date__isnull=True
            )

            end_time = time.time()
            print(f"Query executed in {end_time - start_time:.4f} seconds")

            if not available_inventories.exists():
                return CustomResponse.not_found(
                    f"no available inventory found for film with id: {film_id} with access of staff: {staff.staff_id}")

            inventory = available_inventories.first()

            with transaction.atomic():
                created_rental = Rental.objects.create(
                    rental_date=timezone.now(),
                    inventory=inventory,
                    customer=customer,
                    staff=staff,
                    last_update=timezone.now(),
                )
                Payment.objects.create(
                    customer=customer,
                    staff=staff,
                    rental=created_rental,
                    amount=film.rental_rate,
                    payment_date=timezone.now()
                )
                return CustomResponse.successful_200(
                    f"renting film with id: {film_id} by inventory with id: {inventory.inventory_id} to customer with id: {customer_id} was successful.")
        except Customer.DoesNotExist:
            return CustomResponse.not_found(f"customer with id: {customer_id} not found.")
        except Staff.DoesNotExist:
            return CustomResponse.not_found(f"staff with user id: {request.user.id} not found.")
        except Film.DoesNotExist:
            return CustomResponse.not_found(f"film with id: {film_id} not found.")
        except:
            return CustomResponse.server_error('An error occurred')


class StaffPaymentView(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsStoreStaff]
    http_method_names = ['get']

    def get_queryset(self):
        staff = self.request.user.staff
        return Payment.objects.filter(staff=staff)


class TotalRevenueView(views.APIView):
    permission_classes = [IsStoreStaff]

    @extend_schema(parameters=[
        OpenApiParameter(name="start_date", type=OpenApiTypes.STR),
        OpenApiParameter(name="end_date", type=OpenApiTypes.STR),
    ])
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        try:
            if start_date and end_date:
                total_revenue = Payment.objects.filter(
                    staff_id=request.user.staff.staff_id,
                    payment_date__range=(start_date, end_date)
                ).aggregate(Sum('amount')).get('amount__sum')
            elif start_date and not end_date:
                end_date = timezone.now()
                total_revenue = Payment.objects.filter(
                    staff_id=request.user.staff.staff_id,
                    payment_date__range=(start_date, end_date)
                ).aggregate(Sum('amount')).get('amount__sum')
            elif not start_date and end_date:
                start_date = timezone.datetime(1990, 1, 1, 0, 0, 0)
                total_revenue = Payment.objects.filter(
                    staff_id=request.user.staff.staff_id,
                    payment_date__range=(start_date, end_date)
                ).aggregate(Sum('amount')).get('amount__sum')
            else:
                total_revenue = Payment.objects.filter(
                    staff_id=request.user.staff.staff_id).aggregate(
                    Sum('amount')).get('amount__sum')
            return CustomResponse.json_response({"total_revenue": float(total_revenue)
                                                 if total_revenue is not None else total_revenue})
        except ValidationError:
            return CustomResponse.bad_request(
                'start_date and end_date must be date. the format is like this: YYYY-MM-DD')


class AddFilmInventoryToStoreView(views.APIView):
    permission_classes = [IsStoreStaff]

    def post(self, request, pk):
        store = request.user.staff.store
        if not store:
            return CustomResponse.bad_request(
                f'staff with id: {request.user.staff.staff_id} does not attend to any store')

        try:
            film = Film.objects.get(film_id=pk)
        except Film.DoesNotExist:
            return CustomResponse.not_found(f'film with id: {pk} not found.')

        inventory = Inventory.objects.create(
            film=film,
            store_id=store.store_id,
            last_update=timezone.now()
        )
        serializer = InventorySerializer(instance=inventory)

        return CustomResponse.successful_201(serializer.data)


class RemoveInventoryFromStoreView(views.APIView):
    permission_classes = [IsStoreStaff]

    def post(self, request, pk):
        store = request.user.staff.store
        if not store:
            return CustomResponse.bad_request(
                f'staff with id: {request.user.staff.staff_id} does not attend to any store')

        try:
            inventory = Inventory.objects.get(inventory_id=pk, store_id=store.store_id)
            inventory.delete()
            return CustomResponse.successful_204_no_content()
        except Inventory.DoesNotExist:
            return CustomResponse.not_found(f'inventory with id: {pk} in store with id: {store.store_id} not found.')


class RemoveAllFilmInventoriesFromStoreView(views.APIView):
    def post(self, request, pk):
        store = request.user.staff.store
        if not store:
            return CustomResponse.bad_request(
                f'staff with id: {request.user.staff.staff_id} does not attend to any store')

        try:
            film = Film.objects.get(film_id=pk)
        except Film.DoesNotExist:
            return CustomResponse.not_found(f'film with id: {pk} in store with id: {store.store_id} not found.')

        film.inventory_set.filter(store_id=store.store_id).delete()

        return CustomResponse.successful_204_no_content()
