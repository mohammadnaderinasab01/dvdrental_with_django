from rest_framework import viewsets, generics, views
from .models import Store, Staff
from .serializers import StoreSerializer, StoreForUnAuthenticatedUserSerializer, \
    MostRentingCustomerSerializer, NonReturnedFilmsSerializer, \
    TopStoreInventoriesTotalRentingSerializer
from rest_framework.permissions import IsAuthenticated
from utils.permissions import IsStoreStaff
from films.models import Film, Inventory
from films.serializers import TopRentedFilmsSerializer
from django.db.models import Count
from customer.models import Customer
from utils.responses import CustomResponse
from payment.models import Payment
from django.db.models import Sum


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreForUnAuthenticatedUserSerializer
    permission_classes = []
    http_method_names = ['get']


class TopRentedFilmsByStoreView(generics.ListAPIView):
    permission_classes = [IsStoreStaff]
    serializer_class = TopRentedFilmsSerializer

    def get_queryset(self):
        store = self.request.user.staff.store
        if not store:
            return Film.objects.none()
        top_rented_films = Film.objects.filter(inventory__store_id=store.store_id).annotate(
            rental_count=Count('inventory__rental')).order_by('-rental_count')
        return top_rented_films

    def get(self, request, *args, **kwargs):
        store = request.user.staff.store
        if not store:
            return CustomResponse.not_found('no store found related to the staff member.')
        return super().get(request, *args, **kwargs)


class MostRentingCustomerView(generics.ListAPIView):
    permission_classes = [IsStoreStaff]
    serializer_class = MostRentingCustomerSerializer

    def get_queryset(self):
        store = self.request.user.staff.store
        if not store:
            return Customer.objects.none()
        return Customer.objects.filter(
            store_id=store.store_id).annotate(
            films_taken_count=Count('rental')).order_by('-films_taken_count')

    def get(self, request, *args, **kwargs):
        store = request.user.staff.store
        if not store:
            return CustomResponse.not_found('no store found related to the staff member.')
        return super().get(request, *args, **kwargs)


class TotalPaymentAmountForStoreView(views.APIView):
    permission_classes = [IsStoreStaff]

    def get(self, request):
        try:
            staff = request.user.staff
        except Staff.DoesNotExist:
            return CustomResponse.not_found(f'staff not found.')
        total_payment_amount = Payment.objects.filter(staff=staff).aggregate(Sum('amount')).get('amount__sum')
        return CustomResponse.json_response({'total_payment_amount': float(
                total_payment_amount) if total_payment_amount is not None else total_payment_amount})


class NonReturnedFilmInventoriesView(generics.ListAPIView):
    permission_classes = [IsStoreStaff]
    serializer_class = NonReturnedFilmsSerializer

    def get_queryset(self):
        try:
            store = self.request.user.staff.store
        except Store.DoesNotExist:
            return Inventory.objects.none()
        queryset = Inventory.objects.filter(store_id=store.store_id,
                                            rental__return_date__isnull=True).select_related('film').prefetch_related('rental_set')
        return queryset


class TopStoreInventoriesTotalRentingView(generics.ListAPIView):
    permission_classes = [IsStoreStaff]
    serializer_class = TopStoreInventoriesTotalRentingSerializer

    def get_queryset(self):
        try:
            store = self.request.user.staff.store
        except Store.DoesNotExist:
            return Inventory.objects.none()
        queryset = Inventory.objects.filter(
            store_id=store.store_id).annotate(
            total_renting=Count('rental')).order_by('-total_renting')
        return queryset
