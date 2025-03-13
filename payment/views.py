from rest_framework import generics
from .models import Rental
from .serializers import RentalSerializer
from rest_framework import filters
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.permissions import IsAdminUser


class RentalListView(generics.ListAPIView):
    queryset = Rental.objects.all()
    serializer_class = RentalSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['customer__first_name', 'customer__last_name', 'customer__email',
                     'inventory__film__title', 'inventory__film__description',
                     'inventory__film__fulltext', 'inventory__film__special_features',
                     'staff__first_name', 'staff__last_name', 'staff__email', 'staff__username']
    ordering_fields = ['return_date', 'last_update']

    @extend_schema(parameters=[
        OpenApiParameter(name="search", type=OpenApiTypes.STR)
    ])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class RentalDetailsView(generics.RetrieveAPIView):
    queryset = Rental.objects.all()
    serializer_class = RentalSerializer
    permission_classes = [IsAdminUser]
