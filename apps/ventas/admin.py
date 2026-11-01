"""Registro de los modelos de ventas en el admin."""

from django.contrib import admin

from .models import Cliente, DetallePedido, Pedido, Resena


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "email", "telefono", "tipo", "activo")
    list_filter = ("tipo", "activo")
    search_fields = ("nombre", "email", "telefono")
    ordering = ("nombre",)
    readonly_fields = ("creado_en", "actualizado_en")
    date_hierarchy = "creado_en"
    list_per_page = 20


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1
    fields = ("cerveza", "cantidad", "precio_unitario", "subtotal")
    readonly_fields = ("subtotal",)
    autocomplete_fields = ("cerveza",)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cliente",
        "fecha_pedido",
        "estado",
        "canal",
        "total",
        "cantidad_items",
    )
    list_filter = ("estado", "canal", "fecha_pedido")
    search_fields = ("cliente__nombre", "cliente__email", "notas")
    ordering = ("-fecha_pedido",)
    autocomplete_fields = ("cliente",)
    readonly_fields = ("total", "cantidad_items", "creado_en", "actualizado_en")
    date_hierarchy = "fecha_pedido"
    inlines = [DetallePedidoInline]
    list_per_page = 20


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = (
        "pedido",
        "cerveza",
        "cantidad",
        "precio_unitario",
        "subtotal",
    )
    list_filter = ("cerveza__estilo",)
    search_fields = ("pedido__cliente__nombre", "cerveza__nombre")
    ordering = ("pedido", "cerveza__nombre")
    autocomplete_fields = ("pedido", "cerveza")
    readonly_fields = ("subtotal",)
    list_per_page = 20


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ("cerveza", "cliente", "puntuacion", "creado_en")
    list_filter = ("puntuacion", "cerveza__estilo")
    search_fields = ("cerveza__nombre", "cliente__nombre", "comentario")
    ordering = ("-creado_en",)
    autocomplete_fields = ("cerveza", "cliente")
    readonly_fields = ("creado_en", "actualizado_en")
    date_hierarchy = "creado_en"
    list_per_page = 20
