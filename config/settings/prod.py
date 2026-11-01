"""Configuración para producción."""

from .base import *  # noqa: F403
from .base import env

DEBUG = False

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
