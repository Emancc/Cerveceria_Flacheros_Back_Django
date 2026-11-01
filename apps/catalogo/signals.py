"""Señales de la app `catalogo`."""

from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Cerveza


@receiver(post_delete, sender=Cerveza)
def borrar_imagen_archivo(sender, instance, **kwargs):
    """Borra del storage el archivo de imagen al eliminar la cerveza."""
    if instance.imagen_archivo:
        instance.imagen_archivo.delete(save=False)
