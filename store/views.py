from rest_framework import viewsets, generics
from .models import Store, Staff
from .serializers import StoreSerializer, StoreForUnAuthenticatedUserSerializer, \
    MostRentingCustomerSerializer
from rest_framework.permissions import IsAuthenticated
from utils.permissions import IsStoreStaff
from films.models import Film
from films.serializers import TopRentedFilmsSerializer
from django.db.models import Count
from customer.models import Customer
from utils.responses import CustomResponse


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
