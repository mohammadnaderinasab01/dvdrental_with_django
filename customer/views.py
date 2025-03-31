from rest_framework import generics, viewsets, views
from rest_framework.permissions import IsAuthenticated
from .models import Address, Customer, WishList
from payment.models import Rental
from payment.serializers import RentalSerializer
from .serializers import AddressSerializer, CustomerAddressUpdateCreateSerializer, \
    RecommendedFilmsSerializer, WishListSerializer, AddScoreToFilmByCustomerRequestSerializer
import time
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from payment.models import Payment
from payment.serializers import PaymentSerializer
from utils.responses import CustomResponse
from films.models import Actor, Film, FilmActor, FilmScore
from django.db.models import Count, Q, Sum, F, OuterRef, Subquery, IntegerField, FloatField
from django.db.models.functions import Coalesce
from django.db import connection
from utils.filters import DateRangeFilter
from utils.validators import valid_date_format
from django.core.exceptions import ValidationError
from django.utils import timezone
from films.serializers import FilmSerializer


class CustomerAddressView(generics.CreateAPIView, generics.RetrieveAPIView,
                          generics.UpdateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['post', 'get', 'put', 'delete']

    @extend_schema(
        request=CustomerAddressUpdateCreateSerializer
    )
    def post(self, request, *args, **kwargs):
        try:
            customer = self.request.user.customer
        except Customer.DoesNotExist:
            return CustomResponse.not_found('no customer instance found for this user')
        if customer.address:
            return CustomResponse.bad_request('you have an address already')
        request_serializer = CustomerAddressUpdateCreateSerializer(data=request.data)
        if request_serializer.is_valid():
            if not Address.objects.filter(address_id=request_serializer.validated_data['address_id']).exists():
                return CustomResponse.not_found(
                    f'No address found with id: {request_serializer.validated_data["address_id"]}')
            customer.address = Address.objects.get(address_id=request_serializer.validated_data['address_id'])
            customer.save()
            response_serializer = AddressSerializer(request.user.customer.address)
            return CustomResponse.successful_200(response_serializer.data)
        return CustomResponse.bad_request(request_serializer.errors)

    def get(self, request, *args, **kwargs):
        try:
            customer = self.request.user.customer
        except Customer.DoesNotExist:
            return CustomResponse.not_found('no customer instance found for this user')
        start_time = time.time()
        if not customer.address:
            return CustomResponse.not_found('No address found for you')
        serializer = AddressSerializer(instance=self.request.user.customer.address)
        end_time = time.time()
        print(f"Query executed in {end_time - start_time:.4f} seconds")
        return CustomResponse.successful_200(serializer.data)

    @extend_schema(
        request=CustomerAddressUpdateCreateSerializer
    )
    def put(self, request, *args, **kwargs):
        try:
            customer = self.request.user.customer
        except Customer.DoesNotExist:
            return CustomResponse.not_found('no customer instance found for this user')
        start_time = time.time()
        if not customer.address:
            return CustomResponse.not_found('No address found for you')
        request_serializer = CustomerAddressUpdateCreateSerializer(data=request.data)
        if request_serializer.is_valid():
            if not Address.objects.filter(address_id=request_serializer.validated_data['address_id']).exists():
                return CustomResponse.not_found(
                    f'No address found with id: {request_serializer.validated_data["address_id"]}')
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
    filter_backends = [DateRangeFilter]
    filterset_fields = ['rental_date', 'return_date']

    def get_queryset(self):
        return Rental.objects.filter(customer=self.request.user.customer)

    @extend_schema(parameters=[
        OpenApiParameter(name="start_date", type=OpenApiTypes.STR),
        OpenApiParameter(name="end_date", type=OpenApiTypes.STR),
    ])
    def get(self, request, *args, **kwargs):
        try:
            start_date = request.query_params.get('start_date', None)
            end_date = request.query_params.get('end_date', None)
            if start_date:
                valid_date_format(start_date)
            if end_date:
                valid_date_format(end_date)
            customer = self.request.user.customer
        except Customer.DoesNotExist:
            return CustomResponse.not_found('no customer instance found for this user')
        except ValidationError as e:
            return CustomResponse.bad_request(e)
        return super().get(request, *args, **kwargs)


class CustomerNonReturnedFilmsView(generics.ListAPIView):
    serializer_class = FilmSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        customer = self.request.user.customer
        return Film.objects.filter(
            inventory__rental__customer=customer,
            inventory__rental__return_date__isnull=True
        ).distinct()

    def list(self, request, *args, **kwargs):
        try:
            customer = request.user.customer
        except Customer.DoesNotExist:
            return CustomResponse.not_found('customer not found.')

        return super().list(request, *args, **kwargs)


class CustomerPaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get_queryset(self):
        try:
            customer = self.request.user.customer
        except Customer.DoesNotExist:
            return Payment.objects.none()
        return Payment.objects.filter(customer=customer)


class CustomerTotalPaymentAmountView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            customer = self.request.user.customer
        except Customer.DoesNotExist:
            return CustomResponse.not_found('no customer instance found for this user')
        total_payment_amount = Payment.objects.filter(customer=customer).aggregate(Sum('amount')).get('amount__sum')
        return CustomResponse.json_response({'total_payment_amount': float(
                total_payment_amount) if total_payment_amount is not None else total_payment_amount})

# normal version
# class FilmRecommendationsForCustomer(generics.ListAPIView):
#     serializer_class = RecommendedFilmsSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):

#         start_time = time.time()

#         customer = self.request.user.customer

#         most_popular_actors = Actor.objects.prefetch_related('filmactor__set', 'filmactor__set__film__set', 'filmactor__set__film__set__inventory__set').annotate(
#             films_count=Count(
#                 'filmactor__film', filter=Q(
#                     filmactor__film__inventory__rental__customer_id=customer.customer_id))).order_by('-films_count').values('actor_id', 'films_count')
#         # print('most_popular_actors query: ', most_popular_actors.query)

#         films_with_actor_films = Film.objects.select_related('language').prefetch_related('filmactor_set', 'filmactor_set__actor').annotate(
#             actors_films_count_sum=Coalesce(Sum(
#                 Subquery(
#                     most_popular_actors.filter(
#                         actor_id=OuterRef('filmactor__actor__actor_id')
#                     ).values('films_count')
#                 )
#             ), 0),
#         ).order_by('-actors_films_count_sum')
#         # films_with_actor_films = Film.objects.select_related('language').prefetch_related('filmactor_set', 'filmactor_set__actor').annotate(
#         #     actors_films_count_sum=Count('filmactor'),
#         # ).order_by('-actors_films_count_sum')
#         # films_with_actor_films = Film.objects.annotate(
#         #     actors_films_count_sum=Coalesce(Sum(
#         #         Subquery(
#         #             most_popular_actors.filter(
#         #                 actor_id=OuterRef('filmactor__actor__actor_id')
#         #             ).values('films_count')
#         #         )
#         #     ), 0),
#         # ).order_by('-actors_films_count_sum')
#         # print('films_with_actor_films query: ', films_with_actor_films.query)

#         print(films_with_actor_films[0])
#         end_time = time.time()
#         print(f"Query executed in {end_time - start_time:.4f} seconds")

#         return films_with_actor_films

#     def list(self, request, *args, **kwargs):
#         print(1)
#         queryset = self.filter_queryset(self.get_queryset())
#         print(2)
#         # Profile the pagination step
#         pagination_start_time = time.time()
#         page = self.paginate_queryset(queryset)
#         pagination_end_time = time.time()
#         print(f'Pagination took {pagination_end_time - pagination_start_time:.4f} seconds')
#         print(3)
#         if page is not None:
#             print(4)
#             serializer = self.get_serializer(page, many=True)
#             print(5)
#             return self.get_paginated_response(serializer.data)
#         print(6)
#         serializer = self.get_serializer(queryset, many=True)
#         print(7)
#         return CustomResponse.successful_200('')


# extra-work version with the help of raw query


class FilmRecommendationsForCustomer(generics.ListAPIView):
    serializer_class = RecommendedFilmsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        start_time = time.time()

        customer = self.request.user.customer

        raw_query = """
            WITH most_popular_actors AS (
                SELECT a.actor_id, COUNT(fa.film_id) AS films_count
                FROM actor a
                JOIN film_actor fa ON a.actor_id = fa.actor_id
                JOIN inventory i ON fa.film_id = i.film_id
                JOIN rental r ON i.inventory_id = r.inventory_id
                WHERE r.customer_id = %s
                GROUP BY a.actor_id
            )
            SELECT f.film_id, f.title, SUM(mpa.films_count) AS actors_films_count_sum
            FROM film f
            JOIN film_actor fa ON f.film_id = fa.film_id
            JOIN most_popular_actors mpa ON fa.actor_id = mpa.actor_id
            GROUP BY f.film_id, f.title
            ORDER BY actors_films_count_sum DESC
        """
        films_with_actor_films = Film.objects.raw(raw_query, [customer.customer_id], translations={
            'actors_films_count_sum': 'actors_films_count_sum'
        })

        end_time = time.time()
        print(f"Query executed in {end_time - start_time:.4f} seconds")

        return films_with_actor_films


class WishListViewSet(viewsets.ModelViewSet):
    queryset = WishList.objects.all()
    serializer_class = WishListSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def destroy(self, request, *args, **kwargs):
        film_id = kwargs.get('film_id')
        try:
            customer_id = request.user.customer.customer_id
            WishList.objects.get(customer__customer_id=customer_id, film__film_id=film_id).delete()
            return CustomResponse.successful_204_no_content()
        except WishList.DoesNotExist:
            return CustomResponse.not_found(
                f'no wishlist found with customer_id: {customer_id} and film_id: {film_id}')
        except Customer.DoesNotExist:
            return CustomResponse.not_found('no customer found.')
        except Film.DoesNotExist:
            return CustomResponse.not_found('no film found.')

    def get_queryset(self):
        try:
            customer = self.request.user.customer
        except Customer.DoesNotExist:
            return WishList.objects.none()
        return WishList.objects.filter(customer=customer)


class AddScoreToFilmByCustomerView(views.APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=AddScoreToFilmByCustomerRequestSerializer)
    def post(self, request, film_id):
        request_serializer = AddScoreToFilmByCustomerRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            return CustomResponse.bad_request(request_serializer.errors)
        score = request_serializer.validated_data.get('score', None)
        try:
            customer = request.user.customer
            film = Film.objects.get(film_id=film_id)
            if not Rental.objects.filter(inventory__film=film, customer=customer).exists():
                return CustomResponse.bad_request(f'you haven\'t rented film with id: {film_id} before')
            FilmScore.objects.get(film=film, customer=customer)
            return CustomResponse.bad_request(f'you\'ve been scored film with id: {film_id} previously.')
        except Customer.DoesNotExist:
            return CustomResponse.not_found('customer not found.')
        except AttributeError:
            return CustomResponse.not_found('error occurred')
        except Film.DoesNotExist:
            return CustomResponse.not_found(f'film with id: {film_id} not found.')
        except FilmScore.DoesNotExist:
            FilmScore.objects.create(
                score=score,
                film=film,
                customer=customer,
                last_update=timezone.now()
            )
            return CustomResponse.successful_201(result=f'your score for film with id: {film_id} successfully added.')

    @extend_schema(request=AddScoreToFilmByCustomerRequestSerializer)
    def put(self, request, film_id):
        request_serializer = AddScoreToFilmByCustomerRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            return CustomResponse.bad_request(request_serializer.errors)
        score = request_serializer.validated_data.get('score', None)
        try:
            customer = request.user.customer
            film = Film.objects.get(film_id=film_id)
            film_score = FilmScore.objects.get(film=film, customer=customer)
            film_score.score = score
            film_score.last_update = timezone.now()
            film_score.save()
            return CustomResponse.successful_200(result=f'your score for film with id: {film_id} successfully updated.')
        except Customer.DoesNotExist:
            return CustomResponse.not_found('customer not found.')
        except AttributeError:
            return CustomResponse.not_found('error occurred')
        except Film.DoesNotExist:
            return CustomResponse.not_found(f'film with id: {film_id} not found.')
        except FilmScore.DoesNotExist:
            return CustomResponse.not_found(f'your film_score for film with id: {film_id} not found.')
