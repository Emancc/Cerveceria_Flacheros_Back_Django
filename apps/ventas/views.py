"""Viewsets de ventas."""

from django.db.models import Count
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import ClienteFilter, DetallePedidoFilter, PedidoFilter, ResenaFilter
from .models import Cliente, DetallePedido, Pedido, Resena
from .serializers import (
    ClienteSerializer,
    DetallePedidoSerializer,
    PedidoListSerializer,
    PedidoSerializer,
    ResenaListSerializer,
    ResenaSerializer,
)


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = (
        Cliente.objects.annotate(pedidos_count=Count("pedidos"))
        .order_by("nombre")
    )
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ClienteFilter
    search_fields = ["nombre", "email", "telefono"]
    ordering_fields = ["nombre", "email"]
    ordering = ["nombre"]


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = (
        Pedido.objects.select_related("cliente")
        .prefetch_related("detalles__cerveza")
        .annotate(detalles_count=Count("detalles"))
        .order_by("-fecha_pedido")
    )
    permission_classes = [IsAuthenticated]
    filterset_class = PedidoFilter
    search_fields = ["cliente__nombre", "cliente__email"]
    ordering_fields = ["fecha_pedido", "total", "estado"]
    ordering = ["-fecha_pedido"]

    def get_serializer_class(self):
        if self.action == "list":
            return PedidoListSerializer
        return PedidoSerializer

    @extend_schema(
        request=inline_serializer(
            name="CambiarEstadoPedido",
            fields={
                "estado": serializers.ChoiceField(choices=Pedido.Estado.choices),
            },
        ),
        responses=PedidoSerializer,
        description="Cambia el estado de un pedido.",
    )
    @action(detail=True, methods=["post"], url_path="cambiar-estado")
    def cambiar_estado(self, request, pk=None):
        pedido = self.get_object()
        estado = request.data.get("estado")
        estados_validos = {valor for valor, _ in Pedido.Estado.choices}

        if estado not in estados_validos:
            return Response(
                {"estado": ["Estado inválido."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pedido.estado = estado
        pedido.save(update_fields=["estado", "actualizado_en"])
        return Response(PedidoSerializer(pedido).data)


class DetallePedidoViewSet(viewsets.ModelViewSet):
    queryset = DetallePedido.objects.select_related(
        "pedido__cliente",
        "cerveza",
    ).order_by("pedido", "cerveza__nombre")
    serializer_class = DetallePedidoSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = DetallePedidoFilter
    search_fields = ["cerveza__nombre", "pedido__cliente__nombre"]
    ordering_fields = ["pedido", "cantidad"]
    ordering = ["pedido", "cerveza__nombre"]


class ResenaViewSet(viewsets.ModelViewSet):
    queryset = Resena.objects.select_related("cerveza", "cliente").order_by(
        "-creado_en"
    )
    permission_classes = [IsAuthenticated]
    filterset_class = ResenaFilter
    search_fields = ["cerveza__nombre", "cliente__nombre", "comentario"]
    ordering_fields = ["puntuacion", "creado_en"]
    ordering = ["-creado_en"]

    def get_serializer_class(self):
        if self.action == "list":
            return ResenaListSerializer
        return ResenaSerializer
