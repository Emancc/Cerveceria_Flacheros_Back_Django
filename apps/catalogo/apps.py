"""Configuración de la app `catalogo`."""

from django.apps import AppConfig


class CatalogoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.catalogo"
    verbose_name = "Catálogo"

    def ready(self):
        # Registrar la limpieza de archivos de imagen al borrar cervezas.
        from . import signals  # noqa: F401
