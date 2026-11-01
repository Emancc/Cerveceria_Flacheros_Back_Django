"""Registro de los modelos de catálogo en el admin."""

from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Cerveza,
    Estilo,
    Ingrediente,
    Lote,
    Proveedor,
    Receta,
    RecetaIngrediente,
)


@admin.register(Estilo)
class EstiloAdmin(admin.ModelAdmin):
    list_display = ("nombre", "slug", "color", "creado_en")
    list_filter = ("creado_en",)
    search_fields = ("nombre", "slug", "descripcion")
    ordering = ("nombre",)
    readonly_fields = ("creado_en", "actualizado_en")
    list_per_page = 20


@admin.register(Cerveza)
class CervezaAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "estilo",
        "graduacion",
        "amargor",
        "precio",
        "stock",
        "activo",
    )
    list_editable = ("precio", "stock", "activo")
    list_filter = ("estilo", "activo")
    search_fields = ("nombre", "estilo__nombre", "descripcion")
    ordering = ("nombre",)
    autocomplete_fields = ("estilo",)
    readonly_fields = ("creado_en", "actualizado_en", "imagen_url")
    date_hierarchy = "creado_en"
    list_per_page = 20

    @admin.display(description="URL de imagen")
    def imagen_url(self, obj):
        if obj.imagen_archivo:
            url = obj.imagen_archivo.url
        elif obj.imagen:
            url = obj.imagen
        else:
            return "-"
        return format_html(
            '<a href="{0}" target="_blank" rel="noopener">{0}</a>',
            url,
        )


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "contacto", "email", "telefono", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre", "contacto", "email", "cuit")
    ordering = ("nombre",)
    readonly_fields = ("creado_en", "actualizado_en")
    list_per_page = 20


@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "tipo",
        "unidad",
        "stock",
        "stock_minimo",
        "proveedor",
    )
    list_filter = ("tipo", "unidad", "proveedor")
    search_fields = ("nombre", "proveedor__nombre")
    ordering = ("nombre",)
    autocomplete_fields = ("proveedor",)
    readonly_fields = ("creado_en", "actualizado_en")
    list_per_page = 20


class RecetaIngredienteInline(admin.TabularInline):
    model = RecetaIngrediente
    extra = 1
    fields = ("ingrediente", "cantidad", "unidad")
    autocomplete_fields = ("ingrediente",)


@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ("cerveza", "nombre", "version", "volumen_litros", "activa")
    list_filter = ("activa", "cerveza__estilo")
    search_fields = ("nombre", "cerveza__nombre")
    ordering = ("cerveza__nombre", "-version")
    autocomplete_fields = ("cerveza",)
    readonly_fields = ("creado_en", "actualizado_en")
    date_hierarchy = "creado_en"
    inlines = [RecetaIngredienteInline]
    list_per_page = 20


@admin.register(RecetaIngrediente)
class RecetaIngredienteAdmin(admin.ModelAdmin):
    list_display = ("receta", "ingrediente", "cantidad", "unidad")
    list_filter = ("unidad", "receta__cerveza")
    search_fields = ("receta__nombre", "ingrediente__nombre")
    ordering = ("receta", "ingrediente__nombre")
    autocomplete_fields = ("receta", "ingrediente")
    list_per_page = 20


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "cerveza",
        "receta",
        "fecha_elaboracion",
        "fecha_vencimiento",
        "volumen_litros",
        "estado",
    )
    list_filter = ("estado", "cerveza__estilo")
    search_fields = ("codigo", "cerveza__nombre", "receta__nombre")
    ordering = ("-fecha_elaboracion",)
    autocomplete_fields = ("cerveza", "receta")
    readonly_fields = ("creado_en", "actualizado_en")
    date_hierarchy = "fecha_elaboracion"
    list_per_page = 20
