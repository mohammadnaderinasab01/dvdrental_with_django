from rest_framework import generics, filters, views
from .models import Film, Actor, Category, Inventory, Language
from .serializers import FilmSerializer, TopRentedFilmsSerializer, ActorSerializer, \
    MostPopularActorsSerializer, CategorySerializer, InventorySerializer, \
    FilmAvailabilityRequestSerializer, MostInUsedLanguagesSerializer, \
    MostPaidForFilmsSerializer
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
import time
from utils.responses import CustomResponse
from utils.pagination import PaginationWithCustomDataFormat
from rest_framework.permissions import IsAdminUser
import decimal


class FilmListView(generics.ListAPIView):
    queryset = Film.objects.all().select_related('language')
    serializer_class = FilmSerializer
    authentication_classes = []
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['release_year', 'language']
    search_fields = ['title', 'description', 'fulltext', 'special_features']
    ordering_fields = ['release_year', 'rental_duration', 'rental_rate',
                       'length', 'replacement_cost', 'rating', 'last_update']

    @extend_schema(parameters=[
        OpenApiParameter(name="search", type=OpenApiTypes.STR)
    ])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = []
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['last_update']

    @extend_schema(parameters=[
        OpenApiParameter(name="search", type=OpenApiTypes.STR)
    ])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ActorListView(generics.ListAPIView):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    authentication_classes = []
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['last_update']

    @extend_schema(parameters=[
        OpenApiParameter(name="search", type=OpenApiTypes.STR)
    ])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class InventoryListView(generics.ListAPIView):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    authentication_classes = []
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['film__title', 'film__description', 'film__fulltext', 'film__special_features']
    ordering_fields = ['last_update']

    @extend_schema(parameters=[
        OpenApiParameter(name="search", type=OpenApiTypes.STR)
    ])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class FilmDetailsView(generics.RetrieveAPIView):
    queryset = Film.objects.all()
    serializer_class = FilmSerializer
    authentication_classes = []


class TopRentedFilmsView(generics.ListAPIView):
    serializer_class = TopRentedFilmsSerializer
    authentication_classes = []

    def get_queryset(self):
        start_time = time.time()
        queryset = Film.objects.annotate(
            rental_count=Count('inventory__rental')).order_by('-rental_count')
        end_time = time.time()
        print(f"Query executed in {end_time - start_time:.4f} seconds")
        return queryset


class MostPaidForFilmsView(generics.ListAPIView):
    serializer_class = MostPaidForFilmsSerializer
    authentication_classes = []

    def get_queryset(self):
        return Film.objects.annotate(total_paid_amount=Coalesce(Sum(
            'inventory__rental__payment__amount'), decimal.Decimal(0))).order_by('-total_paid_amount')


class MostPopularActorsView(generics.ListAPIView):
    serializer_class = MostPopularActorsSerializer
    authentication_classes = []

    def get_queryset(self):
        start_time = time.time()
        queryset = Actor.objects.annotate(
            rental_count=Count('filmactor__film__inventory__rental')).order_by('-rental_count')
        end_time = time.time()
        print(f"Query executed in {end_time - start_time:.4f} seconds")
        return queryset


class FilmAvailabilityView(views.APIView):
    authentication_classes = []

    @extend_schema(parameters=[
        OpenApiParameter(name="store_id", type=OpenApiTypes.STR)
    ])
    def get(self, request, pk):
        request_serializer = FilmAvailabilityRequestSerializer(data=request.GET)
        if not request_serializer.is_valid():
            return CustomResponse.bad_request(request_serializer.errors)
        store_id = request_serializer.validated_data.get('store_id')

        try:
            film = Film.objects.get(film_id=pk)
        except Film.DoesNotExist:
            return CustomResponse.not_found(f"film with id: {pk} not found.")

        inventories = Inventory.objects.filter(film=film, store_id=store_id)

        if inventories.exists():
            return CustomResponse.successful_200(
                f'film with id: {pk} in store with id: {store_id} has {inventories.count()} inventories')
        else:
            return CustomResponse.not_found(f'film with id: {pk} in store with id: {store_id} has no inventory')


class MostInUsedLanguagesView(generics.ListAPIView):
    serializer_class = MostInUsedLanguagesSerializer
    authentication_classes = []

    def get_queryset(self):
        return Language.objects.annotate(total_films_usage=Count("film")).order_by('-total_films_usage')


class FilmActorsView(generics.ListAPIView):
    serializer_class = ActorSerializer
    pagination_class = PaginationWithCustomDataFormat
    authentication_classes = []

    def get_queryset(self):
        film_id = self.kwargs.get('pk')
        return Actor.objects.filter(filmactor__film__film_id=film_id)

    def get(self, request, *args, **kwargs):
        film_id = kwargs.get('pk')

        if not film_id:
            return CustomResponse.bad_request('film_id is required')

        try:
            film = Film.objects.get(film_id=film_id)
            film_serializer = FilmSerializer(instance=film, many=False)
        except:
            return CustomResponse.not_found(f'film with id: {film_id} not found.')

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            actors_serializer = self.get_serializer(page, many=True)
            return CustomResponse.json_response({
                "film": film_serializer.data,
                "actors": self.get_paginated_response(actors_serializer.data)
            })

        actors_serializer = self.get_serializer(queryset, many=True)

        return CustomResponse.json_response({
            "film": film_serializer.data,
            "actors": actors_serializer.data
        })


class FilmCreateView(generics.CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = FilmSerializer


class FilmDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = FilmSerializer
    queryset = Film.objects.all()


class ActorFilmsView(generics.ListAPIView):
    serializer_class = FilmSerializer
    authentication_classes = []
    lookup_field = 'actor_id'

    def get_queryset(self):
        actor_id = self.kwargs.get('actor_id')
        return Film.objects.filter(filmactor__actor__actor_id=actor_id)

    def list(self, request, actor_id, *args, **kwargs):
        try:
            Actor.objects.get(actor_id=actor_id)
        except Actor.DoesNotExist:
            return CustomResponse.not_found(f'actor with id: {actor_id} not found.')
        return super().list(request, *args, **kwargs)
