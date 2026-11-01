"""Rutas de la API v1."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.catalogo.views import (
    CervezaViewSet,
    EstiloViewSet,
    IngredienteViewSet,
    LoteViewSet,
    ProveedorViewSet,
    RecetaViewSet,
)
from apps.cuentas.views import MeView, PerfilUsuarioViewSet
from apps.ventas.views import (
    ClienteViewSet,
    DetallePedidoViewSet,
    PedidoViewSet,
    ResenaViewSet,
)

router = DefaultRouter()
router.register("perfiles", PerfilUsuarioViewSet, basename="perfil")
router.register("estilos", EstiloViewSet, basename="estilo")
router.register("cervezas", CervezaViewSet, basename="cerveza")
router.register("proveedores", ProveedorViewSet, basename="proveedor")
router.register("ingredientes", IngredienteViewSet, basename="ingrediente")
router.register("recetas", RecetaViewSet, basename="receta")
router.register("lotes", LoteViewSet, basename="lote")
router.register("clientes", ClienteViewSet, basename="cliente")
router.register("pedidos", PedidoViewSet, basename="pedido")
router.register("detalles-pedido", DetallePedidoViewSet, basename="detalle-pedido")
router.register("resenas", ResenaViewSet, basename="resena")

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("", include(router.urls)),
]
