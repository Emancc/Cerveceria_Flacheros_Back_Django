"""Serializers de cuentas."""

from rest_framework import serializers

from .models import PerfilUsuario, Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_active",
        )


class PerfilUsuarioSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    rol_display = serializers.CharField(source="get_rol_display", read_only=True)

    class Meta:
        model = PerfilUsuario
        fields = (
            "id",
            "usuario",
            "telefono",
            "rol",
            "rol_display",
            "bio",
            "avatar",
            "creado_en",
        )
