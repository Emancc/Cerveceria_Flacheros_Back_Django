"""Viewsets de ventas."""

from django.db import transaction
from django.db.models import Count
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.catalogo.models import Cerveza
from apps.cuentas.permissions import (
    DetallesPorRol,
    EsAdminOVentas,
    PedidosPorRol,
    ROL_CLIENTE,
    rol_de,
)

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

MENSAJE_SOLO_CLIENTES = "Solo los clientes pueden usar el checkout."


def cliente_del_usuario(usuario):
    """Devuelve (o crea) el Cliente asociado al usuario por su email."""
    nombre = f"{usuario.first_name} {usuario.last_name}".strip()
    if not nombre:
        nombre = usuario.email.split("@")[0]

    cliente, _ = Cliente.objects.get_or_create(
        email=usuario.email,
        defaults={
            "nombre": nombre,
            "tipo": Cliente.Tipo.MINORISTA,
            "activo": True,
        },
    )
    return cliente


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = (
        Cliente.objects.annotate(pedidos_count=Count("pedidos"))
        .order_by("nombre")
    )
    serializer_class = ClienteSerializer
    permission_classes = [EsAdminOVentas]
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
    permission_classes = [PedidosPorRol]
    filterset_class = PedidoFilter
    search_fields = ["cliente__nombre", "cliente__email"]
    ordering_fields = ["fecha_pedido", "total", "estado"]
    ordering = ["-fecha_pedido"]

    def get_queryset(self):
        queryset = super().get_queryset()
        usuario = self.request.user
        if usuario.is_authenticated and rol_de(usuario) == ROL_CLIENTE:
            return queryset.filter(cliente__email__iexact=usuario.email)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PedidoListSerializer
        return PedidoSerializer

    def perform_create(self, serializer):
        usuario = self.request.user
        if rol_de(usuario) == ROL_CLIENTE:
            serializer.save(
                cliente=cliente_del_usuario(usuario),
                estado=Pedido.Estado.PENDIENTE,
                canal=Pedido.Canal.WEB,
            )
            return
        serializer.save()

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
        return Response(PedidoSerializer(pedido, context={"request": request}).data)

    @extend_schema(
        request=inline_serializer(
            name="CheckoutPedido",
            fields={
                "items": serializers.ListField(
                    child=inline_serializer(
                        name="ItemCheckout",
                        fields={
                            "cerveza": serializers.IntegerField(),
                            "cantidad": serializers.IntegerField(min_value=1),
                        },
                    ),
                ),
                "notas": serializers.CharField(required=False, allow_blank=True),
            },
        ),
        responses=PedidoSerializer,
        description=(
            "Crea un pedido para el cliente autenticado con sus líneas de detalle "
            "en una sola operación. El precio unitario se toma del catálogo."
        ),
    )
    @action(detail=False, methods=["post"], url_path="checkout")
    def checkout(self, request):
        if rol_de(request.user) != ROL_CLIENTE:
            return Response(
                {"detail": MENSAJE_SOLO_CLIENTES},
                status=status.HTTP_403_FORBIDDEN,
            )

        items = request.data.get("items")
        if not isinstance(items, list) or not items:
            raise ValidationError(
                {"items": ["Debés enviar al menos un producto."]}
            )

        preparados = {}
        for item in items:
            if not isinstance(item, dict):
                raise ValidationError(
                    {"items": ["Cada ítem debe incluir cerveza y cantidad."]}
                )

            try:
                cantidad = int(item.get("cantidad"))
            except (TypeError, ValueError):
                raise ValidationError(
                    {"items": ["La cantidad debe ser un número entero."]}
                )

            if cantidad < 1:
                raise ValidationError(
                    {"items": ["La cantidad debe ser mayor a cero."]}
                )

            try:
                cerveza = Cerveza.objects.get(pk=item.get("cerveza"))
            except (Cerveza.DoesNotExist, TypeError, ValueError):
                raise ValidationError(
                    {"items": ["Una de las cervezas no existe."]}
                )

            if not cerveza.activo:
                raise ValidationError(
                    {"items": [f'"{cerveza.nombre}" no está disponible.']}
                )

            if cerveza.pk in preparados:
                preparados[cerveza.pk][1] += cantidad
            else:
                preparados[cerveza.pk] = [cerveza, cantidad]

            if preparados[cerveza.pk][1] > cerveza.stock:
                raise ValidationError(
                    {
                        "items": [
                            f'No hay stock suficiente de "{cerveza.nombre}".'
                        ]
                    }
                )

        notas = str(request.data.get("notas") or "").strip()[:500]

        with transaction.atomic():
            pedido = Pedido.objects.create(
                cliente=cliente_del_usuario(request.user),
                estado=Pedido.Estado.PENDIENTE,
                canal=Pedido.Canal.WEB,
                notas=notas,
            )
            for cerveza, cantidad in preparados.values():
                DetallePedido.objects.create(
                    pedido=pedido,
                    cerveza=cerveza,
                    cantidad=cantidad,
                    precio_unitario=cerveza.precio,
                )
            pedido.refresh_from_db()

        return Response(
            PedidoSerializer(pedido, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class DetallePedidoViewSet(viewsets.ModelViewSet):
    queryset = DetallePedido.objects.select_related(
        "pedido__cliente",
        "cerveza",
    ).order_by("pedido", "cerveza__nombre")
    serializer_class = DetallePedidoSerializer
    permission_classes = [DetallesPorRol]
    filterset_class = DetallePedidoFilter
    search_fields = ["cerveza__nombre", "pedido__cliente__nombre"]
    ordering_fields = ["pedido", "cantidad"]
    ordering = ["pedido", "cerveza__nombre"]

    def get_queryset(self):
        queryset = super().get_queryset()
        usuario = self.request.user
        if usuario.is_authenticated and rol_de(usuario) == ROL_CLIENTE:
            return queryset.filter(
                pedido__cliente__email__iexact=usuario.email
            )
        return queryset

    def perform_create(self, serializer):
        usuario = self.request.user
        if rol_de(usuario) != ROL_CLIENTE:
            serializer.save()
            return

        pedido = serializer.validated_data.get("pedido")
        if pedido is None or pedido.cliente.email.lower() != usuario.email.lower():
            raise PermissionDenied("No podés agregar ítems a un pedido ajeno.")

        cerveza = serializer.validated_data.get("cerveza")
        cantidad = serializer.validated_data.get("cantidad") or 0
        if cerveza is not None and cantidad > cerveza.stock:
            raise serializers.ValidationError(
                {"cantidad": ["No hay stock suficiente."]}
            )

        serializer.save(precio_unitario=cerveza.precio)


class ResenaViewSet(viewsets.ModelViewSet):
    queryset = Resena.objects.select_related("cerveza", "cliente").order_by(
        "-creado_en"
    )
    permission_classes = [EsAdminOVentas]
    filterset_class = ResenaFilter
    search_fields = ["cerveza__nombre", "cliente__nombre", "comentario"]
    ordering_fields = ["puntuacion", "creado_en"]
    ordering = ["-creado_en"]

    def get_serializer_class(self):
        if self.action == "list":
            return ResenaListSerializer
        return ResenaSerializer