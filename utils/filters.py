from rest_framework import filters
from django.db.models import Q


class DateRangeFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        filterset_fields = getattr(view, 'filterset_fields')

        if not start_date or not end_date:
            return queryset

        queries = []
        for field in filterset_fields:
            queries.append(Q(**{f"{field}__range": (start_date, end_date)}))

        # Combine all Q objects with OR operator
        final_query = queries.pop()
        for query in queries:
            final_query |= query

        return queryset.filter(final_query)
