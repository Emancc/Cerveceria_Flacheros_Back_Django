"""Permisos basados en el rol del perfil del usuario."""

from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import PerfilUsuario

ROL_ADMIN = "admin"
ROL_CERVECERO = "cervecero"
ROL_VENTAS = "ventas"
ROL_CLIENTE = "cliente"

ROLES_PERSONAL = frozenset({ROL_ADMIN, ROL_CERVECERO, ROL_VENTAS})


def rol_de(usuario):
    """Devuelve el rol efectivo del usuario.

    Los usuarios staff/superuser siempre se consideran administradores.
    Si el perfil no existe (o no tiene rol), se asume cliente.
    """
    if usuario is None or not getattr(usuario, "is_authenticated", False):
        return ""

    if getattr(usuario, "is_staff", False) or getattr(usuario, "is_superuser", False):
        return ROL_ADMIN

    rol = (
        PerfilUsuario.objects.filter(usuario=usuario)
        .values_list("rol", flat=True)
        .first()
    )
    return rol or ROL_CLIENTE


class RolRequerido(BasePermission):
    """Base para permisos que exigen uno de los roles indicados."""

    roles_permitidos = frozenset()

    def has_permission(self, request, view):
        usuario = request.user
        if usuario is None or not usuario.is_authenticated:
            return False
        return rol_de(usuario) in self.roles_permitidos


class EsAdminOCervecero(RolRequerido):
    roles_permitidos = frozenset({ROL_ADMIN, ROL_CERVECERO})


class EsAdminOVentas(RolRequerido):
    roles_permitidos = frozenset({ROL_ADMIN, ROL_VENTAS})


class Personal(RolRequerido):
    roles_permitidos = ROLES_PERSONAL


class LecturaPublicaEscrituraCerveceria(BasePermission):
    """Lectura abierta para todos; escritura solo admin/cervecero."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        usuario = request.user
        if usuario is None or not usuario.is_authenticated:
            return False
        return rol_de(usuario) in {ROL_ADMIN, ROL_CERVECERO}


class PedidosPorRol(BasePermission):
    """Admin/ventas gestionan todo; el cliente solo ve y crea lo propio."""

    ACCIONES_CLIENTE = frozenset({"list", "retrieve", "checkout"})

    def has_permission(self, request, view):
        usuario = request.user
        if usuario is None or not usuario.is_authenticated:
            return False
        rol = rol_de(usuario)
        if rol in {ROL_ADMIN, ROL_VENTAS}:
            return True
        if rol == ROL_CLIENTE:
            return getattr(view, "action", None) in self.ACCIONES_CLIENTE
        return False

    def has_object_permission(self, request, view, obj):
        rol = rol_de(request.user)
        if rol in {ROL_ADMIN, ROL_VENTAS}:
            return True
        if rol != ROL_CLIENTE:
            return False
        email = getattr(getattr(obj, "cliente", None), "email", "") or ""
        return email.lower() == request.user.email.lower()


class DetallesPorRol(BasePermission):
    """Admin/ventas gestionan todo; el cliente solo ítems de sus pedidos."""

    ACCIONES_CLIENTE = frozenset({"list", "retrieve"})

    def has_permission(self, request, view):
        usuario = request.user
        if usuario is None or not usuario.is_authenticated:
            return False
        rol = rol_de(usuario)
        if rol in {ROL_ADMIN, ROL_VENTAS}:
            return True
        if rol == ROL_CLIENTE:
            return getattr(view, "action", None) in self.ACCIONES_CLIENTE
        return False

    def has_object_permission(self, request, view, obj):
        rol = rol_de(request.user)
        if rol in {ROL_ADMIN, ROL_VENTAS}:
            return True
        if rol != ROL_CLIENTE:
            return False
        pedido = getattr(obj, "pedido", None)
        email = getattr(getattr(pedido, "cliente", None), "email", "") or ""
        return email.lower() == request.user.email.lower()