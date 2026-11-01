"""Viewsets del catálogo."""

from datetime import timedelta
from uuid import uuid4

from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import Avg, Count, Sum
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from PIL import Image, UnidentifiedImageError
from rest_framework import filters, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .filters import (
    CervezaFilter,
    IngredienteFilter,
    LoteFilter,
    ProveedorFilter,
    RecetaFilter,
)
from .models import Cerveza, Estilo, Ingrediente, Lote, Proveedor, Receta
from .serializers import (
    CervezaListSerializer,
    CervezaSerializer,
    EstiloSerializer,
    IngredienteListSerializer,
    IngredienteSerializer,
    LoteListSerializer,
    LoteSerializer,
    ProveedorSerializer,
    RecetaListSerializer,
    RecetaSerializer,
)


class EstiloViewSet(viewsets.ModelViewSet):
    queryset = (
        Estilo.objects.annotate(cervezas_count=Count("cervezas"))
        .order_by("nombre")
    )
    serializer_class = EstiloSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ["nombre", "slug"]
    ordering_fields = ["nombre"]
    ordering = ["nombre"]


PESO_MAXIMO_IMAGEN = 5 * 1024 * 1024
EXTENSIONES_POR_FORMATO = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}


class CervezaViewSet(viewsets.ModelViewSet):
    queryset = (
        Cerveza.objects.select_related("estilo")
        .annotate(resenas_count=Count("resenas"))
        .order_by("nombre")
    )
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = CervezaFilter
    search_fields = ["nombre", "descripcion", "estilo__nombre"]
    ordering_fields = [
        "nombre",
        "precio",
        "stock",
        "graduacion",
        "amargor",
        "creado_en",
    ]
    ordering = ["nombre"]

    def get_serializer_class(self):
        if self.action == "list":
            return CervezaListSerializer
        return CervezaSerializer

    def perform_update(self, serializer):
        ruta_anterior = (
            serializer.instance.imagen_archivo.name
            if serializer.instance.imagen_archivo
            else ""
        )
        instancia = serializer.save()
        ruta_nueva = (
            instancia.imagen_archivo.name if instancia.imagen_archivo else ""
        )
        if ruta_anterior and ruta_anterior != ruta_nueva:
            default_storage.delete(ruta_anterior)

    @extend_schema(
        request=inline_serializer(
            name="SubidaImagenCerveza",
            fields={"imagen": serializers.FileField()},
        ),
        responses={
            201: inline_serializer(
                name="ImagenCervezaSubida",
                fields={
                    "ruta": serializers.CharField(),
                    "url": serializers.URLField(),
                },
            ),
        },
        description=(
            "Sube una imagen de cerveza (JPEG, PNG o WEBP, hasta 5 MB y "
            "mínimo 200x200 px). Devuelve la ruta relativa para asignarla "
            "al campo `imagen_archivo` de una cerveza."
        ),
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="imagenes",
        permission_classes=[IsAuthenticated],
        parser_classes=[MultiPartParser, FormParser],
    )
    def imagenes(self, request):
        if not request.user.is_staff:
            return Response(
                {"detail": "No tenés permisos para subir imágenes."},
                status=status.HTTP_403_FORBIDDEN,
            )

        archivo = request.FILES.get("imagen")
        if archivo is None:
            return Response(
                {"imagen": ["Debés adjuntar un archivo en el campo 'imagen'."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if archivo.size > PESO_MAXIMO_IMAGEN:
            return Response(
                {"imagen": ["La imagen no puede superar los 5 MB."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            imagen = Image.open(archivo)
            formato = (imagen.format or "").upper()
            ancho, alto = imagen.size
            imagen.verify()
        except (UnidentifiedImageError, OSError, ValueError):
            return Response(
                {"imagen": ["El archivo no es una imagen válida."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if formato not in EXTENSIONES_POR_FORMATO:
            return Response(
                {
                    "imagen": [
                        "Solo se permiten imágenes en formato JPEG, PNG o WEBP."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if ancho < 200 or alto < 200:
            return Response(
                {
                    "imagen": [
                        "La imagen debe medir al menos 200x200 píxeles."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        archivo.seek(0)
        extension = EXTENSIONES_POR_FORMATO[formato]
        ruta = default_storage.save(
            f"cervezas/{timezone.now():%Y/%m}/{uuid4().hex}{extension}",
            archivo,
        )
        return Response(
            {
                "ruta": ruta,
                "url": request.build_absolute_uri(settings.MEDIA_URL + ruta),
            },
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        responses=inline_serializer(
            name="EstadisticasCerveza",
            fields={
                "total": serializers.IntegerField(),
                "estilos": serializers.IntegerField(),
                "stockTotal": serializers.IntegerField(),
                "precioPromedio": serializers.FloatField(),
            },
        ),
        description="Estadísticas agregadas del catálogo de cervezas.",
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="estadisticas",
        permission_classes=[IsAuthenticated],
    )
    def estadisticas(self, request):
        agregados = Cerveza.objects.aggregate(
            total=Count("id"),
            estilos=Count("estilo", distinct=True),
            stock_total=Sum("stock"),
            precio_promedio=Avg("precio"),
        )
        return Response(
            {
                "total": agregados["total"] or 0,
                "estilos": agregados["estilos"] or 0,
                "stockTotal": int(agregados["stock_total"] or 0),
                "precioPromedio": round(
                    float(agregados["precio_promedio"] or 0),
                    2,
                ),
            }
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="umbral",
                type=OpenApiTypes.INT,
                required=False,
                description="Umbral de stock (por defecto 10).",
            ),
        ],
        responses=CervezaListSerializer(many=True),
        description="Lista paginada de cervezas con stock menor al umbral.",
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="bajo-stock",
        permission_classes=[IsAuthenticated],
    )
    def bajo_stock(self, request):
        try:
            umbral = int(request.query_params.get("umbral", 10))
        except (TypeError, ValueError):
            return Response(
                {"umbral": ["Debe ser un número entero."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(stock__lt=umbral).order_by("stock")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CervezaListSerializer(
                page, many=True, context=self.get_serializer_context()
            )
            return self.get_paginated_response(serializer.data)
        serializer = CervezaListSerializer(
            queryset, many=True, context=self.get_serializer_context()
        )
        return Response(serializer.data)


class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = (
        Proveedor.objects.annotate(ingredientes_count=Count("ingredientes"))
        .order_by("nombre")
    )
    serializer_class = ProveedorSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ProveedorFilter
    search_fields = ["nombre", "contacto", "email", "cuit"]
    ordering_fields = ["nombre"]
    ordering = ["nombre"]


class IngredienteViewSet(viewsets.ModelViewSet):
    queryset = Ingrediente.objects.select_related("proveedor").order_by("nombre")
    permission_classes = [IsAuthenticated]
    filterset_class = IngredienteFilter
    search_fields = ["nombre", "proveedor__nombre"]
    ordering_fields = ["nombre", "stock"]
    ordering = ["nombre"]

    def get_serializer_class(self):
        if self.action == "list":
            return IngredienteListSerializer
        return IngredienteSerializer


class RecetaViewSet(viewsets.ModelViewSet):
    queryset = (
        Receta.objects.select_related("cerveza")
        .prefetch_related("ingredientes__ingrediente")
        .annotate(ingredientes_count=Count("ingredientes"))
        .order_by("cerveza__nombre", "-version")
    )
    permission_classes = [IsAuthenticated]
    filterset_class = RecetaFilter
    search_fields = ["nombre", "cerveza__nombre"]
    ordering_fields = ["nombre", "version", "creado_en"]
    ordering = ["cerveza__nombre", "-version"]

    def get_serializer_class(self):
        if self.action == "list":
            return RecetaListSerializer
        return RecetaSerializer


class LoteViewSet(viewsets.ModelViewSet):
    queryset = Lote.objects.select_related("cerveza", "receta").order_by(
        "-fecha_elaboracion"
    )
    permission_classes = [IsAuthenticated]
    filterset_class = LoteFilter
    search_fields = ["codigo", "cerveza__nombre"]
    ordering_fields = ["codigo", "fecha_elaboracion", "volumen_litros", "estado"]
    ordering = ["-fecha_elaboracion"]

    def get_serializer_class(self):
        if self.action == "list":
            return LoteListSerializer
        return LoteSerializer

    @extend_schema(
        request=None,
        responses=LoteSerializer,
        description="Marca el lote como envasado y asigna vencimiento a 30 días.",
    )
    @action(detail=True, methods=["post"], url_path="finalizar")
    def finalizar(self, request, pk=None):
        lote = self.get_object()
        lote.estado = Lote.Estado.ENVASADO
        if lote.fecha_vencimiento is None:
            lote.fecha_vencimiento = timezone.localdate() + timedelta(days=30)
        lote.save(
            update_fields=["estado", "fecha_vencimiento", "actualizado_en"]
        )
        return Response(self.get_serializer(lote).data)
