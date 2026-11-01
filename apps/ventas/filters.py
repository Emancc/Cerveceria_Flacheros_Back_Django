"""Filtros de ventas."""

import django_filters

from .models import Cliente, DetallePedido, Pedido, Resena


class ClienteFilter(django_filters.FilterSet):
    class Meta:
        model = Cliente
        fields = ["tipo", "activo"]


class PedidoFilter(django_filters.FilterSet):
    fecha_desde = django_filters.DateFilter(
        field_name="fecha_pedido",
        lookup_expr="date__gte",
    )
    fecha_hasta = django_filters.DateFilter(
        field_name="fecha_pedido",
        lookup_expr="date__lte",
    )

    class Meta:
        model = Pedido
        fields = ["estado", "canal", "cliente", "fecha_desde", "fecha_hasta"]


class DetallePedidoFilter(django_filters.FilterSet):
    class Meta:
        model = DetallePedido
        fields = ["pedido", "cerveza"]


class ResenaFilter(django_filters.FilterSet):
    puntuacion_min = django_filters.NumberFilter(
        field_name="puntuacion",
        lookup_expr="gte",
    )

    class Meta:
        model = Resena
        fields = ["cerveza", "cliente", "puntuacion_min"]
