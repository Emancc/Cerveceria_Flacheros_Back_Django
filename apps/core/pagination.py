"""Paginación estándar de la API."""

from rest_framework.pagination import PageNumberPagination


class PaginacionEstandar(PageNumberPagination):
    """Paginación por número de página con tamaño configurable por query param."""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100
