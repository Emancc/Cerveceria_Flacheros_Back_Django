"""Tests del comando que migra imágenes locales a Cloudinary."""

import shutil
import tempfile
from decimal import Decimal
from unittest.mock import patch

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from apps.catalogo.models import Cerveza, Estilo

URL_CLOUDINARY = (
    "https://res.cloudinary.com/demo/image/upload/v123/"
    "cervezas/migradas/local.png"
)


class MigrarImagenesCloudinaryCommandTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.estilo = Estilo.objects.create(
            nombre="IPA",
            slug="ipa",
            descripcion="Lúpulo intenso",
            color="#e0a53c",
        )

    def setUp(self):
        self.media_root = tempfile.mkdtemp(prefix="migrar-imagenes-")
        self._override = override_settings(MEDIA_ROOT=self.media_root)
        self._override.enable()
        self.addCleanup(self._override.disable)
        self.addCleanup(shutil.rmtree, self.media_root, ignore_errors=True)

    def _crear_cerveza(self, nombre, imagen_archivo=""):
        return Cerveza.objects.create(
            nombre=nombre,
            estilo=self.estilo,
            graduacion=Decimal("5.00"),
            amargor=30,
            descripcion="Cerveza de prueba para migración",
            precio=Decimal("3000.00"),
            stock=10,
            imagen_archivo=imagen_archivo,
        )

    @override_settings(
        USE_CLOUDINARY=True,
        CLOUDINARY_URL="cloudinary://123456789:secreto@demo",
    )
    @patch(
        "apps.catalogo.management.commands.migrar_imagenes_cloudinary.subir_imagen"
    )
    def test_apply_sube_archivos_y_limpia_referencias_rotas(self, subir_mock):
        subir_mock.return_value = {"secure_url": URL_CLOUDINARY}
        ruta = default_storage.save(
            "cervezas/2026/11/local.png",
            ContentFile(b"contenido de imagen"),
        )
        con_archivo = self._crear_cerveza("Con archivo", ruta)
        sin_archivo = self._crear_cerveza(
            "Sin archivo",
            "cervezas/2026/11/perdida.png",
        )

        call_command("migrar_imagenes_cloudinary", "--apply")

        con_archivo.refresh_from_db()
        sin_archivo.refresh_from_db()
        self.assertEqual(con_archivo.imagen, URL_CLOUDINARY)
        self.assertFalse(con_archivo.imagen_archivo)
        self.assertFalse(sin_archivo.imagen_archivo)
        subir_mock.assert_called_once()
        _, carpeta = subir_mock.call_args.args
        self.assertEqual(carpeta, "cervezas/migradas")

    @override_settings(
        USE_CLOUDINARY=True,
        CLOUDINARY_URL="cloudinary://123456789:secreto@demo",
    )
    @patch(
        "apps.catalogo.management.commands.migrar_imagenes_cloudinary.subir_imagen"
    )
    def test_dry_run_no_modifica_nada(self, subir_mock):
        ruta = default_storage.save(
            "cervezas/2026/11/local.png",
            ContentFile(b"contenido de imagen"),
        )
        cerveza = self._crear_cerveza("Con archivo", ruta)

        call_command("migrar_imagenes_cloudinary")

        cerveza.refresh_from_db()
        self.assertEqual(cerveza.imagen, "")
        self.assertEqual(cerveza.imagen_archivo.name, ruta)
        subir_mock.assert_not_called()

    @override_settings(USE_CLOUDINARY=False)
    def test_sin_cloudinary_falla(self):
        with self.assertRaises(CommandError):
            call_command("migrar_imagenes_cloudinary")
