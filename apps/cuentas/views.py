"""Vistas de cuentas."""

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PerfilUsuario
from .serializers import PerfilUsuarioSerializer, UsuarioSerializer


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=inline_serializer(
            name="MeResponse",
            fields={
                "usuario": UsuarioSerializer(),
                "perfil": PerfilUsuarioSerializer(),
            },
        ),
        description="Datos del usuario autenticado y su perfil.",
    )
    def get(self, request):
        perfil, _ = PerfilUsuario.objects.get_or_create(usuario=request.user)
        return Response(
            {
                "usuario": UsuarioSerializer(request.user).data,
                "perfil": PerfilUsuarioSerializer(perfil).data,
            }
        )


class PerfilUsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PerfilUsuario.objects.none()
    serializer_class = PerfilUsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return PerfilUsuario.objects.none()
        queryset = PerfilUsuario.objects.select_related("usuario").order_by(
            "usuario__email"
        )
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(usuario=self.request.user)
