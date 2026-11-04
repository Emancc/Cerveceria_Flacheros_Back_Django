"""Subida de imágenes de cervezas a Cloudinary."""

from urllib.parse import urlparse
from uuid import uuid4

import cloudinary
import cloudinary.uploader
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def cloudinary_activo():
    """Indica si la subida a Cloudinary está habilitada."""
    return bool(getattr(settings, "USE_CLOUDINARY", False))


def configurar_cloudinary():
    """Configura el SDK a partir de la URL de credenciales."""
    url = getattr(settings, "CLOUDINARY_URL", "")
    if not url:
        raise ImproperlyConfigured(
            "USE_CLOUDINARY está activo pero falta la variable CLOUDINARY_URL."
        )

    parsed = urlparse(url)
    if (
        parsed.scheme != "cloudinary"
        or not parsed.hostname
        or not parsed.username
        or not parsed.password
    ):
        raise ImproperlyConfigured(
            "CLOUDINARY_URL inválida. Formato esperado: "
            "cloudinary://API_KEY:API_SECRET@CLOUD_NAME."
        )

    cloudinary.config(
        cloud_name=parsed.hostname,
        api_key=parsed.username,
        api_secret=parsed.password,
        secure=True,
    )


def subir_imagen(archivo, carpeta):
    """Sube un archivo a Cloudinary y devuelve la respuesta del SDK."""
    configurar_cloudinary()
    return cloudinary.uploader.upload(
        archivo,
        folder=carpeta,
        public_id=uuid4().hex,
        resource_type="image",
        overwrite=False,
    )
