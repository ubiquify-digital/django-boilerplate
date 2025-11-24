from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .mixin import CamelSnakeMixin


class PaginationSerializer(CamelSnakeMixin, serializers.Serializer):
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    total_items = serializers.IntegerField()
    has_next = serializers.BooleanField()
    has_previous = serializers.BooleanField()
    next = serializers.URLField()
    previous = serializers.URLField()
    results = serializers.ListField(child=serializers.DictField())


class StandardResultsSetPagination(PageNumberPagination):
    """
    Custom pagination class with configurable page size.

    Features:
    - Default page size: 10 items
    - Configurable via 'page_size' query parameter
    - Maximum page size: 100 items
    - Page size query parameter: 'page_size'
    - Page query parameter: 'page'
    """

    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 100
    page_query_param = "page"

    def get_paginated_response(self, data):
        """
        Return a paginated style Response object with additional metadata.
        """
        serializer = PaginationSerializer(
            {
                "count": self.page.paginator.count,
                "page": self.page.number,
                "page_size": self.get_page_size(self.request),
                "total_pages": self.page.paginator.num_pages,
                "total_items": self.page.paginator.count,
                "has_next": self.page.has_next(),
                "has_previous": self.page.has_previous(),
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )
        return Response(serializer.data)

    def get_next_link(self):
        """
        Return the next page URL using the same scheme as the request.
        """
        if not self.page.has_next():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.next_page_number()
        return self._replace_query_param(url, self.page_query_param, page_number)

    def get_previous_link(self):
        """
        Return the previous page URL using the same scheme as the request.
        """
        if not self.page.has_previous():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.previous_page_number()
        if page_number == 1:
            return self._remove_query_param(url, self.page_query_param)
        return self._replace_query_param(url, self.page_query_param, page_number)

    def _replace_query_param(self, url, key, value):
        """
        Replace or add a query parameter in the URL.
        """
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        query_params[key] = [str(value)]
        new_query = urlencode(query_params, doseq=True)
        return urlunparse(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment,
            )
        )

    def _remove_query_param(self, url, key):
        """
        Remove a query parameter from the URL.
        """
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        query_params.pop(key, None)
        new_query = urlencode(query_params, doseq=True)
        return urlunparse(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment,
            )
        )

    def get_page_size(self, request):
        """
        Get the page size for this request.
        """
        if self.page_size_query_param:
            page_size = request.query_params.get(self.page_size_query_param)
            if page_size is not None:
                try:
                    page_size = int(page_size)
                    if page_size > 0:
                        if self.max_page_size:
                            return min(page_size, self.max_page_size)
                        return page_size
                except (KeyError, ValueError):
                    pass
        return self.page_size


class AdminPagination(StandardResultsSetPagination):
    """
    Pagination class specifically for admin views with larger default page size.
    """

    page_size = 25
    max_page_size = 200


class LargeResultsPagination(StandardResultsSetPagination):
    """
    Pagination class for views that need to handle larger datasets.
    """

    page_size = 50
    max_page_size = 500
