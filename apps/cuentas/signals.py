"""Señales de la app `cuentas`."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PerfilUsuario, Usuario


@receiver(post_save, sender=Usuario)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crea el perfil al dar de alta un usuario, sin duplicarlo."""
    if created:
        PerfilUsuario.objects.get_or_create(usuario=instance)
