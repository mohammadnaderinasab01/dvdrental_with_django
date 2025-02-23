from rest_framework import generics, filters
from .models import Film, Actor, Category, Inventory
from .serializers import FilmSerializer, TopRentedFilmsSerializer, ActorSerializer, \
    MostPopularActorsSerializer, CategorySerializer, InventorySerializer
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Count
import time


class FilmListView(generics.ListAPIView):
    queryset = Film.objects.all()
    serializer_class = FilmSerializer
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


class TopRentedFilmsView(generics.ListAPIView):
    serializer_class = TopRentedFilmsSerializer

    def get_queryset(self):
        start_time = time.time()
        queryset = Film.objects.annotate(
            rental_count=Count('inventory__rental')).order_by('-rental_count')
        end_time = time.time()
        print(f"Query executed in {end_time - start_time:.4f} seconds")
        return queryset


class MostPopularActorsView(generics.ListAPIView):
    serializer_class = MostPopularActorsSerializer

    def get_queryset(self):
        start_time = time.time()
        queryset = Actor.objects.annotate(
            rental_count=Count('filmactor__film__inventory__rental')).order_by('-rental_count')
        end_time = time.time()
        print(f"Query executed in {end_time - start_time:.4f} seconds")
        return queryset
