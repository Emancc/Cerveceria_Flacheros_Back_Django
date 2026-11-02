"""Serializers del catálogo."""

from django.core.files.storage import default_storage
from rest_framework import serializers

from .models import (
    Cerveza,
    Estilo,
    Ingrediente,
    Lote,
    Proveedor,
    Receta,
    RecetaIngrediente,
)


def _url_imagen(obj, contexto) -> str:
    if obj.imagen_archivo:
        request = contexto.get("request")
        url = obj.imagen_archivo.url
        if request is not None:
            return request.build_absolute_uri(url)
        return url
    return obj.imagen or ""


class EstiloSerializer(serializers.ModelSerializer):
    cervezas_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Estilo
        fields = (
            "id",
            "nombre",
            "slug",
            "descripcion",
            "color",
            "cervezas_count",
        )


class CervezaSerializer(serializers.ModelSerializer):

    estilo = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Estilo.objects.all(),
    )
    imagen_archivo = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
    )
    imagen_url = serializers.SerializerMethodField()
    resenas_promedio = serializers.SerializerMethodField()

    class Meta:
        model = Cerveza
        fields = (
            "id",
            "nombre",
            "estilo",
            "graduacion",
            "amargor",
            "descripcion",
            "precio",
            "stock",
            "imagen",
            "imagen_archivo",
            "imagen_url",
            "color",
            "activo",
            "resenas_promedio",
            "creado_en",
            "actualizado_en",
        )
        read_only_fields = ("creado_en", "actualizado_en")

    def validate_imagen_archivo(self, value):
        if not value:
            return value
        if not value.startswith("cervezas/"):
            raise serializers.ValidationError("La ruta debe comenzar con 'cervezas/'.")
        if not default_storage.exists(value):
            raise serializers.ValidationError(
                "No existe un archivo de imagen en la ruta indicada."
            )
        return value

    def get_imagen_url(self, obj) -> str:
        return _url_imagen(obj, self.context)

    def get_resenas_promedio(self, obj) -> float | None:
        return obj.resenas_promedio


class CervezaListSerializer(serializers.ModelSerializer):

    estilo = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    estilo_detalle = EstiloSerializer(source="estilo", read_only=True)
    imagen_url = serializers.SerializerMethodField()
    resenas_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Cerveza
        fields = (
            "id",
            "nombre",
            "estilo",
            "estilo_detalle",
            "graduacion",
            "amargor",
            "precio",
            "stock",
            "imagen",
            "imagen_url",
            "color",
            "activo",
            "resenas_count",
            "creado_en",
        )

    def get_imagen_url(self, obj) -> str:
        return _url_imagen(obj, self.context)


class CervezaResumenSerializer(serializers.ModelSerializer):
    estilo = serializers.SlugRelatedField(slug_field="slug", read_only=True)

    class Meta:
        model = Cerveza
        fields = ("id", "nombre", "estilo")


class ProveedorSerializer(serializers.ModelSerializer):
    ingredientes_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Proveedor
        fields = (
            "id",
            "nombre",
            "contacto",
            "email",
            "telefono",
            "cuit",
            "direccion",
            "activo",
            "ingredientes_count",
        )


class IngredienteSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.CharField(
        source="proveedor.nombre",
        read_only=True,
        allow_null=True,
    )
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    unidad_display = serializers.CharField(
        source="get_unidad_display",
        read_only=True,
    )
    bajo_minimo = serializers.SerializerMethodField()

    class Meta:
        model = Ingrediente
        fields = (
            "id",
            "nombre",
            "tipo",
            "unidad",
            "stock",
            "stock_minimo",
            "proveedor",
            "proveedor_nombre",
            "tipo_display",
            "unidad_display",
            "bajo_minimo",
        )

    def get_bajo_minimo(self, obj) -> bool:
        return obj.stock < obj.stock_minimo


class IngredienteListSerializer(IngredienteSerializer):
    proveedor = ProveedorSerializer(read_only=True)


class RecetaIngredienteSerializer(serializers.ModelSerializer):
    ingrediente_nombre = serializers.CharField(
        source="ingrediente.nombre",
        read_only=True,
    )
    unidad_display = serializers.CharField(
        source="get_unidad_display",
        read_only=True,
    )

    class Meta:
        model = RecetaIngrediente
        fields = (
            "id",
            "ingrediente",
            "ingrediente_nombre",
            "cantidad",
            "unidad",
            "unidad_display",
        )


class RecetaSerializer(serializers.ModelSerializer):
    cerveza_nombre = serializers.CharField(
        source="cerveza.nombre",
        read_only=True,
    )
    ingredientes_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Receta
        fields = (
            "id",
            "cerveza",
            "cerveza_nombre",
            "nombre",
            "version",
            "volumen_litros",
            "notas",
            "activa",
            "ingredientes_count",
        )


class RecetaResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receta
        fields = ("id", "nombre", "version")


class RecetaListSerializer(RecetaSerializer):

    cerveza = CervezaResumenSerializer(read_only=True)
    ingredientes = RecetaIngredienteSerializer(many=True, read_only=True)

    class Meta(RecetaSerializer.Meta):
        fields = RecetaSerializer.Meta.fields + ("ingredientes",)


class LoteSerializer(serializers.ModelSerializer):
    cerveza_nombre = serializers.CharField(
        source="cerveza.nombre",
        read_only=True,
    )
    receta_nombre = serializers.CharField(
        source="receta.nombre",
        read_only=True,
        allow_null=True,
    )
    estado_display = serializers.CharField(
        source="get_estado_display",
        read_only=True,
    )

    class Meta:
        model = Lote
        fields = (
            "id",
            "cerveza",
            "receta",
            "cerveza_nombre",
            "receta_nombre",
            "codigo",
            "fecha_elaboracion",
            "fecha_vencimiento",
            "volumen_litros",
            "estado",
            "estado_display",
            "observaciones",
        )


class LoteListSerializer(LoteSerializer):
    """Serializer de listado con cerveza y receta anidadas."""

    cerveza = CervezaResumenSerializer(read_only=True)
    receta = RecetaResumenSerializer(read_only=True)
