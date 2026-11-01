"""Modelos abstractos compartidos por las apps del proyecto."""

from django.db import models


class ModeloConFechas(models.Model):
    """Agrega marcas de auditoría de creación y actualización."""

    creado_en = models.DateTimeField(
        "creado en",
        auto_now_add=True,
    )
    actualizado_en = models.DateTimeField(
        "actualizado en",
        auto_now=True,
    )

    class Meta:
        abstract = True
