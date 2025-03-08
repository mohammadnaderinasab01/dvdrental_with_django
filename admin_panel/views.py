from rest_framework import generics, viewsets, views, filters
from rest_framework.permissions import IsAdminUser
from customer.models import Customer, Country, WishList
from customer.serializers import CustomerSerializer, WishListSerializer
from payment.models import Rental, Payment
from django.db.models import Count, Q, Sum
from django.utils import timezone
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from django_filters.rest_framework import DjangoFilterBackend
from store.models import Staff, Store
from .serializers import TopPerformingStoresSerializer, CountriesHavingMostCustomersSerializer, \
    AddOrRemoveActorToOrFromFilmRequestSerializer
from store.serializers import StaffSerializer
from utils.responses import CustomResponse
from films.models import Film, Actor, FilmActor


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['store_id']
    search_fields = ['first_name', 'last_name', 'email',
                     'address__address', 'address__address2',
                     'address__district']
    ordering_fields = ['create_date', 'last_update']

    @extend_schema(parameters=[
        OpenApiParameter(name="search", type=OpenApiTypes.STR)
    ])
    @extend_schema(parameters=[
        OpenApiParameter(name="ordering", type=OpenApiTypes.STR)
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class TopRentingCustomersView(generics.ListAPIView):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        return Customer.objects.annotate(rental_count=Count('rental')).order_by('-rental_count')


class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ['get']


class StoreTotalRevenueView(views.APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(parameters=[
        OpenApiParameter(name="start_date", type=OpenApiTypes.STR),
        OpenApiParameter(name="end_date", type=OpenApiTypes.STR),
    ])
    def get(self, request, pk):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        try:
            store = Store.objects.get(store_id=pk)
            if start_date and end_date:
                total_revenue = Payment.objects.filter(
                    staff_id=store.manager_staff.staff_id,
                    payment_date__range=(start_date, end_date)
                ).aggregate(Sum('amount')).get('amount__sum')
            elif start_date and not end_date:
                end_date = timezone.now()
                total_revenue = Payment.objects.filter(
                    staff_id=store.manager_staff.staff_id,
                    payment_date__range=(start_date, end_date)
                ).aggregate(Sum('amount')).get('amount__sum')
            elif not start_date and end_date:
                start_date = timezone.datetime(1990, 1, 1, 0, 0, 0)
                total_revenue = Payment.objects.filter(
                    staff_id=store.manager_staff.staff_id,
                    payment_date__range=(start_date, end_date)
                ).aggregate(Sum('amount')).get('amount__sum')
            else:
                total_revenue = Payment.objects.filter(
                    staff_id=store.manager_staff.staff_id).aggregate(
                    Sum('amount')).get('amount__sum')
            return CustomResponse.json_response({"total_revenue": float(
                total_revenue) if total_revenue is not None else total_revenue})
        except Store.DoesNotExist:
            return CustomResponse.not_found(f'store with id: {pk} not found.')
        except ValidationError:
            return CustomResponse.bad_request(
                'start_date and end_date must be date. the format is like this: YYYY-MM-DD')


class TopPerformingStoresView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = TopPerformingStoresSerializer

    def get_queryset(self):
        queryset = Store.objects.annotate(total_rental_records=Count(
            'manager_staff__rental')).order_by('-total_rental_records')
        return queryset


class CountriesHavingMostCustomersView(generics.ListAPIView):
    serializer_class = CountriesHavingMostCustomersSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Country.objects.annotate(total_customers=Count('city__address__customer')).order_by('-total_customers')


class AddActorToFilmView(views.APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(request=AddOrRemoveActorToOrFromFilmRequestSerializer)
    def post(self, request, pk):
        request_serializer = AddOrRemoveActorToOrFromFilmRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            return CustomResponse.bad_request(request_serializer.errors)
        actor_id = request_serializer.validated_data.get('actor_id')
        try:
            film = Film.objects.get(film_id=pk)
            actor = Actor.objects.get(actor_id=actor_id)
            if FilmActor.objects.filter(film=film, actor=actor).exists():
                return CustomResponse.bad_request(f'actor with id: {actor_id} in film with id: {pk} already exists.')
            FilmActor.objects.create(
                actor=actor,
                film=film,
                last_update=timezone.now()
            )
            return CustomResponse.successful_200(f'actor with id: {actor_id} successfully added to film with id: {pk}.')
        except Film.DoesNotExist:
            return CustomResponse.not_found(f'film with id: {pk} not found.')
        except Actor.DoesNotExist:
            return CustomResponse.not_found(f'actor with id: {actor_id} not found.')
        except:
            return CustomResponse.server_error('an error occurred')


class RemoveActorFromFilmView(views.APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(request=AddOrRemoveActorToOrFromFilmRequestSerializer)
    def post(self, request, pk):
        request_serializer = AddOrRemoveActorToOrFromFilmRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            return CustomResponse.bad_request(request_serializer.errors)
        actor_id = request_serializer.validated_data.get('actor_id')
        try:
            film = Film.objects.get(film_id=pk)
            actor = Actor.objects.get(actor_id=actor_id)
            if not FilmActor.objects.filter(film=film, actor=actor).exists():
                return CustomResponse.bad_request(f'actor with id: {actor_id} in film with id: {pk} does not exist.')
            FilmActor.objects.get(film=film, actor=actor).delete()
            return CustomResponse.successful_200(
                f'actor with id: {actor_id} successfully removed from film with id: {pk}.')
        except Film.DoesNotExist:
            return CustomResponse.not_found(f'film with id: {pk} not found.')
        except Actor.DoesNotExist:
            return CustomResponse.not_found(f'actor with id: {actor_id} not found.')
        except:
            return CustomResponse.server_error('an error occurred')


class WishListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WishList.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = WishListSerializer
