"""Serializers de ventas."""

from decimal import Decimal

from rest_framework import serializers

from apps.catalogo.serializers import CervezaResumenSerializer

from .models import Cliente, DetallePedido, Pedido, Resena


class ClienteResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ("id", "nombre", "email")


class ClienteSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    pedidos_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Cliente
        fields = (
            "id",
            "nombre",
            "email",
            "telefono",
            "tipo",
            "tipo_display",
            "direccion",
            "activo",
            "pedidos_count",
        )


class DetallePedidoSerializer(serializers.ModelSerializer):
    cerveza_nombre = serializers.CharField(
        source="cerveza.nombre",
        read_only=True,
    )
    precio_unitario = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
        min_value=Decimal("0"),
    )
    subtotal = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = DetallePedido
        fields = (
            "id",
            "pedido",
            "cerveza",
            "cerveza_nombre",
            "cantidad",
            "precio_unitario",
            "subtotal",
        )


class PedidoSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(
        source="cliente.nombre",
        read_only=True,
    )
    estado_display = serializers.CharField(
        source="get_estado_display",
        read_only=True,
    )
    canal_display = serializers.CharField(
        source="get_canal_display",
        read_only=True,
    )
    cantidad_items = serializers.IntegerField(read_only=True)
    detalles_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Pedido
        fields = (
            "id",
            "cliente",
            "cliente_nombre",
            "fecha_pedido",
            "estado",
            "estado_display",
            "canal",
            "canal_display",
            "notas",
            "total",
            "cantidad_items",
            "detalles_count",
        )
        read_only_fields = ("total", "cantidad_items", "detalles_count")


class PedidoListSerializer(PedidoSerializer):
    """Serializer de listado con cliente y detalles anidados."""

    cliente = ClienteResumenSerializer(read_only=True)
    detalles = DetallePedidoSerializer(many=True, read_only=True)

    class Meta(PedidoSerializer.Meta):
        fields = PedidoSerializer.Meta.fields + ("detalles",)


class ResenaSerializer(serializers.ModelSerializer):
    cerveza_nombre = serializers.CharField(
        source="cerveza.nombre",
        read_only=True,
    )
    cliente_nombre = serializers.CharField(
        source="cliente.nombre",
        read_only=True,
    )

    class Meta:
        model = Resena
        fields = (
            "id",
            "cerveza",
            "cliente",
            "cerveza_nombre",
            "cliente_nombre",
            "puntuacion",
            "comentario",
            "creado_en",
        )


class ResenaListSerializer(ResenaSerializer):
    """Serializer de listado con cerveza y cliente anidados."""

    cerveza = CervezaResumenSerializer(read_only=True)
    cliente = ClienteResumenSerializer(read_only=True)
