"""Configuración para producción."""

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .base import CLOUDINARY_URL, USE_CLOUDINARY, env

DEBUG = False

if USE_CLOUDINARY and not CLOUDINARY_URL:
    raise ImproperlyConfigured(
        "USE_CLOUDINARY está activo pero falta CLOUDINARY_URL. "
        "Configurá la variable de entorno en Render."
    )

# En producción SECRET_KEY es obligatoria: si falta, django-environ lanza
# ImproperlyConfigured y el proceso no arranca.
SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# Detrás de un proxy/balanceador que termina TLS.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# WhiteNoise sirve los estáticos comprimidos y con hash.
STORAGES = {
    **STORAGES,  # noqa: F405
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
