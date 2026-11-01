"""Modelos de usuarios y perfiles."""

from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import ModeloConFechas


class UsuarioManager(UserManager):
    """Manager de usuarios que usa el email como identificador único."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio.")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_active", True)
        usuario = self.model(email=email, **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Un superusuario debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Un superusuario debe tener is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    """Usuario del sistema, autenticado por email."""

    username = None
    email = models.EmailField(_("correo electrónico"), unique=True)

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("usuario")
        verbose_name_plural = _("usuarios")
        ordering = ["email"]

    def __str__(self):
        return self.email


class PerfilUsuario(ModeloConFechas):
    """Datos adicionales del usuario."""

    class Rol(models.TextChoices):
        ADMIN = "admin", _("Administrador")
        CERVECERO = "cervecero", _("Cervecero")
        VENTAS = "ventas", _("Ventas")
        CLIENTE = "cliente", _("Cliente")

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
        verbose_name=_("usuario"),
    )
    telefono = models.CharField(_("teléfono"), max_length=30, blank=True)
    rol = models.CharField(
        _("rol"),
        max_length=20,
        choices=Rol.choices,
        default=Rol.CLIENTE,
    )
    bio = models.TextField(_("biografía"), blank=True)
    avatar = models.URLField(_("avatar"), blank=True)

    class Meta:
        verbose_name = _("perfil de usuario")
        verbose_name_plural = _("perfiles de usuario")

    def __str__(self):
        return f"Perfil de {self.usuario.email}"
