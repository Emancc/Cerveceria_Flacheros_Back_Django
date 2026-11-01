"""Registro de los modelos de `cuentas` en el admin."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import BaseUserCreationForm, UserChangeForm

from .models import PerfilUsuario, Usuario


class UsuarioCreationForm(BaseUserCreationForm):
    """Alta de usuario por email (el form de Django usa `username`)."""

    class Meta:
        model = Usuario
        fields = ("email",)


class UsuarioChangeForm(UserChangeForm):
    """Edición de usuario por email."""

    class Meta(UserChangeForm.Meta):
        model = Usuario
        fields = "__all__"
        field_classes = {}


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    form = UsuarioChangeForm
    add_form = UsuarioCreationForm

    list_display = ("email", "first_name", "last_name", "is_staff", "is_active")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

    # `UserAdmin` trae fieldsets con `username`; se reemplazan por email.
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Datos personales", {"fields": ("first_name", "last_name")}),
        (
            "Permisos",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Fechas importantes", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "telefono", "rol", "creado_en")
    list_filter = ("rol",)
    search_fields = ("usuario__email", "telefono")
    ordering = ("usuario__email",)
