"""Filtros del catálogo."""

import django_filters
from django.db.models import F

from .models import Cerveza, Ingrediente, Lote, Proveedor, Receta


class CervezaFilter(django_filters.FilterSet):
    estilo = django_filters.CharFilter(
        field_name="estilo__slug",
        lookup_expr="iexact",
    )
    activo = django_filters.BooleanFilter(field_name="activo")
    graduacion_min = django_filters.NumberFilter(
        field_name="graduacion",
        lookup_expr="gte",
    )
    graduacion_max = django_filters.NumberFilter(
        field_name="graduacion",
        lookup_expr="lte",
    )
    precio_min = django_filters.NumberFilter(
        field_name="precio",
        lookup_expr="gte",
    )
    precio_max = django_filters.NumberFilter(
        field_name="precio",
        lookup_expr="lte",
    )

    class Meta:
        model = Cerveza
        fields = [
            "estilo",
            "activo",
            "graduacion_min",
            "graduacion_max",
            "precio_min",
            "precio_max",
        ]


class IngredienteFilter(django_filters.FilterSet):
    bajo_minimo = django_filters.BooleanFilter(method="filtrar_bajo_minimo")

    class Meta:
        model = Ingrediente
        fields = ["tipo", "unidad", "proveedor", "bajo_minimo"]

    def filtrar_bajo_minimo(self, queryset, name, value):
        if value is None:
            return queryset
        if value:
            return queryset.filter(stock__lt=F("stock_minimo"))
        return queryset.filter(stock__gte=F("stock_minimo"))


class ProveedorFilter(django_filters.FilterSet):
    class Meta:
        model = Proveedor
        fields = ["activo"]


class RecetaFilter(django_filters.FilterSet):
    class Meta:
        model = Receta
        fields = ["cerveza", "activa"]


class LoteFilter(django_filters.FilterSet):
    fecha_desde = django_filters.DateFilter(
        field_name="fecha_elaboracion",
        lookup_expr="gte",
    )
    fecha_hasta = django_filters.DateFilter(
        field_name="fecha_elaboracion",
        lookup_expr="lte",
    )

    class Meta:
        model = Lote
        fields = ["estado", "cerveza", "fecha_desde", "fecha_hasta"]
