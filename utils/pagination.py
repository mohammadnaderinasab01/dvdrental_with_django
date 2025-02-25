from rest_framework import pagination
from rest_framework.response import Response


class PaginationWithCustomDataFormat(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return {
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        }
